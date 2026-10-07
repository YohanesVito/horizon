"""Explicit cloud smoke check. One temporary probe record is removed in finally."""
from pathlib import Path
import json
import sys
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select, text, delete
from backend import store
from backend.config import ROOT
from backend.migration import digest, read_source, transfer_records


def main():
    if store.engine.dialect.name != 'postgresql':
        raise RuntimeError('This check requires the configured Supabase database.')
    store.init_store()
    source = read_source(ROOT / '.runtime/dividen.db')
    report = {}
    with store.worker_lease():
        try:
            with store.worker_lease():
                raise AssertionError('A second backend unexpectedly acquired the lease')
        except RuntimeError as error:
            assert 'already using' in str(error)
            report['second_backend_rejected'] = True
        with store.engine.begin() as connection:
            report['idempotent_inserted'] = transfer_records(connection, source)
            assert report['idempotent_inserted'] == 0
            role = connection.execute(text("select current_user, rolsuper, rolcreaterole, rolcreatedb, rolbypassrls from pg_roles where rolname=current_user")).one()
            assert role[0] == 'horizon_app' and not any(role[1:])
            report['restricted_role_verified'] = True
            access = connection.execute(text("select has_schema_privilege('anon', 'horizon', 'USAGE'), has_schema_privilege('authenticated', 'horizon', 'USAGE'), has_schema_privilege(current_user, 'horizon', 'CREATE'), (select relrowsecurity from pg_class where oid='horizon.records'::regclass)")).one()
            assert tuple(access) == (False, False, False, True)
            report['private_schema_and_rls_verified'] = True
        probe = 'migration-probe-' + str(uuid4())
        try:
            store.save(probe, 'migration-probe', {'version': 1, 'value': '0.000001', 'missing': None})
            assert store.get(probe)['version'] == 1
            assert store.get(probe, kind='run') is None
            with store.Session() as session:
                original_created = session.get(store.Record, probe).created_at
            store.save(probe, 'migration-probe', {'version': 2, 'value': '0.000001', 'missing': None})
            assert store.get(probe) == {'version': 2, 'value': '0.000001', 'missing': None}
            with store.Session() as session:
                assert session.get(store.Record, probe).created_at == original_created
            try:
                store.save(probe, 'run', {'invalid': True})
                raise AssertionError('Kind collision was accepted')
            except ValueError:
                pass
            assert store.get(probe)['version'] == 2
            report['read_insert_update_kind_guard_verified'] = True
        finally:
            with store.engine.begin() as connection:
                connection.execute(delete(store.Record).where(store.Record.key == probe, store.Record.kind == 'migration-probe'))
        with store.engine.connect() as connection:
            actual = list(connection.execute(select(store.Record.__table__)).mappings())
        assert len(actual) == len(source) and digest(actual) == digest(source)
        report.update(records_after_probe=len(actual), source_digest=digest(source), destination_digest=digest(actual),
                      temporary_probe_removed=True, storage=store.healthcheck())
    (ROOT / 'outputs/development/supabase-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    store.engine.dispose()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Do not print SQL/parameters/credentials when a cloud verification fails.
        raise SystemExit(f'Verification failed ({type(error).__name__}); inspect the individual checks without printing credentials.') from None
