# Paket review PM — Rencana rotasi

6 Oktober 2026. Kandidat lokal untuk diskusi produk dan rancangan testing. **Bukan persetujuan UAT, rekonsiliasi PRD, atau keputusan delivery final.**

## User, keputusan, input, dan output

Retail dividend hunter mempunyai satu modal dan ingin membandingkan beberapa urutan pembelian dividen. Ia memasukkan modal, awal/akhir periode, universe emiten, financial logic dan batas holding. Output adalah kandidat rute dengan alasan yang dapat diaudit, kemudian perbandingan gross PnL, drawdown, kas/piutang, lama modal tertahan, serta event yang terlewat. Pengguna mengeksekusi order sendiri di luar produk.

Versi ini menguji **periode historis tahun 2025**. Output tidak memprediksi jadwal atau harga masa depan. Maksimum tiga kandidat heuristik dapat menjadi kurang dari tiga bila hasil rutenya sama atau tidak ada event yang lolos.

## Alur demo yang sudah disiapkan

1. Buka `http://127.0.0.1:3000/` → Intelligence. Periksa objective dan batas sampel/risiko tim. Klik **Rencanakan dengan logika ini**. Alternatif: filter Peluang/Watchlist → **Gunakan emiten ini untuk rencana**.
2. Gunakan modal Rp100 juta, 1 Maret–30 Juni2025, seluruh sembilan emiten, entry5 sesi sebelum cum, statistik t20, min3 sampel, Wilson upper≤100%, median return≥−100%, exit BEP, holding20 sesi, maks5 event.
3. **Susun kandidat rute**. Periksa cutoff1 Maret; default menghasilkan6 event lolos dan3 dikeluarkan karena sampel lengkap kurang dari3. Maks5 menyebabkan satu kandidat tidak dimasukkan dalam rute kronologis. Rute dibekukan sebelum replay.
4. **Uji semua rute ×3 strategi modal**. Sembilan hasil memakai modal dan periode sama. Jangan memilih “terbaik” dari PnL lalu menganggapnya forecast. Telusuri satu event terlewat, satu posisi terbuka di bawah entry, dan piutang yang belum tersedia.
5. Buka **Rencana & replay tersimpan** setelah reload. Input dan versi hasil lama tidak berubah ketika aturan tim disunting.
6. Matikan asumsi jadwal sudah diketahui. Semua event tanpa timestamp pengumuman harus dikeluarkan, dengan alasan yang terlihat; tidak membuat kalender baru.

## Pertanyaan keputusan produk untuk PM

| Area | Keputusan yang perlu disepakati | Bukti yang dilihat |
|---|---|---|
| Nilai produk | Apakah urutan, risiko dan waktu kas lebih membantu daripada daftar yield? | Bandingkan rute dan alasan satu event tidak dapat dibeli |
| Own financial logic | Apakah objective + filter cukup, atau tim perlu formula yang dapat ditulis sendiri? | Ubah min sampel/risiko dan telusuri perubahan kandidat |
| Strategi | Apakah split per event sudah sesuai ekspektasi, atau perlu split per emiten/bobot pengguna? | Dua event issuer yang sama memperoleh dua anggaran pada split per event |
| Batas waktu | Apakah force-exit ketika holding limit tercapai sesuai kebutuhan? | PnL rugi saat harga belum BEP, bukan menunggu tanpa batas |
| Kalender | Apakah replay bersyarat cukup untuk fase riset berikutnya? | Declaration belum ada; verified-only tidak menghasilkan rute |
| Recovery | Apakah tampilan posisi terbuka, harga di bawah entry dan sampel censored cukup jelas? | Intelligence dan ledger replay memakai definisi berbeda yang diberi label |
| Scope delivery | Requirement mana yang wajib dan mana yang boleh tetap bypass? | Cocokkan PRD/user story asli, ISS-001/024/029/030/032 |

## Kandidat acceptance checks untuk dibahas

Ini usulan, bukan kriteria yang dianggap telah disetujui PM:

- User dapat menjelaskan alasan suatu event lolos/tidak lolos tanpa membuka kode.
- Input nominal/tanggal yang terlihat sama dengan snapshot yang diproses.
- Perbandingan memakai modal dan periode sama; saldo kas tidak pernah negatif.
- Hak dividen tidak hilang saat jual sebelum payment; uang yang belum settle tidak dibelanjakan.
- Price BEP terpisah dari total BEP; gap open setelah sinyal dapat menyebabkan PnL saham negatif.
- Pengamatan belum pulih tidak diperlakukan sebagai kerugian nol atau pasti pulih di masa depan.
- Mode asumsi, sumber/fingerprint, biaya yang diabaikan, dan keterbatasan sampel terlihat.
- Run lama dapat ditelusuri setelah reload/perubahan rules tanpa ditimpa.

Pengujian kalkulasi/API/build/browser oleh developer dicatat terpisah di [VERIFICATION.md](./VERIFICATION.md). Tindak lanjut produksi: timestamp pengumuman, kalender resmi, lapkeu point-in-time, validasi model, biaya transaksi, normalized storage, akun dan worker durable; urutannya menunggu prioritas PM.

Matriks pemeriksaan developer dan tugas uji bersama PM tersedia di [TEST_MATRIX.md](./TEST_MATRIX.md). Kasus ADRO akhir2025 dapat dipakai untuk menguji pemahaman NAV versus kas.

Mulai review singkat melalui [panduan percobaan pertama](./UAT_SESSION.md): satu event, kas versus NAV, lalu salin hasil dan ubah satu aturan. Input asli kini terlihat langsung pada hasil Simulator; pengubahan draf tidak menimpa hasil tersimpan.
