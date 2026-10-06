"""Fill the continuous 2025 replay window through Sectors MCP, with rate pacing."""
from datetime import date, timedelta
import json
from pathlib import Path
import collect_intelligence as collector

OUT = Path(__file__).resolve().parents[1] / 'outputs/rotation/raw'
OUT.mkdir(parents=True, exist_ok=True)
collector.OUT = OUT
jobs = []
start = date(2024, 12, 1)
while start <= date(2026, 1, 10):
    end = min(start+timedelta(days=89), date(2026, 1, 10))
    args = {'start': str(start), 'end': str(end)}
    jobs.append((f'ihsg-{start}.json', 'fetch-index-daily', {'index_code': 'ihsg', **args}))
    for symbol in collector.SYMBOLS:
        jobs.append((f'prices-{symbol}-{start}.json', 'fetch-daily-price', {'symbol': symbol, **args}))
    start = end+timedelta(days=1)

if __name__ == '__main__':
    print(json.dumps({'requests': len(jobs), 'coverage': ['2024-12-01', '2026-01-10']}), flush=True)
    results = []
    for i, job in enumerate(jobs, 1):
        result = collector.collect(job)
        results.append(result)
        if result.get('error') or i % 10 == 0:
            print(json.dumps({'finished': i, 'of': len(jobs), 'error': result.get('error')}), flush=True)
    (OUT.parent/'collection.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps({'completed': sum(not r.get('error') for r in results), 'failures': [r for r in results if r.get('error')]}), flush=True)
