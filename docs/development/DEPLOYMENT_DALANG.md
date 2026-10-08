# Deployment backend Horizon ke Dalang

Status **8 Oktober 2026 WITA: DEP-01–DEP-04 DONE pada scope deployment backend dan verifikasi alur produksi**. FastAPI berjalan dalam Docker di VPS Dalang, database tetap Supabase, dan frontend Vercel membaca API baru. UAT final belum dilakukan.

## Rilis aktif setelah DEP-04

- Release `20261008T053018Z-8544ed8b61`, source SHA-256 `8544ed8b6115c4e90c3df9207cfe82b0274688745b180a9aa22e6ea4a8df3d50`, image `sha256:adf13f074124e53ea7282b8cabe66d545e84b4eb3f1a8116a6124343905ab603`. Paket allowlist 213 file, tanpa secret dan tanpa perubahan source yang belum di-commit; manifest `git_head` `24162d8` memuat `main` `a20d32c`.
- `/opt/horizon/current` menunjuk release ini; `/opt/horizon/deployment.json` menyimpan metadata aktif. Release sebelumnya `20261007T125050Z-f062081aa6` tetap tersedia untuk rollback.
- Verifikasi 8 Oktober: image smoke dan lima preview kandidat lulus; `https://horizon-dividend.vercel.app` menampilkan DMAS, LPPF, ADRO, CFIN, RALS, dengan 5/5/9/2/4 peristiwa historis. Panel risiko LPPF menampilkan 4 event lengkap dan 75% hasil gross negatif sebagai statistik eksploratif. Browser membuktikan pergantian grafik ke DMAS.
- Verifier HTTPS→API→worker→Supabase lulus memakai fixture `readiness-case-timeline-ui.json`: akses tanpa key ditolak, replay identik, probe sementara dihapus, checksum 20 record awal terjaga. Snapshot 06:54 UTC menunjukkan container running/healthy/restart 0, lima layanan kurasi inactive/PID 0. Bukti lokal: `outputs/deployment/deployment.json`, `live-editorial-verification.json`, `dalang-api-verification.json`.
- Build dan cutover berjalan lambat karena tekanan I/O VPS hingga sekitar 98% full pada beberapa interval. Akar masalah ISS-048 masih terbuka; jangan reboot tanpa mempertimbangkan autostart lima unit kurasi. Rilis baru bukan UAT atau prediksi numerik.

## Rilis awal 7 Oktober (arsip)

- Backend: https://10e0ff54-f828-44de-a965-5671328a08d3.svc.dalang.io
- Public health: `/api/health`; data, mutation dan OpenAPI membutuhkan key antarlayanan.
- VPS `hyperliquid-engine`, ID `10e0ff54-f828-44de-a965-5671328a08d3`, hostname `vps-10e0ff54`; Ubuntu24.04.4, 2vCPU, RAM2048MB, disk10GB.
- Docker Engine29.8.2, containerd2.3.6, Compose5.6.0. Container `horizon-api-1` terverifikasi healthy, restart_count0.
- Release `20261007T125050Z-f062081aa6`;211file, SHA sumber `f062081aa6e849a672ac3d7c0fde754b71ac2b6c27b93dadf25c860a13f92937`.
- Image `sha256:4cec0602445d515db19c1d8d1e76d0ca4b49bca6029a51fa71ec393eb4002099`.
- Release awal terpasang `/opt/horizon/releases/20261007T125050Z-f062081aa6`; pointer `/opt/horizon/current` dan metadata `/opt/horizon/deployment.json` menunjuk ke rilis ini pada saat deployment awal, sebelum DEP-04.
- Ini snapshot working tree termasuk perubahan belum di-commit, bukan klaim remote Git sudah memuat release.
- Kelima layanan kurasi tetap inactive/PID0; konfigurasi/data tidak diubah. Enabled state saat boot tetap aktif. Jangan reboot untuk mencoba mengatasi I/O tanpa mempertimbangkan autostart tersebut. [Runbook pemulihan kurasi](./DALANG_SERVICE_PAUSE.md).

## Alur dan konfigurasi

Browser → Next.js `/api/*` → HTTPS provider → satu proses FastAPI dalam Docker → Supabase PostgreSQL melalui Session Pooler.

Next.js menyisipkan bearer key dari environment server; browser tidak menerima key tersebut. `.env.local` lokal memakai BACKEND_URL origin HTTPS di atas dan HORIZON_API_KEY yang sama dengan backend. Tanpa awalan NEXT_PUBLIC. Jalankan frontend dengan `bun run start:lan` setelah production build. FastAPI lokal8000 sudah dihentikan; jangan menjalankan backend kedua pada database yang sama.

Runtime env VPS di `/opt/horizon/shared/backend.env`, mode600 dalam direktori root-only. Isinya hanya DATABASE_URL role `horizon_app` dan HORIZON_API_KEY. Compose mewajibkan `HORIZON_REQUIRE_API_KEY=1`. Admin/migration credentials, Supabase secret key dan Sectors key tidak dikirim ke VPS atau image.

Session Pooler disalin dari dialog Connect proyek Supabase, host `aws-0-ap-southeast-2.pooler.supabase.com`, port5432; username runtime `horizon_app.edapqawssqjwcrqllpco`. Password runtime tetap sama dan tidak dicetak. Direct database hostname hanya menyediakan IPv6 yang tidak terjangkau container. Jangan memakai transaction pooler6543 karena worker memakai advisory lock sesi. TLS client→pooler diperiksa melalui libpq; `pg_stat_ssl` pada koneksi internal pooler→database berbeda dan tidak membuktikan TLS client. [Dokumentasi resmi koneksi Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres).

API key ini autentikasi antarlayanan, bukan login/isolasi pengguna. Frontend publik tetap mempunyai gap akses pengguna ISS-009. Snapshot Sectors disertakan sebagai data riset immutable; deployment ini tidak mengambil data pasar live baru. Worker tetap thread dalam proses, belum durable queue (ISS-010). Hasil simulasi di luar biaya transaksi, pajak dan slippage.

## Batas container

`deploy/compose.yaml` menjalankan satu Uvicorn worker, non-root `horizon`, root filesystem read-only, tmpfs runtime sementara, RAM768MB, CPU1,5, PID128, capabilities dilepas, no-new-privileges, log rotation dan restart policy unless-stopped. Host port80 diteruskan ke container8000; HTTPS diterminasi provider. Database tidak berada dalam volume Docker.

## Masalah yang ditemukan dan ditangani

- ISS-047 RESOLVED: sudo half-configured/trigger libc-bin tertunda diperbaiki memakai `dpkg --force-confold --configure --pending`, tanpa full OS upgrade/reboot.
- ISS-049 RESOLVED: container timeout ke PyPI; uplink VPS MTU1442 berbeda dari bridge1500. `deploy/configure-docker-network.sh` mempertahankan opsi daemon lain, memvalidasi config dan menyamakan MTU bridge/default bridge1442. Uji HTTPS dari container serta retry build berhasil.
- ISS-050 RESOLVED: startup database gagal Network is unreachable melalui IPv6. Pindah ke Session Pooler resmi dengan role terbatas; API→worker→Supabase lulus.
- **ISS-048 OPEN:** waktu tunggu storage sekitar89–95% selama install/build/recreate. Setelah startup, snapshot terbaru full avg10=5,88% dan avg60=14,19%; ini tidak membuktikan akar masalah pulih. Root cause host/provider belum diketahui. Jangan memaksa kill dpkg, menghapus lock atau menonaktifkan fsync. Tidak ada pesan support dikirim, addon dibeli, atau VPS direprovision.

## Bukti pemeriksaan

Semua file bukti berada di `outputs/deployment/`:

- `build-result.json`, `docker-build.log`: checksum211file, build dan smoke aplikasi terkemas (health/catalog/intelligence/timeline/preview) lulus memakai SQLite disposable, tanpa menyentuh Supabase.
- `session-pooler-verification.json`: role runtime,20record dan TLS client.
- `start-result.json`, `runtime-verification.json`: container healthy/non-root/read-only, lima layanan kurasi inactive, kapasitas disk dan tekanan I/O.
- `dalang-api-verification.json`: HTTPS health PostgreSQL200; tanpa key/key salah ditolak401 untuk baca/tulis; delapan endpoint200; replay API→worker→Supabase sama persis dengan fixture lokal. Probe selesai dihapus dan checksum20record lama tetap sama.
- Replay historis ADRO: modalRp100juta, grossPnLRp2.900.364 dan endingNAVRp102.900.364; di luar biaya/pajak/slippage, bukan prediksi atau keuntungan aktual.
- `frontend-proxy-verification.json`: health/catalog/timeline/riwayat melalui Next lokal200/no-store, tidak ada key pada respons, backend lokal8000 tidak berjalan.
- `browser-verification.json`: reload Peluang menampilkan9emiten/12event; Timeline dan pratinjau LPPF2021–2025 terbuka; console error/warning kosong. Katalog timeline masih0emiten lengkap dari170kandidat karena gap data yang sudah ada.
- `local-verification.json`:60pytest,7pemeriksaan proxy, lint/TypeScript/production build;83asset browser tanpa secret. Dijalankan pada tahap packaging sebelumnya, tidak diklaim sebagai pengujian ulang setelah perubahan env.
- `deployment.json`: release, image, status dan batas delivery akhir.

Pemeriksaan ini merupakan development verification; tidak menggantikan UAT/acceptance PM atau coverage PRD/user story yang lampirannya belum tersedia.

## Operasi dan update

Gunakan CLI Dalang yang sudah terautentikasi. Jangan mencetak isi env, expanded `docker compose config` atau `docker inspect` penuh. Untuk status tanpa secret:

```sh
dalang exec hyperliquid-engine 'docker ps --filter name=horizon-api-1 --format "{{.Names}} {{.Status}}"'
dalang exec hyperliquid-engine 'python3 /opt/horizon/inspect-runtime.py'
dalang scp hyperliquid-engine:/opt/horizon/runtime-verification.json /private/tmp/horizon-runtime.json
```

`dalang exec` memakai sesi tmux dan dapat mengembalikan output parsial sebelum perintah panjang selesai. Jalankan operasi panjang melalui systemd-run --no-block, simpan output ke log, lalu verifikasi file hasil melalui scp. Return code CLI saja bukan bukti deployment selesai.

Untuk release berikutnya:

1. Jalankan pemeriksaan aplikasi yang relevan, lalu `.venv/bin/python work/build_backend_release.py`. Arsip allowlist dan manifest berada di `.runtime/deploy/RELEASE/`; helper memeriksa nilai secret sebelum membuat arsip.
2. Upload arsip ke `/opt/horizon/releases/RELEASE.tar.gz`; build menggunakan `/opt/horizon/build-release.sh RELEASE` melalui transient unit. Build script memverifikasi checksum dan menjalankan smoke aplikasi disposable. Pastikan `build-result.json` passed.
3. Pastikan tidak ada job queued/running. Hentikan API lama secara graceful, maksimal75detik; jangan menjalankan dua backend pada database yang sama.
4. Jalankan `/opt/horizon/activate-release.sh RELEASE` lewat transient unit. Compose menunggu healthy. Jangan ubah pointer current sebelum verifikasi selesai.
5. Jalankan verifier dari repo lokal:

```sh
PYTHONPATH=. .venv/bin/python work/verify_dalang_deployment.py https://10e0ff54-f828-44de-a965-5671328a08d3.svc.dalang.io
```

Verifier memakai key lokal, menjalankan satu replay sementara, membandingkan fixture, membersihkan probe yang selesai, serta memeriksa checksum record sebelumnya. Jalankan saat tidak ada perubahan pengguna bersamaan agar checksum dapat dibandingkan.

Untuk release backend yang sudah menyertakan `feat/timeline-ui-polish`, tambahkan `--fixture outputs/development/readiness-case-timeline-ui.json`. Default `readiness-case.json` tetap untuk release Dalang awal. Fixture baru hanya mengubah 12 field prosa sesi→hari bursa yang sudah ditinjau; pemeriksaan result tetap kesamaan JSON penuh. Snapshot lama tidak ditulis ulang. Deployment frontend dapat memakai backend Dalang awal karena kontrak dan hitungan sama; formatter UI menangani prosa lama.

6. Verifikasi frontend→proxy→API, lalu arahkan `/opt/horizon/current` ke release baru dan simpan metadata/bukti. Pertahankan image/manifest sebelumnya untuk rollback.

## Stop, start dan rollback

Perintah berikut hanya dijalankan ketika diperlukan; layanan kurasi tidak termasuk:

```sh
# Hentikan API secara graceful.
dalang exec hyperliquid-engine 'docker compose --env-file /opt/horizon/current/release.env -f /opt/horizon/current/deploy/compose.yaml stop --timeout 75 api'
# Mulai kembali release yang sama.
dalang exec hyperliquid-engine 'docker compose --env-file /opt/horizon/current/release.env -f /opt/horizon/current/deploy/compose.yaml up -d --wait --wait-timeout 120'
```

Untuk rollback image, hentikan API saat ini, jalankan Compose dengan path release sebelumnya yang telah diverifikasi, ulangi health/API smoke, lalu ubah pointer current. Tidak perlu migrasi ulang atau menghapus data Supabase.

Fallback lokal: hentikan container VPS terlebih dahulu dan pastikan tidak lagi berjalan, ubah BACKEND_URL lokal ke `http://127.0.0.1:8000`, jalankan `.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`, lalu restart frontend. HORIZON_API_KEY tetap sama. Kunci sesi database mencegah dua worker aktif; jangan menghapus perlindungan ini untuk memaksa startup.
