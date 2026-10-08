from fastapi.testclient import TestClient

from backend.main import app


def test_dividend_discovery_does_not_require_complete_five_year_chart():
    client = TestClient(app)
    discovery = client.get('/api/dividend-candidates')
    timeline = client.get('/api/timeline')

    assert discovery.status_code == 200
    data = discovery.json()
    assert data['year'] == 2025
    assert data['universe_count'] == 368
    assert [row['symbol'] for row in data['candidates']] == ['DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS']
    assert all(row['yield_pct'] > 0 and row['dps'] > 0 for row in data['candidates'])
    assert timeline.json()['companies'] == []
