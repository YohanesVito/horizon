# Screenshot README

## Demo CFIN terbaru — 8 Oktober 2026

`cfin-demo-results-20261008.png` berasal dari web publik https://horizon-dividend.vercel.app/, arsip run `7768ae04-704b-4163-96ab-9a966bdfb8f1`: modal Rp10 juta, hanya CFIN ex-date 11 Juni 2025, all-in independen, pengamatan sampai 1 Juli 2025. Nilai akhir Rp9.270.120; hasil −Rp729.880. Screenshot ini menggantikan ilustrasi tiga strategi pada README utama. Angka dicocokkan dengan API live dan perhitungan komponennya di `outputs/development/cfin-demo-20261008.json`.

## Arsip screenshot lokal sebelumnya

Gambar di bawah tetap dipertahankan sebagai bukti lama; form dan tiga alokasinya bukan alur Simulasi saat ini.

Diambil pada 8 Oktober 2026 dari source aplikasi `8a8b5a6` menggunakan browser pada preview lokal Next.js → FastAPI, dengan SQLite terpisah. Gambar adalah screenshot antarmuka nyata; tidak memakai mockup atau gambar generatif.

| Berkas | Isi | Konteks |
|---|---|---|
| `analysis.jpg` | Overlay LPPF, mode perubahan persen, histori 2021–2025 yang tersedia | Pratinjau data; sumbu relatif ex-date berdasarkan urutan harga tersedia. |
| `simulation-input.jpg` | Modal contoh Rp100 juta dan pilihan alokasi | Form yang digunakan untuk contoh README; riwayat hanya dari database demo. |
| `simulation-results.jpg` | Perbandingan tiga alokasi pada replay 1 Maret–20 Mei 2025 | Input/hasil lengkap disimpan pada [bukti walkthrough](../../outputs/development/readme-walkthrough.json). |

Peristiwa contoh: BBCA 21 Maret, BMRI 14 April, LPPF 22 April 2025; entry 5 sesi sebelum cum; keluar setelah sinyal BEP harga dengan batas 20 sesi setelah ex; strategi utama rotasi. Seluruh nominal di luar biaya transaksi, pajak, dan slippage. Nilai akhir mencakup posisi terbuka dan piutang bila ada.

AI/provider key dinonaktifkan pada preview dokumentasi. Tidak ada screenshot yang mengklaim keluaran AI live. Screenshot ini bukan bukti versi atau kesehatan deployment publik.
