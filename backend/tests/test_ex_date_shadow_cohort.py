from datetime import datetime, timezone
import json

import pytest

from backend import store
from backend.ex_date_shadow import capture
from work.score_ex_date_shadow_cohort import process


def frozen_event(tmp_path, symbol='TSTA'):
    out = tmp_path / 'outputs'
    out.mkdir()
    (out / 'calendar.json').write_text(json.dumps({
        'retrieved_at': '2026-10-08T08:00:00+00:00',
        'result': {'upcoming_dividend': [{
            'symbol': f'{symbol}.JK', 'cum_date': '2026-10-12',
            'ex_date': '2026-10-13', 'dividend_amount': 80,
        }]},
    }))
    (out / 'price.json').write_text(json.dumps({
        'retrieved_at': '2026-10-08T08:00:00+00:00',
        'result': [{'symbol': f'{symbol}.JK', 'date': '2026-10-07', 'close': 1000}],
    }))
    (out / 'notice.pdf').write_bytes(b'official fixture')
    manifest = {'symbol': symbol, 'cum_date': '2026-10-12', 'ex_date': '2026-10-13',
                'last_price_date': '2026-10-07', 'last_close': 1000, 'dps': 80,
                'calendar_snapshot': 'outputs/calendar.json', 'price_snapshot': 'outputs/price.json',
                'notice_file': 'outputs/notice.pdf', 'notice_url': 'https://example.com/notice.pdf',
                'notice_document_date': '2026-10-06'}
    store.init_store()
    return capture(manifest, root=tmp_path, now=datetime(2026, 10, 8, 9, tzinfo=timezone.utc))


def test_cohort_waits_until_after_ex_date_then_scores_once(tmp_path):
    record = frozen_event(tmp_path)
    before = process([record], collect=True, root=tmp_path, output_dir='outputs/actual',
                     client_factory=lambda: pytest.fail('MCP called before ex-date'),
                     now=datetime(2026, 10, 8, 10, tzinfo=timezone.utc))
    assert before['summary'] is None
    assert before['pending'][0]['state'] == 'awaiting_ex_date'

    class FakeClient:
        def initialize(self):
            return None

        def request(self, method, params):
            assert method == 'tools/call'
            assert params['arguments'] == {'symbol': 'TSTA', 'start': '2026-10-13', 'end': '2026-10-13'}
            return {'content': [{'type': 'text', 'text': json.dumps([
                {'symbol': 'TSTA.JK', 'date': '2026-10-13', 'close': 900},
            ])}]}

    after = process([record], collect=True, root=tmp_path, output_dir='outputs/actual',
                    client_factory=FakeClient,
                    now=datetime(2026, 10, 14, 8, tzinfo=timezone.utc))
    assert after['summary']['n'] == 1
    assert after['summary']['model_mae_pct'] == '2.00'
    assert after['summary']['flat_mae_pct'] == '10.0'
    assert after['performance_claim_allowed'] is False
    assert not after['pending']
    assert len(list((tmp_path / 'outputs' / 'actual').glob('price-*.json'))) == 1

    repeat = process([record], collect=True, root=tmp_path, output_dir='outputs/actual',
                     client_factory=lambda: pytest.fail('MCP called after outcome stored'),
                     now=datetime(2026, 10, 14, 9, tzinfo=timezone.utc))
    assert repeat['summary'] == after['summary']


def test_cohort_rejects_modified_export(tmp_path):
    record = frozen_event(tmp_path, 'TSTB')
    with pytest.raises(ValueError, match='tidak sama'):
        process([{**record, 'last_close': '999'}], root=tmp_path,
                now=datetime(2026, 10, 8, 10, tzinfo=timezone.utc))
    (tmp_path / record['official_notice']['file']).write_bytes(b'mutated')
    with pytest.raises(ValueError, match='Sumber kohort hilang atau berubah'):
        process([record], root=tmp_path,
                now=datetime(2026, 10, 8, 10, tzinfo=timezone.utc))
