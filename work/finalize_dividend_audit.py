"""Refresh the data audit from saved research envelopes; no network or credentials."""
from pathlib import Path
import json
import hashlib
import re
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/dividend-research'
audit_path = ROOT / 'outputs/sectors-data-audit.json'
audit = json.loads(audit_path.read_text())
study = json.loads((OUT / 'study-results.json').read_text())
now = datetime.now(ZoneInfo('Asia/Makassar')).isoformat()
audit.setdefault('prior_audits', []).append({
    'audited_at': audit.get('audited_at'),
    'status': audit['status'],
    'integration_access_method': audit['integration']['access_method'],
    'sample_coverage': audit['sample_coverage'],
}) if audit.get('status') != 'expanded_calendar_and_BBCA_research_complete' else None
audit['status'] = 'expanded_calendar_and_BBCA_research_complete'
audit['audited_at'] = now
audit['integration']['access_method'] = 'MCP Streamable HTTP plus official Sectors REST calendar; calendar endpoint absent from inspected 66-tool registry'
audit['integration']['authenticated_data_calls_succeeded_initial_audit'] = audit['integration'].pop('authenticated_data_calls_succeeded', 6)
raw = []
for p in sorted(OUT.glob('*.json')):
    data = json.loads(p.read_text())
    if 'transport' in data:
        raw.append((p, data))
audit['integration']['saved_expanded_audit_responses'] = len(raw)
audit['documentation'] = sorted(set(audit['documentation'] + [
    'https://docs.sectors.app/api-references',
    'https://docs.sectors.app/api-references/v2/indonesia/news/corporate-actions',
    'https://docs.sectors.app/api-references/v2/indonesia/screener/companies',
]))
for need in audit['requirements']:
    if need['need'].startswith('Kalender'):
        need['verification'] = 'cum_ex_recording_payment_verified_via_REST_calendar; declaration_unverified; upcoming_revision_conflict'
        need['documented_candidate_tools'].append('REST GET /v2/corporate-actions/') if 'REST GET /v2/corporate-actions/' not in need['documented_candidate_tools'] else None
        need['observed'] = '43 dividend rows in March–April 2025; all 8 BBCA 2022–2025 events have cum/ex/recording/payment. October–November 2026 query has 8 upcoming rows, including past ex-dates and UNTR/ASGR schedules requiring revision verification. Declaration timestamp remains absent in sampled calendars; BBCA news query returned empty.'
        need['open_questions'] = ['Declaration timestamp and when information first became public', 'Market type of cum/ex fields', 'Schedule revision history and cancellation/postponement propagation']
    elif need['need'].startswith('Harga'):
        need['verification'] = 'historical_OHLCV_verified_on_8_BBCA_event_windows'
        need['observed'] = '8 windows around 2022–2025 BBCA events; unique dates, OHLC ordering, positive volume, 10 pre-ex and 20 post-ex session offsets checked. Exchange-session completeness still needs an independent calendar.'
    elif need['need'].startswith('Benchmark'):
        need['verification'] = 'IHSG_price_data_verified_on_8_event_windows_with_3_missing_dates'
        need['observed'] = study['missing_benchmark_dates']
audit['modeling_assumptions_current'] = {
    'fees': 0, 'taxes': 0, 'slippage': 0,
    'label': 'Gross; before transaction fees, taxes and slippage, per latest PM instruction',
    'recovery_reference': 'User purchase price; pilot uses cum close',
    'observation_window': 'Ex t=0 through t=20 inclusive; 21 closes',
    'production_prediction_ready': False,
}
audit['sample_coverage']['expanded_research'] = {
    'BBCA_events': 8, 'event_years': [2022, 2023, 2024, 2025],
    'annual_yield_top5': ['DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS'],
    'calendar_upcoming_rows': 8, 'calendar_March_April_2025_dividend_rows': 43,
    'declaration_date_available': False,
}
issue_id = 'upcoming-calendar-postponement'
audit['quality_findings'] = [i for i in audit['quality_findings'] if i['id'] != issue_id]
audit['quality_findings'].append({
    'id': issue_id, 'severity': 'quarantine_affected_events_pending_Sectors_confirmation',
    'symbols': ['UNTR', 'ASGR'],
    'observed': 'Sectors calendar snapshot 2026-10-06 01:01 Asia/Makassar still reports payment 2026-10-26. Sectors news for 2026-10-01..05 returns 18 articles, including UNTR schedule change and ASGR conversion canceling the old schedule. KSEI letters dated 2026-10-02 separately postpone these payments until further notice.',
    'Sectors_evidence': ['outputs/dividend-research/calendar-upcoming.json', 'outputs/dividend-research/untr-asgr-news-2026-october-corrected.json', 'outputs/dividend-research/schedule-conflict-evidence.json'],
    'source_boundary': 'KSEI used to detect a quality conflict, not replace financial model inputs; Sectors remains the required data provider.',
    'external_evidence': [
        'https://web.ksei.co.id/Announcement/Files/200234_ksei_24911_jku_1026_202610021447.pdf',
        'https://web.ksei.co.id/Announcement/Files/200235_ksei_24908_jku_1026_202610021447.pdf',
    ],
})
audit['next_step'] = 'Resolve calendar revisions, declaration and financial publication timestamps, market type and adjustment/unit definitions; then broaden chronological strategy tests. Discovery and explicit-assumption simulation can precede calibrated forecasting.'
audit['raw_evidence_files'] = sorted(set(audit['raw_evidence_files'] + [str(p.relative_to(ROOT)) for p, _ in raw]))
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')

sources = [
    {'role': 'announcement research', 'url': 'https://ersj.eu/journal/1460', 'access': 'publisher abstract'},
    {'role': 'announcement research', 'url': 'https://link.springer.com/article/10.1007/s43546-021-00198-8', 'access': 'publisher abstract'},
    {'role': 'settlement rules', 'url': 'https://web.ksei.co.id/services/types/transaction-settlement'},
    {'role': 'cum/ex market-specific schedule semantics only', 'url': 'https://web.ksei.co.id/Announcement/Files/HRTA_DIV_20260615_ID.pdf'},
    {'role': 'market mechanics', 'url': 'https://sikapiuangmu.ojk.go.id/FrontEnd/images/FileDownload/560_Buku%20Saku%20Pasar%20Modal_compressed.pdf'},
    *[{'role': 'quality conflict only; not simulation feed', 'url': url} for url in audit['quality_findings'][-1]['external_evidence']],
]
manifest = {
    'created_at': now, 'financial_data_source': 'Sectors',
    'external_research_and_rules': sources,
    'files': [
        {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'retrieved_at': d.get('retrieved_at'), 'tool_or_url': d.get('tool', d.get('url')), 'isError': d.get('result', {}).get('isError', False)}
        for p, d in raw
    ],
}
(OUT / 'evidence-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
architecture = (OUT / 'arsitektur-sistem.md').read_text()
diagrams = re.findall(r'```mermaid\n(.*?)\n```', architecture, re.S)
for name, content in zip(['arsitektur-data.mmd', 'siklus-modal.mmd'], diagrams):
    (OUT / name).write_text(content + '\n')
print(json.dumps({'raw_response_files': len(raw), 'mermaid_diagrams': len(diagrams), 'audit_updated': str(audit_path)}, ensure_ascii=False))
