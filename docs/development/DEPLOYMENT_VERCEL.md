# Deployment frontend Horizon ke Vercel

Status 8 Oktober 2026: integrasi kode sudah di-push pada `feat/supabase-migration`, build lokal dan build cloud berhasil. **Belum ada frontend cloud yang berfungsi end-to-end.** Pengiriman environment menunggu izin eksplisit PM karena automatic approval review menolak secret + tujuan yang belum disetujui secara eksplisit. `main` belum diubah.

## Target yang telah diverifikasi

- Scope: `vitos-projects-c7162407` (Vito's projects).
- Project: `horizon`, ID `prj_1fNZpwZUGVCZTEIkP1GRUsodrJZc`.
- Git: `https://github.com/YohanesVito/horizon.git`. Git integration Vercel belum dihubungkan.
- Konfigurasi Next: `vercel.json`, Bun frozen lockfile, build Webpack.
- Frontend lokal: `bun run start:lan` pada port3000, memakai FastAPI HTTPS Dalang dan Supabase melalui proxy server.
- `.vercel/` diabaikan Git. `.vercelignore` mengecualikan `.env*`, backend, runtime, riset dan output dari unggahan frontend. Upload cloud teramati hanya42file/670,7KB.

## Environment yang diperlukan

| Nama | Environment | Jenis | Fungsi |
|---|---|---|---|
| BACKEND_URL | Preview dan Production | Config server | Origin HTTPS FastAPI Dalang |
| HORIZON_API_KEY | Preview dan Production | Secret server | Key yang sama dengan backend Dalang |

Jangan beri prefix NEXT_PUBLIC. Tidak perlu DATABASE_URL, password PostgreSQL, Sectors key atau Supabase secret pada frontend Vercel. Nilai tersimpan lokal tidak dicetak ke log atau command arguments. Setelah izin eksplisit, masukkan lewat stdin privat atau dashboard project. Jangan menjalankan `env pull .env.local --yes` yang dapat mengganti konfigurasi lokal dengan environment cloud yang belum lengkap.

## Melanjutkan setelah izin environment

1. Verifikasi project dari direktori repo: `bunx vercel project inspect --scope vitos-projects-c7162407 --non-interactive`.
2. Pasang dua environment di atas. CLI62.7.0 menerima target `production,preview`; gunakan stdin, `--sensitive` untuk key dan `--no-sensitive` untuk URL. Jangan memakai `--value` dengan secret.
3. Deploy branch integrasi dengan `bunx vercel deploy --target preview --scope vitos-projects-c7162407 --non-interactive --yes`. **Periksa target aktual dari respons/inspect**, jangan menganggap flag berarti sudah Preview. `--skip-domain` hanya berlaku untuk target Production, bukan Preview.
4. Bila platform memperlakukan deployment pertama sebagai Production, jangan mengklaim Preview lulus atau meneruskan main. Gunakan deployment staging tanpa pemasangan domain untuk pemeriksaan, atau konfigurasi Git Preview yang terverifikasi. Jangan mematikan Deployment Protection; gunakan `vercel curl` atau sesi browser yang berhak.
5. Uji browser → Next proxy → VPS → Supabase: health PostgreSQL, catalog/intelligence/timeline/LPPF, history, input modal, simulasi terkontrol dan hasil. Hasil tetap gross di luar biaya/pajak/slippage. Perubahan record asli harus terjaga; probe hanya dibersihkan ketika selesai.
6. Sesudah pemeriksaan lulus, fetch ulang, merge branch integrasi ke main tanpa force push, lalu hubungkan Git pada project yang benar dan verifikasi Production Branch=main. Deploy/review production dari commit main dan simpan URL/commit/evidence. Jangan menganggap build READY membuktikan API berfungsi.

## Bukti dan kendala tahap ini

Integrasi: `outputs/development/integration-verification.json`; build/lint/60backend tests/7proxy checks/strict fixture lulus. Browser lokal menunjukkan chart LPPF dan modal50.000.000 dengan console bersih. Bukan UAT.

Build cloud deployment `dpl_Bo9H84eF3RZBp3owW2BCnCQjq9W8` berhasil memakai Next16.3.8, Bun1.3.14, Node24 dan machine basic2CPU/8GB. CLI meminta Preview tetapi deployment pertama diberi target Production oleh platform (ISS-056). Deployment kosong tersebut **sudah dihapus**, tanpa mengunggah environment atau mengubah data backend. Tidak ada URL cloud siap pakai yang diserahkan pada tahap ini. Perintah Preview dengan `--skip-domain` ditolak CLI sebelum deployment dibuat. Daftar env project terverifikasi kosong.

Automatic approval review untuk pengiriman key ditolak (ISS-055); izin PM sedang diminta. Koneksi MCP ke scope403, CLI resmi berhasil dengan akun yang sama. Tidak membeli paket/add-on atau menonaktifkan proteksi. Runtime FastAPI tetap release Dalang awal; perubahan backend UI hanya wording dan fixture baru siap untuk release berikutnya.

Gap produk tetap berlaku: data LPPF belum lolos syarat lengkap, forecast ditunda, pilihan emiten belum mengalir ke Simulator, workspace belum punya akun/isolasi pengguna. Pengujian developer atau deployment tidak menutup gap ini.
