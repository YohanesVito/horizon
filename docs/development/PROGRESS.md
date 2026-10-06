# Progres development MVP

Tanggal pembaruan: 6 Oktober 2026. Tahap saat ini: implementasi MVP lokal. PRD/user story lampiran belum tersedia; baseline sementara mengikuti percakapan dan instruksi coding 6 Oktober.

## Aturan pencatatan

Perbarui status setelah pekerjaan berubah, bukan hanya di akhir sprint. Setiap task selesai memiliki tanggal, hasil konkret, path/commit bila ada, pemeriksaan yang benar-benar dijalankan, dan issue tersisa. Task yang dibypass tetap ditandai `BYPASSED`, tidak berubah menjadi `DONE` hanya karena pekerjaan lain dilanjutkan.

Status task: `TODO`, `IN_PROGRESS`, `WAITING_INPUT`, `BLOCKED`, `BYPASSED`, `DONE`. `DONE` berarti selesai pada lingkup task dan pemeriksaan development yang dicatat; bukan otomatis lulus testing akhir. Status milestone `READY_FOR_TESTING` dan `DELIVERED` mengikuti [rencana sprint](./SPRINT_PLAN.md).

## Status task

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
| S1-02 | BYPASSED | Pydantic/OpenAPI + SQLite record JSON; schema/migrasi kanonis ditunda | ISS-010, ISS-013 |
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
