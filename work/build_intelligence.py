"""Reproducible export of the frozen baseline; never fetches or edits raw data."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.intelligence import IntelligenceDataset

analysis = IntelligenceDataset().analyze(5, 20)
out = ROOT / 'outputs/intelligence'
(out / 'baseline-analysis.json').write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + '\n')
fields = ['id', 'symbol', 'ex_date', 'cum_date', 'payment_date', 'dps', 'eligible', 'entry_date', 'entry_price', 'complete',
          'observed_sessions', 'gross_return_pct', 'price_bep_session', 'total_bep_session', 'reasons', 'sources']
with (out / 'event-audit.csv').open('w') as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for company in analysis['companies']:
        writer.writerows(company['events'])
print(json.dumps({'audit': analysis['audit'], 'version': analysis['dataset_version'], 'sources': len(analysis['sources'])}))
