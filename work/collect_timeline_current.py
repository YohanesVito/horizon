"""Collect the current-year LPPF preview via Sectors MCP; no forecast values."""
from datetime import date, timedelta, datetime, timezone
import json
import subprocess
import sys
import time
from audit_timeline_overlay import ROOT, RAW, unpack
from sectors_mcp_probe import Client


def main():
    client = Client()
    client.initialize()
    start, cutoff = date(2026, 4, 3), date(2026, 10, 7)
    while start <= cutoff:
        end = min(start + timedelta(days=89), cutoff)
        path = RAW / f'current-prices-LPPF-{start}.json'
        if not path.exists():
            args = {'symbol': 'LPPF', 'start': str(start), 'end': str(end)}
            result = client.request('tools/call', {'name': 'fetch-daily-price', 'arguments': args})
            path.write_text(json.dumps({'transport': 'MCP Streamable HTTP',
                'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'tool': 'fetch-daily-price', 'arguments': args, 'result': result}, indent=2))
        bars = unpack(path)
        print(json.dumps({'file': path.name, 'bars': len(bars)}), flush=True)
        start = end + timedelta(days=1)
        time.sleep(4)
    path = RAW / 'current-calendar-2026-04-01.json'
    if not path.exists():
        subprocess.run([sys.executable, str(ROOT / 'work/sectors_calendar_probe.py'),
            '--start', '2026-04-01', '--end', '2026-06-29', '--output', str(path)],
            capture_output=True, check=True)
    print(json.dumps({'file': path.name, 'events': len(unpack(path)['dividend'])}))


if __name__ == '__main__':
    main()
