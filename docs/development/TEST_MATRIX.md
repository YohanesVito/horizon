# Matriks pemeriksaan MVP — 6 Oktober 2026

Baseline: C-01–C-08 dari percakapan. PRD/user story asli belum tersedia (ISS-001). Ini hasil pemeriksaan developer dan persiapan uji bersama PM; tidak menyatakan persetujuan UAT atau profitabilitas strategi.

## Cara mengulang pemeriksaan

```sh
.venv/bin/python -m pytest backend/tests -q
.venv/bin/python work/verify_mvp.py
bun run lint
bun run typecheck
bun run build
```

`verify_mvp.py` memakai snapshot Sectors lokal tanpa panggilan API provider atau perubahan database pengguna. Hasil disimpan di `outputs/development/mvp-readiness.json`. Matriksnya: 12 event individual + 3 portofolio lintas emiten/dividen berulang × 3 entry offsets × 4 exit rules × 3 holding limits × 3 alokasi = **1.620 replay**. Setiap replay dicek terhadap hak dividen berdasarkan tanggal kepemilikan, lot100, urutan entry/exit/settlement, keseimbangan NAV, serta nilai finite/nonnegatif. Ini pemeriksaan akuntansi, bukan 1.620 strategi yang terbukti menguntungkan.

## Hasil developer

| ID | Skenario dan harapan | Status | Bukti |
|---|---|---|---|
| QA-01 | Hak dividen setiap lot sesuai seluruh ex-date ketika dimiliki, termasuk event tak dipilih | PASS | Matriks1.620/0gagal; fixture dua lot di test_rotation.py |
| QA-02 | Kas, posisi, piutang jual, piutang dividen berjumlah NAV; tidak ada margin tersembunyi | PASS | Seluruh matriks, semua bar saldo nonnegatif |
| QA-03 | Modal kurang satu lot tidak membuka posisi atau menghasilkan return dari pembulatan | PASS | Tiga regression test kas pecahan; engine v2.1 |
| QA-04 | Kas jual baru boleh dipakai setelah settlement, termasuk bila entry berikutnya jatuh tepat pada hari settlement | PASS | Synthetic deterministic fixture untuk entryT+1terlewat/entryT+2berhasil |
| QA-05 | Event akhir Desember dijual sebelum payment; kas/piutang tetap dipisahkan saat akhir replay | PASS | Test ADRO2025-12-30 dan alur browser; payment/settlement terjadi2026 |
| QA-06 | BEP close dipakai sebagai sinyal; fill open berikutnya dapat di bawah entry | PASS | Fixture gap down dan terminal signal tanpa future fill |
| QA-07 | Ranking/rute tidak berubah saat harga setelah cutoff dimodifikasi | PASS | Test perturbasi futureprice7×, unfinished event tetap censored |
| QA-08 | Empty/verified-only/minsamplestrict menjelaskan alasan dan tidak membuat hasil rekaan | PASS | API regression + browser sprintR |
| QA-09 | Job gagal tidak stuck; input diperbaiki menghasilkan run baru | PASS | Test failed→corrected retry, record gagal tetap tersimpan |
| QA-10 | Restart menandai job terputus gagal tanpa mengubah hasil completed | PASS | Test startup kedua jenis job pada database sementara |
| QA-11 | ID rencana/rotation-run/manual-run tidak saling terbaca dengan kontrak berbeda | PASS | Test silang ID→404; hasil asli tetap200 |
| QA-12 | Klik event tertentu di detail membawa ID dan tanggal yang sesuai ke simulator | PASS | Browser ADROex30Des memilih satu event; bukan tiga event contoh |
| QA-13 | Tanggal lintas tahun jelas, halaman mobile tidak melebar | PASS | Bukti browser di VERIFICATION.md dan screenshot kesiapan |
| QA-14 | Build dan pemeriksaan statis lulus | PASS | ESLint, TypeScript, webpack build;40pytest lulus, warning Starlette tetap ISS-016 |
| QA-15 | Hasil lama menampilkan input asli; salin tidak mengubah hasil; eksperimen satu aturan membuat ID baru | PASS | Browser + saved-input-comparison.json: ex_close→price_bep satu-satunya perbedaan input, record awal identik; legacy start-date fallback dan lihat semua diuji |

## Uji bersama PM — belum dijalankan

| ID | Tugas pengguna tanpa bantuan developer | Pertanyaan evaluasi | Status |
|---|---|---|---|
| PM-01 | Pilih emiten dari Peluang, telusuri timeline, kirim satu event ke Simulator | Apakah jelas emiten dan event mana yang sedang diuji? | WAITING_PM |
| PM-02 | Ubah satu aturan financial logic lalu buat kandidat rute | Apakah alasan perubahan ranking dapat dipahami? | WAITING_PM |
| PM-03 | Bandingkan all-in/split/rotasi pada modal dan periode yang sama | Apakah gross PnL, risiko dan waktu modal tertahan cukup untuk memilih eksperimen berikutnya? | WAITING_PM |
| PM-04 | Telusuri ADROakhir2025 dan jawab berapa uang yang langsung bisa dipakai | Apakah pengguna membedakan NAV dari kas tersedia? | WAITING_PM |
| PM-05 | Cari contoh saham belum pulih; ubah batas holding | Apakah force-exit dan perbedaan BEP harga/BEP total dipahami? | WAITING_PM |
| PM-06 | Matikan asumsi kalender; buka event yang dikeluarkan | Apakah jelas mengapa sistem belum boleh mengklaim forecast? | WAITING_PM |
| PM-07 | Pilih hasil lama setelah reload | Apakah input/hasil/versi lama dapat ditelusuri tanpa mengira hasil mengikuti form baru? | WAITING_PM |

## Gap yang tetap terlihat

- **BYPASSED:** declaration timestamp/vintage data, kalender settlement resmi, lapkeu point-in-time, koreksi basis split empat event, infrastruktur lokal dan multi-user.
- **BELUM TERSEDIA:** model trap terkalibrasi, proyeksi jadwal/harga, optimizer rotasi forward.
- **DI LUAR HASIL:** biaya transaksi, pajak, slippage sesuai arahan PM; semua nominal gross.
- **WAITING_INPUT:** pemetaan ke PRD/user story asli. Kelulusan pemeriksaan developer tidak menghapus gap tersebut.

Rincian perbaikan ada di [ISSUES.md](./ISSUES.md), status task di [PROGRESS.md](./PROGRESS.md), dan konteks diskusi di [PM_REVIEW.md](./PM_REVIEW.md).

[UAT_SESSION.md](./UAT_SESSION.md) menyiapkan satu kasus ADRO beserta tugas dan lembar observasi untuk PM-01/04/07. Dokumen tersebut belum berisi hasil uji manusia.
