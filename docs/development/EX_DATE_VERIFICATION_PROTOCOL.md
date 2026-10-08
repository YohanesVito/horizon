# Protokol audit dan uji ex-date v0.3

Ditulis 8 Oktober 2026 **sebelum membaca pasangan harga cum/ex 2026 untuk uji ini**. Terkait F-02/ISS-042 dan C-02/C-06/C-07. Ini tidak mengubah formula v0.2 atau status prediksi live.

## Uji temporal tambahan yang dibekukan

- Event uji: satu event LPPF 2026 dalam `outputs/timeline-audit/raw/current-calendar-2026-04-01.json`, bila cum-date, ex-date, DPS, dan kedua harga tersedia. Jangan mengganti event setelah melihat hasilnya.
- Latih pooled-PDR hanya pada 44 pasangan eligible 2022–2025 yang sudah dipakai v0.2; `kappa = median((cum close − ex close) / DPS)` tanpa retuning, aturan fallback, atau efek emiten baru.
- Pembanding tetap: `P_cum` (flat) dan `P_cum − DPS` (full-DPS). Skor satu event: `abs(prediksi − close aktual ex) / close cum × 100`. Laporkan pula arah galat dan PDR aktual. Satu event tidak cukup membuktikan generalisasi.
- Uji ini **temporal tambahan**, bukan holdout blind: LPPF sudah terlihat pada UI riset, universe dipilih sebelumnya, dan snapshot 2026 diambil sesudah event.

## Gate bukti per event

1. Temukan dokumen pengumuman perusahaan/BEI dengan tanggal publikasi dan DPS yang cocok, paling lambat pada cum-date. Tanggal RUPS saja tidak membuktikan DPS telah diketahui ketika investor mengambil keputusan.
2. Bandingkan jadwal dan DPS Sectors dengan dokumen primer. Bedakan corporate action final/interim dan revisi jadwal. Konflik berarti `unverified` sampai diselesaikan.
3. Cocokkan harga cum/ex dan DPS pada basis saham/IDR yang sama. Audit split, bonus, rights, adjustment provider, tanggal sesi BEI, dan OHLCV kedua hari. Rasio yang tampak wajar bukan bukti basis terverifikasi.
4. Simpan URL dokumen, tanggal terbit, nilai yang dikutip, snapshot dan hasil pemeriksaan dalam artefak non-rahasia. `verified` hanya jika semua gerbang sumber, waktu dan basis lolos; selain itu beri alasan spesifik `partial`/`unverified`.

Endpoint riset boleh menyimpan diagnostik retrospektif. Timeline `forecast.status` tetap `not_available` sampai gate data serta evaluasi lebih luas disetujui. Hasil proyeksi gross selalu di luar biaya transaksi, pajak dan slippage.
