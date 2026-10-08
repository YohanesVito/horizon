"""User-supplied ex-date scenario; this is arithmetic, not a price forecast."""

from decimal import Decimal, ROUND_FLOOR

from pydantic import BaseModel, Field


class ExDateScenarioInput(BaseModel):
    capital_idr: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    entry_price: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    dps: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    assumed_ex_price: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


def calculate_ex_date_scenario(body: ExDateScenarioInput):
    lot_cost = body.entry_price * 100
    lots = int((body.capital_idr / lot_cost).to_integral_value(rounding=ROUND_FLOOR))
    if lots < 1:
        raise ValueError('Modal belum cukup untuk satu lot (100 saham) pada harga beli ini.')
    shares = lots * 100
    invested = body.entry_price * shares
    remaining_cash = body.capital_idr - invested
    capital_change = (body.assumed_ex_price - body.entry_price) * shares
    dividend = body.dps * shares
    gross_pnl = capital_change + dividend
    total_bep = body.entry_price - body.dps

    def amount(value):
        return float(value.quantize(Decimal('0.01')))

    return {
        'status': 'scenario',
        'basis': 'Input pengguna; diasumsikan saham dibeli sebelum cum-date, berhak atas dividen, dan dijual pada harga ex-date asumsi.',
        'input': body.model_dump(mode='json'),
        'lots': lots, 'shares': shares,
        'invested_idr': amount(invested),
        'remaining_cash_idr': amount(remaining_cash),
        'capital_pnl_idr': amount(capital_change),
        'dividend_idr': amount(dividend),
        'gross_pnl_idr': amount(gross_pnl),
        'gross_return_pct': amount(gross_pnl / invested * 100),
        'price_bep_idr': amount(body.entry_price),
        'total_bep_idr': amount(total_bep),
        'total_bep_reached': body.assumed_ex_price >= total_bep,
        'label': 'Skenario, bukan prediksi. Persentase terhadap modal terpakai; hasil gross di luar biaya transaksi, pajak, dan slippage. Dividen dapat dibayarkan setelah ex-date.',
    }
