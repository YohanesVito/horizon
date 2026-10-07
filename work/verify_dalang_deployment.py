"""Verify HTTPS, API protection, database preservation and a disposable replay."""
from datetime import datetime, timezone
from pathlib import Path
from time import sleep, monotonic
import json
import sys
import httpx
from dotenv import dotenv_values
from sqlalchemy import select, delete

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import store
from backend.migration import digest


def main():
    base = sys.argv[1].rstrip('/')
    assert base.startswith('https://'), 'Verification requires HTTPS'
    values = dotenv_values(ROOT / '.env.local')
    key = values['HORIZON_API_KEY']
    report = {'base_url': base, 'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'checks': {}}
    with store.engine.connect() as connection:
        before = list(connection.execute(select(store.Record.__table__)).mappings())
    probe_id = None
    completed = False
    try:
        with httpx.Client(base_url=base, timeout=35, follow_redirects=False) as client:
            health = client.get('/api/health')
            assert health.status_code == 200 and health.json()['storage'] == 'postgresql'
            report['health'] = health.json()
            assert client.get('/api/catalog').status_code == 401
            assert client.get('/api/catalog', headers={'Authorization': 'Bearer invalid'}).status_code == 401
            assert client.post('/api/watchlist', json={'symbol': 'BBCA'}).status_code == 401
            report['checks']['unauthorized_read_and_write_rejected'] = True
            client.headers['Authorization'] = 'Bearer ' + key
            for path in ['/api/catalog', '/api/intelligence', '/api/timeline', '/api/timeline/LPPF?preview=true',
                         '/api/watchlist', '/api/simulations', '/api/rotation-plans', '/api/rotation-runs']:
                response = client.get(path)
                assert response.status_code == 200, path
                assert key not in response.text
                report['checks'][path] = 200
            fixture = json.loads((ROOT / 'outputs/development/readiness-case.json').read_text())
            submitted = client.post('/api/simulations', json=fixture['input'])
            assert submitted.status_code == 202
            probe_id = submitted.json()['id']
            deadline = monotonic() + 45
            while monotonic() < deadline:
                result = client.get('/api/simulations/' + probe_id).json()
                if result.get('status') in ('completed', 'failed'):
                    break
                sleep(0.5)
            assert result['status'] == 'completed'
            completed = True
            assert result['result'] == fixture['result'], 'Replay differs from verified local fixture'
            assert store.get(probe_id, kind='run')['result'] == result['result']
            report['checks']['api_worker_supabase_replay_parity'] = True
            report['replay'] = {'probe_id': probe_id, 'gross_pnl': result['result']['primary']['gross_pnl'],
                                'ending_nav': result['result']['primary']['ending_nav'],
                                'label': 'Historical replay, outside fees, tax and slippage'}
    finally:
        # Do not delete a still-running job; it may be writing its final result.
        if probe_id and completed:
            with store.engine.begin() as connection:
                connection.execute(delete(store.Record).where(store.Record.key == probe_id, store.Record.kind == 'run'))
            report['temporary_probe_removed'] = True
        store.engine.dispose()
    with store.engine.connect() as connection:
        after = list(connection.execute(select(store.Record.__table__)).mappings())
    assert digest(before) == digest(after), 'Existing records changed during verification'
    report.update(original_records=len(before), original_records_preserved=True, status='passed')
    folder = ROOT / 'outputs/deployment'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'dalang-api-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        raise SystemExit(f'Deployment verification failed ({type(error).__name__}); no credentials printed.') from None
