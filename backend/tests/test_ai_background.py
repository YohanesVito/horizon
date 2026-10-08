import asyncio
from time import monotonic
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import ai, insights, store
from backend.main import app


def test_kickoff_returns_before_ai_and_status_poll_is_read_only(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/background.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    store.init_store()
    run = {'id': 'background-run', 'status': 'completed', 'input': {'capital': 100},
           'result': {'primary': {'allocation': 'equal', 'trades': [{'symbol': 'TEST', 'shares': 100}]}, 'alternatives': []}}
    store.save(run['id'], 'run', run)
    calls = []
    monkeypatch.setattr(ai, '_api_key', lambda: 'test')

    async def exercise():
        started, release = asyncio.Event(), asyncio.Event()
        async def held_research(*args):
            started.set()
            await release.wait()
            return {'sources': [], 'gaps': [], 'status': 'completed'}
        async def generate(*args, **kwargs):
            calls.append(1)
            return {'summary': 'Filled after provider completion', 'findings': []}
        monkeypatch.setattr(insights, 'research_context', held_research)
        monkeypatch.setattr(ai, 'generate_structured', generate)
        path = '/api/simulations/background-run/insights'
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            before = await client.get(path)
            assert before.status_code == 404
            assert store.get('ai-run:background-run', kind='simulation-insight') is None
            began = monotonic()
            response = await asyncio.wait_for(client.post(path, json={'allocation': 'equal'}), timeout=1)
            assert monotonic()-began < 1
            assert response.json()['status'] == 'processing'
            await asyncio.wait_for(started.wait(), timeout=1)
            # Provider is intentionally unresolved; algorithm and health remain usable.
            health, completed_run = await asyncio.gather(client.get('/api/health'), client.get('/api/simulations/background-run'))
            assert health.status_code == 200
            assert completed_run.json()['status'] == 'completed'
            assert completed_run.json()['result'] == run['result']
            assert calls == []
            repeats = await asyncio.gather(*[client.post(path, json={'allocation': 'equal'}) for _ in range(6)])
            polls = await asyncio.gather(*[client.get(path) for _ in range(6)])
            assert all(item.json()['status'] == 'processing' for item in repeats+polls)
            assert store.get('ai-run:background-run')['attempts'] == 1
            assert calls == []
            release.set()
            for _ in range(100):
                finished = await client.get(path)
                if finished.json()['status'] == 'completed':
                    break
                await asyncio.sleep(.005)
            assert finished.json()['summary'] == 'Filled after provider completion'
            assert finished.json()['attempts'] == 1
            assert calls == [1]
            assert (await client.post(path, json={'allocation': 'equal'})).json() == finished.json()
            assert calls == [1]
    asyncio.run(exercise())
