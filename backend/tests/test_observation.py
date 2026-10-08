from types import SimpleNamespace
from decimal import Decimal
from backend.observation import observe_holding


def data():
    days = ['2025-04-10', '2025-04-11', '2025-04-14', '2025-04-15']
    bars = {d: {'open': 100, 'high': 110, 'low': 90, 'close': 100} for d in days}
    bars[days[0]]['high'] = 120
    bars[days[1]]['low'] = 70
    return SimpleNamespace(market_sessions=days, prices={'TEST': bars}), {
        'symbol': 'TEST', 'cum_date': days[0], 'ex_date': days[1], 'payment_date': days[1], 'dps': 10}


def test_ohlc_extrema_and_dividend_accounting_use_entry_investment():
    dataset, event = data()
    result = observe_holding(dataset, event, 200, Decimal(105))
    assert result['end_date'] == '2025-04-15'  # two actual sessions after Friday payment
    assert result['complete']
    assert result['invested'] == 21000
    assert result['highest']['price'] == 120  # high rather than flat closing prices
    assert result['highest']['total_value'] == 26000
    assert result['highest']['pnl'] == 5000
    assert result['lowest']['total_value'] == 16000
    assert result['lowest']['pnl'] == -5000
    assert result['points'][0]['dividend_entitled'] == 0
    assert result['points'][0]['dividend_paid'] == 0
    assert result['points'][1]['dividend_entitled'] == 2000
    assert result['points'][1]['dividend_paid'] == 2000


def test_incomplete_future_payment_never_invents_boundary():
    dataset, event = data()
    event['payment_date'] = '2026-01-15'
    result = observe_holding(dataset, event, 100, 100)
    assert result['end_date'] is None
    assert not result['complete']
    assert result['available_end_date'] == '2025-04-15'
    assert all(p['dividend_paid'] == 0 for p in result['points'])
    assert result['gaps']


def test_missing_ohlc_is_gap_not_synthetic_price_and_skipped_has_no_value_extrema():
    dataset, event = data()
    del dataset.prices['TEST']['2025-04-14']['high']
    result = observe_holding(dataset, event, 0, 100)
    assert not result['complete']
    assert len(result['points']) == 3
    assert result['highest'] is None and result['lowest'] is None
    assert '2025-04-14' in result['gaps'][0]


def automatic_data():
    from datetime import date, timedelta
    days = [(date(2025, 3, 3) + timedelta(days=i)).isoformat() for i in range(21) if (date(2025, 3, 3) + timedelta(days=i)).weekday() < 5]
    prices = {d: {'open': 120, 'high': 125, 'low': 115, 'close': 120, 'volume': 1000} for d in days}
    for d, close in zip(days[:5], [100, 101, 102, 103, 105]):
        prices[d] = {'open': close, 'high': close, 'low': close, 'close': close, 'volume': 1000}
    e = {'id': 'TEST:auto', 'symbol': 'TEST', 'cum_date': days[5], 'ex_date': days[6],
         'payment_date': days[8], 'dps': 10, 'replay_available': True}
    return SimpleNamespace(prices={'TEST': prices}, events={e['id']: e}, market_sessions=days), e, days


def test_automatic_mean_excludes_cum_and_ignores_old_timing_defaults():
    from backend.domain import SimulationRequest
    from backend.simulator import compare
    dataset, event, days = automatic_data()
    result = compare(dataset, SimulationRequest(timing_mode='payment_plus_2', capital=10219,
                     event_ids=[event['id']], compare=False))
    trade = result['primary']['trades'][0]
    assert trade['entry_price'] == 102.2
    assert trade['entry_date'] == days[5]
    assert trade['entry_reference_dates'] == days[:5]
    assert trade['shares'] == 0  # one lot costs10220, never round mean to102
    assert result['input']['end_date'] == days[10]
    result = compare(dataset, SimulationRequest(timing_mode='payment_plus_2', capital=10220,
                     event_ids=[event['id']], compare=False))
    trade = result['primary']['trades'][0]
    assert trade['shares'] == 100
    assert trade['exit_date'] is None
    assert trade['observation']['end_date'] == days[10]
    assert trade['settlement_date'] is None
    assert result['primary']['pending_sales'] is None
    assert trade['end_valuation']['pnl'] == 2780


def test_automatic_partial_window_stays_open_and_missing_reference_fails():
    import pytest
    from backend.domain import SimulationRequest
    from backend.simulator import simulate
    dataset, event, days = automatic_data()
    event['payment_date'] = '2026-01-15'
    req = SimulationRequest(timing_mode='payment_plus_2', capital=10220, event_ids=[event['id']])
    result = simulate(dataset, req)
    assert result['end_date'] == days[-1]
    assert result['trades'][0]['status'] == 'partial'
    assert result['trades'][0]['exit_date'] is None
    assert not result['trades'][0]['observation']['complete']
    del dataset.prices['TEST'][days[0]]
    with pytest.raises(ValueError, match='Tidak ada peristiwa'):
        simulate(dataset, req)
