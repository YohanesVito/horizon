"""Reproduce the pre-specified LPPF 2026 ex-date audit; no new market fetches.

Primary source values below were transcribed from the issuer disclosure
published 2026-04-16 and KSEI notice dated 2026-04-17. Historical references
come from the issuer's current dividend table and announcement archive.
See docs/development/EX_DATE_VERIFICATION_PROTOCOL.md before interpreting output.
"""

import hashlib
import json
from pathlib import Path

from backend.data import ROOT, unpack
from backend.ex_date_forecast import VERSION, observations, predict_ex_close
from backend.intelligence import IntelligenceDataset, valid_bar

CALENDAR = ROOT / 'outputs/timeline-audit/raw/current-calendar-2026-04-01.json'
PRICES = ROOT / 'outputs/timeline-audit/raw/current-prices-LPPF-2026-04-03.json'
ACTIONS = ROOT / 'outputs/timeline-audit/raw/actions-LPPF.json'
OUTPUT = ROOT / 'outputs/forecast/lppf-2026-exdate-verification.json'
OFFICIAL = {
    'symbol': 'LPPF', 'dividend_type': 'final', 'dps_idr': 250,
    'cum_regular': '2026-04-23', 'ex_regular': '2026-04-24',
    'recording': '2026-04-27', 'payment': '2026-05-04',
    'issuer_idxnet_publication': '2026-04-16', 'ksei_notice': '2026-04-17',
}
SOURCES = {
    'issuer_announcements': 'https://matahari.com/pages/corporate-announcements',
    'issuer_dividend_history': 'https://matahari.com/pages/dividends-en',
    'issuer_dividend_notice': 'https://cdn.shopify.com/s/files/1/0666/9212/0727/files/20260416_LPPF_Disclosure_of_information_for_the_distribution_of_final_dividends_for_the_financial_year_2025.pdf?v=1776419994',
    'ksei_dividend_notice': 'https://web.ksei.co.id/Announcement/Files/LPPF_DIV_20260427_ID.pdf',
}
HISTORICAL_ISSUER_REFERENCE = {
    '2022-04-14': {'dps_idr': 250, 'announcement_date': '2022-04-12'},
    '2023-04-10': {'dps_idr': 525, 'announcement_date': '2023-03-30'},
    '2024-04-22': {'dps_idr': 200, 'announcement_date': '2024-04-03'},
    '2025-04-22': {'dps_idr': 300, 'announcement_date': '2025-04-16'},
}


def source(path):
    raw = path.read_bytes()
    metadata = json.loads(raw)
    return {'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
            'retrieved_at': metadata.get('retrieved_at'), 'transport': metadata.get('transport')}


def report():
    rows = [r for r in unpack(CALENDAR)['dividend']
            if r['symbol'] == 'LPPF.JK' and r['ex_date'] == OFFICIAL['ex_regular']]
    if len(rows) != 1:
        raise ValueError('Event LPPF 2026 tidak unik/tersedia pada snapshot kalender.')
    event = rows[0]
    schedule = {'dps_idr': event['dividend_amount'], 'cum_regular': event['cum_date'],
                'ex_regular': event['ex_date'], 'recording': event['recording_date'],
                'payment': event['payment_date']}
    if any(schedule[key] != OFFICIAL[key] for key in schedule):
        raise ValueError('DPS/jadwal Sectors tidak cocok dengan dokumen primer.')
    bars = unpack(PRICES)
    dates = [bar['date'] for bar in bars]
    if dates != sorted(set(dates)):
        raise ValueError('Tanggal harga duplikat atau tidak berurutan.')
    cum_idx = dates.index(event['cum_date'])
    ex_idx = dates.index(event['ex_date'])
    if ex_idx != cum_idx + 1 or not all(valid_bar(bar) for bar in (bars[cum_idx], bars[ex_idx])):
        raise ValueError('Pasangan OHLCV cum/ex tidak valid/berurutan.')
    if OFFICIAL['issuer_idxnet_publication'] > event['cum_date'] or OFFICIAL['ksei_notice'] > event['cum_date']:
        raise ValueError('Pengumuman resmi tidak mendahului cum-date.')
    cum_close, ex_close, dps = bars[cum_idx]['close'], bars[ex_idx]['close'], event['dividend_amount']
    history = IntelligenceDataset()
    training, exclusions = observations(history.events)
    if len(training) != 44 or len(history.events) != 48:
        raise ValueError('Versi cohort historis berubah; protokol perlu dibekukan ulang.')
    historical_lppf = [row for row in training if row['symbol'] == 'LPPF']
    if len(historical_lppf) != len(HISTORICAL_ISSUER_REFERENCE):
        raise ValueError('Jumlah event latih LPPF berubah.')
    historical_crosscheck = []
    for row in historical_lppf:
        reference = HISTORICAL_ISSUER_REFERENCE.get(row['ex_date'])
        if not reference or row['dps'] != reference['dps_idr']:
            raise ValueError('DPS/ex-date LPPF historis tidak cocok dengan tabel emiten.')
        if reference['announcement_date'] > row['cum_date']:
            raise ValueError('Arsip pengumuman LPPF tidak mendahului cum-date.')
        historical_crosscheck.append({
            'event_id': row['event_id'], 'cum_date': row['cum_date'],
            'ex_date': row['ex_date'], 'dps_idr': row['dps'],
            'issuer_archive_announcement_date': reference['announcement_date'],
            'status': 'dps_ex_date_match_current_issuer_table; archival_notice_content_not_fully_audited',
        })
    fitted = predict_ex_close(cum_close, dps, training, event['cum_date'])
    if fitted is None or fitted['training_events'] != len(training):
        raise ValueError('Model tidak dapat dilatih hanya dengan event sebelum cum-date.')
    predictions = {'flat': cum_close, 'full_dps': cum_close-dps, 'pooled_pdr': fitted['close']}
    actions = unpack(ACTIONS)['corporate_actions']
    nearby_splits = [item for item in actions.get('stock_split') or []
                     if '2022-01-01' <= item['date'] <= event['ex_date']]
    return {
        'status': 'partial_verification_research_only', 'event_id': 'LPPF:2026-04-24',
        'protocol': 'docs/development/EX_DATE_VERIFICATION_PROTOCOL.md',
        'official': OFFICIAL, 'primary_urls': SOURCES,
        'historical_lppf_crosscheck': historical_crosscheck,
        'snapshot_sources': [source(path) for path in (CALENDAR, PRICES, ACTIONS)],
        'checks': {
            'published_before_cum': True, 'schedule_and_dps_match_primary': True,
            'provider_cum_ex_bars_adjacent_and_valid': True,
            'provider_stock_splits_2022_to_ex': nearby_splits,
            'price_dividend_adjustment_basis_verified': False,
            'independent_price_close_verified': False,
        },
        'observed': {
            'cum_close_idr': cum_close, 'ex_close_idr': ex_close, 'dps_idr': dps,
            'price_drop_idr': cum_close-ex_close, 'observed_pdr': (cum_close-ex_close)/dps,
            'gross_ex_date_pnl_per_share_idr': ex_close-cum_close+dps,
            'gross_ex_date_return_pct': (ex_close-cum_close+dps)/cum_close*100,
        },
        'model': {'version': VERSION, 'training_dataset_version': history.version,
                  'training_events': fitted['training_events'],
                  'training_latest_ex_date': fitted['training_latest_ex_date'],
                  'training_exclusions': exclusions, 'kappa': fitted['kappa']},
        'test': {'predicted_ex_close_idr': predictions,
                 'signed_error_pct_of_cum': {key: (value-ex_close)/cum_close*100
                                             for key, value in predictions.items()},
                 'absolute_error_pct_of_cum': {key: abs(value-ex_close)/cum_close*100
                                               for key, value in predictions.items()}},
        'limitations': [
            'Satu event; LPPF sudah terlihat dalam UI/sampel pilihan dan bukan holdout blind.',
            'Snapshot Sectors diambil setelah ex-date; dokumen resmi mendukung DPS/jadwal, bukan vintage harga provider.',
            'Tidak ada konfirmasi independen close/adjustment factor harga provider untuk kedua hari.',
            'Tiada pemeriksaan seluruh aksi korporasi, kondisi pasar, atau biaya transaksi, pajak, slippage.',
        ],
        'release_decision': 'Tetap research-only; jangan tampilkan garis/angka forecast live.',
    }


if __name__ == '__main__':
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result = report()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"{result['event_id']}: {result['status']}; saved {OUTPUT.relative_to(ROOT)}")
