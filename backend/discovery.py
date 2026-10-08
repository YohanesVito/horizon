"""Historical dividend candidates from a dated, read-only Sectors MCP snapshot."""

import json
from math import isfinite
from pathlib import Path

from .data import ROOT, unpack


SNAPSHOT = 'outputs/dividend-discovery/top-yield-2025-mcp-2026-10-08.json'


def top_dividend_yield(root: Path = ROOT, limit: int = 5):
    path = root / SNAPSHOT
    envelope = json.loads(path.read_text())
    results = unpack(path)
    rows = []
    seen = set()
    for item in results['results']:
        symbol = item['symbol'].removesuffix('.JK')
        values = item.get('query_values') or {}
        yield_ratio = values.get('total_yield[2025]')
        dps = values.get('total_dividend[2025]')
        if (symbol in seen or not isinstance(yield_ratio, (int, float))
                or not isfinite(yield_ratio) or yield_ratio <= 0
                or not isinstance(dps, (int, float)) or not isfinite(dps) or dps <= 0):
            continue
        seen.add(symbol)
        rows.append({'symbol': symbol, 'name': item['company_name'],
                     'dps': dps, 'yield_pct': yield_ratio * 100})
    rows.sort(key=lambda row: (-row['yield_pct'], row['symbol']))
    return {'year': 2025, 'as_of': envelope['retrieved_at'],
            'source': 'Sectors MCP · fetch-companies',
            'basis': 'Total yield tahunan 2025 menurut Sectors; bukan yield mendatang atau proyeksi laba.',
            'universe_count': results['pagination']['total_count'],
            'candidates': rows[:limit]}
