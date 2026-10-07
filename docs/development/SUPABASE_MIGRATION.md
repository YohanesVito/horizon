# Supabase — migrasi penyimpanan aplikasi

7 Oktober 2026 · DB-01/DB-02/DB-03 · branch `feat/supabase-migration`.

## Scope

Memindahkan record aplikasi SQLite ke PostgreSQL Supabase: settings/watchlist/rules, run simulasi, scenario, rotation-plan, dan rotation-run. Kontrak API serta payload hasil lama dipertahankan, termasuk null, presisi angka yang disimpan, ID, versi engine/dataset dan timestamp. Dataset harga/kalender Sectors tetap snapshot immutable di repository. Migrasi ini tidak menambah akun pengguna, memindahkan market snapshots, atau men-deploy FastAPI/Next.js ke hosting publik.

Alur: browser → Next.js proxy → FastAPI → schema `horizon` di Supabase. Engine kalkulasi tetap Python. Semua pengguna masih berbagi satu workspace; Supabase Auth/JWKS belum digunakan untuk login aplikasi.

## Konfigurasi server

Install dependensi backend dari `backend/requirements.lock`. Backend otomatis membaca `.env.local` dengan `python-dotenv`; environment proses eksplisit mengungguli file. File lokal diabaikan Git dan harus berizin600. Nilai rahasia tidak masuk dokumentasi, log atau frontend.

- `DATABASE_URL`: koneksi runtime `horizon_app` yang disimpan oleh migrator setelah verifikasi.
- `MIGRATION_DATABASE_URL`: koneksi admin untuk CLI migrasi saja.
- `HORIZON_DB_APP_PASSWORD`: rahasia akun runtime untuk pemulihan konfigurasi setelah migrasi terputus; tidak dirotasi oleh rerun.
- Variabel Supabase API key yang sudah tersimpan tetap utuh. SQLAlchemy memakai koneksi PostgreSQL; API keys tidak menggantikan password database.

Gunakan direct connection atau session pooler. Runtime memakai advisory lock sesi untuk membatasi satu backend aktif; transaction pooler port6543 ditolak. Driver dinormalisasi ke `postgresql+psycopg`, SSL diwajibkan, connection timeout10detik dan parameter SQL disembunyikan dari exception SQLAlchemy. Gunakan URL dari dialog Connect Supabase, bukan menebak hostname pooler. `sslmode=require` mengenkripsi koneksi; konfigurasi `verify-full` dengan root certificate dapat digunakan ketika deployment memerlukan verifikasi sertifikat eksplisit.

## Schema dan akses

`backend/migrations/001_records.sql` membuat `horizon.records`, indeks kind, dan `horizon.schema_migrations`. Versi serta checksum SQL diperiksa pada startup; runtime PostgreSQL tidak menjalankan `create_all`. SQLite lokal masih dapat menginisialisasi tabel untuk pengembangan/testing.

Schema tidak diberi USAGE kepada `PUBLIC`, `anon` atau `authenticated`. `horizon_app` tidak memiliki superuser, create-role, create-database atau bypass-RLS. Haknya adalah USAGE schema, DML records dan SELECT migration history. RLS records aktif dengan policy khusus backend. Ini pembatasan akses database untuk workspace bersama, bukan isolasi antar-user.

Payload tetap bertipe text agar migrasi byte-preserving; normalisasi schema domain/JSONB merupakan pekerjaan lain. `created_at` adalah timestamp UTC tanpa timezone mengikuti SQLite lama. Upsert runtime atomik dan menolak key yang sudah dipakai kind berbeda.

## Menjalankan migrasi

Hentikan backend sumber dahulu. Jangan menjalankan pengujian ini ketika pengguna sedang mengubah watchlist/rules atau menjalankan simulasi.

```sh
.venv/bin/python -m pip install -r backend/requirements.lock
.venv/bin/python -m backend.migration --report outputs/development/supabase-migration-dry-run.json
.venv/bin/python -m backend.migration --apply --report outputs/development/supabase-migration.json
```

Dry-run tidak membuat schema, role atau record. Apply membuat backup konsisten melalui SQLite backup API di `.runtime/backups/` dengan izin600. Source dibuka read-only; job queued/running ditolak. Semua konflik diperiksa sebelum insert. Schema/role/data/version dibuat dalam transaksi PostgreSQL. Rerun melewati record identik, tetapi menolak record berbeda; tidak menyediakan opsi force/overwrite.

Sebelum commit, seluruh record yang diimpor diverifikasi berdasarkan checksum ID/kind/payload/timestamp. Setelah commit, koneksi akun terbatas diverifikasi kembali sebelum DATABASE_URL runtime diganti. Kegagalan driver hanya menampilkan kelas error generik, tanpa URL/SQL/payload. Bila konfigurasi gagal setelah commit, database tidak otomatis dihapus; gunakan koneksi admin dan rahasia runtime yang sudah tersimpan untuk rerun.

Jangan menimpa laporan migrasi awal setelah aplikasi mulai berubah. Skrip default menerima sumber `.runtime/dividen.db`; `--source` dapat menunjuk backup yang sudah diverifikasi.

## Menjalankan dan memeriksa aplikasi

```sh
.venv/bin/python -m pytest backend/tests -q
# Cloud smoke: jalankan ketika backend berhenti. Satu record probe dibuat lalu dibersihkan.
.venv/bin/python work/verify_supabase.py
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Terminal frontend:

```sh
bun run start:lan
```

`GET /api/health` melakukan query tabel dan melaporkan `storage=postgresql`; database tidak terjangkau menghasilkan503 tanpa detail koneksi. API riwayat/watchlist tetap sama. Frontend memakai build chart yang sudah ada; tidak ada perubahan TSX/CSS pada migrasi ini.

`work/verify_supabase.py` memeriksa akun terbatas, schema privat/RLS, rerun tanpa insert, read/insert/update/kind guard, timestamp, pembersihan record probe, checksum seluruh record dan penolakan backend kedua. Skrip ini ditujukan untuk pemeriksaan segera setelah migrasi; jika data cloud telah berubah dari sumber, checksum memang akan berbeda. Pengujian pytest selalu memaksa database lokal, agar tidak menulis ke Supabase melalui `.env.local`.

Local-thread worker tetap belum durable. Jalankan **satu proses FastAPI, tanpa `--workers` >1**. Advisory lock mencegah startup kedua menandai job proses pertama sebagai gagal. Worker queue/lease dengan recovery lintas instance tetap pekerjaan selanjutnya.

## Rollback

Untuk kembali ke snapshot lokal, hentikan backend lalu jalankan dengan URL SQLite eksplisit:

```sh
DATABASE_URL=sqlite:////Users/killerbie/Documents/Codex/horizon/.runtime/dividen.db \
  .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Ini membuka keadaan lokal sebelum migrasi. Perubahan baru di Supabase tidak otomatis tersalin ke SQLite. Jika sudah ada data baru di cloud, ekspor dan rekonsiliasi dahulu; jangan mengklaim rollback tanpa kehilangan update. Schema/role/data cloud tidak dihapus oleh rollback. Backup lokal dan snapshot riset tetap dipertahankan.

## Referensi

- [Koneksi PostgreSQL Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [API keys Supabase](https://supabase.com/docs/guides/getting-started/api-keys)
- [Role PostgreSQL](https://supabase.com/docs/guides/database/postgres/roles)
- [SQLAlchemy schema translation](https://docs.sqlalchemy.org/en/20/core/connections.html#translation-of-schema-names)

Bukti pemeriksaan aktual dicatat di PROGRESS.md dan `outputs/development/supabase-*.json`. UAT, data lengkap lima tahun dan prediksi tetap berstatus sesuai issue sebelumnya.

Hasil7Oktober2026:20record sumber/tujuan cocok,57tes backend lulus, cloud smoke/rerun0insert lulus, dan10GET lewat proxy frontend menghasilkan200 dengan riwayat serta hasil lama tetap sama. Perbaikan upsert diperlukan karena rowcount psycopg mengembalikan−1; menggunakan RETURNING key memperbaiki pemeriksaan hasil (ISS-045). Tidak ada build frontend atau UAT yang diklaim dijalankan pada migrasi ini.
