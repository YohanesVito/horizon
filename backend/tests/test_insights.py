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
    result = client.post(endpoint, json={'allocation': 'equal'})
    assert result.status_code == 200
    assert result.json()['status'] == 'completed'
    assert client.post(endpoint, json={'allocation': 'equal'}).json() == result.json()
    assert len(calls) == 1
    assert store.get('run-1', kind='run')['status'] == 'completed'
    assert client.post(endpoint, json={'allocation': 'single'}).status_code == 422
    assert client.post(endpoint, json={'allocation': 'equal', 'capital': 900}).status_code == 422
    assert client.post('/api/simulations/absent/insights', json={'allocation': 'equal'}).status_code == 404
    store.save('queued', 'run', {**run_record('queued'), 'status': 'queued'})
    assert client.post('/api/simulations/queued/insights', json={'allocation': 'equal'}).status_code == 409
    store.save('other-kind', 'scenario', run_record('other-kind'))
    assert client.post('/api/simulations/other-kind/insights', json={'allocation': 'equal'}).status_code == 404
    # Same run with changed historical source should not reuse older explanation.
    main.timeline_dataset.companies['TEST']['history'][0]['points'][2]['close'] = 50
    assert client.post(endpoint, json={'allocation': 'equal'}).json()['status'] == 'completed'
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
    assert client.post(endpoint, json={'allocation': 'equal'}).json()['status'] == 'unavailable'
    assert client.post(endpoint, json={'allocation': 'equal'}).json()['status'] == 'unavailable'
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
    response = client.post('/api/simulations/run-1/insights', json={'allocation': 'equal'})
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
    initial = client.post(path, json={'allocation': 'equal'}).json()
    monkeypatch.setattr(insights, 'VERSION', 'new-version')
    later = client.post(path, json={'allocation': 'single'}).json()
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
    first = client.post(path, json={'allocation': 'equal'}).json()
    assert first['status'] == 'completed'
    assert first['attempts'] == 3
    assert first['exhausted'] is False
    assert client.post(path, json={'allocation': 'equal'}).json() == first
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
    missing_result = client.post(path, json={'allocation': 'equal'}).json()
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
    response = client.post(path, json={'allocation': 'equal'}).json()
    assert response['status'] == 'completed'
    assert response['attempts'] == 1
