"""Bounded, restartable Sectors MCP/REST collection. No secrets in argv/output."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from sectors_mcp_probe import Client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/intelligence/raw'
SYMBOLS = ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS']


def unpack(path):
    r = json.loads(path.read_text())['result']
    if 'content' in r:
        if r.get('isError'):
            raise ValueError('Provider returned error')
        return json.loads(next(x['text'] for x in r['content'] if x['type'] == 'text'))
    return r


def collect(job):
    name, tool, args = job
    path = OUT / name
    if path.exists():
        try:
            unpack(path)
            return {'file': name, 'cached': True}
        except (ValueError, KeyError):
            pass
    try:
        if tool == 'calendar':
            r = subprocess.run([sys.executable, str(ROOT / 'work/sectors_calendar_probe.py'),
                                '--start', args['start'], '--end', args['end'], '--output', str(path)], capture_output=True, text=True)
            if r.returncode:
                return {'file': name, 'error': 'calendar failed; inspect redacted snapshot'}
        else:
            client = Client()
            client.initialize()
            result = client.request('tools/call', {'name': tool, 'arguments': args})
            if result.get('isError') and '429' in str(result):
                # One bounded retry per request, with a fresh minute window.
                time.sleep(65)
                result = client.request('tools/call', {'name': tool, 'arguments': args})
            if result.get('isError'):
                return {'file': name, 'error': 'MCP tool error'}
            path.write_text(json.dumps({'transport': 'MCP Streamable HTTP', 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                                        'tool': tool, 'arguments': args, 'result': result}, ensure_ascii=False, indent=2) + '\n')
        data = unpack(path)
        time.sleep(2.5)
        return {'file': name, 'ok': True, 'rows': len(data) if isinstance(data, list) else None}
    except Exception as error:
        return {'file': name, 'error': type(error).__name__}


def jobs_for(stage):
    if stage == 'actions':
        return [(f'actions-{s}.json', 'fetch-corporate-actions', {'symbol': s}) for s in SYMBOLS]
    if stage == 'calendar':
        jobs = []
        start = date(2022, 1, 1)
        while start <= date(2025, 12, 31):
            end = min(start + timedelta(days=89), date(2025, 12, 31))
            jobs.append((f'calendar-{start}.json', 'calendar', {'start': str(start), 'end': str(end)}))
            start = end + timedelta(days=1)
        return jobs
    jobs = []
    for s in SYMBOLS:
        for event in unpack(OUT / f'actions-{s}.json')['corporate_actions'].get('dividend') or []:
            if not '2022-01-01' <= event['ex_date'] <= '2025-12-31':
                continue
            ex = date.fromisoformat(event['ex_date'])
            jobs.append((f'prices-{s}-{ex}.json', 'fetch-daily-price', {'symbol': s, 'start': str(ex-timedelta(days=21)), 'end': str(ex+timedelta(days=68))}))
    # Stable deduplication, no return-dependent selection.
    return list({job[0]: job for job in jobs}.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['actions', 'calendar', 'prices'])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = jobs_for(args.stage)
    print(json.dumps({'stage': args.stage, 'requests': len(jobs)}), flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(collect, jobs))
    (OUT.parent / f'collection-{args.stage}.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({'completed': sum(bool(r.get('ok') or r.get('cached')) for r in results), 'failures': [r for r in results if r.get('error')]}), flush=True)
