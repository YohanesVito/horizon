# Pemetaan kebutuhan ke pekerjaan development

## Integrasi UI BR-07 dan batas backend skenario

BR-07 menggabungkan UI polish terbaru dengan pekerjaan F-02 lokal untuk C-02/C-08. Alur kandidat/timeline historis terverifikasi pada backend aktif dan browser lokal, sedangkan form skenario ex-date sementara tidak ditampilkan karena endpoint FastAPI terkait belum ada pada image produksi (ISS-067 BYPASSED). Kode engine dan komponen tetap disimpan untuk rilis backend berikutnya; ini belum memenuhi fitur skenario live ataupun validasi prediksi.

## Keputusan operasi terbaru — 8 Oktober 2026

DEP-01–DEP-03 DONE: FastAPI/Docker Dalang healthy, Supabase Session Pooler, HTTPS provider dan proxy Next server-only terverifikasi. Smoke image, delapan endpoint, penolakan401, replay identik fixture, preservasi20record, frontend→VPS dan browser Peluang/Timeline lulus. Kelima layanan kurasi tetapinactive. Bukti `outputs/deployment/deployment.json` dan laporan terkait; [DEPLOYMENT_DALANG.md](./DEPLOYMENT_DALANG.md). Frontend publik, UAT, login, durablequeue serta gap data/model bukan hasil deployment ini. ISS-048 storage tetap OPEN.

Instruksi langsung PM: FastAPI tetap dipakai, target deployment Docker pada VPS Dalang, database Supabase; proposal rewrite Next.js + ORM TypeScript tidak dilanjutkan. OPS-01 menangani penghentian sementara dan pencatatan restart. Setelah ditemukan bahwa layanan lama berjalan melalui systemd, PM mengotorisasi penghentian tepat lima layanan kurasi. Bukti dan runbook berada di [DALANG_SERVICE_PAUSE.md](./DALANG_SERVICE_PAUSE.md). Keputusan hosting bukan bukti deployment selesai atau kesesuaian PRD yang belum diterima.

Tanggal: 6 Oktober 2026. Status: pemetaan sementara dari percakapan; menunggu PRD dan user story lampiran. ID `C-*` adalah referensi internal untuk kebutuhan percakapan, bukan ID resmi dokumen pengguna.

## Daftar sumber

| Sumber | Lokasi atau keterangan | Status |
|---|---|---|
| Instruksi sprint PM | Pesan chat yang meminta plan, pencatatan progres/bug/TODO, bypass dan testing akhir | Tersedia |
| Keputusan FastAPI | Pesan chat terbaru: performa belum concern dan memilih FastAPI | Disepakati |
| PRD lampiran | Path/tautan belum tersedia | Menunggu input |
| User story lampiran | Path/tautan belum tersedia | Menunggu input |
| Proposal arsitektur | [arsitektur-sistem.md](../../outputs/dividend-research/arsitektur-sistem.md) | Referensi teknis, bukan PRD final |

## Baseline percakapan

Kriteria di bawah adalah kriteria kerja sementara yang dirumuskan dari percakapan. Rekonsiliasi dengan kata-kata dan ID dokumen asli dilakukan pada S0-04.

| ID | Kebutuhan atau alur | Asal | Kriteria yang akan diperiksa | Task terkait | Status terhadap PRD |
|---|---|---|---|---|---|
| C-01 | Menemukan kandidat tanpa harus mengetahui ticker terlebih dahulu | Kebutuhan eksplorasi PM; UI discovery diusulkan assistant | Daftar kandidat bisa disaring/diurutkan, periode dan makna yield terbaca | S2-03 | Belum dipetakan |
| C-02 | Melihat timeline dividen beberapa emiten dan detail harga historis | Kebutuhan PM | Declaration/cum/ex/record/payment dibedakan; null dan revisi terlihat | S2-01, S2-02, S2-04 | Belum dipetakan |
| C-03 | Memilih serta menyimpan emiten yang ingin dipantau | Usulan watchlist dalam percakapan | Penambahan/penghapusan bekerja; jenis persistensi mengikuti PRD | S2-04 | Belum dipetakan |
| C-04 | Menyimulasikan modal dengan aturan masuk, keluar dan horizon | Kebutuhan PM | Input menghasilkan posisi, dividen, PnL gross, kas dan asumsi yang dapat ditelusuri | S1-02, S3-01, S3-02, S3-04 | Belum dipetakan |
| C-05 | Membandingkan all-in, split dan urutan rotasi | Kebutuhan PM | Modal/horizon pembanding sama; modal tertahan dan kesempatan yang terlewat ditampilkan | S3-03, S4-03 | Belum dipetakan |
| C-06 | Memahami risiko trap dan waktu pemulihan | Kebutuhan PM | BEP harga terpisah dari BEP total; event belum pulih, sampel dan batas estimasi tetap terlihat | S3-02, S4-01, S4-02, S4-03 | Belum dipetakan |
| C-07 | Menggunakan logika finansial milik tim | Kebutuhan PM | Aturan serta versi disimpan dengan input/hasil; perubahan tidak menimpa hasil lama | S2-03, S3-02, S4-02 | Belum dipetakan |
| C-08 | Menjaga sumber dan asumsi perhitungan | Arahan PM | Finansial dari Sectors, gross di luar biaya/pajak/slippage, tidak mengeksekusi order | S1-02, S2-01, S2-02, S3-01 | Belum dipetakan |

## Format pemetaan final

Saat dokumen tersedia, tambahkan tabel berikut dengan kutipan lokasi requirement yang cukup spesifik. Jangan menciptakan ID story pengguna jika dokumennya tidak memiliki ID; buat ID internal dan tandai asalnya.

| ID PRD atau story | File dan bagian sumber | Acceptance criteria | Task | Bukti implementasi | Bukti verifikasi | Issue atau bypass | Status |
|---|---|---|---|---|---|---|---|
| Menunggu dokumen | — | — | S0-03, S0-04 | — | — | ISS-001 | WAITING_INPUT |

Status final dapat membedakan belum dikerjakan, sebagian, selesai development, dibypass, serta sudah diuji. Coverage sementara tidak boleh dinyatakan sebagai persentase cakupan PRD sebelum seluruh dokumen dibaca.

## Bukti baseline yang sudah diimplementasikan

| Kebutuhan | Implementasi | Verifikasi / gap |
|---|---|---|
| C-01 | Peluang: query, sort, rules yield/frequency/replay | Browser filter10% menghasilkan5 emiten; rules persisten. Composite scoring belum ada. |
| C-02 | Kalender + detail lima tanggal dan harga | Null declaration eksplisit; kalender snapshot2025, bukan current/live. |
| C-03 | Watchlist API/SQLite | Browser tambah/hapus dan reload; tidak ada akun. |
| C-04 | FastAPI job + Decimal ledger |13 pemeriksaan backend; browser berhasil dari form ke hasil. |
| C-05 | Tiga alokasi dengan modal/horizon sama | BMRI terlewat saat rotasi; bukan optimizer rute global. |
| C-06 | Statistik BBCA, replay, serta intelligence9 emiten | Wilson, KM dan audit48 event; analog nominal gross. Forecast/probabilitas terkalibrasi belum ada. I-01/I-02/I-04; ISS-022–025. |
| C-07 | Screening + ranking objective/risiko tim, rules/input/result persisten | Prioritas median return/worst return/risiko/BEP, filter minimum sampel dan Wilson upper bound. Belum bahasa formula bebas. I-03; API/browser diuji. |
| C-08 | Sectors MCP + REST snapshots, gross, read-only |81 artifact frontend diperiksa tanpa key; tidak ada order execution. |

Tabel ini bukan rekonsiliasi PRD. Sumber dokumen asli masih dibutuhkan untuk mengukur coverage final.

Sprint intelligence memperluas baseline C-04 dengan stress test **satu posisi**, bukan menggantikan replay rotasi C-05. Rencana rotasi forward, proyeksi tanggal dan ML trap tetap gap ISS-024; kelulusan pengujian kalkulasi tidak mengisi gap tersebut.

## Integrasi rotasi R-01–R-05

| Kebutuhan | Implementasi sekarang | Batas |
|---|---|---|
| C-01/C-02/C-08 | 12 event kanonis 2025 dari sembilan emiten, ID/tanggal/DPS sama dengan Intelligence; 50 snapshot MCP harga/IHSG baru | Bukan coverage IDX penuh; empat gap IHSG diperbaiki dari konsensus feed, ISS-029 |
| C-03/C-07 | Filter emiten Peluang/Watchlist → planner; salinan aturan Intelligence → cutoff sebelum keputusan | Pemilihan universe manual dapat tetap bias; bukan formula bebas |
| C-04/C-05 | 1–3 rute sebelum replay, lalu tiga alokasi tiap rute + baseline cash pada modal/periode sama | Heuristik, bukan optimum global; jadwal mendatang dalam replay masih asumsi |
| C-06 | Drawdown, lot terbuka/di bawah entry, durasi modal, missed events, ledger dengan dividen berulang | Statistik masa lalu, bukan trained probability atau forecast waktu pulih |
| C-07/C-08 | Rencana frozen, evidence IDs/cutoff/reasons, fingerprint, job hasil terpisah, riwayat tersimpan | SQLite/local worker; declaration timestamp dan snapshot point-in-time belum tersedia |

[PM_REVIEW.md](./PM_REVIEW.md) mengusulkan alur diskusi serta calon acceptance checks. R-05 tidak menutup S5-03/S6 atau menyatakan PRD/UAT sudah selesai.

U-01 menambah bukti C-04/C-07/C-08: hasil manual menampilkan snapshot aturan/event/versi, form dibedakan dari hasil, dan salinan input menjadi run baru. U-02 menyediakan [UAT_SESSION.md](./UAT_SESSION.md); penilaian pemahaman pengguna serta coverage PRD belum dinyatakan lulus.

## Timeline T-03–T-05

C-02/C-06/C-08: menu Timeline dengan overlay lima periode satu emiten, fokus hover/klik/keyboard, hargaRp/perubahan%, fase dividen per tahun dan lapisan aktual2026dengan placeholder prediksi. API memisahkan katalog histori lengkap dari pratinjau riset LPPF.46tesbackend,build/lint/typecheck,API dan browser diperiksa; lihat [TIMELINE_IMPLEMENTATION.md](./TIMELINE_IMPLEMENTATION.md). Dataset lengkap masih gap ISS-041; engine prediksi ditunda oleh PM pada ISS-042. Bukan klaim coverage PRD final atau UAT lulus.

## Migrasi Supabase DB-01–DB-03

C-03/C-04/C-05/C-07/C-08 dan S1-02: penyimpanan watchlist, rules, scenario, rencana dan hasil dipindahkan dari SQLite ke schema privat PostgreSQL. Migrasi berversi mempertahankan ID/payload/timestamp, memiliki backup, deteksi konflik dan pemeriksaan checksum; akun backend terpisah dari admin. [Runbook](./SUPABASE_MIGRATION.md) menjelaskan batas: market snapshots tetap file, workspace masih bersama, local worker belum durable, dan frontend/backend tetap berjalan lokal. Status pemeriksaan aktual di PROGRESS.md; tidak mengubah klaim coverage PRD/UAT.

## Fokus demo D-01

Instruksi PM 7 Oktober memprioritaskan satu alur: analisis emiten (histori dan periode berjalan) lalu simulator. D-01 mengubah pintu masuk dan navigasi demo, bukan menghapus C-01/C-03/C-05 atau implementasinya. Pratinjau LPPF tetap berlabel belum terverifikasi (ISS-041); simulator satu-emiten belum terhubung dan masih perlu pekerjaan terpisah (ISS-054). Sumber/metodologi tersedia sebagai tautan sekunder.

D-02 menggabungkan arah demo dari PM (D-01, perubahan lokal pada branch UI) dengan implementasi Sammy pada `feat/chart-sammy` (UX-01–UX-04: input modal, pilihan strategi, klik chart, dan copy/istilah). `dashboard.tsx` diselaraskan manual agar pemangkasan copy/sidebar Sammy tidak mengembalikan delapan menu atau landing Peluang. Ini sinkronisasi kontribusi, bukan bukti bahwa simulator satu-emiten, data lengkap, atau forecast sudah selesai.

## Penemuan emiten D-03 — perubahan syarat PM 8 Oktober

C-01/C-02: kelengkapan histori overlay lima tahun tidak lagi menjadi filter untuk menemukan **nama emiten**. D-03 mengambil peringkat yield tahunan 2025 dari MCP Sectors untuk seluruh emiten dengan dividen/yield positif yang dikembalikan screener, dan menampilkan lima teratas sebagai kandidat historis. Tahun, waktu snapshot, DPS dan batas interpretasi terlihat. `history_eligible` serta katalog grafik terverifikasi tetap dipakai hanya untuk overlay; emiten tanpa grafik dapat tetap muncul dalam daftar kandidat. ISS-041 sekarang membatasi grafik, bukan penemuan nama. Peringkat ini belum mengukur keuntungan strategi, keamanan dividen, atau kondisi pasar saat ini (ISS-057).

Arahan PM berikutnya pada 8 Oktober mengubah batas grafik juga: C-02/C-08 melalui T-08 menampilkan **semua jendela peristiwa yang mempunyai event dan harga dalam snapshot** untuk lima kandidat, tanpa mewajibkan lima tahun penuh. Tahun tanpa kurva ditandai sebagai kekosongan snapshot; beberapa pembayaran pada satu tahun tetap terpisah menurut ex-date. `eligible` kini menguji verifikasi setiap periode yang ditampilkan, bukan jumlah tahun. Semua kandidat saat ini masih berstatus pratinjau karena gap verifikasi ISS-041; peringkat yield historis D-03 tidak berubah.

## Formula prediksi F-01 — rancangan riset 8 Oktober

C-02/C-04/C-06/C-07: [PREDICTION_FORMULA.md](./PREDICTION_FORMULA.md) mendefinisikan input point-in-time, target harga/trap/BEP/waktu pulih, hipotesis model dan cara menguji sebelum angka prediksi ditampilkan. Ini **dokumen proposal**, bukan implementasi S4-02 atau penyelesaian ISS-024/ISS-042; statusnya tetap mengikuti PROGRESS.md dan ISSUES.md.

F-02a menambahkan eksperimen ex-date v0.2 untuk C-02/C-06/C-07: pasangan harga cum/ex Sectors, model pooled PDR dan dua pembanding diuji per tahun melalui `/api/research/ex-date`. Angka tersebut adalah diagnostik retrospektif karena vintage DPS/jadwal tidak ada dan sampel telah dipilih/ditinjau sebelumnya. F-02, ISS-024/ISS-042, dan forecast timeline live tetap terbuka; hasil dan batasnya tercatat di PROGRESS.md, ISSUES.md, dan formula v0.2.

F-02b menambah pemeriksaan C-02/C-06/C-07 pada LPPF ex-date 2026: pengumuman emiten dan KSEI membuktikan DPS/jadwal dipublikasikan sebelum cum-date, Sectors MCP menyediakan dua harga OHLCV, dan model 44-event v0.2 diuji tanpa retuning. Pada satu event ini full-DPS lebih akurat daripada pooled-PDR. Basis adjustment/close independen belum terverifikasi, sampel bukan holdout blind, dan ISS-041/ISS-042 tetap terbuka. Rincian protokol, artefak dan keputusan ada pada formula v0.3 serta PROGRESS.md; tidak ada perubahan angka prediksi live atau status UAT.

F-02c melanjutkan C-02/C-06/C-07 dengan audit 48 event sumber (44 pasangan eligible) dan pembanding issuer-shrunk yang diprapilih. Tiga notice LPPF 2023–2025 cocok dengan Sectors; jadwal pembayaran LPPF 2022 memiliki versi awal dan final yang berbeda (ISS-062). Perbandingan model pada 36 event lama dan satu LPPF 2026 tidak melewati gate point-in-time, basis harga, atau holdout blind. Formula v0.4 dan artefak F-02c menyimpan status per event; F-02/ISS-041/ISS-042 dan forecast live tetap terbuka, tanpa klaim UAT.

## Integrasi BR-02 dan deployment frontend V-01/V-02

C-02/C-04/C-08, S5-02: gabungan UI polish523c993 dengan proxy Next/Supabase/Dalang f64df85 mempertahankan kedua kontribusi. Fixture berversi membuktikan hitungan tidak berubah; issue052/053/054 merujuk UX/handoff, sedangkan044–050 tetap migrasi/deployment. Status deployment Vercel dan bukti aktual mengikuti PROGRESS.md; bukan kelulusan UAT.

Arahan PM terbaru 8 Oktober menyerahkan deployment Vercel kepada PM dan meminta merge main segera. V-02 dibatasi merge/push; V-01 tetap PARTIAL/HANDOFF. Env server telah dipasang setelah izin; build cloud READY belum merupakan verifikasi browser/API/database atau UAT.

## Hierarki chart UI-03 (Chunk 2; D-03 pada branch UI asal)

UI-03 merapikan hirarki visual timeline agar grafik historis menjadi fokus utama layar. Header/picker emiten dibuat kompak, kontrol grafik disatukan dalam dua baris terstruktur (`timeline-toolbar` untuk legenda peristiwa dan sakelar mode/satuan; `timeline-status-bar` untuk sinyal pergerakan Cum → Ex dan instruksi interaksi). Fitur interaksi Sammy (klik/tap chart untuk mengunci fokus, tombol peristiwa, opasitas seri, istilah hari bursa, dan form simulator) tetap bekerja; T-08 memperluas fokus dari tahun ke ID peristiwa agar beberapa dividen pada satu tahun dapat dibaca terpisah. ID UI-03 dipakai agar tidak bertabrakan dengan D-03 penemuan emiten. Pemisahan tegas aktual vs prediksi dan handoff emiten ke simulator masih terbuka.

## Penyederhanaan UI D-04

D-04 menindaklanjuti keputusan PM 8 Oktober untuk memprioritaskan alur dan tampilan dibanding algoritme proyeksi. C-02/C-04 tetap lewat Analisis dan Simulasi; C-08 tetap terlihat melalui label sumber, caveat preview, serta metodologi. Mode periode berjalan diberi label aktual, bukan prediksi. Detail keputusan, referensi, dan pemeriksaan ada di [UI_REDESIGN.md](./UI_REDESIGN.md). D-04 tidak menutup ISS-041/042/054 atau menyelesaikan PRD/UAT.

## Revisi editorial D-05

D-05 mengubah hierarki visual dua layar demo atas contoh Arcturis dari PM, tanpa memperluas cakupan produk. C-02 tetap melalui grafik multi-tahun beserta kontrol fokus/satuan dan detail event; C-04 melalui form replay, pembanding, dan hasil gross; C-08 melalui sumber, caveat pratinjau LPPF, dan metodologi. Hero yang besar menempatkan chart/form di bawah fold secara sengaja. Tidak ada requirement yang ditutup oleh styling ini: ISS-041/042/054 dan UAT tetap terbuka. Detail keputusan dan bukti pemeriksaan ada di [UI_REDESIGN.md](./UI_REDESIGN.md) dan [PROGRESS.md](./PROGRESS.md).

D-07 menggabungkan main terbaru secara lokal dengan UI D-05. C-02/C-04/C-08 kini berada bersama backend Supabase dan proxy server Next tanpa mengubah rumus atau data. Build dan tes development lulus; browser/API lokal gabungan belum diuji karena server tidak berjalan. Merge ini tidak mempublikasikan branch atau mengubah status deployment/UAT.

## Integrasi desain dan data BR-04

C-01/C-02/C-08: desain editorial `feat/timeline-ui-polish` menjadi dasar tampilan; lima kandidat D-03 dan grafik parsial T-08 ditambahkan tanpa menyingkirkan toolbar, panel harga, kronologi, maupun layar Simulasi. Fokus berubah dari tahun ke ID event agar dua pembayaran satu emiten pada tahun sama tetap terpisah. C-06/C-07: panel Engine Riset membaca statistik empiris lama beserta aturan, ukuran sampel, dan rentang Wilson; ini belum menjalankan hipotesis prediksi harga/probabilitas F-01. `forecast.status` tetap `not_available` sesuai ISS-042. Perubahan dan bukti integrasi mengikuti PROGRESS.md; bukan penutupan PRD/UAT.

## Sinkronisasi produksi DEP-04

C-01/C-02/C-06/C-08 melalui BR-04 akhirnya terhubung end-to-end pada URL Vercel setelah FastAPI Dalang dinaikkan dari release awal ke `20261008T053018Z-8544ed8b61` (ISS-061). Lima kandidat, preview parsial, detail grafik yang dapat dipilih, dan statistik risiko historis terbukti melalui browser dan API; perhitungan replay API→worker→Supabase identik dengan fixture, tanpa perubahan 20 record awal. Bukti ada di `outputs/deployment/deployment.json`, `live-editorial-verification.json`, dan `dalang-api-verification.json`. Ini hanya menutup ketidakcocokan versi produksi; validasi data per event ISS-041, forecast ISS-042, I/O ISS-048, PRD/user story asli, serta UAT tetap terbuka.

F-02d menambah C-02/C-04/C-06: API skenario ex-date dan form Analisis menghitung hasil gross, dividen dan dua BEP dari input pengguna. Ini uji asumsi, bukan sumber harga live atau probabilitas. F-02e menambah C-02/C-06/C-07: CLI privat membekukan baseline pre-cum dengan hash snapshot Sectors serta append outcome setelah ex-date. Kode/gate diuji lokal; kandidat nyata dan validasi sumber belum tersedia (ISS-063), sehingga F-02/ISS-042 dan `forecast.status=not_available` tetap terbuka. Formula v0.5, runbook dan bukti ada di PROGRESS.md; belum dideploy/UAT.

F-02f melanjutkan C-02/C-06/C-07: kalender REST v2 Sectors yang baru dan harga/aksi korporasi MCP dipasangkan dengan PDF KSEI. Empat baseline ASII/TLDN/AMRT/BSBK dibekukan pada 8 Oktober sebelum cum-date; timestamp capture, hash file serta alasan tiga event lain tidak masuk disimpan sebagai artefak. `notice_document_date` tidak disamakan dengan waktu publikasi. Belum ada outcome atau akurasi; AMRT memiliki gap di MCP corporate actions, AUTO memiliki revisi rasio KSEI, dan basis harga tetap belum diaudit (ISS-064/ISS-065). F-02/ISS-042 serta `forecast.status=not_available` tetap terbuka; formula v0.6 dan PROGRESS.md memuat rinciannya. Tidak ada perubahan UI/deployment/UAT.

F-02g melanjutkan C-02/C-06/C-07: protokol evaluasi menetapkan target, error ternormalisasi, pembanding flat, dan aturan tidak membuang event buruk sebelum close ex-date tersedia. CLI privat `status` memvalidasi DB terhadap ekspor kohort dan semua hash sumber; `collect-score` hanya mengambil MCP price setelah ex-date WIB, mengarsipkan response dan memanggil score append-only. Uji fixture mengonfirmasi gate waktu, validasi hash, idempotensi dan perhitungan report; status nyata tetap 0/4 outcome. Tidak ada probabilitas baru, klaim performa, endpoint/UI atau deployment; F-02/ISS-042/ISS-063/ISS-064 tetap terbuka.
