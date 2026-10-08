from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.ex_date_forecast import observations, predict_ex_close, retrospective_diagnostic
from backend.intelligence import IntelligenceDataset
from backend.main import app


def event(year, number, pdr=1):
    cum, ex = f'{year}-03-{number:02d}', f'{year}-03-{number+1:02d}'
    close, dps = 100, 10
    def bar(day, price):
        return {'symbol': 'TEST.JK', 'date': day, 'open': price, 'high': price,
                'low': price, 'close': price, 'volume': 100}
    return {'id': f'TEST:{ex}', 'symbol': 'TEST', 'cum_date': cum,
            'ex_date': ex, 'dps': dps, 'reasons': [],
            'bars': [bar(cum, close), bar(ex, close-pdr*dps)]}


def test_folds_use_only_prior_year_even_when_test_year_has_earlier_events():
    source = SimpleNamespace(events=[*(event(2022, i) for i in range(1, 9)),
                                     event(2023, 1, 3), event(2023, 4, 3)], version='test')
    result = retrospective_diagnostic(source)
    assert [fold['status'] for fold in result['folds']] == ['insufficient_prior_events', 'retrospective']
    assert len(result['evaluated']) == 2
    assert all(row['train_n'] == 8 and row['kappa'] == 1 for row in result['evaluated'])
    assert all(row['train_latest_ex_date'] < row['cum_date'] for row in result['evaluated'])
    assert result['overall_metrics']['pooled_pdr']['n'] == 2


def test_predict_excludes_same_day_and_future_labels():
    rows, _ = observations([*(event(2022, i) for i in range(1, 9)), event(2024, 1, 3)])
    model = predict_ex_close(100, 10, rows, '2023-03-01')
    assert model == {'close': 90, 'kappa': 1, 'training_events': 8,
                     'training_latest_ex_date': '2022-03-09'}
    assert predict_ex_close(100, 10, rows, '2022-03-09') is None
    with pytest.raises(ValueError):
        predict_ex_close(0, 10, rows, '2023-03-01')


def test_invalid_and_nonadjacent_pairs_are_excluded_without_imputation():
    bad = event(2023, 1)
    bad['bars'].insert(1, {**bad['bars'][0], 'date': '2023-03-02'})
    # A valid intervening bar means cum and ex are not adjacent observations.
    bad['bars'][-1]['date'] = '2023-03-03'
    bad['ex_date'] = '2023-03-03'
    bad['id'] = 'TEST:2023-03-03'
    missing = event(2023, 4)
    missing['bars'].pop()
    rows, reasons = observations([bad, missing])
    assert rows == []
    assert reasons['Cum/ex bukan bar teramati yang berurutan'] == 1
    assert reasons['Harga cum/ex tidak tersedia'] == 1


def test_real_snapshot_diagnostic_remains_research_only_and_timeline_forecast_empty():
    result = retrospective_diagnostic(IntelligenceDataset())
    assert result['audit']['source_events'] == 48
    assert result['audit']['paired_events'] == 44
    assert result['audit']['excluded_events'] == 4
    assert result['audit']['snapshot_retrieved_dates'] == ['2026-10-06', '2026-10-06']
    assert len(result['evaluated']) == 36
    assert result['paired_wins_vs_full_dps'] == {'pooled_pdr': 22, 'full_dps': 14, 'ties': 0}
    assert result['by_symbol_metrics']['LPPF']['pooled_pdr']['mae_pct_of_cum'] > result['by_symbol_metrics']['LPPF']['full_dps']['mae_pct_of_cum']
    assert result['status'] == 'research_only'
    assert result['release_blockers']
    with TestClient(app) as client:
        response = client.get('/api/research/ex-date')
        assert response.status_code == 200
        assert response.json()['version'] == result['version']
        timeline = client.get('/api/timeline/LPPF?preview=true').json()
        assert timeline['forecast'] == {'status': 'not_available', 'points': [],
                                        'message': 'Prediksi belum tersedia. Perhitungan akan dikembangkan pada tahap berikutnya.'}
