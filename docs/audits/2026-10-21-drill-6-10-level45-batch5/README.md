# Generator indikator 6–10, level 4–5: tahap 5

7 generator ditambahkan pada tahap ini; total 82/100 soal diaktifkan.
Sumber dan pembahasan original dipertahankan; katalog Drill paket 1 memakai nomor asli.
18 soal tersisa tercatat dalam pending.csv; temuan akademik tetap memerlukan tindak lanjut.

Seluruh domain parameter diperiksa oleh oracle matematika dari teks hasil render.
Reproduksi original, variasi unik, seed deterministik, serta workbench tanpa DB/penyimpanan diuji.
Audit hanya menyimpan ringkasan pemeriksaan dan hash, tanpa konten soal varian.

Rentang belum disetujui kurikulum atau dikalibrasi IRT; self-adjustment tetap nonaktif.
Panggilan Generate dapat diulang; domain numerik tiap konfigurasi tetap terbatas.

Jalankan dari root repo:
```
python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch5.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch5.py
```

| Soal | Varian unik valid |
| --- | ---: |
| pg-6-4-1 | 30 |
| pg-6-5-1 | 30 |
| pg-6-5-3 | 30 |
| pg-7-4-3 | 30 |
| pg-7-5-5 | 30 |
| pg-9-5-2 | 30 |
| mcma-10-4-7 | 30 |


## Koreksi kunci yang pasti

Tujuh kunci dikoreksi dengan stimulus dan opsi sumber tetap identik.
Pembahasan original yang keliru tetap tersedia verbatim dalam metadata;
pembahasan varian dihitung ulang. Sumber DOCX dan audit historis tidak diubah.
Status tetap NOT_CURRICULUM_APPROVED.

Sisa 18: 17 menunggu keputusan revisi sumber dan 1 konseptual menunggu keputusan stok.
Lihat [usulan revisi per soal](../2026-10-21-drill-6-10-level45-batch5-source-proposal.md).
