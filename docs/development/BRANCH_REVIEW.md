# Review branch untuk Vercel — 8 Oktober 2026

## Pembaruan BR-03 — branch UI terbaru vs grafik parsial lokal

Bagian BR-01 di bawah adalah snapshot historis sebelum integrasi awal ke `main`; jangan gunakan hash atau rekomendasi deployment lamanya sebagai status terkini. Untuk BR-03, `git ls-remote` dan fetch 8 Oktober memverifikasi `origin/main` = `598e135` serta `origin/feat/timeline-ui-polish` = `dbf21b6`. Branch UI terbaru sudah memasukkan `main` melalui merge `dbf21b6` dan menambah redesain editorial `95ced66`. Working tree `main` masih memuat perubahan lokal D-03/F-01/T-08 yang belum di-commit; tidak ada merge atau checkout yang dilakukan pada repo aktif.

Salinan sementara dari `main` plus seluruh perubahan tracked/untracked lokal dipakai untuk `git merge --no-commit --no-ff dbf21b6`. Merge berhenti pada **empat konflik konten**: `src/components/dividend-timeline.tsx`, `src/app/globals.css`, `docs/development/PROGRESS.md`, dan `docs/development/SPRINT_PLAN.md`. `TRACEABILITY.md` auto-merge, tetapi isinya tetap perlu direkonsiliasi. Ini hasil dry run terhadap hash tersebut, bukan jaminan branch remote tidak akan berubah lagi. Salinan sementara berada di `/private/tmp/horizon-merge-audit.HbuMxA`; checkout aktif tetap pada `main` dan perubahan lokalnya tidak disentuh oleh simulasi.

| Area | Kontribusi lokal yang harus bertahan | Kontribusi branch UI yang harus bertahan | Risiko bila memilih satu sisi seluruh file |
|---|---|---|---|
| `dividend-timeline.tsx` | Lima kandidat, grafik parsial, gap tahun, event ganda dibedakan menurut ID/ex-date, tab 2026 hanya saat ada snapshot, provenance pratinjau | Hierarki editorial, toolbar/status bar, fokus keyboard, panel chart dan kronologi | Branch UI masih memakai fokus menurut `year` dan copy lima tahun/LPPF; event ADRO pada tahun sama tertukar atau kandidat menghilang |
| `globals.css` + `editorial.css` | Gaya kartu kandidat, catatan gap, keadaan disabled | Palet/hero/panel editorial dan layout responsif | CSS auto-merge sekalipun dapat menimpa warna/kontras atau menyembunyikan gap secara visual |
| Dokumen sprint | D-03 discovery dan T-08 grafik parsial beserta bukti 62 tes | D-03 UI hierarchy, D-04/D-05/D-07 dan bukti UI | ID `D-03` dipakai dua task berbeda; status atau bukti bisa keliru jika teks digabung begitu saja |

Urutan integrasi yang aman: (1) simpan perubahan lokal pada branch kerja tersendiri dengan commit yang hanya berisi file terpilih; periksa bahwa credential/runtime DB tidak ikut; (2) buat branch integrasi dari `main`, gabungkan hash UI yang sudah di-fetch, lalu gabungkan branch kerja lokal; (3) resolusi per komponen, bukan `accept ours/theirs` satu file; pakai kerangka visual UI terbaru sambil memindahkan logika kandidat/event-ID/gap/tab disabled dari T-08; (4) beri ID unik untuk task hierarki UI, misalnya `UI-03` dengan catatan asal `D-03`, dan pertahankan D-03 discovery; (5) jalankan tes backend, typecheck, lint, build, smoke lima endpoint, serta browser desktop/mobile untuk semua kandidat dan dua event ADRO 2024; (6) review diff final sebelum merge ke `main` atau push. Backend FastAPI/discovery dan snapshot Sectors lokal tidak berkonflik dengan branch UI pada dry run, tetapi tetap harus masuk commit integrasi. Jangan menafsirkan build hijau sebagai bukti semantik chart benar.

BR-03 adalah review saja. Belum ada resolusi konflik, build hasil gabungan, smoke browser hasil gabungan, commit, push, atau deployment.

Task BR-01: review yang diminta PM, terkait DEP-02/DEP-03 dan S5-02. Rekomendasi: **gabungkan perubahan deployment/Supabase lokal dengan feat/timeline-ui-polish, uji sebagai preview, lalu merge hasilnya ke main untuk production**. Tidak ada merge, commit, push atau deployment Vercel yang dilakukan pada review ini.

## Posisi branch yang diverifikasi dari GitHub

| Branch | Commit | Isi / keputusan |
|---|---|---|
| main | d3d64c7 | Baseline lama; belum chart maupun deployment terbaru. Target production setelah integrasi. |
| feat/chart | 9cc1c81 | Timeline dasar; sudah menjadi ancestor Sammy dan polish. Tidak perlu merge terpisah. |
| feat/chart-sammy | 9fdf32b | Input modal, penjelasan strategi, klik/tap pin tahun dan istilah hari bursa. Seluruhnya sudah tercakup di polish. |
| feat/timeline-ui-polish | 523c993 | Mencakup chart dan Sammy; menambahkan landing analisis emiten, default LPPF, dua menu utama, metadata baru. Sumber UI paling lengkap. |
| feat/supabase-migration | HEAD lokal 9cc1c81 | Nama branch ada lokal, belum remote. Perubahan Supabase, Docker, API key, proxy Next, bukti dan runbook masih uncommitted. Harus dicatat dalam commit sebelum bisa dipakai Git deployment. |

Riwayat remote satu garis: main → chart → chart-sammy → timeline-ui-polish. Perubahan Supabase/Dalang berada di working tree terpisah yang masih bertumpu pada chart. Tidak ditemukan pull request pada saat pemeriksaan.

## Temuan yang mempengaruhi deployment

1. **P1: polish sendiri belum mempunyai proxy yang menyisipkan key backend.** `next.config.ts` pada polish baris22–29 masih rewrite langsung ke BACKEND_URL dan tidak ada `src/app/api` route. VPS menolak `/api/catalog` tanpa key dengan HTTP401 (diuji). Jika BACKEND_URL kosong, targetnya127.0.0.1:8000 yang tidak menyediakan FastAPI di Vercel. Ambil Route Handler server dan next.config tanpa rewrite dari perubahan deployment lokal. Jangan mengekspos key lewat NEXT_PUBLIC atau menaruhnya di browser.
2. **Perubahan produk yang perlu dikenali:** menu utama tinggal Analisis emiten dan Simulator; fitur lainnya masih ada di source tetapi tidak masuk navigasi utama. Pratinjau LPPF terbuka otomatis dan tetap berlabel belum terverifikasi. Menu Simulator menghapus selection event khusus dan memakai default BBCA/BMRI/LPPF; analisis satu emiten belum tersambung ke simulator. Batas ini sudah dicatat sebagai ISS-046 di branch polish, bertabrakan dengan ISS-046 deployment pada branch lokal.
3. **P2: fixture deployment perlu diperbarui sebelum backend hasil gabungan dirilis.** `work/verify_dalang_deployment.py:55` membandingkan seluruh result ke readiness-case lama. Replay gabungan menunjukkan12perbedaan teks akibat istilah sesi→hari bursa; seluruh angka/struktur sama. Jangan menganggapnya regresi kalkulasi atau menghapus pemeriksaan. Perbarui fixture yang sudah ditinjau atau pisahkan validasi angka/struktur dari wording secara eksplisit (ISS-051 lokal).
4. **Konflik dokumentasi:** simulasi merge menemukan konflik teks pada ISSUES.md, SPRINT_PLAN.md dan TRACEABILITY.md; tidak ada konflik kode aplikasi. README/PROGRESS overlap tetapi auto-merge bersih. Penomoran ISS-044/045/046 mempunyai makna berbeda pada kedua sisi dan perlu dirapikan agar referensinya tidak tertukar.

## Pemeriksaan aktual

Semua dilakukan pada salinan sementara, tanpa membawa .env.local atau mengubah checkout aktif. Dependensi yang sudah terpasang digunakan untuk build.

- Build Next.js produksi dan TypeScript: lulus, termasuk route dinamis `/api/[...path]`.
- Lint: lulus.
- Backend:60tes lulus,1warning upstream Starlette yang sudah dikenal.
- Replay lokal disposable SQLite: struktur dan angka sesuai fixture;12perubahan prosa seperti dijelaskan di atas. Percobaan awal in-memory SQLite tidak berbagi tabel lintas thread; harness diperbaiki menggunakan file sementara dan file dihapus sesudah selesai.
- Preview produksi localhost3101 dengan konfigurasi server-only ke VPS: health200, landing LPPF tampil, dua menu, simulator awal kosong lalu input50000000 menjadi50.000.000; consoleerror/warning kosong. Tidak mengirim simulasi atau mutation baru ke database cloud. Preview review ditutup setelah pemeriksaan.
- Bukan UAT, bukan bukti deployment Vercel, dan bukan validasi ulang seluruh interaksi desktop/mobile.

Bukti terstruktur: [branch-review.json](../../outputs/development/branch-review.json).

## Urutan yang disarankan

1. Commit dan push seluruh perubahan deployment/Supabase yang sudah ditinjau pada feat/supabase-migration. Pastikan .env, runtime DB dan key tetap diabaikan Git.
2. Merge feat/timeline-ui-polish ke feat/supabase-migration. Pertahankan kode proxy/auth/cloud storage dan kontribusi UI. Selesaikan tiga konflik dokumentasi, nomor issue dan fixture deployment.
3. Jalankan pemeriksaan gabungan final, lalu gunakan branch gabungan tersebut untuk Preview Vercel.
4. Setelah preview lulus pemeriksaan alur, merge feat/supabase-migration ke main dan gunakan main sebagai production branch. Branch chart dan chart-sammy tidak perlu di-merge satu per satu.

Environment server Next/Vercel yang diperlukan: BACKEND_URL ke origin HTTPS Dalang dan HORIZON_API_KEY sama dengan VPS. DATABASE_URL/Supabase secret key tetap di backend VPS; frontend tidak memerlukan keduanya untuk arsitektur ini. Konfigurasi Preview dan Production harus diperiksa masing-masing saat deploy. Ini rekomendasi target main; belum memeriksa/mengubah production branch pada dashboard Vercel.

Kontrak API UI polish kompatibel dengan backend VPS yang sekarang. Lima file backend yang berubah berisi prosa/label hari bursa; UI juga menormalisasi wording hasil lama. Pembaruan backend dapat menjadi release berikutnya setelah fixture ditinjau; tidak perlu migrasi ulang Supabase untuk perubahan UI ini. Login/isolasi pengguna, durable worker, coverage data dan UAT tetap gap yang sudah terdokumentasi.
