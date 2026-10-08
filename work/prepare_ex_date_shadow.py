"""Prepare auditable, pre-cum shadow manifests from frozen Sectors snapshots.

Official notices are reviewed separately; this command never invents their
publication timestamp and never writes a forecast to the application store.
"""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path

from backend.data import ROOT
from backend.ex_date_shadow import MARKET_TZ, _date, _positive, _snapshot


def prepare(calendar_path, price_paths, notices, *, now=None, root=ROOT):
    as_of = now or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        raise ValueError('Waktu persiapan harus timezone-aware.')
    today = as_of.astimezone(MARKET_TZ).date()
    _, calendar, calendar_at, _ = _snapshot(calendar_path, root)
    if calendar_at > as_of:
        raise ValueError('Snapshot kalender berasal dari masa depan.')
    rows = calendar.get('result', {}).get('upcoming_dividend', [])
    if not isinstance(rows, list):
        raise ValueError('Kalender upcoming_dividend tidak valid.')

    ready, skipped = [], []
    for row in sorted(rows, key=lambda item: (item.get('ex_date') or '', item.get('symbol') or '')):
        symbol = row.get('symbol', '').removesuffix('.JK')
        reason = None
        try:
            cum = _date(row.get('cum_date'), 'cum_date')
            ex = _date(row.get('ex_date'), 'ex_date')
            dps = _positive(row.get('dividend_amount'), 'DPS')
            if not today < cum < ex:
                reason = 'cum-date tidak lagi di masa depan WIB'
            elif symbol not in price_paths:
                reason = 'snapshot harga MCP belum tersedia'
            elif symbol not in notices:
                reason = 'notice resmi belum direview'
            else:
                review = notices[symbol]
                if (review['cum_date'] != cum.isoformat()
                        or review['ex_date'] != ex.isoformat()
                        or Decimal(str(review['dps'])) != dps
                        or review['payment_date'] != row.get('payment_date')):
                    reason = 'review notice tidak cocok dengan kalender Sectors'
                else:
                    _date(review['document_date'], 'document_date')
                    notice = (root / review['file']).resolve()
                    if not notice.is_relative_to((root / 'outputs').resolve()) or not notice.is_file():
                        reason = 'berkas notice tidak ditemukan di outputs/'
                    else:
                        _, price, price_at, _ = _snapshot(price_paths[symbol], root)
                        if price_at > as_of:
                            reason = 'snapshot harga berasal dari masa depan'
                        else:
                            text = next((item['text'] for item in price['result'].get('content', [])
                                         if item.get('type') == 'text'), None)
                            bars = json.loads(text) if text is not None else price['result']
                            bars = [bar for bar in bars if bar.get('symbol', '').removesuffix('.JK') == symbol
                                    and _date(bar.get('date'), 'tanggal harga') < today]
                            if not bars:
                                reason = 'close sebelum hari capture tidak tersedia'
                            else:
                                last = max(bars, key=lambda bar: bar['date'])
                                last_date = _date(last['date'], 'tanggal harga')
                                close = _positive(last.get('close'), 'close')
                                if (today - last_date).days > 7:
                                    reason = 'close terakhir lebih dari 7 hari kalender'
                                elif dps >= close:
                                    reason = 'DPS tidak lebih kecil dari close'
                                else:
                                    ready.append({
                                        'symbol': symbol, 'cum_date': cum.isoformat(), 'ex_date': ex.isoformat(),
                                        'last_price_date': last_date.isoformat(), 'last_close': str(close),
                                        'dps': str(dps), 'calendar_snapshot': calendar_path,
                                        'price_snapshot': price_paths[symbol], 'notice_file': review['file'],
                                        'notice_url': review['url'],
                                        'notice_document_date': review['document_date'],
                                    })
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            reason = f'data sumber tidak valid: {exc}'
        if reason:
            skipped.append({'symbol': symbol, 'cum_date': row.get('cum_date'), 'reason': reason})
    return {'prepared_at': as_of.isoformat(), 'ready': ready, 'skipped': skipped}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--calendar', required=True)
    parser.add_argument('--price', action='append', default=[], metavar='SYMBOL=PATH')
    parser.add_argument('--notice-review', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    prices = dict(item.split('=', 1) for item in args.price)
    notices = json.loads(args.notice_review.read_text())
    report = prepare(args.calendar, prices, notices)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    for manifest in report['ready']:
        (args.output_dir / f"{manifest['symbol']}.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (args.output_dir / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'ready': len(report['ready']), 'skipped': len(report['skipped']),
                      'output_dir': str(args.output_dir)}))


if __name__ == '__main__':
    main()
