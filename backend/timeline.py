"""Sourced timeline views. Incomplete evidence stays outside the eligible catalog."""
from datetime import date
import json
from math import isfinite
from pathlib import Path
from .data import ROOT, unpack

HISTORY_YEARS = list(range(2021, 2026))
CURRENT_YEAR = 2026  # Snapshot period, not a claim that this feed is live.
PHASES = [('rups_date', 'RUPS'), ('declaration_date', 'Declaration'),
          ('cum_date', 'Cum'), ('ex_date', 'Ex'),
          ('recording_date', 'Recording'), ('payment_date', 'Payment')]


def offset(day, anchor):
    return (date.fromisoformat(day) - date.fromisoformat(anchor)).days


def make_period(event, bars, sources, review=None):
    review = review or {}
    issues, prices = [], {}
    ex = event['ex_date']
    date.fromisoformat(ex)
    for bar in bars:
        try:
            date.fromisoformat(bar['date'])
            close = bar['close']
            if not isinstance(close, (int, float)) or not isfinite(close) or close <= 0:
                raise ValueError('invalid close')
            if bar['date'] in prices and prices[bar['date']] != close:
                issues.append('Harga berbeda pada tanggal yang sama.')
            prices[bar['date']] = close
        except (ValueError, TypeError, KeyError):
            issues.append('Ada bar harga tidak valid.')
    base = prices.get(event.get('cum_date'))
    if base is None:
        issues.append('Harga penutupan cum-date belum tersedia.')
    if ex not in prices:
        issues.append('Harga ex-date belum tersedia.')
    for field in ['cum_date', 'recording_date', 'payment_date']:
        if not event.get(field):
            issues.append(f'{field} belum tersedia.')
    if not event.get('declaration_date') and not event.get('rups_date'):
        issues.append('Tanggal RUPS/declaration terkait event belum terverifikasi.')
    dps = event.get('dividend_amount')
    if not isinstance(dps, (int, float)) or not isfinite(dps) or dps <= 0:
        issues.append('DPS belum valid.')
    try:
        ordered = [date.fromisoformat(event[k]) for k in ['cum_date', 'ex_date', 'recording_date', 'payment_date']]
        if ordered != sorted(ordered):
            issues.append('Urutan tanggal dividen tidak valid.')
    except (ValueError, TypeError, KeyError):
        issues.append('Tanggal dividen belum valid.')
    for key, message in [
        ('announcement_link_verified', 'Hubungan pengumuman dan event belum diverifikasi.'),
        ('sessions_verified', 'Kelengkapan sesi harga belum diverifikasi.'),
        ('basis_verified', 'Basis harga, DPS dan mata uang belum diverifikasi.'),
        ('cycle_verified', 'Jenis siklus dividen belum diverifikasi.'),
    ]:
        if review.get(key) is not True:
            issues.append(message)
    if not review.get('cycle_key'):
        issues.append('Identitas siklus pembanding belum tersedia.')
    if prices and event.get('payment_date') and max(prices) < event['payment_date']:
        issues.append('Harga belum mencapai payment date.')
    starts = [event[k] for k in ['rups_date', 'declaration_date', 'cum_date'] if event.get(k)]
    if prices and starts and min(prices) > min(starts):
        issues.append('Harga belum mencakup awal timeline.')
    if not sources:
        issues.append('Sumber belum tersedia.')
    points = [{'date': day, 'day': offset(day, ex), 'close': close,
               'change_pct': round((close / base - 1) * 100, 6) if base else None}
              for day, close in sorted(prices.items())]
    phases = [{'key': key, 'label': label, 'date': event.get(key),
               'day': offset(event[key], ex) if event.get(key) else None,
               'status': 'recorded' if event.get(key) else 'unavailable'} for key, label in PHASES]
    return {'id': f"{event['symbol'].removesuffix('.JK')}:{ex}",
            'year': int(ex[:4]), 'ex_date': ex, 'dps': dps, 'cum_close': base,
            'cycle': review.get('cycle_label', 'Pembayaran tercatat · jenis belum terverifikasi'),
            'cycle_key': review.get('cycle_key'),
            'points': points, 'phases': phases, 'sources': sources,
            'actual_through': max(prices) if prices else None,
            'issues': sorted(set(issues)), 'eligible': not issues}


def history_eligible(periods, years=HISTORY_YEARS):
    # Require exactly one reviewed, comparable cycle for each requested year.
    cycles = {p.get('cycle_key') for p in periods if p['year'] in years}
    return len(cycles) == 1 and None not in cycles and all(len([p for p in periods if p['year'] == y]) == 1 and
               all(p['eligible'] for p in periods if p['year'] == y) for y in years)


class TimelineDataset:
    def __init__(self, root: Path = ROOT):
        folder = root / 'outputs/timeline-audit'
        self.companies = {}
        coverage_path = folder / 'coverage.json'
        self.coverage = json.loads(coverage_path.read_text()) if coverage_path.exists() else {}
        pilot_path = folder / 'pilot-LPPF.json'
        if not pilot_path.exists():
            return
        periods = []
        for record in json.loads(pilot_path.read_text()):
            path = root / record['price_file']
            if path.exists():
                periods.append(make_period(record['calendar'], unpack(path), [
                    record['price_file'], 'outputs/timeline-audit/pilot-LPPF.json']))
        current = []
        calendar = folder / 'raw/current-calendar-2026-04-01.json'
        if calendar.exists():
            for event in unpack(calendar).get('dividend', []):
                if event['symbol'] != 'LPPF.JK' or not event['ex_date'].startswith(str(CURRENT_YEAR)):
                    continue
                paths = sorted((folder / 'raw').glob('current-prices-LPPF-*.json'))
                bars = [b for path in paths for b in unpack(path)]
                current.append(make_period(event, bars, [str(p.relative_to(root)) for p in [calendar, *paths]]))
        self.companies['LPPF'] = {'symbol': 'LPPF', 'name': 'PT MDS Retailing Tbk',
            'history': periods, 'current': current, 'eligible': history_eligible(periods)}

    def catalog(self):
        return {'history_years': HISTORY_YEARS, 'current_year': CURRENT_YEAR,
            'companies': [{'symbol': c['symbol'], 'name': c['name']} for c in self.companies.values() if c['eligible']],
            'preview_symbols': list(self.companies),
            'calendar_candidates': self.coverage.get('five_year_calendar_core_count', 0),
            'audited_symbols': self.coverage.get('symbol_count', 0),
            'source': 'Sectors MCP + REST · snapshot riset',
            'reason': 'Histori harus lengkap dan terverifikasi sebelum masuk katalog timeline.'}

    def detail(self, symbol, preview=False):
        company = self.companies[symbol]
        if not company['eligible'] and not preview:
            raise ValueError('Histori belum lengkap. Data ini hanya tersedia dalam pratinjau berlabel.')
        return {**company, 'preview': not company['eligible'],
            'history_years': HISTORY_YEARS, 'current_year': CURRENT_YEAR,
            'axis_unit': 'calendar_days', 'forecast': {'status': 'not_available', 'points': [],
                'message': 'Prediksi belum tersedia. Perhitungan akan dikembangkan pada tahap berikutnya.'},
            'source': 'Sectors MCP + REST · snapshot riset',
            'issues': sorted({i for p in company['history'] for i in p['issues']})}
