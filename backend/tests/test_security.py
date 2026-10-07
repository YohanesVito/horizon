import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.security import validate_api_key_config


def test_production_requires_server_key(monkeypatch):
    monkeypatch.setenv('HORIZON_REQUIRE_API_KEY', '1')
    monkeypatch.delenv('HORIZON_API_KEY', raising=False)
    with pytest.raises(RuntimeError, match='server-only'):
        validate_api_key_config()
    monkeypatch.setenv('HORIZON_API_KEY', 'short-test-key')
    with pytest.raises(RuntimeError):
        validate_api_key_config()
    monkeypatch.setenv('HORIZON_API_KEY', 'a-test-key-that-is-at-least-32-characters')
    validate_api_key_config()


def test_key_protects_data_mutations_and_docs_but_allows_health(monkeypatch):
    secret = 'a-test-key-that-is-at-least-32-characters'
    monkeypatch.setenv('HORIZON_API_KEY', secret)
    monkeypatch.setattr('backend.store.healthcheck', lambda: 'test-database')
    client = TestClient(app)
    for path in ['/api/catalog', '/docs', '/openapi.json', '/api/health/']:
        assert client.get(path).status_code == 401
    assert client.post('/api/watchlist', json={'symbol': 'BBCA'}).status_code == 401
    assert client.get('/api/catalog', headers={'Authorization': 'Bearer wrong'}).status_code == 401
    assert client.get('/api/catalog', headers={'Authorization': 'Bearer ' + secret}).status_code == 200
    assert client.get('/api/health').json()['status'] == 'ok'
    assert secret not in client.get('/api/catalog').text


def test_local_mode_without_key_preserves_catalog(monkeypatch):
    monkeypatch.delenv('HORIZON_API_KEY', raising=False)
    monkeypatch.delenv('HORIZON_REQUIRE_API_KEY', raising=False)
    validate_api_key_config()
    assert TestClient(app).get('/api/catalog').status_code == 200
