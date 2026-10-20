# Generator indikator 6–10, level 4–5: tahap 1

20/100 soal diaktifkan: tiap indikator mendapat dua soal level 4 dan dua soal level 5.
Sumber dan pembahasan original dipertahankan; katalog Drill paket 1 memakai nomor asli.
80 soal tersisa tercatat dalam pending.csv; temuan akademik tetap memerlukan tindak lanjut.

Seluruh domain parameter diperiksa oleh oracle matematika dari teks hasil render.
Reproduksi original, variasi unik, seed deterministik, serta workbench tanpa DB/penyimpanan diuji.
Audit hanya menyimpan ringkasan pemeriksaan dan hash, tanpa konten soal varian.

Rentang belum disetujui kurikulum atau dikalibrasi IRT; self-adjustment tetap nonaktif.
Panggilan Generate dapat diulang; domain numerik tiap konfigurasi tetap terbatas.

Jalankan dari root repo:
```
python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch1.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch1.py
```
