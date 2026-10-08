# Hipotesis formula prediksi dividen

Versi: **0.1 — rancangan riset**, 8 Oktober 2026. Pemilik keputusan produk: PM. Terkait C-02/C-04/C-06/C-07, S4-02, T-02, dan F-01.

Dokumen ini adalah tempat iterasi **logika finansial tim** untuk satu dividend play di saham Indonesia: rentang harga sepanjang timeline, risiko rugi setelah menerima dividen, dan waktu menuju BEP. Ini bukan model yang sudah dilatih, angka prediksi produk, rekomendasi transaksi, atau perubahan pada [protokol statistik historis v1](./INTELLIGENCE_POLICY.md). Implementasi prediksi periode berjalan masih ditunda (ISS-024/ISS-042). Setiap revisi perlu mempertahankan versi lama beserta alasan dan bukti uji.

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

## 8. Pertanyaan terbuka untuk iterasi

| Keputusan berikutnya | Bukti yang dibutuhkan |
|---|---|
| Aturan masuk/keluar dan horizon utama mana yang paling bernilai bagi pengguna? | Uji tugas pengguna + distribusi hasil replay untuk beberapa aturan **yang dibekukan lebih dulu**. |
| Apakah efek ex-date lebih stabil per emiten, sektor, atau rezim? | Sampel event bersih, perbandingan walk-forward dengan pooling, dan interval ketidakpastian. |
| Apakah data declaration dan vintage fundamental tersedia point-in-time? | Audit endpoint/dokumen dengan timestamp publikasi; tanpa itu fitur terkait tetap dikeluarkan. |
| Apa syarat minimum agar angka prediksi boleh tampil? | Kriteria ukuran/cakupan sampel, kalibrasi dan stabilitas yang diputuskan sebelum evaluasi akhir. |
| Bagaimana memodelkan tanggal event yang masih belum diumumkan? | Dataset tanggal publikasi historis dan evaluasi terpisah; **jangan menyamakan forecast jadwal dengan jadwal resmi**. |

## Riwayat versi

| Versi | Tanggal | Perubahan | Bukti/status |
|---|---|---|---|
| 0.1 | 8 Oktober 2026 | Definisi target, hipotesis model harga → trap → pemulihan, data point-in-time, rancangan validasi dan batas UI. | Dokumen riset saja; ISS-024/ISS-042 tetap terbuka/ditunda. Belum ada training atau validasi prediktif. |

Revisi berikutnya perlu menulis hipotesis yang berubah, alasan, dataset/cutoff, hasil pembanding, risiko bias, serta keputusan `diterima`, `ditolak`, atau `belum cukup bukti`. Jangan menimpa hasil eksperimen atau mengubah definisi target secara diam-diam.
