# Panduan teknis Horizon

Dokumen ini melengkapi [README produk](../README.md). Peta berikut mengikuti source `8a8b5a6`, 8 Oktober 2026. Navigasi utama demo adalah **Analisis** dan **Simulasi**; keberadaan modul/API tidak berarti semua fiturnya tersedia sebagai menu demo.

## Peta implementasi

| Area | Implementasi | Batas akses/status |
|---|---|---|
| Analisis | [Timeline](../backend/timeline.py), [kandidat](../backend/discovery.py), dan [UI](../src/components/dividend-timeline.tsx) | Lima kandidat DMAS, LPPF, ADRO, CFIN, RALS; histori pratinjau. Tab 2026 pada snapshot ini hanya tersedia untuk LPPF. |
| Simulasi | [Engine](../backend/simulator.py), [dataset terpadu](../backend/unified.py), dan [UI](../src/components/simulator.tsx) | Replay 12 event 2025, maksimal 10 event dalam satu permintaan; tiga alokasi. |
| Penjelasan AI | [Statistik dan hasil](../backend/insights.py), [riset](../backend/ai_research.py), [gateway MCP](../backend/sectors_tools.py) | Opsional dengan key server; tanpa key, replay tetap berfungsi. Tidak menghitung angka portofolio atau membuktikan penyebab perubahan pasar. |
| Ranking dan statistik | [Intelligence](../backend/intelligence.py), [aturan](../backend/domain.py) | API tersedia. UI Intelligence bukan menu utama; aturan terstruktur, belum editor formula bebas. |
| Planner rute | [Planner](../backend/planner.py) | API tersedia. Tiga heuristik rute, bukan optimum global; UI bukan menu utama. |
| Skenario analog | [Scenario](../backend/intelligence.py) | API tersedia; analog satu posisi, bukan distribusi probabilitas masa depan yang terkalibrasi. |
| Riset ex-date | [Protokol verifikasi](development/EX_DATE_VERIFICATION_PROTOCOL.md), [formula](development/PREDICTION_FORMULA.md) | Diagnostik dan eksperimen terpisah. Tidak menjadikan forecast publik tervalidasi. |

## Logika keuangan yang dijalankan

- Engine menggunakan `Decimal`, lot 100 saham, dan tidak memakai margin. Sisa kas yang tidak cukup untuk satu lot tetap menjadi kas.
- Hak dividen dibukukan pada ex-date untuk posisi yang memenuhi kepemilikan; piutang baru menjadi kas pada payment date. Menjual sebelum payment tidak menghapus hak yang sudah diperoleh.
- Hasil jual menjadi kas tersedia setelah T+2 sesi dataset. Uang yang belum tersedia tidak dapat dibelanjakan untuk event berikutnya.
- Nilai portofolio adalah kas, nilai posisi terbuka, piutang hasil jual, dan piutang dividen. Perpindahan antar-komponen tidak menciptakan keuntungan tambahan.
- Entry terjadwal memakai close. Sinyal BEP harga memakai close terhadap harga beli, lalu dijual pada open berikutnya dalam batas replay. Gap turun dapat membuat hasil jual di bawah BEP.
- Batas holding memakai sesi setelah ex-date. Waktu modal tertahan yang ditampilkan memakai hari kalender sampai settlement atau akhir pengamatan. Posisi yang belum dijual pada akhir replay tetap dinilai dengan harga terakhir.
- Run menyimpan input, aturan, versi engine, fingerprint dataset, hasil, dan ledger. Mengubah aturan tidak menulis ulang hasil lama.
- Biaya transaksi, pajak, dan slippage dikecualikan sesuai scope MVP. Hasil selalu dibaca sebagai gross.

### Statistik dan financial logic

Intelligence memisahkan BEP harga dan BEP total. Frekuensi hasil negatif dilengkapi interval Wilson 95%; waktu pemulihan memakai Kaplan–Meier agar pengamatan yang berakhir sebelum pulih tetap diperhitungkan sebagai tersensor. Keduanya bersifat eksploratif dan mempunyai asumsi yang dijelaskan dalam [kebijakan intelligence](development/INTELLIGENCE_POLICY.md).

Ranking menerima minimum sampel, batas atas interval risiko, minimum median return, dan objective return/worst return/risiko/pemulihan. Setiap pengecualian membawa alasan. Planner memotong statistik sebelum awal periode dan membekukan rute sebelum replay. Tes mengubah harga masa depan untuk memastikan ranking/rute tidak ikut berubah; jadwal yang belum memiliki timestamp pengumuman tetap asumsi, sehingga keseluruhan replay belum bebas bias informasi historis.

## Data Sectors dan reproduksi

Snapshot finansial tersimpan di repository; Supabase/SQLite menyimpan record aplikasi. Menjalankan replay tidak memerlukan pengambilan data baru.

| Dataset | Isi | Lokasi |
|---|---|---|
| Intelligence | 74 respons sumber: 9 aksi korporasi, 17 kalender, 48 jendela harga | [Raw](../outputs/intelligence/raw/), [audit event](../outputs/intelligence/event-audit.csv), [baseline](../outputs/intelligence/baseline-analysis.json) |
| Replay terpadu | 12 event 2025 pada sembilan emiten; 45 respons harga emiten dan 5 IHSG | [Raw rotasi](../outputs/rotation/raw/) |
| Riset awal dan timeline | Respons, provenance, dan studi pendukung | [Riset](../outputs/dividend-research/), [snapshot](../outputs/sectors-live/), [data MVP](../outputs/mvp-sectors/) |

Harga dan aksi korporasi dikumpulkan melalui **Sectors MCP**. Kalender menggunakan REST resmi Sectors karena endpoint kalender yang dibutuhkan tidak tersedia pada registry MCP yang diaudit. Metadata sumber mencatat tool/endpoint, argumen, waktu pengambilan, dan fingerprint; hasil audit mempertahankan event yang dikeluarkan beserta alasannya.

Empat gap IHSG pada 2, 6, 7 Mei dan 20 Oktober 2025 dilengkapi menggunakan tanggal dengan OHLCV valid pada seluruh sembilan feed emiten. Perbaikan dicatat pada `session_repairs`; kalender settlement resmi tetap perlu verifikasi. Histori dengan konflik jadwal atau basis split yang belum setara tidak boleh dianggap valid tanpa audit.

Perintah berikut **opsional**, hanya untuk melengkapi cache dengan kredensial Sectors server. Kolektor memakai cache; jangan menjalankannya hanya untuk mencoba aplikasi atau memperbarui snapshot lama secara diam-diam.

```sh
.venv/bin/python work/collect_mvp_data.py
.venv/bin/python work/collect_intelligence.py actions
.venv/bin/python work/collect_intelligence.py calendar
.venv/bin/python work/collect_intelligence.py prices
.venv/bin/python work/build_intelligence.py
.venv/bin/python work/collect_rotation.py
```

Restart backend setelah dataset diubah. Rencana rotasi dengan fingerprint lama harus dibuat ulang; hasil historis yang sudah tersimpan tetap memiliki versi aslinya.

## API dan penyimpanan

Kontrak interaktif tersedia pada `/docs` backend lokal. Untuk backend yang memakai proteksi key, dokumentasi dan endpoint data juga memerlukan otorisasi.

| Kebutuhan | Endpoint utama |
|---|---|
| Kesehatan, katalog, kandidat | `GET /api/health`, `/api/catalog`, `/api/dividend-candidates` |
| Timeline | `GET /api/timeline`, `/api/timeline/{symbol}?preview=true` |
| Simulasi dan riwayat | `POST/GET /api/simulations`, `GET /api/simulations/{id}` |
| Penjelasan AI | `POST /api/simulations/{id}/insights` |
| Intelligence | `GET /api/intelligence`, `PUT /api/intelligence/rules` |
| Skenario analog | `POST/GET /api/scenarios` |
| Rencana rotasi | `POST/GET /api/rotation-plans`, `GET /api/rotation-plans/{id}` |
| Replay rute | `POST /api/rotation-plans/{id}/replay`, `GET /api/rotation-runs`, `GET /api/rotation-runs/{id}` |

FastAPI menjalankan engine dan background job. Database menyimpan settings, rencana, run, dan hasil dalam record JSON. SQLite digunakan untuk lokal; PostgreSQL Supabase memakai schema privat, migrasi berversi, dan role terbatas. Worker masih berbasis thread, dengan satu backend aktif per database cloud. Restart menandai job yang terputus sebagai gagal; belum memakai durable queue.

## Konfigurasi dan operasi

Contoh variabel tersedia di [`.env.local.example`](../.env.local.example). Backend membaca `.env.local` dengan prioritas environment proses. Jangan menimpa file yang sudah berisi kredensial.

| Variabel | Fungsi |
|---|---|
| `BACKEND_URL` | Tujuan proxy server Next.js. Default lokal `http://127.0.0.1:8000`. |
| `DATABASE_URL` | SQLite lokal atau PostgreSQL untuk record aplikasi. |
| `HORIZON_API_KEY` | Key antarlayanan; nilainya sama di Next.js dan FastAPI. Bukan akun pengguna. |
| `HORIZON_REQUIRE_API_KEY` | Set `1` pada deployment FastAPI untuk mewajibkan konfigurasi key. |
| `SECTORS_API_KEY` | Pengumpulan snapshot dan riset konteks MCP. |
| `AI_KEY` | Penjelasan AI melalui OpenAI; lihat [setup helper](development/AI_HELPER.md). |

Semua key tetap di server. Untuk AI aktif, jangan gunakan override `AI_KEY='' SECTORS_API_KEY=''` dari quick start tanpa-key. Atur key pada environment backend sendiri, lalu restart. Model dan hak akses akun perlu tersedia; keberadaan key tidak menjamin semua sumber konteks tersedia.

Riset AI dibatasi dua ronde, enam dispatch tool, dan 12 kredit Sectors per run. Hasil sukses dipakai kembali; tahap penulisan final dibatasi tiga percobaan total per ID run. Klaim dan hasil tersimpan atomik. Validasi schema serta ID sumber tidak membuktikan semua narasi AI benar atau hubungan kausal pasar. [Kontrak lengkap](development/AI_INSIGHTS.md).

Untuk frontend remote, gunakan backend HTTPS dan key antarlayanan. Jangan menjalankan preview tambahan pada database produksi. [Deployment backend](development/DEPLOYMENT_DALANG.md), [deployment frontend](development/DEPLOYMENT_VERCEL.md), dan [migrasi Supabase](development/SUPABASE_MIGRATION.md) memuat prosedur operasional; catatan deployment lama bukan konfirmasi kesehatan saat ini.

Jika Python sistem gagal membuat virtualenv karena `pyexpat`/`libexpat`, alternatif yang pernah digunakan adalah Python 3.12 melalui `uv`:

```sh
uv python install 3.12
uv venv --python 3.12 .runtime/ui-feedback-venv
uv pip install --python .runtime/ui-feedback-venv/bin/python -r backend/requirements.lock
```

Gunakan interpreter itu sebagai pengganti `.venv/bin/python` pada quick start. Untuk pengembangan frontend, `bun run dev` memakai webpack polling. `bun run start:lan` membuka frontend ke jaringan lokal; semua pengunjung tetap berbagi settings/riwayat karena akun terpisah belum tersedia.

## Bukti pemeriksaan

Tes yang relevan untuk reviewer:

- [Simulator](../backend/tests/test_simulator.py): hak dividen, settlement, konservasi nilai, lot, dan risiko gap saat sinyal BEP.
- [Rotasi](../backend/tests/test_rotation.py): beberapa lot, dividen berulang, kas tersedia, dan isolasi harga masa depan.
- [Intelligence](../backend/tests/test_intelligence.py): Wilson, censoring, validasi data, dan filter ranking.
- [API](../backend/tests/test_api.py): input → job → hasil → riwayat pada database sementara.
- [AI](../backend/tests/test_insights.py) dan [tools MCP](../backend/tests/test_sectors_tools.py): cache, klaim atomik, retry, dan batas query.

`work/verify_mvp.py` tersedia untuk matriks pemeriksaan akuntansi tambahan tanpa provider; ia menulis laporan ke `outputs/development/mvp-readiness.json`. Hasil pemeriksaan terdahulu disimpan sebagai bukti historis. Jangan menyamakan jumlah tes yang lulus dengan akurasi prediksi atau kelulusan UAT.
