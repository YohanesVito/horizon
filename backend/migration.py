"""Non-destructive SQLite -> Supabase record migration.

Run `python -m backend.migration` to inspect; add --apply to migrate and configure.
"""
from collections import Counter
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import tempfile
from dotenv import dotenv_values
from psycopg import sql
from sqlalchemy import select, text
from .config import ROOT, WORKER_LOCK, database_url, database_engine
from .store import Record

VERSION = '001_records'
SQL_PATH = ROOT / 'backend/migrations/001_records.sql'


class MigrationError(Exception):
    pass


def checksum():
    return hashlib.sha256(SQL_PATH.read_bytes()).hexdigest()


def verify_schema(connection):
    installed = dict(connection.execute(text('select version, checksum from horizon.schema_migrations')).all())
    if installed != {VERSION: checksum()}:
        raise MigrationError('Database schema version/checksum differs. Run the matching migration before starting Horizon.')


def schema_exists(connection):
    return connection.scalar(text("select exists(select 1 from pg_namespace where nspname='horizon')"))


def normalize_row(row):
    row = dict(row)
    if isinstance(row['created_at'], str):
        row['created_at'] = datetime.fromisoformat(row['created_at'])
    if row['created_at'] is not None and row['created_at'].tzinfo is not None:
        row['created_at'] = row['created_at'].astimezone(timezone.utc).replace(tzinfo=None)
    return row


def digest(rows):
    data = [normalize_row(row) for row in sorted(rows, key=lambda row: row['key'])]
    encoded = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()


def read_source(source):
    if not source.is_file():
        raise MigrationError('SQLite source does not exist.')
    # mode=ro prevents a misspelled path from creating an empty source database.
    with sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True) as db:
        if db.execute('pragma integrity_check').fetchone()[0] != 'ok':
            raise MigrationError('SQLite integrity check failed.')
        db.row_factory = sqlite3.Row
        rows = [normalize_row(row) for row in db.execute('select key, kind, payload, created_at from records order by key')]
    for row in rows:
        payload = json.loads(row['payload'])
        if row['kind'] in ('run', 'rotation-run') and payload.get('status') in ('queued', 'running'):
            raise MigrationError('Finish active jobs and stop the local backend before migration.')
    return rows


def backup_source(source):
    folder = ROOT / '.runtime/backups'
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix='pre-supabase-', suffix='.db', dir=folder)
    os.fchmod(fd, 0o600)
    os.close(fd)
    with sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True) as src:
        with sqlite3.connect(name) as dst:
            src.backup(dst)
    return Path(name)


def inspect_records(connection, rows):
    existing = {row['key']: normalize_row(row) for row in connection.execute(select(Record.__table__)).mappings()}
    conflicts = [row['key'] for row in rows if row['key'] in existing and row != existing[row['key']]]
    if conflicts:
        raise MigrationError(f'{len(conflicts)} existing record(s) differ. No records were overwritten.')
    return [row for row in rows if row['key'] not in existing]


def transfer_records(connection, rows):
    # Check every conflict before the first insert; the caller owns the transaction.
    missing = inspect_records(connection, rows)
    if missing:
        connection.execute(Record.__table__.insert(), missing)
    keys = [row['key'] for row in rows]
    copied = list(connection.execute(select(Record.__table__).where(Record.key.in_(keys))).mappings())
    if digest(copied) != digest(rows):
        raise MigrationError('Record verification failed; transaction must roll back.')
    return len(missing)


def install_schema(connection, password):
    if schema_exists(connection):
        verify_schema(connection)
        return False
    if connection.scalar(text("select exists(select 1 from pg_roles where rolname='horizon_app')")):
        raise MigrationError('horizon_app already exists without the expected schema. Inspect ownership before migration.')
    driver = connection.connection.driver_connection
    # Compose the password in the driver, never in CLI args, logs, or a saved SQL file.
    driver.execute(sql.SQL('CREATE ROLE horizon_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS PASSWORD {}').format(sql.Literal(password)))
    driver.execute(SQL_PATH.read_text(), prepare=False)
    connection.execute(text('insert into horizon.schema_migrations (version, checksum) values (:version, :checksum)'),
                       {'version': VERSION, 'checksum': checksum()})
    return True


def write_private_env(values):
    path = ROOT / '.env.local'
    if path.is_symlink():
        raise MigrationError('Refusing to replace a symlink for the private environment.')
    lines = path.read_text().splitlines() if path.exists() else []
    kept = []
    for line in lines:
        match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
        if not match or match.group(1) not in values:
            kept.append(line)
    body = '\n'.join(kept).rstrip() + '\n' + '\n'.join(f'{key}={value}' for key, value in values.items()) + '\n'
    fd, temp = tempfile.mkstemp(prefix='.env.local.', dir=ROOT)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run(source, apply=False):
    local = dotenv_values(ROOT / '.env.local')
    raw = os.getenv('MIGRATION_DATABASE_URL') or local.get('MIGRATION_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not raw:
        raise MigrationError('Set MIGRATION_DATABASE_URL or DATABASE_URL in the private environment.')
    admin = database_url(raw)
    if admin.get_backend_name() != 'postgresql':
        raise MigrationError('Migration destination must be PostgreSQL.')
    if admin.username == 'horizon_app':
        raise MigrationError('Use the migration/admin connection, not the runtime role.')
    rows = read_source(source)
    report = {'mode': 'apply' if apply else 'dry-run', 'schema_version': VERSION,
              'source_records': len(rows), 'source_by_kind': dict(Counter(row['kind'] for row in rows)),
              'source_digest': digest(rows), 'source_preserved': True}
    target = database_engine(admin)
    password = local.get('HORIZON_DB_APP_PASSWORD') or secrets.token_urlsafe(36)
    runtime = admin.set(username='horizon_app', password=password)
    # Shared session poolers include the project ref in the username.
    if admin.host.endswith('.pooler.supabase.com'):
        if '.' not in admin.username:
            raise MigrationError('Session pooler username must include its project reference.')
        runtime = runtime.set(username='horizon_app.' + admin.username.split('.', 1)[1])
    try:
        with target.begin() as connection:
            if not connection.scalar(text('select pg_try_advisory_xact_lock(:key)'), {'key': WORKER_LOCK}):
                raise MigrationError('Horizon is running against this database. Stop it before migration.')
            exists = schema_exists(connection)
            if exists:
                verify_schema(connection)
                missing = inspect_records(connection, rows)
            else:
                missing = rows
            report.update(schema_exists=exists, records_to_insert=len(missing))
            if not apply:
                return report
            backup = backup_source(source)
            backed_up_rows = read_source(backup)
            if digest(backed_up_rows) != digest(rows):
                raise MigrationError('Source changed during migration. Stop the SQLite backend and retry.')
            if exists and not local.get('HORIZON_DB_APP_PASSWORD'):
                raise MigrationError('Missing saved runtime role password; existing credentials were not rotated.')
            # Save the role secret before DB changes so interrupted configuration is recoverable.
            write_private_env({'MIGRATION_DATABASE_URL': admin.render_as_string(hide_password=False),
                               'HORIZON_DB_APP_PASSWORD': password})
            install_schema(connection, password)
            report['inserted'] = transfer_records(connection, rows)
            report['verified_records'] = len(rows)
            report['backup'] = str(backup.relative_to(ROOT))
        # The transaction has committed. Check the restricted role before switching runtime.
        runtime_engine = database_engine(runtime)
        try:
            with runtime_engine.connect() as connection:
                verify_schema(connection)
                stored = list(connection.execute(select(Record.__table__).where(Record.key.in_([row['key'] for row in rows]))).mappings())
                if digest(stored) != digest(rows):
                    raise MigrationError('Restricted-role verification failed; runtime was not switched.')
        finally:
            runtime_engine.dispose()
        write_private_env({'DATABASE_URL': runtime.render_as_string(hide_password=False)})
        report.update(runtime_configured=True, runtime_role='horizon_app', destination_digest=digest(stored))
        return report
    finally:
        target.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / '.runtime/dividen.db')
    parser.add_argument('--apply', action='store_true', help='Apply schema and data migration; default only inspects.')
    parser.add_argument('--report', type=Path, help='Save counts and checksums, never credentials or record payloads.')
    args = parser.parse_args()
    try:
        report = run(args.source, args.apply)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    except MigrationError as error:
        parser.exit(1, f'Migration stopped: {error}\n')
    except Exception as error:
        # Driver exceptions can include SQL, credentials, or private payloads.
        parser.exit(1, f'Migration stopped ({type(error).__name__}). Check the private connection configuration and database availability. No source records were deleted.\n')


if __name__ == '__main__':
    main()
