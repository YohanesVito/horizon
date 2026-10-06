# Rotation planner v1 — protokol sebelum melihat hasil rute

6 Oktober 2026. Scope R-01–R-05, C-01 sampai C-08.

1. Universe tetap sembilan emiten riset. Sumber event, DPS, audit dan statistik berasal dari IntelligenceDataset yang sama. Harga berkelanjutan Des2024–Jan2026 serta sesi IHSG dilengkapi melalui MCP. Replay memilih event dan periode tahun2025; histori statistik2022–2025 dipotong sesuai tanggal keputusan.
2. Tanggal keputusan = awal periode. Semua statistik screening memakai harga dan event yang tersedia **sebelum** tanggal tersebut; event yang belum selesai boleh tersensor, tidak mengisi outcome masa depan. Ranking tahunan yield2025 di halaman Peluang tidak dipakai sebagai fitur pemilihan rute2025.
3. Timestamp declaration/vintage snapshot belum tersedia. Default replay bersyarat pada asumsi jadwal dividen sudah diketahui. Mode jadwal terverifikasi saja akan mengeluarkan event tanpa bukti pengumuman. Ini tetap bukan backtest point-in-time penuh. Universe dipilih setelah2025, sehingga selection/survivorship bias masih ada.
4. Rute disusun sebelum replay: (a) kronologis semua kandidat hingga batas jumlah event, (b) kronologis dengan jeda modal konservatif, (c) prioritas ranking tim dengan jeda konservatif. Tidak mencari urutan berdasarkan realized PnL, harga keluar atau BEP aktual. Jika rute identik, tampilkan sekali. Ini kandidat heuristik terbatas, bukan optimum global.
5. Jeda konservatif memakai batas waktu ex+H sesi pasar teramati +T+2. Untuk exit ex-close dapat memakai ex+T+2. Untuk payment-close, exit dibatasi H. Untuk BEP, waktu pulih masa depan tidak boleh dipakai untuk menyeleksi rute. Konflik jadwal/batas jumlah event tampil sebagai alasan tidak dipilih.
6. Untuk setiap rute, bandingkan all-in event pertama, split anggaran awal sama rata per event, dan rotasi kas tersedia; modal/awal/akhir/rules sama. Split per event berbeda dari split per emiten. Tidak ada margin dan lot100. Kas kecil sisa rotasi dapat membeli posisi berikutnya bila cukup satu lot.
7. Replay dapat memegang beberapa lot emiten yang sama. Hak untuk setiap ex-date berlaku pada seluruh lot yang masih dimiliki, termasuk dividen kedua di tengah holding. Bayar pada payment date; hasil jual settle T+2 sesi IHSG teramati. BEP signal close dieksekusi open sesi berikutnya. Batas holding berlaku pada seluruh exit yang berpotensi menunggu.
8. Ketidaktersediaan harga tidak boleh dianggap pulih/rugi nol. Validasi kontinuitas terhadap sesi IHSG, quarantine OHLC/volume invalid, dan audit corporate actions diterapkan sebelum replay. Kalender IHSG teramati merupakan proxy sesi, bukan konfirmasi kalender settlement resmi.
9. Semua perbandingan adalah hasil historis gross, di luar biaya/pajak/slippage. Ada baseline kas tanpa transaksi. Posisi belum terjual dan piutang tetap dibedakan dari kas tersedia. Skenario buruk di sini adalah drawdown/hasil yang benar-benar teramati, bukan proyeksi probabilistik.
10. Data dan hasil lama tetap disimpan dengan versinya. Draft rencana menyimpan input, rules, cutoff, evidence IDs dan alasan pemilihan; replay mempunyai run terpisah yang menunjuk draft. Perubahan rules setelahnya tidak mengubah run lama.

Belum ada forecast tanggal/harga terkalibrasi atau optimizer rotasi forward. Review PM dan UAT tidak dianggap selesai sebelum dilakukan bersama pengguna.

## Koreksi kualitas sesi saat implementasi

Feed IHSG melewatkan 2/6/7 Mei serta 20 Oktober 2025. Kesembilan feed emiten mempunyai OHLCV valid pada tanggal tersebut. Sesi pasar dilengkapi hanya dari irisan tanggal valid **seluruh sembilan** emiten; keempat tanggal tersimpan sebagai `session_repairs` dalam fingerprint dan metadata. Ini mengoreksi gap indeks, bukan mengasumsikan libur atau memakai rata-rata harga. Sesi ini tetap proxy, bukan kalender settlement BEI resmi. Aturan pemilihan rute tidak diubah berdasarkan PnL. Jika entry bersamaan, prioritas eksekusi alfabet emiten mengikuti replay.
