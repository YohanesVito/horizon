"""Private CLI for prospective ex-date research; never publishes a forecast."""

import argparse
import json
from pathlib import Path

from backend import store
from backend.ex_date_shadow import capture, score


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('capture').add_argument('manifest', type=Path)
    scoring = sub.add_parser('score')
    scoring.add_argument('forecast_id')
    scoring.add_argument('price_snapshot')
    args = parser.parse_args()
    store.init_store()
    if args.command == 'capture':
        result = capture(json.loads(args.manifest.read_text()))
        print(json.dumps({'id': result['id'], 'captured_at': result['captured_at'],
                          'status': result['status'], 'baseline_ex_close': result['baseline_ex_close']}))
    else:
        record = store.get(args.forecast_id, kind='shadow-forecast')
        if record is None:
            parser.error('Forecast shadow tidak ditemukan.')
        result = score(record, args.price_snapshot)
        print(json.dumps({'id': result['id'], 'scored_at': result['scored_at'],
                          'absolute_error_pct_of_last_close': result['absolute_error_pct_of_last_close']}))


if __name__ == '__main__':
    main()
