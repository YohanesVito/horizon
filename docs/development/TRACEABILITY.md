# Pemetaan kebutuhan ke pekerjaan development

Tanggal: 6 Oktober 2026. Status: pemetaan sementara dari percakapan; menunggu PRD dan user story lampiran. ID `C-*` adalah referensi internal untuk kebutuhan percakapan, bukan ID resmi dokumen pengguna.

## Daftar sumber

| Sumber | Lokasi atau keterangan | Status |
|---|---|---|
| Instruksi sprint PM | Pesan chat yang meminta plan, pencatatan progres/bug/TODO, bypass dan testing akhir | Tersedia |
| Keputusan FastAPI | Pesan chat terbaru: performa belum concern dan memilih FastAPI | Disepakati |
| PRD lampiran | Path/tautan belum tersedia | Menunggu input |
| User story lampiran | Path/tautan belum tersedia | Menunggu input |
| Proposal arsitektur | [arsitektur-sistem.md](../../outputs/dividend-research/arsitektur-sistem.md) | Referensi teknis, bukan PRD final |

## Baseline percakapan

Kriteria di bawah adalah kriteria kerja sementara yang dirumuskan dari percakapan. Rekonsiliasi dengan kata-kata dan ID dokumen asli dilakukan pada S0-04.

| ID | Kebutuhan atau alur | Asal | Kriteria yang akan diperiksa | Task terkait | Status terhadap PRD |
|---|---|---|---|---|---|
| C-01 | Menemukan kandidat tanpa harus mengetahui ticker terlebih dahulu | Kebutuhan eksplorasi PM; UI discovery diusulkan assistant | Daftar kandidat bisa disaring/diurutkan, periode dan makna yield terbaca | S2-03 | Belum dipetakan |
| C-02 | Melihat timeline dividen beberapa emiten dan detail harga historis | Kebutuhan PM | Declaration/cum/ex/record/payment dibedakan; null dan revisi terlihat | S2-01, S2-02, S2-04 | Belum dipetakan |
| C-03 | Memilih serta menyimpan emiten yang ingin dipantau | Usulan watchlist dalam percakapan | Penambahan/penghapusan bekerja; jenis persistensi mengikuti PRD | S2-04 | Belum dipetakan |
| C-04 | Menyimulasikan modal dengan aturan masuk, keluar dan horizon | Kebutuhan PM | Input menghasilkan posisi, dividen, PnL gross, kas dan asumsi yang dapat ditelusuri | S1-02, S3-01, S3-02, S3-04 | Belum dipetakan |
| C-05 | Membandingkan all-in, split dan urutan rotasi | Kebutuhan PM | Modal/horizon pembanding sama; modal tertahan dan kesempatan yang terlewat ditampilkan | S3-03, S4-03 | Belum dipetakan |
| C-06 | Memahami risiko trap dan waktu pemulihan | Kebutuhan PM | BEP harga terpisah dari BEP total; event belum pulih, sampel dan batas estimasi tetap terlihat | S3-02, S4-01, S4-02, S4-03 | Belum dipetakan |
| C-07 | Menggunakan logika finansial milik tim | Kebutuhan PM | Aturan serta versi disimpan dengan input/hasil; perubahan tidak menimpa hasil lama | S2-03, S3-02, S4-02 | Belum dipetakan |
| C-08 | Menjaga sumber dan asumsi perhitungan | Arahan PM | Finansial dari Sectors, gross di luar biaya/pajak/slippage, tidak mengeksekusi order | S1-02, S2-01, S2-02, S3-01 | Belum dipetakan |

## Format pemetaan final

Saat dokumen tersedia, tambahkan tabel berikut dengan kutipan lokasi requirement yang cukup spesifik. Jangan menciptakan ID story pengguna jika dokumennya tidak memiliki ID; buat ID internal dan tandai asalnya.

| ID PRD atau story | File dan bagian sumber | Acceptance criteria | Task | Bukti implementasi | Bukti verifikasi | Issue atau bypass | Status |
|---|---|---|---|---|---|---|---|
| Menunggu dokumen | — | — | S0-03, S0-04 | — | — | ISS-001 | WAITING_INPUT |

Status final dapat membedakan belum dikerjakan, sebagian, selesai development, dibypass, serta sudah diuji. Coverage sementara tidak boleh dinyatakan sebagai persentase cakupan PRD sebelum seluruh dokumen dibaca.

## Bukti baseline yang sudah diimplementasikan

| Kebutuhan | Implementasi | Verifikasi / gap |
|---|---|---|
| C-01 | Peluang: query, sort, rules yield/frequency/replay | Browser filter10% menghasilkan5 emiten; rules persisten. Composite scoring belum ada. |
| C-02 | Kalender + detail lima tanggal dan harga | Null declaration eksplisit; kalender snapshot2025, bukan current/live. |
| C-03 | Watchlist API/SQLite | Browser tambah/hapus dan reload; tidak ada akun. |
| C-04 | FastAPI job + Decimal ledger |13 pemeriksaan backend; browser berhasil dari form ke hasil. |
| C-05 | Tiga alokasi dengan modal/horizon sama | BMRI terlewat saat rotasi; bukan optimizer rute global. |
| C-06 | Statistik BBCA, replay, serta intelligence9 emiten | Wilson, KM dan audit48 event; analog nominal gross. Forecast/probabilitas terkalibrasi belum ada. I-01/I-02/I-04; ISS-022–025. |
| C-07 | Screening + ranking objective/risiko tim, rules/input/result persisten | Prioritas median return/worst return/risiko/BEP, filter minimum sampel dan Wilson upper bound. Belum bahasa formula bebas. I-03; API/browser diuji. |
| C-08 | Sectors MCP + REST snapshots, gross, read-only |81 artifact frontend diperiksa tanpa key; tidak ada order execution. |

Tabel ini bukan rekonsiliasi PRD. Sumber dokumen asli masih dibutuhkan untuk mengukur coverage final.

Sprint intelligence memperluas baseline C-04 dengan stress test **satu posisi**, bukan menggantikan replay rotasi C-05. Rencana rotasi forward, proyeksi tanggal dan ML trap tetap gap ISS-024; kelulusan pengujian kalkulasi tidak mengisi gap tersebut.

## Integrasi rotasi R-01–R-05

| Kebutuhan | Implementasi sekarang | Batas |
|---|---|---|
| C-01/C-02/C-08 | 12 event kanonis 2025 dari sembilan emiten, ID/tanggal/DPS sama dengan Intelligence; 50 snapshot MCP harga/IHSG baru | Bukan coverage IDX penuh; empat gap IHSG diperbaiki dari konsensus feed, ISS-029 |
| C-03/C-07 | Filter emiten Peluang/Watchlist → planner; salinan aturan Intelligence → cutoff sebelum keputusan | Pemilihan universe manual dapat tetap bias; bukan formula bebas |
| C-04/C-05 | 1–3 rute sebelum replay, lalu tiga alokasi tiap rute + baseline cash pada modal/periode sama | Heuristik, bukan optimum global; jadwal mendatang dalam replay masih asumsi |
| C-06 | Drawdown, lot terbuka/di bawah entry, durasi modal, missed events, ledger dengan dividen berulang | Statistik masa lalu, bukan trained probability atau forecast waktu pulih |
| C-07/C-08 | Rencana frozen, evidence IDs/cutoff/reasons, fingerprint, job hasil terpisah, riwayat tersimpan | SQLite/local worker; declaration timestamp dan snapshot point-in-time belum tersedia |

[PM_REVIEW.md](./PM_REVIEW.md) mengusulkan alur diskusi serta calon acceptance checks. R-05 tidak menutup S5-03/S6 atau menyatakan PRD/UAT sudah selesai.

U-01 menambah bukti C-04/C-07/C-08: hasil manual menampilkan snapshot aturan/event/versi, form dibedakan dari hasil, dan salinan input menjadi run baru. U-02 menyediakan [UAT_SESSION.md](./UAT_SESSION.md); penilaian pemahaman pengguna serta coverage PRD belum dinyatakan lulus.

## Timeline T-03–T-05

C-02/C-06/C-08: menu Timeline dengan overlay lima periode satu emiten, fokus hover/klik/keyboard, hargaRp/perubahan%, fase dividen per tahun dan lapisan aktual2026dengan placeholder prediksi. API memisahkan katalog histori lengkap dari pratinjau riset LPPF.46tesbackend,build/lint/typecheck,API dan browser diperiksa; lihat [TIMELINE_IMPLEMENTATION.md](./TIMELINE_IMPLEMENTATION.md). Dataset lengkap masih gap ISS-041; engine prediksi ditunda oleh PM pada ISS-042. Bukan klaim coverage PRD final atau UAT lulus.

## Fokus demo D-01

Instruksi PM 7 Oktober memprioritaskan satu alur: analisis emiten (histori dan periode berjalan) lalu simulator. D-01 mengubah pintu masuk dan navigasi demo, bukan menghapus C-01/C-03/C-05 atau implementasinya. Pratinjau LPPF tetap berlabel belum terverifikasi (ISS-041); simulator satu-emiten belum terhubung dan masih perlu pekerjaan terpisah (ISS-046). Sumber/metodologi tersedia sebagai tautan sekunder.

D-02 menggabungkan arah demo dari PM (D-01, perubahan lokal pada branch UI) dengan implementasi Sammy pada `feat/chart-sammy` (UX-01–UX-04: input modal, pilihan strategi, klik chart, dan copy/istilah). `dashboard.tsx` diselaraskan manual agar pemangkasan copy/sidebar Sammy tidak mengembalikan delapan menu atau landing Peluang. Ini sinkronisasi kontribusi, bukan bukti bahwa simulator satu-emiten, data lengkap, atau forecast sudah selesai.
