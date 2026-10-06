"""Financial invariants using explicit synthetic fixtures; never shown as market data."""
from types import SimpleNamespace
from decimal import Decimal
from datetime import date
import pytest
from backend.domain import SimulationRequest
from backend.simulator import simulate, compare
from backend.data import Dataset

DAYS = ['2025-03-19', '2025-03-20', '2025-03-21', '2025-03-24', '2025-03-25', '2025-03-26', '2025-03-27', '2025-03-28']


def fixture(second=False):
    bars = {day: {'open': 90, 'close': 90} for day in DAYS}
    bars[DAYS[0]] = bars[DAYS[1]] = {'open': 100, 'close': 100}
    event = {'id': 'AAAA:2025-03-21', 'symbol': 'AAAA', 'cum_date': DAYS[1], 'ex_date': DAYS[2],
             'payment_date': DAYS[5], 'dps': 10, 'replay_available': True}
    d = SimpleNamespace(prices={'AAAA': bars}, events={event['id']: event}, market_sessions=DAYS)
    if second:
        other = {**event, 'id': 'BBBB:2025-03-25', 'symbol': 'BBBB', 'cum_date': DAYS[3], 'ex_date': DAYS[4], 'payment_date': DAYS[6]}
        d.events[other['id']] = other
        d.prices['BBBB'] = {day: {'open': 100, 'close': 100} for day in DAYS}
    return d


def request(**kwargs):
    return SimulationRequest(**{'capital': Decimal(10000), 'event_ids': ['AAAA:2025-03-21'],
                                'entry_sessions_before_cum': 0, 'exit_rule': 'ex_close',
                                'end_date': date(2025, 3, 28), **kwargs})


def test_entitlement_payment_and_sale_do_not_double_count():
    r = simulate(fixture(), request())
    assert r['dividends'] == 1000
    assert r['ending_nav'] == r['ending_cash'] == 10000
    assert r['gross_pnl'] == 0
    ex = next(c for c in r['curve'] if c['date'] == DAYS[2])
    assert ex['cash'] == 0 and ex['sale_receivable'] == 9000 and ex['dividend_receivable'] == 1000
    assert next(l['date'] for l in r['ledger'] if l['kind'] == 'settlement') == DAYS[4]
    assert r['trades'][0]['capital_days'] == 5  # cum date to T+2 settlement, calendar days


def test_sale_before_payment_preserves_dividend_right():
    r = simulate(fixture(), request(end_date=date(2025, 3, 24)))
    assert r['trades'][0]['status'] == 'sold'
    assert r['pending_dividends'] == 1000 and r['dividends'] == 1000
    assert r['ending_cash'] == 0
    assert r['ending_nav'] == 10000


def test_rotation_cannot_spend_unsettled_sale_or_dividend():
    r = simulate(fixture(True), request(event_ids=['AAAA:2025-03-21', 'BBBB:2025-03-25']))
    assert r['trades'][1]['status'] == 'skipped'
    assert all(p['cash'] >= 0 for p in r['curve'])


def test_close_bep_signal_executes_next_open_with_gap_risk():
    d = fixture()
    d.prices['AAAA'][DAYS[3]] = {'open': 90, 'close': 100}
    d.prices['AAAA'][DAYS[4]] = {'open': 95, 'close': 110}
    r = simulate(d, request(exit_rule='price_bep', max_holding_sessions=4))
    t = r['trades'][0]
    assert t['signal_date'] == DAYS[3]
    assert t['exit_date'] == DAYS[4] and t['exit_price'] == 95
    assert t['capital_pnl'] == -500


def test_terminal_signal_cannot_execute_beyond_horizon():
    d = fixture()
    d.prices['AAAA'][DAYS[3]] = {'open': 90, 'close': 100}
    r = simulate(d, request(exit_rule='price_bep', end_date=date(2025, 3, 24)))
    assert r['trades'][0]['status'] == 'holding'
    assert r['remaining_positions'] == 10000
    assert r['ending_nav'] == 11000


def test_below_one_lot_skips_without_fractional_shares():
    r = simulate(fixture(), request(capital=9999))
    assert r['trades'][0]['status'] == 'skipped'
    assert r['ending_cash'] == 9999 and r['dividends'] == 0


def test_unrecovered_forced_exit_at_limit():
    r = simulate(fixture(), request(exit_rule='price_bep', max_holding_sessions=2))
    assert r['trades'][0]['exit_date'] == DAYS[4]
    assert r['trades'][0]['signal_date'] is None


def test_comparison_uses_same_capital_end_and_conserves_wealth():
    result = compare(fixture(True), request(capital=30000, event_ids=['AAAA:2025-03-21', 'BBBB:2025-03-25']))
    assert {r['capital'] for r in result['alternatives']} == {30000}
    assert {r['end_date'] for r in result['alternatives']} == {'2025-03-28'}
    for r in result['alternatives']:
        assert r['ending_nav'] == pytest.approx(r['capital'] + sum(t['gross_pnl'] for t in r['trades']))
        for p in r['curve']:
            assert p['nav'] == pytest.approx(p['cash'] + p['positions'] + p['sale_receivable'] + p['dividend_receivable'])


def test_real_sectors_default_replay_and_window_restriction():
    d = Dataset()
    r = compare(d, SimulationRequest(event_ids=['BBCA:2025-03-21', 'BMRI:2025-04-14', 'LPPF:2025-04-22']))
    assert len(r['alternatives']) == 3
    assert r['primary']['trades'][1]['status'] == 'skipped'
    for a in r['alternatives']:
        assert a['ending_nav'] == pytest.approx(a['capital'] + sum(t['gross_pnl'] for t in a['trades']), abs=.01)
    with pytest.raises(ValueError):
        simulate(d, SimulationRequest(event_ids=['BBCA:2022-03-28']))


def test_duplicate_events_rejected():
    with pytest.raises(ValueError):
        request(event_ids=['AAAA:2025-03-21', 'AAAA:2025-03-21'])


@pytest.mark.parametrize('capital', ['0.000001', '1.00009', '1.00001'])
def test_idle_fractional_cash_never_creates_rounding_return(capital):
    result = simulate(fixture(), request(capital=capital))
    assert result['trades'][0]['status'] == 'skipped'
    assert result['gross_pnl'] == 0
    assert result['return_pct'] == 0
    assert result['ending_cash'] == result['capital']
