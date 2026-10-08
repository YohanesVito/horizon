from fastapi.testclient import TestClient

from backend.main import app


def test_ex_date_scenario_keeps_price_and_total_bep_separate():
    response = TestClient(app).post('/api/ex-date/scenario', json={
        'capital_idr': 1050000, 'entry_price': 1000,
        'dps': 80, 'assumed_ex_price': 900,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'scenario'
    assert (data['lots'], data['shares']) == (10, 1000)
    assert data['remaining_cash_idr'] == 50000
    assert (data['capital_pnl_idr'], data['dividend_idr'], data['gross_pnl_idr']) == (-100000, 80000, -20000)
    assert data['gross_return_pct'] == -2
    assert data['price_bep_idr'] == 1000
    assert data['total_bep_idr'] == 920
    assert not data['total_bep_reached']
    assert 'bukan prediksi' in data['label']
    assert 'di luar biaya transaksi, pajak, dan slippage' in data['label']


def test_ex_date_scenario_rejects_insufficient_capital():
    response = TestClient(app).post('/api/ex-date/scenario', json={
        'capital_idr': 99999, 'entry_price': 1000,
        'dps': 80, 'assumed_ex_price': 920,
    })
    assert response.status_code == 422
