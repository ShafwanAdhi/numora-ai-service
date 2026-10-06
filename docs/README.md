# Dokumentasi Numora AI Service

Panduan aktif mengikuti kode; arsip menyimpan keputusan pada tanggalnya.

| Kebutuhan | Dokumen |
|---|---|
| Setup dan status bank | [README repo](../readme.md) |
| UI/CLI, paket, tes, troubleshooting | [OPERATIONS](OPERATIONS.md) |
| Config, original, validator, versi | [GENERATOR](GENERATOR.md) |
| Modul, DB, ekspor dan batas integrasi | [ARCHITECTURE](ARCHITECTURE.md) |
| 74 soal tanpa generator; 70 mempunyai stok, 4 HOLD | [Review soal skip](../variant_gen/soalskip.md) |

## Kondisi repo dan generator

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
