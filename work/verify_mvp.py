"""Read-only Sectors replay matrix. Does not call a provider or write user history.

Run from the workspace with .venv/bin/python work/verify_mvp.py.
This checks accounting, not profitability or predictive validity.
"""
import json
import math
import sys
from datetime import date, datetime, timezone
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.domain import SimulationRequest
from backend.intelligence import IntelligenceDataset
from backend.simulator import simulate
from backend.unified import UnifiedDataset


def verify():
    data = UnifiedDataset(IntelligenceDataset())
    bundles = [[e] for e in data.events] + [
        ['BBCA:2025-03-21', 'BBRI:2025-04-11', 'LPPF:2025-04-22', 'DMAS:2025-05-08', 'RALS:2025-05-22'],
        ['BBCA:2025-03-21', 'BBCA:2025-12-03', 'BBRI:2025-12-30', 'ADRO:2025-12-30'],
        ['ADRO:2025-06-13', 'ADRO:2025-12-30'],
    ]
    failures, count, methods = [], 0, set()
    for ids, offset, exit_rule, horizon, allocation in product(
        bundles, [0, 5, 10], ['ex_close', 'payment_close', 'price_bep', 'holding_period'],
        [1, 20, 60], ['single', 'equal', 'rotation'],
    ):
        body = SimulationRequest(event_ids=ids, entry_sessions_before_cum=offset,
                                 exit_rule=exit_rule, max_holding_sessions=horizon, allocation=allocation,
                                 start_date=date(2025, 1, 1), end_date=date(2025, 12, 31))
        count += 1
        try:
            result = simulate(data, body)
            methods.add(result['rules_version'])
            expected_pnl = 0
            for trade in result['trades']:
                # Independent event-date oracle: all entitlements while holding,
                # regardless of which event originally opened the lot.
                expected_dividend = sum(
                    event['dps'] * trade['shares'] for event in data.events.values()
                    if event['symbol'] == trade['symbol']
                    and trade['entry_date'] < event['ex_date'] <= result['end_date']
                    and (not trade['exit_date'] or event['ex_date'] <= trade['exit_date'])
                )
                assert abs(expected_dividend - trade['dividend']) < .01, 'Hak dividen tidak cocok dengan tanggal kepemilikan'
                expected_pnl += expected_dividend + trade['capital_pnl']
                assert trade['shares'] % 100 == 0, 'Jumlah saham bukan kelipatan lot'
                if trade['exit_date']:
                    assert trade['entry_date'] < trade['exit_date'] <= result['end_date']
                    if trade['settlement_date']:
                        assert trade['settlement_date'] > trade['exit_date']
            assert abs(expected_pnl - result['gross_pnl']) < .01, 'PnL tidak cocok dengan lot dan hak dividen'
            for point in result['curve']:
                amounts = [point[k] for k in ['cash', 'nav', 'positions', 'sale_receivable', 'dividend_receivable']]
                assert all(math.isfinite(x) and x >= 0 for x in amounts), 'Nilai tidak finite atau negatif'
                assert abs(point['nav'] - sum(point[k] for k in ['cash', 'positions', 'sale_receivable', 'dividend_receivable'])) < .01, 'NAV tidak seimbang'
            assert (result['curve'][0]['date'], result['curve'][-1]['date']) == ('2025-01-01', '2025-12-31')
        except Exception as error:
            failures.append({'input': body.model_dump(mode='json'), 'error': repr(error)})
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'dataset_version': data.version,
              'engine_versions': sorted(methods), 'runs': count, 'failures': failures,
              'dimensions': {'event_bundles': len(bundles), 'entry_offsets': [0, 5, 10], 'holding_limits': [1, 20, 60], 'exit_rules': 4, 'allocations': 3},
              'checks': ['entitlement from dates held', 'gross PnL equals lot gains plus dividends', '100-share lots', 'entry/exit/settlement order', 'finite nonnegative balances', 'NAV conservation', 'common period'],
              'limits': ['Accounting checks only; not out-of-sample strategy validation.', 'Official calendar, declaration timestamps and fees remain documented gaps.']}
    path = ROOT / 'outputs/development/mvp-readiness.json'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({'runs': count, 'failures': len(failures), 'report': str(path)}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(verify())
