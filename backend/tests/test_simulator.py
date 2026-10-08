"""Independent observation invariants; fixtures are synthetic, never market claims."""
import pytest
from pydantic import ValidationError
from backend.domain import SimulationRequest
from backend.simulator import simulate, compare
from backend.tests.test_observation import automatic_data


def test_one_event_uses_full_capital_and_keeps_residual_cash():
    dataset, event, days = automatic_data()
    result = compare(dataset, SimulationRequest(capital=24000, event_ids=[event['id']]))
    trade = result['primary']['trades'][0]
    assert trade['starting_capital'] == 24000
    assert trade['shares'] == 200
    assert trade['residual_cash'] == 3560
    assert trade['end_valuation']['total_value'] == 29560
    assert trade['exit_date'] is None
    assert result['primary']['analysis_mode'] == 'independent_events'
    assert result['primary']['ending_nav'] is None
    assert result['primary']['curve'] == [] and result['primary']['ledger'] == []
    assert result['alternatives'] == []


def test_overlapping_events_each_get_full_budget_with_partial_second():
    dataset, first, days = automatic_data()
    second = {**first, 'id': 'NEXT:auto', 'symbol': 'NEXT', 'cum_date': days[6],
              'ex_date': days[7], 'payment_date': '2026-01-15'}
    dataset.events[second['id']] = second
    dataset.prices['NEXT'] = {d: {'open': 120, 'high': 125, 'low': 115, 'close': 120} for d in days}
    result = compare(dataset, SimulationRequest(capital=24000, event_ids=[first['id'], second['id']]))
    a, b = result['primary']['trades']
    assert a['starting_capital'] == b['starting_capital'] == 24000
    assert a['shares'] == b['shares'] == 200
    assert a['residual_cash'] == 3560 and b['residual_cash'] == 0
    assert a['end_valuation']['total_value'] == 29560
    assert b['end_valuation']['total_value'] == 26000
    assert b['status'] == 'partial'
    assert a['exit_date'] is b['exit_date'] is None
    assert result['primary']['ending_nav'] is None
    assert result['alternatives'] == []


@pytest.mark.parametrize('allocation', ['equal', 'rotation'])
def test_removed_strategies_are_not_accepted(allocation):
    with pytest.raises(ValidationError):
        SimulationRequest(event_ids=['TEST:auto'], allocation=allocation)
