"""Transparent empirical risk and recovery, separate from the replay dataset.

All outputs are exploratory. No fitted predictive model or hidden imputation.
See docs/development/INTELLIGENCE_POLICY.md for definitions and limitations.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
from math import isclose, isfinite, sqrt
from pathlib import Path
from statistics import NormalDist, median

from .data import ROOT, unpack

RAW = ROOT / 'outputs/intelligence/raw'
SYMBOLS = ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS']
VERSION = 'empirical-v1.0'
LIMITS = [
    'Statistik sampel terpilih 2022–2025, bukan seluruh IDX atau probabilitas prediksi tervalidasi.',
    'Wilson 95% memakai asumsi binomial independen; korelasi antar-event dan perubahan rezim belum dimodelkan.',
    'Tanggal declaration dan vintage data tidak tersedia; kelayakan membeli sebelum pengumuman belum terbukti.',
    'Hari bursa mengikuti harga teramati. Kalender resmi dan penjelasan suspensi belum tersedia.',
    'Price BEP adalah sinyal close mencapai harga entry, bukan jaminan eksekusi atau waktu settlement.',
    'DPS diperlakukan sebagai IDR sesuai data IDX Sectors; respons tidak membawa metadata mata uang per event.',
    'Censoring akibat dividen berikutnya dapat informatif; kurva KM eksploratif tidak membuktikan peluang pemulihan masa depan.',
    'Di luar biaya transaksi, pajak, dan slippage. Dividen dapat masih berupa piutang.',
]


def wilson(losses, n):
    """Two-sided nominal 95% score interval, including all-success/failure cases."""
    if not n:
        return None
    if not 0 <= losses <= n:
        raise ValueError('Invalid binomial count')
    z = NormalDist().inv_cdf(.975)
    p, denom = losses / n, 1 + z*z/n
    centre = (p + z*z/(2*n)) / denom
    half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
    return [max(0., centre-half)*100, min(1., centre+half)*100]


def quantile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered)-1)*q
    lower = int(position)
    upper = min(lower+1, len(ordered)-1)
    return ordered[lower]+(ordered[upper]-ordered[lower])*(position-lower)


def kaplan_meier(observations, horizon):
    """(observed time, reached BEP); ties recover before censors leave risk set."""
    survival, curve = 1., []
    last_observed = max((duration for duration, _ in observations), default=-1)
    for t in range(horizon+1):
        at_risk = sum(duration >= t for duration, _ in observations)
        recovered = sum(duration == t and reached for duration, reached in observations)
        censored = sum(duration == t and not reached for duration, reached in observations)
        if at_risk:
            survival *= (1 - recovered/at_risk)
        curve.append({'session': t, 'at_risk': at_risk, 'recovered': recovered, 'censored': censored,
                      'recovery_pct': (1-survival)*100 if observations and (t <= last_observed or survival == 0) else None})
    return {'curve': curve, 'median_sessions': next((r['session'] for r in curve if r['recovery_pct'] is not None and r['recovery_pct'] >= 50), None)}


def valid_bar(bar):
    values = [bar.get(k) for k in ('open', 'high', 'low', 'close')]
    return (all(type(v) in (int, float) and isfinite(v) and v > 0 for v in values)
            and bar['low'] <= min(bar['open'], bar['close']) <= max(bar['open'], bar['close']) <= bar['high']
            and type(bar.get('volume')) in (int, float) and bar['volume'] > 0)


class IntelligenceDataset:
    def __init__(self, root: Path = RAW):
        self.events = []
        self.sources = []
        calendar = defaultdict(list)
        calendar_sources = defaultdict(list)
        digest = hashlib.sha256()
        for path in sorted(root.glob('*.json')):
            if not path.name.startswith(('actions-', 'prices-', 'calendar-')):
                continue
            raw = path.read_bytes()
            digest.update(path.name.encode() + raw)
            metadata = json.loads(raw)
            self.sources.append({'file': path.name, 'retrieved_at': metadata.get('retrieved_at'),
                                 'tool': metadata.get('tool', 'Sectors REST calendar'),
                                 'sha256': hashlib.sha256(raw).hexdigest()})
            if path.name.startswith('calendar-'):
                for row in unpack(path).get('dividend', []):
                    key = (row['symbol'].removesuffix('.JK'), row['ex_date'])
                    calendar[key].append(row)
                    calendar_sources[key].append(path.name)
        for symbol in SYMBOLS:
            path = root / f'actions-{symbol}.json'
            if not path.exists():
                continue
            actions = unpack(path)['corporate_actions']
            seen = set()
            dividends = actions.get('dividend') or []
            for row in sorted(dividends, key=lambda r: r['ex_date']):
                ex = row['ex_date']
                if not '2022-01-01' <= ex <= '2025-12-31' or ex in seen:
                    continue
                seen.add(ex)
                candidates = [r for r in dividends if r['ex_date'] == ex] + calendar.get((symbol, ex), [])
                event = {'id': f'{symbol}:{ex}', 'symbol': symbol, 'ex_date': ex, 'declaration_date': None,
                         'dps': row.get('dividend_amount'), 'cum_date': None, 'payment_date': row.get('payment_date'),
                         'recording_date': None, 'reasons': [], 'warnings': [], 'bars': [],
                         'sources': [path.name, *calendar_sources.get((symbol, ex), [])]}
                for key in ['dividend_amount', 'cum_date', 'payment_date', 'recording_date']:
                    values = [c[key] for c in candidates if c.get(key) is not None]
                    if values and any(not isclose(v, values[0], rel_tol=1e-6, abs_tol=1e-6) if key == 'dividend_amount' else v != values[0] for v in values):
                        event['reasons'].append(f'Konflik Sectors: {key}')
                    if key != 'dividend_amount' and values:
                        event[key] = values[0]
                if not event['cum_date'] or not event['cum_date'] < ex:
                    event['reasons'].append('Cum date tidak tersedia atau tidak mendahului ex')
                if any(event[k] and event[k] < ex for k in ('payment_date', 'recording_date')):
                    event['reasons'].append('Urutan tanggal tidak valid')
                if not isinstance(event['dps'], (int, float)) or not isfinite(event['dps']) or event['dps'] <= 0:
                    event['reasons'].append('DPS tidak valid')
                # Provider dividend histories can be split-adjusted while old OHLC are not.
                if any(split['date'] >= ex for split in actions.get('stock_split') or []):
                    event['reasons'].append('Event sebelum split; kesetaraan basis DPS/OHLC belum terverifikasi')
                prices_path = root / f'prices-{symbol}-{ex}.json'
                if prices_path.exists():
                    bars = sorted(unpack(prices_path), key=lambda b: b['date'])
                    event['sources'].append(prices_path.name)
                    if len({b['date'] for b in bars}) != len(bars):
                        event['reasons'].append('Tanggal harga duplikat')
                    if any(b['symbol'].removesuffix('.JK') != symbol for b in bars):
                        event['reasons'].append('Symbol harga tidak cocok')
                    event['bars'] = bars
                    if bars:
                        for key in ('right_issue', 'bonus', 'warrant'):
                            for action in actions.get(key) or []:
                                action_date = action.get('ex_date') or action.get('date')
                                if action_date and bars[0]['date'] <= action_date <= bars[-1]['date']:
                                    event['reasons'].append(f'Aksi lain dalam jendela: {key}')
                        gaps = [(a['date'], b['date']) for a, b in zip(bars, bars[1:]) if (date.fromisoformat(b['date'])-date.fromisoformat(a['date'])).days > 7]
                        if gaps:
                            event['warnings'].append('Jeda harga >7 hari; mungkin libur/suspensi, belum diverifikasi')
                else:
                    event['reasons'].append('Snapshot harga belum tersedia')
                event['next_ex_date'] = min((d['ex_date'] for d in dividends if d['ex_date'] > ex), default=None)
                self.events.append(event)
        self.version = 'intelligence-' + digest.hexdigest()[:16]

    def observe(self, event, entry_offset, horizon):
        result = {k: v for k, v in event.items() if k not in ('bars', 'next_ex_date')}
        result['reasons'] = list(event['reasons'])
        bars = event['bars']
        dates = [b['date'] for b in bars]
        if event['cum_date'] not in dates or event['ex_date'] not in dates:
            result['reasons'].append('Harga cum/ex tidak tersedia')
        if result['reasons']:
            return {**result, 'eligible': False}
        cum_idx, ex_idx = dates.index(event['cum_date']), dates.index(event['ex_date'])
        entry_idx = cum_idx-entry_offset
        if entry_idx < 0 or not all(valid_bar(b) for b in bars[entry_idx:ex_idx+1]):
            return {**result, 'eligible': False, 'reasons': ['Harga entry/cum/ex tidak lengkap atau OHLC/volume invalid']}
        entry = bars[entry_idx]['close']
        post = []
        for bar in bars[ex_idx:ex_idx+horizon+1]:
            if not valid_bar(bar) or (event['next_ex_date'] and bar['date'] >= event['next_ex_date']):
                break
            post.append(bar)
        if not post:
            return {**result, 'eligible': False, 'reasons': ['Tidak ada harga ex yang valid']}
        observed = len(post)-1
        complete = observed == horizon
        recovery = next((i for i, bar in enumerate(post) if bar['close'] >= entry), None)
        dps_decimal, entry_decimal = Decimal(str(event['dps'])), Decimal(str(entry))
        total_recovery = next((i for i, bar in enumerate(post) if Decimal(str(bar['close']))+dps_decimal >= entry_decimal), None)
        price_returns = [(bar['close']/entry-1)*100 for bar in post]
        gross_return = float((Decimal(str(post[-1]['close']))-entry_decimal+dps_decimal)/entry_decimal*100)
        return {**result, 'eligible': True, 'entry_date': dates[entry_idx], 'entry_price': entry,
                'observed_sessions': observed, 'complete': complete, 'last_date': post[-1]['date'],
                'price_bep_session': recovery, 'total_bep_session': total_recovery,
                'price_return_pct': price_returns[-1] if complete else None,
                'gross_return_pct': gross_return if complete else None, 'trap': gross_return < 0 if complete else None,
                'dividend_paid_at_horizon': bool(event['payment_date'] and event['payment_date'] <= post[-1]['date']) if complete else None,
                'price_path_pct': price_returns, 'worst_price_move_pct': min(price_returns),
                'early_censor_reason': None if complete else 'Data terpotong/invalid atau ada ex-dividen berikutnya'}

    def analyze(self, entry_offset=5, horizon=20, as_of=None):
        # A decision at the beginning of a date cannot use that day's close.
        # Clip before observation, so an unfinished event remains censored.
        events = self.events
        if as_of:
            events = [{**e, 'bars': [b for b in e['bars'] if b['date'] < as_of],
                       'next_ex_date': e['next_ex_date'] if e['next_ex_date'] and e['next_ex_date'] < as_of else None}
                      for e in events if e['ex_date'] < as_of]
        observations = [self.observe(e, entry_offset, horizon) for e in events]
        companies = []
        for symbol in SYMBOLS:
            rows = [r for r in observations if r['symbol'] == symbol]
            valid = [r for r in rows if r['eligible']]
            full = [r for r in valid if r['complete']]
            price = kaplan_meier([(r['price_bep_session'] if r['price_bep_session'] is not None else r['observed_sessions'], r['price_bep_session'] is not None) for r in valid], horizon)
            total = kaplan_meier([(r['total_bep_session'] if r['total_bep_session'] is not None else r['observed_sessions'], r['total_bep_session'] is not None) for r in valid], horizon)
            returns = [r['gross_return_pct'] for r in full]
            losses = sum(r['trap'] for r in full)
            temporal = []
            for name, start, end in [('2022–2024', '2022', '2024'), ('2025', '2025', '2025')]:
                subset = [r for r in full if start <= r['ex_date'][:4] <= end]
                temporal.append({'period': name, 'n': len(subset), 'trap_pct': sum(r['trap'] for r in subset)/len(subset)*100 if subset else None})
            companies.append({'symbol': symbol, 'total_events': len(rows), 'eligible_events': len(valid), 'complete_events': len(full),
                              'excluded_events': len(rows)-len(valid), 'early_censored': sum(not r['complete'] for r in valid),
                              'price_unrecovered': sum(r['price_bep_session'] is None for r in valid),
                              'total_unrecovered': sum(r['total_bep_session'] is None for r in valid),
                              'losses': losses, 'trap_pct': losses/len(full)*100 if full else None, 'trap_interval': wilson(losses, len(full)),
                              'median_return_pct': median(returns) if returns else None, 'worst_return_pct': min(returns) if returns else None,
                              'price_recovery': price, 'total_recovery': total, 'temporal': temporal,
                              'evidence_status': 'exploratory' if full else 'insufficient_data',
                              'period': [min(r['ex_date'] for r in valid), max(r['ex_date'] for r in valid)] if valid else None,
                              'events': rows})
        return {'version': VERSION, 'dataset_version': self.version, 'entry_offset': entry_offset, 'horizon': horizon, 'as_of': as_of,
                'companies': companies, 'sources': self.sources, 'limitations': LIMITS,
                'audit': {'symbols': len(SYMBOLS), 'events': len(observations), 'eligible': sum(r['eligible'] for r in observations),
                          'complete': sum(r.get('complete', False) for r in observations),
                          'excluded': sum(not r['eligible'] for r in observations)}}


def rank(analysis, rules):
    ranked, excluded = [], []
    for company in analysis['companies']:
        reasons = []
        if company['complete_events'] < rules.minimum_samples:
            reasons.append(f"Sampel lengkap {company['complete_events']} < {rules.minimum_samples}")
        interval = company['trap_interval']
        if interval is None or interval[1] > rules.maximum_loss_upper_pct:
            reasons.append('Batas atas Wilson risiko rugi melewati aturan tim atau tidak tersedia')
        if company['median_return_pct'] is None or company['median_return_pct'] < rules.minimum_median_return_pct:
            reasons.append('Median return di bawah aturan atau tidak tersedia')
        if rules.objective == 'recovery' and company['price_recovery']['median_sessions'] is None:
            reasons.append('Median BEP belum tercapai')
        item = {k: company[k] for k in ['symbol', 'complete_events', 'trap_pct', 'trap_interval', 'median_return_pct', 'worst_return_pct']}
        item['median_recovery_sessions'] = company['price_recovery']['median_sessions']
        item['reasons'] = reasons
        (excluded if reasons else ranked).append(item)
    field, direction = {'return': ('median_return_pct', -1), 'worst_return': ('worst_return_pct', -1),
                        'risk': ('trap_pct', 1), 'recovery': ('median_recovery_sessions', 1)}[rules.objective]
    ranked.sort(key=lambda r: (direction*r[field], r['symbol']))
    for i, row in enumerate(ranked, 1):
        row['rank'] = i
    return {'ranked': ranked, 'excluded': excluded, 'rules': rules.model_dump(), 'dataset_version': analysis['dataset_version'],
            'version': VERSION, 'label': 'Ranking historis eksploratif; bukan rekomendasi atau forecast'}


def scenario(analysis, request):
    company = next((c for c in analysis['companies'] if c['symbol'] == request.symbol), None)
    if not company:
        raise ValueError('Emiten tidak tersedia.')
    events = [e for e in company['events'] if e['eligible'] and e['complete']]
    # Historical analogs must finish strictly before the hypothetical entry date.
    events = [e for e in events if e['last_date'] < request.entry_date.isoformat()]
    if not events:
        raise ValueError('Tidak ada analog lengkap yang berakhir sebelum tanggal masuk skenario.')
    capital, entry, dps = request.capital, request.entry_price, request.dps
    shares = int((capital/(entry*100)).to_integral_value(rounding=ROUND_FLOOR))*100
    if shares == 0:
        raise ValueError('Modal belum cukup untuk satu lot pada harga input.')
    leftover = capital-shares*entry
    dividend = shares*dps
    rows = []
    paths = []
    for event in events:
        # Price scenario only: replace the old dividend with the user's assumed DPS.
        change = Decimal(str(event['price_return_pct']))/100
        exit_price = entry*(1+change)
        gain = shares*(exit_price-entry)
        pnl = gain+dividend
        paths.append([float(shares*entry*Decimal(str(pct))/100+dividend) for pct in event['price_path_pct']])
        rows.append({'event_id': event['id'], 'ex_date': event['ex_date'], 'price_change_pct': float(change*100),
                     'exit_price': float(exit_price), 'capital_gain': float(gain), 'dividend': float(dividend),
                     'gross_pnl': float(pnl), 'gross_return_pct': float(pnl/capital*100),
                     'ending_value': float(capital+pnl), 'price_bep_session': event['price_bep_session'],
                     'assumed_receivable': request.payment_date > request.valuation_date})
    rows.sort(key=lambda r: r['gross_pnl'])
    values = [r['gross_pnl'] for r in rows]
    trajectory = [{'session': t, 'p10': quantile([path[t] for path in paths], .1),
                   'median': median(path[t] for path in paths), 'p90': quantile([path[t] for path in paths], .9)}
                  for t in range(analysis['horizon']+1)]
    return {'symbol': request.symbol, 'analog_count': len(rows), 'shares': shares, 'uninvested_cash': float(leftover),
            'dividend_entitlement': float(dividend), 'dividend_cash': float(dividend) if request.payment_date <= request.valuation_date else 0,
            'dividend_receivable': float(dividend) if request.payment_date > request.valuation_date else 0,
            'price_bep': float(entry), 'total_bep': float(entry-dps),
            'pnl': {'worst': min(values), 'p10': quantile(values, .1), 'median': median(values), 'p90': quantile(values, .9), 'best': max(values)},
            'loss_scenarios': sum(v < 0 for v in values), 'rows': rows, 'dataset_version': analysis['dataset_version'],
            'trajectory': trajectory, 'worst_observed_pnl': min(value for path in paths for value in path),
            'version': 'analogs-v1.0', 'model_version': None,
            'assumptions': [
                'Stress test satu posisi: harga/DPS/jadwal diinput pengguna, bukan jadwal terkonfirmasi atau target harga.',
                f"Perubahan harga analog dari entry {analysis['entry_offset']} hari bursa sebelum cum hingga t{analysis['horizon']} setelah ex diterapkan ke harga input.",
                'Tanggal valuasi adalah asumsi tanggal tH dari pengguna; jumlah hari bursa menurut kalender BEI belum diverifikasi.',
                'P10/P50/P90 adalah kuantil sampel analog, bukan peluang/rentang prediksi masa depan.',
                'Kurva kuantil dihitung per hari bursa; tiap garis bukan satu jalur event dan bukan simulasi eksekusi.',
                'Nilai akhir adalah valuasi posisi + hak dividen + sisa kas; bukan kas siap rotasi. Tidak menyimulasikan penjualan/T+2.',
                'Di luar biaya transaksi, pajak, dan slippage. Tidak memasukkan dividen kedua atau reinvestasi.',
            ]}
