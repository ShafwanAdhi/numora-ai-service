# Audit Drill Paket1 indikator1–2, level1–3

60 original:30 PG,18 MCMA,12 KATEGORI. **34 ACTIVE,17 HOLD_SOURCE,9 DEFERRED_CONCEPTUAL**. Indikator1:18 aktif; indikator2:16 aktif. Semua skipped beserta alasan dan syarat aktivasi: [soalskip](../../variant_gen/soalskip.md).

34 config mereproduksi original; masing-masing mencapai20 variant unik (680 hasil). Seed tambahan201–250 menghasilkan1.700 hasil accepted, semua opsi diperiksa oracle matematika independen. [Data per soal/hash/seed/domain/rejections](2026-10-05-drill-1-2-generator-audit.json); contoh hasil dihapus pada 6 Oktober 2026; audit hash/seed tetap tersedia.

Sumber SHA256 `f12c25edf8b1e6a4a10daa19cbbe7459624450f619921186d0c75818e6b499c6`. DOCX diarsipkan utuh, source_text/declared_key/pembahasan asli disimpan. Normalisasi tipografi tidak mengesahkan rekonstruksi akademik. Beberapa PG memiliki beberapa opsi benar, opsi duplikat, hasil tidak tersedia atau caption kunci bertentangan; tetap HOLD. Klaim konseptual universal dengan jawaban tetap ditunda.

<!-- ponytail: domain generator terbatas; perluas parameter independen ketika stok unik operasional habis, lalu audit ulang. -->
Domain parameter bounded (lihat range/step per soal pada JSON); hasil20 unik merupakan stok sampling, bukan jaminan stok tanpa batas. Pembahasan dan variasi belum merupakan approval kurikulum atau kalibrasi IRT. Indikator3–5 belum runtime; tidak membuat level4–5 untuk1–5.

Reproduksi audit:

```powershell
python -B variant_gen/tests/audit_drill_1_2.py --output docs/audits/2026-10-05-drill-1-2-generator-audit.json
python -B -m unittest discover -s variant_gen/tests -v
```

Pemeriksaan seluruh domain setelah review:1.012 kandidat constraint-valid lolos oracle opsi dan pembahasan yang diperiksa. Mutation tests menolak ekspresi produk, ekuivalensi model, formula yang diklaim tetap sama, dan pembahasan numerik yang sengaja dirusak.

CLI/UI menggunakan engine existing dan snapshot lokal. Generator tidak mengakses DB. Verifikasi akhir dicatat pada [progres](../superpowers/plans/2026-10-05-drill-1-2-generator-progress.md).
