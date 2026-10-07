# Penghentian sementara layanan Dalang

Status: selesai dan terverifikasi pada **7 Oktober 2026, 12:10:07 UTC / 20:10:07 WITA**.
Task: **OPS-01**, instruksi langsung PM; bukan deployment Horizon atau kelulusan UAT.

## Keputusan dan otorisasi

PM memilih mempertahankan FastAPI dan meng-host backend Horizon menggunakan Docker di VPS Dalang. Proposal mengganti backend dengan Next.js + ORM TypeScript tidak dilanjutkan. Tidak ada rewrite atau penghapusan SQLAlchemy yang sudah digunakan backend pada pekerjaan ini. Database aplikasi tetap Supabase.

Permintaan awal adalah menghentikan seluruh container Docker. Pemeriksaan langsung menemukan Docker/Podman tidak tersedia, proses dockerd/containerd tidak berjalan, dan unit docker.service/docker.socket/containerd.service tidak ditemukan. Lima layanan kurasi berjalan langsung melalui systemd. Setelah mendapat daftar tersebut, PM mengonfirmasi: **“Ya, hentikan kelima layanan kurasi.”**

## Identitas VPS dan bukti

- Dalang service: `hyperliquid-engine`.
- VPS ID: `10e0ff54-f828-44de-a965-5671328a08d3`.
- Hostname guest: `vps-10e0ff54`.
- Spesifikasi dari provider: 2 vCPU, RAM 2048 MB, storage 10 GB.
- Akses terverifikasi melalui CLI `dalang exec`; tidak menggunakan SSH ke domain dalang.io.
- Salinan bukti pada VPS: `/root/horizon-ops/20261007T120842Z/`.
- Inventaris sebelum tindakan: [before.json](../../outputs/operations/dalang-20261007T120842Z/before.json).
- Perintah dan waktu penghentian: [stop-request.json](../../outputs/operations/dalang-20261007T120842Z/stop-request.json).
- Verifikasi sesudah tindakan: [after.json](../../outputs/operations/dalang-20261007T120842Z/after.json).

## Layanan yang dihentikan

| Unit systemd | Fungsi menurut konfigurasi | Sebelum | Hasil terverifikasi | Autostart |
|---|---|---|---|---|
| `curation-realtime.service` | Producer kurasi read-only | active/running | inactive/dead, PID 0, success | enabled, tidak diubah |
| `curation-recorder.service` | Recorder kurasi | active/running | inactive/dead, PID 0, success | enabled, tidak diubah |
| `curation-reversal-paper.service` | Eksperimen reversal paper | active/running | inactive/dead, PID 0, success | enabled, tidak diubah |
| `curation-reversal-paper-v2.service` | Eksperimen reversal paper v2 | active/running | inactive/dead, PID 0, success | enabled, tidak diubah |
| `curation-zone-paper.service` | Eksperimen zone reversal paper | active/running | inactive/dead, PID 0, success | enabled, tidak diubah |

Container Docker yang dihentikan: **0**. Layanan systemd yang dihentikan: **5**.

`systemctl stop --no-block` dikirim pada 12:09:29 UTC. Verifikasi pada 12:10:07 UTC menemukan seluruh unit inactive/dead, Result=success, MainPID=0 dan tidak ada job terkait yang tertunda. Snapshot sebelum penghentian menyimpan restart policy, dependency, lokasi unit, dan jumlah restart. Tidak ada kill paksa, uninstall, disable, penghapusan database atau penghapusan volume.

Pengaturan enabled tetap dipertahankan: layanan dapat hidup kembali setelah reboot VPS. Pengumpulan data dan eksperimen forward berhenti selama layanan tidak aktif; periode tersebut bukan data observasi yang terkumpul. Tidak ada pemeriksaan integritas seluruh database pada pekerjaan ini.

## Menyalakan kembali ketika diminta PM

Jangan menjalankan langkah ini otomatis sebagai bagian deployment Horizon. Verifikasi ulang identitas VPS dan status saat menerima permintaan restart berikutnya; snapshot adalah bukti historis. Jangan menimpa konfigurasi/data layanan lama.

1. Periksa VPS dan kelima unit. Jika CLI membutuhkan autentikasi, gunakan alur login Dalang.

```sh
dalang service list --json
dalang exec hyperliquid-engine 'systemctl show curation-realtime.service curation-recorder.service curation-reversal-paper.service curation-reversal-paper-v2.service curation-zone-paper.service --property=Id,ActiveState,SubState,MainPID,UnitFileState'
```

2. Jalankan producer terlebih dahulu, periksa statusnya, lalu jalankan recorder dan eksperimen. `start` pada unit aktif tidak memulai ulang proses yang sudah berjalan.

```sh
dalang exec hyperliquid-engine 'systemctl start curation-realtime.service'
dalang exec hyperliquid-engine 'systemctl is-active curation-realtime.service'
dalang exec hyperliquid-engine 'systemctl start curation-recorder.service curation-reversal-paper.service curation-reversal-paper-v2.service curation-zone-paper.service'
```

3. Ulangi pemeriksaan seluruh unit; pastikan active/running dan PID bukan 0. Periksa timestamp hasil producer, recorder, dan collector sebelum menyatakan alur data pulih. Status systemd aktif saja belum membuktikan data fresh. Catat waktu pemulihan dan hasil aktual di log baru; pertahankan snapshot penghentian.

## Pekerjaan lanjutan

Docker belum terpasang. Instalasi Docker, image/Compose Horizon, konfigurasi server-only, HTTPS, domain dan deployment backend belum dilakukan pada OPS-01. Gunakan satu proses backend sesuai batas advisory lock runtime saat ini. Tinjau kapasitas jika layanan kurasi diaktifkan lagi bersamaan dengan Horizon; belum ada benchmark kapasitas bersama.

Temuan lain: `curation-realtime.service` mempunyai `NRestarts=641` sebelum penghentian. Penyebab dan rentang akumulasi tidak diperiksa; ini bukan diagnosis crash, kekurangan RAM atau masalah storage tertentu. Verifikasi kesehatan producer pada pemulihan berikutnya.
