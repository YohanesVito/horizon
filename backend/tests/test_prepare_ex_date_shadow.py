from datetime import datetime, timezone
import json

from work.prepare_ex_date_shadow import prepare


def test_preparation_keeps_only_reviewed_future_event_with_fresh_price(tmp_path):
    out = tmp_path / 'outputs'
    out.mkdir()
    (out / 'calendar.json').write_text(json.dumps({
        'retrieved_at': '2026-10-08T08:00:00+00:00',
        'result': {'upcoming_dividend': [
            {'symbol': 'GOOD.JK', 'cum_date': '2026-10-12', 'ex_date': '2026-10-13',
             'payment_date': '2026-10-30', 'dividend_amount': 80},
            {'symbol': 'PAST.JK', 'cum_date': '2026-10-08', 'ex_date': '2026-10-09',
             'payment_date': '2026-10-30', 'dividend_amount': 80},
            {'symbol': 'MISS.JK', 'cum_date': '2026-10-12', 'ex_date': '2026-10-13',
             'payment_date': '2026-10-30', 'dividend_amount': 80},
        ]},
    }))
    (out / 'prices.json').write_text(json.dumps({
        'retrieved_at': '2026-10-08T08:01:00+00:00',
        'result': {'content': [{'type': 'text', 'text': json.dumps([
            {'symbol': 'GOOD.JK', 'date': '2026-10-07', 'close': 1000},
            {'symbol': 'GOOD.JK', 'date': '2026-10-08', 'close': 1100},
        ])}]},
    }))
    (out / 'notice.pdf').write_bytes(b'reviewed notice')
    review = {'GOOD': {'url': 'https://example.com/notice.pdf', 'file': 'outputs/notice.pdf',
                       'document_date': '2026-10-06', 'cum_date': '2026-10-12',
                       'ex_date': '2026-10-13', 'payment_date': '2026-10-30', 'dps': 80}}
    result = prepare('outputs/calendar.json', {'GOOD': 'outputs/prices.json'}, review,
                     now=datetime(2026, 10, 8, 9, tzinfo=timezone.utc), root=tmp_path)
    assert len(result['ready']) == 1
    assert result['ready'][0]['symbol'] == 'GOOD'
    assert result['ready'][0]['last_price_date'] == '2026-10-07'
    assert result['ready'][0]['last_close'] == '1000'
    assert {row['symbol'] for row in result['skipped']} == {'PAST', 'MISS'}

    review['GOOD']['dps'] = 79
    mismatch = prepare('outputs/calendar.json', {'GOOD': 'outputs/prices.json'}, review,
                       now=datetime(2026, 10, 8, 9, tzinfo=timezone.utc), root=tmp_path)
    assert not mismatch['ready']
    assert any(row['symbol'] == 'GOOD' and 'tidak cocok' in row['reason']
               for row in mismatch['skipped'])
