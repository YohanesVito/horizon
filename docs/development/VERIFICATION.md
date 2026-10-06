# Pemeriksaan development — 6 Oktober 2026

Status: kandidat lokal berdasarkan percakapan, **bukan testing akhir/UAT dan bukan bukti profitabilitas strategi**. PRD/user story lampiran belum diterima. Tidak ada deployment publik.

## Hasil pemeriksaan

| Pemeriksaan | Hasil aktual | Batas |
|---|---|---|
| `pytest backend/tests -q` | **13 passed**, satu warning deprecation Starlette/httpx | Fixture keuangan, snapshot Sectors nyata, API/database sementara. Bukan validasi model pasar. |
| `bun run lint` | Lulus tanpa error/warning | ESLint Next/TypeScript |
| `bun run typecheck` | Lulus | TypeScript strict |
| `bun run build` | Lulus dengan webpack; route `/` diprerender | Build terakhir setelah perbaikan form, navigasi dan mobile history |
| Frontend HTTP + proxy | Halaman3000 dan `/api/catalog` HTTP200 | Backend8000 bind localhost |
| Scan credential frontend | Key Sectors tidak ditemukan pada81 file `.next/static` | Key dibaca hanya untuk pemeriksaan dalam proses; nilainya tidak dicetak |
| Browser desktop | Discovery, kalender, detail, watchlist, rules, simulator, pembanding dan ledger berhasil | In-app browser desktop1280px; bukan matriks semua browser |
| Browser mobile | Lebar DOM390px sama dengan scrollWidth390px; nav/rute terbaca, history tetap terlihat | Satu breakpoint390×844; bukan seluruh perangkat |
| Browser log | Tidak ada console error/warn pada pengamatan final | Tidak menjamin seluruh state bebas bug |

## Bukti alur pengguna

1. **Watchlist:** tambah BBCA dari Peluang → Watchlist menampilkan BBCA → reload dan restart server tetap tersimpan → hapus BBCA berhasil. Data uji watchlist dikembalikan kosong.
2. **Logika screening:** minimum yield10% →5 emiten tampil → simpan → reload tetap5 → kembalikan minimum0. Aturan yang disimpan menjadi snapshot pada run baru.
3. **Pencarian:** `ZZZZ` menghasilkan empty state yang menjelaskan tindakan berikutnya. Pencarian dikosongkan setelah uji.
4. **Detail BBCA:** modal menampilkan harga aktual, lima tahap tanggal, declaration kosong, delapan event studi; BEP harga/total dan event belum pulih dipisahkan. Event Desember2025 tidak lagi eligible replay Maret–Mei.
5. **Kalender:** April2025 menampilkan42 ex-date dalam snapshot. Ticker tanpa laporan/detail dimuat ditampilkan pasif; bukan tombol detail yang pura-pura berfungsi.
6. **Simulasi:** tiga event default → POST202 → run completed → grafik tiga strategi, metrik, posisi, settlement, dividen dan ledger. Pemilihan Bagi rata mengganti nilai dan jejak posisi sesuai hasil backend.
7. **Input invalid:** horizon21 Maret dengan event April menghasilkan error eksplisit. Diperbaiki menjadi20 Mei → run completed. Perbaikan ini menutup ISS-019, yaitu nilai field tanggal yang awalnya belum masuk state submission.
8. **Mobile:** form, hasil dan kartu rute terbaca; tabel memiliki scroll lokal; tidak ada overflow dokumen. Riwayat run tidak disembunyikan. Viewport dikembalikan ke ukuran awal setelah pemeriksaan.

Run browser final yang berhasil: `8f5def9c` (prefix ID); engine `replay-v1.1`; dataset `sectors-5b885fb8a3dea1f4`. Run gagal yang disengaja dan contoh historis tetap terlihat di riwayat untuk audit; bukan kegagalan tersembunyi. Run lama `replay-v1` tidak diubah menjadi v1.1.

Modal Rp100.000.000, entry5 sesi sebelum cum, aturan BEP dengan batas20 sesi, horizon20 Mei2025:

| Strategi | NAV akhir | Return gross | Maximum drawdown |
|---|---:|---:|---:|
| All-in event pertama | Rp101.110.000 | 1,1100% | −10,5450% |
| Bagi rata | Rp108.743.577,6 | 8,7436% | −6,5870% |
| Rotasi kas | Rp101.440.000 | 1,4400% | −10,5450% |

Nilai di atas replay historis dan mencakup posisi terbuka/piutang; bukan keuntungan kas seluruhnya, forecast, atau rekomendasi. Biaya/pajak/slippage nol. Periode, saham dan kalender dipilih untuk pilot; tidak ada klaim bebas selection bias atau look-ahead.

## Artifact

- [API smoke evidence](../../outputs/development/api-smoke.json)
- [Dashboard desktop](../../outputs/development/dashboard-desktop.jpg)
- [Dashboard mobile](../../outputs/development/dashboard-mobile.jpg)
- [Simulator desktop](../../outputs/development/simulator-desktop.jpg)
- [Unit/API/data tests](../../backend/tests/)
- [Issue dan bypass](./ISSUES.md)

Screenshot full-page browser dapat melewatkan painting panel glass yang berada jauh di luar viewport. Kartu rute mobile diperiksa lagi pada viewport nyata dan tampil. Screenshot dashboard yang disimpan menggunakan capture viewport.

## Belum diverifikasi / belum selesai

Prediksi tanggal/harga/trap, kalibrasi model, optimasi rute global, point-in-time lapkeu, kalender resmi settlement, full corporate-action adjustment, PostgreSQL/Redis/RQ, multi-user/auth, deployment dan UAT. Dev polling disiapkan setelah EMFILE, tetapi pemeriksaan browser memakai production build/start yang telah berhasil.

Bukti lint/build/smoke tidak mengubah status gap tersebut. Detail kriteria testing akhir akan dibahas dengan PM.

## Perluasan intelligence — 6 Oktober 2026

Pemeriksaan development, bukan UAT atau validasi model.

| Pemeriksaan | Hasil aktual |
|---|---|
| Koleksi Sectors |74 snapshot:9 corporate actions MCP,48 harga MCP,17 kalender REST; registry66 tools terverifikasi. Batch harga awal429, retry/cache pulih48/48. |
| Audit default |48 event,44 layak,43 lengkap,4 quarantine split,1 censored dini sebelum dividen berikutnya. Dataset `intelligence-8a6d340ad419b922`. |
| Backend |22 pytest lulus:13 regresi lama +9 uji intelligence. API test diperluas dengan rules persisten, empty ranking, skenario, chronology422, piutang, hasil lama tetap setelah rule berubah. Satu warning Starlette/httpx tetap ada. |
| Matematis |Wilson nol/semua rugi tidak memberi kepastian palsu; KM ties memasukkan censor ke risk set, null median/tail tanpa observasi; BEP harga/total terpisah; data terpotong tidak dihitung sebagai loss/success; dividen kedua menghentikan cohort; analog masa depan dikeluarkan; lot dan piutang tidak dihitung ganda. |
| Frontend |Build produksi dan TypeScript lulus; lint lulus. Build diulang setelah perbaikan warna sumbu, berhasil. |
| Rules browser |Minimum100 →0 lolos dan9 alasan; setelah reload tetap0. Minimum3 dan t5 →44 lengkap; kembali t20 →43 lengkap. Default akhir dipulihkan: entry5, horizon20, minimum3, upper risk100, minimum median−100, objective median return. |
| Alur detail |Buka detail BMRI→Buka Intelligence BMRI menampilkan pilihanBMRI,2 event valid dan2 karantina; alasan basis split terlihat per event. |
| Skenario browser |Payment1 Okt2026 ditolak karena sebelum ex/recording; mengubah10 Des2026 menghasilkan8 analog BBCA. Modal100 juta/entry10.000/DPS250, valuation8 Des: piutang2,5 juta, kas dividen0, medianPnL−247.419,3019826287. Input hipotetis, bukan harga/jadwal terkonfirmasi. |
| Persistence |Skenario BBCA tersedia kembali setelah reload dan restart frontend; memilih riwayat membuka hasil/kurva dengan input aslinya. |
| Responsif |Desktop1280: clientWidth=scrollWidth=1280. Mobile390: clientWidth=scrollWidth=390 pada overview dan hasil/kurva skenario. Tabel tetap dapat digulir di dalam panel. Override viewport dikembalikan ke normal. |
| Browser errors |Setelah reload build akhir, log error browser kosong. Validasi422 sebelumnya merupakan kasus uji yang diharapkan. |
| Rahasia |81 artifact `.next/static` diperiksa setelah build; literal API key tidak ditemukan. Key tidak dicetak. |

Artifact tambahan:

- [Intelligence desktop](../../outputs/development/intelligence-desktop.jpg)
- [Intelligence mobile](../../outputs/development/intelligence-mobile.jpg)
- [Skenario dan kurva mobile](../../outputs/development/intelligence-scenario-mobile.jpg)
- [Bukti API/rules/skenario](../../outputs/development/intelligence-api.json)
- [Audit48 event CSV](../../outputs/intelligence/event-audit.csv)
- [Baseline JSON lengkap](../../outputs/intelligence/baseline-analysis.json)
- [Protokol dan batas metode](./INTELLIGENCE_POLICY.md)

Sisa scope: forecast/kalibrasi model, financials point-in-time, normalisasi split/currency, jadwal future terkonfirmasi, forward rotation optimizer, kalender resmi, PRD mapping, infrastruktur final dan UAT. Skenario analog hanya satu posisi; replay rotasi tetap cohort Maret–Mei2025. Tidak menyatakan MVP memenuhi PRD yang belum tersedia.


## Verifikasi integrasi rotasi — 6 Oktober 2026

Story: pengguna membawa emiten/rules ke planner → FastAPI menghitung bukti sebelum keputusan dari snapshot Sectors → menyimpan rencana → worker mereplay tiap rute dengan tiga alokasi → browser menampilkan hasil/ledger dan riwayat.

| Batas yang diperiksa | Hasil | Bukti |
|---|---|---|
| Sectors MCP → raw | PASS |50/50 respons baru tanpa kegagalan; collection.json,45harga+5IHSG. Provider dipanggil melalui adapter MCP server-side, bukan dari browser. |
| Raw → dataset | PASS dengan bypass |12IDevent2025 sama dengan Intelligence; tidak ada konflik OHLC overlap;4gapIHSG dikoreksi dari9feedvalid, metadata session_repairs. Kalender resmi tetap gap. |
| Statistik → kandidat | PASS |Cutoff bar sebelum keputusan; unfinished event censored; ubah futureprices7× tidak mengubah rute/ranking; verified-only kosong dengan alasan. |
| Plan → worker/ledger | PASS |32pytest total (test_rotation9 dan test_rotation_api1 menambah22baseline): beberapa lot/hak berulang, hak event tak dipilih, cap payment sebelumcash, missingbar reject, konservasi NAV, period/capital sama, frozenrules dan staleversion409. |
| UI → API → hasil | PASS |Browser submit201 plan→202 job→200completed; default3rute×3alokasi,6lolos/3ditolak. API proxy3000 disimpan di rotation-api.json. |
| Bridge emiten/rules | PASS |SearchBBCA pada Peluang→planner1emiten; Intelligence→planner9emiten dengan financiallogic tersimpan. |
| Input dan empty state | PASS setelah fix |Rp50juta/akhir15Juni+ubahcheckbox → snapshot tetap15Juni; verified-only0rute/alasanterlihat; tombolreplaydisabled. ISS-033. |
| Persistence/history | PASS setelah fix |Reload → buka run55146461 → hasilidentik. Replayulang9fb6a42c tampilcompleted di daftar; pollinghistory mengikuti statuslist. ISS-034. |
| Build/quality | PASS |bun lint, TypeScript, next build --webpack.32pytest lulus; satu warning Starlette/httpx tetap ISS-016. |
| Visual | PASS |Desktop1280×900 danmobile390×844; halamanmobileclientWidth390/scrollWidth390. Tabel lebar memakai scroll internal. Screenshotrotation-desktop.jpg/rotation-mobile.jpg. Console warn/error kosong pada alurfinal. |

Artefak di outputs/development. Default snapshot unified-b749e08ddb769800; planner-v1.0/replay-v2.0. NAV tetap memisahkan kas/posisi/piutang; PnL di luar biaya transaksi, pajak, slippage. Uji developer bukan UAT atau validasi prediksi/market proof. Review berikutnya tersedia di PM_REVIEW.md.

Pemeriksaan handoff:10 dokumen mempunyai seluruh tautan lokal valid;81 asset frontend diperiksa terhadap key server tanpa menemukan kebocoran. Override viewport direset dan tab hasil tetap dibuka.


## Pemeriksaan kesiapan Q-01–Q-03

- **Backend:**40pytest lulus dalam0,58detik; mencakup3kaspecahan, akhir tahun, kasT+2dipakai pada entryhariyangsama, prioritasentryserentak, failed→retry, restartinterruptedjobs, kontrakIDlintasendpoint. Warning Starlette/httpx tetap ISS-016.
- **Matriks data nyata:** work/verify_mvp.py →1.620replay,0failures; datasetunified-b749e08ddb769800,enginereplay-v2.1. Ini accounting check; bukan bukti profitabilitas atau validasi holdout.
- **Frontend:** ESLint/TypeScript/build webpack lulus setelah seluruh perbaikan. Tidak menambahkan UI library atau mengubah tema.
- **Browser:** detailADRO menampilkan tombol event13Jun dan30Des berbeda. Klik30Des hanya memilih ADRO:2025-12-30. Mengubah awalreplay1Des danexitexclose menghasilkanrun52c72d21completed. Nilai dikonfirmasi APIproxy3000 di readiness-case.json; reload lalu history membuka hasil yang sama.
- **Kas versus NAV:**102.900.364=60.000+95.206.000+7.634.364; dividen danhasiljual belum tersedia dalam kas. Tanggal5Jan2026/15Jan2026 tercetak lengkap. Snapshotgrossdi luarpajak/biaya/slippage.
- **Layout:**mobile390×844 clientWidth/scrollWidth390; screenshot readiness-mobile.jpg. Desktop1280×900 readiness-desktop.jpg. Console warn/error kosong pada alurterakhir. Override viewport direset saat handoff.
- **Batas:**PM-01–07 dalam TEST_MATRIX.md belum dijalankan PM; tidak mengubah statusS5-03/S6 atau mengklaimcoveragePRD.

## Persiapan review U-01–U-02

- **Pemeriksaan statis:** ESLint, TypeScript dan build produksi webpack lulus setelah perubahan Simulator/types/CSS. Backend dan engine perhitungan tidak diubah, sehingga suite40pytest/matriks1.620 tidak diulang pada tahap ini.
- **Hasil tersimpan:** buka52c72d21 saat form masih contoh3event; UI menyatakan form berbeda dan menampilkan input ADRO,1–31Desember,entry5,exitexclose,holding20,modal100juta,engine/dataset yang asli.
- **Salin dan eksperimen:** tombol salin memperbarui semua field dan memfokuskan modal, tanpa submit. Ubah hanya exitkeBEP; snapshot lama tetap exclose. Submit membuat d049736a. API membandingkan seluruh input dan menyatakan hanya exit_rule berbeda; seluruh record52c72d21 identik dengan bukti awal readiness-case.json.
- **Semantik hasil:** kedua run mempunyai gross PnL2.900.364. Runawal memuat piutangjual95.206.000; runBEP memuat posisisaham95.206.000 dan piutangjual0. Jejak menunjukkan Terjual versus Masih dipegang. Bukan klaim perbaikan profit atau prediksi.
- **Riwayat/legacy:** lihatsemua membuka recordketujuh6fed9bfe; hasil replay-v1 tidak diberi datasetversion rekaan. Salininput tanpa start_date memakai13Maret dari hasil. Tidak menjalankan ulang atau mengubah record legacy. Reload dan buka52c72d21 berhasil.
- **Visual:** desktop1280×900 dan mobile390×844, clientWidth/scrollWidth390, consolewarn/error kosong. Screenshot [desktop](../../outputs/development/saved-input-desktop.jpg), [mobile](../../outputs/development/saved-input-mobile.jpg). Override viewport direset setelah pemeriksaan.
- **Artefak/API:** [input dan hasil kedua run](../../outputs/development/saved-input-comparison.json), [panduan PM](./UAT_SESSION.md). Seluruh tugas PM tetap WAITING_PM. Tidak ada panggilan Sectors baru atau deployment.

## Akses LAN L-01 — 6 Oktober 2026

`bun run start:lan` membuka frontend pada0.0.0.0:3000. IP antarmuka en0 saat pemeriksaan10.64.50.225. Listener *:3000 terkonfirmasi; halaman dan proxy /api/catalog melalui IP LAN memberikanHTTP200, judulDividenLab dan9emiten/12event. Backend tetaploopback8000. Tidak perlu rebuild karena perubahan hanya script peluncuran/dokumentasi. Akses dari perangkat kedua belum diperiksa; firewall/router tidak diubah.
