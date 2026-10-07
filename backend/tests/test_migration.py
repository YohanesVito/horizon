from datetime import datetime
import sqlite3
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend import store
from backend.config import database_url
from backend.migration import MigrationError, read_source, digest, transfer_records, write_private_env
from backend.main import app


def rows():
    return [dict(key='watchlist', kind='settings', payload='{"symbols": ["BBCA"], "missing": null}', created_at=datetime(2026, 1, 1, 2, 3, 4, 123456)),
            dict(key='old-run', kind='run', payload='{"status":"completed","result":{"value":"0.000001"}}', created_at=None)]


def test_migration_preserves_payload_timestamps_null_and_is_idempotent(tmp_path):
    engine = create_engine(f'sqlite:///{tmp_path}/target.db')
    store.Base.metadata.create_all(engine)
    with engine.begin() as connection:
        assert transfer_records(connection, rows()) == 2
        assert transfer_records(connection, rows()) == 0
        actual = list(connection.execute(select(store.Record.__table__)).mappings())
        assert digest(actual) == digest(rows())
        assert actual[0]['payload'] == rows()[0]['payload']


def test_conflicts_never_overwrite_or_partially_import(tmp_path):
    engine = create_engine(f'sqlite:///{tmp_path}/target.db')
    store.Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(store.Record.__table__.insert(), [{**rows()[1], 'payload': '{"newer":true}'}])
    with pytest.raises(MigrationError, match='differ'):
        with engine.begin() as connection:
            transfer_records(connection, rows())
    with engine.connect() as connection:
        actual = list(connection.execute(select(store.Record.__table__)).mappings())
        assert len(actual) == 1 and actual[0]['payload'] == '{"newer":true}'


def test_missing_source_is_not_created_and_active_jobs_are_rejected(tmp_path):
    path = tmp_path / 'source.db'
    with pytest.raises(MigrationError, match='does not exist'):
        read_source(path)
    assert not path.exists()
    with sqlite3.connect(path) as db:
        db.execute('create table records (key text, kind text, payload text, created_at text)')
        db.execute('insert into records values (?, ?, ?, ?)', ('run', 'run', '{"status":"running"}', '2026-01-01 02:03:04'))
    with pytest.raises(MigrationError, match='active jobs'):
        read_source(path)


def test_postgres_url_uses_psycopg_and_ssl_and_redacts_repr():
    url = database_url('postgresql://postgres:test-password@db.example:5432/postgres')
    assert url.drivername == 'postgresql+psycopg'
    assert url.query['sslmode'] == 'require'
    assert 'test-password' not in str(url)


@pytest.mark.parametrize('url', [
    'postgresql://postgres:secret@db.example:6543/postgres',
    'postgresql://postgres:secret@db.example/postgres?sslmode=disable',
    'postgresql://postgres@db.example/postgres',
    'postgresql://postgres:secret@db.example:invalid/postgres',
])
def test_invalid_connections_do_not_leak_password(url):
    with pytest.raises(ValueError) as caught:
        database_url(url)
    assert 'secret' not in str(caught.value)


def test_private_env_update_preserves_other_keys_and_permissions(tmp_path, monkeypatch):
    from backend import migration
    monkeypatch.setattr(migration, 'ROOT', tmp_path)
    path = tmp_path / '.env.local'
    path.write_text('# keep this\nSECTORS_API_KEY=existing-test-value\nDATABASE_URL=old\n')
    write_private_env({'DATABASE_URL': 'new-test-value'})
    assert 'SECTORS_API_KEY=existing-test-value' in path.read_text()
    assert '# keep this' in path.read_text()
    assert path.read_text().count('DATABASE_URL=') == 1
    assert path.stat().st_mode & 0o777 == 0o600


def test_health_fails_closed_without_exposing_database_error(monkeypatch):
    def unavailable():
        raise RuntimeError('postgresql://postgres:private-password@example/db')
    monkeypatch.setattr(store, 'healthcheck', unavailable)
    # No lifespan here: this is an unavailable-database response, not a cloud test.
    client = TestClient(app)
    response = client.get('/api/health')
    assert response.status_code == 503
    assert 'private-password' not in response.text


def test_record_kind_collision_preserves_original(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path}/test.db')
    monkeypatch.setattr(store, 'engine', engine)
    monkeypatch.setattr(store, 'Session', sessionmaker(bind=engine))
    store.init_store()
    store.save('fixed-key', 'settings', {'original': True})
    with pytest.raises(ValueError, match='different kind'):
        store.save('fixed-key', 'run', {'original': False})
    assert store.get('fixed-key', kind='settings') == {'original': True}
