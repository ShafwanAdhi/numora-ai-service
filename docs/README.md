# Dokumentasi Numora AI Service

Panduan aktif mengikuti kode; arsip menyimpan keputusan pada tanggalnya.

| Kebutuhan | Dokumen |
|---|---|
| Setup dan status bank | [README repo](../readme.md) |
| UI/CLI, paket, tes, troubleshooting | [OPERATIONS](OPERATIONS.md) |
| Config, original, validator, versi | [GENERATOR](GENERATOR.md) |
| Modul, DB, ekspor dan batas integrasi | [ARCHITECTURE](ARCHITECTURE.md) |
| Sepuluh Drill tanpa generator | [Review soal skip](../variant_gen/soalskip.md) |

## Arsip dan sumber

Angka stok/snapshot pada audit merupakan evidence run historis, bukan inventaris terkini. Label `PROPOSED` tidak menyatakan fitur sudah tersedia.

- [Audit Drill 4 Oktober](audits/2026-10-04-variant-config-audit.md), [data audit](audits/2026-10-04-variant-config-audit.json).
- [Desain Tryout](superpowers/specs/2026-10-04-tryout-variant-generator-design.md), [plan](superpowers/plans/2026-10-04-tryout-variant-generator.md), [hasil](superpowers/plans/2026-10-04-tryout-variant-generator-progress.md).
- [Desain browser DB](superpowers/specs/2026-10-04-database-package-browser-design.md), [plan](superpowers/plans/2026-10-04-database-package-browser.md), [hasil](superpowers/plans/2026-10-04-database-package-browser-progress.md).
- [Rancangan varian dan IRT](../rancangan%20fitur%20soal%20variant%20dan%20irt.pdf): sumber rancangan; IRT belum tersedia dalam kode ini.
- [Source Tryout verbatim](../variant_gen/data/tryout-1/source.docx): dokumen akademik asli. Normalisasi/koreksi runtime tercatat pada metadata/ledger bank.

Saat mengubah perilaku, perbarui panduan aktif yang sesuai. Pertahankan arsip bertanggal; checklist plan tidak menggantikan verifikasi kode atau approval publikasi.
