"""Private Sectors MCP outcome collection for a frozen ex-date shadow cohort."""

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from backend import store
from backend.data import ROOT
from backend.ex_date_shadow import MARKET_TZ, score
from backend.ex_date_shadow_evaluation import evaluate_cohort
from work.sectors_mcp_probe import Client


def load_cohort(path):
    payload = json.loads(path.read_text())
    records = payload['records']
    if not isinstance(records, list) or not records:
        raise ValueError('Kohort harus berisi forecast yang sudah dibekukan.')
    if len({record['id'] for record in records}) != len(records):
        raise ValueError('Forecast ID dalam kohort tidak unik.')
    return records


def verify_source(source, root):
    relative = source.get('path', source.get('file'))
    if not isinstance(relative, str):
        raise ValueError('Path sumber kohort tidak valid.')
    path = (root / relative).resolve()
    if (not path.is_relative_to((root / 'outputs').resolve()) or not path.is_file()
            or sha256(path.read_bytes()).hexdigest() != source.get('sha256')):
        raise ValueError(f'Sumber kohort hilang atau berubah: {relative}')


def process(forecasts, *, collect=False, root=ROOT, output_dir=None, client_factory=Client, now=None):
    observed_at = now or datetime.now(timezone.utc)
    if observed_at.tzinfo is None:
        raise ValueError('Waktu operasi harus timezone-aware.')
    store.init_store()
    for frozen in forecasts:
        stored = store.get(frozen['id'], kind='shadow-forecast')
        if stored != frozen:
            raise ValueError(f"Record DB tidak sama dengan export yang dibekukan: {frozen['id']}")
        for source in (frozen['calendar_source'], frozen['price_source'], frozen['official_notice']):
            verify_source(source, root)

    client = None
    errors = []
    if collect:
        if output_dir is None:
            raise ValueError('Direktori output wajib untuk koleksi harga.')
        folder = (root / output_dir).resolve()
        if not folder.is_relative_to((root / 'outputs').resolve()):
            raise ValueError('Direktori output harus berada di outputs/.')
        folder.mkdir(parents=True, exist_ok=True)
        for frozen in forecasts:
            ex_date = date.fromisoformat(frozen['ex_date'])
            if observed_at.astimezone(MARKET_TZ).date() <= ex_date:
                continue
            outcome_id = f"outcome:{frozen['id']}"
            if store.get(outcome_id, kind='shadow-outcome') is not None:
                continue
            try:
                if client is None:
                    client = client_factory()
                    client.initialize()
                result = client.request('tools/call', {
                    'name': 'fetch-daily-price',
                    'arguments': {'symbol': frozen['symbol'], 'start': frozen['ex_date'],
                                  'end': frozen['ex_date']},
                })
                if not isinstance(result, dict) or result.get('isError'):
                    raise ValueError('Sectors MCP mengembalikan error.')
                retrieved_at = now or datetime.now(timezone.utc)
                stamp = retrieved_at.strftime('%Y%m%dT%H%M%S%fZ')
                snapshot = folder / f"price-{frozen['symbol']}-{frozen['ex_date']}-{stamp}.json"
                envelope = {'transport': 'MCP Streamable HTTP', 'tool': 'fetch-daily-price',
                            'arguments': {'symbol': frozen['symbol'], 'start': frozen['ex_date'],
                                          'end': frozen['ex_date']},
                            'retrieved_at': retrieved_at.isoformat(), 'result': result}
                with snapshot.open('x') as stream:
                    json.dump(envelope, stream, ensure_ascii=False, indent=2)
                    stream.write('\n')
                score(frozen, str(snapshot.relative_to(root)), root=root, now=retrieved_at)
            except (RuntimeError, ValueError, OSError, KeyError, TypeError) as exc:
                errors.append({'symbol': frozen['symbol'], 'reason': str(exc)})

    outcomes = [store.get(f"outcome:{row['id']}", kind='shadow-outcome') for row in forecasts]
    for outcome in outcomes:
        if outcome:
            verify_source(outcome['price_source'], root)
    report = evaluate_cohort(forecasts, [row for row in outcomes if row], now=observed_at)
    report['checked_at'] = observed_at.isoformat()
    report['collection_errors'] = errors
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['status', 'collect-score'])
    parser.add_argument('--cohort', required=True, type=Path)
    parser.add_argument('--output-dir', default='outputs/forecast/shadow-outcomes')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = process(load_cohort(args.cohort), collect=args.command == 'collect-score',
                     output_dir=args.output_dir)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open('x') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps({'forecast_count': report['forecast_count'],
                      'observed_count': len(report['observed']),
                      'pending_count': len(report['pending']),
                      'collection_errors': report['collection_errors'],
                      'status': report['status']}, ensure_ascii=False))
    if report['collection_errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
