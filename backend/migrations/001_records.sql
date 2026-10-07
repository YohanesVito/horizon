-- Private, single-workspace application records. Market snapshots remain files.
CREATE SCHEMA horizon;
REVOKE ALL ON SCHEMA horizon FROM PUBLIC, anon, authenticated;

CREATE TABLE horizon.schema_migrations (
    version varchar(50) PRIMARY KEY,
    checksum varchar(64) NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE horizon.records (
    key varchar(100) PRIMARY KEY,
    kind varchar(30) NOT NULL,
    payload text NOT NULL,
    created_at timestamp without time zone
);
COMMENT ON COLUMN horizon.records.created_at IS 'UTC timestamp preserved from the SQLite application store';
CREATE INDEX ix_records_kind ON horizon.records (kind);

REVOKE ALL ON ALL TABLES IN SCHEMA horizon FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA horizon TO horizon_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON horizon.records TO horizon_app;
GRANT SELECT ON horizon.schema_migrations TO horizon_app;
ALTER TABLE horizon.records ENABLE ROW LEVEL SECURITY;
CREATE POLICY horizon_backend_records ON horizon.records
    FOR ALL TO horizon_app USING (true) WITH CHECK (true);
