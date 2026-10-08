# Riset overlay timeline dividen — 7 Oktober 2026

Status: UI/API diimplementasikan pada T-03/T-04; kelengkapan histori T-01 masih parsial. Permintaan PM: satu emiten, area transparan per periode tahunan, hover menonjolkan periode, lima tahun terakhir, hanya emiten dengan data lengkap. C-02/C-06/C-08. Bukti implementasi di TIMELINE_IMPLEMENTATION.md.

**Perubahan PM 8 Oktober:** frasa “hanya emiten dengan data lengkap” kini dibatasi pada katalog **grafik overlay terverifikasi**. Penemuan/ranking nama emiten tidak memakai gate lima tahun. Kandidat dengan grafik belum lengkap tetap boleh ditemukan dengan tahun, sumber dan gap yang jelas; pembahasan gate di bawah adalah spesifikasi grafik, bukan filter discovery.

**Arahan PM terbaru 8 Oktober (T-08):** syarat lima tahun penuh juga dilepas untuk **menampilkan grafik**. Periode dengan event dan harga yang benar-benar tersedia boleh tampil sebagai pratinjau, sementara tahun tanpa kurva dinyatakan sebagai gap snapshot. Beberapa event dalam satu tahun tetap terpisah berdasarkan ex-date; data tidak diimputasi. Kriteria lengkap lima tahun di bawah adalah riwayat rancangan awal dan bukan gate tampilan yang berlaku. Verifikasi asal jadwal, basis harga/DPS, dan jenis siklus tetap diperlukan sebelum mengesahkan data sebagai lengkap (ISS-041).

## Keputusan desain yang sedang dirumuskan

- Gunakan overlay, bukan stacked area: harga antarperiode tidak dijumlahkan. Garis harga tetap terlihat, fill tipis; hover garis/legenda menonjolkan periode dan meredupkan yang lain. Klik mengunci fokus; perangkat sentuh memakai tap dan pemilih periode.
- Lima tahun penuh sementara adalah2021–2025. Pilihan2022–2026 mencakup2026YTD, bukan tahun penuh. Pertanyaan rentang disampaikan ke PM; belum mengklaim persetujuan.
- Implementasi T-04 memakai hari kalender relatif terhadap ex-date (H0), sehingga akhir pekan dan jarak antar tanggal tetap benar tanpa menebak sesi yang belum tervalidasi. Ini menggantikan usulan awal sumbu sesi. RUPS/declaration/payment tiap periode mempunyai offset sendiri. Pada hover/fokus marker periode aktif yang ditegaskan.
- Default usulan sumbu y: perubahan harga terhadap close cum-date (=0% atau indeks100), dengan rupiah asli pada tooltip dan mode nominal tersendiri. Normalisasi tidak memperbaiki split/basis harga yang belum diketahui.
- Satu tahun dapat mempunyai beberapa pembayaran. Seri harus mempunyai event ID; perlu selektor jenis/siklus (misalnya final/interim yang diverifikasi). Jangan memilih pembayaran terbesar atau menyatukan beberapa siklus diam-diam. Tanggal ex menentukan label tahun perbandingan; berbeda dari tahun buku.
- Kurva memakai observasi nyata; tidak dihaluskan menjadi lintasan rekaan, tidak mengisi missing dengan nol, dan tidak memaksa pemulihan pada payment.

## Arahan PM: periode berjalan sebagai prediksi

PM meminta periode yang masih berjalan mempunyai bagian prediksi; perhitungan/model prediksi sengaja ditunda. Ini keputusan perilaku produk, belum implementasi atau hasil model. T-02 mencatat desain, ISS-042 mencatat engine yang ditunda.

- Periode selesai tetap historis. Periode berjalan memakai label seperti **2026 — Aktual + Prediksi**: data harga yang sudah tersedia berupa garis utuh; bagian setelah titik data aktual terakhir direncanakan bergaris putus-putus dengan area transparan berbeda. Batas menyebut tanggal data aktual terakhir, bukan otomatis hari ini bila feed tertinggal.
- Hover membedakan status Historis/Prediksi, tanggal, harga dan fase dividen. Klik/hover fokus periode tetap mengikuti rancangan overlay.
- Sebelum engine tersedia, bagian mendatang menampilkan **Prediksi belum tersedia**. Bila nanti dibuat wireframe dengan kurva contoh, labelnya **Ilustrasi desain**, bukan hasil perhitungan. Tidak mengisi harga, probabilitas trap, interval ketidakpastian atau tanggal pulih dengan angka rekaan.
- Status tanggal event terpisah dari status harga: jadwal mendatang yang sudah diumumkan tetap **Terkonfirmasi**; tanggal yang belum diketahui tetap **Belum tersedia**, atau **Estimasi** hanya setelah ada metode yang menghasilkan estimasinya. Tidak mengubah jadwal terkonfirmasi menjadi prediksi hanya karena tanggalnya di masa depan.
- Syarat lengkap berlaku pada histori pembanding dan data aktual yang sudah seharusnya tersedia. Masa depan yang belum terjadi bukan kegagalan kelengkapan histori; ini juga tidak menghapus gap declaration historis ISS-041. Siklus dividen yang sudah selesai pada tahun berjalan tetap historis.
- Audit2021–2025yang sudah selesai tetap disimpan. Arahan ini belum menetapkan apakah tampilan memuat lima tahun termasuk2026atau lima tahun historis ditambah2026; keputusan jumlah periode tetap terpisah. Contoh label2026hanya menunjukkan tahun berjalan saat diskusi.

Urutan kerja: lanjutkan definisi tampilan dan audit histori; sediakan status/ruang prediksi pada rancangan; rumus, training dan validasi engine dibahas pada tahap berikutnya.

## Kriteria lengkap untuk tampilan baru

1. Kelima tahun pengamatan mempunyai siklus dividen yang dapat diidentifikasi dan dibandingkan. Tahun tanpa pembayaran yang terkonfirmasi berbeda dari missing data; keduanya tidak dibuatkan kurva dividen fiktif.
2. DPS, unit/mata uang, cum/ex/record/payment dan sumbernya dapat ditelusuri; tidak ada konflik antarrespons.
3. RUPS dan/atau declaration yang diklaim pada grafik harus mempunyai tanggal dan bukti hubungan dengan event tersebut. AGM terdekat tidak otomatis declaration; label public expose di feed AGM tidak dianggap RUPS dividen.
4. Harga valid sepanjang jendela yang ditampilkan, dari marker awal yang diketahui sampai payment dan batas pengamatan yang dipilih. Hari libur/suspensi/gap feed dibedakan; tidak menganggap semua hari tanpa bar adalah libur.
5. Basis harga/DPS/split dapat direkonsiliasi sebelum perbandingan nominal atau simulasi. Metadata yang belum cukup membuat status belum terverifikasi.

Hanya `eligible_strict=true` yang boleh ditampilkan pada katalog overlay baru. Daftar audit internal tetap menyimpan emiten yang gagal beserta alasan. Jangan mengubah/mengosongkan katalog lama selama tahap diskusi.

Implementasi: katalog Timeline memeriksa eligibility di server, bukan membaca flag audit awal sebagai persetujuan. Saat ini katalog lengkap kosong. Tombol **Buka pratinjau LPPF** membuka ruang riset terpisah dengan label jelas dan endpoint `preview=true`; ini tidak memasukkan LPPF ke katalog lengkap atau mengganti filter diam-diam. Snapshot histori tetap2021–2025, ditambah lapisan2026 aktual/prediksi. Sebanyak123bar2026tersedia hingga6Oktober2026; forecast tetap kosong. Pemilihan lima tahun historis plus tahun berjalan adalah keputusan implementasi yang dinyatakan, bukan persetujuan rentang baru yang dikarang.

## Tahap audit

Mulai dengan registry MCP terkini, kalender dividen pasar2021–2025 dan snapshot2022–2025 yang sudah ada. Ambil jendela harga tambahan hanya untuk kandidat yang relevan setelah memeriksa field jadwal. Cari dukungan declaration melalui news/filings Sectors bila schema kalender tidak memuatnya. Catat batas cakupan; tidak menyatakan seluruhIDX lengkap hanya dari sampel emiten.

Dokumentasi resmi: [Corporate Actions](https://docs.sectors.app/api-references/v2/indonesia/company/corporate-actions), [Calendar](https://docs.sectors.app/api-references/v2/indonesia/news/corporate-actions), [Screener](https://docs.sectors.app/api-references/v2/indonesia/screener/companies). MCP tetap dipakai; kalenderREST melengkapi endpoint yang tidak ada pada registry. Snapshot dan hasil audit disimpan di outputs/timeline-audit tanpa API key.

## Hasil audit awal

Rentang sementara2021–2025, berdasarkan tahun ex-date. Ada22jendela kalender: lima respons2021 diambil7Oktober2026;17snapshot2022–2025 dari riset sebelumnya dipakai ulang. Seluruh tanggal dalam rentang tercakup oleh permintaan. Ini membuktikan cakupan query, bukan kelengkapan data provider terhadap seluruh pengumumanIDX.

| Kebutuhan | Temuan | Status / tindakan |
|---|---|---|
| Kalender pasar lima tahun | 1.900 event unik dari477emiten;170memiliki event pada setiap tahun | Kandidat kalender ditemukan. Cocok dengan170hasil MCP screener `total_dividend[2021..2025] > 0`, pagination selesai. Bukan ranking kualitas atau yield. |
| Cum, ex, recording, payment, DPS | Field terisi untuk170kandidat; format/urutan tanggal dan DPS positif lolos pemeriksaan struktur | Lanjut validasi unit, basis penyesuaian dan hubungan ke pengumuman. |
| Declaration | Tidak ditemukan field tanggal declaration dalam1.900record kalender | Belum memenuhi timeline lengkap. Probe news BBCA keyword `dividen` pada2021dan2025 menghasilkan0record; ini hanya batas query tersebut, bukan bukti semua berita Sectors tidak tersedia. |
| Harga lima periode, contoh LPPF | Lima jendela sekitar event2021–2025,272bar; tanpa tanggal ganda/OHLC invalid; ada harga tepat pada empat tanggal kalender setiap event | Harga contoh ditemukan. Bukan harga kontinu lima tahun; kalender seluruh sesi, suspensi dan basis adjustment belum diverifikasi. |
| RUPS/declaration LPPF | Feed corporate-actions memuat AGM2022–2026, tanpa2021; hasil rapat2022–2025 null; salah satu entri adalah public expose | Hubungan rapat dengan keputusan dividen belum terbukti. Tidak memakai AGM terdekat sebagai declaration. |
| Emiten boleh tampil pada overlay lengkap | Belum ada emiten yang disahkan melalui seluruh pemeriksaan | `eligible_strict=false` berarti belum disetujui, bukan terbukti mustahil tersedia. Katalog website belum diubah. |

Dari sembilan emiten riset sebelumnya, kandidat lima tahun kalender adalah ADRO, BBCA, BBNI, BBRI, BMRI dan LPPF. CFIN tidak memiliki record pada2021/2022/2024; DMAS pada2024; RALS pada2021. Ketidakadaan record belum membuktikan tidak ada pembayaran: simpan status perlu verifikasi. Kelengkapan kalender tidak menyatakan final/interim sebanding.

Audit contoh LPPF dipilih karena satu event per tahun dalam kalender, bukan rekomendasi investasi. Pemilihan2021–2025juga belum disetujui PM. Jangan menyebut riset ini prediksi atau mengasumsikan harga pulih pada payment.

## Bukti dan pekerjaan lanjutan

- Reproduksi: `.venv/bin/python work/audit_timeline_overlay.py collect` (memakai cache, hanya mengambil yang belum ada), lalu `analyze` (offline). Perintah collect memakai API key server melalui mekanisme probe yang sudah ada; key tidak dicetak.
- `outputs/timeline-audit/coverage.csv` dan `coverage.json`:477emiten, jumlah event per tahun, field hilang/invalid, provenance query dan status verifikasi.
- `outputs/timeline-audit/pilot-LPPF.json`: lima jendela harga dan pemeriksaan struktur, dengan flag yang belum diverifikasi tetapfalse.
- `outputs/timeline-audit/verification.json`: sembilan pemeriksaan konsistensi audit dan tidak adanya key tersimpan dalam artifact lulus; total272bar pilot. `git diff --check` lulus untuk perubahan tracked. Ini bukan validasi kebenaran pasar atau kelulusan timeline lengkap.
- `outputs/timeline-audit/mcp-registry-2026-10-07.json`, `raw/` dan `collection.json`: bukti respons MCP/REST; snapshot lama tidak ditimpa.
- Berikutnya: tentukan siklus dividen yang sebanding; cari dokumen pengumuman historis dan tanggal declaration yang terhubung ke event di Sectors; verifikasi seluruh sesi harga pada jendela serta basis corporate action. Jangan melonggarkan definisi lengkap atau mengganti sumber tanpa menjelaskan perubahan kepada PM.
- Pemeriksaan kode aplikasi/build/UAT tidak dijalankan ulang: tahap ini hanya riset, skrip audit dan dokumentasi. Lihat ISS-041 untuk gap data yang tetap terbuka.
