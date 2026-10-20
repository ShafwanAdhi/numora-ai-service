# Indikator 6–10 level 4–5: penyelesaian

Seluruh 100 soal Drill paket 1 terlayani: 99 generator dan 1 soal konseptual dengan 3 stok berulang.
Tahap ini menambah 17 generator serta stok `mcma-7-5-6`. Tidak ada soal antrean.
Generator dan stok tersedia pada katalog service, CLI, serta workbench lokal.

Revisi lokal minimum disetujui pengguna. Sumber mentah, pembahasan sumber, temuan audit,
dan perubahan sebelum/sesudah tersedia dalam metadata serta `source-review.json`.
Original lokal menampilkan naskah dan pembahasan revisi yang konsisten; DOCX/audit historis tidak diubah.

Semua 527 kombinasi input diperiksa dari teks hasil render; tiap generator mempunyai 30 varian unik valid.
Nilai original direproduksi pada k=0; nilai tersebut ditolak sebagai varian oleh validator yang sama.
Tiga stok konseptual diperiksa melalui derajat dan jumlah variabel persamaan.
Stok ini adalah inventaris editorial yang ditulis offline; hasil generate runtime tidak disimpan.
Stok dapat dipilih kembali tanpa penghitung pemakaian atau perubahan database.

Rentang belum dikalibrasi IRT atau disetujui kurikulum; self-adjustment tetap nonaktif.

## Batas verifikasi repo

Suite service API masih mempunyai satu kegagalan di luar cakupan batch ini:
`test_level45_local_generators_are_visible_but_review_drafts_are_not` merujuk
`variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch2/q0_bank.csv` yang belum tersedia.
Berkas/implementasi indikator 1–5 tersebut tidak diubah oleh pekerjaan ini.

```powershell
python -B variant_gen/tests/build_drill_6_10_level45_batch6.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch6.py
python -B -m unittest discover -s variant_gen/tests -p 'test_drill_6_10_level45_batch*.py'
```

| Indikator | Generator level 4–5 | Soal dengan stok |
|---|---:|---:|
| 6 | 20 | 0 |
| 7 | 19 | 1 |
| 8 | 20 | 0 |
| 9 | 20 | 0 |
| 10 | 20 | 0 |

## Kapasitas generator tahap ini

| Soal | Varian unik valid |
|---|---:|
| pg-6-4-2 | 30 |
| pg-6-4-4 | 30 |
| mcma-6-4-8 | 30 |
| kategori-6-4-10 | 30 |
| pg-6-5-2 | 30 |
| pg-6-5-4 | 30 |
| mcma-6-5-8 | 30 |
| kategori-6-5-10 | 30 |
| pg-7-4-4 | 30 |
| mcma-7-5-8 | 30 |
| kategori-7-5-9 | 30 |
| pg-9-4-1 | 30 |
| pg-9-5-1 | 30 |
| pg-9-5-5 | 30 |
| mcma-9-5-7 | 30 |
| pg-10-4-2 | 30 |
| kategori-10-5-9 | 30 |
