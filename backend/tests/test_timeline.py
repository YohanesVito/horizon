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


def test_verified_partial_history_does_not_need_five_years():
    event, bars, review = reviewed_period()
    valid = make_period(event, bars, ['source.json'], review)
    assert history_eligible([valid])
    assert history_eligible([valid, {**valid, 'id': 'TEST:2025-10-01'}])
    assert not history_eligible([])
    assert not history_eligible([valid, {**valid, 'eligible': False}])


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


def test_all_five_yield_candidates_have_as_is_timeline_previews():
    client = TestClient(app)
    catalog = client.get('/api/timeline').json()
    assert set(catalog['preview_symbols']) == {'DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS'}
    expected = {
        'DMAS': {2022: 2, 2023: 2, 2025: 1},
        'LPPF': {2021: 1, 2022: 1, 2023: 1, 2024: 1, 2025: 1},
        'ADRO': {2022: 1, 2023: 3, 2024: 3, 2025: 2},
        'CFIN': {2023: 1, 2025: 1},
        'RALS': {2022: 1, 2023: 1, 2024: 1, 2025: 1},
    }
    for symbol, year_counts in expected.items():
        response = client.get(f'/api/timeline/{symbol}?preview=true')
        assert response.status_code == 200
        data = response.json()
        assert data['preview'] and not data['eligible']
        assert {year: sum(p['year'] == year for p in data['history']) for year in year_counts} == year_counts
        assert len(data['history']) == sum(year_counts.values())
        assert len({p['id'] for p in data['history']}) == len(data['history'])
        assert all(p['cum_close'] > 0 and p['points'] and p['sources'] for p in data['history'])
        assert all(p['year'] in year_counts for p in data['history'])
        assert (bool(data['current']) == (symbol == 'LPPF'))
        if symbol == 'ADRO':
            november = next(p for p in data['history'] if p['ex_date'] == '2024-11-28')
            assert november['actual_through'] < '2024-12-30'
            assert 'Jendela harga berhenti sebelum ex-date dividen berikutnya.' in november['issues']


def test_missing_snapshot_keeps_catalog_empty(tmp_path):
    dataset = TimelineDataset(tmp_path)
    assert dataset.catalog()['companies'] == []
    assert dataset.catalog()['preview_symbols'] == []
