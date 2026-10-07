"""Application records in private Supabase PostgreSQL, or local SQLite."""
from contextlib import contextmanager
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, text, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import declarative_base, sessionmaker
import json
from .config import ROOT, WORKER_LOCK, database_url, database_engine

(ROOT / '.runtime').mkdir(exist_ok=True)
URL = database_url()
engine = database_engine(URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Record(Base):
    __tablename__ = 'records'
    key = Column(String(100), primary_key=True)
    kind = Column(String(30), index=True, nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_store():
    if engine.dialect.name == 'sqlite':
        Base.metadata.create_all(engine)
    else:
        from .migration import verify_schema
        with engine.connect() as connection:
            verify_schema(connection)
            connection.execute(select(Record.key).limit(1))


@contextmanager
def worker_lease():
    """One local-thread worker process per cloud database; not a durable queue."""
    if engine.dialect.name == 'sqlite':
        yield
        return
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
        acquired = connection.scalar(text('select pg_try_advisory_lock(:key)'), {'key': WORKER_LOCK})
        if not acquired:
            raise RuntimeError('Another Horizon backend is already using this database. Stop it before starting a new instance.')
        try:
            yield
        finally:
            connection.execute(text('select pg_advisory_unlock(:key)'), {'key': WORKER_LOCK})


def healthcheck():
    with engine.connect() as connection:
        connection.execute(select(Record.key).limit(1))
    return 'sqlite-local' if engine.dialect.name == 'sqlite' else 'postgresql'


def save(key, kind, payload):
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    if engine.dialect.name == 'postgresql':
        statement = pg_insert(Record).values(key=key, kind=kind, payload=serialized)
        statement = statement.on_conflict_do_update(
            index_elements=[Record.key], set_={'payload': statement.excluded.payload},
            where=Record.kind == kind,
        ).returning(Record.key)
        with Session.begin() as s:
            if s.execute(statement).scalar_one_or_none() != key:
                raise ValueError('Record key belongs to a different kind.')
        return
    with Session.begin() as s:
        old = s.get(Record, key)
        if old:
            if old.kind != kind:
                raise ValueError('Record key belongs to a different kind.')
            old.payload = serialized
        else:
            s.add(Record(key=key, kind=kind, payload=serialized))


def get(key, default=None, *, kind=None):
    with Session() as s:
        row = s.get(Record, key)
        return json.loads(row.payload) if row and (kind is None or row.kind == kind) else default


def list_records(kind, limit=20):
    with Session() as s:
        rows = s.query(Record).filter_by(kind=kind).order_by(Record.created_at.desc()).limit(limit).all()
        return [json.loads(r.payload) for r in rows]
