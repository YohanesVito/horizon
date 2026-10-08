"""Read-only smoke check of the public editorial flow through the Next.js proxy."""

from datetime import datetime, timezone
from pathlib import Path
import json
import sys

import httpx


ROOT = Path(__file__).resolve().parents[1]
BASE = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'https://horizon-dividend.vercel.app'
EXPECTED = ['DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS']


def main():
    if not BASE.startswith('https://'):
        raise ValueError('Live verification requires HTTPS')
    report = {'base_url': BASE, 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'in_progress', 'checks': {}}
    with httpx.Client(base_url=BASE, timeout=35, follow_redirects=False) as client:
        def get(path):
            response = client.get(path)
            if response.status_code != 200:
                raise AssertionError(f'{path} returned HTTP {response.status_code}')
            return response.json()

        health = get('/api/health')
        assert health['status'] == 'ok' and health['storage'] == 'postgresql'
        report['checks']['health'] = {'status': 'ok', 'storage': health['storage']}

        candidates = get('/api/dividend-candidates')
        symbols = [row['symbol'] for row in candidates['candidates']]
        assert symbols == EXPECTED, f'Unexpected candidate symbols: {symbols}'
        report['checks']['candidates'] = {'year': candidates['year'], 'symbols': symbols,
                                          'universe_count': candidates['universe_count']}

        catalog = get('/api/timeline')
        assert set(catalog['preview_symbols']) == set(EXPECTED)
        assert 'Periode dengan harga tersedia' in catalog['reason']
        report['checks']['timeline_catalog'] = {
            'preview_symbols': catalog['preview_symbols'],
            'verified_symbols': [row['symbol'] for row in catalog['companies']],
        }

        report['checks']['previews'] = {}
        for symbol in symbols:
            detail = get(f'/api/timeline/{symbol}?preview=true')
            history = detail['history']
            assert detail['symbol'] == symbol and detail['preview'] and history
            assert all(period['points'] and period['sources'] for period in history)
            assert detail['forecast']['status'] == 'not_available'
            report['checks']['previews'][symbol] = {
                'events': len(history),
                'years': sorted({period['year'] for period in history}),
                'forecast_status': detail['forecast']['status'],
            }

        intelligence = get('/api/intelligence')
        lppf = next((row for row in intelligence['companies'] if row['symbol'] == 'LPPF'), None)
        assert lppf and lppf['complete_events'] > 0 and lppf['trap_pct'] is not None
        report['checks']['historical_risk'] = {
            'symbol': 'LPPF', 'complete_events': lppf['complete_events'],
            'trap_pct': lppf['trap_pct'], 'evidence_status': lppf['evidence_status'],
        }

    report['status'] = 'passed'
    path = ROOT / 'outputs/deployment/live-editorial-verification.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
