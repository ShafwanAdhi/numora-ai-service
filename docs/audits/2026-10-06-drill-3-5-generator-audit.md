# Audit Drill Paket1 indikator3–5 level1–3

90 original:45 PG,27 MCMA,18 KATEGORI;9 grup. **64 generator aktif,25 HOLD_SOURCE,1 DEFERRED_CONCEPTUAL**.

| Indikator | Aktif | HOLD | Ditunda | Stok unik sampling | Tambahan accepted |
|---|---:|---:|---:|---:|---:|
|3 Pembulatan/estimasi|20|10|0|400|1.000|
|4 Faktorisasi/FPB/KPK|17|13|0|340|850|
|5 Rasio/skala/laju|27|2|1|540|1.350|
|Total|64|25|1|1.280|3.200|

[Audit gabungan per soal/hash/domain/seed/rejections](2026-10-06-drill-3-5-generator-audit.json); contoh hasil dihapus pada 6 Oktober 2026; audit hash/seed tetap tersedia. Indikator4 tidak memiliki KATEGORI aktif setelah review; contoh mencakup format yang tersedia. [Semua26 skipped beserta alasan](../../variant_gen/soalskip.md). Audit domain lebih rinci: [3](2026-10-06-drill-indicator3-audit.json), [4](2026-10-06-drill-indicator4-audit.json), [5](2026-10-06-drill-indicator5-audit.json).

Raw DOCX SHA256 `f12c25edf8b1e6a4a10daa19cbbe7459624450f619921186d0c75818e6b499c6`; disalin utuh untuk provenance. Runtime hanya level1–3. Metadata menyimpan teks/key/explanation asli. Normalisasi tipografi pecahan/akar/pangkat/uang tidak mengesahkan koreksi akademik atau instruksi rekonstruksi dalam dokumen.

Review memperbaiki oracle echoed weights/radicands, klausa konseptual prima, satuan debit/luas dan domain kategori penjumlahan akar agar pembulatan jumlah sama dengan jumlah pembulatan komponen. Tanggal/jam/KPK, waktu awal tidak dihitung, reduced ratios, skala luas kuadrat, unit prices dan debit diperiksa dari teks rendered. Oracle tidak mengambil jawaban dari evaluator produksi atau config.

Sumber HOLD meliputi diagonal persegi tidak sesuai luas, aturan estimasi/pembulatan tidak tunggal, kunci atau caption bertentangan, serta pembagian/pemotongan yang tidak menetapkan asumsi maksimum/terpanjang. `pg-5-2-4` ditunda: alasan total harga paket tidak membuktikan harga per unit; profil alternatif unit setara juga membuat dua opsi PG benar. Original tetap terlihat dengan status/reason, generator/editor ditolak.

<!-- ponytail: bounded domains only; extend independent parameters when unique stock exhausted, then audit. -->
Domain bounded.20 unique per soal adalah stok sampling;3.200 accepted tambahan boleh mengulang di seed berbeda, bukan3.200 stok tambahan unik. Config bukan approval kurikulum/kalibrasi IRT. Tidak membuat level4–5 untuk indikator1–5, tidak menulis DB atau repoNumora.

```powershell
python -B variant_gen/tests/audit_drill_3_5.py --output docs/audits/2026-10-06-drill-3-5-generator-audit.json
python -B -m unittest discover -s variant_gen/tests -v
```

UI/CLI lifecycle diuji dengan store sementara/DB mock. Browser filter3–5/level1–3/PG-MCMA-KATEGORI/idempotent/HOLD lulus. Hasil suite final/review dan hash preservation pada [progres](../superpowers/plans/2026-10-06-drill-3-5-generator-progress.md).
