"""Reproduce F-02c data gates and frozen issuer-shrinkage research comparison.

No provider fetch or live forecast. Primary-source facts are manually transcribed
in this file, with URLs and publication dates retained in the output.
"""

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean, median

from backend.data import ROOT
from backend.ex_date_forecast import MIN_TRAIN_EVENTS, observations, predict_ex_close
from backend.intelligence import IntelligenceDataset, RAW
from work.verify_ex_date_2026 import report as lppf_2026_report

OUTPUT = ROOT / 'outputs/forecast/ex-date-f02c-audit.json'
EXPECTED_DATASET = 'intelligence-8a6d340ad419b922'
PRIOR_WEIGHT = 4
EXTERNAL_LPPF_2026 = {
    'source': 'https://intervest.io/symbol/LPPF/historical',
    'cum_date': '2026-04-23', 'cum_close': 1940,
    'ex_date': '2026-04-24', 'ex_close': 1650,
}
PRIMARY_LPPF = {
    'LPPF:2022-04-14': {
        'notice_date': '2022-04-06', 'cum': '2022-04-13', 'ex': '2022-04-14',
        'dps': 250, 'recording': '2022-04-18', 'payment': '2022-05-06',
        'url': 'https://www.ksei.co.id/Announcement/Files/LPPF_DIV_20220418_ID.pdf',
        'revision_archive_date': '2022-04-12',
        'revision_archive_url': 'https://matahari.com/pages/corporate-announcements',
        'current_issuer_payment': '2022-04-28',
        'current_issuer_url': 'https://matahari.com/pages/dividends-en',
    },
    'LPPF:2023-04-10': {
        'notice_date': '2023-03-31', 'cum': '2023-04-06', 'ex': '2023-04-10',
        'dps': 525, 'recording': '2023-04-11', 'payment': '2023-04-17',
        'url': 'https://www.ksei.co.id/Announcement/Files/LPPF_DIV_20230411_ID.pdf',
    },
    'LPPF:2024-04-22': {
        'notice_date': '2024-04-04', 'cum': '2024-04-19', 'ex': '2024-04-22',
        'dps': 200, 'recording': '2024-04-23', 'payment': '2024-04-29',
        'url': 'https://www.ksei.co.id/Announcement/Files/LPPF_DIV_20240423_ENG.pdf',
    },
    'LPPF:2025-04-22': {
        # The notice is dated April 10; the issuer archive lists it on April 16.
        'notice_date': '2025-04-16', 'cum': '2025-04-21', 'ex': '2025-04-22',
        'dps': 300, 'recording': '2025-04-23', 'payment': '2025-04-29',
        'url': 'https://cdn.shopify.com/s/files/1/0666/9212/0727/files/Schedule_of_Distribution_of_Final_Dividend_FY_2024.pdf?v=1751347947',
        'archive_url': 'https://matahari.com/pages/corporate-announcements',
    },
}


def _files(event):
    result = []
    for name in event['sources']:
        path = RAW / name
        metadata = json.loads(path.read_text())
        result.append({'file': str(path.relative_to(ROOT)),
                       'sha256': sha256(path.read_bytes()).hexdigest(),
                       'retrieved_at': metadata.get('retrieved_at'),
                       'transport': metadata.get('transport', metadata.get('tool', 'Sectors REST calendar'))})
    return result


def audit_events(dataset, rows):
    row_ids = {r['event_id'] for r in rows}
    audits = []
    for event in dataset.events:
        ref = PRIMARY_LPPF.get(event['id'])
        provider = 'pass' if event['id'] in row_ids else 'excluded'
        official = 'unknown'
        note = None
        if ref:
            if (event['cum_date'], event['ex_date'], event['dps'], event['recording_date']) != (
                    ref['cum'], ref['ex'], ref['dps'], ref['recording']):
                official = 'conflict'
                note = 'DPS atau tanggal cum/ex/recording tidak cocok dengan dokumen primer.'
            elif ref['notice_date'] > event['cum_date']:
                official = 'late_notice'
                note = 'Dokumen resmi terbit setelah keputusan cum-close.'
            elif event['payment_date'] != ref['payment']:
                official = 'revision_unresolved'
                note = ('LPPF 2022: KSEI 6 April mencantumkan pembayaran 6 Mei; '
                        'snapshot Sectors dan tabel emiten sekarang 28 April. Arsip emiten '
                        'mencatat revisi 12 April tetapi isi dokumen revisi belum diperiksa.')
            else:
                official = 'pass_notice_before_cum'
        audits.append({
            'event_id': event['id'], 'symbol': event['symbol'],
            'cum_date': event['cum_date'], 'ex_date': event['ex_date'],
            'dps': event['dps'], 'payment_date': event['payment_date'],
            'gates': {'provider_internal': provider, 'official_dividend': official,
                      'external_close_display': 'unknown', 'price_basis': 'unknown',
                      'point_in_time': 'unknown'},
            'exclusion_reasons': event['reasons'], 'source_files': _files(event),
            'official_reference': ref, 'note': note,
        })
    return audits


def _predictions(row, training):
    model = predict_ex_close(row['cum_close'], row['dps'], training, row['cum_date'])
    if model is None:
        return None
    same = [r['observed_pdr'] for r in training
            if r['symbol'] == row['symbol'] and r['ex_date'] < row['cum_date']]
    issuer_kappa = median(same) if same else model['kappa']
    shrunk_kappa = (PRIOR_WEIGHT*model['kappa'] + len(same)*issuer_kappa) / (PRIOR_WEIGHT+len(same))
    prices = {'flat': row['cum_close'], 'full_dps': row['cum_close']-row['dps'],
              'pooled': model['close'], 'issuer_shrunk': row['cum_close']-shrunk_kappa*row['dps']}
    if any(price <= 0 for price in prices.values()):
        raise ValueError(f"Prediksi harga tidak positif pada {row['event_id']}")
    error = {key: (value-row['ex_close'])/row['cum_close']*100 for key, value in prices.items()}
    return {'event_id': row['event_id'], 'symbol': row['symbol'],
            'cum_date': row['cum_date'], 'ex_date': row['ex_date'],
            'observed_ex_close': row['ex_close'], 'training_n': model['training_events'],
            'training_latest_ex_date': model['training_latest_ex_date'],
            'issuer_training_n': len(same), 'kappa_pooled': model['kappa'],
            'kappa_issuer_shrunk': shrunk_kappa, 'predicted_close': prices,
            'signed_error_pct_of_cum': error,
            'absolute_error_pct_of_cum': {key: abs(value) for key, value in error.items()}}


def _metrics(items):
    if not items:
        return None
    methods = ('flat', 'full_dps', 'pooled', 'issuer_shrunk')
    result = {'n': len(items), 'mae_pct_of_cum': {}, 'median_ae_pct_of_cum': {},
              'wins_vs_full_dps': {}}
    for method in methods:
        values = [item['absolute_error_pct_of_cum'][method] for item in items]
        result['mae_pct_of_cum'][method] = mean(values)
        result['median_ae_pct_of_cum'][method] = median(values)
        if method != 'full_dps':
            diff = [value-item['absolute_error_pct_of_cum']['full_dps']
                    for value, item in zip(values, items)]
            result['wins_vs_full_dps'][method] = {
                'wins': sum(v < -1e-12 for v in diff),
                'losses': sum(v > 1e-12 for v in diff),
                'ties': sum(abs(v) <= 1e-12 for v in diff),
            }
    return result


def evaluate(rows):
    evaluated = []
    folds = []
    for year in (2023, 2024, 2025):
        train = [row for row in rows if row['ex_date'] < f'{year}-01-01']
        test = [row for row in rows if row['ex_date'].startswith(str(year))]
        if len(train) < MIN_TRAIN_EVENTS:
            raise ValueError(f'Train tahun {year} kurang dari minimum yang dibekukan.')
        results = [_predictions(row, train) for row in test]
        if any(result is None for result in results):
            raise ValueError(f'Model gagal untuk event tahun {year}; jangan buang event.')
        evaluated += results
        folds.append({'year': year, 'training_n': len(train), 'metrics': _metrics(results)})
    by_symbol = defaultdict(list)
    for result in evaluated:
        by_symbol[result['symbol']].append(result)
    return {'folds': folds, 'metrics': _metrics(evaluated),
            'by_symbol': {symbol: _metrics(items) for symbol, items in sorted(by_symbol.items())},
            'evaluated': evaluated}


def report():
    dataset = IntelligenceDataset()
    if dataset.version != EXPECTED_DATASET:
        raise ValueError('Digest kohort berubah; protokol F-02c perlu ditinjau ulang.')
    rows, exclusions = observations(dataset.events)
    if len(dataset.events) != 48 or len(rows) != 44:
        raise ValueError('Jumlah event berubah; protokol F-02c perlu ditinjau ulang.')
    audits = audit_events(dataset, rows)
    comparison = evaluate(rows)
    lppf = lppf_2026_report()
    added = {'event_id': lppf['event_id'], 'symbol': 'LPPF',
             'cum_close': lppf['observed']['cum_close_idr'],
             'ex_close': lppf['observed']['ex_close_idr'],
             'dps': lppf['observed']['dps_idr'],
             'cum_date': lppf['official']['cum_regular'],
             'ex_date': lppf['official']['ex_regular']}
    lppf_result = _predictions(added, rows)
    if lppf_result is None:
        raise ValueError('Model gagal untuk event LPPF 2026.')
    displayed_prices_match = all((added['cum_date'] == EXTERNAL_LPPF_2026['cum_date'],
                                  added['cum_close'] == EXTERNAL_LPPF_2026['cum_close'],
                                  added['ex_date'] == EXTERNAL_LPPF_2026['ex_date'],
                                  added['ex_close'] == EXTERNAL_LPPF_2026['ex_close']))
    source_counts = Counter(audit['gates']['official_dividend'] for audit in audits)
    return {
        'status': 'research_only_partial_data_audit',
        'protocol': 'docs/development/EX_DATE_F02C_PROTOCOL.md',
        'dataset_version': dataset.version, 'source_events': len(dataset.events),
        'eligible_events': len(rows), 'excluded_reasons': exclusions,
        'official_dividend_gate_counts': dict(sorted(source_counts.items())),
        'event_audit': audits,
        'comparison': {'prior_weight': PRIOR_WEIGHT, **comparison},
        'lppf_2026': {**lppf_result, 'test_status': 'one_seen_temporal_event_not_blind',
                      'external_close_display': {
                          'status': 'match_unproven_independence' if displayed_prices_match else 'conflict',
                          **EXTERNAL_LPPF_2026,
                          'provider_lineage_known': False,
                      },
                      'price_basis': 'unknown'},
        'release_decision': 'No live forecast; source/vintage/basis gates and untouched evaluation remain incomplete.',
        'costs': 'Di luar biaya transaksi, pajak, dan slippage.',
    }


if __name__ == '__main__':
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result = report()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"{result['eligible_events']} pairs; official gates {result['official_dividend_gate_counts']}; saved {OUTPUT.relative_to(ROOT)}")
