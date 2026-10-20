# Generator indikator 6–10, level 4–5: tahap 2

20 generator ditambahkan pada tahap ini; total 40/100 soal diaktifkan.
Sumber dan pembahasan original dipertahankan; katalog Drill paket 1 memakai nomor asli.
60 soal tersisa tercatat dalam pending.csv; temuan akademik tetap memerlukan tindak lanjut.

Seluruh domain parameter diperiksa oleh oracle matematika dari teks hasil render.
Reproduksi original, variasi unik, seed deterministik, serta workbench tanpa DB/penyimpanan diuji.
Audit hanya menyimpan ringkasan pemeriksaan dan hash, tanpa konten soal varian.

Rentang belum disetujui kurikulum atau dikalibrasi IRT; self-adjustment tetap nonaktif.
Panggilan Generate dapat diulang; domain numerik tiap konfigurasi tetap terbatas.

Jalankan dari root repo:
```
python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch2.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch2.py
```

| Soal | Varian unik valid |
| --- | ---: |
| pg-6-4-5 | 30 |
| mcma-6-4-7 | 30 |
| pg-7-4-1 | 30 |
| pg-7-4-5 | 30 |
| mcma-7-4-7 | 30 |
| mcma-7-4-8 | 30 |
| pg-7-5-1 | 30 |
| pg-7-5-4 | 30 |
| pg-8-4-2 | 30 |
| pg-8-4-3 | 30 |
| pg-8-5-1 | 30 |
| mcma-8-5-7 | 30 |
| pg-9-4-5 | 30 |
| mcma-9-4-6 | 30 |
| mcma-9-4-7 | 30 |
| kategori-9-5-9 | 30 |
| pg-10-4-5 | 30 |
| mcma-10-4-8 | 30 |
| pg-10-5-3 | 30 |
| mcma-10-5-8 | 30 |
