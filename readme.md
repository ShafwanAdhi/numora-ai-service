# Numora AI Service

**Progres terkini:** Drill 1.150 original = 1.051 generator + 83 konseptual + 16 HOLD; 0 unavailable. Cakupan lokal 98,6%. [Rincian seluruh indikator dan sisa pekerjaan](docs/PROGRESS.md). Angka pada snapshot sebelumnya bersifat historis.

## Indikator 20 level 4-5 selesai, 21 Oktober 2026

13 generator yang sebelumnya belum tersedia kini aktif. Indikator 20 memuat 50 original: **41 generator + 9 konseptual**, dengan seluruh 20 soal level 4-5 memiliki generator. Original, nomor sumber dan paket tetap dipertahankan.

Runtime keseluruhan: **1.180 original, 1.078 generator, 86 konseptual dan 16 HOLD**; tidak ada original unavailable. Total Drill: 1.150 original, 1.051 generator, 83 konseptual, 16 HOLD. Angka pada snapshot tahap sebelumnya bersifat historis. Rentang baru belum dikalibrasi IRT dan penyesuaian otomatis tetap nonaktif.

[Laporan, daftar 13 ID, domain dan bukti pengujian](docs/audits/2026-10-21-drill-20-level45-completion/README.md).

## Inventaris seluruh indikator, 21 Oktober 2026

Bank lokal memuat **1.150 original Drill** (50 per indikator 1-23): **1.038 generator**, **83 konseptual dengan stok**, **16 HOLD**, dan **13 belum mempunyai generator/stok**. Sebanyak 1.121/1.150 posisi sudah terlayani secara lokal (97,5%). Cakupan bukan persetujuan akademik atau kesetaraan kesulitan.

Bersama Tryout: 1.180 original, 1.065 generator, 86 konseptual/248 varian manual. Seluruh 1.065 generator lulus validasi config, reproduksi original dan satu panggilan seed tetap pada pemeriksaan ini. Ini bukan audit ulang seluruh domain parameter.

[Laporan per indikator, per level, dan 29 soal tersisa](docs/audits/2026-10-21-all-indicators-progress/README.md). Angka pada pembaruan tahap sebelumnya merupakan snapshot historis.

## Pembaruan 21 Oktober 2026: koreksi indikator 1-5 disetujui

**ENGINEERING DECISION - instruksi pengguna:** 28 koreksi dan aktivasi generator lokal telah disetujui. Indikator 1-5 kini memuat **250 original**, dengan **100 generator level 4-5**. Total indikator 1-5: 238 generator, 10 original konseptual dengan stok manual, dan 2 HOLD lama pada level 1-3.

Bank tambahan `variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/` mempertahankan original v2/config v1 yang sama dengan draf yang direview. Persetujuan dicatat sebagai `USER_APPROVED_CORRECTION`; arsip draf tetap utuh. Penyesuaian otomatis, publikasi database, dan persetujuan kesetaraan kesulitan tidak diaktifkan.

[Laporan aktivasi dan catatan persetujuan](docs/audits/2026-10-21-drill-1-5-level45-approved/README.md). Angka dan status draf pada laporan tahap sebelumnya merupakan snapshot sebelum persetujuan ini. Restart proses lokal yang sudah berjalan untuk memuat bank/config tambahan.

## Status terbaru 21 Oktober 2026: batch kedua generator indikator 20-23

Tambahan **27 generator** (indikator 20=4, 21=8, 22=11, 23=4). Total **54/80 original baru (67,5%)** sudah memiliki generator; tersisa **13 menunggu generator/stok + 13 HOLD**. Seluruh indikator 20-23: **200 original, 156 generator, 18 konseptual/50 stok**. Batch ini lolos 837 input dan regresi 50 tes. Original serta stok tetap; hasil runtime tidak disimpan, database tidak diubah. Pembaruan sebelumnya merupakan snapshot historis.

[Daftar generator dan validasi](docs/audits/2026-10-21-drill-20-23-level45-batch2/README.md).

## Status terbaru 21 Oktober 2026: 27 generator indikator 20-23 level 4-5

Tahap pertama **27/80 soal (33,75%)** selesai: indikator20=3,21=8,22=6,23=10. Seluruh837 input diuji;810 varian unik valid. Total indikator20-23: **200 original,129 generator,18 konseptual/50 stok,40 menunggu generator/stok,13 HOLD**. Original tidak direvisi, hasil runtime tidak disimpan, database utama tidak diubah. Angka pada pembaruan sebelumnya merupakan snapshot historis.

[Daftar generator dan validasi](docs/audits/2026-10-21-drill-20-23-level45-batch1/README.md).

## Status terbaru 21 Oktober 2026: impor original indikator 20-23 level 4-5

80 original selesai diaudit dan masuk bank lokal: **67 ACTIVE, 13 HOLD_SOURCE**. Indikator20-23 kini lengkap **200 original**, lima level x sepuluh soal per indikator. Tambahan ini belum mempunyai generator/stok; bank lama tetap102 generator dan18 konseptual/50 stok. Kunci primer serta sumber mentah dipertahankan; database utama tidak diubah. Pembaruan bertanggal sebelumnya merupakan snapshot historis.

[Audit per soal dan daftar HOLD](docs/audits/2026-10-21-drill-20-23-level45-import/README.md).

## Status terbaru 21 Oktober 2026: indikator 16-19 lengkap

Seluruh 80 original level 4-5 kini terlayani: **65 generator + 15 konseptual dengan 30 stok**, 0 HOLD. Tambahan tahap akhir: 38 generator dan 30 stok; 14 original direvisi lokal v2 dengan sumber mentah tetap tersimpan. Total indikator 16-19: **200 original, 177 generator, 23 konseptual/52 stok**. Generate runtime tidak disimpan; database utama tidak diubah. Angka pada pembaruan sebelumnya merupakan snapshot historis.

[Laporan dan bukti validasi](docs/audits/2026-10-21-drill-16-19-level45-completion/README.md).

Service terpisah untuk membuat dan meninjau varian soal Numora. Implementasi saat ini: generator deterministik berbasis config JSON, stok konseptual manual, CLI, workbench lokal, dan browser database read-only. Generasi tidak memanggil model AI/LLM. Komputasi IRT belum diimplementasikan di repo ini.

Numora menjalankan aplikasi utama pada VPS utama; repo ini ditujukan untuk VPS AI terpisah. Workbench merupakan alat operator di localhost, belum API produksi untuk aplikasi Numora.

## Pembaruan 20 Oktober 2026: level 4-5 indikator 1-5

Tahap pertama **33 dari 100 original** sudah memiliki generator config v1: indikator 1/2/3 masing-masing 7 soal, indikator 4/5 masing-masing 6 soal; 17 soal level 4 dan 16 soal level 5. Tetap berada di **Drill Paket 1 (`drill-1`)**, dengan nomor sumber dipertahankan. Level tersebut masih parsial, bukan paket level lengkap berisi 10 soal.

Bank tambahan: `variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch1/`. Loader CLI, workbench dan service membaca bank ini. Restart proses yang sudah berjalan untuk memuatnya. Contoh: `python -B variant_gen/cli.py gen pg-1-4-3 s1`.

Inventaris saat ini: **823 original Drill / 752 generator**, serta **30 original Tryout / 27 generator**; total **853 original / 779 generator**. Bank, config, stok dan arsip sumber sebelumnya dipertahankan. Tersisa 67 soal level 4-5: 39 antrean generator dan 28 memerlukan tindak lanjut akademik.

Status `ACTIVE` hanya berarti dapat dibuat secara lokal. Seluruh 33 soal ditandai `NOT_CURRICULUM_APPROVED`, penyesuaian otomatis tidak aktif; tidak ada publikasi/import ke database utama atau persetujuan kesetaraan kesulitan. Rentang input baru dibatasi eksplisit dalam config; batas generator lama tidak diubah. [Daftar soal, kapasitas, pengujian dan antrean](docs/audits/2026-10-20-drill-1-5-level45-batch1/README.md).

## Mulai

Semua perintah dokumentasi dijalankan dari root **Numora-ai-service**, kecuali disebut lain. Gunakan Python 3.11 atau lebih baru.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -B variant_gen/webui.py
```

Buka http://127.0.0.1:8765. Pada soal berstok, pilih Varian1–N; seed/Generate/editor disembunyikan. Restart workbench setelah asset stok berubah. Tab **Service AI** berjalan tanpa database. UI membutuhkan `python-dotenv` dan `psycopg`; engine/CLI generator memakai stdlib. Di Linux, aktivasi venv memakai `source .venv/bin/activate`.

## Status bank lokal - arsip 7 Oktober 2026

Inventaris kode/data per **7 Oktober 2026**:

| Aktivitas | Paket | Original | Soal dengan config | Struktur |
|---|---|---:|---:|---|
| Drill & Practice | `drill-1` / Paket 1 | 790 | 719 | Paket > indikator1–23 > level sumber > soal |
| Tryout | `tryout-1` / Tryout 1 | 30 | 27 | Paket > bab 1–4 > soal |
| Pretest | Belum tersedia | 0 | 0 | Belum memiliki bank lokal |
| Total | | 820 | 746 | |

Paket Drill menargetkan 5 level × 10 soal per indikator. Indikator 11–15 memiliki level 1–5; indikator 6–10 dan 16–23 memiliki level 1–3. Total790 original; indikator1–2 dibatasi level1–3 sesuai scope, indikator3–5 level1–3 sudah tersedia. Seluruh 60 soal indikator 18–19 memiliki config. Config tersedia bukan approval kurikulum atau bukti kesetaraan IRT.

**Stok konseptual lengkap: 67 original Drill, 206 varian VERIFIED, masing-masing2–4.** Generator719 + stok67 + 4 soal HOLD =790 Drill. Stok dapat dibaca berulang walaupun generator belum ada. [Audit variasi dan kesulitan per ID](docs/audits/2026-10-06-conceptual-stock-audit.md).

**Tryout:27 generator +3 original dengan9 stok manual VERIFIED =30 soal.** Pilih stok pada UI/CLI per soal; generate paket tetap memakai original untuk tiga soal konseptual. Total stok seluruh aktivitas70 original/215 varian. [Audit Tryout](docs/audits/2026-10-07-tryout-conceptual-stock-audit.md).

Indikator **1–2**:60 original level1–3, **50 generator aktif**,1 HOLD_SOURCE,9 DEFERRED_CONCEPTUAL dengan stok manual. Enam belas original revisi v2 kini memiliki generator config v1; `pg-1-2-1` tetap ditahan. [Audit generator revisi](docs/audits/2026-10-07-revised-1-5-generator-audit.md); [impor sumber](docs/audits/2026-10-07-drill-1-5-source-revision.md).

Indikator **3–5**:90 original level1–3,**88 generator aktif**,1 HOLD_SOURCE,1 DEFERRED_CONCEPTUAL dengan stok manual. Dua puluh empat original revisi v2 kini memiliki generator config v1; `pg-5-3-3` masih ditahan. [Audit generator revisi](docs/audits/2026-10-07-revised-1-5-generator-audit.md); [impor sumber](docs/audits/2026-10-07-drill-1-5-source-revision.md).

Indikator **6–10**: 150 original, **140 generator aktif**, 1 HOLD_SOURCE dan 9 DEFERRED_CONCEPTUAL dengan stok manual. Sebelas original v2 revisi kurikulum sudah memiliki generator config v1; `mcma-6-3-7` tetap ditahan. Level 1–3 tersedia; level 4–5 belum memiliki sumber. [Audit generator revisi](docs/audits/2026-10-07-revised-6-10-generator-audit.md).

Indikator **11–15**: 250 original, **227 generator aktif**, 1 HOLD_SOURCE dan 22 DEFERRED_CONCEPTUAL dengan stok manual. Bank dan config sudah terintegrasi ke checkout ini; pilih Service AI > Drill > Paket 1 > indikator 11–15 > level 1–5. [Audit generator revisi](docs/audits/2026-10-07-revised-11-15-generator-audit.md).

Indikator **20–23**: 120 original, **102 generator aktif**, **18 DEFERRED_CONCEPTUAL**, tanpa HOLD_SOURCE. Enam belas original revisi kurikulum v2 kini memiliki config v1 dan lolos 20 varian unik per soal serta oracle matematika independen. [Audit generator revisi](docs/audits/2026-10-07-revised-20-23-generator-audit.md) memuat parameter, bukti pemeriksaan dan contoh hasil. Audit 5 Oktober tetap menjadi arsip kondisi sebelumnya. Delapan Drill indikator16–19 dan tiga Tryout tetap tanpa generator.

Di tab **Service AI**, pilih Drill > Paket 1 > indikator20–23 > level > soal. Generate menampilkan respons tanpa penyimpanan lokal. Tidak ada Regen atau riwayat varian; generate dapat diulang tanpa batas stok. Seed sama menghasilkan soal sama, seed lain belum tentu unik. Nomor dokumen dan status review ditampilkan; kunci HOLD belum disahkan. Kategori Kuantitatif/Kualitatif dan Sesuai/Tidak Sesuai mempertahankan label sumber. Level4–5 tersedia pada indikator 11–15; kelompok lainnya masih kosong.

```powershell
python -B variant_gen/cli.py gen pg-21-1-1 s1-20
python -B variant_gen/cli.py view pg-21-1-1 s1
```

Bank tambahan disimpan di `variant_gen/data/drill-1-indicators-{1-2,3-5,6-10,11-15,20-23}/` dan dimuat bersama bank dasar; bank/config dipertahankan. Generator memakai engine deterministik dan mengembalikan hasil tanpa menyimpannya. Ekspor kontrak kategori boolean menolak label kategori khusus; tidak mengakses atau menulis database Numora.

Original disimpan sebagai CSV dengan ledger revisi. Hasil generator numerik hanya berada dalam respons/tampilan; stok konseptual adalah asset JSON offline yang dibaca ulang tanpa habis. Jumlah ini **bukan inventaris database Numora**. Tab **DB Utama** membaca database bila `DATABASE_URL` dikonfigurasi; generator tidak mengimpor/memublikasikan hasil ke database tersebut.

## Dokumentasi

- [Panduan penggunaan](docs/OPERATIONS.md): UI, CLI, seed, generate, paket, tes, troubleshooting.
- [Referensi generator](docs/GENERATOR.md): bank, config, variabel, validator, versi, penambahan soal.
- [Arsitektur dan integrasi](docs/ARCHITECTURE.md): modul, alur data, ekspor Numora, akses DB, batas implementasi.
- [Integrasi generator HTTP v1](docs/handoffs/NUMORA_GENERATOR_INTEGRATION_V1.md): service compute, kontrak, konfigurasi dan runbook. [Prompt repo pusat](docs/handoffs/NUMORA_CENTRAL_IMPLEMENTATION_PROMPT.md). Service default nonaktif; UI pusat masih perlu implementasi.
- [Indeks dan arsip](docs/README.md): desain, audit, progres, sumber akademik.

## Verifikasi

```powershell
python -B -m unittest discover -s variant_gen/tests -v
```

Verifikasi gabungan dicatat pada [laporan kondisi repo](docs/audits/2026-10-07-repository-status.md). Tes memakai fixture sementara dan memeriksa generate tanpa penyimpanan. Editor config tetap memerlukan satu writer untuk folder config yang sama.
## Penyelesaian indikator 1–5 level 4–5 (21 Oktober 2026)

Cakupan 100 soal sumber baru kini memiliki **72 generator lokal** (33 tahap pertama + 39 tambahan) dan **28 draf koreksi beserta generator terpisah yang belum aktif**. Seluruhnya mempertahankan Drill Paket 1, indikator, level, serta nomor sumber. Draf tidak muncul dalam katalog atau jalur generate default.

[Laporan dan bukti audit](docs/audits/2026-10-20-drill-1-5-level45-completion/README.md) · [Ringkasan 28 usulan koreksi](docs/audits/2026-10-20-drill-1-5-level45-completion/correction-review.csv) · [Isi sebelum/sesudah koreksi](variant_gen/drafts/2026-10-20-level45-academic/proposed_corrections.json).

Rentang dan kesetaraan kesulitan belum disetujui Kurikulum; penyesuaian otomatis tetap nonaktif. Tidak ada publikasi atau perubahan database. Restart proses lokal untuk memuat bank/config tambahan.
