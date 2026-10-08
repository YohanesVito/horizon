from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend import store
from backend.main import app



def test_removed_rotation_routes_reject_new_work_but_history_remains(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/rotation.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    with TestClient(app) as c:
        store.save('old-plan', 'rotation-plan', {'id': 'old-plan', 'candidates': [], 'routes': []})
        store.save('old-run', 'rotation-run', {'id': 'old-run', 'plan_id': 'old-plan', 'status': 'completed', 'result': {'historical': True}})
        assert c.post('/api/rotation-plans', json={}).status_code == 410
        assert c.post('/api/rotation-plans/old-plan/replay').status_code == 410
        assert c.get('/api/rotation-plans/old-plan').json()['id'] == 'old-plan'
        assert c.get('/api/rotation-runs/old-run').json()['result'] == {'historical': True}
        for mode in ['equal', 'rotation']:
            assert c.post('/api/simulations', json={'event_ids': ['BBCA:2025-03-21'], 'allocation': mode}).status_code == 422
        assert c.get('/api/rotation-runs').json()[0]['id'] == 'old-run'

def test_startup_marks_only_interrupted_jobs_as_failed(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/restart.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    store.init_store()
    for kind in ['run', 'rotation-run']:
        for status in ['queued', 'running', 'completed']:
            key = f'{kind}-{status}'
            store.save(key, kind, {'id': key, 'status': status, 'result': {'proof': 'original'}})
    store.save('ai-run:local:ticker:BBCA', 'simulation-insight', {'status': 'processing', 'started_at': 0, 'provenance': {'run_id': 'local', 'symbol': 'BBCA'}})
    with TestClient(app):
        assert store.get('ai-run:local:ticker:BBCA')['status'] == 'unavailable'
        assert store.get('ai-run:local') is None
        for kind in ['run', 'rotation-run']:
            for status in ['queued', 'running']:
                job = store.get(f'{kind}-{status}')
                assert job['status'] == 'failed' and 'terhenti' in job['error']
            assert store.get(f'{kind}-completed') == {'id': f'{kind}-completed', 'status': 'completed', 'result': {'proof': 'original'}}
