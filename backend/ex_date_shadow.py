"""Freeze sourced, pre-cum ex-date baselines for later prospective evaluation.

No public forecast is served from these research records. The notice document
date is operator supplied; capture time proves only that its bytes were present.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from . import store
from .data import ROOT

MODEL_VERSION = 'pre-cum-full-dps-baseline-v0.1'
MARKET_TZ = ZoneInfo('Asia/Jakarta')


def _snapshot(relative, root):
    if not isinstance(relative, str):
        raise ValueError('Path snapshot harus berada di outputs/.')
    path = (root / relative).resolve()
    if not path.is_relative_to((root / 'outputs').resolve()) or not path.is_file():
        raise ValueError('Path snapshot harus berupa berkas yang ada di outputs/.')
    raw = path.read_bytes()
    body = json.loads(raw)
    stamp = _as_datetime(body.get('retrieved_at'), 'retrieved_at snapshot')
    return path, body, stamp, sha256(raw).hexdigest()


def _as_datetime(value, field):
    try:
        result = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field} harus ISO-8601 dengan zona waktu.') from None
    if result.tzinfo is None:
        raise ValueError(f'{field} harus ISO-8601 dengan zona waktu.')
    return result


def _date(value, field):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field} harus tanggal ISO-8601.') from None


def _positive(value, field):
    try:
        number = Decimal(str(value))
    except Exception:
        raise ValueError(f'{field} harus angka positif.') from None
    if not number.is_finite() or number <= 0:
        raise ValueError(f'{field} harus angka positif.')
    return number


def _matched_rows(payload, field, symbol, day):
    result = payload.get('result', payload)
    if isinstance(result, dict) and 'content' in result:
        result = json.loads(next(item['text'] for item in result['content'] if item['type'] == 'text'))
    rows = result if isinstance(result, list) else [
        row for group in ('dividend', 'upcoming_dividend')
        for row in result.get(group, [])
    ]
    return [row for row in rows if row.get('symbol', '').removesuffix('.JK') == symbol
            and row.get(field) == day]


def capture(manifest, *, root=ROOT, now=None):
    """Capture once before cum-date, checking the input against both Sectors files."""
    captured_at = now or datetime.now(timezone.utc)
    if captured_at.tzinfo is None:
        raise ValueError('Waktu capture harus timezone-aware.')
    symbol = manifest.get('symbol', '')
    if not symbol.isascii() or not symbol.isalnum() or not symbol.isupper() or not 2 <= len(symbol) <= 6:
        raise ValueError('Simbol emiten tidak valid.')
    cum = _date(manifest.get('cum_date'), 'cum_date')
    ex = _date(manifest.get('ex_date'), 'ex_date')
    price_date = _date(manifest.get('last_price_date'), 'last_price_date')
    today = captured_at.astimezone(MARKET_TZ).date()
    if not price_date < today < cum < ex:
        raise ValueError('Capture harus sebelum cum-date; close terakhir harus dari hari sebelumnya.')
    dps = _positive(manifest.get('dps'), 'dps')
    last_close = _positive(manifest.get('last_close'), 'last_close')
    if dps >= last_close:
        raise ValueError('DPS harus lebih kecil dari close agar baseline valid.')

    calendar_path, calendar, calendar_at, calendar_hash = _snapshot(manifest.get('calendar_snapshot'), root)
    price_path, prices, prices_at, price_hash = _snapshot(manifest.get('price_snapshot'), root)
    if calendar_at > captured_at or prices_at > captured_at:
        raise ValueError('Snapshot diambil setelah waktu capture.')
    if prices_at.astimezone(MARKET_TZ).date() < price_date:
        raise ValueError('Snapshot harga diambil sebelum tanggal close yang diklaim.')
    events = _matched_rows(calendar, 'ex_date', symbol, ex.isoformat())
    if not events or any(row.get('cum_date') != cum.isoformat()
                         or _positive(row.get('dividend_amount'), 'DPS sumber') != dps for row in events):
        raise ValueError('Jadwal/DPS input tidak cocok dengan snapshot Sectors.')
    bars = _matched_rows(prices, 'date', symbol, price_date.isoformat())
    if len(bars) != 1 or _positive(bars[0].get('close'), 'Close sumber') != last_close:
        raise ValueError('Harga input tidak cocok dengan snapshot Sectors.')

    notice_day = _date(manifest.get('notice_document_date'), 'notice_document_date')
    notice_url = manifest.get('notice_url', '')
    if not isinstance(notice_url, str) or not notice_url.startswith('https://') or notice_day > today:
        raise ValueError('URL dan tanggal dokumen notice harus tersedia sebelum capture.')
    notice_file = manifest.get('notice_file')
    if not isinstance(notice_file, str):
        raise ValueError('Berkas notice resmi harus tersedia di outputs/.')
    notice_path = (root / notice_file).resolve()
    if not notice_path.is_relative_to((root / 'outputs').resolve()) or not notice_path.is_file():
        raise ValueError('Berkas notice resmi harus tersedia di outputs/.')
    notice_hash = sha256(notice_path.read_bytes()).hexdigest()

    key = f'shadow:{symbol}:{ex.isoformat()}:{MODEL_VERSION}'
    record = {
        'id': key, 'status': 'research_shadow', 'model_version': MODEL_VERSION,
        'target': 'ex_date_close_from_pre_cum_last_close',
        'captured_at': captured_at.isoformat(), 'symbol': symbol,
        'cum_date': cum.isoformat(), 'ex_date': ex.isoformat(),
        'last_price_date': price_date.isoformat(),
        'last_close': str(last_close), 'dps': str(dps),
        'baseline_ex_close': str(last_close - dps),
        'calendar_source': {'path': str(calendar_path.relative_to(root)), 'sha256': calendar_hash,
                            'retrieved_at': calendar_at.isoformat()},
        'price_source': {'path': str(price_path.relative_to(root)), 'sha256': price_hash,
                         'retrieved_at': prices_at.isoformat()},
        'official_notice': {'url': notice_url, 'file': str(notice_path.relative_to(root)),
                            'sha256': notice_hash, 'document_date_claim': notice_day.isoformat(),
                            'observed_at_capture': captured_at.isoformat(),
                            'publication_time_verified': False},
        'limitations': ['Baseline riset sebelum cum-date; bukan prediksi tervalidasi.',
                        'Tanggal dokumen bukan bukti waktu publikasi; basis harga masih perlu audit independen.'],
    }
    store.insert_once(key, 'shadow-forecast', record)
    return record


def score(record, price_snapshot, *, root=ROOT, now=None):
    """Append observed ex-close without modifying the frozen forecast."""
    scored_at = now or datetime.now(timezone.utc)
    if scored_at.tzinfo is None or scored_at.astimezone(MARKET_TZ).date() < date.fromisoformat(record['ex_date']):
        raise ValueError('Harga aktual hanya boleh dicatat pada/setelah ex-date.')
    for source in (record['calendar_source'], record['price_source'], record['official_notice']):
        original = (root / source['path'] if 'path' in source else root / source['file']).resolve()
        if (not original.is_relative_to((root / 'outputs').resolve()) or not original.is_file()
                or sha256(original.read_bytes()).hexdigest() != source['sha256']):
            raise ValueError('Sumber forecast berubah atau hilang; audit sebelum scoring.')
    path, prices, retrieved_at, digest = _snapshot(price_snapshot, root)
    if retrieved_at > scored_at or retrieved_at.astimezone(MARKET_TZ).date() <= date.fromisoformat(record['ex_date']):
        raise ValueError('Snapshot harga aktual harus diambil setelah ex-date dan sebelum scoring.')
    rows = _matched_rows(prices, 'date', record['symbol'], record['ex_date'])
    if len(rows) != 1:
        raise ValueError('Satu bar ex-date Sectors wajib tersedia.')
    actual = _positive(rows[0].get('close'), 'Close ex-date')
    predicted = Decimal(record['baseline_ex_close'])
    outcome = {'id': f"outcome:{record['id']}", 'forecast_id': record['id'],
               'scored_at': scored_at.isoformat(), 'actual_ex_close': str(actual),
               'absolute_error_pct_of_last_close': str(abs(predicted - actual) / Decimal(record['last_close']) * 100),
               'price_source': {'path': str(path.relative_to(root)), 'sha256': digest,
                                'retrieved_at': retrieved_at.isoformat()},
               'status': 'research_observed',
               'limitations': ['Basis harga Sectors dan notice resmi masih perlu audit sebelum klaim akurasi.']}
    store.insert_once(outcome['id'], 'shadow-outcome', outcome)
    return outcome
