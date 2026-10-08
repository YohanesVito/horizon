# AI-02 — Pola hasil simulasi dan riset IDX adaptif

Instruksi PM8Oktober2026: tampilkan penjelasan compact di atas **JEJAK TRANSAKSI**; pisahkan riset agentic dari penulisan hasil, izinkan kemampuan Sectors IDX, batasi retry ketika gagal. OpenAI memakai `gpt-6-luna` dari helper server `backend.ai`; key tetap server-only `AI_KEY` dan `SECTORS_API_KEY`.

## Endpoint dan guard biaya

`POST /api/simulations/{job_id}/insights` menerima `{"allocation":"equal"}` (single/rotation kompatibel). Data selalu dari run selesai tersimpan; analisis canonical memakai strategi primary dan ringkasan alternatif. Mengganti tab/alokasi, histori, model atau versi kode tidak menghasilkan analisis baru setelah success. Run unknown/different-kind404; belum selesai409; strategi tidak tersedia/field tambahan422.

Respons200: `status` processing/completed/unavailable, `summary`, maksimal empat `findings` (title/detail/source_ids), `sources`, `limitations`, `statistics`, provenance, serta metadata research/attempts/exhausted pada record baru. Frontend membaca per ID run. Replay tetap terbaca saat AI memproses. Processing dapat diperiksa dengan guarded POST, bukan membuka generation baru. Setelah tiga failure, exhausted=true dan summary/findings kosong; section AI disembunyikan.

Record `ai-run:{run_id}` diklaim atomik `INSERT ... ON CONFLICT DO NOTHING` pada PostgreSQL/SQLite sebelum model/provider dipanggil. Counter durable mengizinkan maksimal **tiga attempt final total**, retry hanya ketika gagal (pertama + maksimal dua retry). CAS klaim retry dan CAS completion menolak race/hasil attempt lama. Concurrent request menerima processing/cache; tidak membuka owner kedua. Success dipertahankan permanen. Restart tidak mereset budget: pending orphan ditutup melalui worker lease PostgreSQL atau expiry100detik; sisa counter tetap maksimal tiga. Legacy success diprioritaskan yang cocok primary, fallback earliest cached answer dengan provenance asli dan tanpa panggilan AI baru.

`AI_KEY` belum dikonfigurasi diperiksa sebelum klaim/model: configured=false, attempts=0, exhausted=false. Tidak ada budget yang digunakan; setelah key disetel, request ID yang sama dapat berjalan. Hasil success tersimpan tetap dapat dibaca tanpa key.

## Riset terpisah dan adaptif

`backend/ai_research.py` menyimpan evidence `ai-research:{run_id}` sekali. Model mendapat angka otoritatif, katalog schema **32tool IDX**, allowed ticker, jendela historis+replay, dan memilih tool/argumen. Ronde kedua membaca hasil/rejection/gap ronde pertama lalu memilih pencarian lanjutan; bukan daftar news/index yang selalu dipanggil. Gateway read-only `backend/sectors_tools.py` memvalidasi schema asli, simbol, tanggal, pagination, sections/quarter limits dan kredit sebelum MCP.

Katalog dikemas di `backend/data/sectors_idx_tools.json`, dari registry MCP yang diverifikasi7Oktober2026; Docker COPY backend membawa file ini. Tool mencakup prices/indices/foreign flows, broker/shareholders/insider, corporate actions, news/filings, financial periods/segments, company/subsector/peer reports dan helper/reference/screener IDX. Katalog SGX/KLSE tidak dimasukkan; extension mining ditolak. Tidak ada URL/arbitrary HTTP tool atau user-supplied tool schema. Tool current snapshot berlabel saat ini dan tidak boleh diklaim menjelaskan kondisi yang diketahui pada kejadian lama; tool tanpa kemampuan as-of dapat dibatasi gateway. Allowed catalog bukan janji setiap tool diperlukan/dipanggil.

Batas satu run: **dua panggilan model planning**, maksimal tiga dispatch per ronde/**enam total**, maksimal **12credit Sectors**, keseluruhan riset40detik. Setelah riset, maksimal tiga panggilan model final20detik masing-masing: maksimal **lima OpenAI calls** total/run dan nominal≤100detik/request; proxy khusus endpoint120detik. Counter tiga attempt berlaku tahap final, tahap riset terpisah dan tidak diulang. Evidence/dispatch disimpan sebelum MCP, hasil/gap setelahnya. Riset terhenti memakai bukti parsial tanpa mengulang query berbayar; failure final memakai evidence yang sama. Tidak ada penelitian baru untuk run success lama.

Sumber mempunyai ID server, tool/query/retrieved_at, URL provider/dokumentasi terpercaya, excerpt terbatas dan tanda truncation/temporal scope. News aggregate menunjuk query Sectors, bukan menyamakan semua artikel dengan URL artikel pertama. Konten provider/payload adalah data tidak tepercaya, tidak boleh diikuti sebagai instruksi. ID sumber rekaan membuat final attempt gagal. Schema/ID validation tidak membuktikan otomatis seluruh narasi model atau kausalitas.

## Statistik dan batas kesimpulan

Kode menghitung maximum decline dari cum close pada21close tersedia pertama sejak ex-date, per emiten/event. Nilai kosong/jendela kurang21close dikeluarkan, tidak diisi nol. Event tidak otomatis satu sampel tahunan. Kelompok cycle_key diketahui dipisah; tanpa identitas siklus memiliki distribusi deskriptif pratinjau berlabel, bukan annual comparable risk estimate. Mean/median/maksimum/mean-without-one-maximum dihitung kode; outlier deskriptif memakai pagar Tukey `Q3+1.5×IQR`, kuartil inclusive, minimal lima event. Maksimum tidak otomatis outlier; mean<median tidak mendukung cerita satu kejadian yang menaikkan rata-rata.

Basis split, kelengkapan sesi, siklus dan arsip lama belum seluruhnya terverifikasi. Fundamental report_date adalah akhir periode, bukan publication/vintage timestamp: nilai historis dapat menjadi konteks retrospektif, bukan bukti informasi tersedia saat kejadian. Current reports tidak memiliki historical vintage. Riset berbatas tool/kredit/waktu; gap tetap dinyatakan, tidak memaksa cerita penyebab. Ini deskripsi replay di luar biaya/pajak/slippage, bukan prediction/causal inference/decision-time backtest/rekomendasi order.

## Bukti development

- Fixture24/1/2/1/2 →mean6%, median2%, mean-without-max1,5%, upper outliertrue; 2/15/18/20/22 bukan outlier. Missing histories/cycle/sample tidak ditutupi.
- Guard: fail/fail/success→tiga final calls; failed3/repeated request tetap tiga;20claim awal dan20retry CAS dari sesi DB independen masing-masing satu owner; late completion ditolak; key absent nol attempt dan recover setelah konfigurasi.
- Adaptive fixture: ronde pertama corporate action, ronde kedua quarterly finance setelah membaca sumber pertama; researched evidence direuse; dua planning + tiga final fail/fail/success tepat lima model calls.
- Smoke live freshrun `f272006d-7a93-496f-b27a-c12245763c36`, SQLite lokal8001: **200 completed37,721detik**, final attempt1. **Dua planning**, enam dispatch, **empat actual MCP calls/four credits**, tiga sumber. Model memilih corporate action/daily price/news pada ronde pertama; setelah membaca hasil/gap, memilih daily price historis/news keyword/IHSG pada ronde kedua. Provider news kosong dan dua request ditolak guard; tidak dipresentasikan sebagai berita/penyebab terbukti. Request kedua berbeda alokasi menghasilkan respons identik tanpa generation baru. [ai-insight-agentic-live.json](../../outputs/development/ai-insight-agentic-live.json) menyimpan hasil dan audit riset tersanitasi.
- Smoke tersebut menemukan window yang belum memasukkan akhir replay20Mei2025 dan link IHSG lama. Keduanya diperbaiki lewat regression deterministik: window mencakup replay start/end sehingga query21April–20Mei diterima, dan source memakai API resmi /v2/index-daily/{code}/ dengan query tanggal. Cached success live tetap dipertahankan; tidak digenerate ulang untuk menutupi hasil sebelum perbaikan.
- Bukti guard raw10POST concurrent run legacy: [ai-insight-once-guard.json](../../outputs/development/ai-insight-once-guard.json). Bukti UI/live awal: [ai-insight-live.json](../../outputs/development/ai-insight-live.json).

Pemeriksaan akhir: 115tes backend lulus; git diff --check bersih. Pemeriksaan development bukan UAT/deployment. Listener pengguna8000/3000, Supabase dan environment production tidak diubah.

Integrasi main BR-08: source AI digabungkan dengan origin/main725d9c4 tanpa mengganti engine/scenario/shadow ex-date atau UI polish incoming.138tes backend gabungan serta lint/build/typecheck lulus; independen review lulus. ID gap kualitas AI sekarang ISS-068 (ISS-060 dipertahankan untuk performa). Preview terbaru lokal3001→8001; deployment production sebelumnya tidak otomatis memperoleh endpoint BE hanya dengan push frontend/main.
