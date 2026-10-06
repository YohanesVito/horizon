"""Deterministic daily replay. No forecast, order execution, or synthetic market prices."""
from decimal import Decimal, ROUND_FLOOR
from bisect import bisect_right
from datetime import date
from .domain import SimulationRequest

D = lambda value: Decimal(str(value))


def number(value):
    return round(float(value), 4)


def simulate(dataset, request: SimulationRequest, allocation=None):
    allocation = allocation or request.allocation
    end = request.end_date.isoformat()
    unified = getattr(dataset, 'multi_event', False)
    selected = []
    for event_id in request.event_ids:
        event = dataset.events.get(event_id)
        if not event or not event['replay_available']:
            raise ValueError('Event tidak memiliki harga dan jadwal yang cukup untuk replay: ' + event_id)
        if not unified and not '2025-03-01' <= event['ex_date'] <= '2025-05-20':
            raise ValueError('Event di luar jendela replay Maret–Mei 2025.')
        if event['ex_date'] > end:
            raise ValueError('Tanggal akhir harus setelah ex-date semua event yang dipilih.')
        selected.append(event)
    if not unified and len({e['symbol'] for e in selected}) != len(selected):
        raise ValueError('Pilih satu event per emiten untuk replay MVP ini.')
    if not unified and (end > '2025-05-20' or end < '2025-03-21'):
        raise ValueError('Dataset replay ini mendukung tanggal akhir 21 Maret–20 Mei 2025.')
    if unified and not dataset.replay_start <= end <= dataset.replay_end:
            raise ValueError('Dataset terpadu mendukung replay dalam tahun 2025.')
    selected.sort(key=lambda e: (e['cum_date'], e['symbol']))
    if allocation == 'single':
        selected = selected[:1]
    plans = []
    for event in selected:
        bars = dataset.prices[event['symbol']]
        dates = dataset.market_sessions if unified else sorted(bars)
        cum_idx, ex_idx = dates.index(event['cum_date']), dates.index(event['ex_date'])
        entry_idx = cum_idx - request.entry_sessions_before_cum
        if entry_idx < 0:
            raise ValueError(f"Harga sebelum cum {event['symbol']} belum cukup.")
        entry = dates[entry_idx]
        if request.start_date and entry < request.start_date.isoformat():
            raise ValueError(f"Entry {event['id']} mendahului awal periode.")
        if entry > end:
            raise ValueError('Tanggal masuk berada setelah akhir simulasi.')
        last_idx = min(ex_idx + request.max_holding_sessions, len(dates) - 1)
        limit = min(dates[last_idx], end)
        if unified:
            coverage_end = event['ex_date'] if request.exit_rule == 'ex_close' else limit
            if request.exit_rule == 'payment_close' and event.get('payment_date'):
                payment_session = next((d for d in dates if d >= event['payment_date']), None)
                if payment_session:
                    coverage_end = min(coverage_end, payment_session)
            dataset.validate_coverage(event, entry, coverage_end)
        exit_date, price_field, exit_reason = None, 'close', 'Belum keluar'
        signal_date = None
        if request.exit_rule == 'ex_close':
            exit_date, exit_reason = event['ex_date'], 'Close ex-date'
        elif request.exit_rule == 'payment_close':
            payment = event.get('payment_date')
            if not payment:
                raise ValueError(f"Payment date {event['symbol']} belum tersedia.")
            exit_date = next((d for d in dates if d >= payment and d <= end), None)
            exit_reason = 'Close pada/setelah payment date'
            if unified and ex_idx + request.max_holding_sessions < len(dates):
                cap_date = dates[ex_idx + request.max_holding_sessions]
                if cap_date <= end and (exit_date is None or exit_date > cap_date):
                    exit_date, exit_reason = cap_date, 'Batas waktu sebelum payment date; hak dividen tetap disimpan'
        elif request.exit_rule == 'holding_period':
            if ex_idx + request.max_holding_sessions < len(dates) and dates[ex_idx + request.max_holding_sessions] <= end:
                exit_date, exit_reason = dates[ex_idx + request.max_holding_sessions], 'Batas sesi pengamatan'
        else:
            # A close-based signal may only be executed at the next available open.
            # The signal at the terminal date cannot create a trade beyond the run.
            for k in range(ex_idx, last_idx + 1):
                if dates[k] > limit:
                    break
                if D(bars[dates[k]]['close']) >= D(bars[entry]['close']):
                    signal_date = dates[k]
                    if k + 1 < len(dates) and dates[k + 1] <= limit:
                        exit_date, price_field = dates[k + 1], 'open'
                        exit_reason = 'Open sesi setelah sinyal BEP harga'
                    break
            if exit_date is None and ex_idx + request.max_holding_sessions < len(dates) and dates[ex_idx + request.max_holding_sessions] <= end:
                exit_date, price_field, exit_reason = dates[ex_idx + request.max_holding_sessions], 'close', 'Batas waktu; BEP tidak menjamin fill'
        if exit_date and exit_date > end:
            exit_date = None
        plans.append({'event': event, 'entry_date': entry, 'entry_price': D(bars[entry]['close']),
                      'exit_date': exit_date, 'exit_field': price_field, 'exit_reason': exit_reason,
                      'signal_date': signal_date, 'shares': 0, 'status': 'waiting',
                      'dividend': Decimal(0), 'realized_pnl': Decimal(0), 'last_price': D(bars[entry]['close']),
                      'settlement_date': None})
    start = request.start_date.isoformat() if request.start_date else min(p['entry_date'] for p in plans)
    if start > end or (unified and start < dataset.replay_start):
        raise ValueError('Awal periode tidak valid.')
    sessions = [d for d in dataset.market_sessions if start <= d <= end]
    # Calendar dates for payments are processed even if not a price session.
    days = set(sessions + [start, end])
    dividend_calendar = list(dataset.events.values()) if unified else [p['event'] for p in plans]
    days.update(e['payment_date'] for e in dividend_calendar if e.get('payment_date') and start <= e['payment_date'] <= end)
    cash = request.capital
    sale_receivables = []
    dividends = []
    ledger, curve = [], []
    capital = request.capital
    peak = capital
    max_drawdown = Decimal(0)

    def log(day, kind, symbol, amount, detail):
        ledger.append({'date': day, 'kind': kind, 'symbol': symbol, 'amount': number(amount), 'detail': detail})

    def sell(plan, day):
        nonlocal cash
        shares = plan['shares']
        price = D(dataset.prices[plan['event']['symbol']][day][plan['exit_field']])
        proceeds = price * shares
        plan['realized_pnl'] = (price - plan['entry_price']) * shares
        plan['exit_price'] = price
        plan['status'] = 'sold'
        i = bisect_right(dataset.market_sessions, day)
        settlement = dataset.market_sessions[i + 1] if i + 1 < len(dataset.market_sessions) else None
        plan['settlement_date'] = settlement
        sale_receivables.append({'date': settlement, 'amount': proceeds, 'symbol': plan['event']['symbol']})
        log(day, 'sell', plan['event']['symbol'], proceeds, f"{shares:,} saham × Rp{price}; {plan['exit_reason']}")

    for day in sorted(days):
        for receivable in sale_receivables[:]:
            if receivable['date'] is not None and receivable['date'] <= day:
                cash += receivable['amount']
                log(day, 'settlement', receivable['symbol'], receivable['amount'], 'Hasil jual menjadi kas tersedia (T+2 sesi dataset)')
                sale_receivables.remove(receivable)
        for e in dividend_calendar:
            if day != e['ex_date']:
                continue
            for plan in plans:
                if plan['status'] == 'holding' and plan['event']['symbol'] == e['symbol']:
                    amount = D(e['dps']) * plan['shares']
                    plan['dividend'] += amount
                    dividends.append({'date': e['payment_date'], 'amount': amount, 'symbol': e['symbol']})
                    log(day, 'entitlement', e['symbol'], amount, f"Hak dividen {e['id']} untuk lot {plan['event']['id']}; belum menjadi kas")
        for dividend in dividends[:]:
            if dividend['date'] and dividend['date'] <= day:
                cash += dividend['amount']
                log(day, 'dividend', dividend['symbol'], dividend['amount'], 'Dividen berpindah dari piutang ke kas')
                dividends.remove(dividend)
        for plan in plans:
            if plan['status'] == 'holding' and plan['exit_date'] == day and plan['exit_field'] == 'open':
                sell(plan, day)
        for plan in plans:
            if plan['entry_date'] == day:
                budget = capital / len(plans) if allocation == 'equal' else cash
                budget = min(budget, cash)
                lot_cost = plan['entry_price'] * 100
                shares = int((budget / lot_cost).to_integral_value(rounding=ROUND_FLOOR)) * 100
                if shares == 0:
                    plan['status'] = 'skipped'
                    plan['exit_reason'] = 'Kas tersedia tidak cukup untuk satu lot pada tanggal masuk'
                    log(day, 'skipped', plan['event']['symbol'], 0, plan['exit_reason'])
                else:
                    plan['shares'], plan['status'] = shares, 'holding'
                    amount = shares * plan['entry_price']
                    cash -= amount
                    log(day, 'buy', plan['event']['symbol'], -amount, f'{shares:,} saham pada close sesi masuk')
        for plan in plans:
            if plan['status'] == 'holding':
                bar = dataset.prices[plan['event']['symbol']].get(day)
                if bar:
                    plan['last_price'] = D(bar['close'])
                if plan['exit_date'] == day and plan['exit_field'] == 'close':
                    sell(plan, day)
        position_value = sum((p['shares'] * p['last_price'] for p in plans if p['status'] == 'holding'), Decimal(0))
        pending_sale = sum((r['amount'] for r in sale_receivables), Decimal(0))
        pending_dividend = sum((r['amount'] for r in dividends), Decimal(0))
        nav = cash + position_value + pending_sale + pending_dividend
        peak = max(peak, nav)
        max_drawdown = min(max_drawdown, nav / peak - 1)
        assert cash >= 0, 'Conservation error: negative cash'
        curve.append({'date': day, 'nav': number(nav), 'cash': number(cash), 'positions': number(position_value),
                      'sale_receivable': number(pending_sale), 'dividend_receivable': number(pending_dividend)})
    final = curve[-1]
    results = []
    for p in plans:
        e = p['event']
        exit_price = p.get('exit_price')
        unrealized = (p['last_price'] - p['entry_price']) * p['shares'] if p['status'] == 'holding' else Decimal(0)
        results.append({'event_id': e['id'], 'symbol': e['symbol'], 'status': p['status'], 'shares': p['shares'],
                        'entry_date': p['entry_date'], 'entry_price': number(p['entry_price']),
                        'exit_date': p['exit_date'] if p['status'] == 'sold' else None,
                        'exit_price': number(exit_price) if exit_price is not None else None,
                        'settlement_date': p['settlement_date'], 'payment_date': e['payment_date'],
                        'dividend': number(p['dividend']), 'capital_pnl': number(p['realized_pnl'] + unrealized),
                        'gross_pnl': number(p['realized_pnl'] + unrealized + p['dividend']),
                        'reason': p['exit_reason'], 'signal_date': p['signal_date'],
                        'capital_days': (date.fromisoformat(min(p['settlement_date'], end) if p['status'] == 'sold' and p['settlement_date'] else end) - date.fromisoformat(p['entry_date'])).days if p['shares'] else 0})
    return {'allocation': allocation, 'capital': number(capital), 'end_date': end, 'start_date': start,
            'ending_nav': final['nav'], 'ending_cash': final['cash'], 'remaining_positions': final['positions'],
            'pending_sales': final['sale_receivable'], 'pending_dividends': final['dividend_receivable'],
            # Compute returns before presentation rounding; an idle fractional
            # balance must never create a gain or loss just from formatting.
            'gross_pnl': number(nav - capital), 'return_pct': number((nav / capital - 1) * 100),
            'dividends': number(sum((p['dividend'] for p in plans), Decimal(0))),
            'max_drawdown_pct': number(max_drawdown * 100), 'trades': results, 'ledger': ledger, 'curve': curve,
            'open_below_entry': sum(p['status'] == 'holding' and p['last_price'] < p['entry_price'] for p in plans),
            'method': 'historical_replay', 'rules_version': 'replay-v2.1' if unified else 'replay-v1.2', 'model_version': None,
            'dataset_version': getattr(dataset, 'version', 'synthetic-test-fixture'),
            'assumptions': ['Harga aktual Sectors; replay bersyarat pada kalender yang tersedia sekarang.',
                            'Di luar biaya transaksi, pajak, dan slippage.',
                            ('Beberapa event/lot per emiten; split anggaran per event; lot 100, tanpa margin. T+2 sesi IHSG dan konsensus sembilan feed emiten; kalender resmi belum diverifikasi.' if unified else 'Satu event per emiten; lot 100 saham; tanpa margin. Hasil jual tersedia setelah T+2 sesi dataset.'),
                            'Entry dan exit terjadwal memakai close. Sinyal BEP dieksekusi pada open sesi berikutnya; hasilnya bisa di bawah BEP.',
                            'Posisi yang belum keluar pada tanggal akhir tetap dinilai dengan harga terakhir yang tersedia.',
                            'Urutan saham mengikuti tanggal masuk; saham pertama adalah baseline all-in. Ini bukan optimasi rute global.']}


def compare(dataset, request):
    primary = simulate(dataset, request)
    alternatives = [simulate(dataset, request, mode) for mode in ['single', 'equal', 'rotation']] if request.compare else [primary]
    return {'primary': primary, 'alternatives': alternatives, 'input': request.model_dump(mode='json')}
