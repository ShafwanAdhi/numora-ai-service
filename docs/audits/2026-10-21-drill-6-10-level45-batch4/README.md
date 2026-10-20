# Generator indikator 6–10, level 4–5: tahap 4

25 generator ditambahkan pada tahap ini; total 75/100 soal diaktifkan.
Sumber dan pembahasan original dipertahankan; katalog Drill paket 1 memakai nomor asli.
25 soal tersisa tercatat dalam pending.csv; temuan akademik tetap memerlukan tindak lanjut.

Seluruh domain parameter diperiksa oleh oracle matematika dari teks hasil render.
Reproduksi original, variasi unik, seed deterministik, serta workbench tanpa DB/penyimpanan diuji.
Audit hanya menyimpan ringkasan pemeriksaan dan hash, tanpa konten soal varian.

Rentang belum disetujui kurikulum atau dikalibrasi IRT; self-adjustment tetap nonaktif.
Panggilan Generate dapat diulang; domain numerik tiap konfigurasi tetap terbatas.

Jalankan dari root repo:
```
python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch4.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch4.py
```

| Soal | Varian unik valid |
| --- | ---: |
| kategori-6-4-9 | 30 |
| mcma-6-5-7 | 30 |
| kategori-6-5-9 | 30 |
| mcma-7-4-6 | 30 |
| kategori-7-4-10 | 30 |
| kategori-7-5-10 | 30 |
| pg-8-4-4 | 30 |
| mcma-8-4-6 | 30 |
| kategori-8-4-10 | 30 |
| pg-8-5-4 | 30 |
| mcma-8-5-6 | 30 |
| pg-9-4-3 | 30 |
| pg-9-4-4 | 30 |
| mcma-9-4-8 | 30 |
| pg-9-5-3 | 30 |
| pg-9-5-4 | 30 |
| kategori-9-5-10 | 30 |
| pg-10-4-1 | 30 |
| pg-10-4-4 | 30 |
| kategori-10-4-9 | 30 |
| kategori-10-4-10 | 30 |
| pg-10-5-2 | 30 |
| pg-10-5-4 | 30 |
| mcma-10-5-7 | 30 |
| kategori-10-5-10 | 30 |


## Tinjauan sumber tahap ini

Seluruh stimulus dan kunci terpilih berstatus VALID/CORRECT pada audit akademik.
Temuan pembahasan, domain, presisi, atau proyeksi dicatat dalam source-review.json.
Deklarasi kunci yang bocor ke stimulus dihapus pada bank baru; teks proyeksi mentah
dan pembahasan original tetap tersimpan verbatim dalam metadata. Pembahasan varian
memperbaiki perhitungan atau alasan yang ditemukan keliru. Sumber DOCX tidak diubah.

Untuk opsi kualitatif, sebagian varian menambahkan hasil perhitungan pendukung agar
jawaban memuat variasi matematis yang dapat diuji. Original tetap direproduksi persis
pada nilai original setelah normalisasi batas komponen di atas. Aturan engine tidak dilonggarkan.
