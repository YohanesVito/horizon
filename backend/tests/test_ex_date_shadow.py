from datetime import datetime, timezone
import json

import pytest

from backend import store
from backend.ex_date_shadow import capture, score

BEFORE = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
AFTER = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)


def fixtures(tmp_path, symbol='SHDW'):
    out = tmp_path / 'outputs'
    out.mkdir()
    calendar = out / 'calendar.json'
    prices = out / 'prices.json'
    notice = out / 'notice.pdf'
    calendar.write_text(json.dumps({
        'retrieved_at': '2026-10-08T10:00:00+00:00',
        'result': {'upcoming_dividend': [{
            'symbol': f'{symbol}.JK', 'cum_date': '2026-11-10',
            'ex_date': '2026-11-11', 'dividend_amount': 80,
        }]},
    }))
    prices.write_text(json.dumps({
        'retrieved_at': '2026-10-08T10:00:00+00:00',
        'result': [{'symbol': f'{symbol}.JK', 'date': '2026-10-07', 'close': 1000}],
    }))
    notice.write_bytes(b'official notice fixture')
    manifest = {'symbol': symbol, 'cum_date': '2026-11-10', 'ex_date': '2026-11-11',
                'last_price_date': '2026-10-07', 'last_close': 1000, 'dps': 80,
                'calendar_snapshot': 'outputs/calendar.json', 'price_snapshot': 'outputs/prices.json',
                'notice_file': 'outputs/notice.pdf', 'notice_url': 'https://example.com/notice.pdf',
                'notice_document_date': '2026-10-07'}
    return manifest, calendar, prices, out


def test_shadow_capture_is_pre_cum_and_immutable(tmp_path):
    store.init_store()
    manifest, _, _, _ = fixtures(tmp_path)
    record = capture(manifest, root=tmp_path, now=BEFORE)
    assert record['status'] == 'research_shadow'
    assert record['baseline_ex_close'] == '920'
    assert record['official_notice']['publication_time_verified'] is False
    assert record['official_notice']['observed_at_capture'] == BEFORE.isoformat()
    assert store.get(record['id'], kind='shadow-forecast') == record
    with pytest.raises(ValueError, match='tidak boleh ditimpa'):
        capture({**manifest, 'notice_url': 'https://example.com/revised.pdf'}, root=tmp_path, now=BEFORE)
    assert store.get(record['id'], kind='shadow-forecast') == record
    with pytest.raises(ValueError, match='sebelum cum-date'):
        capture(manifest, root=tmp_path, now=AFTER)


def test_shadow_rejects_snapshot_mismatch_and_future_source(tmp_path):
    manifest, calendar, prices, _ = fixtures(tmp_path, 'TSTB')
    with pytest.raises(ValueError, match='Jadwal/DPS'):
        capture({**manifest, 'dps': 79}, root=tmp_path, now=BEFORE)
    with pytest.raises(ValueError, match='Harga input'):
        capture({**manifest, 'last_close': 999}, root=tmp_path, now=BEFORE)
    with pytest.raises(ValueError, match='tanggal dokumen'):
        capture({**manifest, 'notice_document_date': '2026-10-09'}, root=tmp_path, now=BEFORE)
    body = json.loads(calendar.read_text())
    body['retrieved_at'] = '2026-10-09T10:00:00+00:00'
    calendar.write_text(json.dumps(body))
    with pytest.raises(ValueError, match='setelah waktu capture'):
        capture(manifest, root=tmp_path, now=BEFORE)
    assert prices.exists()


def test_shadow_accepts_archived_mcp_price_content(tmp_path):
    store.init_store()
    manifest, _, prices, _ = fixtures(tmp_path, 'TSTE')
    body = json.loads(prices.read_text())
    body['result'] = {'content': [{'type': 'text', 'text': json.dumps(body['result'])}]}
    prices.write_text(json.dumps(body))
    record = capture(manifest, root=tmp_path, now=BEFORE)
    assert record['baseline_ex_close'] == '920'


def test_shadow_outcome_is_appended_only_after_ex_date(tmp_path):
    store.init_store()
    manifest, _, _, out = fixtures(tmp_path, 'TSTC')
    record = capture(manifest, root=tmp_path, now=BEFORE)
    actual_file = out / 'actual.json'
    actual_file.write_text(json.dumps({
        'retrieved_at': '2026-11-12T08:00:00+00:00',
        'result': [{'symbol': 'TSTC.JK', 'date': '2026-11-11', 'close': 900}],
    }))
    with pytest.raises(ValueError, match='pada/setelah ex-date'):
        score(record, 'outputs/actual.json', root=tmp_path, now=BEFORE)
    outcome = score(record, 'outputs/actual.json', root=tmp_path, now=AFTER)
    assert outcome['actual_ex_close'] == '900'
    assert outcome['absolute_error_pct_of_last_close'] == '2.00'
    assert store.get(record['id'], kind='shadow-forecast') == record
    with pytest.raises(ValueError, match='tidak boleh ditimpa'):
        score(record, 'outputs/actual.json', root=tmp_path, now=AFTER)


def test_shadow_scoring_rejects_mutated_original_source(tmp_path):
    store.init_store()
    manifest, calendar, _, out = fixtures(tmp_path, 'TSTD')
    record = capture(manifest, root=tmp_path, now=BEFORE)
    (out / 'actual.json').write_text(json.dumps({
        'retrieved_at': '2026-11-12T08:00:00+00:00',
        'result': [{'symbol': 'TSTD.JK', 'date': '2026-11-11', 'close': 900}],
    }))
    calendar.write_text(calendar.read_text() + ' ')
    with pytest.raises(ValueError, match='Sumber forecast berubah'):
        score(record, 'outputs/actual.json', root=tmp_path, now=AFTER)
