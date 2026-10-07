from copy import deepcopy
from fastapi.testclient import TestClient
from backend.main import app
from backend.timeline import TimelineDataset, make_period, history_eligible


def reviewed_period():
    event = {'symbol': 'TEST.JK', 'declaration_date': '2025-04-01',
             'cum_date': '2025-04-03', 'ex_date': '2025-04-04',
             'recording_date': '2025-04-07', 'payment_date': '2025-04-09',
             'dividend_amount': 100}
    bars = [{'date': day, 'close': close} for day, close in [
        ('2025-04-01', 900), ('2025-04-03', 1000),
        ('2025-04-04', 950), ('2025-04-07', 980), ('2025-04-09', 990)]]
    review = {key: True for key in ['announcement_link_verified', 'sessions_verified', 'basis_verified', 'cycle_verified']}
    review['cycle_key'] = 'final'
    return event, bars, review


def test_price_normalization_and_calendar_alignment_are_not_total_return():
    event, bars, review = reviewed_period()
    period = make_period(event, bars, ['source.json'], review)
    assert period['eligible']
    points = {p['date']: p for p in period['points']}
    assert points['2025-04-03']['change_pct'] == 0
    assert points['2025-04-04']['day'] == 0
    assert points['2025-04-04']['change_pct'] == -5  # Cash dividend is not added to price.
    assert points['2025-04-07']['day'] == 3  # Weekend spacing is preserved.
    assert period['phases'][0]['date'] is None  # No fabricated RUPS.


def test_complete_calendar_is_insufficient_and_missing_base_is_not_zero():
    event, bars, review = reviewed_period()
    period = make_period(event, bars, ['source.json'])
    assert not period['eligible']
    no_cum = make_period(event, [b for b in bars if b['date'] != event['cum_date']], ['source.json'], review)
    assert not no_cum['eligible']
    assert no_cum['cum_close'] is None
    assert all(p['change_pct'] is None for p in no_cum['points'])


def test_bad_prices_dates_and_missing_window_cannot_pass_gate():
    event, bars, review = reviewed_period()
    for bad in [0, float('nan'), float('inf'), -10]:
        altered = deepcopy(bars)
        altered[1]['close'] = bad
        result = make_period(event, altered, ['source.json'], review)
        assert not result['eligible']
        assert result['cum_close'] is None
    assert not make_period({**event, 'payment_date': '2025-04-02'}, bars, ['source.json'], review)['eligible']
    assert not make_period(event, bars[:-1], ['source.json'], review)['eligible']
    assert not make_period(event, bars[1:], ['source.json'], review)['eligible']


def test_five_year_gate_rejects_missing_duplicate_or_unreviewed_cycles():
    event, bars, review = reviewed_period()
    valid = make_period(event, bars, ['source.json'], review)
    periods = [{**valid, 'year': year} for year in range(2021, 2026)]
    assert history_eligible(periods)
    assert not history_eligible(periods[:-1])
    assert not history_eligible(periods + [periods[0]])
    assert not history_eligible([{**p, 'cycle_key': 'interim'} if p['year'] == 2023 else p for p in periods])
    assert not history_eligible([{**p, 'eligible': False} if p['year'] == 2023 else p for p in periods])


def test_sourced_preview_is_separate_from_catalog_and_forecast_is_empty():
    client = TestClient(app)
    catalog = client.get('/api/timeline').json()
    assert catalog['history_years'] == [2021, 2022, 2023, 2024, 2025]
    assert catalog['companies'] == []
    assert catalog['calendar_candidates'] == 170
    assert client.get('/api/timeline/LPPF').status_code == 422
    assert client.get('/api/timeline/UNKNOWN?preview=true').status_code == 404
    payload = client.get('/api/timeline/lppf?preview=true').json()
    assert payload['preview'] and not payload['eligible']
    assert len(payload['history']) == 5
    assert sum(len(p['points']) for p in payload['history']) == 272
    assert payload['forecast']['points'] == []
    assert payload['forecast']['status'] == 'not_available'
    assert all(p['year'] == 2026 for p in payload['current'])
    assert all(p['actual_through'] == max(b['date'] for b in p['points']) for p in payload['current'])
    assert all(p['sources'] for p in payload['history'])


def test_missing_snapshot_keeps_catalog_empty(tmp_path):
    dataset = TimelineDataset(tmp_path)
    assert dataset.catalog()['companies'] == []
    assert dataset.catalog()['preview_symbols'] == []
