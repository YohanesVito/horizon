# Progres development MVP

## Handoff deployment dan merge main — arahan PM terbaru 8 Oktober 2026

PM mengambil alih deployment Vercel dan meminta merge sekarang. **V-02 DONE dengan scope terbaru hanya merge/push main**; kewajiban Preview end-to-end sebelum merge pada rencana lama digantikan arahan ini. V-01 PARTIAL/HANDOFF, bukan DONE/UAT. Environment BACKEND_URL dan HORIZON_API_KEY berhasil dipasang pada Preview/Production setelah izin eksplisit PM; key bertipe Secret. Proses deployment yang telah dikirim sebelum interupsi ternyata selesai sebagai Production/READY (`dpl_9n4FifdytrSNHRdS4JdFRpuwtryi`), alias https://horizon-nu-kohl.vercel.app, source4588681. Belum diuji end-to-end dan bukan bukti API berfungsi. Integrasi Git otomatis ditolak approval review karena akses lintas layanan; tidak dijalankan. Tidak membuat deployment baru sesudah arahan handoff.

Bukti V-02: merge non-fast-forward `90e07c1` memuat integrasi `6536fbb` dan seluruh UI polish `523c993`; push main dan branch integrasi berhasil. `git ls-remote` memverifikasi main=`90e07c11c38bb495711b20a80af740797e6bcdb7`. Pohon merge identik dengan branch integrasi; source aplikasi/config/dependency identik dengan build/60tes/7proxychecks yang sudah lulus sebelum merge. Tidak menjalankan ulang suite untuk perubahan dokumentasi saja. Checkout berada di main, tanpa konflik. Catatan penyelesaian ini merupakan commit dokumentasi sesudah merge.

Catatan di bawah adalah riwayat; status menunggu izin secret dan env kosong sudah digantikan update ini.

## Integrasi dan Vercel — 8 Oktober 2026

**BR-02 DONE pada integrasi lokal dan pemeriksaan development.** PM menyetujui urutan BR-01. Supabase/Dalang f64df85 sudah di-push pada feat/supabase-migration. UI polish523c993 digabung tanpa konflik kode; tiga dokumen direkonsiliasi. Issue UI asal044/045/046 menjadi052/053/054; ID migrasi/deployment tetap. Snapshot readiness-case asli dipertahankan, fixture versi UI cocok secara strict dengan result engine. Build produksi/TypeScript, lint,60tes backend dan7check proxy lulus. Frontend3000 direstart; browser membuktikan landing LPPF, dua menu, modal kosong lalu50.000.000, dan console tanpa error/warning. Health proxy200 memakai PostgreSQL melalui VPS. Bukti integration-verification.json. GitHub500 pada dua percobaan awal teratasi melalui push CLI yang berhasil. Tidak mengubah release backend aktif, data cloud, atau layanan kurasi.

**V-01 IN_PROGRESS, V-02 PENDING.** Project Vercel horizon dibuat dan linked ke Vito's projects (vitos-projects-c7162407); CLI berhasil meskipun MCP403. Build/install Next ditetapkan di vercel.json; .vercelignore mengecualikan backend, secrets, runtime dan snapshot dari upload frontend. Automatic approval review menolak pengiriman BACKEND_URL/HORIZON_API_KEY ke Vercel karena meminta izin eksplisit untuk secret dan tujuan tersebut. Perintah tidak dijalankan, environment belum dipasang. Preview end-to-end dan promosi main/production menunggu penyelesaian izin ini. UAT tetap belum dilakukan.

Update V-01: commit merge7be31b2 sudah di-push dan remote cocok. Build cloud Vercel berhasil (42file frontend), tetapi deployment pertama otomatis menjadi Production walau --target preview; deployment kosong itu sudah dihapus. Tidak ada env terunggah, env ls kosong. Percobaan --skip-domain bersama target Preview ditolak sebelum deploy (opsi hanya Production). Target main tetap commit lama; uji cloud end-to-end menunggu izin environment. Bukti vercel-preparation.json; langkah lanjut di DEPLOYMENT_VERCEL.md. Localhost3000 tetap memakai build gabungan dan backend VPS.

## Review branch sebelum Vercel — 8 Oktober 2026

**BR-01 DONE pada scope review.** Remote `feat/timeline-ui-polish` 523c993 mencakup Sammy9fdf32b dan chart9cc1c81; Supabase/Dalang masih uncommitted di branch lokal feat/supabase-migration. Salinan sementara gabungan lulus build/TypeScript, lint dan60tes backend; preview browser tersambung VPS dan input modal bekerja. Tidak ada konflik kode, tiga dokumen berkonflik, ID issue bertabrakan. Fixture replay berbeda12teks tetapi angka/struktur sama (ISS-051). Rekomendasi dan bukti: [BRANCH_REVIEW.md](./BRANCH_REVIEW.md), `outputs/development/branch-review.json`. Checkout/branch aplikasi tidak diganti; tidak merge/commit/push/deploy Vercel. UAT tidak dijalankan.

## Deployment selesai — 8 Oktober 2026 WITA

**DEP-01, DEP-02, DEP-03: DONE pada scope backend dan development verification.** FastAPI container `horizon-api-1` healthy di Dalang, memakai Supabase Session Pooler dengan role runtime terbatas. Frontend lokal3000 sudah membaca backend VPS melalui proxy server; backend lokal8000 berhenti. HTTPS, proteksi key baca/tulis, delapan endpoint, replay API→worker→Supabase dan checksum20record lama lulus. Probe replay dibersihkan. Browser Peluang/Timeline/pratinjauLPPF tampil, consoleerror/warning kosong. Lima layanan kurasi tetap inactive/PID0; enabledstate tidak diubah.

Release `20261007T125050Z-f062081aa6`, image `sha256:4cec0602445d515db19c1d8d1e76d0ca4b49bca6029a51fa71ec393eb4002099`. Bukti final `outputs/deployment/deployment.json`, `dalang-api-verification.json`, `runtime-verification.json`, `frontend-proxy-verification.json`, `browser-verification.json`; [runbook operasi/rollback](./DEPLOYMENT_DALANG.md). Packaging sebelumnya:60pytest,7proxychecks, lint/TypeScript/build dan image smoke lulus. Retry mengubah konfigurasi koneksi, tidak mengubah engine atau menjalankan ulang seluruh suite.

ISS-047/049/050 RESOLVED (paket dpkg, MTU Docker, koneksi IPv6). ISS-048 tetap OPEN: I/O sangat lambat saat install/build/recreate, membaik setelah startup tetapi akar penyebab belum diketahui. Kebutuhan login, durableworker, gap data/forecast, PRD dan UAT tetap seperti sebelumnya. Frontend belum dipublikasikan ke Vercel; tidak ada commit/push atau klaim UAT. Catatan di bawah adalah riwayat tahap sebelumnya.

## Deployment Docker Dalang — 7 Oktober 2026

**DEP-01 DONE, DEP-02/DEP-03 IN_PROGRESS (13:59 UTC).** Image `sha256:4cec0602445d515db19c1d8d1e76d0ca4b49bca6029a51fa71ec393eb4002099` berhasil dibangun; smoke packaged health/catalog/intelligence/timeline/preview lulus. Bukti `outputs/deployment/build-result.json` dan `docker-build.log`. Backend lokal dihentikan dengan application shutdown complete sebelum aktivasi VPS untuk melepas single-worker lease. Aktivasi container produksi sedang berjalan; HTTPS/Supabase end-to-end belum dinyatakan lulus.

Update DEP-01 berikutnya: build pertama timeout ke PyPI pada bridge MTU1500, sedangkan uplink VPS1442 dan curl host berhasil. MTU daemon/default bridge disamakan1442; uji HTTPS dari container lulus. Build retry berhasil mengunduh dan memasang seluruh dependency terkunci, dilanjutkan copy layer aplikasi. ISS-049 RESOLVED pada konektivitas; uji image dan cutover tetap pending.

Update DEP-01: Docker Engine29.8.2/containerd2.3.6/Compose5.6.0 terpasang dan API daemon merespons. Build image sudah berjalan, checksum211file cocok. Laporan installer di `outputs/deployment/docker-install.log`. Masih menunggu build/smoke dan cutover; kendala I/O ISS-048 belum dinyatakan pulih.

**DEP-01–DEP-03: IN_PROGRESS, tertahan storage VPS (ISS-048).** PM meminta deploy sekarang. Dockerfile/Compose non-root, release allowlist 211 file dan runtime env terbatas sudah disiapkan/diunggah. Prasyarat dpkg sudo/libc-bin yang terputus berhasil diperbaiki (ISS-047). Instalasi Docker berikutnya berjalan sangat lambat pada penulisan paket; pengamatan 13:05:07 UTC menemukan IO full avg10=94.85%, memory PSI=0, Docker belum tersedia dan lima layanan kurasi tetap inactive. `horizon-build.service` diantrikan setelah installer berhasil; belum ada bukti build image atau API VPS lulus. Backend lokal belum dihentikan dan frontend belum dialihkan ke VPS.

Pemeriksaan lokal: 60 pytest lulus; tujuh pemeriksaan proxy server lulus; lint/TypeScript/production build lulus; 83 asset browser tidak memuat secret; health via frontend lokal HTTP200 dengan storage PostgreSQL. Kredensial yang diunggah hanya DATABASE_URL role terbatas dan HORIZON_API_KEY, file mode600; tidak ada admin/Supabase secret key pada VPS atau image. Bukti di `outputs/deployment/`, runbook [DEPLOYMENT_DALANG.md](./DEPLOYMENT_DALANG.md). Tidak membeli addon/domain, memaksa kill dpkg, mengaktifkan layanan kurasi, atau menyatakan deployment/UAT selesai. Docker lokal juga tidak berjalan, sehingga tidak ada klaim image sudah diuji di Docker lokal.

## Operasi Dalang — 7 Oktober 2026

**OPS-01: DONE.** PM mempertahankan FastAPI dengan target Docker pada VPS Dalang. Inventaris langsung menemukan satu VPS `hyperliquid-engine` (ID `10e0ff54-f828-44de-a965-5671328a08d3`), Docker tidak tersedia, dan lima layanan kurasi systemd aktif. Setelah PM mengonfirmasi penghentian kelima layanan, `systemctl stop --no-block` dikirim 12:09:29 UTC. Verifikasi 12:10:07 UTC: lima unit inactive/dead, Result=success, MainPID=0 dan tanpa pending job. Tidak mengubah enabled state, menghapus data atau mendeploy Horizon. Runbook: [DALANG_SERVICE_PAUSE.md](./DALANG_SERVICE_PAUSE.md); snapshot tersimpan di `outputs/operations/dalang-20261007T120842Z/` dan `/root/horizon-ops/20261007T120842Z/` pada VPS. Autostart saat reboot tetap aktif. Build/UAT tidak dijalankan karena tidak ada perubahan kode aplikasi. Kebutuhan deployment berikutnya: ISS-046.

Tanggal pembaruan: 6 Oktober 2026. Tahap saat ini: implementasi MVP lokal. PRD/user story lampiran belum tersedia; baseline sementara mengikuti percakapan dan instruksi coding 6 Oktober.

## Aturan pencatatan

Perbarui status setelah pekerjaan berubah, bukan hanya di akhir sprint. Setiap task selesai memiliki tanggal, hasil konkret, path/commit bila ada, pemeriksaan yang benar-benar dijalankan, dan issue tersisa. Task yang dibypass tetap ditandai `BYPASSED`, tidak berubah menjadi `DONE` hanya karena pekerjaan lain dilanjutkan.

Status task: `TODO`, `IN_PROGRESS`, `WAITING_INPUT`, `BLOCKED`, `BYPASSED`, `DONE`. `DONE` berarti selesai pada lingkup task dan pemeriksaan development yang dicatat; bukan otomatis lulus testing akhir. Status milestone `READY_FOR_TESTING` dan `DELIVERED` mengikuti [rencana sprint](./SPRINT_PLAN.md).

## Status task

DB-01/DB-02/DB-03 DONE pada scope migrasi record (7 Oktober 2026). Branch `feat/supabase-migration` dari `feat/chart`. Schema privat `horizon` di PostgreSQL Supabase dibuat dengan migration version/checksum, RLS dan akun runtime terbatas `horizon_app`; backend membaca env server dengan SSL.20record dipindahkan dan seluruh ID/kind/payload/timestamp mempunyai checksum sumber/tujuan sama. Backup `.runtime/backups/pre-supabase-lx6m5567.db` berizin600; SQLite asli tetap utuh. Cloud smoke membuktikan rerun0insert, pembatasan role/schema, penolakan backend kedua, CRUD/kind guard dan pembersihan probe.57pytest lulus (warning upstream ISS-016). ISS-044/045 dicatat serta diperbaiki.10GET melalui frontend3000 menghasilkan200: health melaporkanpostgresql, watchlist/rules/riwayat cocok, hasil simulasi lengkap tetap sama, katalog9emiten dan previewTimeline tersedia. Pemeriksaan API cloud read-only.57tes mencakup regression backend; tidak menjalankan ulang build/lint frontend karena TSX/CSS tidak berubah. Secret scan444file termasuk bundlefrontend tidak menemukan kredensial tersimpan; env lokal600 dan diabaikan Git. Bukti `supabase-migration-dry-run.json`, `supabase-migration.json`, `supabase-verification.json`, `supabase-api-verification.json`; runbook di SUPABASE_MIGRATION.md. FastAPI8000 dan frontend3000 dijalankan kembali. Hosting aplikasi, market snapshots, worker durable, akun pengguna dan UAT tetap di luar tahap ini.

Pemeriksaan lanjutan: Q-01–Q-03 DONE pada scope developer. Matriks1.620 replay/0gagal,40pytest, lint/typecheck/build dan browser lulus. TEST_MATRIX.md mencatat pengujian PM yang belum dijalankan; status UAT tidak diubah.

Sprint integrasi rotasi: R-01–R-05 DONE pada scope replay historis. Backend, UI, pemeriksaan development dan paket review tersedia. Timestamp announcement tetap asumsi eksplisit; PRD/UAT/forecast belum dinyatakan selesai.

Sprint intelligence: I-01 sampai I-05 DONE pada scope eksploratif yang tercatat. Baseline task di bawah tetap menjadi acuan; forecast terkalibrasi, coverage PRD dan UAT tidak otomatis selesai karena perluasan sprint.

| Task | Status | Hasil atau langkah berikutnya | Bukti atau issue |
|---|---|---|---|
| S0-01 | DONE | Inventaris sumber dan workspace | Catatan persiapan; ISS-001 |
| S0-02 | DONE | Rencana, traceability, progress dan issue log | 23 task; sumber PRD dibedakan dari percakapan |
| S0-03 | WAITING_INPUT | Lampiran PRD/user story belum tersedia | ISS-001; lokasi sudah ditanyakan sebelumnya |
| S0-04 | WAITING_INPUT | Rekonsiliasi dokumen asli belum dapat dilakukan | Bergantung S0-03 |
| S1-01 | DONE | Next.js + FastAPI berjalan lokal | Build, typecheck, lint, health dan proxy API lolos |
| S1-02 | BYPASSED sebagian | Supabase PostgreSQL record text/JSON dan migrasi berversi tersedia melalui DB-01/DB-02; schema domain kanonis dan market snapshots dalam database tetap ditunda | ISS-010, ISS-013; SUPABASE_MIGRATION.md |
| S1-03 | DONE | Lima area UI glassmorphism/dark sesuai palette | Browser desktop dan mobile390 px diperiksa |
| S2-01 | DONE | MCP Sectors7 respons baru + importer snapshot kalender REST | outputs/mvp-sectors; 9 emiten, 50 event2025 |
| S2-02 | DONE | Null, OHLC, urutan tanggal, konflik dan jendela replay divalidasi | 5 event eligible; uji karantina konflik dan eligibility lolos |
| S2-03 | DONE | Search/sort/filter dan simpan rules | Browser: yield≥10 menampilkan5 emiten, persisten setelah reload |
| S2-04 | DONE | Detail5 tanggal, kalender bulanan, watchlist persisten | Browser tambah/hapus/reload; statistik dan harga tampil |
| S3-01 | DONE | Ledger Decimal: lot, kas, posisi dan piutang | Uji konservasi NAV dan tanpa double count |
| S3-02 | DONE | 4 exit rules, sinyal BEP sesi berikutnya, horizon terbatas | Uji gap sesudah sinyal, exit batas waktu, posisi belum pulih |
| S3-03 | DONE | All-in event pertama, split rata, rotasi kas tersedia | Uji modal belum settle dan pembanding modal/horizon sama |
| S3-04 | DONE | API job, worker lokal, run/version/input/result persisten | Browser POST→completed→grafik; infra lokal bypass ISS-010 |
| S4-01 | DONE | Studi8 event BBCA dengan BEP harga/total dan non-recovery | 5 pulih,3 tersensor t20; bukan probabilitas prediksi |
| S4-02 | BYPASSED | Statistik empiris, ranking dan stress test analog tersedia lewat I-01–I-04; forecast terkalibrasi/rotasi forward belum tersedia | ISS-001, ISS-007, ISS-022–024; bagian forecast tetap gap |
| S4-03 | DONE | Harga/NAV, drawdown, piutang dan durasi modal tertahan | Browser pembanding dan ledger; durasi sampai settlement v1.1 |
| S5-01 | DONE | Alur discovery→simulasi→hasil serta empty/error terhubung | Browser termasuk tanggal invalid lalu perbaikan input |
| S5-02 | DONE | README, design, issue log dan bukti verifikasi | Preview localhost3000; VERIFICATION.md |
| S5-03 | WAITING_INPUT | Handoff lokal tersedia; coverage PRD belum bisa diaudit | ISS-001; bukan READY_FOR_TESTING formal atau DELIVERED |
| S6-01 | TODO | Pembahasan testing akhir bersama PM | Belum disepakati |
| S6-02 | TODO | Testing akhir/UAT setelah disepakati | Pemeriksaan development tidak menggantikan UAT |

## Catatan pekerjaan yang selesai

### 6 Oktober 2026

- **S0-01:** memeriksa daftar file workspace, AGENTS.md pada direktori induk, serta attachment artifact chat. Ditemukan dokumen riset/arsitektur dan skrip analisis. Tidak ditemukan PRD/user story, `package.json`, `pyproject.toml`, atau aplikasi yang berjalan. Daftar artifact chat kosong. Batas pemeriksaan: ini tidak membuktikan dokumen tidak ada di lokasi lain; lokasi sumber sudah ditanyakan.
- **S0-02:** membuat [SPRINT_PLAN.md](./SPRINT_PLAN.md), [TRACEABILITY.md](./TRACEABILITY.md), [PROGRESS.md](./PROGRESS.md), [ISSUES.md](./ISSUES.md), dan [AGENTS.md](../../AGENTS.md). Pemeriksaan lokal memastikan 23 ID task unik dan sama antara rencana/progres, sembilan ID issue unik, seluruh referensi issue dikenal, tautan berkas lokal ada, serta blok kode berpasangan. Pemeriksaan dokumen lolos; tidak ada testing aplikasi pada langkah ini.
- Keputusan PM **FastAPI** dicatat. Prioritas performa ditunda. Belum ada perubahan kode aplikasi, deployment, maupun testing akhir pada turn perencanaan ini.

## Template catatan penyelesaian berikutnya

```text
Tanggal:
Task dan story:
Perubahan yang selesai:
Bukti lokasi atau commit:
Pemeriksaan yang dijalankan dan hasil:
Issue, bypass atau TODO tersisa:
Status akhir task:
```

### Implementasi dan pemeriksaan awal — 6 Oktober 2026

- **S1-01/S1-03:** Next.js 16.3.8, React, Tailwind 4, ECharts, TanStack Query dan FastAPI berjalan. UI memakai glassmorphism/dark dan palette PM; #1A1A1D mengikuti gambar. Build produksi dan TypeScript lolos. Preview HTTP 200 pada port 3000, API health dan rewrite /api/catalog 200.
- **S2-01:** 7 panggilan MCP Sectors berhasil: harga BBRI/BMRI/BBNI/LPPF + laporan dividen tiga bank. Tersimpan di outputs/mvp-sectors dengan tool, arguments dan retrieved_at; kalender berasal dari REST Sectors snapshot riset yang sudah ada. Catalog nyata berisi 9 emiten, 50 event 2025, 5 event replay Maret–Mei.
- **S2-03/S2-04:** search, filter yield/frekuensi, sorting, simpan logika, kalender bulanan, detail lima tanggal, harga, dan watchlist tersedia. Browser berhasil menambahkan BBCA lalu menampilkan satu emiten di Watchlist. Detail BBCA menunjukkan declaration kosong serta tanggal cum/ex/record/payment asli.
- **S3-01/S3-02/S3-03/S3-04:** simulator Decimal, lot100, ledger hak dividen/kas/piutang, T+2 sesi dataset, empat aturan keluar, tiga alokasi, job API dan hasil persisten berjalan. Sepuluh uji kalkulasi serta satu uji alur API lulus. Browser menjalankan tiga emiten sampai hasil, termasuk BMRI terlewat karena modal belum tersedia. Worker thread lokal adalah bypass infrastruktur ISS-010.
- **S4-01/S4-03:** statistik 8 event BBCA, BEP harga/total, 3 event belum pulih pada t20, grafik harga/NAV, drawdown, capital lockup dan pembanding tampil. Angka ini statistik sampel, bukan model probabilitas.
- **S1-02 BYPASSED:** kontrak Pydantic/OpenAPI dan penyimpanan JSON SQLAlchemy berfungsi, tetapi schema kanonis terpisah/migrasi PostgreSQL belum diimplementasikan. Data sumber tetap snapshot read-only; bukan pemenuhan arsitektur storage final.
- Semua status DONE di atas berlaku pada baseline percakapan dan pemeriksaan development, bukan coverage PRD atau kelulusan UAT.

### Handoff kandidat lokal

Status: **IMPLEMENTED_BASELINE_WITH_BYPASSES**. 16 task DONE,2 BYPASSED,3 WAITING_INPUT,2 TODO. Aplikasi dapat didemonstrasikan berdasarkan percakapan. Belum READY_FOR_TESTING menurut definisi sprint karena PRD/user story belum dipetakan; belum DELIVERED/UAT.

Pemeriksaan terakhir:13 pytest lulus (1 peringatan deprecation upstream), lint/TypeScript/build produksi lulus. Browser membuktikan watchlist dan rules persisten, pencarian kosong, timeline/studi, kalender, tiga pembanding, ledger, dan validasi tanggal yang sesuai input. Tampilan390 px tidak memiliki overflow halaman. Bukti rinci di [VERIFICATION.md](./VERIFICATION.md).

### Sprint intelligence — 6 Oktober 2026

| Task | Status | Hasil dan bukti |
|---|---|---|
| I-01 | DONE | Protokol sebelum ekspansi, registry66 tools diperiksa,74 raw snapshots (9 actions/17 calendars/48 prices), manifest dan event-audit.csv. Rate limit429 dipulihkan dengan cache/jeda. |
| I-02 | DONE | Engine empirical-v1.0: entry0/5/10, horizon5/10/20, trap per horizon, Wilson, KM ties/censor/null median, diagnosis periode. Default43 lengkap/4 quarantine/1 early-censor. Sembilan uji engine baru lulus. |
| I-03 | DONE | FinancialLogic tersimpan: objective eksplisit, minimum sampel, maksimum upper bound Wilson, minimum median return. Browser membuktikan min100 menghasilkan0 ranking, tetap sama setelah reload; horizon5→44 lengkap lalu20→43. |
| I-04 | DONE | Analog stress test satu posisi: Decimal lot100, DPS hipotetis, harga path historis, future-analog cutoff, valuasi/piutang, P10/P50/P90, riwayat/versi SQLite. Browser memperbaiki tanggal invalid lalu menghasilkan8 analog BBCA. |
| I-05 | DONE | Build/lint/TypeScript dan22 pytest lulus; tautan detail→Intelligence emiten benar, riwayat terlihat setelah reload, desktop1280/mobile390 tanpa overflow halaman. Kontras sumbu grafik diperbaiki dan diverifikasi visual. Screenshot dan bukti API tersimpan; README/traceability/issues diperbarui. |

Hasil contoh **hipotetis** BBCA: modal100 juta, entry10.000, DPS250, valuation8 Des2026 sebelum payment10 Des2026;10.000 saham, piutang2,5 juta, median PnL sampel−247.419,30 dari8 analog. Bukan estimasi keuntungan masa depan. Input, hasil, versi dan ranking aktual disimpan di outputs/development/intelligence-api.json.

Model terlatih, forecast tanggal/rotasi forward, koreksi basis split, point-in-time financials, kalender resmi, PRD mapping dan UAT tetap belum selesai. Tidak menandai S4-02, S5-03 atau S6 selesai hanya karena fitur eksplorasi dapat dijalankan.


## Sprint integrasi rotasi selesai — 6 Oktober 2026

| Task | Status | Perubahan dan bukti |
|---|---|---|
| R-01 | DONE | UnifiedDataset menyatukan 12 event2025 dengan Intelligence;50 snapshot MCP baru,12 event lolos audit awal; empat gap IHSG diselesaikan dengan konsensus feed (ISS-029). Data di outputs/rotation; fingerprint unified-b749e08ddb769800. |
| R-02 | DONE | Screening memotong seluruh event/bar sebelum tanggal keputusan;3 heuristik kandidat dibekukan sebelum replay; evidence IDs/cutoff/aturan/alasan persist. Future-price7× tidak mengubah ranking/rute. Declaration/vintage tetap gap ISS-030. |
| R-03 | DONE | Engine v2: beberapa lot/event per issuer, hak untuk dividen tambahan, batas payment/holding, T+2, modal/periode sama,3 alokasi per rute.32 pytest total lulus termasuk regresi kas dan API frozen plan. |
| R-04 | DONE | Peluang/Watchlist→cakupan emiten, Intelligence→salinan financial logic, plan→replay→riwayat. Browser menghasilkan3 rute/9 hasil, mode verified-only0rute, tanggal15Juni terkirim benar, riwayat pulih sesudah reload. Desktop1280/mobile390 diverifikasi; scrollWidth390=clientWidth390. |
| R-05 | DONE | Lint, TypeScript, webpack build,32pytest lulus; bukti API dan screenshot disimpan. README/TRACEABILITY/ISSUES diperbarui; PM_REVIEW.md berisi alur diskusi dan calon acceptance checks. Tidak menyatakan S5-03/S6 atau PRD/UAT selesai. |

Contoh replay yang diperiksa: modal100 juta,1Maret–30Juni2025, default min3sampel/entry5/t20/holding20/maks5event.6 kandidat lolos,3dikeluarkan; rute semua peluang BBCA→BBRI→LPPF→DMAS→RALS menghasilkan PnL gross rotasi Rp2.566.800 dengan satu event terlewat; drawdown−10,545%. Rute prioritas BBRI→ADRO masih mempunyai satu lot terbuka di bawah entry pada akhir periode. Ini hasil aktual historis bersyarat, bukan proyeksi.

Bukti: outputs/development/rotation-api.json, rotation-desktop.jpg, rotation-mobile.jpg; backend/tests/test_rotation.py dan test_rotation_api.py. Bug input tanggal dan status history diperbaiki (ISS-033/034). Versi snapshot/hasil lama tetap dipertahankan.


## Pemeriksaan kesiapan Q-01–Q-03 — 6 Oktober 2026

| Task | Status | Bukti |
|---|---|---|
| Q-01 | DONE | Script work/verify_mvp.py memeriksa1.620 kombinasi;0 kegagalan. Oracle hak memakai tanggal kepemilikan, bukan mengulang akumulasi ledger. outputs/development/mvp-readiness.json menyimpan dimensi dan versi. |
| Q-02 | DONE | Tombol per-event detail membawa ID benar ke simulator. Periode awal2025 eksplisit; sidebar tetap contoh manual. Return kas pecahan dihitung sebelum pembulatan; endpoint detail memfilter kind. Tanggal lintas tahun dan jumlah event/posisi dibeli diperjelas. ISS-035–038. |
| Q-03 | DONE |40pytest lulus, lint/typecheck/build lulus. Browser ADRODesember→simulator→hasil→reload/riwayat; mobile390tanpaoverflow, desktop1280, console bersih. TEST_MATRIX.md memisahkan PASSdeveloper dan WAITING_PM. |

Kasus handoff: ADROex30Des2025, modal100juta,entry5sebelumcum,exitcloseex,1–31Des2025.52.600saham padaRp1.900 dijualRp1.810; PnLsaham−4.734.000 +hakdividen7.634.364 =gross2.900.364. NAV102.900.364 terdiri dari kas60.000 +piutangjual95.206.000 +piutangdividen7.634.364. Settlement5Jan2026 danpayment15Jan2026 belum masukkas padaakhirreplay. Bukti readiness-case.json dan readiness-desktop.jpg/readiness-mobile.jpg.

Tidak ada panggilan provider baru, deployment, transaksi saham, atau pengubahan snapshot Sectors pada sprint pemeriksaan ini. Lampiran PRD/user story, model prediksi dan UAT tetap gap yang tercatat.

## Persiapan review pengguna — 6 Oktober 2026

| Task | Status | Hasil dan bukti |
|---|---|---|
| U-01 | DONE | Snapshot input/versi, status beda draf, salin eksplisit, identitas riwayat dan lihat semua. Lint/typecheck/build serta alur browser desktop/mobile lulus. API membuktikan hanya exit_rule berubah dan record asal identik. ISS-039. |
| U-02 | DONE | UAT_SESSION.md berisi kasus tetap, tiga tugas, acuan developer, dan lembar observasi kosong. Tautan lokal diperiksa. PM-01/04/07 tetap WAITING_PM; S6 belum ditandai selesai. |

Eksperimen terkontrol: salin run52c72d21 lalu ubah hanya exit_rule ex_close→price_bep menghasilkan rund049736a. Gross PnL keduanya Rp2.900.364, tetapi yang pertama mempunyai piutang penjualan Rp95.206.000 dan yang kedua masih memegang saham senilai Rp95.206.000. Modal/periode/event/entry/holding/alokasi sama. Hasil lama tetap identik dengan readiness-case.json. Hasil yang sama secara nominal tidak berarti konsekuensi kas/posisi sama.

Bukti: outputs/development/saved-input-comparison.json, saved-input-desktop.jpg, saved-input-mobile.jpg. Salinan input legacy replay-v1 mengambil awal periode dari hasil tersimpan (13 Maret2025), tanpa mengarang versi dataset yang tidak tercatat. Tidak ada perubahan engine finansial/provider pada tahap U ini; pemeriksaan backend40tes dan matriks1.620 tetap bukti Q sebelumnya, tidak diklaim dijalankan ulang.

## Demo LAN — 6 Oktober 2026

| Task | Status | Bukti |
|---|---|---|
| L-01 | DONE | Permintaan PM membuka akses teman satu jaringan. Script start:lan menjalankan frontend0.0.0.0:3000; backend tetap127.0.0.1:8000. lsof menunjukkan listener *:3000. GET halaman dan /api/catalog lewat10.64.50.225:3000 menghasilkan200; judul benar,9emiten/12event. README memuat cara menjalankan dan mengembalikan akses localhost. |

Pemeriksaan dilakukan dari komputer host melalui IP LAN; koneksi dari perangkat teman belum diamati. IP dapat berubah ketika jaringan/DHCP berubah. Tidak mengubah firewall/router atau mengekspos port8000. Seluruh pengguna LAN berbagi workspace lokal yang sama.

## Relokasi direktori — 7 Oktober 2026

**M-01: PARTIAL (salinan tujuan terverifikasi; folder asal masih ada).** Rename akar workspace bro→horizon ditolak sandbox, termasuk setelah izin write asal/tujuan diberikan. Workaround aman: salinan penuh ke `/Users/killerbie/Documents/Codex/horizon` tanpa menghapus sumber. Konfigurasi privat, database dan lockfile identik; 16 file path-dependent diperbarui (virtualenv dan dua skrip PDF). Skrip PDF kini memakai root relatif terhadap lokasinya. Python/pip/SQLite menunjuk horizon. Build Next webpack dan40pytest lulus (warning upstream lama ISS-016). Source dan artifact riset diverifikasi checksum; status UAT tidak berubah. Server3000/8000 tidak aktif saat pemeriksaan awal, sehingga tidak ada proses yang dipindahkan. Chat ini masih menunjuk workspace lama; gunakan horizon untuk pekerjaan selanjutnya. ISS-040 menjelaskan sisa relokasi.

## Publikasi GitHub — 7 Oktober 2026

**G-01: DONE.** Repo tujuan YohanesVito/horizon terverifikasi publik dan kosong melalui GitHub API. Git diinisialisasi pada direktori horizon, branch main. Pemeriksaan316 kandidat berkas tidak menemukan key Sectors yang tersimpan lokal (termasuk bentuk encoded) atau pola token/private-key umum. Env lokal, database runtime, node_modules, virtualenv dan build diabaikan Git; contoh env kosong serta snapshot yang diperlukan aplikasi ikut commit. Commit aplikasi `8260585` berhasil dipush ke origin/main dengan tracking aktif. Arsip dari commit diuji dalam direktori sementara tanpa env privat/database: startup API berhasil, health200, catalog200 dengan9emiten/12event. Build/40tes pada relokasi sebelumnya tetap bukti validasi kode yang sama, bukan pengujian yang diulang pada tahap publikasi. Enam berkas artifact sumber mempunyai whitespace bawaan; tidak diubah agar bukti sumber tetap utuh. Pemeriksaan whitespace kode aplikasi/config/docs development lulus. Git sempat terhalang DNS sandbox; push berhasil setelah izin jaringan diberikan. Status UAT dan sisa relokasi M-01 tetap terpisah.

## Overlay timeline — 7 Oktober 2026

T-07 DONE (checkpoint Git lokal). Implementasi timeline/chart, adapter API, snapshot sumber, dokumentasi dan bukti pemeriksaan disimpan pada branch `feat/chart` sesuai permintaan PM. Commit ini mencakup T-01–T-06; status gap data, model prediksi dan UAT tidak berubah. Pemeriksaan konten staged dan pengecualian kredensial dilakukan sebelum commit. Build/testing pada T-05/T-06 tetap bukti sebelumnya, tidak dijalankan ulang karena checkpoint tidak mengubah kode aplikasi.

T-06 DONE. Cum date, Ex date, Recording dan Payment ditampilkan langsung pada grafik dalam lajur agar tidak bertumpuk; posisi tanggal tetap akurat. Area/garis cum→ex memakai close aktual: negatif merah, positif hijau, nol netral; tanpa harga lengkap tidak ada warna arah. Mengikuti periode fokus dan mode Rp/%. Lint dan build (termasuk TypeScript) lulus. Pemeriksaan fungsi memakai histori LPPF2025 (−14,8989899%) serta variasi uji positif, nol dan missing; variasi uji tidak dimasukkan ke data aplikasi. Browser desktop1440 membuktikan empat label, area merah, perubahan fokus2025→2024 dan modeRp/%; mobile390 mempunyai scrollWidth390 dan label tidak bertumpuk. Log browser tanpa error/warning. Bukti `outputs/development/timeline-phase-labels-desktop.jpg` dan `timeline-phase-labels-mobile.jpg`. Frontend direstart memakai build baru. Tidak mengubah data atau engine prediksi; ISS-041/042 dan status UAT tetap berlaku.

T-01 PARTIAL. Diskusi perilaku dan audit kalender awal selesai; kelengkapan timeline per emiten belum terpenuhi. PM meminta satu emiten dengan overlay area per tahun, hover fokus, lima tahun dan hanya data lengkap. Rentang sementara2021–2025. Registry66tool MCP diverifikasi; lima kalenderREST2021melengkapi17snapshot2022–2025. Audit offline menemukan1.900event/477emiten,170kandidat lima tahun dengan field kalender terisi serta format/urutan tanggal dan DPS positif valid. Himpunan170kandidat sama dengan hasil MCP screener, pagination selesai. PilotLPPFmemiliki272bar dalam lima jendela event; tidak ada tanggal ganda/OHLC invalid dan ada bar pada cum/ex/record/payment kelima tahun. Declaration, seluruh sesi harga, siklus final/interim dan adjustment belum terverifikasi; belum ada emiten dinyatakan lengkap. NewsBBCA2021/2025dengan keyworddividen kosong, tidak digeneralisasi sebagai seluruh feed kosong. Temuan dan langkah berikutnya di TIMELINE_OVERLAY_RESEARCH.md, coverage.csv/json, pilot-LPPF.json dan ISS-041. UI/katalog lama tidak berubah; build/testing aplikasi/UAT tidak diklaim dijalankan pada tahap riset ini.

T-02 DONE (pencatatan spesifikasi saja). Arahan PM terbaru: periode berjalan mempunyai prediksi; perhitungannya dibahas nanti. TIMELINE_OVERLAY_RESEARCH.md kini memuat pemisahan aktual/prediksi, batas tanggal data aktual terakhir, hover status, jadwal terkonfirmasi yang tetap terkonfirmasi, serta placeholder sebelum engine tersedia. Syarat histori lengkap tetap berlaku; masa depan tidak diperlakukan sebagai missing histori. Tidak menetapkan jumlah tahun baru, membuat angka prediksi, mengambil data tambahan atau mengubah website. Engine DEFERRED di ISS-042; T-01 dan UAT tetap pada status sebelumnya.

## Membuka preview untuk PM — 7 Oktober 2026

T-03/T-04/T-05 IN_PROGRESS. PM meminta implementasi overlay. Katalog baru tetap mensyaratkan histori lengkap; pratinjau desain dengan data LPPF yang belum memenuhi syarat dipisahkan dan diberi label. Lima tahun histori2021–2025dipertahankan;2026menjadi lapisan tambahan aktual/prediksi. Harga dan kalender2026diambil melalui MCP+REST Sectors; perhitungan prediksi tetap ditunda. Untuk menjaga jarak waktu saat kalender sesi belum tervalidasi, sumbu x tahap ini memakai hari kalender relatif terhadap ex-date dengan label eksplisit.

T-03 DONE (implementasi API/gate dan pratinjau, bukan kelengkapan dataset). Snapshot MCP+REST2026menambah123bar hingga6Oktober2026; histori272bar/lima periode. API menyediakan katalog ketat dan pratinjau eksplisit dengan provenance/gap. Forecast tetap kosong. T-01/ISS-041 tetap parsial/open.

T-04 DONE (UI). Menu Timeline, lima overlay area transparan, hover/tooltip, fokus tahun terkunci, tombol keyboard, modeRp/%, enam marker fase dan tabel harga tersedia. Tahun berjalan aktual terpisah dari panel prediksi belum tersedia. Pratinjau diberi banner; katalog eligible tidak memasukkan data yang belum lengkap.

T-05 DONE (pemeriksaan developer).46pytestlulus, lint/typecheck/build lulus, API200/404/422sesuai gate, browserdesktop1440danmobile390diperiksa. Perbaikan overflowmobile408→390terverifikasi; log browser terakhir tanpa error/warning. Screenshot dan `timeline-verification.json` tersimpan; keyscan source/frontendbundle/artifacttimeline tidak menemukan key tersimpan. Detail dan runbook di TIMELINE_IMPLEMENTATION.md. Server3000/8000direstart memakai build terbaru, pratinjau ditinggalkan terbuka. Tidak mengklaim forecast, seluruh emiten lengkap, UAT atau delivery final.

L-02 DONE (menjalankan aplikasi yang tersedia; C-01/C-08). Server dimulai dari horizon: FastAPI127.0.0.1:8000 dan frontend melalui `bun run start:lan` di port3000, memakai build yang sudah ada karena tidak ada perubahan kode aplikasi. Browser dibuka ke http://127.0.0.1:3000/ dan ditinggalkan terbuka. Pemeriksaan proxy `/api/health` serta `/api/catalog` menghasilkanHTTP200,9emiten/12event dari snapshotSectors. DOM dan screenshot memperlihatkan halaman Peluang serta grafik BBCA2025; log browser yang diperiksa tidak memuat error/warning. Overlay lima tahun dan prediksi tetap spesifikasi T-01/T-02, belum implementasi. Tidak menjalankan ulang build, simulasi, atau UAT pada tahap membuka preview ini.

## Feedback UI dan setup lokal — 7 Oktober 2026

**UX-01: DONE (C-04/C-05/C-08, S5-02; pemeriksaan development).** Copy halaman/form menjelaskan alur dengan bahasa Indonesia dan mempertahankan asal historis/asumsi/gross. Strategi utama Simulator memakai tiga kartu radio dengan penjelasan all-in pertama, bagi rata per event, dan rotasi kas/T+2. Input uang di Simulator, planner dan skenario Intelligence menampilkan pemisah ribuan Indonesia; nilai FormData/API tetap angka tanpa pemisah, desimal memakai koma pada tampilan. API/engine/sumber snapshot tidak diganti.

Browser production pada `http://localhost:3000` memakai FastAPI asli dan snapshot Sectors lokal, tanpa mock/provider request baru. Mengetik `100000000` menampilkan `100.000.000`; paste `50.000.000` menghasilkan POST Simulator `capital:50000000` dan planner `capital:"50000000"`. Tiga simulasi berstatus completed, input/primary allocation masing-masing single/equal/rotation dan compare=true tetap memberi tiga alternatif. Hasilnya tersimpan dan dibaca kembali lewat API. Skenario menerima modal `50.000.000,25`, harga `10.000,5` dan DPS `0,125` sebagai `50000000.25`/`10000.5`/`0.125`, tersimpan di history. Required, minimum, maksimum, step bulat, karakter invalid dan paste notasi ilmiah menghalangi POST; edit tengah/caret dan backspace melewati separator diuji. Salin hasil mengembalikan modal dan menghapus error paste bahkan ketika nilai angka sama (ISS-052). Space/ArrowRight memilih tiga radio; screenshot dan DOM Simulator/planner/Intelligence pada1440/390 menunjukkan scrollWidth sama dengan viewport.

Pengukuran cache browser pada jendela1,484detik: GET BBCA tetap1 sesudah dua pembukaan detail; GET timeline LPPF tetap1 setelah fokus tahun, Rp/%, dan hover. Cache staleTime60detik tetap konfigurasi lama; bukan janji tidak ada refetch setelah stale/remount. Kontrol timeframe/zoom belum diimplementasikan dan tidak diuji. Tidak mengklaim optimasi cache baru.

`npm run lint`, `npm run typecheck` dan `npm run build` lulus. Browser production tanpa pageerror atau warning; favicon404 tetap issue kosmetik ISS-053. Bukti dan skrip ulang: [ui-feedback-verification.json](../../outputs/development/ui-feedback-verification.json), [verify_ui_feedback.cjs](../../work/verify_ui_feedback.cjs), screenshot [desktop](../../outputs/development/ui-feedback-simulator-1440.png)/[mobile](../../outputs/development/ui-feedback-simulator-390.png). Skrip membutuhkan Playwright/Chromium; instalasi pemeriksaan tersedia di `/tmp/horizon-ui-check/node_modules` (contoh command di header skrip).

Setup lokal memakai npm dan uv managed Python3.12 karena Python sistem gagal ensurepip dengan `pyexpat`/`libexpat`. Venv terisolasi `.runtime/ui-feedback-venv` dan dependencies lock berhasil; tidak mengganti Python global. README memuat command setup/restart. Backend127.0.0.1:8000 dan frontend production127.0.0.1:3000 ditinggalkan berjalan; proxy localhost health200/catalog200 (9emiten/12event). Pemeriksaan ini bukan UAT, coverage PRD final atau persetujuan delivery. Gap timeline/prediksi yang sudah tercatat tetap berlaku.

**UX-02: DONE (C-02/C-06/C-08, S5-02; pemeriksaan development).** Klik langsung di plot Timeline kini mengunci tahun terdekat, bersama garis/fase dan “Jejak dividen”. Klik kedua di plot melepas kunci sesuai arahan terbaru PM. Tombol tahun tetap memilih/toggle fokus; “Bandingkan semua” tetap reset. Hit-test yang sama dipakai untuk hover/click; klik di luar area plot diabaikan. Feedback label ticker tetap ditunda, tidak termasuk perubahan ini.

Baseline production sebelum perubahan: hover pada node SVG2024 lalu2025 mengubah fokus, tetapi klik2024 diikuti hover2025 tidak mengunci. Sesudah perubahan, browser desktop1440 dan mobile390 dengan touch emulation memakai koordinat dari node `path` SVG aktual LPPF (bukan posisi perkiraan). Klik/tap2024 mengunci2024; pindah ke garis2025 tetap menampilkan Jejak2024 dan tooltip2024. Tooltip cocok dengan snapshot API: desktop5Apr2024/Rp1.870 dan mobile2Mei2024/Rp1.570. Pointer leave mempertahankan kunci/Jejak dan menghilangkan tooltip. Klik/tap kedua melepas kunci, menghilangkan tooltip dan mengembalikan opacity kelima seri ke1; hover berikutnya menampilkan Jejak2025. Tap pertama mobile diuji tanpa hover sebelumnya. Tombol2023 mengunci; Enter melepas2023, Space mengunci2022; reset mengembalikan hover bebas. Klik di luar plot tidak mengunci. Kedua viewport memiliki scrollWidth sama dengan1440/390; tidak ada pageerror.

Build production terbaru (termasuk pemeriksaan TypeScript) lulus dan frontend direstart; backend snapshot tetap berjalan. Bukti: [baseline](../../outputs/development/timeline-pin-baseline.json), [hasil toggle terakhir](../../outputs/development/timeline-pin-verification.json), [skrip ulang](../../work/verify_timeline_pin.cjs), screenshot [desktop](../../outputs/development/timeline-pin-1440.png)/[mobile](../../outputs/development/timeline-pin-390.png). Tidak mengambil data provider baru, mengubah metode/data timeline, atau mengklaim perangkat fisik/UAT. Batas pratinjau dan prediksi ISS-041/042 tetap berlaku.

**UX-03: DONE (C-04/C-08, S5-02; pemeriksaan development).** Modal awal Simulator kini benar-benar kosong pada draf baru, dengan placeholder “Masukkan modal”. Label dan input nominal diperbesar khusus Simulator: computed label11→14px, input12→24px dan tinggi43,1875→64,390625px. Label event historis tetap dipertahankan sesuai arahan PM; modal awal planner/skenario tidak berubah.

Browser production desktop1440/mobile390 membuktikan form baru kosong dan native required menolak submit tanpa POST. Mengetik `50000000` menghasilkan `50.000.000`, POST angka `capital:50000000` dan hasil completed dengan modal tersimpan50juta. Membuka hasil lama lalu menyalin input mengisi nominal asli; paste invalid `1e8` kemudian salin nilai yang sama kembali valid/messagekosong. Navigasi keluar→Simulator dan detailBBCA→Simulator membuat draf modal kosong; handoff detail tetap memilih satu eventBBCA. Planner dan skenario Intelligence tetap menampilkan100.000.000. Kedua viewport tidak overflow (scrollWidth1440/390), tanpa pageerror. Build production terbaru (termasuk TypeScript) lulus; frontend direstart dan health proxy200. Bukti [baseline ukuran/nilai](../../outputs/development/simulator-capital-baseline.json), [hasil browser/API](../../outputs/development/simulator-capital-verification.json), [skrip ulang](../../work/verify_simulator_capital.cjs), screenshot [desktop](../../outputs/development/simulator-capital-1440.png)/[mobile](../../outputs/development/simulator-capital-390.png). Backend/data/engine tetap memakai snapshot lokal; bukan UAT/perangkat fisik atau coverage PRD final.

**UX-04: DONE (C-02/C-04/C-05/C-06/C-08, S5-02; pemeriksaan development).** Istilah hari perdagangan pada UI dan pesan backend kini “hari bursa”, menggantikan “sesi”. Label entry/batas pengamatan, satuan pemulihan, metodologi, asumsi, ledger, alasan trade/eligibility dan error diperbarui. Identifier/API seperti `max_holding_sessions`/`entry_sessions_before_cum` tetap dipakai; hitungan tidak diubah. Sumbu Timeline H tetap hari kalender. Prosa hasil lama dinormalisasi hanya saat ditampilkan, tanpa menulis ulang snapshot/database/record hasil.

Browser production memeriksa Simulator, planner, Intelligence, Metodologi, detailBBCA, Timeline dan hasil lama: DOM/accessible label tidak memuat “sesi”; contoh yang terlihat adalah “5 hari bursa sebelumnya”, “Pulih ≤20 hari bursa” dan “T+2 hari bursa”. Timeline tetap menyebut “Hari kalender relatif terhadap ex-date”. Simulasi baru50juta dengan exit holding_period selesai; respons asli backend memuat “Batas hari bursa pengamatan”, “close hari bursa masuk” dan “open hari bursa berikutnya”. Skenario baru juga memuat “Kuantil/kurva per hari bursa” dan “jumlah hari bursa menurut kalender BEI”. Hasil lama edb55364 masih mempunyai prosa “sesi” pada respons API, tetapi ditampilkan sebagai “hari bursa”; respons sebelum/sesudah identik. Tidak ada pageerror. Inventaris source src/backend tidak menemukan istilah lama di prosa statis; formatter khusus mempertahankan kompatibilitas teks lama. Build terbaru (termasuk TypeScript) lulus; frontend dan backend direstart memakai source final. Bukti ringkas: [trading-day-wording-verification.json](../../outputs/development/trading-day-wording-verification.json). Pemeriksaan ini bukan UAT atau pengujian ulang seluruh kalkulasi.

## Fokus navigasi demo — 7 Oktober 2026

**D-01 DONE pada scope navigasi/landing (instruksi PM terbaru; C-02/C-08; S5-02).** Halaman awal kini Analisis emiten; navigasi utama hanya Analisis emiten dan Simulator. Peluang, Kalender, Intelligence, Rencana rotasi, Watchlist dan halaman Metodologi tidak dihapus; metodologi tersedia dari tautan sekunder. Pratinjau LPPF langsung terbuka dengan label belum lolos verifikasi, tanpa kartu angka nol yang menunda chart. Judul halaman dan metadata mengikuti fokus dividen. File aplikasi: `src/components/dashboard.tsx`, `src/components/dividend-timeline.tsx`, `src/app/layout.tsx`.

Pemeriksaan aktual sebelum sinkronisasi Sammy: `npm run lint`, `npm run typecheck`, dan `npm run build` lulus. Browser lokal viewport362px memperlihatkan hanya dua item navigasi, LPPF terpilih dengan label pratinjau, chart histori dimuat, perpindahan Simulator→Analisis dan tautan Metodologi→Analisis berfungsi; lebar dokumen347px pada viewport362px (tanpa overflow horizontal). Belum menjalankan UAT atau mengubah perhitungan/data. Simulator masih default multi-event dan belum mengikuti emiten dari chart (ISS-054); kelengkapan LPPF dan forecast tetap ISS-041/042. Tidak ada commit/push.

## Integrasi pekerjaan PM dan Sammy — 7 Oktober 2026

**D-02 DONE (integrasi lokal; C-02/C-04/C-08).** Branch PM `feat/timeline-ui-polish` di-fast-forward dari `9cc1c81` ke commit Sammy `9fdf32b` pada `origin/feat/chart-sammy`, lalu perubahan D-01 yang belum di-commit diterapkan kembali. Arah navigasi dua menu, landing Analisis emiten, dan pratinjau LPPF berasal dari feedback PM dan pekerjaan D-01; interaksi klik/tap untuk mengunci tahun chart, perbaikan input modal/strategi Simulator, serta istilah “hari bursa” berasal dari pekerjaan Sammy UX-01–UX-04. Konflik dashboard dan dokumentasi diselesaikan dengan mempertahankan kedua kontribusi. Nomor issue handoff Simulator dari D-01 menjadi ISS-054 agar ISS-052/045 milik branch Sammy tetap utuh.

Sesudah integrasi, `npm run lint`, `npm run typecheck`, `npm run build`, dan 46 tes backend lulus (satu warning deprecation Starlette yang sudah ada). Browser lokal memastikan dua menu dan landing LPPF, klik chart mengunci/melepas tahun, modal Simulator kosong lalu terformat `50.000.000`, tautan Metodologi berfungsi, serta tidak ada overflow horizontal pada viewport 362px. Ini pemeriksaan integrasi, bukan UAT atau validasi data/prediksi. HEAD branch sama dengan commit Sammy; perubahan D-01 dan dokumentasi masih lokal/uncommitted. Tidak ada commit atau push baru; snapshot stash integrasi disimpan sebagai cadangan pemulihan.
