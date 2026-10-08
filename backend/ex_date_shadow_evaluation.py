"""Private, descriptive evaluation of frozen ex-date shadow observations."""

from datetime import date, datetime
from decimal import Decimal
from statistics import median

from .ex_date_shadow import MARKET_TZ


def evaluate_cohort(forecasts, outcomes, *, now=None):
    """Compare the pre-cum full-DPS baseline with a flat last-close comparator.

    No release decision or probability is inferred from these descriptive metrics.
    """
    observed_at = now or datetime.now(MARKET_TZ)
    if observed_at.tzinfo is None:
        raise ValueError('Waktu evaluasi harus timezone-aware.')
    today = observed_at.astimezone(MARKET_TZ).date()
    by_id = {row['id']: row for row in forecasts}
    if len(by_id) != len(forecasts):
        raise ValueError('Forecast ID kohort harus unik.')
    outcome_by_id = {row['forecast_id']: row for row in outcomes}
    if len(outcome_by_id) != len(outcomes) or not set(outcome_by_id) <= set(by_id):
        raise ValueError('Outcome duplikat atau tidak cocok dengan kohort.')

    observed, pending = [], []
    for forecast in sorted(forecasts, key=lambda row: (row['ex_date'], row['symbol'])):
        outcome = outcome_by_id.get(forecast['id'])
        if outcome is None:
            pending.append({'symbol': forecast['symbol'], 'ex_date': forecast['ex_date'],
                            'scorable_after': forecast['ex_date'],
                            'state': 'awaiting_ex_date' if today <= date.fromisoformat(forecast['ex_date'])
                            else 'awaiting_price_snapshot_or_audit'})
            continue
        last = Decimal(forecast['last_close'])
        predicted = Decimal(forecast['baseline_ex_close'])
        actual = Decimal(outcome['actual_ex_close'])
        if last <= 0 or actual <= 0 or predicted <= 0:
            raise ValueError('Harga evaluasi harus positif.')
        model_error = abs(predicted - actual) / last * 100
        flat_error = abs(last - actual) / last * 100
        if Decimal(outcome['absolute_error_pct_of_last_close']) != model_error:
            raise ValueError('Galat outcome tidak cocok dengan forecast yang dibekukan.')
        observed.append({'symbol': forecast['symbol'], 'ex_date': forecast['ex_date'],
                         'actual_ex_close': str(actual), 'model_error_pct': str(model_error),
                         'flat_error_pct': str(flat_error),
                         'model_better_than_flat': model_error < flat_error})

    summary = None
    if observed:
        model = [Decimal(row['model_error_pct']) for row in observed]
        flat = [Decimal(row['flat_error_pct']) for row in observed]
        summary = {'n': len(observed),
                   'model_mae_pct': str(sum(model) / len(model)),
                   'flat_mae_pct': str(sum(flat) / len(flat)),
                   'model_median_error_pct': str(median(model)),
                   'model_wins_ties_losses_vs_flat': [
                       sum(a < b for a, b in zip(model, flat)),
                       sum(a == b for a, b in zip(model, flat)),
                       sum(a > b for a, b in zip(model, flat))]}
    return {'status': 'research_only', 'target': 'ex_date_close_from_pre_cum_last_close',
            'forecast_count': len(forecasts), 'observed': observed, 'pending': pending,
            'summary': summary, 'performance_claim_allowed': False,
            'limitations': ['Sampel terpilih; bukan bukti akurasi umum.',
                            'Basis harga Sectors, revisi notice dan sumber close independen belum diaudit.',
                            'Metrik deskriptif tidak sama dengan probabilitas atau hasil trading neto.']}
