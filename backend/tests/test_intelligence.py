from datetime import date, timedelta
from decimal import Decimal
import json

import pytest
from pydantic import ValidationError
from backend.domain import FinancialLogic, ScenarioRequest
from backend.intelligence import IntelligenceDataset, kaplan_meier, rank, scenario, wilson


def test_wilson_does_not_turn_zero_losses_into_certainty():
    assert wilson(0, 0) is None
    assert wilson(0, 10) == pytest.approx([0, 27.753279986288917])
    assert wilson(10, 10) == pytest.approx([72.24672001371109, 100])
    assert wilson(5, 10) == pytest.approx([23.659309051259, 76.340690948741])


def test_km_tied_censors_are_in_risk_set_and_missing_median_stays_null():
    # t1: one of four recovers and one censors. t2: one of two recovers.
    km = kaplan_meier([(1, True), (1, False), (2, True), (3, False)], 3)
    assert km['curve'][1]['recovery_pct'] == 25
    assert km['curve'][2]['recovery_pct'] == 62.5
    assert km['median_sessions'] == 2
    assert kaplan_meier([(20, False), (2, True), (20, False)], 20)['median_sessions'] is None
    assert kaplan_meier([], 20)['curve'][0]['recovery_pct'] is None
    assert kaplan_meier([(2, False), (3, False)], 20)['curve'][4]['recovery_pct'] is None


def fixture_event():
    bars = []
    for i, close in enumerate([100, 99, 93, 98, 100, 97, 105]):
        bars.append({'symbol': 'TEST.JK', 'date': str(date(2025, 1, 1)+timedelta(days=i)),
                     'open': close, 'high': close, 'low': close, 'close': close, 'volume': 100})
    return {'id': 'TEST:2025-01-03', 'symbol': 'TEST', 'ex_date': '2025-01-03', 'cum_date': '2025-01-02',
            'payment_date': '2025-02-01', 'dps': 5, 'reasons': [], 'bars': bars, 'next_ex_date': None}


def test_bep_definitions_entry_rule_and_horizon_loss_are_separate():
    obj = object.__new__(IntelligenceDataset)
    result = obj.observe(fixture_event(), 0, 3)  # entry 99; ex93; t1=98; t2=100; t3=97
    assert result['entry_price'] == 99
    assert result['price_bep_session'] == 2
    assert result['total_bep_session'] == 1
    assert result['gross_return_pct'] == pytest.approx(3/99*100)
    assert result['dividend_paid_at_horizon'] is False
    event = fixture_event()
    event['bars'][4]['volume'] = 0
    result = obj.observe(event, 0, 3)
    assert result['observed_sessions'] == 1
    assert not result['complete']
    assert result['trap'] is None  # missing history is neither a loss nor a success
    assert result['price_bep_session'] is None


def test_next_dividend_censors_without_double_counting_entitlements():
    obj = object.__new__(IntelligenceDataset)
    event = fixture_event()
    event['next_ex_date'] = '2025-01-05'
    result = obj.observe(event, 0, 3)
    assert result['observed_sessions'] == 1
    assert not result['complete']


def write_snapshot(path, data):
    path.write_text(json.dumps({'result': data}))


def test_import_quarantines_conflict_and_split_instead_of_rescaling(tmp_path):
    event = fixture_event()
    dividend = {'ex_date': event['ex_date'], 'dividend_amount': 5, 'payment_date': event['payment_date']}
    write_snapshot(tmp_path/'actions-BBCA.json', {'corporate_actions': {'dividend': [dividend], 'stock_split': [{'date': '2025-08-01', 'split_ratio': 5}]}})
    write_snapshot(tmp_path/'calendar-2025-01-01.json', {'dividend': [{'symbol': 'BBCA.JK', **dividend, 'dividend_amount': 6, 'cum_date': event['cum_date']}]})
    data = IntelligenceDataset(tmp_path)
    row = data.analyze()['companies'][0]['events'][0]
    assert not row['eligible']
    assert 'Konflik Sectors: dividend_amount' in row['reasons']
    assert any('split' in reason for reason in row['reasons'])


def request(**overrides):
    return ScenarioRequest(symbol='BBCA', capital=Decimal('1000'), entry_price=Decimal('5'), dps=Decimal('.2'),
                           entry_date=date(2026, 11, 1), cum_date=date(2026, 11, 9), ex_date=date(2026, 11, 10),
                           recording_date=date(2026, 11, 11), payment_date=date(2026, 12, 1), valuation_date=date(2026, 11, 30), **overrides)


def test_analog_uses_new_dps_and_keeps_receivable_out_of_cash():
    analysis = {'dataset_version': 'test', 'entry_offset': 5, 'horizon': 20, 'companies': [{'symbol': 'BBCA', 'events': [
        {'id': 'old', 'eligible': True, 'complete': True, 'last_date': '2025-12-30', 'ex_date': '2025-12-01', 'price_return_pct': -10, 'price_path_pct': [-10]*21, 'dps': 999, 'price_bep_session': None},
        {'id': 'future', 'eligible': True, 'complete': True, 'last_date': '2027-12-30', 'ex_date': '2027-12-01', 'price_return_pct': 100, 'price_bep_session': 0}]}]}
    result = scenario(analysis, request())
    assert result['analog_count'] == 1
    assert result['shares'] == 200
    assert result['dividend_cash'] == 0
    assert result['dividend_receivable'] == 40
    assert result['rows'][0]['ending_value'] == 940
    assert result['rows'][0]['gross_pnl'] == -60
    assert result['trajectory'][-1]['median'] == -60
    assert result['worst_observed_pnl'] == -60
    assert result['price_bep'] == 5 and result['total_bep'] == 4.8


def test_no_future_analog_or_invalid_dates_or_insufficient_lot():
    req = request()
    with pytest.raises(ValidationError):
        ScenarioRequest.model_validate({**req.model_dump(), 'payment_date': '2026-10-01'})
    with pytest.raises(ValueError, match='Tidak ada analog'):
        scenario({'companies': [{'symbol': 'BBCA', 'events': []}]}, req)
    with pytest.raises(ValueError, match='satu lot'):
        scenario({'companies': [{'symbol': 'BBCA', 'events': [
            {'eligible': True, 'complete': True, 'last_date': '2025-01-01'}]}]},
                 ScenarioRequest.model_validate({**req.model_dump(), 'capital': '1'}))


def test_rank_filters_uncertainty_not_point_estimate():
    common = {'complete_events': 4, 'trap_pct': 0, 'median_return_pct': 5, 'worst_return_pct': 1, 'price_recovery': {'median_sessions': 2}}
    analysis = {'dataset_version': 'test', 'companies': [
        {**common, 'symbol': 'BBCA', 'trap_interval': [0, 90]},
        {**common, 'symbol': 'BBRI', 'trap_interval': [0, 45]},
    ]}
    result = rank(analysis, FinancialLogic(maximum_loss_upper_pct=50))
    assert [r['symbol'] for r in result['ranked']] == ['BBRI']
    assert result['excluded'][0]['symbol'] == 'BBCA'


def test_real_cohort_keeps_all_events_and_audits_exclusions():
    result = IntelligenceDataset().analyze()
    assert result['audit'] == {'symbols': 9, 'events': 48, 'eligible': 44, 'complete': 43, 'excluded': 4}
    assert len(result['sources']) == 74  # 9 actions, 17 calendar, 48 windows
    for company in result['companies']:
        assert company['total_events'] == company['eligible_events']+company['excluded_events']
        assert company['complete_events']+company['early_censored'] == company['eligible_events']
