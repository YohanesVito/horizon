"""Retained historical research/calendars; rotation API is inactive."""
from copy import deepcopy
import pytest

from backend.domain import RotationRequest
from backend.intelligence import IntelligenceDataset
from backend.planner import plan_routes
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
