# Audit generator revisi indikator20-23 - 7 Oktober 2026

Seluruh16 original revisi kurikulum kini memiliki config v1 yang dipin ke hash original v2. Metadata ACTIVE / IMPLEMENTED, dengan source_review_status REVISED_CURRICULUM. Bank20-23 memiliki102 generator dari120 original;18 soal lain tetap tersedia melalui stok konseptual manual.

Implementasi mengikuti engine deterministik/config JSON existing. CSV, ledger revisi, DOCX, config existing, stok dan snapshot lama dipertahankan. Generate runtime stateless, tanpa penyimpanan hasil atau akses database. Fixture contoh audit disimpan terpisah.

[DOCX revisi](../../variant_gen/data/drill-1-indicators-20-23/source-revision-2026-10-07.docx) SHA256 `1edd91abfc4e9a2ad1143cc578d0df8da54becd711b8e0cdb1dc8dc1543608e9`. [Audit impor](2026-10-07-drill-20-23-source-revision.md) mencatat keputusan transkripsi. Semua original_values mereproduksi stem, opsi dan kunci sumber v2.

## Parameter generator

| Generator | Parameter bebas |
|---|---|
| pg-20-3-3, pg-21-2-2, pg-21-3-4 | Pergeseran t=-50..10; rata-rata, nilai tambahan dan distractor dihitung bersama. Sumber pg-20-3-3 memang memakai nilai tambahan110, sehingga domain tidak memakai batas nilai sekolah100. |
| pg-21-3-1 | Jumlah siswa3..25, mean40..85, kenaikan1..3; nilai tambahan maksimum100. |
| mcma-21-3-8 | Pergeseran t=-30..20. |
| kategori-21-3-9 | Pergeseran t=-40..10. |
| pg-21-3-5, pg-22-1-1, mcma-22-1-6, mcma-22-1-7, mcma-22-3-8 | case0..7 dan t=-20..20; dua dataset lima nilai, setiap nilai0..100. Case0 mereproduksi sumber; tujuh profil varian mengubah hubungan statistik. |
| pg-23-3-2, mcma-23-3-7 | Percobaan100..1500 kelipatan100, frekuensi perseratus bukan0,5. pg-23-3-2 membatasi frekuensi minimum0,06. |
| mcma-23-3-8 | Percobaan100..1500 kelipatan100, frekuensi perseribu bukan0,5; jumlah kejadian wajib bulat. |
| kategori-23-3-9 | Percobaan100..1500 kelipatan100, frekuensi0,01..0,49. |
| pg-23-3-5 | Percobaan30..900 kelipatan30; profil2/15 atau1/5. Profil sumber2/15 ditolak saat generate oleh same_answer_as_original. Domain efektif30 varian unik. |

Parameter derived menghitung stimulus, opsi benar/salah dan pembahasan secara bersamaan. Fakta peluang teoretis tetap konstanta. Jumlah jawaban benar MCMA/Kategori mengikuti original. Seed berbeda tidak menjamin varian unik. Aturan existing menolak teks jawaban benar yang sama dengan original dan duplikat jika others diberikan; API/CLI tidak menyimpan others lintas request.

## Verifikasi

- TDD: pengujian16 config awalnya gagal karena generator belum tersedia, kemudian lulus setelah implementasi.
- Audit20 varian unik per ID:320 kandidat,1600 pemeriksaan seed tambahan,16 PASS / 0 FAIL. Oracle memakai teks hasil render, Fraction dan statistik tanpa membaca formula config.
- Tes memeriksa reproduksi original, determinisme, batas parameter, seluruh profil perbandingan dan ambang frekuensi.
- Reviewer independen memeriksa8000 kandidat; tidak menemukan masalah Critical, Important atau Minor yang bermakna.
- Suite gabungan: `python -B -m unittest discover -s variant_gen/tests -v`,147 tes,82,736 detik,OK. Termasuk dua generator indikator17 yang masuk di luar lingkup pekerjaan ini.
- Playwright memilih dan Generate seluruh16 ID; original v2/config v1 terlihat. HTTP test memeriksa matematika respons, seed berulang dan ketiadaan penulisan storage/akses DB.
- Hash715 baseline asset diperiksa. Perubahan dalam lingkup ini hanya metadata bank20-23. Metadata bank dasar berubah oleh aktivasi dua generator indikator17; tidak ada baseline hilang.

[Audit JSON](../../variant_gen/data/drill-1-indicators-20-23/revision-generator-audit.json) memuat hash original/config, domain parameter, seed dan draw per ID. [16 contoh hasil](../../variant_gen/data/drill-1-indicators-20-23/revision-generator-examples.json) disimpan sebagai fixture offline.

```powershell
python -B variant_gen/tests/audit_drill_20_23_revisions.py --output .scratch/revision-audit/report.json
```

Validasi matematika ini belum membuktikan kesetaraan psikometrik/IRT. Perubahan lokal belum di-commit/push.
