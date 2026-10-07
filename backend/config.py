"""Server-only configuration. Explicit process values override the local env file."""
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env.local', override=False)
DATABASE_SCHEMA = 'horizon'
WORKER_LOCK = 4351820671001


def database_url(raw=None):
    value = raw if raw is not None else os.getenv('DATABASE_URL')
    if not value:
        return make_url('sqlite:///' + str(ROOT / '.runtime/dividen.db'))
    try:
        url = make_url(value)
        if url.drivername in ('postgres', 'postgresql', 'postgresql+psycopg'):
            url = url.set(drivername='postgresql+psycopg')
            if not url.host or not url.username or not url.password:
                raise ValueError()
            if url.port == 6543:
                raise ValueError('Use a direct connection or session pooler (port 5432).')
            if url.query.get('sslmode', 'require') not in ('require', 'verify-ca', 'verify-full'):
                raise ValueError('PostgreSQL requires SSL.')
            return url.update_query_dict({'sslmode': url.query.get('sslmode', 'require')})
        if url.drivername == 'sqlite':
            return url
    except Exception:
        # Never include the connection string or driver error in a config error.
        raise ValueError('Invalid DATABASE_URL. Use SQLite or PostgreSQL with SSL and a direct/session connection.') from None
    raise ValueError('Unsupported database driver.')


def database_engine(url):
    if url.get_backend_name() == 'sqlite':
        return create_engine(url, connect_args={'check_same_thread': False}, hide_parameters=True)
    return create_engine(
        url, pool_pre_ping=True, pool_size=5, max_overflow=2, pool_timeout=15,
        connect_args={'connect_timeout': 10}, hide_parameters=True,
        execution_options={'schema_translate_map': {None: DATABASE_SCHEMA}},
    )
