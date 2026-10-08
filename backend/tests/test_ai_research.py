import asyncio
import json
from types import SimpleNamespace
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import ai, ai_research, store
from backend.sectors_news import NewsClient


@pytest.fixture
def storage(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/research.db', connect_args={'check_same_thread': False})
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    store.init_store()
    monkeypatch.setattr(ai_research, '_key', lambda: 'test')
    async def initialize(self):
        pass
    monkeypatch.setattr(NewsClient, 'initialize', initialize)


def inputs():
    run = {'id': 'research-run', 'input': {'capital': 100}, 'result': {'primary': {
        'allocation': 'equal', 'trades': [{'symbol': 'TEST', 'shares': 100}], 'start_date': '2021-04-01', 'end_date': '2021-05-01'}}}
    statistics = {'companies': [{'symbol': 'TEST', 'groups': [], 'unclassified_samples': [
        {'ex_date': '2021-04-01', 'cum_date': '2021-03-31', 'low_date': '2021-04-15'}]}]}
    return run, statistics


def test_adaptive_round_reads_first_results_and_durable_reuse(storage, monkeypatch):
    import backend.sectors_tools as tools
    requests = []
    class Gateway:
        def __init__(self, mcp, **kwargs):
            assert kwargs['max_calls'] == 6
            assert kwargs['credit_budget'] == 12
        def catalog(self):
            return [{'name': name, 'inputSchema': {'type': 'object'}} for name in ['fetch-corporate-actions', 'fetch-quarterly-financials']]
        async def execute(self, name, args):
            requests.append((name, args))
            return {'ok': True, 'source': {'id': f'source-{len(requests)}', 'title': name, 'url': 'https://docs.sectors.app', 'published_at': None, 'excerpt': 'Split event, report context'}, 'data': {'huge': 'must not pass raw full bodies'}}
    monkeypatch.setattr(tools, 'SectorsResearchGateway', Gateway)
    calls = []
    async def plan(prompt, schema, **kwargs):
        payload = json.loads(prompt)
        calls.append(payload)
        if len(calls) == 1:
            return {'complete': False, 'calls': [{'tool': 'fetch-corporate-actions', 'arguments_json': '{"symbol":"TEST"}', 'reason': 'Check price basis'}]}
        assert payload['previous_evidence']['sources'][0]['id'] == 'source-1'
        assert 'data' not in payload['previous_evidence']['rounds'][0]['results'][0]
        return {'complete': True, 'calls': [{'tool': 'fetch-quarterly-financials', 'arguments_json': '{"symbol":"TEST","report_date":"2021-03-31"}', 'reason': 'Follow up disclosed context'}]}
    monkeypatch.setattr(ai, 'generate_structured', plan)
    run, stats = inputs()
    result = asyncio.run(ai_research.research_context(run, stats))
    assert result['model_calls'] == 2
    assert result['tool_calls'] == 2
    assert len(result['sources']) == 2
    assert [name for name, _ in requests] == ['fetch-corporate-actions', 'fetch-quarterly-financials']
    assert asyncio.run(ai_research.research_context(run, stats)) == result
    assert len(calls) == 2


def test_planner_failure_records_partial_and_never_repeats_research(storage, monkeypatch):
    async def failure(*args, **kwargs):
        raise ai.AIError('failure')
    monkeypatch.setattr(ai, 'generate_structured', failure)
    run, stats = inputs()
    result = asyncio.run(ai_research.research_context(run, stats))
    assert result['status'] == 'partial'
    assert result['model_calls'] == 1
    assert result['sources'] == []
    assert result['gaps']
    assert asyncio.run(ai_research.research_context(run, stats)) == result


def test_interrupted_research_reuses_partial_evidence_without_calls(storage, monkeypatch):
    run, stats = inputs()
    value = {'status': 'processing', 'sources': [], 'gaps': [], 'model_calls': 1, 'tool_calls': 1}
    store.save('ai-research:research-run', 'simulation-research', value)
    async def no_call(*args, **kwargs):
        raise AssertionError('No additional provider requests after interrupted research')
    monkeypatch.setattr(ai, 'generate_structured', no_call)
    result = asyncio.run(ai_research.research_context(run, stats))
    assert result['status'] == 'partial'
    assert result['model_calls'] == 1
    assert result['tool_calls'] == 1


def test_research_once_plus_three_final_attempts_has_five_model_calls(storage, monkeypatch):
    from backend import insights
    import backend.sectors_tools as tools
    monkeypatch.setattr(ai, '_api_key', lambda: 'test')
    class Gateway:
        def __init__(self, *args, **kwargs):
            pass
        def catalog(self):
            return [{'name': 'fetch-corporate-actions', 'inputSchema': {'type': 'object'}}]
        async def execute(self, name, args):
            return {'ok': True, 'credits_used': 1, 'source': {'id': 'proof-1', 'title': 'Proof', 'url': 'https://docs.sectors.app', 'published_at': None, 'excerpt': 'Provider facts'}}
    monkeypatch.setattr(tools, 'SectorsResearchGateway', Gateway)
    counts = {'planning': 0, 'final': 0}
    async def model(prompt, schema, **kwargs):
        if 'calls' in schema['properties']:
            counts['planning'] += 1
            if counts['planning'] == 1:
                return {'complete': False, 'calls': [{'tool': 'fetch-corporate-actions', 'arguments_json': '{"symbol":"TEST"}', 'reason': 'Basis'}]}
            return {'complete': True, 'calls': []}
        counts['final'] += 1
        if counts['final'] < 3:
            raise ai.AIError('temporary failure')
        assert 'proof-1' in prompt
        return {'summary': 'Success', 'findings': [{'title': 'Context', 'detail': 'Evidence', 'source_ids': ['proof-1']}]}
    monkeypatch.setattr(ai, 'generate_structured', model)
    monkeypatch.setattr(insights, 'research_context', ai_research.research_context)
    run, _ = inputs()
    result = asyncio.run(insights.generate_insights(run, run['result']['primary'], SimpleNamespace(companies={})))
    assert result['status'] == 'completed'
    assert result['attempts'] == 3
    assert counts == {'planning': 2, 'final': 3}
    assert result['research']['model_calls'] == 2
    assert result['research']['tool_calls'] == 1
    assert asyncio.run(insights.generate_insights(run, run['result']['primary'], SimpleNamespace(companies={}))) == result
    assert counts == {'planning': 2, 'final': 3}


def test_research_window_includes_replay_end_beyond_historical_samples():
    run, stats = inputs()
    run['result']['primary'].update(start_date='2025-03-10', end_date='2025-05-20')
    stats['companies'][0]['unclassified_samples'] = [
        {'ex_date': '2021-04-01', 'cum_date': '2021-03-31', 'low_date': '2021-04-15'},
        {'ex_date': '2025-04-22', 'cum_date': '2025-04-21', 'low_date': '2025-04-24'}]
    start, end = ai_research._window(run, stats)
    assert start == '2021-03-17'
    assert end == '2025-06-03'
    from backend.sectors_tools import SectorsResearchGateway
    class MCP:
        async def request(self, method, params):
            assert params['arguments']['end'] == '2025-05-20'
            return {'content': [{'type': 'text', 'text': '[{"symbol":"TEST.JK","date":"2025-05-20","close":100}]'}]}
    gateway = SectorsResearchGateway(MCP(), allowed_symbols={'TEST'}, window_start=start, window_end=end)
    result = asyncio.run(gateway.execute('fetch-daily-price', {'symbol': 'TEST', 'start': '2025-04-21', 'end': '2025-05-20'}))
    assert result['status'] == 'completed'


def test_research_window_includes_payment_observation_beyond_actual_sale():
    run, stats = inputs()
    run['result']['primary']['trades'][0]['observation'] = {
        'cum_date': '2021-03-31', 'payment_date': '2021-06-01',
        'end_date': '2021-06-03', 'highest': {'date': '2021-05-25'},
        'lowest': {'date': '2021-04-16'}}
    assert ai_research._window(run, stats) == ('2021-03-17', '2021-06-17')
