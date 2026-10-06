from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend import store
from backend.main import app


def test_frozen_plan_replay_history_and_validation(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/rotation.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    with TestClient(app) as c:
        assert c.post('/api/rotation-plans', json={'start_date': '2026-01-01'}).status_code == 422
        assert c.get('/api/rotation-plans/missing').status_code == 404
        assert c.get('/api/rotation-runs/missing').status_code == 404
        response = c.post('/api/rotation-plans', json={})
        assert response.status_code == 201
        p = response.json()
        assert len(p['routes']) == 3
        assert 'result' not in p
        assert p['decision_date'] == '2025-03-01'
        assert p['dataset_version'] == c.get('/api/catalog').json()['meta']['dataset_version']
        assert c.get('/api/rotation-plans').json()[0]['id'] == p['id']
        old_rules = p['input']['rules']
        c.put('/api/intelligence/rules', json={**old_rules, 'minimum_samples': 100})
        assert c.get(f"/api/rotation-plans/{p['id']}").json()['input']['rules'] == old_rules
        queued = c.post(f"/api/rotation-plans/{p['id']}/replay")
        assert queued.status_code == 202
        job_id = queued.json()['id']
        for _ in range(200):
            job = c.get(f'/api/rotation-runs/{job_id}').json()
            if job['status'] in ('completed', 'failed'):
                break
            sleep(.01)
        assert job['status'] == 'completed', job
        assert job['plan_id'] == p['id']
        assert c.get(f'/api/simulations/{job_id}').status_code == 404
        assert c.get(f'/api/rotation-plans/{job_id}').status_code == 404
        assert sum(len(r['comparison']['alternatives']) for r in job['result']['routes']) == 9
        assert job['result']['input']['rules'] == old_rules
        assert c.get('/api/rotation-runs').json()[0]['id'] == job_id
        assert 'result' not in c.get('/api/rotation-runs').json()[0]
        store.save(p['id'], 'rotation-plan', {**p, 'dataset_version': 'old'})
        assert c.post(f"/api/rotation-plans/{p['id']}/replay").status_code == 409
        empty = c.post('/api/rotation-plans', json={'allow_calendar_assumption': False}).json()
        assert c.post(f"/api/rotation-plans/{empty['id']}/replay").status_code == 422
        assert c.get(f'/api/rotation-runs/{job_id}').json()['status'] == 'completed'


def test_failed_job_is_visible_and_corrected_retry_succeeds(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/retry.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    with TestClient(app) as c:
        def finish(body):
            response = c.post('/api/simulations', json=body)
            assert response.status_code == 202
            for _ in range(200):
                job = c.get('/api/simulations/'+response.json()['id']).json()
                if job['status'] in ('completed', 'failed'):
                    return job
                sleep(.01)
            raise AssertionError('Job did not reach a terminal state')
        body = {'event_ids': ['BBCA:2025-12-03']}
        failed = finish(body)
        assert failed['status'] == 'failed' and 'Tanggal akhir' in failed['error']
        success = finish({**body, 'start_date': '2025-11-01', 'end_date': '2025-12-31'})
        assert success['status'] == 'completed'
        assert success['id'] != failed['id']
        assert c.get('/api/simulations/'+failed['id']).json()['status'] == 'failed'
        assert c.get('/api/rotation-runs/'+success['id']).status_code == 404


def test_startup_marks_only_interrupted_jobs_as_failed(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/restart.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    store.init_store()
    for kind in ['run', 'rotation-run']:
        for status in ['queued', 'running', 'completed']:
            key = f'{kind}-{status}'
            store.save(key, kind, {'id': key, 'status': status, 'result': {'proof': 'original'}})
    with TestClient(app):
        for kind in ['run', 'rotation-run']:
            for status in ['queued', 'running']:
                job = store.get(f'{kind}-{status}')
                assert job['status'] == 'failed' and 'terhenti' in job['error']
            assert store.get(f'{kind}-completed') == {'id': f'{kind}-completed', 'status': 'completed', 'result': {'proof': 'original'}}
