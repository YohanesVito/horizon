"""Read-only, cached Sectors audit for a five-year dividend timeline design."""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from sectors_mcp_probe import Client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/timeline-audit'
RAW = OUT / 'raw'
YEARS = list(range(2021, 2026))
SYMBOLS = ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS']


def unpack(path):
    envelope = json.loads(path.read_text())
    if envelope.get('http_status', 200) != 200:
        raise ValueError('Provider HTTP error')
    result = envelope['result']
    if isinstance(result, dict) and 'content' in result:
        if result.get('isError'):
            raise ValueError('MCP tool error')
        result = json.loads(next(x['text'] for x in result['content'] if x['type'] == 'text'))
    return result


def collect():
    RAW.mkdir(parents=True, exist_ok=True)
    jobs = []
    start = date(2021, 1, 1)
    while start <= date(2021, 12, 31):
        end = min(start + timedelta(days=89), date(2021, 12, 31))
        jobs.append((f'calendar-{start}.json', 'calendar', {'start': str(start), 'end': str(end)}))
        start = end + timedelta(days=1)
    jobs += [('five-year-dividend-payers.json', 'fetch-companies', {
        'where': ' and '.join(f'total_dividend[{y}] > 0' for y in YEARS),
        'order_by': 'symbol', 'limit': 200, 'offset': 0, 'include_query_values': True,
    })]
    for year in [2021, 2025]:
        jobs.append((f'news-BBCA-{year}.json', 'fetch-news', {
            'symbols': 'BBCA', 'keyword': 'dividen', 'extension': 'idx',
            'start': f'{year}-01-01', 'end': f'{year}-12-31', 'limit': 30, 'offset': 0,
        }))
    jobs += [
        ('prices-LPPF-2021-11-11.json', 'fetch-daily-price', {
            'symbol': 'LPPF', 'start': '2021-10-21', 'end': '2022-01-18',
        }),
        ('actions-LPPF.json', 'fetch-corporate-actions', {'symbol': 'LPPF'}),
    ]
    client = Client()
    client.initialize()
    results = []
    for name, tool, args in jobs:
        path = RAW / name
        try:
            if path.exists():
                unpack(path)
                results.append({'file': name, 'cached': True})
                continue
            if tool == 'calendar':
                cmd = [sys.executable, str(ROOT / 'work/sectors_calendar_probe.py'),
                       '--start', args['start'], '--end', args['end'], '--output', str(path)]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            else:
                result = client.request('tools/call', {'name': tool, 'arguments': args})
                path.write_text(json.dumps({'transport': 'MCP Streamable HTTP',
                    'retrieved_at': datetime.now(timezone.utc).isoformat(),
                    'tool': tool, 'arguments': args, 'result': result}, ensure_ascii=False, indent=2))
            data = unpack(path)
            results.append({'file': name, 'ok': True,
                            'rows': len(data.get('dividend', [])) if tool == 'calendar' else None})
        except Exception as exc:
            results.append({'file': name, 'error_type': type(exc).__name__})
        print(json.dumps(results[-1]), flush=True)
        # Bounded, sequential collection; no automatic credit-expanding retries.
        time.sleep(4)
    (OUT / 'collection.json').write_text(json.dumps(results, indent=2))


def analyze():
    calendar_paths = sorted(RAW.glob('calendar-*.json')) + sorted((ROOT / 'outputs/intelligence/raw').glob('calendar-*.json'))
    events, conflicts, windows = {}, [], []
    for path in calendar_paths:
        body = unpack(path)
        windows.append({'start': body['start'], 'end': body['end'], 'file': str(path.relative_to(ROOT))})
        for item in body.get('dividend', []):
            if int(item['ex_date'][:4]) not in YEARS:
                continue
            key = (item['symbol'].removesuffix('.JK'), item['ex_date'])
            if key in events and events[key]['row'] != item:
                conflicts.append({'event': list(key), 'files': [events[key]['source'], str(path.relative_to(ROOT))]})
            events[key] = {'row': item, 'source': str(path.relative_to(ROOT))}
    required = ['cum_date', 'ex_date', 'recording_date', 'payment_date', 'dividend_amount']
    by_symbol = defaultdict(list)
    for (symbol, ex), item in events.items():
        by_symbol[symbol].append(item)
    summaries = []
    for symbol, items in sorted(by_symbol.items()):
        counts = Counter(int(i['row']['ex_date'][:4]) for i in items)
        missing = Counter(f for i in items for f in required if i['row'].get(f) is None)
        invalid = Counter()
        for item in items:
            row = item['row']
            try:
                phase_dates = [date.fromisoformat(row[k]) for k in required[:-1]]
                if phase_dates != sorted(phase_dates):
                    invalid['date_order'] += 1
            except (ValueError, TypeError, KeyError):
                invalid['invalid_date'] += 1
            if not isinstance(row.get('dividend_amount'), (int, float)) or row['dividend_amount'] <= 0:
                invalid['nonpositive_or_invalid_dps'] += 1
        declared = sum(any(i['row'].get(f) for f in ['declaration_date', 'announcement_date', 'announced_at']) for i in items)
        summaries.append({'symbol': symbol, **{str(y): counts[y] for y in YEARS},
            'five_year_event_presence': all(counts[y] > 0 for y in YEARS),
            'calendar_core_missing': dict(missing), 'calendar_core_invalid': dict(invalid), 'event_count': len(items),
            'declaration_dates_found': declared,
            'price_coverage': 'not_audited_for_full_five_years',
            'verification_status': 'incomplete',
            'eligible_strict': False,
            'reason': 'Declaration-event linkage, price completeness and adjustment basis not verified'})
    coverage_missing = []
    day = date(YEARS[0], 1, 1)
    while day <= date(YEARS[-1], 12, 31):
        if not any(w['start'] <= str(day) <= w['end'] for w in windows):
            coverage_missing.append(str(day))
        day += timedelta(days=1)
    screen = unpack(RAW / 'five-year-dividend-payers.json')
    screened_symbols = {x['symbol'].removesuffix('.JK') for x in screen['results']}
    calendar_candidates = {x['symbol'] for x in summaries if x['five_year_event_presence']}
    pilot = []
    for (symbol, ex), item in sorted(events.items()):
        if symbol != 'LPPF':
            continue
        name = f'prices-{symbol}-{ex}.json'
        price_path = RAW / name
        if not price_path.exists():
            price_path = ROOT / 'outputs/intelligence/raw' / name
        if not price_path.exists():
            pilot.append({'symbol': symbol, 'ex_date': ex, 'price_file': None})
            continue
        bars = unpack(price_path)
        dates = [bar['date'] for bar in bars]
        row = item['row']
        pilot.append({'symbol': symbol, 'ex_date': ex,
            'calendar': row, 'price_file': str(price_path.relative_to(ROOT)),
            'bar_count': len(bars), 'first_bar': min(dates), 'last_bar': max(dates),
            'duplicate_dates': len(dates) - len(set(dates)),
            'invalid_ohlc': sum(not all(isinstance(bar.get(k), (int, float)) and bar[k] > 0
                for k in ['open', 'high', 'low', 'close']) or
                not (bar['low'] <= min(bar['open'], bar['close']) <=
                     max(bar['open'], bar['close']) <= bar['high']) for bar in bars),
            'milestone_bars_found': {k: row[k] in dates for k in required if k != 'dividend_amount'},
            'all_market_sessions_verified': False,
            'adjustment_basis_verified': False,
            'declaration_link_verified': False})
    (OUT / 'pilot-LPPF.json').write_text(json.dumps(pilot, ensure_ascii=False, indent=2))
    report = {'audit_period': [str(YEARS[0])+'-01-01', str(YEARS[-1])+'-12-31'],
        'scope': 'All symbols returned by Sectors dividend calendar; not full price/filing audit of all IDX companies',
        'calendar_windows': windows, 'unqueried_calendar_days': coverage_missing,
        'calendar_event_count': len(events), 'symbol_count': len(summaries),
        'five_year_event_presence_count': sum(x['five_year_event_presence'] for x in summaries),
        'five_year_calendar_core_count': sum(x['five_year_event_presence'] and not x['calendar_core_missing'] and not x['calendar_core_invalid'] for x in summaries),
        'declared_event_count': sum(x['declaration_dates_found'] for x in summaries),
        'conflicts': conflicts,
        'screener_reconciliation': {
            'count': len(screened_symbols), 'pagination': screen.get('pagination'),
            'calendar_only': sorted(calendar_candidates - screened_symbols),
            'screener_only': sorted(screened_symbols - calendar_candidates)},
        'eligibility_note': 'Not assessed end-to-end; false means not yet approved, not proved unavailable',
        'eligible_strict_symbols': [], 'companies': summaries}
    (OUT / 'coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    with (OUT / 'coverage.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(summaries[0]) if summaries else ['symbol'])
        writer.writeheader()
        for row in summaries:
            writer.writerow({**row, 'calendar_core_missing': json.dumps(row['calendar_core_missing']),
                             'calendar_core_invalid': json.dumps(row['calendar_core_invalid'])})
    print(json.dumps({k:v for k,v in report.items() if k not in ['companies','calendar_windows']}, ensure_ascii=False))
    print('Existing research universe:', json.dumps([x for x in summaries if x['symbol'] in SYMBOLS], ensure_ascii=False))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['collect', 'analyze'])
    args = p.parse_args()
    collect() if args.stage == 'collect' else analyze()
