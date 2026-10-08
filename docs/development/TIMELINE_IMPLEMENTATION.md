# Timeline overlay — implementasi 7 Oktober 2026

Scope T-03/T-04/T-05/T-06, kebutuhan percakapan C-02/C-06/C-08. PRD lampiran dan persetujuan UAT tetap belum tersedia. Tampilan berhasil dibangun; kelengkapan dataset untuk katalog penuh tetap belum tercapai (ISS-041).

Perubahan D-03 (8 Oktober): gate lima tahun di dokumen ini berlaku untuk **grafik overlay terverifikasi** saja. Daftar penemuan nama emiten memakai snapshot MCP Sectors terpisah tanpa gate itu; lihat `outputs/dividend-discovery/top-yield-2025-mcp-2026-10-08.json`. Peringkatnya yield historis 2025, bukan prediksi profit.

**Arahan PM berikutnya pada 8 Oktober (T-08) mengganti gate tampilan tersebut:** grafik boleh memuat tahun apa pun yang punya jendela harga/event pada snapshot, dengan gap yang dinyatakan eksplisit. Katalog tetap memisahkan pratinjau dari periode yang sudah diverifikasi. Bagian T-03–T-06 di bawah adalah bukti historis sebelum perubahan ini.

## Cara mencoba

1. Untuk checkout yang `.env.local`-nya mengarah ke Supabase/Dalang, jalankan backend preview dengan SQLite terpisah: `DATABASE_URL=sqlite:////private/tmp/horizon-local-preview.db .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`. Ini tidak membuka worker kedua pada Supabase.
2. Jalankan frontend setelah `npm run build` dengan `BACKEND_URL=http://127.0.0.1:8000 npm run start`; proxy memakai FastAPI lokal untuk perubahan yang belum dideploy.
3. Buka http://127.0.0.1:3000, pilih **Analisis emiten**. Lima kandidat yield historis dapat membuka grafik pratinjau dari snapshot harga yang tersedia; katalog terverifikasi masih kosong karena verifikasi peristiwa belum selesai.
4. Pilih salah satu kandidat atau gunakan pemilih emiten. Gap tahun muncul di atas grafik; untuk emiten dengan beberapa pembayaran dalam satu tahun, pilih event berdasarkan tanggal ex-date pada legenda.
5. Hover garis/area untuk fokus dan tooltip; klik tahun untuk mengunci, **Bandingkan semua** untuk melepas. Tombol tahun juga dapat dipakai dengan keyboard dan pada layar kecil.
6. Bandingkan **Perubahan %** dengan **Harga Rp**. Persentase adalah perubahan close terhadap close cum-date, tidak menambahkan dividen.
7. Untuk LPPF, pilih **2026 Aktual + Prediksi**. Harga aktual tersedia sampai6Oktober2026; panel prediksi masih kosong sesuai arahan PM. Empat kandidat lain belum memiliki snapshot periode berjalan pada integrasi ini, sehingga kontrolnya dinonaktifkan.
8. Label **Cum date, Ex date, Recording, Payment** selalu terlihat pada grafik periode fokus. Area cum→ex merah bila close ex lebih rendah dari close cum, hijau bila lebih tinggi, dan netral bila sama. Selisih ditampilkan di atas grafik. Label bergerak ke lajur terpisah ketika tanggal berdekatan; jarak waktu aktual tetap dipertahankan.

## Data dan pemrosesan

- Sumber: snapshot Sectors MCP `fetch-daily-price`, `fetch-corporate-actions`, `fetch-companies`; kalender melalui REST resmi. Kredensial hanya dibaca oleh skrip kolektor server, tidak ikut API atau frontend.
- Histori LPPF2021–2025:272bar dari lima jendela di sekitar event. Bukan harga kontinu lima tahun. Jenis final/interim belum diverifikasi; setiap seri berlabel pembayaran tercatat.
- Tambahan2026: tiga respons MCP harga (`current-prices-LPPF-*`) dengan123bar dan kalender April–Juni2026. Kolektor `work/collect_timeline_current.py` memakai cache, jendela maksimal90hari, jeda4detik. Pengambilan berakhir pada7Oktober2026; bar terakhir6Oktober2026. Tidak menyatakan harga live.
- `backend/timeline.py` membentuk titik harga, persen dari cum-date, offset hari kalender terhadap ex-date dan fase per event. Harga null tidak dibuat nol. Metadata/pemeriksaan yang belum terverifikasi menghalangi eligibility. Syarat lima tahun mencakup tepat satu siklus terverifikasi per tahun dengan identitas siklus yang sama; tidak diam-diam mencampurkan final/interim.
- `/api/timeline` mengembalikan katalog eligible dan status audit. `/api/timeline/LPPF` menolak data belum lengkap dengan422; `?preview=true` memberi pratinjau dengan `eligible=false`, `preview=true` dan daftar gap. Ticker tak tersedia404.
- Grafik SVG memakai data aktual, tanpa smoothing atau stacking. Sumbu memakai hari kalender karena kalender seluruh sesi belum disahkan. Marker tanggal tidak direntangkan menjadi fase dengan lebar buatan.
- RUPS dan declaration tetap dua field berbeda. Salah satu tanggal pengumuman yang terbukti terkait diperlukan untuk eligibility; tidak mewajibkan RUPS pada dividen yang memang tidak melalui RUPS. Label tanggal yang belum ada tetap belum tersedia.
- Periode2026 yang pembayarannya sudah lewat tetap berupa histori/aktual; status tahun berjalan tidak mengubah harga teramati menjadi hasil model. `forecast.points` kosong sampai engine tersedia.

## Bukti pemeriksaan

| Pemeriksaan | Hasil |
|---|---|
| Backend |46tes lulus, termasuk6tes timeline untuk normalisasi, jarak akhir pekan, harga invalid/null, gate lima tahun/siklus, pemisahan preview, error404/422 dan forecast kosong. Warning deprecation upstream ISS-016 tetap ada. |
| Frontend |Typecheck, lint dan build Next webpack lulus. Build terakhir mencakup perbaikan navigasi mobile. |
| API melalui port3000 |Health dan katalog200;0eligible/170kandidat; preview200dengan272+123bar; akses regulerLPPF422; tickerunknown404. Bukti `outputs/development/timeline-verification.json`. |
| Desktop1440 |Lima area/garis tampil. Klik2024mengunci fokus dan empat seri lain beropacity0.25. Hover historis29Mei2024menampilkanRp1.535,−14,01%,H+37 dan mengubah fase menjadi2024. ModeRp serta2026aktual+placeholder diperiksa. |
| Mobile390 |Sebelum perbaikan scrollWidth408; sesudah perbaikan390. Navigasi bergeser di dalam nav, halaman tidak melebar. Fokus2023denganEnterberhasil;2026aktual+placeholder tetap terbaca. |
| Browser logs |Tidak ada error/warning yang tercatat saat pemeriksaan terakhir. |
| Secret scan |Tidak ditemukan key Sectors tersimpan di source frontend, `.next/static` atau artifact timeline. |

Screenshot: `outputs/development/timeline-desktop.jpg`, `timeline-hover-desktop.jpg`, `timeline-current-desktop.jpg`, `timeline-mobile.jpg`, `timeline-current-mobile.jpg`.

Server preview direstart menggunakan interrupt sesi terminal setelah `kill` langsung ditolak sandbox. Ini bukan bug aplikasi; kedua server baru berhasil berjalan di port yang sama. Ukuran browser dikembalikan ke default setelah pengujian.

### Pemeriksaan tambahan T-06

Lint dan build/TypeScript lulus setelah perubahan label dan warna. Pemeriksaan fungsi mengonfirmasi histori2025 turun14,8989899%, kasus positif, nol dan harga hilang; kasus sintetis hanya untuk pemeriksaan logika, tidak tampil sebagai data pasar. Browser desktop1440 dan mobile390 memperlihatkan empat label tanpa tumpang tindih. Area merah mengikuti tahun2025/2024 dan tetap benar di modeRp/%. Mobile tidak melebar (scrollWidth390); log browser kosong dari error/warning. Bukti: `outputs/development/timeline-phase-labels-desktop.jpg` dan `timeline-phase-labels-mobile.jpg`. Backend tidak berubah sehingga46tes di atas tetap bukti tahap sebelumnya, bukan pemeriksaan yang dijalankan ulang pada T-06.

## Sisa pekerjaan

ISS-041 tetap OPEN: declaration historis, sesi pasar, unit/basis adjustment dan klasifikasi siklus belum disahkan. Pratinjau LPPF bukan pemenuhan syarat data lengkap seluruh emiten. Sampai verifikasi tersebut selesai, katalog Timeline kosong.

ISS-042 tetap DEFERRED oleh PM: rumus, training, interval ketidakpastian dan validasi prediksi. Tidak membuat engine dummy atau mengambil keputusan order. Hasil simulator lama tetap di luar biaya transaksi, pajak dan slippage. UAT akhir belum dilakukan; build dan pemeriksaan browser bukan persetujuan PM.

## T-08 — grafik parsial lima kandidat, 8 Oktober 2026

Sumber tambahan adalah snapshot Sectors MCP/REST yang sudah tersimpan di `outputs/intelligence/raw`, dinormalisasi lewat dataset intelligence yang sama. Tidak ada pengambilan provider baru. LPPF tetap memakai pilot 2021–2025; kandidat lain memakai event 2022–2025 dengan harga jendela tersedia: DMAS 5 event (2022/2023/2025), ADRO 9 (2022–2025), CFIN 2 (2023/2025), RALS 4 (2022–2025). UI menandai tahun tanpa kurva; kekosongan snapshot tidak ditafsirkan sebagai bukti tidak ada dividen. Event dalam tahun yang sama diberi ID/tanggal ex-date sendiri pada legenda dan fokus grafik. Kurva ADRO November 2024 dipotong sebelum ex-date dividen berikutnya pada Desember 2024, dengan alasan terlihat pada audit.

Semua data baru tetap pratinjau: tanggal declaration/RUPS terkait, basis adjustment, kelengkapan hari bursa, dan klasifikasi siklus belum disahkan. Tahun 2026 baru mempunyai snapshot aktual LPPF; engine forecast tetap kosong. Katalog `eligible` tidak lagi mewajibkan lima tahun, tetapi menuntut semua periode yang ditampilkan lolos review. ISS-041/042/057/058 tetap dilacak; tidak ada klaim prediksi atau hasil trading.
