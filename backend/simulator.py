"""Independent historical observations, full starting capital for each event.

No order execution, sale, cash rotation, or summation of independent scenarios.
"""
from decimal import Decimal, ROUND_FLOOR
from math import isfinite
from .domain import SimulationRequest
from .observation import observe_holding

D = lambda value: Decimal(str(value))


def number(value):
    return round(float(value), 4)


# Inactive equal-allocation implementation retained at PM's request.
# def equal_budget(capital, selected_event_count, available_cash):
#     """Former replay divided the original capital per event, bounded by cash."""
#     return min(capital / selected_event_count, available_cash)


def simulate(dataset, request: SimulationRequest, allocation=None):
    if allocation not in (None, 'single') or request.allocation != 'single':
        raise ValueError('Strategi bagi rata dan rotasi tidak tersedia.')
    if request.timing_mode != 'payment_plus_2':
        raise ValueError('Analisis memakai rata-rata lima close sebelum cum dan payment + 2 hari bursa.')
    capital = request.capital
    sessions = sorted(dataset.market_sessions)
    trades = []
    for event_id in request.event_ids:
        event = dataset.events.get(event_id)
        if not event:
            raise ValueError('Event tidak dikenal: ' + event_id)
        bars = dataset.prices.get(event['symbol'], {})
        cum = event['cum_date']
        reference_dates = []
        reason = None
        if cum in sessions:
            index = sessions.index(cum)
            reference_dates = sessions[max(0, index - 5):index]
        reference = [bars.get(day, {}).get('close') for day in reference_dates]
        if len(reference) != 5 or any(type(v) not in (int, float) or not isfinite(v) or v <= 0 for v in reference):
            reason = 'Lima harga close sesi pasar sebelum cum belum lengkap; peristiwa belum dapat dianalisis.'
        elif not event.get('payment_date'):
            reason = 'Payment date belum tersedia; peristiwa belum dapat dianalisis.'
        elif not event.get('replay_available', True):
            reason = 'Data event belum tervalidasi: ' + '; '.join(event.get('reasons', []))
        entry_price = sum((D(v) for v in reference), Decimal(0)) / 5 if not reason else None
        shares = int((capital / (entry_price * 100)).to_integral_value(rounding=ROUND_FLOOR)) * 100 if entry_price else 0
        invested = entry_price * shares if entry_price else Decimal(0)
        cash = capital - invested
        observation = observe_holding(dataset, event, shares, entry_price or 0)
        if reason:
            observation['complete'] = False
            observation['gaps'].insert(0, reason)
        point = observation['points'][-1] if observation['points'] and not reason else None
        valuation = None
        if point:
            position = D(point['close']) * shares
            entitled = D(point['dividend_entitled'])
            total = cash + position + entitled
            pnl = total - capital
            valuation = {'date': point['date'], 'position_value': number(position),
                         'dividend_entitled': number(entitled), 'dividend_paid': point['dividend_paid'],
                         'residual_cash': number(cash), 'total_value': number(total),
                         'pnl': number(pnl), 'return_pct': number(pnl / capital * 100)}
        status = 'unavailable' if reason or not point else ('observed' if observation['complete'] else 'partial')
        trades.append({'event_id': event_id, 'symbol': event['symbol'], 'status': status, 'shares': shares,
                       'entry_date': cum, 'entry_price': number(entry_price) if entry_price else None,
                       'entry_price_basis': 'prior5_close_mean', 'entry_reference_dates': reference_dates,
                       'entry_booking': 'synthetic_cum_reference', 'starting_capital': number(capital),
                       'residual_cash': number(cash), 'end_valuation': valuation, 'observation': observation,
                       'exit_date': None, 'exit_price': None, 'settlement_date': None,
                       'payment_date': event.get('payment_date'), 'dividend': observation['dividend_amount'],
                       'capital_pnl': number(D(point['close']) * shares - invested) if point else None,
                       'gross_pnl': valuation['pnl'] if valuation else None,
                       'reason': reason or ('Periode lengkap' if observation['complete'] else 'Periode teramati belum lengkap'),
                       'signal_date': None, 'capital_days': None})
    if all(t['status'] == 'unavailable' for t in trades):
        raise ValueError('Tidak ada peristiwa yang dapat dianalisis: ' + '; '.join(t['reason'] for t in trades))
    starts = [t['entry_date'] for t in trades]
    ends = [t['observation']['available_end_date'] for t in trades if t['observation']['available_end_date']]
    return {'analysis_mode': 'independent_events', 'allocation': 'single', 'capital': number(capital),
            'start_date': min(starts), 'end_date': max(ends) if ends else min(starts),
            # These historical transport fields stay null: independent observations
            # cannot be added into one portfolio or presented as strategy NAV.
            'ending_nav': None, 'ending_cash': None, 'remaining_positions': None,
            'pending_sales': None, 'pending_dividends': None, 'gross_pnl': None,
            'return_pct': None, 'dividends': None, 'max_drawdown_pct': None,
            'trades': trades, 'ledger': [], 'curve': [], 'open_below_entry': None,
            'method': 'independent_historical_observation', 'rules_version': 'observation-v1',
            'model_version': None, 'dataset_version': getattr(dataset, 'version', 'synthetic-test-fixture'),
            'assumptions': ['Setiap peristiwa dianalisis independen dengan modal awal penuh yang sama; hasil tidak dijumlahkan. Pembulatan lot menyisakan kas.',
                            'Harga masuk referensi: rata-rata aritmetika lima close sesi pasar sebelum cum, tanpa cum. Bukan harga eksekusi satu transaksi atau DCA.',
                            'Pencatatan referensi pada cum; observasi sampai dua hari bursa setelah payment. Tidak ada transaksi jual otomatis.',
                            'Rentang nilai posisi menggunakan high/low historis ditambah dividen peristiwa terpilih dengan asumsi hak dividen diperoleh; bukan kas cair atau laba eksekusi yang dijamin.',
                            'Nilai akhir per peristiwa memakai close terakhir teramati, sisa kas, dan hak dividen yang telah timbul.',
                            'Di luar biaya transaksi, pajak, dan slippage.']}


def compare(dataset, request):
    primary = simulate(dataset, request)
    inputs = request.model_dump(mode='json')
    inputs.update(start_date=primary['start_date'], end_date=primary['end_date'], entry_sessions_before_cum=0,
                  entry_price_basis='prior5_close_mean')
    return {'primary': primary, 'alternatives': [], 'input': inputs}
