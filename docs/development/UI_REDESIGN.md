# Evolusi UI demo — 8 Oktober 2026

## Tujuan dan keputusan

PM mengalihkan prioritas dari engine proyeksi ke alur dan presentasi demo. Layar utama kini mempunyai dua tujuan yang mudah ditemukan: **Analisis** (grafik peristiwa dividen) dan **Simulasi** (replay historis). Navigasi horizontal menggantikan sidebar dua-item yang mengambil lebar chart. Chart tetap menjadi objek utama; catatan sumber dan ketidaklengkapan LPPF tetap terlihat.

Keputusan D-04 mula-mula memakai latar arang kehijauan, teks terang, dan aksen pasir. Ini catatan historis, bukan palet aktif setelah revisi D-05. Merah/hijau tetap menandai arah perubahan Cum → Ex dan hasil yang memang mempunyai makna positif/negatif. Label “2026 Aktual + Prediksi” menjadi “2026 Aktual” karena engine prediksi belum tersedia.

Perubahan hanya pada presentasi dan interaksi UI. Sumber Sectors, nilai harga/dividen, aturan simulasi, dan kalkulasi backend tidak berubah. Mode grafik tidak lagi me-remount toolbar saat berganti, sehingga fokus keyboard tetap berada pada tombol mode; fokus tahun direset saat dataset berubah. `ISS-041` (kelengkapan LPPF), `ISS-042` (engine prediksi), dan `ISS-054` (handoff chart ke Simulator; semula ISS-046 pada branch UI) tetap terbuka.

## Acuan dan penerapannya

| Acuan primer | Prinsip yang dipakai di sini |
|---|---|
| [Linear: A calmer interface for a product in motion](https://linear.app/now/behind-the-latest-design-refresh) | Navigasi yang sudah menyelesaikan orientasi tidak perlu terus bersaing dengan area kerja. Dua tujuan utama dipindah ke header ringkas agar chart mendapat lebar penuh. |
| [TradingView: UI elements](https://www.tradingview.com/charting-library-docs/latest/ui_elements/) | Pemilihan simbol, periode dan satuan dikelompokkan dekat grafik, bukan tersebar di beberapa panel. Tidak menyalin kepadatan fitur trading terminalnya. |
| [TradingView: shared toolbar in multi-chart layouts](https://www.tradingview.com/blog/en/new-bottom-toolbar-in-multichart-layout-11245/) | Kontrol yang sama tidak perlu diduplikasi di setiap bagian; toolbar chart dibatasi pada fokus tahun, mode, dan satuan. |
| [Koyfin: charting and integrated research workflow](https://www.koyfin.com/blog/best-stock-charting-software/) | Chart dapat menjadi awal alur riset, tetapi integrasi analisis-ke-simulasi di produk ini belum selesai (`ISS-054`); jangan menyebut dua layar sebagai satu workflow mulus. |
| [GOV.UK: Data visualisation principles](https://brand.design-system.service.gov.uk/data/) dan [chart colours](https://brand.design-system.service.gov.uk/colour/charts/) | Warna kategori dibatasi, satuan dan sumber tetap eksplisit, arah perubahan tidak hanya dikodekan dengan warna tetapi juga angka dan teks. |
| [Atlassian: Design tokens](https://atlassian.design/foundations/design-tokens) dan [elevation](https://atlassian.design/foundations/elevation/) | Token semantik untuk latar, permukaan, teks, garis, aksen, dan status; permukaan datar dibedakan dengan batas, bukan gradien/shadow berlapis. |

Referensi ini menjadi prinsip evaluasi, bukan bukti bahwa UI telah lolos uji pengguna. Tidak ada aset, komponen, atau kode pihak ketiga yang disalin.

## Pemeriksaan D-04 dan batas

- `npm run lint`, `npm run typecheck`, `npm run build`, serta 46 tes backend lulus; satu warning deprecation Starlette sudah ada sebelumnya.
- Browser lokal: Analisis dan Simulasi dapat dibuka dari header; chart LPPF dan caveat pratinjau terlihat; mode 2026 menampilkan status aktual tanpa angka forecast; pindah mode mempertahankan fokus keyboard. Pada viewport 390px tidak ada overflow horizontal (`scrollWidth` 375px); awal grafik sekitar 768px dari atas pada mode 2026, sehingga interaksi grafik tetap memerlukan scroll pada ponsel.
- Ini pemeriksaan development, bukan UAT atau validasi kelengkapan data. CSS fitur lama yang tidak ada di navigasi utama belum sepenuhnya dimigrasikan ke palet baru; jangan klaim seluruh produk mempunyai theme coverage yang lengkap.

## Revisi D-05: ritme editorial dan ruang baca

Atas contoh langsung dari PM, [Arcturis Data](https://www.arcturisdata.com/) menjadi acuan ritme visual: bidang terang yang lapang, tipografi besar, satu pesan dominan per layar, panel data gelap sebagai kontras, dan aksen jingga yang hemat. Implementasi ini menerjemahkan prinsip tersebut untuk alat riset dividen; tidak mengambil aset, kode, atau menganggap situs acuan sebagai referensi produk finansial. Palet aktif sekarang putih hangat `#f7f7f3`, navy `#131e29`, dan jingga `#ff4713`.

Analisis dan Simulasi masing-masing dimulai dengan hero hampir setinggi viewport dan tautan ke area kerja. Chart mendapat kanvas navy lebih besar dengan lima tahun yang tetap bisa difokuskan, mode `%`/`Rp`, dan fase peristiwa. Form simulasi dibagi menjadi tiga langkah, hasil didahulukan sebelum rincian input; uraian teknis dipindah ke disclosure dan Metodologi. Navigasi, pemilihan tahun, input, replay, serta caveat pratinjau LPPF dan hasil gross dipertahankan. Hero sengaja membuat chart/form berada di bawah fold, termasuk pada ponsel; jangan menyamakan pengukuran D-04 (~768px) dengan versi ini. Halaman Metodologi juga diberi tipografi dan kontras yang sesuai palet terang.

Ini perubahan presentasi, bukan penggantian data, perhitungan, ataupun implementasi proyeksi. `ISS-041`, `ISS-042`, dan `ISS-054` tetap terbuka. Handoff analisis ke simulasi belum otomatis, dan periode berikutnya tidak menampilkan lintasan prediksi. Pemeriksaan D-05 yang benar-benar dilakukan dicatat terpisah di [PROGRESS.md](./PROGRESS.md); pemeriksaan development bukan UAT.
