# Protokol intelligence v1 — dibekukan sebelum ekspansi hasil

Tanggal: 6 Oktober 2026. Scope C-04/C-06/C-07/C-08, turunan S4-02.

- Universe tetap sembilan emiten workspace: BBCA, BBRI, BMRI, BBNI, DMAS, LPPF, ADRO, CFIN, RALS. Ini sampel pilihan, bukan seluruh IDX; pemilihan awal terkait yield 2025 menimbulkan selection/survivorship bias.
- Semua event ex-date 2022–2025 yang ditemukan dicatat, termasuk yang tidak layak. Tidak memilih event berdasarkan return.
- MCP Sectors: corporate actions dan daily price. Kalender REST Sectors melengkapi cum/record/payment yang tidak disediakan tool MCP. Jendela maksimal 90 hari, cache immutable, provenance dan fingerprint disimpan.
- Harga diambil ex−21 hingga ex+68 hari kalender (90 tanggal inklusif). Statistik memakai sesi harga teramati, bukan kalender resmi BEI. Interval tanpa harga >7 hari kalender ditandai untuk audit; tidak otomatis dianggap suspensi karena libur panjang.
- Entry close 0/5/10 sesi sebelum cum; default 5. Horizon setelah ex 5/10/20 sesi; default 20. Ex = t0. Tidak mengoptimalkan parameter ini pada hasil.
- Konflik nilai/tanggal, OHLC tidak valid, event tanpa cum/ex/entry, split atau aksi dilutif dalam jendela, dan basis DPS/harga yang tidak konsisten dikarantina. Tidak mengisi tanggal declaration/rasio/mata uang yang tidak tersedia.
- Trap pada H berarti (close H − entry + DPS) / entry < 0, gross dan dividen berupa hak/piutang bila belum dibayar. Ini label outcome pada horizon, bukan setiap penurunan ex-date.
- Price BEP: close >= entry. Total BEP: close + DPS >= entry. Waktu hitung mulai ex. Pencapaian BEP adalah observasi harga, bukan jaminan bisa mengeksekusi di harga itu.
- Kaplan–Meier memuat event belum pulih sebagai right-censored. Median kosong bila kurva belum mencapai 50%. Pisahkan tidak pulih hingga H dari censoring dini karena data terpotong. Jangan menganggap ketidaktersediaan harga sebagai kerugian/nol.
- Proporsi trap disertai interval Wilson nominal 95%, jumlah event dan periode. Asumsi binomial independen tidak sepenuhnya berlaku pada event issuer/regime yang sama; interval adalah deskripsi dengan batas tersebut, bukan calibrated predictive interval.
- Tidak ada ambang 'model valid' otomatis. Seluruh output v1 berstatus eksploratif, model terlatih dan probabilitas out-of-sample belum tersedia. Minimum sampel untuk ranking adalah pilihan tim, bukan batas ilmiah yang membuktikan keandalan.
- Skenario forward = stress test dengan perubahan harga dari event historis emiten yang sama, entry/DPS/tanggal hipotesis dari pengguna. Angka kuantil adalah ringkasan kumpulan analog, bukan peluang masa depan. Semua analog tetap terlihat, tanpa sampling acak tersembunyi. Tidak menjadikan tanggal input sebagai jadwal terkonfirmasi Sectors.
- Ranking memakai objective eksplisit (median return, worst return, frekuensi rugi atau median BEP) dengan filter jumlah sampel dan batas risiko. Tidak membuat bobot gabungan arbitrer. Aturan, input, versi dan hasil disimpan.
- Analisis temporal 2022–2024 versus 2025 hanya diagnostik. 2025 sudah pernah dilihat saat riset dan universe dipilih belakangan; jangan menyebutnya holdout bersih, backtest point-in-time, atau validasi prediksi.
- Biaya, pajak, slippage = 0 sesuai PM. Lot100 berlaku pada simulasi nominal. Belum mengeksekusi order.

Referensi metode: [NIST Kaplan–Meier](https://itl.nist.gov/div898/handbook/apr/section2/apr215.htm), [statsmodels Wilson interval](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html). Definisi trap, universe, entry dan horizon merupakan keputusan desain riset produk, bukan angka yang ditetapkan referensi tersebut.
