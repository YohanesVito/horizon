"""SQLAlchemy store; SQLite is a documented local fallback, PostgreSQL is configurable."""
from pathlib import Path
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import json

ROOT = Path(__file__).resolve().parents[1]
(ROOT / '.runtime').mkdir(exist_ok=True)
URL = os.getenv('DATABASE_URL', 'sqlite:///' + str(ROOT / '.runtime/dividen.db'))
engine = create_engine(URL, connect_args={'check_same_thread': False} if URL.startswith('sqlite') else {}, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Record(Base):
    __tablename__ = 'records'
    key = Column(String(100), primary_key=True)
    kind = Column(String(30), index=True, nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_store():
    Base.metadata.create_all(engine)


def save(key, kind, payload):
    with Session.begin() as s:
        old = s.get(Record, key)
        text = json.dumps(payload, ensure_ascii=False, default=str)
        if old:
            old.payload = text
        else:
            s.add(Record(key=key, kind=kind, payload=text))


def get(key, default=None, *, kind=None):
    with Session() as s:
        row = s.get(Record, key)
        return json.loads(row.payload) if row and (kind is None or row.kind == kind) else default


def list_records(kind, limit=20):
    with Session() as s:
        rows = s.query(Record).filter_by(kind=kind).order_by(Record.created_at.desc()).limit(limit).all()
        return [json.loads(r.payload) for r in rows]
