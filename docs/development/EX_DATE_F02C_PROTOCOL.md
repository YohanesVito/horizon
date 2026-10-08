# Protokol F-02c: audit basis dan heterogenitas emiten

Ditulis 8 Oktober 2026 sebelum menghitung hasil model tambahan di bawah ini. Terkait C-02/C-06/C-07, F-02, ISS-041 dan ISS-042. Ini eksperimen riset pada sampel yang sudah dipilih dan dilihat; **bukan** holdout blind atau izin menampilkan prediksi live.

## Kohort dan batas bukti

- Bekukan `IntelligenceDataset` versi `intelligence-8a6d340ad419b922`: 48 event 2022–2025, 44 pasangan cum/ex eligible menurut F-02a, sembilan emiten. Jangan menghapus event karena hasil model buruk. Lima emiten produk saat ini (DMAS, LPPF, ADRO, CFIN, RALS) adalah prioritas audit sumber, bukan kohort test baru.
- Sectors MCP/REST snapshot lokal tetap sumber seri harga/jadwal untuk eksperimen. Simpan hash per file dan `retrieved_at`. Dokumen emiten/KSEI digunakan untuk membuktikan DPS dan tanggal publikasi; sumber harga luar Sectors digunakan hanya untuk pemeriksaan silang, dengan asal data yang belum tentu independen.
- Untuk setiap event, pisahkan gate: `provider_internal` (DPS/tanggal/bar konsisten), `official_dividend` (DPS dan jadwal sama dalam dokumen resmi terbit sebelum cum), `external_close_display` (dua close sama di sumber lain), `price_basis` (raw/adjusted serta aksi korporasi selama basis per saham terbukti), dan `point_in_time` (seluruh input diketahui saat keputusan). Nilai `unknown` tidak boleh dinaikkan menjadi `pass` lewat asumsi.
- LPPF 2026 dari F-02b adalah satu pemeriksaan harga prioritas, **tidak** ditambahkan ke 44 event latih. Bila sumber harga publik hanya menampilkan OHLCV identik tanpa penjelasan lineage, catat sebagai `match_unproven_independence`, bukan verifikasi basis.

## Pembanding yang dibekukan

Titik keputusan setelah close cum; target close ex. Untuk tahun uji 2023, 2024, 2025, latih hanya dengan event yang ex-date-nya pada tahun sebelumnya. Event 2026 LPPF diuji sekali dengan seluruh 44 event 2022–2025. Galat absolut tiap event: `abs(P̂_ex − P_ex) / P_cum × 100`; laporkan rerata, median, jumlah menang/kalah/tie terhadap full-DPS, per emiten dan ukuran sampel.

1. `flat`: `P̂_ex = P_cum`.
2. `full-DPS`: `P̂_ex = P_cum − DPS`.
3. `pooled`: `P̂_ex = P_cum − k_pool × DPS`, dengan `k_pool = median(PDR)` pada data latih, sama seperti F-02a.
4. `issuer-shrunk`: `k_issuer = median(PDR)` pada event latih emiten yang sama dan `k_shrunk = (4 × k_pool + n_issuer × k_issuer) / (4 + n_issuer)`. Jika `n_issuer = 0`, gunakan `k_pool`. Bobot empat pseudo-event adalah **pilihan riset tetap, tidak dituning terhadap hasil**, bukan estimasi optimal atau ambang validitas. Bila prediksi tidak positif, event dicatat sebagai gagal model, bukan dihapus diam-diam.

Perbandingan issuer-shrunk dengan pooled/full-DPS menguji apakah penyesuaian emiten sederhana memberi manfaat pada sampel kecil; jangan memilihnya untuk produk hanya karena rerata agregat lebih kecil. Tidak ada fitur sektor, IHSG, berita, fundamental, biaya, pajak atau slippage dalam model ini. Uji per emiten dengan `n` kecil hanyalah diagnostik; tidak ada klaim signifikansi atau kalibrasi. Keputusan rilis tetap `not_available` sampai basis harga, vintage seluruh input, dan validasi yang benar-benar belum dilihat memadai.
