# Dokumentasi Numora AI Service

Panduan aktif mengikuti kode; arsip menyimpan keputusan pada tanggalnya.

| Kebutuhan | Dokumen |
|---|---|
| Setup dan status bank | [README repo](../readme.md) |
| UI/CLI, paket, tes, troubleshooting | [OPERATIONS](OPERATIONS.md) |
| Config, original, validator, versi | [GENERATOR](GENERATOR.md) |
| Modul, DB, ekspor dan batas integrasi | [ARCHITECTURE](ARCHITECTURE.md) |
| 95 soal tanpa generator (92 Drill + 3 Tryout) | [Review soal skip](../variant_gen/soalskip.md) |

## Kondisi repo dan generator

- [Kondisi repo dan verifikasi gabungan](audits/2026-10-05-repository-status.md): inventaris 670 original/575 config dan cakupan yang belum tersedia.
- [Audit Drill 6–10](audits/2026-10-05-drill-6-10-generator-audit.md), [hasil implementasi](superpowers/plans/2026-10-05-drill-6-10-generator-progress.md).
- [Audit Drill 11–15](audits/2026-10-05-drill-11-15-generator-audit.md), [hasil implementasi](superpowers/plans/2026-10-05-drill-11-15-generator-progress.md), [contoh hasil](../variant_gen/data/drill-1-indicators-11-15/examples.json).

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
