# Desain dashboard dividen

Arahan PM: glassmorphism, dark mode, dan palet gambar Color Hunt. Nilai `#1A1A1` pada pesan dinormalisasi menjadi `#1A1A1D` sesuai nama berkas dan gambar.

Skill yang dipakai: web-design-style, mode reference dengan adaptasi tekstur/gradient dari preset awwwards-motion. Scope adalah aplikasi dashboard baru. Instruksi eksplisit PM untuk mulai kode dan tampilan dashboard mengarahkan implementasi; tidak perlu konfirmasi ulang gaya yang sudah dipilih. Preset glassmorphism tidak tersedia sehingga token di bawah diturunkan langsung dari arahan pengguna, bukan mengklaim adanya preset tersebut.

| Sumbu | Keputusan |
|---|---|
| Warna | Charcoal #1A1A1D, plum #3B1C32, berry #6A1E55, rose #A64D79. Teks ivory dan rose muda; hijau/amber hanya untuk makna status. |
| Tipografi | Sora untuk judul, Manrope untuk isi, angka tabular. Font lokal dari package agar build tidak bergantung pada Google Fonts. |
| Ruang dan bentuk | Sidebar ramping, dashboard padat tetapi lapang, radius panel 20–24 px, garis kaca 1 px, padding 20–28 px. |
| Gerak | Transisi pendek 160–220 ms, hover lembut, fokus keyboard jelas, reduced-motion. Gerak dekoratif tidak menghalangi penggunaan dashboard. |
| Tekstur | Lapisan radial plum di belakang panel transparan, backdrop blur, highlight pinggir kaca, tanpa gambar dekoratif yang mengganggu data. |
| Dependency | Next.js, React, Tailwind 4, lucide-react, ECharts, TanStack Query, fontsource Sora/Manrope. Tambah komponen hanya bila dibutuhkan alur. |

Nama produk/UI: Horizon, sesuai branding yang ditetapkan PM pada 8 Oktober 2026.

Alur utama: Peluang, Kalender, Simulator, Watchlist, dan Metodologi. Data snapshot/historis terlihat dekat judul dan angka. Semua output uang berlabel gross. Kosong, konflik jadwal, loading dan error punya tampilan yang dapat dipahami pengguna.
