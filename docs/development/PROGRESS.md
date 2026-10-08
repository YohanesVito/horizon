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

Browser production pada `http://localhost:3000` memakai FastAPI asli dan snapshot Sectors lokal, tanpa mock/provider request baru. Mengetik `100000000` menampilkan `100.000.000`; paste `50.000.000` menghasilkan POST Simulator `capital:50000000` dan planner `capital:"50000000"`. Tiga simulasi berstatus completed, input/primary allocation masing-masing single/equal/rotation dan compare=true tetap memberi tiga alternatif. Hasilnya tersimpan dan dibaca kembali lewat API. Skenario menerima modal `50.000.000,25`, harga `10.000,5` dan DPS `0,125` sebagai `50000000.25`/`10000.5`/`0.125`, tersimpan di history. Required, minimum, maksimum, step bulat, karakter invalid dan paste notasi ilmiah menghalangi POST; edit tengah/caret dan backspace melewati separator diuji. Salin hasil mengembalikan modal dan menghapus error paste bahkan ketika nilai angka sama (ISS-044). Space/ArrowRight memilih tiga radio; screenshot dan DOM Simulator/planner/Intelligence pada1440/390 menunjukkan scrollWidth sama dengan viewport.

Pengukuran cache browser pada jendela1,484detik: GET BBCA tetap1 sesudah dua pembukaan detail; GET timeline LPPF tetap1 setelah fokus tahun, Rp/%, dan hover. Cache staleTime60detik tetap konfigurasi lama; bukan janji tidak ada refetch setelah stale/remount. Kontrol timeframe/zoom belum diimplementasikan dan tidak diuji. Tidak mengklaim optimasi cache baru.

`npm run lint`, `npm run typecheck` dan `npm run build` lulus. Browser production tanpa pageerror atau warning; favicon404 tetap issue kosmetik ISS-045. Bukti dan skrip ulang: [ui-feedback-verification.json](../../outputs/development/ui-feedback-verification.json), [verify_ui_feedback.cjs](../../work/verify_ui_feedback.cjs), screenshot [desktop](../../outputs/development/ui-feedback-simulator-1440.png)/[mobile](../../outputs/development/ui-feedback-simulator-390.png). Skrip membutuhkan Playwright/Chromium; instalasi pemeriksaan tersedia di `/tmp/horizon-ui-check/node_modules` (contoh command di header skrip).

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

Pemeriksaan aktual sebelum sinkronisasi Sammy: `npm run lint`, `npm run typecheck`, dan `npm run build` lulus. Browser lokal viewport362px memperlihatkan hanya dua item navigasi, LPPF terpilih dengan label pratinjau, chart histori dimuat, perpindahan Simulator→Analisis dan tautan Metodologi→Analisis berfungsi; lebar dokumen347px pada viewport362px (tanpa overflow horizontal). Belum menjalankan UAT atau mengubah perhitungan/data. Simulator masih default multi-event dan belum mengikuti emiten dari chart (ISS-046); kelengkapan LPPF dan forecast tetap ISS-041/042. Tidak ada commit/push.

## Integrasi pekerjaan PM dan Sammy — 7 Oktober 2026

**D-02 DONE (integrasi lokal; C-02/C-04/C-08).** Branch PM `feat/timeline-ui-polish` di-fast-forward dari `9cc1c81` ke commit Sammy `9fdf32b` pada `origin/feat/chart-sammy`, lalu perubahan D-01 yang belum di-commit diterapkan kembali. Arah navigasi dua menu, landing Analisis emiten, dan pratinjau LPPF berasal dari feedback PM dan pekerjaan D-01; interaksi klik/tap untuk mengunci tahun chart, perbaikan input modal/strategi Simulator, serta istilah “hari bursa” berasal dari pekerjaan Sammy UX-01–UX-04. Konflik dashboard dan dokumentasi diselesaikan dengan mempertahankan kedua kontribusi. Nomor issue handoff Simulator dari D-01 menjadi ISS-046 agar ISS-044/045 milik branch Sammy tetap utuh.

Sesudah integrasi, `npm run lint`, `npm run typecheck`, `npm run build`, dan 46 tes backend lulus (satu warning deprecation Starlette yang sudah ada). Browser lokal memastikan dua menu dan landing LPPF, klik chart mengunci/melepas tahun, modal Simulator kosong lalu terformat `50.000.000`, tautan Metodologi berfungsi, serta tidak ada overflow horizontal pada viewport 362px. Ini pemeriksaan integrasi, bukan UAT atau validasi data/prediksi. HEAD branch sama dengan commit Sammy; perubahan D-01 dan dokumentasi masih lokal/uncommitted. Tidak ada commit atau push baru; snapshot stash integrasi disimpan sebagai cadangan pemulihan.

## Hierarki chart horizon (Chunk 2) — 8 Oktober 2026

**D-03 DONE (instruksi PM Chunk 2; C-02/C-06/C-08; UX-01–UX-04).** Hierarki tampilan timeline dirapikan agar grafik historis lintas tahun menjadi fokus utama:
1. Header dan picker emiten disederhanakan: padding dan margin dikurangi, letter avatar statis diganti ticker dinamis ringkas, dan batas atas grafik naik ~180px sehingga grafik langsung terlihat tanpa scroll berlebih.
2. Kontrol grafik disatukan dalam dua baris terstruktur:
   - Baris 1 (`timeline-toolbar`): Legenda tahun interaktif (tombol tahun dengan warna indikator, lock icon saat terkunci, dan tombol “Bandingkan semua”) di sisi kiri; sakelar mode (`Histori` / `2026 Aktual + Prediksi`) dan satuan harga (`Perubahan %` / `Harga Rp`) di sisi kanan.
   - Baris 2 (`timeline-status-bar`): Highlight perubahan Cum → Ex periode aktif beserta arah/warna pergerakan di sisi kiri; panduan interaksi klik/tap chart dan satuan harga di sisi kanan.
3. Fitur Sammy sepenuhnya dipertahankan: hit-test klik/tap chart untuk mengunci/melepas fokus tahun, opasitas seri tidak aktif (0.25), keyboard navigation (Enter/Space), istilah “hari bursa”, dan input/strategi Simulator.
4. Rumus, data point, dan kalkulasi tidak diubah. Sumbu X tetap hari kalender relatif terhadap ex-date.

Pemeriksaan: `npm run lint`, `npm run typecheck`, `npm run build`, serta 46 tes backend lulus (1 warning Starlette deprecation yang sudah ada). Layout responsif pada desktop dan mobile diperiksa (tanpa overflow horizontal). Gap sisa: periode berjalan 2026 aktual vs future belum terpisah secara tegas (Chunk 3) dan handoff emiten terpilih ke Simulator masih default multi-event (ISS-046; Chunk 4). Belum ada commit atau push baru.

## Penyederhanaan UI demo — 8 Oktober 2026

**D-04 DONE pada scope UI dua layar utama (instruksi PM terbaru; C-02/C-04/C-08).** Sidebar dua-item diganti header horizontal; judul/copy diperpendek, area chart melebar. Palet permukaan utama diubah ke arang kehijauan dengan aksen pasir, tanpa gradien dekoratif pada layar Analisis dan Simulasi. Preview LPPF tetap jelas sebagai data yang belum lengkap; label periode berjalan kini “2026 Aktual”, bukan klaim prediksi. Grafik dan Simulator memakai warna seri/status yang selaras tanpa mengubah harga, rumus, atau backend. Mode chart tidak lagi me-remount toolbar sehingga fokus keyboard tetap pada tombol yang dipilih. [UI_REDESIGN.md](./UI_REDESIGN.md) memuat alasan, sumber referensi, dan batas penerapan.

Pemeriksaan development: lint, typecheck, build, dan 46 tes backend lulus (satu warning Starlette lama). Browser lokal memperlihatkan header Analisis/Simulasi, chart LPPF dengan caveat, status 2026 aktual, dan fokus keyboard yang bertahan setelah pindah mode. Pada viewport 390px, `scrollWidth` 375px; grafik mulai sekitar 768px dari atas pada mode 2026 sehingga tetap memerlukan scroll di ponsel. Tidak ada UAT, penilaian algoritme forecast, atau commit/push pada pekerjaan ini. Fitur lama di luar dua layar utama belum seluruhnya diselaraskan dengan palet baru; ISS-041/042/046 tetap terbuka.

## Revisi editorial berdasarkan Arcturis — 8 Oktober 2026

**D-05 DONE pada scope visual demo (instruksi PM; C-02/C-04/C-08).** Revisi D-04 yang kurang sesuai diganti menjadi kanvas putih hangat, teks navy, aksen jingga, tipografi lebih besar, dan hero hampir setinggi viewport per layar. Analisis menempatkan pemilihan emiten lalu chart dalam panel data yang dominan; seri historis tidak lagi memakai tumpukan area berwarna keruh, sementara fokus tahun, mode `%`/`Rp`, status 2026 aktual, detail fase, dan caveat LPPF tetap ada. Simulasi memakai tiga langkah input dan urutan hasil yang lebih jelas; rincian teknis berada di disclosure/Metodologi. Halaman Metodologi, tabel hasil, status arsip, dropdown, dan tombol primer diberi kontras sesuai palet baru. [UI_REDESIGN.md](./UI_REDESIGN.md) mencatat keputusan dan batas.

Pemeriksaan development: `npm run lint`, `npm run typecheck`, `npm run build`, dan `git diff --check` lulus. Browser lokal desktop 1440px memperlihatkan hero, panel analisis, chart dan Metodologi yang terbaca; viewport 390px memperlihatkan navigasi Analisis→Simulasi, chart dengan fase ringkas, form langkah pertama, serta Metodologi tanpa overflow horizontal (`innerWidth` 390px, `scrollWidth` 375px karena scrollbar). Pada viewport default 897px, pemeriksaan menemukan label navigasi tersembunyi oleh aturan CSS lama; override D-05 memperbaikinya dan lebar tombol Analisis/Simulasi kembali terukur ~60/65px. Tautan “Mulai simulasi” membawa layar ke form; warna tombol dan option select terukur navy di atas jingga/putih hangat. Hero menempatkan chart/form di bawah fold secara sengaja; ini bukan angka posisi D-04. Tidak ada UAT pengguna, tes ulang kalkulasi/backend, klaim prediksi, atau commit/push. ISS-041/042/046 tetap terbuka.
