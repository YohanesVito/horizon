"""Bounded, date-scoped corporate-action and benchmark context via Sectors MCP."""
import json
from datetime import date, datetime, timedelta, timezone
import httpx
from math import isfinite

INDEX_DOCS = 'https://docs.sectors.app/api-references/v2/indonesia/transaction/index-daily'
_ACTION_DATES = {
    'agm': 'agm_date',
    'dividend': 'ex_date',
    'upcoming_dividend': 'ex_date',
    'bonus': 'ex_date',
    'right_issue': 'ex_date',
    'stock_split': 'date',
    'warrant': 'trading_period_start',
}


def _content_json(result):
    if result.get('isError'):
        raise ValueError('Sectors MCP tool returned an error.')
    structured = result.get('structuredContent')
    if structured is not None:
        return structured
    texts = [item['text'] for item in result.get('content', [])
             if item.get('type') == 'text' and isinstance(item.get('text'), str)]
    if not texts:
        raise ValueError('Sectors MCP response has no JSON content.')
    return json.loads('\n'.join(texts))


async def corporate_context(mcp, symbol, low_date, event_id='', stock_cum_date=None):
    """Return sourced corporate actions and an IHSG window around a historical low.

    Each action/index query costs one Sectors credit. Call only for the bounded
    anomaly symbols selected by the caller (currently at most two). IHSG is
    window context only; this function does not infer relative performance.
    """
    anchor = date.fromisoformat(low_date)
    action_start = anchor - timedelta(days=14)
    action_end = min(anchor + timedelta(days=14), date.today())
    try:
        candidate_start = date.fromisoformat(stock_cum_date) if stock_cum_date else None
    except (TypeError, ValueError):
        candidate_start = None
    matched_stock_window = candidate_start is not None and candidate_start <= anchor
    index_end = anchor
    index_start = candidate_start if matched_stock_window else anchor - timedelta(days=14)
    if (index_end - index_start).days > 90:
        index_start = index_end - timedelta(days=90)
        matched_stock_window = False
    sources, gaps = [], []
    try:
        result = await mcp.request('tools/call', {
            'name': 'fetch-corporate-actions', 'arguments': {'symbol': symbol}})
        payload = _content_json(result)
        requested_symbol = symbol.upper().removesuffix('.JK')
        returned_symbol = payload.get('symbol', '') if isinstance(payload, dict) else ''
        if returned_symbol and returned_symbol.upper().removesuffix('.JK') != requested_symbol:
            raise ValueError('Corporate actions returned a different symbol.')
        actions = payload.get('corporate_actions', {}) if isinstance(payload, dict) else {}
        if not isinstance(actions, dict):
            raise ValueError('Invalid corporate actions response.')
        matched = []
        for category, date_field in _ACTION_DATES.items():
            rows = actions.get(category) or []
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                action_date = row.get(date_field)
                if isinstance(action_date, str) and action_start.isoformat() <= action_date[:10] <= action_end.isoformat():
                    detail = {k: v for k, v in row.items() if k in {
                        'dividend_amount', 'split_ratio', 'rights_ratio', 'ratio',
                        'trading_period_start', 'trading_period_end',
                    } and v is not None}
                    matched.append({'date': action_date[:10], 'type': category, **detail})
        if matched:
            matched.sort(key=lambda row: (row['date'], row['type']))
            endpoint = f'https://api.sectors.app/v2/company/corporate-actions/{requested_symbol}/'
            for index, row in enumerate(matched[:4]):
                details = ', '.join(f'{key}={value}' for key, value in row.items()
                                    if key not in ('date', 'type'))
                label = f"Sectors {row['type']} {symbol} · {row['date']}"
                if details:
                    label += f' · {details}'
                sources.append({
                    'id': f'corporate-{requested_symbol.lower()}-{index + 1}',
                    'title': label,
                    'url': endpoint, 'published_at': row['date'], 'symbol': symbol,
                    'event_id': event_id or None,
                    'excerpt': json.dumps(row, ensure_ascii=False, sort_keys=True),
                    'source_kind': 'provider_record',
                    'retrieved_at': datetime.now(timezone.utc).isoformat(),
                })
        else:
            gaps.append(f"Tidak ada catatan aksi korporasi Sectors untuk {symbol} pada {action_start.isoformat()}–{action_end.isoformat()}; kelengkapan arsip tidak diketahui.")
    except (httpx.HTTPError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        gaps.append(f'Aksi korporasi {symbol} belum dapat ditelusuri melalui Sectors MCP.')

    if anchor < date(2019, 1, 2):
        gaps.append(f'Pembanding IHSG belum tersedia untuk {low_date}; endpoint Sectors mulai 2 Januari 2019.')
        return sources, gaps
    try:
        result = await mcp.request('tools/call', {
            'name': 'fetch-index-daily',
            'arguments': {'index_code': 'ihsg', 'start': index_start.isoformat(), 'end': index_end.isoformat()},
        })
        rows = _content_json(result)
        if isinstance(rows, dict):
            rows = rows.get('results', rows.get('data'))
        if not isinstance(rows, list):
            raise ValueError('Invalid index response.')
        usable = []
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('date'), str):
                continue
            price = row.get('price')
            day = row['date'][:10]
            if (index_start.isoformat() <= day <= index_end.isoformat() and isinstance(price, (int, float))
                    and isfinite(price) and price > 0):
                usable.append((day, float(price)))
        usable.sort()
        if len(usable) >= 2:
            first, last = usable[0], usable[-1]
            change_pct = (last[1] / first[1] - 1) * 100
            window_label = 'jendela cum-date ke low saham' if matched_stock_window else 'jendela sebelum low; bukan perbandingan relatif saham'
            excerpt = (f"IHSG {first[0]}: {first[1]:.2f}; {last[0]}: {last[1]:.2f}; "
                       f"perubahan {change_pct:+.2f}% sepanjang {window_label}. Konteks pasar luas, bukan bukti penyebab.")
            sources.append({
                'id': f'ihsg-{symbol.lower()}',
                'title': (f'IHSG {first[0]}–{last[0]} · {first[1]:.2f} → {last[1]:.2f} '
                          f'({change_pct:+.2f}%) · {window_label}'),
                'url': INDEX_DOCS, 'published_at': last[0], 'symbol': symbol,
                'event_id': event_id or None, 'excerpt': excerpt,
                'source_kind': 'provider_record',
                'retrieved_at': datetime.now(timezone.utc).isoformat(),
            })
        else:
            gaps.append(f'Data IHSG tidak cukup pada jendela {index_start.isoformat()}–{index_end.isoformat()} untuk dibandingkan.')
    except (httpx.HTTPError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        gaps.append(f'Pembanding IHSG {symbol} belum dapat ditelusuri melalui Sectors MCP.')
    return sources, gaps
