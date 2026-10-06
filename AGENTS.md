# Panduan development proyek dividen

## Acuan dan prioritas

- Pengguna adalah PM. Kerjakan scope PRD dan user story terlebih dahulu. Instruksi terbaru pengguna mengungguli rencana atau proposal lama.
- Baca `docs/development/SPRINT_PLAN.md`, `TRACEABILITY.md`, `PROGRESS.md` dan `ISSUES.md` sebelum melanjutkan sprint. Jika PRD/user story belum tersedia, jangan mengaku sudah membaca atau menyelesaikan kesesuaiannya; lanjutkan pekerjaan independen yang berguna.
- Backend yang disepakati adalah FastAPI. Optimasi performa bukan fokus MVP saat ini.
- Sumber finansial adalah Sectors. MCP wajib dipakai dalam integrasi yang relevan; kalender dapat dilengkapi REST resmi Sectors seperti pada audit. Simpan API key di server, jangan tampilkan di log, dokumentasi, frontend atau commit.
- Eksekusi order dilakukan pengguna. Produk ini mendukung keputusan dan simulasi.
- Biaya transaksi, pajak dan slippage diabaikan pada versi awal sesuai arahan PM; label hasil selalu menyebut di luar biaya tersebut.
- BEP harga mengikuti harga beli pengguna, terpisah dari BEP total yang memperhitungkan dividen.

## Cara bekerja selama sprint

- Gunakan ID task dan kaitkan dengan requirement. Perbarui `PROGRESS.md` ketika status berubah; setiap pekerjaan selesai harus punya bukti dan hasil pemeriksaan yang benar-benar dijalankan.
- Catat bug, TODO, gap data dan blocker di `ISSUES.md` saat ditemukan. Bedakan penyebab yang terbukti dari hipotesis.
- PM mengizinkan bypass sementara agar development MVP tetap maju. Terapkan workaround dalam scope, catat dampak serta pekerjaan lanjutan, dan lanjutkan task independen tanpa meminta konfirmasi rutin.
- Jangan menghitung task `BYPASSED` sebagai `DONE`, menyembunyikan requirement yang belum dipenuhi, atau menampilkan data/model rekaan sebagai fakta. Gunakan label historis/skenario/estimasi/belum tersedia sesuai asal data.
- Tunda optimasi, refactor dan fitur di luar PRD yang tidak diperlukan untuk delivery. Tidak ada mandat multi-agent dalam panduan ini.
- Pertahankan skrip dan output riset yang sudah ada. Snapshot lama adalah bukti historis, bukan jaminan status pasar terkini.

## Pemeriksaan dan handoff

- Lakukan pemeriksaan development yang relevan seperti build, smoke API dan kebenaran kalkulasi saat perubahan memerlukannya. Jangan melaporkan pemeriksaan yang belum dijalankan sebagai lulus.
- Testing akhir, skenario UAT dan kriteria delivery akan dibahas dengan PM. Jangan mengarang persetujuan atau kelulusan testing akhir.
- Handoff mencakup cakupan PRD, cara menjalankan aplikasi, bukti alur utama, daftar issue/bypass, dan status siap testing. Aplikasi yang bisa dibuka belum otomatis berarti seluruh requirement selesai.

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
