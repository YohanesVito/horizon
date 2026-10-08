"""Research-only ex-date close model. Never use these diagnostics as live forecasts.

The cohort was selected and downloaded after the events. Year-ahead splits prevent
price-label leakage, but do not repair missing point-in-time dividend vintages.
"""

from collections import Counter
from math import isfinite
from statistics import mean, median

from .intelligence import valid_bar

VERSION = 'ex-date-pooled-pdr-v0.1'
MIN_TRAIN_EVENTS = 8  # Research guardrail, not a statistical validity threshold.


def observations(events):
    """Return audited cum/ex pairs; do not fill missing trading sessions."""
    rows, exclusions = [], Counter()
    for event in events:
        reasons = list(event['reasons'])
        bars = event['bars']
        dates = [bar['date'] for bar in bars]
        cum, ex = event.get('cum_date'), event['ex_date']
        if dates != sorted(set(dates)):
            reasons.append('Tanggal harga duplikat atau tidak berurutan')
        if cum not in dates or ex not in dates:
            reasons.append('Harga cum/ex tidak tersedia')
        if not reasons:
            cum_idx, ex_idx = dates.index(cum), dates.index(ex)
            if ex_idx != cum_idx + 1:
                reasons.append('Cum/ex bukan bar teramati yang berurutan')
            elif not all(valid_bar(b) for b in (bars[cum_idx], bars[ex_idx])):
                reasons.append('OHLCV cum/ex invalid')
        if reasons:
            exclusions.update(reasons)
            continue
        cum_close, ex_close, dps = bars[cum_idx]['close'], bars[ex_idx]['close'], event['dps']
        if not all(type(v) in (int, float) and isfinite(v) and v > 0 for v in (cum_close, ex_close, dps)):
            exclusions.update(['Harga atau DPS invalid'])
            continue
        if dps >= cum_close:
            exclusions.update(['DPS tidak lebih kecil dari harga cum; baseline full-DPS tidak valid'])
            continue
        rows.append({'event_id': event['id'], 'symbol': event['symbol'], 'cum_date': cum,
                     'ex_date': ex, 'cum_close': cum_close, 'ex_close': ex_close,
                     'dps': dps, 'observed_pdr': (cum_close-ex_close)/dps})
    return sorted(rows, key=lambda r: (r['ex_date'], r['event_id'])), dict(sorted(exclusions.items()))


def predict_ex_close(cum_close, dps, training, decision_date):
    """Fit only events whose ex-date strictly precedes the decision date."""
    if not all(isinstance(v, (int, float)) and isfinite(v) and v > 0 for v in (cum_close, dps)):
        raise ValueError('Cum close dan DPS harus positif dan finite.')
    eligible = [row for row in training if row['ex_date'] < decision_date]
    if len(eligible) < MIN_TRAIN_EVENTS:
        return None
    kappa = median(row['observed_pdr'] for row in eligible)
    estimate = cum_close - kappa*dps
    if estimate <= 0:
        return None
    return {'close': estimate, 'kappa': kappa, 'training_events': len(eligible),
            'training_latest_ex_date': max(row['ex_date'] for row in eligible)}


def _score(values):
    if not values:
        return None
    return {'n': len(values), 'mae_pct_of_cum': mean(abs(v) for v in values),
            'median_ae_pct_of_cum': median(abs(v) for v in values),
            'bias_pct_of_cum': mean(values)}


def retrospective_diagnostic(dataset):
    """Compare year-ahead pooled PDR with flat and full-DPS baselines.

    Every observation in one test year uses only labels from earlier years.
    This is a retrospective diagnostic, not an untouched or PIT holdout.
    """
    rows, exclusions = observations(dataset.events)
    retrieved_dates = sorted({source['retrieved_at'][:10] for source in getattr(dataset, 'sources', [])
                              if source.get('retrieved_at')})
    years = sorted({r['ex_date'][:4] for r in rows})
    evaluated, folds = [], []
    for year in years:
        test = [r for r in rows if r['ex_date'].startswith(year)]
        cutoff = f'{year}-01-01'
        train = [r for r in rows if r['ex_date'] < cutoff]
        if len(train) < MIN_TRAIN_EVENTS:
            folds.append({'year': int(year), 'training_events': len(train), 'test_events': len(test),
                          'status': 'insufficient_prior_events'})
            continue
        fold_errors = {'flat': [], 'full_dps': [], 'pooled_pdr': []}
        for row in test:
            model = predict_ex_close(row['cum_close'], row['dps'], train, row['cum_date'])
            if model is None:
                continue
            predictions = {'flat': row['cum_close'], 'full_dps': row['cum_close']-row['dps'],
                           'pooled_pdr': model['close']}
            errors = {key: (price-row['ex_close'])/row['cum_close']*100
                      for key, price in predictions.items()}
            for key, error in errors.items():
                fold_errors[key].append(error)
            evaluated.append({'event_id': row['event_id'], 'symbol': row['symbol'],
                              'cum_date': row['cum_date'], 'ex_date': row['ex_date'],
                              'cum_close': row['cum_close'], 'ex_close': row['ex_close'],
                              'dps': row['dps'], 'train_n': model['training_events'],
                              'train_latest_ex_date': model['training_latest_ex_date'],
                              'kappa': model['kappa'], 'predicted_ex_close': predictions,
                              'error_pct_of_cum': errors})
        folds.append({'year': int(year), 'training_events': len(train), 'test_events': len(test),
                      'evaluated_events': len(fold_errors['pooled_pdr']), 'status': 'retrospective',
                      'metrics': {key: _score(value) for key, value in fold_errors.items()}})
    by_symbol = {}
    for symbol in sorted({row['symbol'] for row in evaluated}):
        subset = [row for row in evaluated if row['symbol'] == symbol]
        by_symbol[symbol] = {name: _score([row['error_pct_of_cum'][name] for row in subset])
                             for name in ('flat', 'full_dps', 'pooled_pdr')}
    paired = [abs(row['error_pct_of_cum']['pooled_pdr']) - abs(row['error_pct_of_cum']['full_dps'])
              for row in evaluated]
    source_vintage = (
        f"Snapshot sumber diambil {retrieved_dates[0]}–{retrieved_dates[-1]}; "
        'vintage jadwal/DPS pada cum-date belum diverifikasi.'
        if retrieved_dates else 'Waktu pengambilan sumber tidak tersedia; vintage jadwal/DPS belum diverifikasi.'
    )
    return {'version': VERSION, 'dataset_version': dataset.version,
            'status': 'research_only', 'target': 'ex_date_close_from_cum_close',
            'audit': {'source_events': len(dataset.events), 'paired_events': len(rows),
                      'excluded_events': len(dataset.events)-len(rows), 'exclusion_reasons': exclusions,
                      'paired_by_symbol': dict(sorted(Counter(r['symbol'] for r in rows).items())),
                      'snapshot_retrieved_dates': [retrieved_dates[0], retrieved_dates[-1]] if retrieved_dates else None},
            'method': {'decision_point': 'setelah close cum-date', 'split': 'train ex-date tahun sebelumnya; test tahun berikutnya',
                       'pooled_model': 'median historis (cum close - ex close) / DPS, lintas sembilan emiten',
                       'minimum_train_events': MIN_TRAIN_EVENTS,
                       'error_unit': 'persen dari cum close; prediksi minus aktual'},
            'folds': folds, 'overall_metrics': {name: _score([r['error_pct_of_cum'][name] for r in evaluated])
                                               for name in ('flat', 'full_dps', 'pooled_pdr')},
            'by_symbol_metrics': by_symbol,
            'paired_wins_vs_full_dps': {'pooled_pdr': sum(diff < 0 for diff in paired),
                                        'full_dps': sum(diff > 0 for diff in paired),
                                        'ties': sum(diff == 0 for diff in paired)},
            'evaluated': evaluated,
            'release_blockers': [
                source_vintage,
                'Basis harga, DPS dan mata uang belum diaudit per event; sesi BEI resmi belum diverifikasi.',
                'Kohort emiten dipilih setelah melihat yield/hasil historis; 2025 bukan holdout yang belum pernah dilihat.',
                'Efek pasar pada cum→ex, ketidakpastian dan stabilitas antar-emiten belum dimodelkan atau divalidasi.',
            ],
            'label': 'Diagnostik retrospektif, bukan prediksi harga untuk transaksi. Di luar biaya transaksi, pajak, dan slippage.'}
