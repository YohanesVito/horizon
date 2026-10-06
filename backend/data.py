"""Normalize immutable Sectors snapshots without inventing missing market fields."""
from pathlib import Path
import json
import hashlib
from math import isfinite
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'outputs/dividend-research'
MVP = ROOT / 'outputs/mvp-sectors'


def unpack(path: Path):
    body = json.loads(path.read_text())
    result = body.get('result', body)
    if isinstance(result, dict) and 'content' in result:
        if result.get('isError'):
            raise ValueError(f'Respons Sectors gagal: {path.name}')
        return json.loads(next(b['text'] for b in result['content'] if b['type'] == 'text'))
    return result


class Dataset:
    def __init__(self):
        self.prices = defaultdict(dict)
        self.events = {}
        self.companies = {}
        self.quality_issues = []
        self.study = json.loads((RESEARCH / 'study-results.json').read_text())
        self.retrieved_at = json.loads((RESEARCH / 'calendar-2025-spring.json').read_text())['retrieved_at']
        reports = list(RESEARCH.glob('dividend-*.json')) + list(MVP.glob('report-*.json'))
        reports += [ROOT / 'outputs/sectors-live/bbca-dividend.json']
        for path in reports:
            report = unpack(path)
            symbol = report['symbol'].replace('.JK', '')
            d = report.get('dividend', {}) or {}
            annual = (d.get('historical_dividends', {}) or {}).get('2025', {})
            history = []
            for year, value in (d.get('historical_dividends', {}) or {}).items():
                history.append({'year': int(year), 'dps': value.get('total_dividend'), 'yield_pct': value['total_yield'] * 100 if value.get('total_yield') is not None else None, 'frequency': len(value.get('breakdown', []))})
            self.companies[symbol] = {
                'symbol': symbol, 'name': report.get('company_name', symbol),
                'annual_yield_pct': annual['total_yield'] * 100 if annual.get('total_yield') is not None else None,
                'annual_dps': annual.get('total_dividend'),
                'frequency': len(annual.get('breakdown', [])), 'year': 2025,
                'history': sorted(history, key=lambda x: x['year']),
            }
        for path in list(RESEARCH.glob('bbca-prices-*.json')) + list(MVP.glob('prices-*.json')):
            for bar in unpack(path):
                if not all(isinstance(bar.get(k), (int, float)) and isfinite(bar[k]) and bar[k] > 0 for k in ('open', 'high', 'low', 'close')):
                    self.quality_issues.append({'source': path.name, 'date': bar.get('date'), 'reason': 'Invalid OHLC; excluded'})
                    continue
                self.prices[bar['symbol'].replace('.JK', '')][bar['date']] = bar
        calendars = [RESEARCH / 'calendar-2025-spring.json'] + list(RESEARCH.glob('calendar-202[2345]-*.json'))
        for path in calendars:
            for row in unpack(path).get('dividend', []):
                self.add_event(row, path.name)
        # Company histories supplement discovery, but missing dates remain unknown.
        for path in reports:
            report = unpack(path)
            div = (report.get('dividend') or {}).get('historical_dividends', {}).get('2025', {})
            for row in div.get('breakdown', []):
                symbol = report['symbol'].replace('.JK', '')
                key = f"{symbol}:{row['date']}"
                if key not in self.events:
                    self.add_event({'symbol': symbol, 'ex_date': row['date'], 'dividend_amount': row['total'], 'dividend_yield': row.get('yield')}, path.name)
        self.events = dict(sorted(self.events.items(), key=lambda item: (item[1]['ex_date'], item[1]['symbol'])))
        for symbol, company in self.companies.items():
            events = [e for e in self.events.values() if e['symbol'] == symbol and e['ex_date'].startswith('2025')]
            company['events'] = events
            company['replay_available'] = any(e['replay_available'] for e in events)
            prices = [b for date, b in self.prices[symbol].items() if '2025-02-24' <= date <= '2025-05-20']
            prices.sort(key=lambda b: b['date'])
            company['price'] = prices[-1]['close'] if prices else None
            company['price_date'] = prices[-1]['date'] if prices else None
            company['sparkline'] = [b['close'] for b in prices[-24:]]
        self.market_sessions = sorted({d for bars in self.prices.values() for d in bars})
        # Fingerprint the actual normalized market inputs, independent of local paths.
        contents = json.dumps({'events': self.events, 'prices': self.prices, 'companies': self.companies}, sort_keys=True)
        self.version = 'sectors-' + hashlib.sha256(contents.encode()).hexdigest()[:16]

    def add_event(self, row, source):
        symbol = row['symbol'].replace('.JK', '')
        key = f"{symbol}:{row['ex_date']}"
        bars = self.prices.get(symbol, {})
        cum = row.get('cum_date')
        dps = row.get('dividend_amount')
        valid_dps = isinstance(dps, (int, float)) and isfinite(dps) and dps >= 0
        valid_dates = bool(cum and cum < row['ex_date'] and all(not row.get(k) or row[k] >= row['ex_date'] for k in ('payment_date', 'recording_date')))
        duplicate = self.events.get(key)
        conflict = bool(duplicate and (duplicate['quality'] == 'conflict' or duplicate['dps'] != dps or any(duplicate.get(k) != row.get(k) for k in ('cum_date', 'payment_date', 'recording_date'))))
        if conflict:
            duplicate.update(replay_available=False, quality='conflict')
            self.quality_issues.append({'source': source, 'id': key, 'reason': 'Conflicting schedule; excluded from replay'})
            return
        self.events[key] = {
            'id': key, 'symbol': symbol, 'declaration_date': None,
            'cum_date': cum, 'ex_date': row['ex_date'],
            'recording_date': row.get('recording_date'), 'payment_date': row.get('payment_date'),
            'dps': dps, 'source_yield_pct': row.get('dividend_yield') * 100 if row.get('dividend_yield') is not None else None,
            'entry_reference': bars.get(cum, {}).get('close'),
            'replay_available': bool(cum in bars and row['ex_date'] in bars and valid_dps and valid_dates and '2025-03-01' <= row['ex_date'] <= '2025-05-20'),
            'quality': 'historical' if valid_dates and valid_dps else 'incomplete',
            'source': source,
        }

    def catalog(self):
        return {
            'companies': sorted(self.companies.values(), key=lambda c: -(c['annual_yield_pct'] or 0)),
            'events': [e for e in self.events.values() if e['ex_date'].startswith('2025')],
            'meta': {'provider': 'Sectors', 'mode': 'historical', 'year': 2025, 'retrieved_at': self.retrieved_at,
                     'dataset_version': self.version, 'quality_issues': self.quality_issues,
                     'price_window': ['2025-02-24', '2025-05-20'],
                     'yield_basis': 'Yield tahunan versi Sectors; bukan proyeksi return strategi.',
                     'cost_label': 'Di luar biaya transaksi, pajak, dan slippage'},
        }

    def detail(self, symbol):
        if symbol not in self.companies:
            raise KeyError(symbol)
        return {**self.companies[symbol], 'prices': sorted([p for d, p in self.prices[symbol].items() if '2025-02-24' <= d <= '2025-05-20'], key=lambda b: b['date']),
                'research': self.study if symbol == 'BBCA' else None}
