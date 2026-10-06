# Generator dan stok varian Numora

Workspace default:820 original,746 config,70 original dengan215 stok konseptual manual VERIFIED: Drill67/206 dan Tryout3/9. Stok maksimum empat per original, saat ini2–4. Tiga soal Tryout tersedia melalui stok per soal; generate paket tetap memakai original. Komputasi IRT belum diimplementasikan.

Panduan aktif:

- [Setup dan status bank](../readme.md)
- [UI/CLI, generator dan stok](../docs/OPERATIONS.md)
- [Config, provenance dan validator](../docs/GENERATOR.md)
- [Arsitektur dan database](../docs/ARCHITECTURE.md)
- [Audit variasi dan kesulitan](../docs/audits/2026-10-06-conceptual-stock-audit.md)
- [Soal tanpa generator dan jumlah stok](soalskip.md)

Dari root repo:

```powershell
python -B variant_gen/webui.py
python -B variant_gen/cli.py gen pg-6-1-1 s1 --json
python -B variant_gen/cli.py stock pg-16-1-1 --variant 2 --json
```

Dari folder variant_gen, gunakan webui.py atau cli.py tanpa awalan folder. Generator numerik tidak menyimpan hasil. Stok adalah asset JSON offline; membaca ulang tidak mengurangi persediaan. Restart UI setelah asset berubah. Tidak ada Regen/riwayat, penulisan stok lewat API, atau upload ke database.
