"""Pre-commit routes from past evidence, then replay without selecting hindsight winners."""
from copy import deepcopy
from .domain import RotationRequest, SimulationRequest
from .intelligence import rank
from .simulator import compare

VERSION = 'rotation-planner-v1.0'


def plan_routes(dataset, request: RotationRequest):
    start, end = request.start_date.isoformat(), request.end_date.isoformat()
    unknown = set(request.symbols)-set(dataset.companies)
    if unknown:
        raise ValueError('Emiten di luar universe riset: '+', '.join(sorted(unknown)))
    evidence = dataset.intelligence.analyze(request.rules.entry_offset, request.rules.horizon, as_of=start)
    ranking = rank(evidence, request.rules)
    stats = {r['symbol']: r for r in [*ranking['ranked'], *ranking['excluded']]}
    blocked = {r['symbol']: r['reasons'] for r in ranking['excluded']}
    source_evidence = {c['symbol']: c for c in evidence['companies']}
    candidates, excluded = [], []
    for event in sorted(dataset.events.values(), key=lambda e: (e['ex_date'], e['symbol'])):
        if event['symbol'] not in request.symbols or not start <= event['ex_date'] <= end:
            continue
        reasons = list(event.get('reasons', []))
        if not event['replay_available']:
            reasons.append('Event belum siap replay')
        reasons += blocked.get(event['symbol'], [])
        declaration = event.get('declaration_date')
        known = bool(declaration and declaration < start)
        if declaration and declaration >= start:
            reasons.append('Pengumuman belum tersedia sebelum tanggal keputusan')
        elif not known and not request.allow_calendar_assumption:
            reasons.append('Timestamp pengumuman belum terverifikasi; asumsi kalender dimatikan')
        try:
            entry = dataset.entry_date(event, request.rules.entry_offset)
            if entry < start:
                reasons.append('Tanggal entry mendahului awal periode')
            ex_idx = dataset.market_sessions.index(event['ex_date'])
            limit_idx = ex_idx+request.max_holding_sessions
            cap = dataset.market_sessions[limit_idx] if limit_idx < len(dataset.market_sessions) else None
            if request.exit_rule == 'ex_close':
                planned_exit = event['ex_date']
            elif request.exit_rule == 'payment_close':
                payment_session = next((d for d in dataset.market_sessions if event.get('payment_date') and d >= event['payment_date']), None)
                planned_exit = min(d for d in (cap, payment_session) if d) if cap or payment_session else None
            else:
                planned_exit = cap
            release = dataset.settlement(planned_exit) if planned_exit else None
            dataset.validate_coverage(event, entry, min(planned_exit or end, end))
        except ValueError as error:
            reasons.append(str(error))
            entry, release, planned_exit = None, None, None
        base = {'event_id': event['id'], 'symbol': event['symbol'], 'entry_date': entry,
                'cum_date': event['cum_date'], 'ex_date': event['ex_date'], 'payment_date': event['payment_date'],
                'dps': event['dps'], 'calendar_status': 'verified' if known else 'assumed' if request.allow_calendar_assumption else 'unknown',
                'planned_exit_bound': planned_exit, 'planned_cash_release': release, 'reasons': reasons,
                'evidence': {k: stats[event['symbol']].get(k) for k in ['rank', 'complete_events', 'median_return_pct', 'trap_pct', 'trap_interval', 'median_recovery_sessions']},
                'evidence_event_ids': [e['id'] for e in source_evidence[event['symbol']]['events'] if e['eligible'] and e['complete']],
                'evidence_latest_observation': max((e['last_date'] for e in source_evidence[event['symbol']]['events'] if e['eligible']), default=None)}
        (excluded if reasons else candidates).append(base)
    chronological = sorted(candidates, key=lambda c: (c['entry_date'], c['symbol'], c['event_id']))
    priority = sorted(candidates, key=lambda c: (c['evidence']['rank'], c['entry_date'], c['event_id']))
    templates = [('all', 'Semua peluang sesuai logika', chronological, False),
                 ('spaced', 'Jeda modal konservatif', chronological, True),
                 ('priority', 'Prioritas ranking tim', priority, True)]
    routes, signatures = [], set()
    for route_id, name, ordering, avoid_overlap in templates:
        chosen, omitted = [], []
        for candidate in ordering:
            conflicts = [c['event_id'] for c in chosen if candidate['entry_date'] < (c['planned_cash_release'] or '9999-12-31') and c['entry_date'] < (candidate['planned_cash_release'] or '9999-12-31')]
            reason = 'Batas jumlah event' if len(chosen) >= request.max_events else 'Jadwal modal konservatif berbenturan dengan '+', '.join(conflicts) if avoid_overlap and conflicts else None
            if reason:
                omitted.append({'event_id': candidate['event_id'], 'reason': reason})
            else:
                chosen.append(candidate)
        chosen.sort(key=lambda c: (c['entry_date'], c['symbol'], c['event_id']))
        signature = tuple(c['event_id'] for c in chosen)
        if not signature:
            continue
        if signature in signatures:
            next(r for r in routes if tuple(r['event_ids']) == signature)['also_matches'].append(name)
            continue
        signatures.add(signature)
        routes.append({'id': route_id, 'name': name, 'event_ids': list(signature), 'steps': chosen, 'omitted': omitted,
                       'also_matches': [], 'method': 'greedy_prior_ranking' if route_id == 'priority' else 'greedy_calendar'})
    return {'version': VERSION, 'dataset_version': dataset.version, 'evidence_dataset_version': evidence['dataset_version'],
            'decision_date': start, 'input': request.model_dump(mode='json'), 'ranking': ranking,
            'candidates': candidates, 'excluded': excluded, 'routes': routes,
            'assumptions': [
                f'Statistik dan outcome dipotong sebelum {start}; kalender dividen berikutnya diasumsikan sudah diketahui jika timestamp pengumuman kosong.',
                'Universe dipilih setelah 2025 dan snapshot terbaru; ini replay bersyarat, bukan backtest point-in-time bersih.',
                'Tiga aturan kandidat rute dibekukan sebelum replay; tidak diurutkan menurut keuntungan yang baru diketahui sesudahnya.',
                'Jeda modal memakai batas waktu dan T+2 sesi pasar teramati, bukan waktu BEP aktual masa depan. Entry bersamaan diurutkan alfabet emiten.',
                'Sesi IHSG dilengkapi pada gap yang dikonfirmasi harga valid seluruh sembilan emiten. Kalender settlement resmi belum diverifikasi.',
                'Median return/risk screening memakai horizon statistik yang dipilih; bukan forecast PnL rute atau exit-rule yang sama.',
                'Di luar biaya transaksi, pajak dan slippage. Skenario masa depan dan optimum rute global belum tersedia.',
            ]}


def replay_routes(dataset, plan):
    if plan['dataset_version'] != dataset.version:
        raise ValueError('Dataset berubah. Buat ulang rencana agar snapshot dan hasil konsisten.')
    if not plan['routes']:
        raise ValueError('Tidak ada kandidat rute yang lolos. Ubah aturan atau cakupan emiten.')
    request = RotationRequest.model_validate(plan['input'])
    results = []
    for route in plan['routes']:
        body = SimulationRequest(capital=request.capital, start_date=request.start_date, end_date=request.end_date,
                                 event_ids=route['event_ids'], entry_sessions_before_cum=request.rules.entry_offset,
                                 exit_rule=request.exit_rule, max_holding_sessions=request.max_holding_sessions)
        comparison = compare(dataset, body)
        for replay in comparison['alternatives']:
            replay['missed_events'] = [{'event_id': t['event_id'], 'reason': t['reason']} for t in replay['trades'] if t['status'] == 'skipped']
            replay['omitted_by_plan'] = deepcopy(route['omitted'])
        results.append({'route_id': route['id'], 'name': route['name'], 'comparison': comparison})
    return {'version': VERSION, 'dataset_version': dataset.version, 'decision_date': plan['decision_date'],
            'routes': results, 'input': plan['input'], 'assumptions': plan['assumptions'],
            'cash_baseline': {'capital': float(request.capital), 'ending_nav': float(request.capital), 'gross_pnl': 0,
                              'start_date': str(request.start_date), 'end_date': str(request.end_date)},
            'label': 'Hasil replay historis; bukan skor yang digunakan menyusun rute'}
