# Rencana sprint MVP simulator rotasi dividen

Tanggal: 6 Oktober 2026. Versi: 0.1. Pemilik produk: pengguna sebagai PM. Pelaksana development: Codex.

Tujuan sprint adalah menyelesaikan alur MVP sesuai PRD dan user story, mencatat setiap task yang selesai, serta menjaga agar temuan tambahan tidak mengalihkan pekerjaan dari delivery. FastAPI sudah dipilih PM; optimasi performa bukan prioritas saat ini. Testing akhir akan dibahas bersama PM setelah development siap.

**Status sumber: draft berdasarkan percakapan. Lampiran PRD dan user story belum terlihat pada pesan atau workspace, dan daftar artifact chat kosong saat diperiksa. Dokumen riset dan arsitektur bukan pengganti PRD tersebut.** Permintaan path atau tautan sumber sudah dikirim; pemetaan final belum dapat dinyatakan selesai.

## Acuan dan keputusan yang berlaku

| Acuan | Status | Cara dipakai |
|---|---|---|
| Instruksi terbaru PM dalam chat | Tersedia | FastAPI, fokus scope MVP, log progres/temuan, bypass sementara, testing akhir dibahas kemudian |
| Lampiran PRD | Menunggu lokasi sumber | Menentukan kebutuhan, batas MVP dan acceptance criteria final |
| Lampiran user story | Menunggu lokasi sumber | Menentukan alur pengguna dan pemetaan setiap task |
| [Arsitektur yang sudah diriset](../../outputs/dividend-research/arsitektur-sistem.md) | Tersedia; proposal teknis | Menjadi referensi pemecahan komponen, bukan bukti fitur sudah dibangun |
| [Resource riset](../../outputs/dividend-research/riset-dividen.md) | Tersedia; snapshot riset | Menjadi sumber temuan data, formula dan batas model |
| [Audit data](../../outputs/sectors-data-audit.json) | Tersedia; snapshot historis | Mengidentifikasi masalah integrasi awal; status data live tetap perlu dicek saat dipakai |

Instruksi PM terbaru mengarahkan pekerjaan. Setelah PRD/user story tersedia, gunakan ID serta acceptance criteria aslinya, tandai konflik dengan keputusan percakapan, dan ubah task terkait secara terarah. Jangan menambah fitur atau menghapus requirement hanya untuk membuat rencana tampak selesai.

Keputusan produk yang sudah tercatat: sumber finansial Sectors; pengguna mengeksekusi order sendiri; bandingkan all-in dan pembagian modal; BEP harga mengikuti harga beli; hasil versi awal di luar biaya transaksi, pajak dan slippage. Source data yang belum tersedia tidak boleh diganti angka rekaan.

## Stack kerja

Backend FastAPI sudah disepakati. Baseline teknis lanjutan dari proposal sebelumnya: Next.js/React/TypeScript untuk frontend; Tailwind dan shadcn/ui; TanStack Query/Table; ECharts; Python untuk simulator dan statistik; PostgreSQL untuk data; pandas/NumPy/Parquet untuk riset; lifelines dan scikit-learn untuk baseline analisis. RQ/Redis dipakai saat alur pekerjaan background dibangun. Pilihan hosting dan autentikasi mengikuti kebutuhan PRD; belum ada deployment atau layanan berbayar yang diprovisikan.

Mulai dengan satu repository, backend modular dan worker yang berbagi package Python. Definisi request/response berada pada schema backend dan kontrak API. Semua kalkulasi finansial resmi berjalan di engine yang sama, bukan salinan formula frontend.

## Urutan sprint

Urutan di bawah adalah urutan pengerjaan, bukan estimasi hari atau komitmen tanggal. Detail fitur pada sprint 2–5 menunggu rekonsiliasi PRD.

| Sprint | Tujuan | Hasil yang bisa ditinjau |
|---|---|---|
| 0 | Menetapkan acuan dan sistem pencatatan | Pemetaan PRD/story ke task, acceptance criteria, progress log dan issue log |
| 1 | Menjalankan fondasi aplikasi | Frontend dan FastAPI dapat dijalankan lokal; koneksi database, schema dasar, layout dan konfigurasi tersedia |
| 2 | Menyambungkan data ke alur eksplorasi | Data Sectors masuk aplikasi; pengguna dapat menemukan kandidat, melihat detail/timeline dan mengelola watchlist sesuai PRD |
| 3 | Menyelesaikan simulator | Input modal/aturan masuk-keluar menghasilkan perhitungan saham, dividen, kas dan alternatif alokasi/rute |
| 4 | Menampilkan risiko dan pemulihan | Statistik historis, BEP, kasus belum pulih dan skenario tampil dengan sumber/metode yang jelas; kebutuhan prediksi mengikuti PRD |
| 5 | Menyatukan alur MVP dan menyiapkan delivery | Alur utama terhubung, state penting tertangani, instruksi menjalankan aplikasi dan daftar keterbatasan tersedia |
| 6 | Testing akhir bersama PM | Ruang lingkup, skenario, lingkungan dan kriteria kelulusan dibahas kemudian; hasil dicatat saat benar-benar diuji |

Target demonstrasi sementara: pengguna menemukan event → memeriksa timeline → memilih emiten/modal/aturan → menjalankan simulasi → membandingkan hasil gross, risiko dan waktu modal tertahan. Autentikasi, persistensi lintas perangkat, ekspor dan fitur lain tidak otomatis masuk scope sebelum PRD dibaca.

## Backlog yang dapat dilacak

ID `C-*` pada kolom sumber merujuk baseline percakapan di [TRACEABILITY.md](./TRACEABILITY.md), belum merupakan ID user story lampiran.

| Task | Pekerjaan | Sumber sementara | Ketergantungan | Bukti selesai yang diharapkan |
|---|---|---|---|---|
| S0-01 | Inventaris workspace, artifact dan dokumen acuan | Instruksi PM | — | Lokasi sumber dan gap dicatat |
| S0-02 | Siapkan rencana, traceability, progress, issue log dan panduan kerja | Instruksi PM | S0-01 | Berkas tersimpan dan tautan diperiksa |
| S0-03 | Baca PRD dan user story lampiran | PRD/US belum diterima | Lokasi dokumen | Versi sumber dan requirement asli tercatat |
| S0-04 | Rekonsiliasi backlog dan acceptance criteria dengan dokumen asli | PRD/US belum diterima | S0-03 | Setiap requirement punya task; scope yang belum jelas ditandai |
| S1-01 | Scaffold frontend, FastAPI dan konfigurasi lokal | FastAPI disetujui | — | Aplikasi berjalan; rahasia server tidak masuk frontend |
| S1-02 | Schema domain, database/migrasi dan kontrak API | C-04, C-08 | S1-01 | Struktur event, harga, aturan dan run tersimpan serta terbaca |
| S1-03 | Layout/navigasi dan komponen UI dasar | C-01–C-05 | S0-04, S1-01 | Halaman sesuai alur PRD dapat dinavigasi |
| S2-01 | Adapter Sectors MCP dan kalender REST, cache serta impor snapshot | C-01, C-02, C-08 | S1-02 | Respons nyata dinormalisasi; asal dan waktu data tercatat |
| S2-02 | Validasi data, null, duplikasi dan konflik jadwal | C-02, C-08 | S2-01 | Event ambigu diberi status; tidak diam-diam dihitung sebagai valid |
| S2-03 | Discovery/screener sesuai logika tim | C-01, C-07 | S0-04, S2-02, S1-03 | Filter dan urutan bekerja dengan penjelasan sumber metrik |
| S2-04 | Detail emiten, kalender/timeline dan watchlist | C-02, C-03 | S0-04, S2-02, S1-03 | Lima tahap timeline dan kondisi data kosong tampil; pilihan emiten dapat dikelola |
| S3-01 | Core simulator dan ledger keuangan | C-04, C-08 | S1-02 | Lot, posisi, kas, hak dividen dan hasil jual konsisten |
| S3-02 | Aturan entry/exit, BEP dan batas pengamatan | C-04, C-06, C-07 | S3-01 | Aturan eksplisit dijalankan tanpa memakai informasi masa depan |
| S3-03 | Alokasi all-in/split dan perpindahan antar-event | C-05 | S3-02 | Modal tidak dipakai dua kali; rute gagal/terlewat tetap tercatat |
| S3-04 | API simulasi, worker dan penyimpanan hasil | C-04, C-05 | S3-03 | Run punya ID, status, input, versi dan hasil yang dapat dibaca UI |
| S4-01 | Statistik historis kerugian dan pemulihan | C-06 | S2-02, S3-02 | Harga BEP dan BEP total terpisah; event belum pulih tetap dihitung |
| S4-02 | Skenario/proyeksi dan kontrak model sesuai PRD | C-06, C-07 | S0-04, S4-01 | Asumsi/metode/sampel tampil; status kecukupan data jelas |
| S4-03 | Grafik dan pembanding strategi | C-05, C-06 | S3-04, S4-01, S4-02 | Hasil gross, arus kas, risiko dan waktu modal tertahan dapat dibandingkan |
| S5-01 | Hubungkan seluruh alur dan tangani loading/empty/error | C-01–C-08 | S2-03, S2-04, S4-03 | Alur utama dapat didemonstrasikan dari awal ke hasil |
| S5-02 | Rapikan usability, dokumentasi menjalankan aplikasi dan known issues | PRD + instruksi PM | S5-01 | Paket MVP bisa dijalankan ulang dan batasnya terbaca |
| S5-03 | Audit cakupan PRD dan siapkan handoff testing | PRD/US asli | S0-04, S5-02 | Checklist requirement, bukti, bypass dan gap tersedia |
| S6-01 | Sepakati testing akhir bersama PM | Instruksi PM | S5-03 | Skenario dan kriteria uji disepakati; belum dilaksanakan |
| S6-02 | Jalankan testing akhir dan tindak lanjuti hasil | S6-01 | S6-01 | Hasil uji aktual, bug, perbaikan dan keputusan delivery dicatat |

Status berjalan masing-masing task hanya diperbarui di [PROGRESS.md](./PROGRESS.md) agar tidak muncul dua status yang bertentangan. Task dapat dipecah jika dibutuhkan, sambil mempertahankan relasi ke requirement dan task induk.

### Sprint intelligence — kelanjutan yang diotorisasi 6 Oktober

| Task | Scope | Induk | Bukti selesai |
|---|---|---|---|
| I-01 | Protokol, koleksi 2022–2025 sembilan emiten, audit sumber | S2-01/S2-02 | Snapshot MCP/REST, manifest, alasan setiap karantina |
| I-02 | Trap empiris, Wilson dan pemulihan tersensor | S4-01/S4-02 | Hasil per emiten, jumlah sampel, definisi, uji matematika |
| I-03 | Ranking dari aturan risiko dan objective tim | S4-02/C-07 | Aturan persisten, filter/ranking dapat ditelusuri |
| I-04 | Stress test nominal berbasis analog historis | S4-02/C-04 | Input entry/DPS pengguna, skenario gross, hasil tersimpan |
| I-05 | UI intelligence + verifikasi integrasi | S5-01/S5-02 | Browser→API→snapshot→hasil, log issue dan handoff |

Protokol [INTELLIGENCE_POLICY.md](./INTELLIGENCE_POLICY.md) membedakan statistik dan skenario dari prediksi terlatih. Sprint ini tidak mengklaim validasi forecast atau cakupan PRD yang belum tersedia.

## Cara menangani temuan tanpa menghambat MVP

### Sprint integrasi rotasi — diotorisasi 6 Oktober

| Task | Scope | Requirement | Bukti selesai |
|---|---|---|---|
| R-01 | Dataset event terpadu, harga kontinu2025 dan sesi IHSG | C-01/C-02/C-08 | Catalog, Intelligence dan simulator memakai ID/source yang sama; audit kelengkapan |
| R-02 | Screening dengan cutoff tanggal keputusan dan kandidat rute | C-01/C-05/C-07 | Tidak memakai future returns; rules/evidence/alasan tersimpan |
| R-03 | Replay beberapa rute × tiga alokasi | C-04/C-05/C-06 | Modal/horizon sama, entitlement berulang, kas/settlement, missed opportunities dan baseline cash |
| R-04 | Alur UI screening→planner→hasil | C-01–C-08 | Pilihan emiten/rules mengalir; draft/hasil persisten, empty/error, desktop/mobile |
| R-05 | Bukti development dan paket review PM | S5/S6 | Pemeriksaan relevan lulus, bug log, checklist review; UAT tetap menunggu PM |

Metode dibekukan di [ROTATION_POLICY.md](./ROTATION_POLICY.md). Status dicatat di PROGRESS.md.

Setiap bug, TODO, gap data dan blocker dicatat di [ISSUES.md](./ISSUES.md) ketika ditemukan. Catat dampak, bukti, task/story terkait, tindakan sementara dan kapan perlu ditinjau lagi. Lanjutkan task lain yang tidak bergantung pada blocker; tidak perlu meminta persetujuan ulang untuk workaround yang sudah berada dalam otorisasi PM.

Bypass boleh memakai snapshot Sectors berlabel historis, adapter sementara, skenario eksplisit atau menonaktifkan cabang yang datanya tidak layak. Mock hanya untuk pengembangan UI dan tidak boleh terlihat sebagai hasil pasar nyata. Bypass tidak otomatis memenuhi acceptance criteria dan tidak boleh diam-diam menghapus requirement dari MVP.

Contoh: tanggal declaration kosong ditampilkan sebagai belum tersedia; event dengan mata uang tidak jelas dikeluarkan dari perhitungan; model yang belum tervalidasi memakai statistik/skenario berlabel. Jika PRD mengharuskan hasil prediksi tertentu, requirement tersebut tetap tercatat sebagai gap sampai diselesaikan atau scope diubah secara eksplisit.

Temuan kosmetik, optimasi performa dan refactor yang tidak diperlukan untuk alur MVP masuk backlog. Kesalahan yang merusak perhitungan inti harus diperbaiki atau dibatasi agar tidak menghasilkan output yang menyesatkan. Ini menjaga MVP yang dapat ditinjau tanpa memalsukan status pekerjaan.

## Batas selesai dan testing

### Pemeriksaan kesiapan lanjutan — Q-01 sampai Q-03

Otorisasi lanjutan PM: “oke lanjutkan”. Ini pemeriksaan developer dan perbaikan alur yang ada; kriteria UAT tetap dibahas dengan PM.

| Task | Cakupan | Bukti selesai |
|---|---|---|
| Q-01 | Matriks engine: 12 event + 3 portofolio, entry/exit/holding/alokasi | Laporan dapat direproduksi, hak dividen dan konservasi kas diperiksa independen |
| Q-02 | Perbaikan alur detail → simulator dan kontrak/error yang ditemukan | Event pilihan masuk ke form/hasil; periode valid dan input batas ditangani |
| Q-03 | Regression/API/browser dan catatan kesiapan | Bukti uji serta matriks PASS/BYPASSED/WAITING_PM |

Task development berstatus `DONE` setelah hasil implementasinya ada dan pemeriksaan relevan tercatat. Catatan pemeriksaan lokal tidak sama dengan kelulusan testing akhir. Build, import, API smoke check dan pemeriksaan kalkulasi yang diperlukan tetap dilakukan selama development; strategi testing akhir belum dibekukan.

`READY_FOR_TESTING` berarti cakupan implementasi terhadap PRD sudah dipetakan, aplikasi dapat dijalankan/didemonstrasikan, serta semua bypass dan keterbatasan terlihat. Requirement wajib yang belum terpenuhi membuat kandidat bersifat parsial dan harus disebutkan, bukan dianggap selesai.

`DELIVERED` baru dicatat sesuai hasil testing dan keputusan delivery yang dibahas dengan PM. Tidak ada status delivered, deployment publik, atau klaim lulus UAT pada tahap perencanaan ini.

### Persiapan review pengguna — U-01–U-02

| Task | Scope | Requirement | Bukti selesai |
|---|---|---|---|
| U-01 | Input asli hasil, salin ke draf, dan identitas riwayat manual | C-04/C-07/C-08, S5-02 | Buka hasil lama, lihat aturan aslinya, salin lalu ubah satu aturan; hasil asal tidak berubah |
| U-02 | Satu panduan percobaan PM dengan lembar observasi kosong | S6-01, PM-01/04/07 | Input dan langkah konkret tersedia; observasi manusia tetap menunggu PM |

### Demo jaringan lokal — permintaan PM

| Task | Scope | Bukti selesai |
|---|---|---|
| L-01 | Frontend dapat diakses teman di LAN melalui port3000 | Listener LAN aktif, halaman dan proxy API merespons lewat IP LAN, cara menjalankan ulang didokumentasikan |

### Relokasi direktori — permintaan PM 7 Oktober 2026

| Task | Scope | Bukti selesai |
|---|---|---|
| M-01 | Memindahkan proyek ke Documents/Codex/horizon | Isi dan environment utuh di tujuan, dapat dibangun/dijalankan, folder asal ditangani sesuai izin filesystem |

### Publikasi repository — permintaan PM 7 Oktober 2026

| Task | Scope | Bukti selesai |
|---|---|---|
| G-01 | Commit dan push proyek horizon ke YohanesVito/horizon | Tidak membawa key/database runtime/dependensi, snapshot yang diperlukan lengkap, commit remote sama dengan lokal |

### Overlay timeline — diskusi desain dan audit data

| Task | Scope | Requirement | Bukti selesai |
|---|---|---|---|
| T-01 | Audit kelengkapan lima tahun untuk overlay satu emiten, definisi periode dan eligibility | C-02/C-06/C-08 | Sumber MCP/REST, tabel tahun/field/harga/gap, status boleh tampil yang tidak mengabaikan missing; rancangan perilaku, tanpa perubahan UI |
| T-02 | Catat perilaku periode berjalan: aktual + prediksi; perhitungan ditunda sesuai arahan PM | C-02/C-06/C-08 | Spesifikasi status, batas data aktual, tampilan belum tersedia, dan pemisahan kelengkapan histori; engine DEFERRED (ISS-042) |
| T-03 | API timeline dengan sumber snapshot, filter histori lengkap dan pratinjau LPPF terpisah | C-02/C-08 | Normalisasi relatif ex-date, provenance, gate server, harga aktual periode berjalan, tanpa angka forecast |
| T-04 | UI overlay area, fokus hover/klik/tap, satu emiten, tooltip tanggal/harga, fase dividen dan mode prediksi | C-02/C-06 | Navigasi Timeline, lima periode historis, pemisahan aktual/prediksi dan gap data terlihat |
| T-05 | Pemeriksaan kalkulasi/gate, build/lint, browser desktop/mobile dan handoff | C-02/C-08 | Bukti yang dijalankan, isu/bypass tercatat; tidak mengklaim UAT final |
| T-06 | Label fase langsung pada grafik dan warna area cum→ex menurut arah perubahan close | C-02/C-06 | Label tidak bertumpuk; negatif merah, positif hijau, nol netral; mengikuti periode fokus dan modeRp/% |
| T-07 | Simpan implementasi chart pada branch `feat/chart` sesuai permintaan PM | C-02/C-06/C-08 | Commit lokal berisi kode, snapshot yang diperlukan, dokumentasi dan bukti pemeriksaan; tidak memuat kredensial |

### Migrasi Supabase — 7 Oktober 2026

| Task | Scope | Requirement | Bukti selesai |
|---|---|---|---|
| DB-01 | Konfigurasi PostgreSQL/Supabase dan schema privat berversi | S1-02/C-03/C-07/C-08 | Env server, SSL, akun backend terbatas, startup memeriksa versi schema |
| DB-02 | Migrasi record SQLite dengan backup, deteksi konflik dan verifikasi | S1-02/C-04/C-05 | Semua ID/payload/timestamp cocok; rerun tidak menduplikasi atau menimpa konflik |
| DB-03 | Alihkan runtime, regression/API dan runbook | S3-04/S5-02/C-08 | Backend memakai Supabase, riwayat terbaca, read/write teruji; rollback dan batas scope jelas |

Tahap ini memindahkan penyimpanan aplikasi (watchlist, rules, skenario, rencana dan hasil). Snapshot harga/kalender Sectors tetap sumber immutable di repo; pemindahan dataset pasar, autentikasi multi-user dan deployment frontend/backend bukan bagian migrasi record ini.

### Operasi VPS Dalang — keputusan PM 7 Oktober 2026

Backend tetap FastAPI, dengan target hosting Docker pada VPS Dalang; proposal rewrite Next.js + ORM TypeScript tidak dilanjutkan. Database tetap Supabase. Scope saat ini hanya penghentian sementara layanan lama dan pencatatan pemulihan.

| Task | Scope | Sumber | Bukti selesai |
|---|---|---|---|
| OPS-01 | Inventaris VPS, penghentian lima layanan kurasi systemd setelah konfirmasi PM, dan runbook restart | Instruksi langsung PM; S5-02 | Snapshot sebelum/perintah/sesudah, kelima unit inactive/dead, catatan lokal + VPS + memori |

Docker belum tersedia; instalasi dan deployment Horizon adalah pekerjaan lanjutan. Detail: [DALANG_SERVICE_PAUSE.md](./DALANG_SERVICE_PAUSE.md).

### Deployment backend Dalang — diotorisasi PM 7 Oktober 2026

| Task | Scope | Sumber | Bukti selesai |
|---|---|---|---|
| DEP-01 | Instalasi Docker dan kemasan runtime/release tanpa kredensial dalam image | Instruksi deploy PM; S1-01/S5-02 | Docker berfungsi, build dari snapshot sumber terpilih, manifest dan konfigurasi tersimpan |
| DEP-02 | FastAPI satu proses, Supabase, HTTPS provider dan proxy frontend dengan key server-only | C-03/C-04/C-08; S3-04 | Backend sehat, key tidak di browser, koneksi database dan alur API berjalan |
| DEP-03 | Verifikasi deployment, simulasi, runbook upgrade/rollback, catatan batas | S5-02/S5-03 | Bukti aktual; deployment frontend publik dan UAT dibedakan |

### Review branch sebelum Vercel — permintaan PM 8 Oktober 2026

| Task | Scope | Sumber | Bukti selesai |
|---|---|---|---|
| BR-01 | Bandingkan ancestry, perubahan polish dan kesiapan gabungan deployment tanpa mengubah checkout | Permintaan review PM; DEP-02/DEP-03, S5-02 | BRANCH_REVIEW.md, branch-review.json, build/lint/60tes/preview browser gabungan; merge dan deploy tetap langkah berikutnya |
