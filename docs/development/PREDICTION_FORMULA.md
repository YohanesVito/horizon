# Hipotesis formula prediksi dividen

Versi: **0.5 — skenario eksplisit dan baseline shadow pre-cum**, 8 Oktober 2026. Pemilik keputusan produk: PM. Terkait C-02/C-04/C-06/C-07, S4-02, T-02, F-01 dan F-02.

Dokumen ini adalah tempat iterasi **logika finansial tim** untuk satu dividend play di saham Indonesia: rentang harga sepanjang timeline, risiko rugi setelah menerima dividen, dan waktu menuju BEP. Versi 0.2 menambahkan baseline yang dilatih dan diuji **secara retrospektif** pada sampel pilihan; versi 0.3 menguji satu event LPPF 2026 tanpa mengubah model; versi 0.4 mengaudit sumber per event dan satu pembanding efek emiten; versi 0.5 memisahkan skenario pengguna dari baseline prospektif pre-cum. Ini bukan angka prediksi produk, rekomendasi transaksi, atau perubahan pada [protokol statistik historis v1](./INTELLIGENCE_POLICY.md). Implementasi prediksi periode berjalan masih ditahan (ISS-024/ISS-042). Setiap revisi perlu mempertahankan versi lama beserta alasan dan bukti uji.

## 1. Pertanyaan keputusan dan batas observasi

Untuk emiten `i`, pada **waktu keputusan** `t_dec`, pengguna memilih aturan masuk, aturan keluar atau batas pengamatan `H`, dan modal. Engine kelak harus menjawab:

1. Berapa rentang harga yang masuk akal pada titik timeline, terutama menjelang cum-date, ex-date, dan sesudahnya?
2. Dengan aturan itu, berapa peluang **hasil total gross** negatif meski berhak atas dividen?
3. Berapa lama sampai harga kembali ke harga beli (**BEP harga**) dan sampai harga plus hak dividen menutup harga beli (**BEP total**)?
4. Bagaimana hasil dan lama modal tertahan berubah jika aturan masuk/keluar diganti?

Semua fitur model, jadwal, dan fundamental historis harus terbukti tersedia **paling lambat pada `t_dec`**. Tanggal dari pengumuman resmi diberi status `terkonfirmasi`; tanggal yang diperkirakan diberi status `estimasi`; declaration yang tidak ditemukan tetap `belum tersedia`, tidak diganti tanggal RUPS. Proyeksi setelah data harga terakhir selalu dibedakan secara visual dari aktual.

## 2. Definisi target yang harus konsisten

| Simbol | Arti |
|---|---|
| `P_b` | Harga beli per saham pada aturan masuk yang dinyatakan (misalnya close pada hari bursa tertentu). |
| `P_x(H)` | Harga jual per saham menurut aturan keluar pada horizon `H`; bukan harga yang dijamin dapat dieksekusi. |
| `D_eligible` | Dividen tunai per saham yang **benar-benar menjadi hak** dari posisi tersebut; nol bila keluar sebelum memperoleh hak. Dividen dapat masih berupa piutang sebelum payment-date. |
| `q` | Jumlah saham yang dapat dibeli menurut modal dan aturan lot. |
| `H` | Batas setelah ex-date dalam **hari bursa**, kecuali eksplisit tertulis hari kalender. |

```text
Laba_total_gross(H) = q × [P_x(H) − P_b + D_eligible]
Return_total_gross(H) = [P_x(H) − P_b + D_eligible] / P_b
Trap(H) = 1 jika P_x(H) − P_b + D_eligible < 0; selain itu 0
BEP_harga(t) = P_t ≥ P_b
BEP_total(t) = P_t + D_eligible ≥ P_b
T_pulih_harga = hari bursa pertama sejak ex-date saat BEP_harga(t) benar
T_pulih_total = hari bursa pertama sejak ex-date saat BEP_total(t) benar
```

Definisi trap ini **tergantung harga beli dan aturan keluar**, bukan sekadar penurunan pada ex-date. Untuk analisis ex-date yang terpisah, `PDR = (P_cum_close − P_ex_close) / D` hanya dihitung bila `D > 0`, basis harga/DPS sebanding, dan kedua close tersedia. PDR bukan probabilitas trap. Biaya transaksi, pajak, dan slippage belum dimasukkan sesuai keputusan PM; seluruh hasil diberi label **gross, di luar biaya transaksi, pajak, dan slippage**. Hari pembayaran menentukan arus kas, bukan hari saat hak dividen mulai ada.

## 3. Data dan asalnya

| Masukan | Fungsi dalam model | Status/prasyarat |
|---|---|---|
| Jadwal declaration/RUPS, cum, ex, recording, payment; DPS | Menentukan fase dan hak dividen | Sectors MCP untuk aksi korporasi, REST resmi Sectors untuk kalender; simpan sumber, waktu ambil, dan status terkonfirmasi/estimasi. Declaration masih gap ISS-002. |
| OHLCV emiten, IHSG, indeks/peer sektor | Harga aktual, return, volatilitas, likuiditas, kondisi pasar | Normalisasi split dan konsistensi mata uang/basis saham wajib diaudit; harga bolong tetap bolong. |
| Harga dan volume **sebelum** `t_dec` | Fitur momentum, volatilitas, likuiditas yang mungkin membantu | Jendela fitur ditetapkan sebelum uji; tidak boleh mengambil harga setelah `t_dec`. |
| Fundamental/payout/cash flow/utang yang telah dipublikasikan sebelum `t_dec` | Kandidat fitur kemampuan membayar dividen dan perubahan rezim | Butuh timestamp publikasi/vintage; saat belum ada, **jangan dipakai** dalam backtest prediktif (ISS-007). Relevansi dan transformasi dapat berbeda per sektor. |
| Aturan pengguna: tanggal masuk, exit, modal, horizon | Menentukan label target dan simulasi nominal | Dibekukan bersama versi engine; entitlement dan T+2 mengikuti aturan simulasi yang diaudit. |

Kandidat emiten **tidak harus memiliki lima tahun grafik lengkap** untuk ditemukan (keputusan D-03). Itu berbeda dari syarat kelengkapan overlay chart dan syarat kecukupan sampel **model prediksi**, yang belum ditentukan dan harus diuji terpisah. Jangan mengisi kekurangan event satu emiten dengan angka emiten lain tanpa label dan model pooling yang eksplisit.

## 4. Model harga: hipotesis bertahap

### 4.1 Baseline yang harus dikalahkan

Baseline pertama adalah distribusi perubahan harga pada event historis dengan aturan entry/exit identik, ditampilkan sebagai **analog historis** beserta ukuran sampel. Baseline kedua adalah skenario harga tetap atau return pasar, untuk memeriksa apakah model rumit memang menambah nilai. Keduanya belum boleh diberi label probabilitas masa depan. Periode dari event yang sudah dipakai memilih universe/aturan tidak boleh diam-diam menjadi holdout.

### 4.2 Reaksi khusus pada ex-date

```text
P_ex_close = P_cum_close × (1 + beta_i × R_pasar,cum→ex)
             − kappa_(i, sektor, rezim) × D + epsilon_ex
```

`kappa` adalah koefisien penurunan harga terhadap DPS **yang harus diestimasi**, bukan konstanta `1` atau angka universal. `beta_i × R_pasar` memisahkan sebagian pergerakan pasar pada interval yang sama; `epsilon_ex` menyisakan perubahan harga yang tidak dijelaskan. Untuk prediksi, return pasar masa depan juga tidak diketahui: gunakan skenario/distribusi yang dilatih hanya dari data sebelum `t_dec`. Estimasi issuer tunggal mungkin sangat bising karena sedikit event; bandingkan pooling lintas sektor/issuer dengan model sederhana. Jangan menghitung kembali dampak ex-date di model fase lain.

Studi [Frank & Jagannathan (1998)](https://experts.umn.edu/en/publications/why-do-stock-prices-drop-by-less-than-the-value-of-the-dividend-e/) menunjukkan rata-rata penurunan ex-date dapat berbeda dari DPS pada sampel Hong Kong; itu alasan **menguji `kappa`**, bukan bukti nilai koefisien yang cocok untuk Indonesia atau setiap emiten.

### 4.3 Jalur di luar ex-date

```text
r_i,t = log(P_i,t / P_i,t−1)
      = beta_i × r_pasar,t + mu_fase(k, X_sebelum_t_dec) + epsilon_i,t
```

`k` adalah jarak hari bursa dari ex-date; fase meliputi pra-pengumuman (jika tanggal diketahui), pasca-pengumuman, menjelang cum, dan pemulihan setelah ex. `X_sebelum_t_dec` dapat memuat volatilitas, volume relatif, ukuran yield saat keputusan, dan fundamental yang mempunyai vintage sah. Perbedaan emiten/sektor dipelajari dengan pooling atau efek parsial; tidak menetapkan bobot sektor manual tanpa uji. Residual/perubahan rezim harus ikut menentukan lebar rentang hasil. Harga pada tanggal kalender non-bursa tidak dipalsukan.

Bila data memadai, model menghasilkan **jalur harga bersama** dari harga aktual terakhir melalui event: misalnya median dan rentang kuantil pada tiap fase, dengan dependensi antarhari dipertahankan. Ini hipotesis arsitektur, bukan formula yang sudah menghasilkan kurva di website. Sebelum layak, tampilkan aktual, jadwal yang diketahui, serta placeholder/analog berlabel; jangan gambar garis prediksi numerik seolah sudah tervalidasi.

## 5. Probabilitas trap dan waktu pulih

Jika kelak tersedia `M` jalur harga prediktif yang telah diuji dan aturan exit sudah tetap, estimasi konsisten dari jalur yang **sama**:

```text
p_trap(H | informasi_t_dec, aturan) ≈ (1/M) × Σ_m 1[P_x,m(H) − P_b + D_eligible < 0]
F_pulih_harga(H) ≈ (1/M) × Σ_m 1[T_pulih_harga,m ≤ H]
F_pulih_total(H) ≈ (1/M) × Σ_m 1[T_pulih_total,m ≤ H]
```

Frekuensi dari simulasi hanya sebaik model jalurnya; **bukan probabilitas terkalibrasi secara otomatis**. Model langsung, misalnya regresi logistik pooled `logit(p_trap) = intercept + efek_sektor + efek_emiten + koefisien·X_sebelum_t_dec`, adalah pembanding yang dapat diuji bila jumlah label memadai. Jangan menggabungkan probabilitas dari model langsung dan jalur harga tanpa rancangan kalibrasi yang jelas.

Yang **sudah ada sekarang** adalah proporsi trap historis per definisi/horizon beserta interval Wilson, serta kurva Kaplan–Meier untuk waktu pulih dengan event belum pulih sebagai *right-censored*. Keduanya deskriptif; asumsi independensi dan sensor non-informatif perlu diuji, terutama saat ex-date lain memotong observasi. `1 − S_KM(H)` adalah estimasi **pemulihan historis pada sampel yang memenuhi syarat**, bukan peluang individual saham periode berikutnya. Jika belum pulih sampai akhir data, statusnya `belum teramati/tersensor`, bukan waktu pulih nol atau tak hingga. Acuan metode: [NIST tentang Kaplan–Meier](https://www.itl.nist.gov/div898/handbook/apr/section2/apr215.htm).

## 6. Cara membuktikan atau menolak hipotesis

1. **Bekukan protokol sebelum melihat hasil baru.** Pilih universe tanpa memakai hasil masa depan, jendela entry/exit/H, definisi close vs harga eksekusi, kebijakan event berulang, split, likuiditas, dan batas observasi. Simpan versi aturan serta alasan perubahan.
2. **Bangun dataset point-in-time.** Untuk setiap keputusan historis, rekonstruksi apa yang benar-benar diketahui saat itu; karantina tanggal, DPS, aksi korporasi, atau fundamental dengan basis/vintage yang tidak pasti. Pecah berdasarkan waktu; jangan acak baris dari event yang sama ke train dan test.
3. **Uji walk-forward dan kelompok yang belum dilihat.** Bandingkan baseline analog/pasar dengan model ex-date + fase, lalu uji stabilitas antar-emiten, sektor, dan rezim. Sampel sembilan emiten yang dipilih belakangan dan 2025 yang pernah dilihat **bukan holdout bersih**.
4. **Ukur target yang tepat.** Untuk harga: kesalahan level/perubahan dan cakupan kuantil pada tiap fase. Untuk trap: Brier score, log loss, reliabilitas/kalibrasi dan jumlah kasus per bucket probabilitas. Untuk pemulihan: evaluasi survival dengan censoring yang sesuai; jangan memberi label tidak pulih permanen pada observasi yang terpotong. Untuk keputusan produk: return gross, drawdown, durasi modal tertahan, dan peluang yang terlewat dibanding aturan sederhana. Prinsip evaluasi prediksi probabilistik: [Gneiting & Raftery (2007)](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).
5. **Gate rilis nilai prediksi.** Angka probabilitas/rentang harga hanya tampil bila cakupan data, kebocoran waktu, kalibrasi out-of-sample, dan ketidakpastian telah ditinjau bersama PM. Ambang numeriknya belum ditetapkan; jangan membuat ambang ilmiah fiktif. Jika gagal, tampilkan statistik historis/skenario berlabel dan alasan prediksi belum tersedia.

## 7. Kontrak hasil untuk UI dan simulator

Setiap hasil kelak menyimpan `ticker`, aturan entry/exit/H, modal, `as_of`, tanggal data harga terakhir, event dan jadwal dengan statusnya, sumber/vintage, versi formula/dataset, ukuran sampel, status validasi, dan asumsi biaya. Timeline menampilkan aktual serta, hanya jika layak, median/rentang prediksi dan pemisah eksplisit. Panel risiko membedakan `frekuensi historis`, `skenario`, dan `probabilitas terkalibrasi`; panel BEP membedakan BEP harga vs total dan menampilkan horizon/censoring. Simulator menghitung nominal dari jalur/aturan yang sama, sehingga grafik dan angka risiko tidak saling bertentangan.

Pada integrasi UI BR-04, panel Engine Riset menampilkan keluaran `IntelligenceDataset` yang **sudah ada**: jumlah event lengkap, frekuensi trap historis dengan rentang Wilson, serta median BEP harga/total dari kurva pemulihan. Aturan entry dan horizon aktif ditampilkan. Ini penggunaan baseline deskriptif, bukan implementasi persamaan harga di bagian 4 atau probabilitas masa depan di bagian 5. Endpoint timeline tetap mengembalikan `forecast.status = not_available` dan `points = []`; tidak ada garis atau angka prediksi numerik yang dibuat dari sampel kecil ini.

## 8. Pertanyaan terbuka untuk iterasi

| Keputusan berikutnya | Bukti yang dibutuhkan |
|---|---|
| Aturan masuk/keluar dan horizon utama mana yang paling bernilai bagi pengguna? | Uji tugas pengguna + distribusi hasil replay untuk beberapa aturan **yang dibekukan lebih dulu**. |
| Apakah efek ex-date lebih stabil per emiten, sektor, atau rezim? | Sampel event bersih, perbandingan walk-forward dengan pooling, dan interval ketidakpastian. |
| Apakah data declaration dan vintage fundamental tersedia point-in-time? | Audit endpoint/dokumen dengan timestamp publikasi; tanpa itu fitur terkait tetap dikeluarkan. |
| Apa syarat minimum agar angka prediksi boleh tampil? | Kriteria ukuran/cakupan sampel, kalibrasi dan stabilitas yang diputuskan sebelum evaluasi akhir. |
| Bagaimana memodelkan tanggal event yang masih belum diumumkan? | Dataset tanggal publikasi historis dan evaluasi terpisah; **jangan menyamakan forecast jadwal dengan jadwal resmi**. |

## 9. Eksperimen ex-date v0.2 — riset retrospektif, belum untuk grafik live

PM memilih **close ex-date** sebagai target pertama. Titik keputusan sementara adalah sesudah close cum-date. Fitur model awal hanya `P_cum_close` dan DPS; target adalah `P_ex_close`. Data sembilan emiten dari snapshot Sectors MCP (corporate actions dan harga) ditambah kalender REST resmi. Empat dari 48 event dikarantina karena basis sebelum split belum terverifikasi; 44 pasang cum/ex tersisa. Sesi cum/ex harus berupa dua bar teramati berurutan, OHLCV dan DPS valid. Ini **tidak** membuktikan seluruh sesi BEI lengkap atau DPS sudah diumumkan pada tanggal keputusan.

Pembanding yang sengaja sederhana:

```text
flat:        P̂_ex = P_cum
full-DPS:    P̂_ex = P_cum − DPS
pooled-PDR:  kappa = median((P_cum − P_ex) / DPS) pada event latih
             P̂_ex = P_cum − kappa × DPS
```

`kappa` dihitung lintas emiten; belum ada beta pasar, efek sektor, interval prediksi, atau kalibrasi. Pembanding `full-DPS` adalah asumsi mekanis untuk diuji, bukan aturan harga pasti. Pilihan median dan batas delapan event latih adalah **guardrail eksperimen**, dibuat setelah mengetahui besar sampel, bukan ambang validitas ilmiah. Penjelasan ekonomi tentang variasi penurunan ex-date dibahas oleh [Frank dan Jagannathan (1998)](https://experts.umn.edu/en/publications/why-do-stock-prices-drop-by-less-than-the-value-of-the-dividend-e/); temuannya tidak menetapkan `kappa` untuk BEI.

Evaluasi memisahkan tahun: semua event tahun uji dilatih hanya dengan event **tahun sebelumnya**. Ini mengikuti prinsip evaluasi asal bergulir yang dijelaskan [Tashman (2000)](https://www.sciencedirect.com/science/article/pii/S0169207000000650), tetapi belum setara validasi point-in-time. Ukuran kesalahan adalah `abs(P̂_ex − P_ex) / P_cum × 100`, rata-rata atas event; bias memakai selisih bertanda `P̂_ex − P_ex`. Hasil dari snapshot `intelligence-8a6d340ad419b922`:

| Tahun uji | Event latih → uji | MAE flat | MAE full-DPS | MAE pooled-PDR |
|---|---:|---:|---:|---:|
| 2022 | 0 → 8 | — | — | — |
| 2023 | 8 → 12 | 5,679% | 1,653% | 1,603% |
| 2024 | 20 → 12 | 5,859% | 2,921% | 2,444% |
| 2025 | 32 → 12 | 7,893% | 1,193% | 1,156% |
| 2023–2025 | 36 diuji | 6,477% | 1,923% | 1,734% |

Model pooled unggul tipis pada sampel ini: 22 dari 36 event lebih dekat ke harga aktual daripada full-DPS, 14 lebih jauh. Ia justru lebih buruk pada LPPF (MAE 3,795% versus 2,733%), CFIN (1,934% versus 1,071%), dan BBCA (1,678% versus 1,629%). Ini alasan konkret menguji efek emiten, bukan menerapkan satu `kappa` universal. **Belum ada holdout bersih**: universe dan 2025 sudah pernah dilihat dalam riset, dan seluruh file sumber diambil pada 2026 sesudah event. Timestamp publikasi DPS/jadwal, basis harga/DPS, kalender sesi resmi dan kondisi pasar belum diverifikasi. Angka MAE bukan rentang keyakinan atau jaminan hasil pada periode berikutnya. Keputusan v0.2: **baseline riset diterima untuk iterasi, rilis prediksi harga ditahan**. Endpoint `/api/research/ex-date` menyediakan setiap event, tahun latih, prediksi historis dan kesalahan; artefak hasil lengkap ada di [ex-date-retrospective-v0.1.json](../../outputs/forecast/ex-date-retrospective-v0.1.json). Timeline produksi tetap `forecast.status = not_available`.

Sebelum rilis angka live: verifikasi arsip pengumuman beserta waktu DPS diketahui, audit aksi korporasi/basis per event dan sesi BEI, pilih universe/cutoff sebelum data baru masuk, lalu jalankan evaluasi yang benar-benar belum dilihat serta cek stabilitas issuer/sektor dan ketidakpastian. Perubahan parameter atau seleksi setelah melihat MAE harus dicatat sebagai eksperimen baru.

## 10. Verifikasi tambahan v0.3 — LPPF ex-date 2026

[Protokol uji](./EX_DATE_VERIFICATION_PROTOCOL.md) membekukan satu event LPPF 2026 dan pembanding **sebelum** pasangan harga 2026 diperiksa. Model pooled-PDR v0.2 tetap memakai 44 event latih 2022–2025, tanpa retuning. Uji ini temporal, **bukan holdout blind**: universe dan emiten sudah terlihat dalam pekerjaan sebelumnya; snapshot Sectors diambil setelah ex-date.

Dokumen [emiten](https://matahari.com/pages/corporate-announcements) mencatat keterbukaan dividen pada **16 April 2026**; [KSEI](https://web.ksei.co.id/Announcement/Files/LPPF_DIV_20260427_ID.pdf) bertanggal **17 April 2026**. Keduanya mendahului cum-date 23 April; KSEI menyatakan DPS Rp250, ex-date 24 April, recording 27 April dan pembayaran 4 Mei. Data kalender Sectors cocok untuk event ini. [Tabel dividen resmi emiten](https://matahari.com/pages/dividends-en) juga cocok dengan DPS/ex-date empat event latih LPPF 2022–2025; [arsip pengumuman](https://matahari.com/pages/corporate-announcements) menempatkan pengumuman masing-masing sebelum cum-date. Audit konten/vintage lengkap per arsip dan seluruh **40 event emiten lain** belum dilakukan.

Snapshot harga Sectors MCP memberi close cum Rp1.940 dan close ex Rp1.650, sehingga penurunan Rp290 dan PDR teramati 1,16. Dua bar OHLCV berurutan dan valid; aksi split yang tercatat di snapshot tidak ada pada 2022–ex2026. Ini **belum membuktikan** basis adjustment harga dan DPS seragam atau close independen. Karena itu event berstatus *partial verification*. Hasil perbandingan satu event, dengan galat absolut sebagai persen harga cum:

| Metode dibekukan | Estimasi close ex | Galat |
|---|---:|---:|
| Harga tetap | Rp1.940 | 14,948% |
| Turun sebesar DPS | Rp1.690 | **2,062%** |
| Pooled-PDR, `kappa = 0,886232` | Rp1.718,44 | 3,528% |
| **Close aktual di snapshot Sectors** | **Rp1.650** | — |

Pooled-PDR **kalah dari full-DPS** pada LPPF 2026, searah dengan kelemahan LPPF pada evaluasi 2023–2025. Jadi peningkatan MAE agregat v0.2 tidak cukup untuk menerapkan satu koefisien pada LPPF atau semua saham. Hasil gross ilustratif bila benar-benar membeli pada close cum dan menjual pada close ex adalah Rp1.650 − Rp1.940 + Rp250 = **−Rp40/saham** (−2,062% dari harga beli), di luar biaya transaksi, pajak, dan slippage; close historis tidak menjamin harga eksekusi. Ini bukan peluang trap dan tidak memberi tahu kapan harga pulih. [Artefak uji](../../outputs/forecast/lppf-2026-exdate-verification.json) menyimpan input, hash snapshot, pemeriksaan sumber dan hasil; `python -m work.verify_ex_date_2026` mereproduksinya.

**Keputusan v0.3:** hipotesis bahwa pooled-PDR universal cukup untuk rilis **ditolak**. Belum cukup bukti untuk memilih model pengganti; full-DPS tetap pembanding, bukan prediksi tervalidasi. Nilai live tetap `not_available`. Langkah berikutnya adalah verifikasi basis harga terhadap sumber independen/aturan adjustment, audit arsip seluruh kohort, lalu evaluasi event baru dengan universe, cutoff dan kriteria rilis yang ditetapkan sebelum label tersedia.

## 11. Audit dan pembanding efek emiten v0.4 — tetap riset

[Protokol F-02c](./EX_DATE_F02C_PROTOCOL.md) membekukan 44 pasangan F-02a serta bobot shrinkage **sebelum hasil model tambahan dihitung**. Audit otomatis mencatat hash dan waktu ambil setiap file Sectors MCP/REST, bar OHLCV, konflik provider, serta status dokumen primer. Dari 48 event sumber, 44 lolos pemeriksaan internal dan empat tetap dikecualikan. Untuk dividen resmi, **tiga event LPPF 2023–2025** cocok dengan pengumuman yang dapat dibaca dan terbit sebelum cum-date: [KSEI 2023](https://www.ksei.co.id/Announcement/Files/LPPF_DIV_20230411_ID.pdf), [KSEI 2024](https://www.ksei.co.id/Announcement/Files/LPPF_DIV_20240423_ENG.pdf), dan [emiten 2025](https://cdn.shopify.com/s/files/1/0666/9212/0727/files/Schedule_of_Distribution_of_Final_Dividend_FY_2024.pdf?v=1751347947) bersama [arsip tanggal tayang](https://matahari.com/pages/corporate-announcements). Empat puluh event eligible lain dan empat event yang dikecualikan belum memiliki audit dokumen primer lengkap; `pass` internal **bukan** berarti point-in-time atau harga terverifikasi.

Khusus **LPPF 2022**, [KSEI 6 April](https://www.ksei.co.id/Announcement/Files/LPPF_DIV_20220418_ID.pdf) menyebut pembayaran 6 Mei, tetapi [riwayat dividen emiten sekarang](https://matahari.com/pages/dividends-en) dan snapshot Sectors menyebut 28 April. [Arsip emiten](https://matahari.com/pages/corporate-announcements) memuat pengumuman jadwal 12 April, sebelum cum 13 April; isi dokumen revisi belum berhasil diperiksa di audit ini. DPS Rp250 serta cum/ex 13/14 April cocok, tetapi payment diberi status **revisi belum dituntaskan**, bukan konflik DPS atau izin membuang event yang performanya tidak disukai. Perubahan jadwal semacam ini menunjukkan mengapa satu snapshot final tidak cukup untuk merekonstruksi informasi saat keputusan.

Untuk LPPF 2026, tampilan harga [Intervest](https://intervest.io/symbol/LPPF/historical) yang terindeks mencantumkan close Rp1.940/Rp1.650 pada 23/24 April, sama dengan Sectors. Asal data kedua layanan tidak terbukti terpisah; tampilan silang ini **belum** membuktikan harga raw, penyesuaian split/dividen atau basis DPS. Gate basis dan sumber harga independen tetap `unknown`.

Pembanding tambahan menggunakan `k_issuer = median(PDR)` event emiten itu pada tahun latih, lalu `k_shrunk = (4 k_pooled + n_issuer k_issuer)/(4+n_issuer)`. Empat pseudo-event adalah pilihan tetap untuk eksperimen, bukan tuning yang optimal. Semua event uji 2023–2025 memakai hanya tahun-tahun sebelumnya; hasil retrospektif pada 36 event:

| Metode | MAE % harga cum | Median galat % | Menang/kalah vs full-DPS |
|---|---:|---:|---:|
| Harga tetap | 6,477 | 5,736 | 3/33 |
| Full-DPS | 1,923 | 1,201 | pembanding |
| Pooled-PDR | **1,734** | **1,098** | 22/14 |
| Efek emiten dengan shrinkage | 1,914 | 1,349 | 17/19 |

Model emiten sederhana **tidak memperbaiki** pooled secara keseluruhan; pada LPPF 2023–2025 galatnya 3,513% versus pooled 3,795% dan full-DPS 2,733% (`n=3`). Pada satu event LPPF 2026, model emiten memberi Rp1.705,26 (galat 2,849%), masih lebih buruk daripada full-DPS Rp1.690 (2,062%). Analisis per emiten lain tersimpan bersama ukuran sampel pada [artefak audit F-02c](../../outputs/forecast/ex-date-f02c-audit.json). Tiga tahun uji dan satu event 2026 berasal dari universe terpilih serta snapshot pascakejadian; angka ini **tidak** membuktikan keuntungan prediktif pada saham baru.

**Keputusan v0.4:** hipotesis bahwa efek emiten sederhana ini cukup memperbaiki model **ditolak untuk rilis**; tidak men-tuning bobot setelah melihat hasil. Seluruh model tetap riset, `forecast.status = not_available`. Pekerjaan berikutnya: dapatkan dokumen revisi LPPF 2022, audit dokumen dan basis harga seluruh kohort, temukan feed raw/adjusted dengan lineage jelas, lalu jalankan evaluasi baru yang dibekukan sebelum labelnya tersedia. Semua simulasi laba tetap gross, di luar biaya transaksi, pajak, dan slippage.

## 12. Skenario dan baseline shadow v0.5

`POST /api/ex-date/scenario` menghitung hasil dari **modal, harga beli, DPS, dan harga jual ex-date asumsi** yang dimasukkan pengguna. Jumlah saham = `100 × floor(modal/(100 × harga beli))`; dividen = `jumlah saham × DPS`; laba gross = `jumlah saham × (harga ex asumsi − harga beli + DPS)`. BEP harga = harga beli; BEP total = harga beli − DPS. Sisa kas tidak dianggap laba. UI tidak mengambil DPS atau close historis sebagai input periode mendatang. Hasil berstatus `scenario` dan selalu diberi label di luar biaya transaksi, pajak, dan slippage. Perhitungan tidak memakai model riset untuk menyatakan peluang atau proyeksi harga.

Untuk keputusan membeli **sebelum cum-date**, baseline shadow berbeda dari F-02a: `P_ex_baseline = P_close_terakhir_sebelum_cum − DPS`. Baseline ini sengaja sederhana; tidak mengandung harga cum-date yang belum diketahui saat keputusan. [Runbook](./EX_DATE_SHADOW_RUNBOOK.md) menjelaskan gate waktu, hash snapshot, sumber notice dan dua record append-only (`shadow-forecast`, `shadow-outcome`). Capture sukses hanya membuktikan input cocok dengan berkas Sectors yang dipasok; waktu publikasi notice, revisi, raw/adjusted close, dan basis DPS masih memerlukan audit. `forecast.status = not_available` pada timeline tidak berubah.

## 13. Kohort prospektif pertama v0.6

Aturan **tidak diubah setelah melihat outcome**: untuk setiap saham yang lolos gate, gunakan close Sectors terakhir yang sudah selesai sebelum tanggal capture, kurangi DPS tunai dari kalender Sectors yang cocok dengan PDF KSEI, dan targetkan close pada ex-date pasar reguler. Candidate gate pada 8 Oktober 2026: cum-date sesudah tanggal capture WIB, PDF KSEI tersedia serta DPS/cum/ex/payment cocok, close MCP paling lama tujuh hari kalender, dan `0 < DPS < close`. Empat saham dipilih dari tujuh event upcoming yang dikembalikan kalender: ASII, TLDN, AMRT, BSBK. AALI/GEMS sudah cum hari itu; AUTO dikeluarkan karena notice revisi rasio pada hari capture. Pemilihan berdasar ketersediaan data berarti kohort ini **bukan sampel acak** dan empat event belum cukup untuk mengklaim generalisasi.

| Simbol | Close 7 Okt 2026 | DPS | Baseline close ex-date | Ex-date | Status |
|---|---:|---:|---:|---|---|
| ASII | Rp4.780 | Rp98 | Rp4.682 | 13 Okt | Shadow, outcome belum ada |
| TLDN | Rp600 | Rp20 | Rp580 | 13 Okt | Shadow, outcome belum ada |
| AMRT | Rp1.225 | Rp14,5 | Rp1.210,5 | 14 Okt | Shadow, outcome belum ada |
| BSBK | Rp45 | Rp1 | Rp44 | 14 Okt | Shadow, outcome belum ada |

Harga dan kalender berasal dari snapshot Sectors yang diambil **8 Oktober sebelum cum**, sedangkan isi jadwal/DPS dicocokkan dengan PDF KSEI bertanggal 5–6 Oktober. `notice_document_date` adalah tanggal cetak dokumen, **bukan jam publikasi**; capture menyimpan observasi pertama yang dapat diaudit pada 8 Oktober. Rekaman dan hash tiap sumber ada di [artefak F-02f](../../outputs/forecast/shadow-captures-2026-10-08.json). Tidak ada akurasi, interval ketidakpastian, probabilitas trap, atau pemulihan yang boleh dihitung dari empat baseline tanpa outcome. Close Sectors raw/adjusted masih belum disetarakan secara independen; MCP corporate actions untuk AMRT juga belum menampilkan upcoming meski kalender REST dan KSEI cocok. Semua angka ini privat untuk riset, bukan prediksi live atau arahan transaksi.

## 14. Evaluasi pra-outcome v0.7

[Protokol F-02g](./EX_DATE_SHADOW_EVALUATION.md) membekukan metrik sebelum close ex-date kohort pertama diketahui. Untuk setiap event: `error_model = |(last_close − DPS) − close_ex| / last_close × 100%`; pembanding pada informasi cutoff sama adalah `error_flat = |last_close − close_ex| / last_close × 100%`. Report menampilkan jumlah outcome, MAE masing-masing, median galat model serta menang/seri/kalah model terhadap flat. Empat event awal hanyalah pemeriksaan pipeline; event yang kelak punya revisi atau basis harga bermasalah tetap ditunjukkan dan diberi status audit, bukan dibuang diam-diam. Nilai ini tidak mengukur return trading neto, probabilitas trap, atau interval harga. CLI tidak mengambil harga sebelum hari setelah ex-date WIB dan tidak mempromosikan angka ke API/UI. Status `forecast.status=not_available` tetap sampai audit dan review produk terpisah.

## Riwayat versi

| Versi | Tanggal | Perubahan | Bukti/status |
|---|---|---|---|
| 0.1 | 8 Oktober 2026 | Definisi target, hipotesis model harga → trap → pemulihan, data point-in-time, rancangan validasi dan batas UI. | Dokumen riset saja; ISS-024/ISS-042 tetap terbuka/ditunda. Belum ada training atau validasi prediktif. |
| 0.2 | 8 Oktober 2026 | Baseline pooled PDR ex-date, pembanding flat/full-DPS, split per tahun dan audit 44 pasangan. | 36 prediksi historis retrospektif; MAE turun dari pembanding full-DPS pada sampel pilihan, tetapi vintage/holdout bersih tidak ada. Status live tetap belum tersedia (ISS-042). |
| 0.3 | 8 Oktober 2026 | Protokol uji satu event LPPF 2026, verifikasi DPS/jadwal resmi dan perbandingan tanpa retuning. | Full-DPS lebih akurat daripada pooled pada event ini; basis harga belum diverifikasi independen. Hipotesis pooled universal ditolak untuk rilis; forecast live tetap belum tersedia. |
| 0.4 | 8 Oktober 2026 | Audit gate per event, kasus revisi LPPF 2022, dan pembanding issuer-shrunk yang dibekukan. | Hanya 3 event LPPF dengan notice cocok penuh; 1 revisi belum tuntas, 44 event lain belum diaudit resmi. Issuer-shrunk MAE 1,914% versus pooled 1,734% pada 36 event retrospektif; tetap research-only. |
| 0.5 | 8 Oktober 2026 | Skenario input pengguna dan baseline shadow sebelum cum-date dengan rekaman immutable. | API/UI skenario dan CLI capture/score diuji lokal; belum ada capture prospektif nyata, evaluasi baru, atau forecast live. |
| 0.6 | 8 Oktober 2026 | Kohort empat baseline prospektif dibekukan pra-cum; tanggal notice dipisah dari waktu publikasi dan daftar pengecualian dicatat. | Empat shadow forecast nyata dengan hash sumber; belum ada outcome, validasi akurasi, atau forecast live. |
| 0.7 | 8 Oktober 2026 | Metrik pra-outcome: galat absolut harga ex-date sebagai % close terakhir, pembanding harga flat dari cutoff sama, MAE/median/menang-seri-kalah; jalur scoring MCP setelah ex-date. | Protokol dan CLI diuji dengan fixture, kohort nyata masih 0/4 outcome; tidak ada probabilitas atau forecast live. |

Revisi berikutnya perlu menulis hipotesis yang berubah, alasan, dataset/cutoff, hasil pembanding, risiko bias, serta keputusan `diterima`, `ditolak`, atau `belum cukup bukti`. Jangan menimpa hasil eksperimen atau mengubah definisi target secara diam-diam.
