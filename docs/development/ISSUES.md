# Log bug TODO dan blocker

## Gap verifikasi AI-01 — 8 Oktober 2026

**AI-01-LIVE / OPEN:** helper structured output diuji dengan mock HTTP dan key
dummy. Kredensial, billing, akses `gpt-6-luna`, dan respons provider live belum
diverifikasi. Saat fitur AI diintegrasikan, jalankan smoke dengan input minimal
pada environment target. Ini batas bukti, bukan kegagalan provider yang diamati.
Schema harus mengikuti subset strict OpenAI; schema di luar subset ditolak API,
tanpa fallback ke output bebas. F-02 tetap pekerjaan terpisah.

## Review integrasi UI dan deployment — 8 Oktober 2026

- **ISS-051 — Fixture deployment / P2 / RESOLVED:** BR-02 mempertahankan readiness-case.json asli dan menambah readiness-case-timeline-ui.json dengan tepat12perubahan prosa yang telah ditinjau. Replay engine gabungan cocok secara strict dengan seluruh JSON result; angka grossPnL2900364/endingNAV102900364 tetap. Verifier menerima --fixture eksplisit dan tidak mengendurkan kesamaan hasil. Default tetap fixture release Dalang awal yang masih aktif; runbook membedakan kedua versi. Issue UI asal044/045/046 direkonsiliasi menjadi052/053/054. Bukti integration-verification.json dan metadata fixture baru.

## Retry deployment — 8 Oktober 2026

- **ISS-050 — Koneksi IPv6 / P1 / RESOLVED:** startup container gagal karena direct database hostname Supabase hanya menyediakan IPv6; jaringan container tidak mempunyai rute IPv6. Container dihentikan saat diagnosis. Session Pooler didapat dari dashboard proyek (host `aws-0-ap-southeast-2.pooler.supabase.com`, port5432), bukan ditebak dari region. Probe lokal melalui pooler memakai role `horizon_app` berhasil membaca20record dan TLS client diverifikasi melalui libpq. Env VPS diganti ke pooler dengan kredensial runtime yang sama; container healthy dan replay API→worker→Supabase lulus,20record sebelumnya tetap utuh. Bukti `outputs/deployment/session-pooler-verification.json`.

## Operasi Dalang — 7 Oktober 2026

- **ISS-049 — Jaringan Docker / P1 / RESOLVED:** build pertama gagal sesudah lima read timeout ke PyPI dari container, sedangkan curl HTTPS di host mendapat 200. Uplink enp5s0 memakai MTU 1442 dan docker0 memakai 1500. `deploy/configure-docker-network.sh` menyamakan bridge/default bridge ke uplink, memvalidasi daemon config, menolak restart bila ada container aktif, lalu menguji HTTPS dari container. Probe yang sama berhasil (`CONTAINER_PYPI_HTTPS_PASSED`); bukti `outputs/deployment/docker-network.log`. Tidak mengubah dependency pin. Build ulang dilacak terpisah pada DEP-01.

- **ISS-048 — Storage VPS / P1 / OPEN:** setelah pemulihan database paket, installer Docker tertahan pada dpkg saat memasang prasyarat curl. Pemeriksaan live `/proc/pressure/io`: some avg10=95.14 dan full avg10=94.80; memory PSI=0. Proses dpkg berstatus D/folio_wait_bit_common dan jbd2/sda2-8 D/wait_on_buffer. Ini membuktikan proses menunggu storage; akar penyebab host/provider belum diketahui. Kelima layanan kurasi tetap inactive. Sesudah deployment healthy, snapshot full avg10=5,88% dan avg60=14,19%; akar masalah belum terdiagnosis sehingga issue tetap OPEN. Build/deployment akhirnya selesai dengan waktu tunggu panjang. Jangan memaksa kill dpkg, menghapus lock atau mematikan fsync. Terkait DEP-01 dan operasi berikutnya.

- **ISS-047 — Paket VPS / P1 / RESOLVED:** instalasi Docker resmi berhenti dengan `dpkg was interrupted` setelah apt update. Audit menemukan sudo half-configured dan trigger libc-bin tertunda. `dpkg --force-confold --configure --pending` menyelesaikan keduanya; retry installer melewati error tersebut. Tidak melakukan upgrade penuh OS atau reboot. Bukti `outputs/deployment/dpkg-audit-before.txt` dan `dpkg-repair.log`. Masalah storage dilacak terpisah sebagai ISS-048; instalasi Docker akhirnya selesai, bukti docker-install.log.

- **ISS-046 — Kesiapan deployment / P2 / RESOLVED:** target baru adalah FastAPI dalam Docker di Dalang. Inventaris VPS membuktikan tidak ada binary Docker/Podman, daemon dockerd/containerd, maupun unit docker.service/docker.socket/containerd.service. Layanan lama ternyata lima unit kurasi systemd dan telah dihentikan setelah konfirmasi eksplisit PM (OPS-01). Docker Engine/Compose terpasang dan deployment Horizon terverifikasi8OktoberWITA (DEP-01–03); bukti di outputs/deployment/deployment.json. Autostart kelima unit tetap enabled. Snapshot juga mencatat NRestarts=641 pada producer; penyebab belum diperiksa. Runbook pemulihan dan tindak lanjut: [DALANG_SERVICE_PAUSE.md](./DALANG_SERVICE_PAUSE.md).

Tanggal pembaruan: 6 Oktober 2026. Log ini menjadi tempat mencatat temuan selama development, workaround, dampak terhadap requirement dan pekerjaan yang ditunda. Daftar awal berasal dari audit riset; bagian implementasi mencatat bug dan bypass aplikasi yang benar-benar ditemukan.

Status: `OPEN`, `IN_PROGRESS`, `BYPASSED`, `RESOLVED`, `DEFERRED`. Tabel awal mempertahankan konteks temuan; status implementasi terkini dirinci di bawah. `BYPASSED` tidak berarti requirement selesai.

Prioritas: `P0` menghentikan keluaran inti yang benar; `P1` mempengaruhi kebutuhan MVP atau keputusan scope; `P2` perbaikan yang dapat ditunda jika tidak menghambat alur. Prioritas ditinjau lagi setelah PRD dibaca.

## Daftar temuan

| ID | Jenis dan prioritas | Temuan serta bukti | Dampak / task | Tindakan sementara yang direncanakan | Status dan pemicu tinjauan ulang |
|---|---|---|---|---|---|
| ISS-001 | Input / P1 | Lampiran PRD dan user story belum terlihat di pesan, workspace maupun artifact chat | S0-03/S0-04; kesesuaian scope belum dapat dibuktikan | Susun rencana sementara dari percakapan; lanjutkan persiapan umum; jangan mengarang isi lampiran | OPEN; ditinjau saat path/tautan/dokumen diterima |
| ISS-002 | Data / P1 | Timestamp declaration belum ditemukan pada sampel audit | C-02/C-06; S2-04/S4-02 | Tampilkan belum tersedia; studi berdasarkan ex-date diberi label; jangan mengganti dengan tanggal RUPS | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau ketika endpoint/field baru diverifikasi |
| ISS-003 | Data / P1 | Snapshot kalender UNTR/ASGR berbeda dari berita perubahan jadwal pada audit sebelumnya | S2-02; eligibility dan rute | Tandai konflik, keluarkan event terkait dari kalkulasi sampai jadwal konsisten | BYPASSED; status workaround aktual ada di tabel implementasi; verifikasi ulang sumber saat implementasi; bukan klaim kondisi live saat ini |
| ISS-004 | Data / P1 | DPS ITMG 2026 pada sampel 0,05712 tanpa definisi unit yang jelas | S2-02/S3-01 | Karantina event; gunakan event dengan unit yang dapat dipastikan untuk demo | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau setelah definisi currency/unit tersedia |
| ISS-005 | Data / P1 | Basis DPS BBCA sebelum split berbeda antar-endpoint dengan rasio 5 | S2-02/S3-01 | Gunakan jendela pasca-split yang terverifikasi; jangan campur harga/saham/DPS dengan basis berbeda | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau setelah definisi adjustment diverifikasi |
| ISS-006 | Model / P1 | Pilot BBCA hanya 8 event dan replay uji 2 event; belum validasi model produk | S4-01/S4-02 | Bangun alur statistik/skenario berlabel dan status data tidak cukup; kebutuhan prediksi wajib tetap dilacak | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau setelah PRD dan dataset/validasi bertambah |
| ISS-007 | Data / P1 | Waktu publikasi/vintage lapkeu belum terverifikasi | S4-02 | Jangan memakai angka yang belum terbukti diketahui pada tanggal keputusan historis | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau setelah publication timestamp tersedia |
| ISS-008 | Data / P1 | Kalender hari bursa lengkap, cakupan suspensi/delisting dan beberapa tanggal benchmark belum tervalidasi | S3-01/S3-02/S4-01 | Batasi replay ke periode dengan sesi dan data yang dapat dipastikan; missing tetap missing | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau sebelum memperluas replay dan settlement ke periode baru |
| ISS-009 | Scope / P1 | Mekanisme akun, penyimpanan watchlist lintas perangkat dan lingkungan delivery belum ditentukan oleh dokumen yang tersedia | S1-03/S2-04/S5-02 | Tunda keputusan fitur spesifik sampai PRD dibaca; siapkan kontrak agar UI tidak bergantung pada satu opsi | BYPASSED; status workaround aktual ada di tabel implementasi; tinjau pada S0-04 |

Bukti data historis: [resource riset](../../outputs/dividend-research/riset-dividen.md), [audit data](../../outputs/sectors-data-audit.json), [konflik jadwal](../../outputs/dividend-research/schedule-conflict-evidence.json), [hasil studi](../../outputs/dividend-research/study-results.json).

## Format bug baru

```text
ID dan tanggal ditemukan:
Jenis / prioritas / status:
Task dan requirement terkait:
Langkah reproduksi:
Perilaku yang diharapkan:
Perilaku aktual dan bukti:
Dampak terhadap MVP:
Penyebab: diketahui atau masih hipotesis
Workaround atau bypass dan batasnya:
Tindakan lanjutan / pemicu untuk ditinjau lagi:
Perbaikan dan bukti verifikasi saat selesai:
```

Bug yang ditemukan saat testing akhir masuk log yang sama dengan penanda tahap testing. Jangan menghapus temuan yang selesai; pertahankan penyebab, perbaikan dan bukti. Fitur yang dibypass tetapi diwajibkan PRD tetap menjadi gap delivery, kecuali PM mengubah scope.

## Temuan implementasi 6 Oktober 2026

- **ISS-010 — Environment / P1 / BYPASSED:** Docker daemon tidak aktif dan PostgreSQL/Redis lokal tidak tersedia. SQLAlchemy memakai SQLite lokal; job memakai thread worker dengan penyimpanan status. PostgreSQL belum diuji, Redis/RQ belum terpasang. Bukan worker durable lintas server. Tinjau sebelum deployment.
- **ISS-011 — Dependency / P2 / RESOLVED:** instalasi Bun gagal menyelesaikan rentang Next ^16.0.0 walau registry menyediakan 16.3.8. Pin Next.js dan eslint-config-next 16.3.8 berhasil; Bun lock tersimpan, build/lint lolos. Cache npm default menolak write; cache task di /private/tmp berhasil.

- **ISS-012 — Dev server / P1 / BYPASSED:** Next dev mengulang restart dengan EMFILE (terlalu banyak file watcher) di workspace campuran Python/Node. Server frontend tidak stabil sehingga preview menolak koneksi. Mengganti dev ke webpack polling dan mengabaikan .venv/outputs/work/.runtime; production build + start tanpa watcher telah berhasil HTTP200 dan alur browser. Dev polling belum diverifikasi ulang; jalur preview menjadi pilihan yang telah diuji.

- **ISS-013 — Storage / P1 / BYPASSED:** MVP memakai record JSON SQLAlchemy untuk watchlist, rules dan run; dataset immutable JSON dibaca dari snapshot. Normalized schema, migration history, multi-user isolation dan provenance relational ditunda. Run menyimpan dataset fingerprint dan versi engine; nilai null tetap null.
- **ISS-014 — Kebenaran UI / P1 / RESOLVED:** detail BBCA sempat memberi label siap replay untuk Desember 2025 walau UI hanya replay Maret–Mei, dan tabel riwayat mencampur 2026 parsial serta 2021 yang basis splitnya bermasalah. Eligibility kini dibatasi jendela replay; tabel histori hanya 2022–2025 dengan catatan basis DPS. Uji data memeriksa lima event eligible.
- **ISS-015 — Kalkulasi / P1 / RESOLVED:** durasi modal tertahan awalnya berhenti pada tanggal jual, belum settlement. Kini sampai settlement atau batas observasi; fixture membuktikan 5 hari dari cum sampai T+2. Engine dinaikkan replay-v1.1; hasil v1 yang pernah disimpan tetap bertanda versi lama.
- **ISS-016 — Dependency / P2 / DEFERRED:** Starlette TestClient memberi peringatan deprecation httpx (menganjurkan httpx2). Sebelas pemeriksaan awal tetap lolos. Tidak mengganti runtime demi peringatan; tinjau saat update dependensi.

## Status bypass data dan scope yang sudah diterapkan

| ID awal | Status implementasi | Workaround nyata / sisa pekerjaan |
|---|---|---|
| ISS-001 | OPEN | Lampiran tetap belum tersedia; baseline C-01 sampai C-08 dibangun, bukan klaim coverage PRD. |
| ISS-002 | BYPASSED | Declaration tampil Belum tersedia dalam lima titik timeline; prediksi tanggal belum dibuat. |
| ISS-003 | BYPASSED | Snapshot kalender terkini UNTR/ASGR tidak dipakai. Replay dibatasi lima event historis; validator menahan konflik tanggal/DPS dan tidak membuka karantina saat reimport. |
| ISS-004 | BYPASSED | ITMG2026 tidak dimasukkan dalam dataset replay. Validasi currency lintas seluruh universe tetap TODO. |
| ISS-005 | BYPASSED | Replay BBCA hanya2025; studi2022–2025; tabel DPS menampilkan2022–2025 dan catatan basis, tanpa2021. |
| ISS-006 | BYPASSED | UI menampilkan statistik8 event, tidak menampilkan probabilitas/forecast fiktif. Model tervalidasi dan proyeksi tetap gap. |
| ISS-007 | BYPASSED | Engine tidak memakai lapkeu sebagai fitur. Model publikasi point-in-time tetap gap. |
| ISS-008 | BYPASSED | T+2 memakai sesi teramati dataset dan disebut sebagai asumsi. Validasi kalender resmi dan suspensi tetap gap sebelum ekspansi. |
| ISS-009 | BYPASSED | Watchlist/rules/run disimpan di server lokal, bind localhost, tanpa akun. Multi-user/cloud belum ada. |

- **ISS-017 — UI angka / P1 / RESOLVED:** formatter rupiah tanpa desimal membuat DPS kecil terlihat Rp0. UI sekarang menampilkan hingga4 desimal; kalkulasi Decimal tidak berubah.
- **ISS-018 — Product / P2 / DEFERRED:** navigasi area menggunakan state lokal; tautan langsung ke run/halaman dan pemulihan tab setelah refresh belum dibuat. Riwayat dan watchlist tetap tersimpan di server.

- **ISS-019 — Form / P1 / RESOLVED:** ketika input tanggal diubah lewat browser automation, nilai terlihat berubah tetapi submission memakai state React lama. Reproduksi menghasilkan run sampai20 Mei meskipun field terlihat21 Maret. Form submission kini membaca tanggal, modal dan batas sesi dari FormData sebagai nilai yang tampil; verifikasi browser berhasil:21 Maret ditolak untuk event April; mengubah kembali ke20 Mei menghasilkan completed. Penyebab event native/React belum dipastikan.

- **ISS-020 — Usability / P2 / RESOLVED:** perpindahan area kini mengembalikan scroll ke atas; riwayat run tetap tersedia pada mobile; ikon navigasi dan brand diberi accessible name; polling berhenti jika endpoint run error. Pemeriksaan akhir memastikan viewport mobile tidak overflow.

## Sprint intelligence — 6 Oktober 2026

- **ISS-021 — Provider / P1 / RESOLVED:** 23 dari 48 permintaan harga pada batch pertama ditolak `429 RATE_LIMIT_EXCEEDED`. Probe menyimpan pesan provider teredaksi di outputs/intelligence/price-probe-error.json. Kolektor memakai cache, jeda, dua worker dan satu retry setelah 65 detik. Batch lanjutan berhasil; 48 snapshot harga tersedia. Tidak menyamakan rate limit dengan ketiadaan data. Untuk universe lebih besar, scheduler dengan rate budget tetap TODO.
- **ISS-022 — Data / P1 / BYPASSED:** empat event BMRI/BBNI 2022–2023 mendahului stock split yang tercatat Sectors. DPS historis dan OHLC belum terbukti berbasis saham yang sama. Event tetap masuk audit, tetapi dikeluarkan dari statistik/skenario; tidak menebak faktor penyesuaian. Verifikasi basis dan metadata currency sebelum membuka karantina. Nominal DPS event lain diperlakukan sebagai IDR; metadata mata uang eksplisit per event masih tidak tersedia.
- **ISS-023 — Research / P1 / BYPASSED:** ADRO ex2024-11-28 memiliki ex-dividen berikutnya pada2024-12-30 sebelum t20. Memotong observasi di t19 mencegah pencampuran dua hak dividen. Event masih masuk KM sebagai censored, tidak masuk proporsi return lengkap t20. Censoring semacam ini bisa informatif; interpretasi prediktif KM belum valid. Risiko/kurva tetap diberi label eksploratif.
- **ISS-024 — Scope / P1 / OPEN:** engine baru adalah proporsi empiris+Wilson, KM, ranking eksplisit dan stress test satu posisi berbasis analog. Belum ada trained/calibrated trap model, proyeksi tanggal pengumuman, kalender future terkonfirmasi, atau optimizer rotasi forward. Input tanggal/harga/DPS skenario diberi label hipotetis; rotasi dengan kas/T+2 tetap melalui replay historis lama. S4-02 tetap BYPASSED pada bagian forecast tervalidasi.
- **ISS-025 — Statistics / P1 / RESOLVED:** kurva KM berpotensi tampak berlanjut setelah seluruh sampel tersensor dini. Tail kini null setelah observasi terakhir bila belum semua pulih. Uji tied recovery/censor, median tak tercapai, dan tail tanpa dukungan lolos. Perhitungan tanda gross return serta BEP total memakai Decimal untuk menghindari pembulatan floating point di nol.
- **ISS-026 — UI / P2 / RESOLVED:** header global semula tetap menulis2025 saat membuka intelligence2022–2025. Header kini mengikuti view; Metodologi dan tautan detail membedakan studi lama entry-cum dari aturan intelligence yang dapat diubah. Pesan validasi API ditampilkan agar urutan tanggal invalid dapat diperbaiki dari form.
- **ISS-027 — Visual / P2 / RESOLVED:** label sumbu default ECharts terlalu gelap pada grafik skenario/pemulihan. Warna eksplisit #b1a3b6 diterapkan; build lolos dan screenshot mobile390 membuktikan sumbu terbaca. Saat QA, override viewport perlu diterapkan kembali setelah reload karena ukuran DOM sempat651 walau capture390; ini perilaku alat, bukan overflow aplikasi. Pemeriksaan memakai ukuran DOM aktual390/scrollWidth390.

## Sprint integrasi rotasi — 6 Oktober 2026

- **ISS-028 — Integrasi / P1 / RESOLVED:** katalog lama berisi 50 event pasar dan replay hanya lima event Maret–Mei, sementara Intelligence memakai 48 event sembilan emiten. `UnifiedDataset` kini memakai ID/tanggal/DPS/audit yang sama dengan Intelligence untuk 12 event tahun 2025. Harga kontinu ditambah 50 snapshot MCP (45 harga, 5 IHSG). Tahun 2022–2024 tetap histori statistik, bukan tambahan event 2025. Snapshot/hasil legacy tetap disimpan dengan versi lama.
- **ISS-029 — Sesi pasar / P1 / BYPASSED:** IHSG tidak memuat 2/6/7 Mei dan 20 Oktober 2025, padahal kesembilan emiten memiliki OHLCV valid. Tanpa perbaikan, DMAS gagal eligibility dan T+2/holding bergeser. Sesi dilengkapi dari konsensus seluruh sembilan feed, diaudit di `session_repairs`; uji memastikan 30 April → settlement 5 Mei. Kalender resmi/suspensi tetap perlu verifikasi sebelum produksi.
- **ISS-030 — Bias waktu / P1 / BYPASSED:** ranking histori penuh akan membocorkan outcome 2025 ke keputusan awal 2025. Planner memotong event dan bar sebelum tanggal keputusan, mempertahankan event belum selesai sebagai censored, membekukan rute sebelum replay. Uji mengubah harga masa depan 7× tanpa mengubah ranking/rute lulus. Timestamp declaration, vintage lapkeu/snapshot dan bias pemilihan universe tetap belum teratasi; asumsi kalender eksplisit, mode verified-only menghasilkan nol rute.
- **ISS-031 — Hak dividen / P1 / RESOLVED:** pembatasan satu event per emiten pada replay lama tidak dapat mewakili rotasi setahun atau dividen kedua saat holding. Engine v2 mengizinkan beberapa lot dan membukukan setiap hak pada seluruh lot yang memenuhi syarat, termasuk event yang tidak dipilih. Fixture dua lot membuktikan hak pertama+kedua tidak hilang atau ganda. Payment-close juga dibatasi holding limit; piutang tetap disimpan setelah jual.
- **ISS-032 — Optimasi / P2 / DEFERRED:** rute menggunakan tiga heuristik deterministik dan deduplikasi; bukan pencarian optimum global atau proyeksi rotasi masa depan. Tidak memberi label “rute terbaik” dari realized return. All-in pertama, split per event dan rotasi kas memakai modal/awal/akhir sama; data risiko yang tampil adalah drawdown historis. Validasi prediktif dan optimizer forward tetap gap ISS-024.
- **ISS-033 — Input tanggal / P1 / RESOLVED:** QA planner mengisi 15 Juni tetapi rencana sempat memakai30 Juni setelah checkbox diubah; pola yang sama dengan ISS-019. Handler `onInput` menyinkronkan date field sebelum render lain, submit juga membaca FormData. Browser sesudah build membuktikan Rp50 juta/15 Juni tetap tersimpan sesudah checkbox diubah. Perbaikan diterapkan pada tanggal awal/akhir planner dan simulator manual.
- **ISS-034 — Riwayat / P2 / RESOLVED:** daftar history dapat berhenti polling saat job detail completed, sementara fetch history terakhir masih running. Polling daftar kini mengikuti status item daftar itu sendiri, sampai daftar menerima terminal state. Perbaikan berlaku untuk replay manual dan planner. Bukti browser dicatat di VERIFICATION.md.


## Pemeriksaan kesiapan lanjutan — Q-01–Q-03

- **ISS-035 — Alur pilihan / P1 / RESOLVED:** callback detail→simulator hanya mengganti menu sehingga pilihan DMAS/RALS/BBCA-Desember hilang dan form memakai tiga event contoh Maret–April. Detail kini memberi tombol per event dengan ID eksplisit; simulator menerima ID itu, memilih satu event, dan mengatur periode awal ke cakupan2025 dengan label agar dapat disunting. Sidebar Simulator tetap membuka contoh umum. Build/typecheck lulus. Browser membuktikan ADROex30Des2025 saja yang dicentang; hasil run52c72d21 memakai ID yang sama dan tampil setelah reload.
- **ISS-036 — Presisi / P1 / RESOLVED:** return dihitung dari NAV yang sudah dibulatkan empat desimal. Modal1,00009 tanpa transaksi dapat menampilkan +0,001%, dan0,000001 dapat menampilkan−100%, padahal saldo tidak berubah. Perhitungan gross PnL/return kini memakai Decimal NAV sebelum pembulatan; pembulatan hanya untuk penyajian. Tiga fixture saldo pecahan menghasilkan PnL/return0. Engine replay-v2.1 (legacy-v1.2); hasil tersimpan lama tidak ditimpa.
- **ISS-037 — Kontrak API / P2 / RESOLVED:** endpoint simulation detail menerima record rotation-run karena hanya memeriksa field status. Objek dengan kontrak berbeda berpotensi dibaca sebagai hasil manual. Store sekarang dapat memfilter kind, ketiga endpoint detail memakai jenis record yang tepat. Tes silang ID antar-endpoint menghasilkan404; riwayat asli tetap bisa dibuka.

- **ISS-038 — Tanggal lintas tahun / P2 / RESOLVED:** detail berjudul timeline2025 sebelumnya menampilkan recording2Jan/payment15Jan tanpa tahun; hasil juga menampilkan settlement5Jan tanpa tahun. Semua tanggal timeline, jejak entry/exit/settlement/payment dan ledger kini menampilkan tahun. Browser membuktikan akhirreplay31Des2025,settlement5Jan2026,payment15Jan2026. Label riwayat memakai jumlah event, bukan jumlah emiten; kartu perbandingan menjelaskan posisi dibeli, bukan posisi yang masih terbuka. Mobile390tidakoverflow.

- **ISS-039 — Riwayat / P1 / RESOLVED:** membuka hasil manual lama hanya mengganti job ID/alokasi, tetapi form tetap memuat draf berbeda. Header hasil tidak menyebut entry/exit/holding/event sehingga pembaca dapat salah mengaitkan aturan dengan PnL. Snapshot input asli kini ditampilkan bersama versi, status beda draf, dan tombol salin eksplisit. Salin tidak menghitung ulang atau menimpa hasil; event yang tak tersedia pada dataset aktif menonaktifkan salin. Riwayat diberi ID, emiten, tanggal akhir dan opsi lihat semua. Browser membuktikan copy→ubah satu exit→hasil baru→reload→hasil lama; API menyatakan original unchanged. Legacy tanpa start_date eksplisit memakai awal periode hasil, versi dataset tak tercatat tetap berlabel demikian. Desktop/mobile dan console diperiksa. Terkait U-01 dan PM-07; penilaian pemahaman PM tetap menunggu.

- **ISS-040 — Relokasi / P2 / BYPASSED:** sistem menolak `rename` akar workspace aktif dari bro ke horizon dengan Operation not permitted, meski izin filesystem asal/tujuan sudah diberikan. Proyek disalin lengkap ke horizon; virtualenv/path pendukung diperbaiki dan build/40tes lulus di sana. Sumber lama tidak dihapus. Penyelesaian pemindahan dan pemilihan workspace baru perlu dilakukan di luar sandbox; jangan menganggap salinan berarti folder asal sudah hilang. Terkait M-01.

- **ISS-041 — Kelengkapan overlay lima tahun / P1 / OPEN:** audit2021–2025menemukan170kandidat dengan kalender lima tahun, tetapi1.900record kalender tidak memuat declaration. Contoh LPPF mempunyai lima jendela harga, sementara feed AGM tidak memuat2021dan hasil rapat2022–2025null; hubungan declaration-event belum terverifikasi. Query newsBBCAkeyworddividen2021/2025kosong, belum merupakan audit seluruh berita/filing provider. Seluruh sesi harga, basis adjustment/unit dan pemilihan final/interim juga belum diverifikasi. Daftar strict eligibility kosong karena verifikasi belum selesai, bukan bukti tidak ada emiten yang mungkin lengkap. Tidak melonggarkan syarat PM atau mengosongkan katalog lama; tahap ini hanya rancangan. Lanjut penelusuran declaration di Sectors dan verifikasi jendela kandidat sebelum mengaktifkan overlay. Terkait T-01, ISS-002/005/022.

Pembaruan 8 Oktober: PM menghapus syarat lima tahun lengkap **untuk penemuan nama emiten**. ISS-041 tetap OPEN hanya sebagai syarat overlay grafik terverifikasi; daftar kandidat D-03 tidak disaring oleh gate tersebut. Kalimat historis di atas menggambarkan scope saat audit awal.

Pembaruan berikutnya 8 Oktober (T-08): PM juga melepas syarat lima tahun penuh **untuk menampilkan grafik**. Pratinjau lima kandidat kini menampilkan jendela yang tersedia dan menandai tahun kosong. ISS-041 tetap OPEN untuk verifikasi per event (declaration/RUPS terkait, kelengkapan harga, basis penyesuaian, dan jenis siklus), bukan sebagai larangan menampilkan data parsial. Pernyataan gate lima tahun sebelumnya disimpan sebagai riwayat keputusan.

- **ISS-042 — Engine prediksi periode berjalan / P2 / OPEN untuk F-02:** PM sebelumnya menunda perhitungan prediksi. Permintaan integrasi 8 Oktober menghidupkan kembali topik tersebut: BR-04 menampilkan engine statistik historis yang sudah ada dalam desain baru, namun F-01 masih [hipotesis rumus versi 0.1](./PREDICTION_FORMULA.md). Belum ada dataset point-in-time/holdout bersih, training, kalibrasi, atau nilai forecast numerik yang layak diklaim. Endpoint tetap `forecast.status = not_available`; angka historis diberi label, bukan probabilitas periode berikutnya. F-02 mencatat implementasi dan validasi yang masih diperlukan. Terkait T-02/ISS-024/ISS-041.

- **ISS-043 — Navigasi mobile / P2 / RESOLVED:** penambahan menu Timeline membuat navigasi delapan ikon melebar sampai408px pada viewport390px. DOM membuktikan sumber overflow adalah nav dan tombol terakhir. Nav kini mempunyai min-width0, scroll horizontal internal dan lebar tombol tetap; setelah rebuild, viewport390/scrollWidth390, nav312/scrollWidth353. Browser membuktikan fokus keyboard2023dan mode2026tetap bekerja. Terkait T-05.

Implementasi T-03/T-04 memasang gate ISS-041 di server dan menampilkan pratinjau LPPF terpisah dengan peringatan. ISS-041 tetap OPEN karena tidak ada emiten yang disahkan lengkap. ISS-042 tetap DEFERRED; UI hanya menyediakan tempat prediksi kosong. Ketersediaan grafik tidak menutup kedua gap tersebut.

## Migrasi Supabase — 7 Oktober 2026

- **ISS-044 — Worker cloud / P1 / RESOLVED untuk MVP satu proses:** startup sebelumnya menandai seluruh job queued/running sebagai failed tanpa membedakan backend pemilik. Dengan database bersama, startup proses kedua dapat mengganggu job proses pertama (jalur kode terbukti; belum ada kehilangan data pengguna yang diamati). Runtime PostgreSQL kini mengambil advisory lock sesi sebelum recovery job; percobaan lease kedua di cloud ditolak, tanpa mengubah20record asli. Tetap satu local-thread worker process, bukan queue durable/lease dengan failover. Bukti `supabase-verification.json`; terkait DB-03 dan ISS-010.
- **ISS-045 — Upsert PostgreSQL / P1 / RESOLVED:** cloud smoke gagal dengan ValueError pada jalur tulis setelah migrasi20record berhasil diverifikasi. Diagnosis terhadap query asli membuktikan `rowcount=-1` pada insert/upsert psycopg/SQLAlchemy; pemeriksaan `rowcount != 1` salah menganggap insert sebagai konflik dan rollback. Implementasi diperbaiki memakai RETURNING key untuk memeriksa keberhasilan insert/update secara eksplisit. Query diagnosis di-rollback, record probe dibersihkan, source SQLite tidak diubah.57tes lokal lulus sesudah perbaikan; cloud smoke read/insert/update/kind guard dan timestamp lulus. Checksum20record asli tetap sama. Bukti `supabase-verification.json`; terkait DB-03.

ISS-010/ISS-013 tidak otomatis tertutup seluruhnya oleh database cloud: worker durable, schema domain ternormalisasi, pemindahan market snapshots dan isolasi multi-user masih belum dibuat. Migrasi record memiliki schema/version dan akun backend sendiri. ISS-009 (akun pengguna) tetap berlaku; kredensial Supabase bukan implementasi login.

## Feedback UI UX-01 — 7 Oktober 2026

- **ISS-052 — Input / P2 / RESOLVED:** setelah modal50juta valid dan hasil tersimpan, paste `1e8` ditolak sehingga tampilan tetap50.000.000 tetapi customValidity invalid. Menekan “Gunakan input hasil ini” dengan nilai angka sama sebelumnya tidak menghapus error; browser membuktikan form tetap invalid. Komponen hanya menyinkronkan draf ketika nilai sumber berubah. Reset eksplisit saat salin hasil kini menyinkronkan raw/error walau nominal sama, sambil mempertahankan elemen/fokus input. Regresi browser production membuktikan display50.000.000, canonical50000000 dan validitytrue/messagekosong. Terkait UX-01/C-04/S5-02; bukti di ui-feedback-verification.json. Ini perbaikan penyebab yang teramati, bukan tebakan gejala.
- **ISS-053 — Kosmetik / P3 / OPEN:** browser production meminta `/favicon.ico` dan menerima404; console mencatat failed resource untuk URL itu. Tidak ada pageerror atau warning pada pemeriksaan alur utama. Favicon belum ditambahkan karena di luar scope feedback ini; tidak menghambat input, simulasi, timeline atau setup lokal. Terkait UX-01/S5-02.

## Fokus demo D-01 — arahan PM 7 Oktober 2026

- **ISS-054 — Alur demo / P1 / OPEN:** landing analisis kini langsung membuka pratinjau LPPF, tetapi navigasi ke Simulator masih membuka form replay historis multi-event dengan pilihan default BBCA/BMRI/LPPF. Identitas emiten yang dianalisis belum diteruskan dan simulasi satu dividend play belum ada. Dampak: urutan analisis → simulator sudah terlihat, tetapi belum menjadi satu alur keputusan emiten yang koheren. D-01 hanya merapikan pintu masuk/navigasi; jangan mengklaim integrasi selesai. Tindak lanjut pada chunk simulator terpisah, setelah kontrak dan asumsi perhitungan diperiksa. Nomor asal UI ISS-046 dipetakan ke ISS-054 saat BR-02; issue UI asal044/045 menjadi052/053 agar tidak bertabrakan dengan migrasi/deployment.

## Deployment frontend V-01 — 8 Oktober 2026

- **ISS-055 — Akses environment / P1 / RESOLVED:** setelah PM memberi izin eksplisit, BACKEND_URL dan HORIZON_API_KEY berhasil dikirim melalui stdin privat ke Vercel project horizon, target Preview/Production. Env ls memverifikasi URL bertipe Config dan key bertipe Secret. MCP403 menggunakan fallback CLI resmi dengan scope sama. Integrasi Git otomatis secara terpisah ditolak approval review (akses lintas layanan) dan belum diaktifkan; PM mengambil alih deployment. Tidak ada secret dalam Git/frontend.

- **ISS-056 — Target deployment pertama / P2 / OPEN:** CLI62.7.0 dipanggil --target preview tetapi deployment pertama project baru diterima sebagai Production dan diberi alias. Build berhasil, env kosong; deployment yang baru dibuat dihapus untuk menghindari penyerahan situs belum terhubung. Source CLI juga menyebut perilaku first deployment → production. --skip-domain hanya untuk Production; kombinasi dengan Preview ditolak sebelum deploy. Verifikasi target aktual dan domain sebelum melanjutkan main; belum ada Preview end-to-end.

Update ISS-056: percobaan berikutnya dari source4588681 juga diterima Production/READY walau --target preview; URL https://horizon-nu-kohl.vercel.app. Proses sudah selesai saat PM meminta handoff. Tidak dihapus atau dilanjutkan pengujiannya karena PM mengambil alih deployment; belum ada Preview end-to-end.

## Penemuan kandidat D-03 — 8 Oktober 2026

- **ISS-057 — Kualitas ranking kandidat / P1 / OPEN:** daftar lima emiten memakai `total_yield[2025]` dan `total_dividend[2025]` dari snapshot MCP Sectors, tanpa gate kelengkapan grafik lima tahun sesuai keputusan PM. Yield tahunan provider tidak mengukur yield pembelian saat ini, sustainability dividen, likuiditas, harga setelah ex-date, maupun proyeksi laba/risiko. Tampilkan sebagai **peringkat historis 2025**, bukan rekomendasi atau hasil strategi; snapshot tidak diperbarui otomatis. Lanjutan: tentukan objective dan cutoff keputusan, audit basis yield/aksi korporasi, ambil event/harga yang tersedia, lalu validasi ranking peluang strategi sebelum mengganti label historis. Terkait D-03/C-01/C-02/S4-02.

- **ISS-058 — Cakupan periode berjalan / P2 / OPEN:** pada T-08, snapshot harga/dividen 2026 untuk timeline periode berjalan hanya tersedia pada LPPF. DMAS, ADRO, CFIN, dan RALS mempunyai jendela historis parsial dari cache 2022–2025, tetapi kontrol 2026 dinonaktifkan agar tidak menampilkan grafik kosong seolah data aktual ada. Ini kekurangan snapshot produk, bukan bukti emiten tidak membayar dividen pada 2026. Lanjutkan koleksi Sectors MCP + REST dan audit hubungan event/harga bila periode berjalan untuk emiten lain diprioritaskan; prediksi tetap ISS-042.

## Integrasi UI editorial dengan grafik parsial — 8 Oktober 2026

- **ISS-059 — Integrasi / P1 / RESOLVED pada branch BR-04:** dry run BR-03 terhadap `origin/feat/timeline-ui-polish` `dbf21b6` menemukan empat konflik konten dan risiko regresi semantik. Branch integrasi lokal kini mempertahankan desain editorial dan mem-port T-08: lima kandidat, fokus ID event, gap eksplisit, dan tab 2026 hanya saat snapshot ada. Task hierarki UI diberi ID `UI-03`; `D-03` tetap discovery. Browser membuktikan sembilan seri ADRO, fokus 28Nov/30Des2024 berbeda, empat emiten lain dan mobile390px tanpa overflow. Forecast numerik tetap gap terpisah ISS-042; penyelesaian konflik lokal belum berarti merge ke main, push, deploy, atau UAT. Terkait BR-03/BR-04/C-02/C-08/T-08.

## AI-02 — Batas analisis dan arsip — 8 Oktober 2026

- **ISS-060 — Kualitas konteks AI / P2 / OPEN:** endpoint insight tersedia, tetapi histori timeline memiliki identitas siklus/basis harga/kelengkapan sesi yang belum seluruhnya diverifikasi. Distribusi event tanpa klasifikasi hanya pratinjau deskriptif; tidak boleh dijadikan rata-rata tahunan comparable atau prediksi risiko. News MCP LPPF sekitar26April2023 dan corporate action12April–10Mei2023 kosong pada smoke live; ini gap arsip, bukan bukti tidak ada kejadian. Fundamental time-aligned dan benchmark sektor belum ditelusuri (IHSG tersedia sebagai konteks pasar luas). Source IDs/schema divalidasi tetapi narasi model masih perlu penilaian pengguna; endpoint tidak membuktikan kausalitas. Tindak lanjut: audit basis split/cycle/sesi, verifikasi coverage arsip, evaluasi narasi dengan sampel nyata, dan putuskan scope fundamental/benchmark sebelum klaim riset menyeluruh. Detail/bukti [AI_INSIGHTS.md](./AI_INSIGHTS.md). Fitur tidak menutup forecast ISS-042 atau UAT.

ISS-060 update guard PM: retry lama per alokasi sudah diganti budget durable maksimal tiga attempt total per run. Success direuse permanen; gagal ketiga tidak ada output AI dan tidak mencoba lagi. Failed model/provider tetap tidak memblokir replay; ini bukan bukti seluruh kesimpulan narasi benar.

## SIM-UX-02-MOBILE — Header transaksi pada ponsel — 8 Oktober 2026

**RESOLVED:** browser real dengan replay equal LPPF pada viewport390px menunjukkan `scrollWidth`399px; header status “Masih dipegang” bersama laba Rp2.508.000 memaksa sisi kanan nominal ke398,6px. Wrapping hanya pada header transaksi mobile memperbaiki dokumen menjadi390px. Isi tabel cash flow tetap memiliki scroll horizontal lokal saat dibuka. Bukti dan batas pemeriksaan: `outputs/development/ai-insight-live-browser.json`; ini perbaikan layout yang diamati, bukan perubahan perhitungan.

ISS-060 update agentic IDX: gateway kini32toolIDX, dipilih model dalam2ronde; source/gap/evidence disimpan. Fundamental/corporate/sector data dapat ditelusuri sesuai tool terpilih dan coverage, tetapi report-period tanpa publication/vintage tetap retrospektif; current snapshot tidak boleh diklaim informasi saatkejadian. Budget6dispatch/12credit/40detik dapat meninggalkan gap. Smoke live menunjukkan news arsip kosong dan dua rejected queries, bukan penyebab pasar terbukti. Window replayend dan provenance URL IHSG telah diperbaiki dengan regression; cachedsuccess lama sengaja dipertahankan. Risiko narasi model/kualitas arsip/basis split/cycle/sesi masih terbuka; tidak menutup prediction ISS-042 atau UAT.
