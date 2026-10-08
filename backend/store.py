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


def claim_once(key, kind, payload):
    """Atomically insert a durable claim; only the inserted owner may do work."""
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    insert = pg_insert if engine.dialect.name == 'postgresql' else sqlite_insert
    statement = insert(Record).values(key=key, kind=kind, payload=json.dumps(payload, ensure_ascii=False))
    statement = statement.on_conflict_do_nothing(index_elements=[Record.key]).returning(Record.key)
    with Session.begin() as session:
        return session.execute(statement).scalar_one_or_none() == key


def insight_for_run(run_id, allocation=None):
    """Find pre-guard cached success without repeating an already billed run."""
    with Session() as session:
        rows = session.query(Record).filter_by(kind='simulation-insight').order_by(Record.created_at.asc(), Record.key).all()
        matches = [json.loads(row.payload) for row in rows if json.loads(row.payload).get('provenance', {}).get('run_id') == run_id and json.loads(row.payload).get('status') == 'completed']
        return next((payload for payload in matches if payload.get('provenance', {}).get('allocation') == allocation), matches[0] if matches else None)
    return None


def claim_retry(key):
    """CAS a failed record into the next attempt; never exceed three owners."""
    from sqlalchemy import update
    with Session.begin() as session:
        row = session.get(Record, key)
        if not row or row.kind != 'simulation-insight':
            raise ValueError('Invalid insight claim.')
        previous = row.payload
        payload = json.loads(previous)
        if payload.get('status') != 'unavailable' or payload.get('attempts', 3) >= 3:
            return None
        import time
        payload.update(status='processing', started_at=time.time(), attempts=payload['attempts']+1, exhausted=False)
        statement = update(Record).where(Record.key == key, Record.kind == 'simulation-insight', Record.payload == previous).values(payload=json.dumps(payload, ensure_ascii=False)).returning(Record.key)
        return payload if session.execute(statement).scalar_one_or_none() else None


def finish_attempt(key, attempt, result):
    """Only the current attempt owner can publish; reject late completion."""
    from sqlalchemy import update
    with Session.begin() as session:
        row = session.get(Record, key)
        previous = row.payload if row and row.kind == 'simulation-insight' else None
        current = json.loads(previous) if previous else {}
        if current.get('status') != 'processing' or current.get('attempts') != attempt:
            return False
        statement = update(Record).where(Record.key == key, Record.kind == 'simulation-insight', Record.payload == previous).values(payload=json.dumps(result, ensure_ascii=False)).returning(Record.key)
        return session.execute(statement).scalar_one_or_none() == key
