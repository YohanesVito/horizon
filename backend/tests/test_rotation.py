"""Temporal isolation, cash conservation and repeated-dividend regression checks."""
from copy import deepcopy
from datetime import date
from types import SimpleNamespace
import pytest

from backend.domain import RotationRequest, SimulationRequest
from backend.intelligence import IntelligenceDataset
from backend.planner import plan_routes, replay_routes
from backend.simulator import simulate
from backend.unified import UnifiedDataset


@pytest.fixture(scope='module')
def data():
    return UnifiedDataset(IntelligenceDataset())


def test_canonical_events_and_index_gaps(data):
    canonical = {e['id'] for e in data.intelligence.events if e['ex_date'].startswith('2025')}
    assert set(data.events) == canonical
    assert len(canonical) == 12
    assert data.session_repairs == ['2025-05-02', '2025-05-06', '2025-05-07', '2025-10-20']
    assert data.settlement('2025-04-30') == '2025-05-05'
    assert all(e['replay_available'] for e in data.events.values())


def test_cutoff_censors_unfinished_event_without_future_outcomes(data):
    analysis = data.intelligence.analyze(as_of='2025-03-24')
    rows = [e for c in analysis['companies'] for e in c['events']]
    bbca = next(e for e in rows if e['id'] == 'BBCA:2025-03-21')
    assert bbca['eligible'] and not bbca['complete']
    assert bbca['last_date'] == '2025-03-21'
    assert bbca['gross_return_pct'] is None
    assert all(e['ex_date'] < '2025-03-24' for e in rows)
    assert all(e['last_date'] < '2025-03-24' for e in rows if e['eligible'])


def test_future_price_changes_cannot_choose_different_routes(data):
    req = RotationRequest()
    before = plan_routes(data, req)
    changed = deepcopy(data)
    for event in changed.intelligence.events:
        for b in event['bars']:
            if b['date'] >= str(req.start_date):
                for k in ('open', 'high', 'low', 'close'):
                    b[k] *= 7
    for prices in changed.prices.values():
        for day, b in prices.items():
            if day >= str(req.start_date):
                for k in ('open', 'high', 'low', 'close'):
                    b[k] *= 7
    after = plan_routes(changed, req)
    assert after['ranking'] == before['ranking']
    assert after['routes'] == before['routes']
    assert all(c['evidence_latest_observation'] < str(req.start_date) for c in before['candidates'])


def test_verified_calendar_and_strict_logic_are_explained(data):
    plan = plan_routes(data, RotationRequest(allow_calendar_assumption=False))
    assert not plan['routes']
    assert all(any('Timestamp' in r for r in e['reasons']) for e in plan['excluded'])
    req = RotationRequest()
    req.rules.minimum_samples = 100
    assert not plan_routes(data, req)['routes']
    with pytest.raises(ValueError):
        plan_routes(data, RotationRequest(symbols=['XXXX']))


def test_route_comparisons_share_dates_and_conserve_money(data):
    plan = plan_routes(data, RotationRequest())
    assert len(plan['routes']) == 3
    result = replay_routes(data, plan)
    assert result['cash_baseline']['gross_pnl'] == 0
    for route in result['routes']:
        for r in route['comparison']['alternatives']:
            assert (r['capital'], r['start_date'], r['end_date']) == (1e8, '2025-03-01', '2025-06-30')
            assert r['ending_nav'] == pytest.approx(r['capital'] + sum(t['gross_pnl'] for t in r['trades']), abs=.01)
            for p in r['curve']:
                assert p['cash'] >= 0
                assert p['nav'] == pytest.approx(p['cash'] + p['positions'] + p['sale_receivable'] + p['dividend_receivable'], abs=.01)
    with pytest.raises(ValueError, match='Dataset berubah'):
        replay_routes(data, {**plan, 'dataset_version': 'old'})


def repeated_fixture():
    days = ['2025-03-19', '2025-03-20', '2025-03-21', '2025-03-24', '2025-03-25', '2025-03-26', '2025-03-27', '2025-03-28']
    first = {'id': 'AAAA:2025-03-21', 'symbol': 'AAAA', 'cum_date': days[1], 'ex_date': days[2], 'payment_date': days[5], 'dps': 10, 'replay_available': True}
    second = {**first, 'id': 'AAAA:2025-03-25', 'cum_date': days[3], 'ex_date': days[4], 'payment_date': days[6], 'dps': 5}
    return SimpleNamespace(multi_event=True, replay_start='2025-01-01', replay_end='2025-12-31',
                           prices={'AAAA': {d: {'open': 100, 'close': 100} for d in days}},
                           market_sessions=days, events={e['id']: e for e in [first, second]}, validate_coverage=lambda *args: None)


def test_multiple_lots_get_each_eligible_dividend_once():
    d = repeated_fixture()
    r = simulate(d, SimulationRequest(capital=20000, event_ids=list(d.events), allocation='equal',
                                     entry_sessions_before_cum=0, exit_rule='holding_period', max_holding_sessions=60,
                                     end_date=date(2025, 3, 26)))
    assert [t['shares'] for t in r['trades']] == [100, 100]
    assert [t['dividend'] for t in r['trades']] == [1500, 500]
    assert r['ending_nav'] == 22000
    assert r['ending_cash'] == r['pending_dividends'] == 1000
    assert len([l for l in r['ledger'] if l['kind'] == 'entitlement']) == 3


def test_unselected_dividend_still_belongs_to_held_lot():
    d = repeated_fixture()
    r = simulate(d, SimulationRequest(capital=20000, event_ids=[next(iter(d.events))],
                                     entry_sessions_before_cum=0, exit_rule='holding_period', max_holding_sessions=60,
                                     end_date=date(2025, 3, 26)))
    assert r['dividends'] == 3000
    assert r['ending_cash'] == 2000 and r['pending_dividends'] == 1000


def test_payment_exit_respects_holding_limit_and_preserves_receivable():
    d = repeated_fixture()
    r = simulate(d, SimulationRequest(capital=10000, event_ids=[next(iter(d.events))],
                                     entry_sessions_before_cum=0, exit_rule='payment_close', max_holding_sessions=1,
                                     end_date=date(2025, 3, 25)))
    assert r['trades'][0]['exit_date'] == '2025-03-24'
    assert r['pending_dividends'] == 1000 and r['pending_sales'] == 10000
    assert r['ending_cash'] == 0


def test_missing_price_session_is_not_silently_filled(data):
    d = deepcopy(data)
    del d.prices['BBCA']['2025-03-20']
    with pytest.raises(ValueError, match='harga/volume'):
        simulate(d, SimulationRequest(event_ids=['BBCA:2025-03-21']))


def test_year_end_sale_and_dividend_remain_receivables(data):
    result = simulate(data, SimulationRequest(event_ids=['ADRO:2025-12-30'], entry_sessions_before_cum=0,
                                             exit_rule='ex_close', start_date=date(2025, 12, 1), end_date=date(2025, 12, 31)))
    trade = result['trades'][0]
    assert trade['status'] == 'sold' and trade['exit_date'] == '2025-12-30'
    assert trade['settlement_date'] > result['end_date']
    assert result['pending_sales'] == pytest.approx(trade['exit_price'] * trade['shares'])
    assert result['pending_dividends'] == result['dividends'] > 0
    assert not any(l['kind'] in ('dividend', 'settlement') for l in result['ledger'])


def test_cash_release_on_entry_date_can_fund_next_trade():
    data = repeated_fixture()
    a = next(iter(data.events.values()))
    # First lot sells Friday21, settles Tuesday25; the second enters at that close.
    b = {**a, 'id': 'BBBB:2025-03-26', 'symbol': 'BBBB', 'cum_date': '2025-03-25', 'ex_date': '2025-03-26', 'payment_date': '2025-03-28'}
    data.events = {a['id']: a, b['id']: b}
    data.prices['BBBB'] = deepcopy(data.prices['AAAA'])
    r = simulate(data, SimulationRequest(capital=10000, event_ids=list(data.events), entry_sessions_before_cum=0,
                                        exit_rule='ex_close', end_date=date(2025, 3, 28)))
    assert [t['shares'] for t in r['trades']] == [100, 100]
    assert r['trades'][0]['settlement_date'] == r['trades'][1]['entry_date']
    assert r['dividends'] == 2000


def test_same_entry_date_has_deterministic_issuer_priority():
    data = repeated_fixture()
    a = next(iter(data.events.values()))
    b = {**a, 'id': 'BBBB:2025-03-21', 'symbol': 'BBBB'}
    data.events = {a['id']: a, b['id']: b}
    data.prices['BBBB'] = deepcopy(data.prices['AAAA'])
    body = SimulationRequest(capital=10000, event_ids=[b['id'], a['id']], entry_sessions_before_cum=0,
                             exit_rule='ex_close', end_date=date(2025, 3, 28))
    r = simulate(data, body)
    assert [(t['symbol'], t['status']) for t in r['trades']] == [('AAAA', 'sold'), ('BBBB', 'skipped')]
