# Protokol evaluasi shadow ex-date

Status 8 Oktober 2026: protokol dan kode evaluasi dibekukan **sebelum** outcome kohort ASII/TLDN/AMRT/BSBK pada 13–14 Oktober tersedia. Ini riset privat F-02g/C-02/C-06/C-07, bukan kriteria bahwa model sudah akurat atau layak tampil live.

## Pertanyaan dan unit analisis

Target adalah **close ex-date pasar reguler** dari informasi yang tersedia saat capture pra-cum. Setiap unit adalah satu `symbol + ex_date + model_version`; empat unit pada kohort pertama dipilih karena kalender Sectors, close MCP dan PDF KSEI tersedia saat capture. Seluruh empat unit tetap dilaporkan, termasuk bila ada revisi atau data bermasalah. Jangan memilih ulang emiten setelah melihat harga ex-date.

Model yang dibekukan: `last_close − DPS`. Pembanding yang dapat diketahui pada cutoff sama: **flat** `last_close` (tanpa penyesuaian dividen). Model pooled F-02a yang membutuhkan close cum-date tidak memenuhi cutoff ini dan tidak menjadi pembanding primer. Keduanya memakai close 7 Oktober untuk kohort pertama; tidak boleh digeser ke close 8/9/12 Oktober sesudah capture.

## Metrik yang ditetapkan sebelum outcome

Untuk setiap event, `error_model = |harga_model − close_ex| / last_close × 100%` dan `error_flat = |last_close − close_ex| / last_close × 100%`. Ringkasan: `n` outcome, mean absolute error (MAE) kedua metode, median error model, serta menang/seri/kalah model terhadap flat per event. Harga, DPS, model dan tanggal capture awal tidak boleh diubah setelah hasil ex-date terlihat. Nilai report adalah **deskriptif**; tidak menunjukkan probabilitas trap, kepastian BEP atau return bersih pengguna.

Outcome baru boleh diambil dari MCP `fetch-daily-price` **sesudah tanggal ex-date WIB**. Simpan response mentah bertimestamp dan hash; `score` menolak bar selain satu bar tepat pada ex-date, snapshot yang diambil terlalu awal, perubahan sumber forecast, dan outcome ganda. Operator memeriksa PDF KSEI untuk revisi pasca-capture, sesi/tanggal perdagangan, serta apakah close Sectors raw atau adjusted sebelum memasukkan event ke subset bersih. Jika ada revisi atau basis tak setara, pertahankan rekaman asli dan tandai keterbatasannya; jangan menghapus event yang membuat model terlihat buruk.

Empat event adalah **uji operasional pipeline**, bukan ukuran sampel untuk klaim akurasi. Report selalu menyatakan `performance_claim_allowed=false`. Keputusan menampilkan forecast numerik memerlukan kohort prospektif tambahan di berbagai emiten/periode, audit basis harga independen, analisis ketidakpastian dan keputusan produk yang terdokumentasi **sebelum** membuka endpoint/UI. Skenario input pengguna tetap dapat dipakai, berlabel di luar biaya transaksi, pajak dan slippage.

## Operasi kohort pertama

DB riset lokal `.runtime/shadow-research-20261008.db` serta ekspor `outputs/forecast/shadow-captures-2026-10-08.json` harus tetap bersama arsip sumber. Status aman untuk dijalankan kapan pun:

```sh
DATABASE_URL=sqlite:////Users/killerbie/Documents/Codex/horizon/.runtime/shadow-research-20261008.db \
  .venv/bin/python -m work.score_ex_date_shadow_cohort status \
  --cohort outputs/forecast/shadow-captures-2026-10-08.json
```

Mulai **14 Oktober WIB** ASII/TLDN dapat diambil; mulai **15 Oktober WIB** AMRT/BSBK. Setelah audit notice/harga, jalankan perintah berikut. Ia mengabaikan event yang belum waktunya, mengambil harga melalui MCP hanya untuk event yang sudah lewat ex-date, menyimpan snapshot baru, dan menulis outcome sekali. Jika sumber/response bermasalah, error dilaporkan dan outcome tidak diisi.

```sh
DATABASE_URL=sqlite:////Users/killerbie/Documents/Codex/horizon/.runtime/shadow-research-20261008.db \
  .venv/bin/python -m work.score_ex_date_shadow_cohort collect-score \
  --cohort outputs/forecast/shadow-captures-2026-10-08.json \
  --output-dir outputs/forecast/shadow-outcomes
```

Jangan jalankan perintah koleksi dengan `DATABASE_URL` Supabase tanpa kebutuhan operasional yang jelas; kohort awal sengaja tetap di database riset lokal. Tidak ada scheduler, deploy, atau promosi forecast otomatis.
