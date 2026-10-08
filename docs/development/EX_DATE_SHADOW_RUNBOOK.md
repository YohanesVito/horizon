# Operasi riset ex-date shadow

Status 8 Oktober 2026: **empat baseline prospektif telah dibekukan secara lokal sebelum cum-date; belum ada outcome ex-date atau job terjadwal**. Ini bagian F-02e/F-02f/C-02/C-06/C-07. Outputnya tidak masuk timeline publik dan belum membuktikan akurasi.

## Titik keputusan dan sumber

Capture dilakukan setelah notice dividen tersedia, **sebelum tanggal cum-date menurut kalender WIB**, memakai close dari hari sebelumnya. Targetnya close ex-date. Baseline riset `pre-cum-full-dps-baseline-v0.1` menghitung `last_close − DPS`; ini bukan model pooled-PDR F-02a yang memakai close cum-date. Tanggal dan waktu capture berasal dari jam proses, bukan input operator. Satu pasangan `simbol + ex-date + versi` hanya dapat disimpan sekali.

Siapkan manifest JSON privat seperti contoh **fiktif** ini; sesuaikan semuanya dengan berkas nyata pada saat event muncul:

```json
{
  "symbol": "DEMO",
  "cum_date": "2026-11-10",
  "ex_date": "2026-11-11",
  "last_price_date": "2026-11-06",
  "last_close": 1000,
  "dps": 80,
  "calendar_snapshot": "outputs/research-input/calendar.json",
  "price_snapshot": "outputs/research-input/prices.json",
  "notice_file": "outputs/research-input/notice.pdf",
  "notice_url": "https://example.com/notice.pdf",
  "notice_document_date": "2026-11-06"
}
```

Snapshot kalender dan harga harus berformat arsip Sectors yang sudah dipakai repo: envelope JSON dengan `retrieved_at` timezone-aware dan `result`. Kalender harus memuat simbol, cum/ex dan DPS yang cocok; harga harus memuat simbol, tanggal dan close yang cocok. Notice disimpan sebagai berkas lokal dengan URL dan **tanggal yang tercetak pada dokumen**, bukan jam publikasi yang dikarang. Engine memeriksa kecocokan dua snapshot, mencatat kapan notice sudah dapat diamati pada saat capture, serta menyimpan hash SHA-256 ketiga sumber. Engine **belum mengaudit jam publikasi asli, apakah price close raw/adjusted dan basis DPS sebanding, atau apakah pengumuman direvisi**. `publication_time_verified` tetap false.

```sh
DATABASE_URL=sqlite:////private/tmp/horizon-shadow-local.db .venv/bin/python -m work.ex_date_shadow capture /private/tmp/event-manifest.json
```

Untuk deployment, proses operator memakai `DATABASE_URL` backend yang sudah aman; jangan menaruh connection string atau API key dalam argumen CLI, manifest, log atau Git. Capture menyisipkan record `shadow-forecast` ke tabel `horizon.records`/SQLite tanpa mengubah record lama. Duplicate ditolak. Database produksi hanya boleh diakses oleh proses yang memang diotorisasi; tidak ada endpoint tulis publik.

Setelah ex-date, ambil snapshot harga Sectors **setelah** hari ex-date, periksa basis harga dan peristiwa, lalu append hasil observasi sekali:

```sh
DATABASE_URL=sqlite:////private/tmp/horizon-shadow-local.db .venv/bin/python -m work.ex_date_shadow score 'shadow:DEMO:2026-11-11:pre-cum-full-dps-baseline-v0.1' outputs/research-input/prices-after-ex.json
```

Scoring menyimpan record `shadow-outcome` terpisah dengan actual close, error absolut sebagai persentase close terakhir dan hash snapshot baru. Forecast asli tidak diubah. Event dengan notice revisi atau harga yang tidak dapat disetarakan tetap harus ditandai dalam audit lanjutan dan tidak masuk klaim performa. Perbandingan model vs baseline dan interval ketidakpastian menunggu event baru yang cukup serta gate F-02.

## Kohort pertama dan langkah berikutnya

Snapshot kalender baru diambil 8 Oktober melalui endpoint REST v2 resmi Sectors; harga ASII, TLDN, AMRT, dan BSBK diambil melalui **MCP Sectors `fetch-daily-price`**. PDF KSEI masing-masing diperiksa terhadap DPS, cum, ex, dan payment pada snapshot; review tercatat di `outputs/forecast/notice-review-2026-10-08.json`. `work.prepare_ex_date_shadow` menyaring tanggal cum yang sudah lewat, harga yang tidak tersedia/stale, dan mismatch hasil review. Empat manifest serta alasan tiga event lain tidak disiapkan ada di `outputs/forecast/shadow-ready-2026-10-08/`.

Empat record `shadow-forecast` dibekukan pada 8 Oktober pukul 15:31 WIB, memakai close **7 Oktober**. ID dan semua hash sumber tersimpan di `outputs/forecast/shadow-captures-2026-10-08.json`, sedangkan database operasional riset lokal ada di `.runtime/shadow-research-20261008.db` (diabaikan Git). Baseline riset: ASII Rp4.682, TLDN Rp580, AMRT Rp1.210,5 dan BSBK Rp44. Ini **bukan** harga target untuk pengguna; tidak ada metrik galat sampai close ex-date diketahui. Kohort dipilih dari event yang saat capture memiliki notice dan harga, sehingga tidak mewakili semua saham. AALI/GEMS sudah cum 8 Oktober; AUTO memiliki revisi rasio KSEI bertanggal 8 Oktober dan sengaja tidak dimasukkan. MCP `fetch-corporate-actions` tidak mengembalikan upcoming AMRT meskipun kalender REST dan PDF KSEI cocok; gap ini dicatat di ISSUES.md.

Untuk event berikutnya, ambil snapshot kalender `upcoming_dividend` dan harga MCP terbaru, arsipkan notice resmi, isi review dokumen, lalu jalankan `python -m work.prepare_ex_date_shadow` dan `capture` sebelum cum-date WIB. Jangan menimpa snapshot/manifest yang sudah dipakai. Mulai **14 Oktober WIB** untuk ASII/TLDN dan **15 Oktober WIB** untuk AMRT/BSBK, CLI `work.score_ex_date_shadow_cohort collect-score` dapat mengambil bar ex-date lewat MCP dan append outcome ke database riset yang sama. `status` aman dijalankan lebih awal dan pada 8 Oktober melaporkan 0 outcome/4 pending. Perintah, metrik yang dibekukan, serta gate audit ada di [protokol evaluasi](./EX_DATE_SHADOW_EVALUATION.md). Setelah koleksi, audit harga dan corporate action sebelum klaim apa pun. Perbandingan dan klaim performa tetap menunggu beberapa kohort independen, audit raw/adjusted serta price source independen; satu kohort empat saham tidak cukup untuk gate F-02.
