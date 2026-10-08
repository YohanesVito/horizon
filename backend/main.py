from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from uuid import uuid4
import time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from .unified import UnifiedDataset
from .domain import SimulationRequest, WatchlistRequest, ScreenRules, FinancialLogic, ScenarioRequest, RotationRequest
from . import store
from .simulator import compare
from .intelligence import IntelligenceDataset, rank, scenario
from .planner import plan_routes, replay_routes
from .timeline import TimelineDataset
from .discovery import top_dividend_yield
from .security import require_api_key, validate_api_key_config
from .insights import InsightRequest, generate_insights

intelligence_dataset = IntelligenceDataset()
dataset = UnifiedDataset(intelligence_dataset)
timeline_dataset = TimelineDataset(intelligence_events=intelligence_dataset.events)
pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='dividen-replay')


@asynccontextmanager
async def lifespan(app):
    global pool
    validate_api_key_config()
    store.init_store()
    with store.worker_lease():
        pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='dividen-replay')
        try:
            for insight in store.list_records('simulation-insight', limit=10000):
                if insight.get('status') == 'processing' and (store.engine.dialect.name == 'postgresql' or time.time() - insight.get('started_at', 0) > 100):
                    insight.update(status='unavailable', summary='Proses analisis terhenti. Percobaan AI untuk simulasi ini sudah digunakan.')
                    store.save(f"ai-run:{insight['provenance']['run_id']}", 'simulation-insight', insight)
            # The lease prevents a second cloud-backed process failing active jobs.
            for kind in ('run', 'rotation-run'):
                for job in store.list_records(kind, limit=1000):
                    if job['status'] in ('queued', 'running'):
                        job.update(status='failed', error='Proses lokal terhenti. Jalankan ulang simulasi.')
                        store.save(job['id'], kind, job)
            yield
        finally:
            pool.shutdown(wait=True)


app = FastAPI(title='Dividen Lab', version='0.1.0', lifespan=lifespan)
app.middleware('http')(require_api_key)


@app.get('/api/intelligence')
def intelligence():
    saved = store.get('financial-logic', FinancialLogic().model_dump())
    logic = FinancialLogic.model_validate(saved)
    analysis = intelligence_dataset.analyze(logic.entry_offset, logic.horizon)
    return {**analysis, 'ranking': rank(analysis, logic), 'rules': saved}


@app.put('/api/intelligence/rules')
def save_financial_logic(body: FinancialLogic):
    saved = {**body.model_dump(), 'saved_at': datetime.now(timezone.utc).isoformat()}
    store.save('financial-logic', 'settings', saved)
    return intelligence()


@app.post('/api/scenarios', status_code=201)
def stress_test(body: ScenarioRequest):
    analysis = intelligence_dataset.analyze(body.entry_offset, body.horizon)
    try:
        result = scenario(analysis, body)
    except ValueError as error:
        raise HTTPException(422, str(error))
    saved = {'id': str(uuid4()), 'input': body.model_dump(mode='json'), 'result': result,
             'created_at': datetime.now(timezone.utc).isoformat(), 'financial_logic': store.get('financial-logic', FinancialLogic().model_dump())}
    store.save(saved['id'], 'scenario', saved)
    return saved


@app.get('/api/scenarios')
def scenario_history():
    return store.list_records('scenario')


@app.get('/api/health')
def health():
    try:
        storage = store.healthcheck()
    except Exception:
        raise HTTPException(503, 'Database tidak dapat diakses.') from None
    return {'status': 'ok', 'source': 'Sectors snapshots', 'storage': storage, 'worker': 'local-thread', 'mode': 'research-mvp'}


@app.get('/api/catalog')
def catalog():
    return dataset.catalog()


@app.get('/api/dividend-candidates')
def dividend_candidates():
    return top_dividend_yield()


@app.get('/api/timeline')
def timeline_catalog():
    return timeline_dataset.catalog()


@app.get('/api/timeline/{symbol}')
def timeline_detail(symbol: str, preview: bool = False):
    try:
        return timeline_dataset.detail(symbol.upper(), preview=preview)
    except KeyError:
        raise HTTPException(404, 'Emiten belum tersedia untuk timeline lima tahun.')
    except ValueError as error:
        raise HTTPException(422, str(error))


@app.get('/api/companies/{symbol}')
def company(symbol: str):
    try:
        return dataset.detail(symbol.upper())
    except KeyError:
        raise HTTPException(404, 'Emiten tidak tersedia dalam dataset riset.')


@app.get('/api/watchlist')
def watchlist():
    return store.get('watchlist', {'symbols': []})


@app.post('/api/watchlist')
def add_watchlist(body: WatchlistRequest):
    if body.symbol not in dataset.companies:
        raise HTTPException(404, 'Emiten tidak tersedia.')
    current = watchlist()
    current['symbols'] = list(dict.fromkeys([*current['symbols'], body.symbol]))
    store.save('watchlist', 'settings', current)
    return current


@app.delete('/api/watchlist/{symbol}')
def remove_watchlist(symbol: str):
    current = watchlist()
    current['symbols'] = [s for s in current['symbols'] if s != symbol]
    store.save('watchlist', 'settings', current)
    return current


@app.get('/api/rules')
def rules():
    return store.get('rules', ScreenRules().model_dump())


@app.put('/api/rules')
def save_rules(body: ScreenRules):
    value = {**body.model_dump(), 'version': datetime.now(timezone.utc).isoformat()}
    store.save('rules', 'settings', value)
    return value


def run_job(job_id, body):
    job = store.get(job_id)
    job.update(status='running')
    store.save(job_id, 'run', job)
    try:
        result = compare(dataset, body)
        job.update(status='completed', result=result, finished_at=datetime.now(timezone.utc).isoformat())
    except ValueError as error:
        job.update(status='failed', error=str(error))
    except Exception:
        # Never put credentials or provider raw responses in a browser error.
        job.update(status='failed', error='Simulasi gagal diproses. Periksa input dan data, lalu coba lagi.')
        import logging
        logging.getLogger(__name__).exception('Simulation job failed')
    store.save(job_id, 'run', job)


@app.post('/api/simulations', status_code=202)
def simulate(body: SimulationRequest):
    unknown = [eid for eid in body.event_ids if eid not in dataset.events]
    if unknown:
        raise HTTPException(422, 'Event tidak dikenal.')
    job_id = str(uuid4())
    job = {'id': job_id, 'status': 'queued', 'input': body.model_dump(mode='json'),
           'screening_rules': rules(), 'dataset_version': dataset.version,
           'created_at': datetime.now(timezone.utc).isoformat()}
    store.save(job_id, 'run', job)
    pool.submit(run_job, job_id, body)
    return job


@app.get('/api/simulations')
def history():
    return [{k: v for k, v in r.items() if k != 'result'} for r in store.list_records('run')]


@app.get('/api/simulations/{job_id}')
def result(job_id: str):
    run = store.get(job_id, kind='run')
    if not run or 'status' not in run:
        raise HTTPException(404, 'Simulasi tidak ditemukan.')
    return run


@app.post('/api/simulations/{job_id}/insights')
async def simulation_insights(job_id: str, body: InsightRequest):
    run = result(job_id)
    if run['status'] != 'completed':
        raise HTTPException(409, 'Simulasi belum selesai.')
    options = [run['result']['primary'], *run['result'].get('alternatives', [])]
    selected = next((option for option in options if option['allocation'] == body.allocation), None)
    if selected is None:
        raise HTTPException(422, 'Strategi tidak tersedia pada hasil simulasi ini.')
    return await generate_insights(run, selected, timeline_dataset)


@app.post('/api/rotation-plans', status_code=201)
def create_rotation_plan(body: RotationRequest):
    try:
        plan = plan_routes(dataset, body)
    except ValueError as error:
        raise HTTPException(422, str(error))
    plan.update(id=str(uuid4()), created_at=datetime.now(timezone.utc).isoformat())
    store.save(plan['id'], 'rotation-plan', plan)
    return plan


@app.get('/api/rotation-plans')
def rotation_plans():
    return store.list_records('rotation-plan')


@app.get('/api/rotation-plans/{plan_id}')
def rotation_plan(plan_id: str):
    plan = store.get(plan_id, kind='rotation-plan')
    if not plan or 'candidates' not in plan:
        raise HTTPException(404, 'Rencana tidak ditemukan.')
    return plan


def run_rotation_job(job_id, plan):
    job = store.get(job_id)
    job.update(status='running')
    store.save(job_id, 'rotation-run', job)
    try:
        job.update(status='completed', result=replay_routes(dataset, plan), finished_at=datetime.now(timezone.utc).isoformat())
    except ValueError as error:
        job.update(status='failed', error=str(error))
    except Exception:
        job.update(status='failed', error='Replay rute gagal diproses. Periksa input dan data lalu coba lagi.')
        import logging
        logging.getLogger(__name__).exception('Rotation replay failed')
    store.save(job_id, 'rotation-run', job)


@app.post('/api/rotation-plans/{plan_id}/replay', status_code=202)
def start_rotation_replay(plan_id: str):
    plan = rotation_plan(plan_id)
    if plan['dataset_version'] != dataset.version:
        raise HTTPException(409, 'Dataset berubah; buat ulang rencana.')
    if not plan['routes']:
        raise HTTPException(422, 'Tidak ada rute yang lolos untuk diuji.')
    job = {'id': str(uuid4()), 'plan_id': plan_id, 'status': 'queued', 'input': plan['input'],
           'dataset_version': plan['dataset_version'], 'created_at': datetime.now(timezone.utc).isoformat()}
    store.save(job['id'], 'rotation-run', job)
    pool.submit(run_rotation_job, job['id'], plan)
    return job


@app.get('/api/rotation-runs')
def rotation_history():
    return [{k: v for k, v in r.items() if k != 'result'} for r in store.list_records('rotation-run')]


@app.get('/api/rotation-runs/{job_id}')
def rotation_result(job_id: str):
    run = store.get(job_id, kind='rotation-run')
    if not run or 'plan_id' not in run:
        raise HTTPException(404, 'Replay rute tidak ditemukan.')
    return run
