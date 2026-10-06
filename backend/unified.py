"""One canonical event identity across discovery, intelligence and rotation replay."""
from bisect import bisect_right
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from .data import ROOT, Dataset, unpack
from .intelligence import IntelligenceDataset, valid_bar

RAW = ROOT / 'outputs/rotation/raw'


class UnifiedDataset:
    replay_start = '2025-01-01'
    replay_end = '2025-12-31'
    multi_event = True

    def __init__(self, intelligence: IntelligenceDataset, root: Path = RAW):
        self.intelligence = intelligence
        pilot = Dataset()
        self.companies = deepcopy(pilot.companies)
        self.study = pilot.study
        self.prices = defaultdict(dict)
        self.events, self.quality_issues, self.sources = {}, [], []
        sessions = set()
        fingerprints = []
        for path in sorted(root.glob('*.json')):
            if not path.name.startswith(('prices-', 'ihsg-')):
                continue
            raw = path.read_bytes()
            metadata = json.loads(raw)
            fingerprints.append((path.name, hashlib.sha256(raw).hexdigest()))
            self.sources.append({'file': path.name, 'retrieved_at': metadata.get('retrieved_at'), 'tool': metadata.get('tool')})
            rows = unpack(path)
            if path.name.startswith('ihsg-'):
                sessions.update(r['date'] for r in rows if r.get('price', 0) > 0)
            else:
                for bar in rows:
                    symbol, day = bar['symbol'].removesuffix('.JK'), bar['date']
                    existing = self.prices[symbol].get(day)
                    if existing and existing != bar:
                        self.quality_issues.append({'symbol': symbol, 'date': day, 'reason': 'Konflik harga duplikat'})
                    self.prices[symbol][day] = bar
                    if not valid_bar(bar):
                        self.quality_issues.append({'symbol': symbol, 'date': day, 'reason': 'OHLC/volume tidak valid'})
        self.market_sessions = sorted(sessions)
        # An index-feed gap is not a market holiday. All nine issuer feeds contain
        # trades on four dates absent from the IHSG response; retain that audit.
        consensus = set.intersection(*(set(d for d, b in bars.items() if valid_bar(b)) for bars in self.prices.values())) if len(self.prices) == 9 else set()
        self.session_repairs = sorted(consensus - sessions)
        self.market_sessions = sorted(sessions | consensus)
        sessions = set(self.market_sessions)
        self.retrieved_at = max((s['retrieved_at'] for s in self.sources if s['retrieved_at']), default=None)
        for event in intelligence.events:
            if not event['ex_date'].startswith('2025'):
                continue
            bars = self.prices[event['symbol']]
            problems = list(event['reasons'])
            if not event['payment_date']:
                problems.append('Payment date belum tersedia')
            if any(d not in bars or not valid_bar(bars[d]) or d not in sessions for d in (event['cum_date'], event['ex_date'])):
                problems.append('Harga/sesi cum atau ex belum valid')
            # Both engines must agree on market prices wherever their snapshots overlap.
            for bar in event['bars']:
                fresh = bars.get(bar['date'])
                if fresh and any(fresh[k] != bar[k] for k in ('open', 'high', 'low', 'close')):
                    problems.append('Basis harga intelligence dan replay berbeda')
                    break
            self.events[event['id']] = {k: deepcopy(v) for k, v in event.items() if k not in ('bars', 'next_ex_date')}
            self.events[event['id']].update(
                replay_available=not problems, quality='incomplete' if problems else 'historical',
                reasons=problems, entry_reference=bars.get(event['cum_date'], {}).get('close'),
                source_yield_pct=None, source='; '.join(event['sources']),
                announcement_status='unknown', calendar_assumption=True,
            )
        for symbol, company in self.companies.items():
            rows = sorted([b for d, b in self.prices[symbol].items() if self.replay_start <= d <= self.replay_end and valid_bar(b)], key=lambda b: b['date'])
            company['events'] = [e for e in self.events.values() if e['symbol'] == symbol]
            company['replay_available'] = any(e['replay_available'] for e in company['events'])
            company.update(price=rows[-1]['close'] if rows else None, price_date=rows[-1]['date'] if rows else None,
                           sparkline=[b['close'] for b in rows[-24:]])
        payload = json.dumps({'prices': fingerprints, 'intelligence': intelligence.version, 'events': self.events, 'session_repairs': self.session_repairs}, sort_keys=True)
        self.version = 'unified-' + hashlib.sha256(payload.encode()).hexdigest()[:16]

    def entry_date(self, event, offset):
        cum = event['cum_date']
        if cum not in self.market_sessions:
            raise ValueError('Cum date tidak ada pada sesi IHSG teramati.')
        i = self.market_sessions.index(cum)-offset
        if i < 0:
            raise ValueError('Sesi sebelum cum belum cukup.')
        day = self.market_sessions[i]
        bar = self.prices[event['symbol']].get(day)
        if not bar or not valid_bar(bar):
            raise ValueError('Harga entry belum valid.')
        return day

    def settlement(self, day):
        i = bisect_right(self.market_sessions, day)
        return self.market_sessions[i+1] if i+1 < len(self.market_sessions) else None

    def validate_coverage(self, event, entry, end):
        symbol = event['symbol']
        missing = [d for d in self.market_sessions if entry <= d <= end and (d not in self.prices[symbol] or not valid_bar(self.prices[symbol][d]))]
        if missing:
            raise ValueError(f"{symbol}: harga/volume tidak valid pada {len(missing)} sesi, mulai {missing[0]}.")
        conflicts = [r for r in self.quality_issues if r['symbol'] == symbol and entry <= r['date'] <= end and 'Konflik' in r['reason']]
        if conflicts:
            raise ValueError(f'{symbol}: konflik harga dalam periode replay.')
        if not self.market_sessions or self.market_sessions[-1] < end or self.market_sessions[0] > entry:
            raise ValueError('Cakupan sesi pasar belum cukup.')
        for other in self.events.values():
            if other['symbol'] == symbol and entry <= other['ex_date'] <= end and other['reasons']:
                raise ValueError(f"Dividen lain belum tervalidasi: {other['id']}")

    def catalog(self):
        return {'companies': sorted(self.companies.values(), key=lambda c: -(c['annual_yield_pct'] or 0)),
                'events': sorted(self.events.values(), key=lambda e: (e['ex_date'], e['symbol'])),
                'meta': {'provider': 'Sectors', 'mode': 'historical', 'year': 2025, 'retrieved_at': self.retrieved_at,
                         'dataset_version': self.version, 'quality_issues': self.quality_issues, 'session_repairs': self.session_repairs, 'price_window': [self.replay_start, self.replay_end],
                         'replay_start': self.replay_start, 'replay_end': self.replay_end,
                         'yield_basis': 'Yield2025 hanya deskriptif; planner menghitung ulang statistik sebelum keputusan.',
                         'cost_label': 'Di luar biaya transaksi, pajak, dan slippage', 'sources': self.sources}}

    def detail(self, symbol):
        if symbol not in self.companies:
            raise KeyError(symbol)
        return {**self.companies[symbol], 'prices': sorted([p for d, p in self.prices[symbol].items() if self.replay_start <= d <= self.replay_end and valid_bar(p)], key=lambda p: p['date']),
                'research': self.study if symbol == 'BBCA' else None}
