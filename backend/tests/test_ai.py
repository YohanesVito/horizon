import asyncio
import json

import httpx
import pytest

from backend import ai

SCHEMA = {
    'type': 'object',
    'properties': {'label': {'type': 'string'}},
    'required': ['label'],
    'additionalProperties': False,
}


def completed(text='{"label":"hello"}'):
    return {'status': 'completed', 'output': [
        {'type': 'reasoning', 'summary': []},
        {'type': 'message', 'content': [{'type': 'output_text', 'text': text}]},
    ]}


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    monkeypatch.setattr(ai, 'ROOT', tmp_path)
    monkeypatch.setenv('AI_KEY', 'test-key-never-live')


def mock_api(monkeypatch, handler):
    original = httpx.AsyncClient
    monkeypatch.setattr(ai.httpx, 'AsyncClient', lambda **kw: original(
        transport=httpx.MockTransport(handler), **kw,
    ))


def test_request_and_parsed_result(monkeypatch):
    def handler(request):
        assert str(request.url) == ai.RESPONSES_URL
        assert request.headers['Authorization'] == 'Bearer test-key-never-live'
        data = json.loads(request.content)
        assert data['model'] == 'gpt-6-luna'
        assert data['input'] == 'Say hello'
        assert data['instructions'] == 'Be brief'
        assert data['store'] is False
        assert data['max_output_tokens'] == 512
        assert data['text']['format'] == {
            'type': 'json_schema', 'name': 'result', 'strict': True, 'schema': SCHEMA,
        }
        return httpx.Response(200, json=completed())
    mock_api(monkeypatch, handler)
    result = asyncio.run(ai.generate_structured(
        'Say hello', SCHEMA, instructions='Be brief', max_output_tokens=512,
    ))
    assert result == {'label': 'hello'}


def test_env_files_and_precedence(monkeypatch, tmp_path):
    (tmp_path / '.env').write_text('AI_KEY=env-key\n')
    (tmp_path / '.env.local').write_text('AI_KEY=local-key\n')
    assert ai._api_key() == 'test-key-never-live'
    monkeypatch.delenv('AI_KEY')
    assert ai._api_key() == 'local-key'
    (tmp_path / '.env.local').unlink()
    assert ai._api_key() == 'env-key'
    assert 'AI_KEY' not in ai.os.environ


@pytest.mark.parametrize('key', [None, '', '   '])
def test_missing_key_fails_without_network(monkeypatch, key):
    if key is None:
        monkeypatch.delenv('AI_KEY')
    else:
        monkeypatch.setenv('AI_KEY', key)
    mock_api(monkeypatch, lambda _: pytest.fail('Unexpected request'))
    with pytest.raises(ai.AIError, match='Set AI_KEY'):
        asyncio.run(ai.generate_structured('hello', SCHEMA))


@pytest.mark.parametrize('body, message', [
    (completed('not json'), 'invalid structured'),
    (completed('{"label":42}'), 'invalid structured'),
    (completed('{}'), 'invalid structured'),
    (completed('{"label":"hi","extra":1}'), 'invalid structured'),
    ({'status': 'incomplete', 'output': []}, 'did not complete'),
    ({'status': 'completed', 'output': []}, 'no structured output'),
    ({'status': 'completed', 'output': [{'type': 'message', 'content': [
        {'type': 'refusal', 'refusal': 'private refusal text'},
    ]}]}, 'refused'),
    ([], 'invalid structured'),
])
def test_unusable_responses(monkeypatch, body, message):
    mock_api(monkeypatch, lambda _: httpx.Response(200, json=body))
    with pytest.raises(ai.AIError, match=message):
        asyncio.run(ai.generate_structured('hello', SCHEMA))


@pytest.mark.parametrize('status', [400, 401, 429, 500])
def test_http_errors_do_not_expose_body_or_key(monkeypatch, status):
    mock_api(monkeypatch, lambda _: httpx.Response(status, text='test-key-never-live private input'))
    with pytest.raises(ai.AIError, match=f'HTTP {status}') as exc:
        asyncio.run(ai.generate_structured('hello', SCHEMA))
    assert 'test-key' not in str(exc.value)
    assert 'private input' not in str(exc.value)


def test_timeout(monkeypatch):
    def handler(request):
        raise httpx.ReadTimeout('private input', request=request)
    mock_api(monkeypatch, handler)
    with pytest.raises(ai.AIError, match='timed out'):
        asyncio.run(ai.generate_structured('hello', SCHEMA))


@pytest.mark.parametrize('prompt,schema', [
    ('', SCHEMA), ('hello', []), ('hello', {'type': 'array'}),
    ('hello', {'type': 'object', 'properties': {'x': {'type': 'invalid'}}}),
])
def test_invalid_input_never_calls_api(monkeypatch, prompt, schema):
    mock_api(monkeypatch, lambda _: pytest.fail('Unexpected request'))
    with pytest.raises(ValueError):
        asyncio.run(ai.generate_structured(prompt, schema))
