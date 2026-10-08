import asyncio
import json
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import ai, insights, store
from backend.main import app
from backend.sectors_news import NewsClient


def timeline(drops, cycle='final'):
    periods = []
    for i, drop in enumerate(drops):
        ex = date(2021+i, 4, 1)
        periods.append({'id': f'TEST:{ex}', 'year': ex.year, 'ex_date': str(ex), 'cum_close': 100,
                        'cycle_key': cycle, 'eligible': True, 'issues': [],
                        'points': [{'date': str(ex+timedelta(days=j)), 'close': 100-drop if j == 2 else 100} for j in range(21)]})
    return SimpleNamespace(companies={'TEST': {'history': periods}})


def test_outlier_distribution_preserves_event_and_missing_data():
    history = timeline([24, 1, 2, 1, 2])
    result = insights.historical_statistics(history, {'TEST'})['companies'][0]
    group = result['groups'][0]
    assert group['upper_outlier'] is True
    assert group['mean_pct'] == 6
    assert group['median_pct'] == 2
    assert group['mean_without_maximum_pct'] == 1.5
    assert group['maximum']['year'] == 2021
    assert group['maximum']['low_date'] == '2021-04-03'
    history.companies['TEST']['history'][1]['points'].pop()
    result = insights.historical_statistics(history, {'TEST'})['companies'][0]
    assert result['groups'][0]['count'] == 4
    assert result['missing_years'] == [2022]
    assert result['excluded'][0]['year'] == 2022


def test_unclassified_cycles_are_not_averaged():
    result = insights.historical_statistics(timeline([24, 1], None), {'TEST'})['companies'][0]
    assert result['groups'] == []
    assert len(result['unclassified_samples']) == 2
    assert result['unclassified_distribution']['mean_pct'] == 12.5
    assert 'not a comparable annual' in result['unclassified_distribution']['comparability']


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/insights.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    async def mocked_research(run, stats):
        sources, gaps = await insights.news_context(stats)
        return {'sources': sources, 'gaps': gaps, 'status': 'completed', 'model_calls': 0, 'tool_calls': 0, 'version': 'fixture'}
    monkeypatch.setattr(insights, 'research_context', mocked_research)
    with TestClient(app) as client:
        yield client


def run_record(key='run-1'):
    selected = {'allocation': 'equal', 'trades': [{'symbol': 'TEST', 'shares': 100}], 'return_pct': 5}
    return {'id': key, 'status': 'completed', 'input': {'capital': 100}, 'dataset_version': 'fixture',
            'result': {'primary': selected, 'alternatives': [selected]}}


def test_endpoint_cache_and_run_isolation(client, monkeypatch):
    import backend.main as main
    monkeypatch.setattr(main, 'timeline_dataset', timeline([24, 1, 2, 1, 2]))
    monkeypatch.setattr(ai, '_api_key', lambda: 'test-key')
    calls = []
    async def news(stats):
        return [], ['Arsip berita tidak tersedia.']
    async def generate(prompt, schema, **kwargs):
        payload = json.loads(prompt)
        calls.append(payload)
        assert payload['input'] == {'capital': 100}
        return {'summary': 'Rata-rata 6% dan median 2%; event 2021 ekstrem.', 'findings': []}
    monkeypatch.setattr(insights, 'news_context', news)
    monkeypatch.setattr(ai, 'generate_structured', generate)
    store.save('run-1', 'run', run_record())
    endpoint = '/api/simulations/run-1/insights'
    result = request_insight(client, endpoint, json={'allocation': 'equal'})
    assert result.status_code == 200
    assert result.json()['status'] == 'completed'
    assert request_insight(client, endpoint, json={'allocation': 'equal'}).json() == result.json()
    assert len(calls) == 1
    assert store.get('run-1', kind='run')['status'] == 'completed'
    assert request_insight(client, endpoint, json={'allocation': 'single'}).status_code == 422
    assert request_insight(client, endpoint, json={'allocation': 'equal', 'capital': 900}).status_code == 422
    assert request_insight(client, '/api/simulations/absent/insights', json={'allocation': 'equal'}).status_code == 404
    store.save('queued', 'run', {**run_record('queued'), 'status': 'queued'})
    assert request_insight(client, '/api/simulations/queued/insights', json={'allocation': 'equal'}).status_code == 409
    store.save('other-kind', 'scenario', run_record('other-kind'))
    assert request_insight(client, '/api/simulations/other-kind/insights', json={'allocation': 'equal'}).status_code == 404
    # Same run with changed historical source should not reuse older explanation.
    main.timeline_dataset.companies['TEST']['history'][0]['points'][2]['close'] = 50
    assert request_insight(client, endpoint, json={'allocation': 'equal'}).json()['status'] == 'completed'
    assert len(calls) == 1


def test_failure_retry_and_inflight_dedup(client, monkeypatch):
    monkeypatch.setattr(ai, '_api_key', lambda: 'test-key')
    async def news(stats):
        return [], []
    monkeypatch.setattr(insights, 'news_context', news)
    calls = []
    async def unsupported(*args, **kwargs):
        calls.append(1)
        return {'summary': 'Unsupported', 'findings': [{'title': 'Fake', 'detail': 'No evidence', 'source_ids': ['invented']}]}
    monkeypatch.setattr(ai, 'generate_structured', unsupported)
    run = run_record()
    store.save(run['id'], 'run', run)
    endpoint = '/api/simulations/run-1/insights'
    assert request_insight(client, endpoint, json={'allocation': 'equal'}).json()['status'] == 'unavailable'
    assert request_insight(client, endpoint, json={'allocation': 'equal'}).json()['status'] == 'unavailable'
    assert len(calls) == 3
    # A failed attempt stays unavailable despite clearing all process state.
    async def good(*args, **kwargs):
        calls.append(1)
        await asyncio.sleep(.02)
        return {'summary': 'Valid', 'findings': []}
    monkeypatch.setattr(ai, 'generate_structured', good)
    run = run_record('fresh-concurrent')
    async def concurrent():
        return await asyncio.gather(*[insights.generate_insights(run, run['result']['primary'], timeline([1,2])) for _ in range(3)])
    results = asyncio.run(concurrent())
    assert sorted(r['status'] for r in results) == ['completed', 'processing', 'processing']
    assert len(calls) == 4


def test_missing_key_does_not_fetch_news_or_mutate_run(client, monkeypatch):
    def missing():
        raise ai.AIError('missing')
    monkeypatch.setattr(ai, '_api_key', missing)
    async def no_call(stats):
        raise AssertionError('News must not be called')
    monkeypatch.setattr(insights, 'news_context', no_call)
    run = run_record()
    store.save(run['id'], 'run', run)
    response = request_insight(client, '/api/simulations/run-1/insights', json={'allocation': 'equal'})
    assert response.json()['status'] == 'unavailable'
    assert store.get(run['id'], kind='run') == run


def test_mcp_news_transport_keeps_session_and_bounded_tool():
    async def exercise():
        import httpx
        requests = []
        def handle(request):
            body = json.loads(request.content)
            requests.append(body)
            if body['method'] == 'initialize':
                return httpx.Response(200, headers={'mcp-session-id': 'session'}, json={'jsonrpc': '2.0', 'id': body['id'], 'result': {'protocolVersion': '2025-03-26'}})
            assert request.headers['mcp-session-id'] == 'session'
            assert request.headers['MCP-Protocol-Version'] == '2025-03-26'
            if body['method'] == 'notifications/initialized':
                return httpx.Response(202)
            assert body['params']['name'] == 'fetch-news'
            assert body['params']['arguments']['limit'] == 3
            message = {'jsonrpc': '2.0', 'id': body['id'], 'result': {'content': [{'type': 'text', 'text': '{"results": []}'}]}}
            return httpx.Response(200, headers={'content-type': 'text/event-stream'}, text='data: '+json.dumps(message)+'\n\n')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            mcp = NewsClient(client, 'test')
            await mcp.initialize()
            assert await mcp.news('TEST', '2021-04-01', '2021-04-20') == []
        assert len(requests) == 3
    asyncio.run(exercise())


def test_news_uses_extreme_date_and_rejects_wrong_ticker_date_url(monkeypatch):
    monkeypatch.setenv('SECTORS_API_KEY', 'test-key')
    requests = []
    async def initialize(self):
        pass
    async def news(self, symbol, start, end):
        requests.append((symbol, start, end))
        return [
            {'source': 'https://example.org/article', 'timestamp': '2021-04-03T10:00:00', 'symbols': ['test.jk'], 'title': 'Relevant context', 'body': 'A disclosed event'},
            {'source': 'javascript:alert(1)', 'timestamp': '2021-04-03', 'symbols': ['TEST'], 'title': 'Unsafe', 'body': 'Unsafe'},
            {'source': 'https://example.org/other', 'timestamp': '2025-04-03', 'symbols': ['WRONG'], 'title': 'Unrelated', 'body': 'Unrelated'},
        ]
    monkeypatch.setattr(NewsClient, 'initialize', initialize)
    monkeypatch.setattr(NewsClient, 'news', news)
    async def corporate(*args, **kwargs):
        return [], []
    monkeypatch.setattr(insights, 'corporate_context', corporate)
    stats = insights.historical_statistics(timeline([24, 1, 2, 1, 2]), {'TEST'})
    sources, gaps = asyncio.run(insights.news_context(stats))
    assert requests == [('TEST', '2021-03-20', '2021-04-10')]
    assert len(sources) == 1
    assert sources[0]['event_id'] == 'TEST:2021-04-01'
    assert sources[0]['url'] == 'https://example.org/article'
    assert gaps == []


def test_largest_decline_is_not_automatically_an_outlier():
    stats = insights.distribution([{'drop_pct': value, 'event_id': str(i)} for i, value in enumerate([2, 15, 18, 20, 22])])
    assert stats['upper_outlier'] is False
    assert stats['median_pct'] > stats['mean_pct']
    assert insights.distribution([{'drop_pct': 24}, {'drop_pct': 1}])['upper_outlier'] is None


def test_corporate_split_context_and_aligned_ihsg_window():
    from backend.sectors_context import corporate_context
    class MCP:
        async def request(self, method, params):
            if params['name'] == 'fetch-corporate-actions':
                payload = {'symbol': 'BBCA.JK', 'corporate_actions': {'stock_split': [
                    {'date': '2021-10-13', 'split_ratio': 5}, {'date': '2020-01-01', 'split_ratio': 2}],
                    'agm': [{'agm_date': '2021-10-15', 'agm_result': 'DO NOT EXPOSE ' * 1000}]}}
            else:
                assert params['arguments']['start'] == '2021-10-01'
                assert params['arguments']['end'] == '2021-10-20'
                payload = [{'date': '2021-10-01', 'price': 100}, {'date': '2021-10-20', 'price': 101}]
            return {'content': [{'type': 'text', 'text': json.dumps(payload)}]}
    sources, gaps = asyncio.run(corporate_context(MCP(), 'BBCA', '2021-10-20', 'event', stock_cum_date='2021-10-01'))
    serialized = json.dumps(sources)
    assert '2021-10-13' in serialized
    assert '2020-01-01' not in serialized
    assert 'DO NOT EXPOSE' not in serialized
    assert '+1.00%' in serialized
    assert all(s['source_kind'] == 'provider_record' for s in sources)


def test_atomic_claim_across_independent_sessions(client):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as pool:
        claimed = list(pool.map(lambda i: store.claim_once('one-key', 'simulation-insight', {'owner': i}), range(20)))
    assert sum(claimed) == 1
    assert store.get('one-key', kind='simulation-insight')['owner'] in range(20)


def test_same_id_cannot_retry_failure_even_different_strategy(client, monkeypatch):
    monkeypatch.setattr(ai, '_api_key', lambda: 'test')
    async def news(stats):
        return [], []
    calls = []
    async def failing(*args, **kwargs):
        calls.append(1)
        raise ai.AIError('failed')
    monkeypatch.setattr(insights, 'news_context', news)
    monkeypatch.setattr(ai, 'generate_structured', failing)
    run = run_record()
    run['result']['alternatives'].append({**run['result']['primary'], 'allocation': 'single'})
    store.save(run['id'], 'run', run)
    path = '/api/simulations/run-1/insights'
    initial = request_insight(client, path, json={'allocation': 'equal'}).json()
    monkeypatch.setattr(insights, 'VERSION', 'new-version')
    later = request_insight(client, path, json={'allocation': 'single'}).json()
    assert initial == later
    assert later['status'] == 'unavailable'
    assert calls == [1, 1, 1]
    assert store.get(run['id'], kind='run') == run


def test_legacy_success_reused_without_paid_call(client, monkeypatch):
    run = run_record()
    old = {'status': 'completed', 'summary': 'Existing billed result', 'findings': [], 'sources': [],
           'limitations': [], 'statistics': {}, 'provenance': {'run_id': run['id']}}
    store.save('legacy-hash-key', 'simulation-insight', old)
    async def no_call(*args, **kwargs):
        raise AssertionError('Must reuse previously generated result')
    monkeypatch.setattr(ai, 'generate_structured', no_call)
    assert asyncio.run(insights.generate_insights(run, run['result']['primary'], timeline([1]))) == old
    assert store.get('ai-run:run-1', kind='simulation-insight') == old


def test_two_failures_then_success_lock_result(client, monkeypatch):
    monkeypatch.setattr(ai, '_api_key', lambda: 'test')
    news_calls = []
    async def news(stats):
        news_calls.append(1)
        return [], []
    calls = []
    async def generate(*args, **kwargs):
        calls.append(1)
        if len(calls) < 3:
            raise ai.AIError('failure')
        return {'summary': 'Third attempt succeeded', 'findings': []}
    monkeypatch.setattr(insights, 'news_context', news)
    monkeypatch.setattr(ai, 'generate_structured', generate)
    run = run_record()
    store.save(run['id'], 'run', run)
    path = '/api/simulations/run-1/insights'
    first = request_insight(client, path, json={'allocation': 'equal'}).json()
    assert first['status'] == 'completed'
    assert first['attempts'] == 3
    assert first['exhausted'] is False
    assert request_insight(client, path, json={'allocation': 'equal'}).json() == first
    assert len(calls) == 3
    assert len(news_calls) == 1


def test_late_completion_cannot_overwrite_newer_claim(client):
    store.claim_once('ai-run:test', 'simulation-insight', {'status': 'processing', 'attempts': 1})
    assert store.finish_attempt('ai-run:test', 1, {'status': 'unavailable', 'attempts': 1})
    assert store.claim_retry('ai-run:test')['attempts'] == 2
    assert not store.finish_attempt('ai-run:test', 1, {'status': 'completed', 'attempts': 1})
    assert store.get('ai-run:test')['attempts'] == 2


def test_concurrent_retry_claims_only_one_next_attempt(client):
    from concurrent.futures import ThreadPoolExecutor
    store.claim_once('retry-key', 'simulation-insight', {'status': 'unavailable', 'attempts': 1})
    with ThreadPoolExecutor(max_workers=8) as pool:
        claims = list(pool.map(lambda i: store.claim_retry('retry-key'), range(20)))
    assert sum(value is not None for value in claims) == 1
    assert store.get('retry-key')['attempts'] == 2


def test_legacy_prefers_primary_allocation(client):
    other = {'status': 'completed', 'summary': 'Other', 'provenance': {'run_id': 'same', 'allocation': 'single'}}
    primary = {'status': 'completed', 'summary': 'Primary', 'provenance': {'run_id': 'same', 'allocation': 'equal'}}
    store.save('old-primary', 'simulation-insight', primary)
    store.save('old-other', 'simulation-insight', other)
    assert store.insight_for_run('same', 'equal') == primary


def test_missing_key_has_zero_budget_and_recovers_after_configuration(client, monkeypatch):
    run = run_record('config-run')
    store.save(run['id'], 'run', run)
    def missing():
        raise ai.AIError('missing')
    monkeypatch.setattr(ai, '_api_key', missing)
    path = '/api/simulations/config-run/insights'
    missing_result = request_insight(client, path, json={'allocation': 'equal'}).json()
    assert missing_result['configured'] is False
    assert missing_result['attempts'] == 0
    assert store.get('ai-run:config-run', kind='simulation-insight') is None
    monkeypatch.setattr(ai, '_api_key', lambda: 'configured')
    async def news(stats):
        return [], []
    async def generate(*args, **kwargs):
        return {'summary': 'Configured now', 'findings': []}
    monkeypatch.setattr(insights, 'news_context', news)
    monkeypatch.setattr(ai, 'generate_structured', generate)
    response = request_insight(client, path, json={'allocation': 'equal'}).json()
    assert response['status'] == 'completed'
    assert response['attempts'] == 1


def request_insight(client, path, **kwargs):
    from time import sleep
    response = client.post(path, **kwargs)
    for _ in range(200):
        if response.status_code != 200 or response.json().get('status') != 'processing':
            return response
        sleep(.005)
        response = client.get(path)
    raise AssertionError('Insight worker did not finish')


def test_holding_payload_uses_persisted_values_and_marks_old_runs(monkeypatch):
    from types import SimpleNamespace
    run = run_record('holding-payload')
    run['input']['timing_mode'] = 'payment_plus_2'
    observation = {'cum_date': '2025-03-13', 'payment_date': '2025-04-11',
                   'end_date': '2025-04-15', 'horizon_sessions': 2, 'complete': False,
                   'gaps': ['One session unavailable'], 'shares': 100, 'invested': 10000,
                   'dividend_amount': 1000,
                   'highest': {'price': 110, 'total_value': 12000, 'pnl': 2000},
                   'lowest': {'price': 80, 'total_value': 9000, 'pnl': -1000},
                   'points': [{'date': '2025-03-13', 'close': 100}]}
    selected = run['result']['primary']
    selected['trades'][0].update(observation=observation, entry_price=100,
                                entry_price_basis='prior5_close_mean',
                                entry_reference_dates=['2025-03-06', '2025-03-07', '2025-03-10', '2025-03-11', '2025-03-12'])
    monkeypatch.setattr(ai, '_api_key', lambda: 'test')
    async def model(prompt, schema, **kwargs):
        payload = json.loads(prompt)
        actual = payload['holding_analysis'][0]['observation']
        assert payload['input']['timing_mode'] == 'payment_plus_2'
        assert payload['simulation']['trades'][0]['entry_price'] == 100
        assert payload['holding_analysis'][0]['entry_price_basis'] == 'prior5_close_mean'
        assert len(payload['holding_analysis'][0]['entry_reference_dates']) == 5
        assert 'rata-rata ini harga pembelian historis nyata' in kwargs['instructions']
        assert 'bukan lima transaksi' in kwargs['instructions']
        assert actual['highest']['total_value'] == 12000
        assert actual['lowest']['pnl'] == -1000
        assert actual['complete'] is False and actual['gaps']
        assert 'points' not in actual
        assert 'observation' not in payload['simulation']['trades'][0]
        assert 'bukan kas yang sudah diterima' in kwargs['instructions']
        assert 'bukan laba maksimum yang pasti bisa dieksekusi' in kwargs['instructions']
        assert '21 close' in kwargs['instructions']
        return {'summary': 'Fixture holding valuation', 'findings': []}
    monkeypatch.setattr(ai, 'generate_structured', model)
    result = asyncio.run(insights._generate(run, selected, SimpleNamespace(companies={}), 'unused', context=([], [])))
    assert result['status'] == 'completed'
    assert result['provenance']['holding_analysis_version'] == 1
    assert result['provenance']['date_grounding_version'] == 1
    assert result['provenance']['timing_mode'] == 'payment_plus_2'
    legacy = insights.holding_analysis(run_record()['result']['primary'])[0]
    assert legacy['observation'] is None and legacy['availability'] == 'unavailable_legacy_run'


def test_real_two_event_engine_observation_reaches_ai_sections(monkeypatch):
    """Exercise bundled market snapshot -> engine -> actual AI request, without paid calls."""
    from backend.main import dataset, timeline_dataset
    from backend.domain import SimulationRequest
    from backend.simulator import compare
    from decimal import Decimal
    event = next(e for e in dataset.events.values() if e['symbol'] == 'BBCA' and e['cum_date'].startswith('2025') and e['replay_available'])
    result = compare(dataset, SimulationRequest(timing_mode='payment_plus_2', capital=15000000,
                     event_ids=[event['id'], next(e['id'] for e in dataset.events.values() if e['symbol'] == 'ADRO' and e['cum_date'].startswith('2025') and e['replay_available'])], compare=False))
    trade = result['primary']['trades'][0]
    dates = dataset.market_sessions
    cum_index = dates.index(event['cum_date'])
    expected_dates = dates[cum_index-5:cum_index]
    expected_price = sum(Decimal(str(dataset.prices['BBCA'][d]['close'])) for d in expected_dates) / 5
    assert trade['entry_reference_dates'] == expected_dates
    assert trade['entry_price'] == float(expected_price)
    run = {'id': 'bbca-integration', 'input': result['input'], 'result': result, 'dataset_version': dataset.version}
    monkeypatch.setattr(ai, '_api_key', lambda: 'fixture')
    observed = []
    async def model(prompt, schema, **kwargs):
        payload = json.loads(prompt)
        assert payload['analysis_mode'] == 'independent_events'
        assert len(payload['holding_analysis']) == 2
        assert all(item['starting_capital'] == 15000000 for item in payload['holding_analysis'])
        assert 'ending_nav' not in payload['simulation']
        assert 'gross_pnl' not in payload['simulation']
        assert payload['alternatives'] == []
        assert all(trade['exit_date'] is None and trade['settlement_date'] is None for trade in payload['simulation']['trades'])
        assert 'Jangan membahas perbandingan antar-event' in kwargs['instructions']
        assert 'bukan penjualan' in kwargs['instructions']
        assert payload['holding_analysis'][0]['end_valuation'] == trade['end_valuation']
        actual = payload['holding_analysis'][0]
        assert actual['event_dates']['cum_date'] == event['cum_date']
        assert actual['event_dates']['ex_date'] == event['ex_date']
        assert actual['event_dates']['cum_date'] != actual['event_dates']['ex_date']
        assert actual['synthetic_booking_date'] == event['cum_date']
        assert 'tanggal di dalam ID bukan tanggal cum' in kwargs['instructions']
        assert actual['entry_reference_dates'] == expected_dates
        assert actual['entry_price_basis'] == 'prior5_close_mean'
        assert actual['observation']['highest'] == trade['observation']['highest']
        assert actual['observation']['lowest'] == trade['observation']['lowest']
        assert payload['simulation']['trades'][0]['entry_price'] == float(expected_price)
        assert payload['input']['timing_mode'] == 'payment_plus_2'
        assert 'harga pembelian historis nyata' in kwargs['instructions']
        observed.append(payload)
        return {'sections': [{'event_id': item['event_id'], 'summary': item['symbol'] + ' independent holding valuation', 'findings': []} for item in reversed(payload['holding_analysis'])]}
    monkeypatch.setattr(ai, 'generate_structured', model)
    insight = asyncio.run(insights._generate(run, result['primary'], timeline_dataset, 'unused', context=([], [])))
    assert insight['status'] == 'completed' and len(observed) == 1
    assert [section['event_id'] for section in insight['sections']] == [t['event_id'] for t in result['primary']['trades']]
    assert [section['symbol'] for section in insight['sections']] == ['BBCA', 'ADRO']
    assert insight['summary'] == '' and insight['findings'] == []
    async def missing_sections(*args, **kwargs):
        return {'summary': 'Unsupported old-format output', 'findings': []}
    monkeypatch.setattr(ai, 'generate_structured', missing_sections)
    missing = asyncio.run(insights._generate(run, result['primary'], timeline_dataset, 'unused', context=([], [])))
    assert missing['status'] == 'unavailable' and 'sections' not in missing


def test_section_event_identity_handles_same_ticker_missing_and_duplicate():
    selected = {'trades': [{'event_id': 'BBCA:a', 'symbol': 'BBCA'}, {'event_id': 'BBCA:b', 'symbol': 'BBCA'}]}
    sections = insights.normalize_sections([{'event_id': 'BBCA:b', 'summary': 'Only second event', 'findings': []}], selected)
    assert sections[0]['event_id'] == 'BBCA:a' and sections[0]['status'] == 'unavailable'
    assert sections[0]['summary'] is None and sections[0]['findings'] == []
    assert sections[1]['event_id'] == 'BBCA:b' and sections[1]['summary'] == 'Only second event'
    with pytest.raises(ai.AIError, match='Unsupported event section'):
        insights.normalize_sections([{'event_id': 'BBCA:a'}, {'event_id': 'BBCA:a'}], selected)
    with pytest.raises(ai.AIError, match='Unsupported event section'):
        insights.normalize_sections([{'event_id': 'OTHER:event'}], selected)


def ticker_fixture_run(event_ids):
    from backend.main import dataset
    from backend.domain import SimulationRequest
    from backend.simulator import compare
    result = compare(dataset, SimulationRequest(capital=15000000, event_ids=event_ids))
    return {'id': 'ticker-parallel-fixture', 'input': result['input'], 'result': result, 'dataset_version': dataset.version}


def test_ticker_calls_start_in_parallel_isolate_payload_and_reuse_cache(client, monkeypatch):
    from backend.main import dataset, timeline_dataset
    ids = [next(e['id'] for e in dataset.events.values() if e['symbol'] == symbol and e['cum_date'].startswith('2025') and e['replay_available']) for symbol in ['BBCA', 'ADRO']]
    run = ticker_fixture_run(ids)
    monkeypatch.setattr(ai, '_api_key', lambda: 'fixture')
    async def research(*args):
        return {'sources': [], 'gaps': []}
    monkeypatch.setattr(insights, 'research_context', research)
    started = []
    async def exercise():
        barrier = asyncio.Event()
        async def model(prompt, schema, **kwargs):
            payload = json.loads(prompt)
            symbols = {item['symbol'] for item in payload['holding_analysis']}
            assert len(symbols) == 1
            symbol = next(iter(symbols))
            assert {trade['symbol'] for trade in payload['simulation']['trades']} == {symbol}
            assert payload['input']['event_ids'] == [item['event_id'] for item in payload['holding_analysis']]
            started.append(symbol)
            if len(started) == 2:
                barrier.set()
            await asyncio.wait_for(barrier.wait(), timeout=1)  # serial dispatch would fail
            return {'sections': [{'event_id': item['event_id'], 'summary': symbol + ' isolated', 'findings': []} for item in payload['holding_analysis']]}
        monkeypatch.setattr(ai, 'generate_structured', model)
        results = await asyncio.gather(*(insights.generate_insights(run, run['result']['primary'], timeline_dataset, symbol=symbol) for symbol in ['BBCA', 'ADRO']))
        assert all(result['status'] == 'completed' for result in results)
        assert [result['provenance']['symbol'] for result in results] == ['BBCA', 'ADRO']
        for symbol in ['BBCA', 'ADRO']:
            cached = await insights.generate_insights(run, run['result']['primary'], timeline_dataset, symbol=symbol)
            assert cached['status'] == 'completed'
            assert insights.insight_status(run, symbol=symbol) == cached
        assert len(started) == 2
    asyncio.run(exercise())


def test_same_ticker_multiple_events_one_call_and_other_ticker_retry_isolated(client, monkeypatch):
    from backend.main import dataset, timeline_dataset
    bbca_ids = [e['id'] for e in dataset.events.values() if e['symbol'] == 'BBCA' and e['replay_available']][:2]
    assert len(bbca_ids) == 2
    adro = next(e['id'] for e in dataset.events.values() if e['symbol'] == 'ADRO' and e['cum_date'].startswith('2025') and e['replay_available'])
    run = ticker_fixture_run(bbca_ids + [adro])
    monkeypatch.setattr(ai, '_api_key', lambda: 'fixture')
    async def research(*args):
        return {'sources': [], 'gaps': []}
    monkeypatch.setattr(insights, 'research_context', research)
    calls = {'BBCA': 0, 'ADRO': 0}
    async def model(prompt, schema, **kwargs):
        payload = json.loads(prompt)
        symbol = payload['holding_analysis'][0]['symbol']
        calls[symbol] += 1
        if symbol == 'ADRO' and calls[symbol] == 1:
            raise ai.AIError('Fixture failure only ADRO')
        return {'sections': [{'event_id': item['event_id'], 'summary': item['event_id'], 'findings': []} for item in payload['holding_analysis']]}
    monkeypatch.setattr(ai, 'generate_structured', model)
    async def exercise():
        bbca, adro_result = await asyncio.gather(*(insights.generate_insights(run, run['result']['primary'], timeline_dataset, symbol=symbol) for symbol in ['BBCA', 'ADRO']))
        assert len(bbca['sections']) == 2 and len({section['event_id'] for section in bbca['sections']}) == 2
        assert bbca['attempts'] == 1 and adro_result['attempts'] == 2
        for symbol in calls:
            await insights.generate_insights(run, run['result']['primary'], timeline_dataset, symbol=symbol)
        assert calls == {'BBCA': 1, 'ADRO': 2}
    asyncio.run(exercise())
