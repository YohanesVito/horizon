from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend import store
from backend.main import app


def test_persisted_user_flow_and_job_contract(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/test.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    with TestClient(app) as c:
        assert c.get('/api/health').status_code == 200
        catalog = c.get('/api/catalog').json()
        assert len(catalog['companies']) == 9
        assert len(catalog['meta']['dataset_version']) > 16
        assert c.get('/api/companies/XXXX').status_code == 404
        assert c.post('/api/watchlist', json={'symbol': 'BBCA'}).json()['symbols'] == ['BBCA']
        assert c.post('/api/watchlist', json={'symbol': 'BBCA'}).json()['symbols'] == ['BBCA']
        assert c.get('/api/watchlist').json()['symbols'] == ['BBCA']
        assert c.delete('/api/watchlist/BBCA').json()['symbols'] == []
        rules = {'name': 'Test financial logic', 'minimum_yield': 10, 'minimum_frequency': 1, 'require_replay': False, 'sort_by': 'yield'}
        assert c.put('/api/rules', json=rules).status_code == 200
        assert c.get('/api/rules').json()['minimum_yield'] == 10
        assert c.post('/api/simulations', json={'event_ids': [], 'capital': -1}).status_code == 422
        r = c.post('/api/simulations', json={'event_ids': ['BBCA:2025-03-21', 'BMRI:2025-04-14', 'LPPF:2025-04-22']})
        assert r.status_code == 202
        job_id = r.json()['id']
        for _ in range(200):
            result = c.get(f'/api/simulations/{job_id}').json()
            if result['status'] in ('completed', 'failed'):
                break
            sleep(.01)
        assert result['status'] == 'completed', result
        assert len(result['result']['alternatives']) == 3
        assert result['result']['primary']['dataset_version'] == catalog['meta']['dataset_version']
        assert c.get('/api/simulations').json()[0]['id'] == job_id
        assert 'result' not in c.get('/api/simulations').json()[0]
        assert store.get(job_id)['status'] == 'completed'
        evidence = c.get('/api/intelligence')
        assert evidence.status_code == 200
        assert evidence.json()['audit']['events'] == 48
        logic = evidence.json()['rules']
        strict = c.put('/api/intelligence/rules', json={**logic, 'minimum_samples': 100}).json()
        assert strict['ranking']['ranked'] == []
        assert len(strict['ranking']['excluded']) == 9
        c.put('/api/intelligence/rules', json=logic)
        payload = {'symbol': 'BBCA', 'capital': '100000000', 'entry_price': '10000', 'dps': '250',
                   'entry_date': '2026-11-02', 'cum_date': '2026-11-09', 'ex_date': '2026-11-10',
                   'recording_date': '2026-11-11', 'payment_date': '2026-12-10', 'valuation_date': '2026-12-08'}
        scenario_run = c.post('/api/scenarios', json=payload)
        assert scenario_run.status_code == 201
        saved = scenario_run.json()
        assert saved['result']['analog_count'] == 8
        assert saved['result']['dividend_cash'] == 0
        assert saved['result']['dividend_receivable'] == 2500000
        assert c.get('/api/scenarios').json()[0]['id'] == saved['id']
        c.put('/api/intelligence/rules', json={**logic, 'horizon': 5})
        assert store.get(saved['id'])['input']['horizon'] == 20
        assert c.post('/api/scenarios', json={**payload, 'payment_date': '2026-10-01'}).status_code == 422
        assert c.post('/api/scenarios', json={**payload, 'symbol': 'XXXX'}).status_code == 422
