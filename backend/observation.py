"""Historical hypothetical holding window; independent of executed replay trades."""
from decimal import Decimal
from math import isfinite


def observe_holding(dataset, event, shares, entry_price):
    sessions = sorted(dataset.market_sessions)
    payment = event.get('payment_date')
    after = [d for d in sessions if payment and d > payment]
    end = after[1] if len(after) >= 2 else None
    gaps = []
    if not payment:
        gaps.append('Payment date belum tersedia.')
    elif end is None:
        gaps.append('Dua hari bursa setelah payment belum tercakup dataset.')
    bars = dataset.prices.get(event['symbol'], {})
    available_end = end or (sessions[-1] if sessions else None)
    expected = [d for d in sessions if event['cum_date'] <= d <= (available_end or event['cum_date'])]
    invested = Decimal(str(entry_price)) * shares
    dividend = Decimal(str(event['dps'])) * shares
    num = lambda v: round(float(v), 4)
    points = []
    for day in expected:
        bar = bars.get(day, {})
        values = [bar.get(k) for k in ('open', 'high', 'low', 'close')]
        valid = (all(type(v) in (int, float) and isfinite(v) and v > 0 for v in values)
                 and bar['low'] <= min(bar['open'], bar['close']) <= max(bar['open'], bar['close']) <= bar['high'])
        if not valid:
            gaps.append(f'OHLC tidak tersedia/valid pada {day}.')
            continue
        entitled = dividend if day >= event['ex_date'] else Decimal(0)
        paid = dividend if payment and day >= payment else Decimal(0)
        value = Decimal(str(bar['close'])) * shares
        points.append({**{k: bar[k] for k in ('open', 'high', 'low', 'close')}, 'date': day,
                       'dividend_entitled': num(entitled), 'dividend_paid': num(paid),
                       'position_value': num(value), 'total_value': num(value + entitled)})
    if not expected or expected[0] != event['cum_date']:
        gaps.append('Hari bursa cum-date belum tercakup dataset.')
    def extreme(field, choose):
        if not points or not shares:
            return None
        point = choose(points, key=lambda p: p[field])
        value = Decimal(str(point[field])) * shares
        total = value + dividend
        pnl = total - invested
        return {'date': point['date'], 'price': point[field], 'position_value': num(value),
                'total_value': num(total), 'pnl': num(pnl),
                'return_pct': num(pnl / invested * 100) if invested else 0}
    return {'cum_date': event['cum_date'], 'ex_date': event['ex_date'], 'payment_date': payment,
            'end_date': end, 'available_end_date': points[-1]['date'] if points else None,
            'horizon_sessions': 2, 'complete': bool(end and points and not gaps), 'gaps': gaps,
            'invested': num(invested), 'shares': shares, 'dividend_amount': num(dividend),
            'dividend_per_share': num(event['dps']), 'points': points,
            'highest': extreme('high', max), 'lowest': extreme('low', min)}
