# Percobaan pertama bersama PM

6 Oktober 2026 · Persiapan U-02 untuk PM-01/04/07.

Tujuan: menilai apakah pengguna memahami event yang diuji, uang yang dapat dipakai, dan hubungan aturan dengan hasil tersimpan. Ini usulan sesi review, belum persetujuan kriteria UAT. Tidak ada penilaian pengguna yang telah dicatat.

Buka [aplikasi lokal](http://127.0.0.1:3000/). Backend dan frontend perlu berjalan. Data merupakan replay historis Sectors; nominal gross di luar biaya transaksi, pajak, dan slippage. Sesi ini tidak menilai kemampuan memprediksi keuntungan.

## Kasus yang dicoba

Kamu mempunyai modal Rp100 juta dan ingin melihat akibat membeli dividen ADRO pada akhir 2025. Tidak perlu melakukan transaksi sungguhan.

| Input | Nilai tetap |
|---|---|
| Event | ADRO, ex-date 30 Desember 2025 saja |
| Modal | Rp100.000.000 |
| Periode | 1–31 Desember 2025 |
| Masuk | 5 sesi sebelum cum date |
| Keluar awal | Close ex-date |
| Batas sesi setelah ex-date | 20 |
| Strategi utama | Rotasi modal; bandingkan tiga alokasi |

## Tugas dan pertanyaan

1. Dari **Peluang**, cari ADRO. Buka detail dan kirim event Desember ke Simulator melalui **Simulasikan event ini**. Sesuaikan input dengan tabel lalu jalankan. Jelaskan event dan rentang waktu yang sedang diuji. Catat bila ada label atau navigasi yang membuat ragu.
2. Dari hasil, jawab: berapa nilai portofolio akhir, berapa kas yang bisa langsung dipakai, dan kapan sisa uang masuk? Tunjukkan informasi yang mendukung jawabanmu. Jangan memakai perhitungan di bawah sebelum mencoba sendiri.
3. Muat ulang halaman, buka Simulator, lalu pilih hasil tadi berdasarkan ID di riwayat. Baca **Input asli hasil ini**. Klik **Gunakan input hasil ini**, ubah **hanya** aturan keluar menjadi **Setelah sinyal BEP harga**, lalu jalankan. Semua input lain tetap. Jelaskan apa yang berubah dan apakah hasil pertama masih bisa ditemukan. Dua hasil boleh sama; tidak ada kewajiban bahwa aturan baru lebih baik.

Dalam satu event, tiga alokasi bisa menghasilkan nominal sama. Untuk mengevaluasi perpindahan modal antar-emiten, lanjutkan sesi terpisah PM-03 dengan [rencana rotasi](./PM_REVIEW.md); jangan menyimpulkan manfaat rotasi dari kasus satu event ini.

## Lembar observasi PM

Isi berdasarkan pengalamanmu, bukan apakah jawaban sesuai harapan developer. Status seluruh tugas masih **WAITING_PM**.

| Tugas | Jawaban / pemahamanmu | Bagian yang membingungkan | Perubahan yang diinginkan |
|---|---|---|---|
| Memilih event dan periode | — | — | — |
| Kas, nilai portofolio, dan waktu penerimaan | — | — | — |
| Memakai ulang input dan membandingkan satu aturan | — | — | — |

Catat ID dua hasil untuk mempermudah penelusuran. Jangan sertakan API key. Observasi akan digunakan untuk perbaikan dan diskusi acceptance criteria; tidak otomatis berarti delivery disetujui.

## Acuan developer — baca setelah mencoba

Kasus awal telah diperiksa pada hasil `52c72d21-4503-4970-97b1-933d12972259`, engine `replay-v2.1`, dataset `unified-b749e08ddb769800`. Hasil baru dengan input/versi sama semestinya sama; ID berbeda.

| Komponen akhir 31 Desember 2025 | Nilai |
|---|---|
| Kas tersedia | Rp60.000 |
| Piutang penjualan, settlement 5 Januari 2026 | Rp95.206.000 |
| Piutang dividen, payment 15 Januari 2026 | Rp7.634.364 |
| Nilai portofolio (NAV) | Rp102.900.364 |
| PnL saham | −Rp4.734.000 |
| PnL total gross termasuk hak dividen | Rp2.900.364 |

52.600 saham dibeli pada Rp1.900 dan dijual pada Rp1.810. Laba total tidak berarti harga telah BEP; kas tersedia juga tidak sama dengan NAV. Tanggal settlement memakai proksi sesi dataset, bukan kalender resmi terverifikasi (ISS-029). Bukti awal: `outputs/development/readiness-case.json`.

Pemeriksaan developer untuk eksperimen kedua menghasilkan run `d049736a-c257-4732-9198-9bf1ebfa7b98`. PnL total sama, tetapi piutang penjualan menjadi Rp0 dan saham senilai Rp95.206.000 masih dipegang. Batas periode tercapai sebelum posisi keluar; bukan bukti harga telah pulih. Hanya `exit_rule` yang berbeda, dan record asal tidak berubah. Bukti: `outputs/development/saved-input-comparison.json`.

Harga kembali ke entry pada close hanya menjadi sinyal jual pada open sesi berikutnya; batas holding atau akhir replay dapat terjadi lebih dahulu. Hasil tidak menjamin harga akan pulih.
