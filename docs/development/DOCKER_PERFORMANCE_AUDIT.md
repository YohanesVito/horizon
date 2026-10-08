# Audit Docker versus native — PERF-01

Permintaan PM 8 Oktober 2026: identifikasi gap performa Horizon pada VPS 2 vCPU, RAM 2 GB, SSD 10 GB. Scope audit dan rekomendasi, terkait DEP-01/S5-02/C-08; tidak mengganti deployment. Pemeriksaan live dilakukan 8 Oktober 2026 pukul 14:21–14:22 WITA melalui Dalang CLI. Tidak menjalankan load test, backend kedua, atau perubahan layanan.

## Bukti live

Output non-rahasia: [resources.txt](../../outputs/operations/docker-performance-20261008/resources.txt) dan [io-and-cgroups.txt](../../outputs/operations/docker-performance-20261008/io-and-cgroups.txt). CLI exec mengembalikan echo/hasil parsial, sehingga hasil dialihkan ke file sementara lalu diambil melalui Dalang scp. Exit code CLI sendiri tidak dipakai sebagai bukti.

| Metrik | Hasil | Interpretasi |
|---|---|---|
| RAM yang terlihat oleh OS | 1.827 MiB total, 1.229 MiB available | Snapshot masih punya headroom; berbeda dari kapasitas paket nominal 2 GB |
| Container Horizon | CPU 0,34%; 73,98 MiB / 768 MiB | Pemakaian saat sampel, bukan kebutuhan puncak pada trafik tinggi; 768 MiB merupakan batas |
| Docker runtime RSS | dockerd 109.620 KiB; containerd 36.288 KiB; shim 12.376 KiB | Jumlah kasar 154,6 MiB; shared pages membuat penjumlahan RSS bukan penghematan RAM eksak |
| Container resource counters | CPU throttling 0; OOM/OOM kill 0; restart 0 | Tidak ada bukti container tertahan kuota CPU atau terbunuh karena RAM pada counter yang dibaca |
| Container memory.peak | 94.908.416 byte, sekitar 90,5 MiB | Counter puncak cgroup yang tersedia, bukan hasil stress test |
| Disk root | 9,6 GiB total, 4,9 GiB used, 4,7 GiB available; 52% | Belum penuh saat audit |
| Docker disk accounting | Images 318,1 MB; build cache 322,5 MB | Jangan dijumlahkan sebagai disk unik/reclaimable; layer dapat berbagi data |
| I/O PSI full avg60 | 81,71%, lalu 85,19% | Proporsi waktu semua tugas non-idle tersendat I/O dalam jendela 60 detik; bukan persentase disk penuh |
| vmstat | Dua interval 1 detik menunjukkan iowait 45% dan 50% | Baris pertama vmstat adalah rata-rata sejak boot dan tidak dipakai sebagai interval live |
| Proses menunggu storage | jbd2: D/wait_on_buffer; dpkg: D/jbd2_log_wait_commit | Menegaskan hambatan I/O; proses unattended-upgrade hadir bersamaan, hubungan sebab-akibat belum terisolasi |
| GET localhost /api/health | HTTP 200, 1,350214 detik | Satu sampel melewati port Docker dan query Supabase; bukan p95 atau overhead Docker murni |

Snapshot live tidak membuktikan kapasitas maksimum pengguna atau representasi seluruh hari. Source lokal dapat lebih baru dari image terpasang; audit kode berikut menjelaskan checkout yang ditinjau, tanpa mengklaim parity seluruh kode dengan release VPS.

## Perbandingan yang relevan untuk Horizon

| Aspek | Docker Engine Linux saat ini | Native Python venv + systemd |
|---|---|---|
| CPU kalkulasi | Proses Python berbagi kernel host; ada limit 1,5 CPU | Menghapus container tidak mengubah algoritme Python; pembandingan harus memakai limit setara |
| RAM | RAM aplikasi ditambah daemon/runtime Docker | Bisa menghilangkan overhead runtime bila Docker/containerd tidak diperlukan layanan lain; RAM aplikasi/dataset tetap ada |
| Disk | Base image, layer, build cache, arsip release | Tetap perlu Python, venv, dependency dan release; berpotensi lebih hemat, besar selisih belum diukur |
| I/O runtime | Root filesystem read-only, tmpfs untuk sementara; data aplikasi di Supabase | Tidak menghilangkan hambatan journal/disk OS yang juga terjadi di luar container |
| Jaringan | Port mapping bridge/NAT; MTU pernah bermasalah dan diperbaiki pada ISS-049 | Menghilangkan jalur bridge/NAT; latensi provider/Supabase tetap ada |
| Deployment | Build image di VPS saat ini menambah pekerjaan I/O/CPU/RAM | pip/install/extract juga memakai I/O; build di luar VPS mengurangi pekerjaan lokal pada kedua pendekatan |
| Operasi | Image terkunci, restart dan pembatasan resource sudah dikonfigurasi | Perlu menjaga versi Python/dependency, restart policy, user, limit dan rollback melalui systemd/release |

Tidak ada angka persen peningkatan native yang dapat dibuktikan: belum dilakukan A/B dengan versi Python, dependency, dataset, resource limit, database dan beban identik. Docker native Linux berbagi kernel; hasil Docker Desktop pada Mac tidak mewakili VPS ini.

## Gap aplikasi yang tidak selesai dengan melepas Docker

- `backend/main.py`: satu proses Uvicorn, dua thread replay. Kalkulasi Python CPU-bound dapat bersaing dengan API; dua thread tidak otomatis setara dua core. Besar dampaknya belum diprofilkan.
- `backend/store.py:worker_lease`: advisory lock PostgreSQL membatasi satu proses backend per database. Menambah `--workers` bukan perubahan konfigurasi yang aman untuk arsitektur sekarang.
- `backend/config.py`: pool 5 + overflow 2; satu koneksi ditahan oleh worker lease. Latensi jaringan/query Supabase dan antrean pool tetap ada pada native. Belum terbukti menjadi bottleneck saat ini.
- Endpoint riwayat mengambil dan mendecode payload hasil lengkap sebelum membuang field `result` (`main.py`, `store.py`). Berpotensi memboroskan transfer/RAM saat hasil membesar; belum ada pengukuran dampak.
- `deploy/build-release.sh` menjalankan `docker build --pull` pada VPS; limit Compose 768 MiB/1,5 CPU tidak membatasi proses build tersebut. Pertumbuhan image, cache dan arsip release perlu kebijakan retensi pada disk 10 GB.
- Docker healthcheck memulai interpreter kecil dan mengakses health/query DB setiap 30 detik. Ada pekerjaan tambahan, tetapi belum ada bukti signifikan pada kapasitas ini.

## Rekomendasi

Pertahankan Docker untuk MVP saat ini. RAM dan kuota CPU tidak menunjukkan masalah pada sampel, sedangkan I/O OS terbukti tersendat. Prioritas berikutnya adalah diagnosis ISS-048: amati I/O setelah pembaruan OS selesai secara normal, periksa error/latensi storage dan batas provider jika tekanan berlanjut. Tidak mematikan updater, memaksa dpkg, atau mengubah fsync.

Untuk deployment berikutnya, pertimbangkan build image di CI/mesin lain dan pull image di VPS, serta retensi release/cache yang mempertahankan rollback. Ini rekomendasi, belum diimplementasikan. Native layak dipertimbangkan bila penghematan RAM/disk menjadi kebutuhan nyata; angka RSS runtime sekitar 155 MiB hanya petunjuk skala, bukan janji penghematan.

A/B lanjutan: gunakan salinan dataset/database terisolasi agar tidak membuka worker kedua pada Supabase produksi. Samakan runtime, versi source, limit CPU/RAM, worker, koneksi DB dan request mix; ukur p50/p95, throughput/error, memory peak, throttling dan PSI pada beban normal serta replay bersamaan. Ukur baseline pada periode I/O stabil dan ulang beberapa kali. Tidak menyimpulkan kapasitas atau keuntungan migrasi dari healthcheck tunggal.

## Referensi primer

- [Docker: container berbagi kernel](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Docker: batas CPU dan RAM](https://docs.docker.com/engine/containers/resource_constraints/)
- [Docker: storage drivers dan layer](https://docs.docker.com/engine/storage/drivers/)
- [Docker: host networking dan NAT](https://docs.docker.com/engine/network/drivers/host/)
- [FastAPI: proses dan memori deployment](https://fastapi.tiangolo.com/deployment/concepts/)
- [Linux kernel: definisi PSI](https://docs.kernel.org/accounting/psi.html)
