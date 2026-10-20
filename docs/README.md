# Dokumentasi Numora AI Service

**Progres terkini:** Drill 1.150 original = 1.051 generator + 83 konseptual + 16 HOLD; 0 unavailable. Cakupan lokal 98,6%. [Rincian seluruh indikator dan sisa pekerjaan](PROGRESS.md). Angka pada snapshot sebelumnya bersifat historis.

## Indikator 20 level 4-5 selesai, 21 Oktober 2026

13 generator yang sebelumnya belum tersedia kini aktif. Indikator 20 memuat 50 original: **41 generator + 9 konseptual**, dengan seluruh 20 soal level 4-5 memiliki generator. Original, nomor sumber dan paket tetap dipertahankan.

Runtime keseluruhan: **1.180 original, 1.078 generator, 86 konseptual dan 16 HOLD**; tidak ada original unavailable. Total Drill: 1.150 original, 1.051 generator, 83 konseptual, 16 HOLD. Angka pada snapshot tahap sebelumnya bersifat historis. Rentang baru belum dikalibrasi IRT dan penyesuaian otomatis tetap nonaktif.

[Laporan, daftar 13 ID, domain dan bukti pengujian](audits/2026-10-21-drill-20-level45-completion/README.md).

## Inventaris seluruh indikator, 21 Oktober 2026

Bank lokal memuat **1.150 original Drill** (50 per indikator 1-23): **1.038 generator**, **83 konseptual dengan stok**, **16 HOLD**, dan **13 belum mempunyai generator/stok**. Sebanyak 1.121/1.150 posisi sudah terlayani secara lokal (97,5%). Cakupan bukan persetujuan akademik atau kesetaraan kesulitan.

Bersama Tryout: 1.180 original, 1.065 generator, 86 konseptual/248 varian manual. Seluruh 1.065 generator lulus validasi config, reproduksi original dan satu panggilan seed tetap pada pemeriksaan ini. Ini bukan audit ulang seluruh domain parameter.

[Laporan per indikator, per level, dan 29 soal tersisa](audits/2026-10-21-all-indicators-progress/README.md). Angka pada pembaruan tahap sebelumnya merupakan snapshot historis.

## Persetujuan koreksi indikator 1-5, 21 Oktober 2026

**ENGINEERING DECISION - instruksi pengguna:** 28 koreksi dan aktivasi generator lokal telah disetujui. Indikator 1-5 kini memuat **250 original**, dengan **100 generator level 4-5**. Total indikator 1-5: 238 generator, 10 original konseptual dengan stok manual, dan 2 HOLD lama pada level 1-3.

Bank tambahan `variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/` mempertahankan original v2/config v1 yang sama dengan draf yang direview. Persetujuan dicatat sebagai `USER_APPROVED_CORRECTION`; arsip draf tetap utuh. Penyesuaian otomatis, publikasi database, dan persetujuan kesetaraan kesulitan tidak diaktifkan.

[Laporan aktivasi dan catatan persetujuan](audits/2026-10-21-drill-1-5-level45-approved/README.md). Angka dan status draf pada laporan tahap sebelumnya merupakan snapshot sebelum persetujuan ini. Restart proses lokal yang sudah berjalan untuk memuat bank/config tambahan.

## Status terbaru 21 Oktober 2026: batch kedua generator indikator 20-23

Tambahan **27 generator** (indikator 20=4, 21=8, 22=11, 23=4). Total **54/80 original baru (67,5%)** sudah memiliki generator; tersisa **13 menunggu generator/stok + 13 HOLD**. Seluruh indikator 20-23: **200 original, 156 generator, 18 konseptual/50 stok**. Batch ini lolos 837 input dan regresi 50 tes. Original serta stok tetap; hasil runtime tidak disimpan, database tidak diubah. Pembaruan sebelumnya merupakan snapshot historis.

[Daftar generator dan validasi](audits/2026-10-21-drill-20-23-level45-batch2/README.md).

## Status terbaru 21 Oktober 2026: 27 generator indikator 20-23 level 4-5

Tahap pertama **27/80 soal (33,75%)** selesai: indikator20=3,21=8,22=6,23=10. Seluruh837 input diuji;810 varian unik valid. Total indikator20-23: **200 original,129 generator,18 konseptual/50 stok,40 menunggu generator/stok,13 HOLD**. Original tidak direvisi, hasil runtime tidak disimpan, database utama tidak diubah. Angka pada pembaruan sebelumnya merupakan snapshot historis.

[Daftar generator dan validasi](audits/2026-10-21-drill-20-23-level45-batch1/README.md).

## Status terbaru 21 Oktober 2026: impor original indikator 20-23 level 4-5

80 original selesai diaudit dan masuk bank lokal: **67 ACTIVE, 13 HOLD_SOURCE**. Indikator20-23 kini lengkap **200 original**, lima level x sepuluh soal per indikator. Tambahan ini belum mempunyai generator/stok; bank lama tetap102 generator dan18 konseptual/50 stok. Kunci primer serta sumber mentah dipertahankan; database utama tidak diubah. Pembaruan bertanggal sebelumnya merupakan snapshot historis.

[Audit per soal dan daftar HOLD](audits/2026-10-21-drill-20-23-level45-import/README.md).

## Status terbaru 21 Oktober 2026: indikator 16-19 lengkap

Seluruh 80 original level 4-5 kini terlayani: **65 generator + 15 konseptual dengan 30 stok**, 0 HOLD. Tambahan tahap akhir: 38 generator dan 30 stok; 14 original direvisi lokal v2 dengan sumber mentah tetap tersimpan. Total indikator 16-19: **200 original, 177 generator, 23 konseptual/52 stok**. Generate runtime tidak disimpan; database utama tidak diubah. Angka pada pembaruan sebelumnya merupakan snapshot historis.

[Laporan dan bukti validasi](audits/2026-10-21-drill-16-19-level45-completion/README.md).

## Pembaruan 21 Oktober: 27 generator tambahan indikator 16?19

27/80 original baru sudah mempunyai generator (33,75%). Total cakupan indikator16?19:139 generator/200 original;8 soal konseptual dengan22 stok existing;39 menunggu generator/stok,14 HOLD. [Validasi batch pertama](audits/2026-10-21-drill-16-19-level45-batch1/README.md).

## Pembaruan 21 Oktober: indikator 16?19 level 4?5

80 original telah divalidasi dan diimpor ke bank aktif: 66 ACTIVE, 14 HOLD_SOURCE; generator/stok belum ditambahkan. Indikator 16?19 kini lengkap 200 original. [Hasil audit dan daftar HOLD](audits/2026-10-21-drill-16-19-level45-import/README.md).

Panduan aktif mengikuti kode; arsip menyimpan keputusan pada tanggalnya.

| Kebutuhan | Dokumen |
|---|---|
| Setup dan status bank | [README repo](../readme.md) |
| UI/CLI, paket, tes, troubleshooting | [OPERATIONS](OPERATIONS.md) |
| Config, original, validator, versi | [GENERATOR](GENERATOR.md) |
| Modul, DB, ekspor dan batas integrasi | [ARCHITECTURE](ARCHITECTURE.md) |
| HTTP compute v1, preview dan Simpan draft | [Handoff integrasi](handoffs/NUMORA_GENERATOR_INTEGRATION_V1.md), [prompt pusat](handoffs/NUMORA_CENTRAL_IMPLEMENTATION_PROMPT.md), [bukti tes](audits/generator-service-v1.md) |
| 115 soal tanpa generator: 86 mempunyai stok, 16 HOLD, 13 menunggu generator/stok | [Review soal skip](../variant_gen/soalskip.md) |

## Kondisi repo dan generator

- [Penyelesaian indikator 6–10 level 4–5](audits/2026-10-21-drill-6-10-level45-batch6/README.md): 100/100 soal paket 1 terlayani, 99 generator + 1 konseptual dengan 3 stok. Revisi lokal disetujui pengguna; hasil generate runtime tidak disimpan.

- [Sumber masuk original indikator 20–23, 19 Oktober 2026](sources/incoming/2026-10-19-indikator-20-23/README.md): 200 soal level 1–5 dan 64 tabel; penomoran sumber 1–50 per indikator dipertahankan. Hanya diarsipkan, tanpa analisis atau perubahan bank/generator.

- [Sumber masuk original indikator 16–19, 19 Oktober 2026](sources/incoming/2026-10-19-indikator-16-19/README.md): 200 nomor soal unik/201 kemunculan heading, level 1–5, termasuk 14 gambar; kedua bagian Soal 10 indikator 17 level 2 dipertahankan. Hanya diarsipkan, tanpa analisis atau perubahan bank/generator.

- [Sumber masuk original indikator 11–15, 19 Oktober 2026](sources/incoming/2026-10-19-indikator-11-15/README.md): DOCX dan ekstraksi 250 soal level 1–5; hanya disimpan, belum dianalisis, dipetakan ke bank aktif, atau dibuatkan generator.

- [Sumber masuk original indikator 6–10, 19 Oktober 2026](sources/incoming/2026-10-19-indikator-6-10/README.md): DOCX dan ekstraksi 250 soal level 1–5; hanya disimpan, belum dianalisis, dipetakan ke bank aktif, atau dibuatkan generator.

- [Sumber masuk original indikator 1–5, 19 Oktober 2026](sources/incoming/2026-10-19-indikator-1-5/README.md): DOCX dan ekstraksi 250 soal level 1–5; hanya disimpan, belum dianalisis, dipetakan ke bank aktif, atau dibuatkan generator.

- [Snapshot masukan 679 generator Drill sebelum revisi1–5](audits/2026-10-07-generator-input-audit.md): 1.027 masukan, domain efektif dan kapasitas, versi/hash serta status persetujuan. Empat puluh generator baru tercatat pada audit berikut; penyesuaian otomatis tetap nonaktif. [CSV per masukan](audits/2026-10-07-generator-input-audit.csv).

- [Generator revisi Drill1–5](audits/2026-10-07-revised-1-5-generator-audit.md):40 generator baru; 138/150 aktif,10 konseptual dengan stok,2 HOLD. [Snapshot impor sumber](audits/2026-10-07-drill-1-5-source-revision.md) memuat41 original v2 sebelum aktivasi generator.

- [Stok konseptual lengkap dan cross-check kesulitan](audits/2026-10-06-conceptual-stock-audit.md): 67 original/206 stok VERIFIED; [progres](superpowers/plans/2026-10-06-conceptual-stock-progress.md).

- [Stok konseptual Tryout](audits/2026-10-07-tryout-conceptual-stock-audit.md):3 original/9 stok VERIFIED; total lintas aktivitas70 original/215 stok. Akses per soal UI/CLI; generate paket tetap memakai original.

- [Audit Drill3–5 level1–3](audits/2026-10-06-drill-3-5-generator-audit.md), [progres](superpowers/plans/2026-10-06-drill-3-5-generator-progress.md).

- [Audit Drill1–2 level1–3](audits/2026-10-05-drill-1-2-generator-audit.md), [progres](superpowers/plans/2026-10-05-drill-1-2-generator-progress.md).

- [Kondisi repo dan verifikasi gabungan](audits/2026-10-07-repository-status.md): inventaris 820 original/746 config dan cakupan yang belum tersedia.
- [Generator revisi Drill 6–10](audits/2026-10-07-revised-6-10-generator-audit.md): 11 generator baru, total 140/150 aktif; satu HOLD tetap ditahan.
- [Audit Drill 6–10](audits/2026-10-05-drill-6-10-generator-audit.md), [hasil implementasi](superpowers/plans/2026-10-05-drill-6-10-generator-progress.md).
- [Audit Drill 11–15](audits/2026-10-05-drill-11-15-generator-audit.md), [hasil implementasi](superpowers/plans/2026-10-05-drill-11-15-generator-progress.md), contoh hasil dihapus pada 6 Oktober 2026; audit hash/seed tetap tersedia.

## Arsip dan sumber

Angka stok/snapshot pada audit merupakan evidence run historis, bukan inventaris terkini. Label `PROPOSED` tidak menyatakan fitur sudah tersedia.

- [Audit Drill 4 Oktober](audits/2026-10-04-variant-config-audit.md), [data audit](audits/2026-10-04-variant-config-audit.json).
- [Audit Drill indikator20–23](audits/2026-10-05-drill-20-23-generator-audit.md), [data audit](audits/2026-10-05-drill-20-23-generator-audit.json): 120 sumber, 86 generator aktif, 11 review sumber, 23 template ditunda.
- [Hasil implementasi Drill indikator20–23](superpowers/plans/2026-10-05-drill-20-23-generator-progress.md): verifikasi end-to-end dan keputusan implementasi.
- [Desain Tryout](superpowers/specs/2026-10-04-tryout-variant-generator-design.md), [plan](superpowers/plans/2026-10-04-tryout-variant-generator.md), [hasil](superpowers/plans/2026-10-04-tryout-variant-generator-progress.md).
- [Desain browser DB](superpowers/specs/2026-10-04-database-package-browser-design.md), [plan](superpowers/plans/2026-10-04-database-package-browser.md), [hasil](superpowers/plans/2026-10-04-database-package-browser-progress.md).
- [Rancangan varian dan IRT](../rancangan%20fitur%20soal%20variant%20dan%20irt.pdf): sumber rancangan; IRT belum tersedia dalam kode ini.
- [Source Tryout verbatim](../variant_gen/data/tryout-1/source.docx): dokumen akademik asli. Normalisasi/koreksi runtime tercatat pada metadata/ledger bank.

Saat mengubah perilaku, perbarui panduan aktif yang sesuai. Pertahankan arsip bertanggal; checklist plan tidak menggantikan verifikasi kode atau approval publikasi.

- [Audit generator Drill 11–15](audits/2026-10-05-drill-11-15-generator-audit.md): 223 aktif, oracle matematika, kapasitas dan contoh hasil.

Sejak 6 Oktober 2026, generate tidak menyimpan varian/paket. Catatan regen, history, dan snapshot pada audit/progres sebelumnya bersifat historis. Contoh hasil lama dihapus; bukti matematika berupa hash/seed/status tetap tersedia. Audit revisi 7 Oktober menyertakan fixture contoh offline; generate runtime tetap tidak menyimpan hasil.

- [Revisi sumber Drill20–23,7 Oktober](audits/2026-10-07-drill-20-23-source-revision.md):16 original v2; [generator sudah aktif](audits/2026-10-07-revised-20-23-generator-audit.md).
- [Revisi sumber Drill16–19, 7 Oktober](audits/2026-10-07-drill-16-19-source-revision.md): dua original v2 dari sepuluh soal skip yang diperiksa; DOCX diarsipkan, dua generator v1 kini aktif.
- [Penyelesaian generator indikator 1–5 level 4–5](audits/2026-10-20-drill-1-5-level45-completion/README.md), diverifikasi 21 Oktober: 72 generator lokal dan 28 draf koreksi/generator belum aktif, lengkap dengan perubahan sebelum/sesudah dan bukti pemeriksaan.
