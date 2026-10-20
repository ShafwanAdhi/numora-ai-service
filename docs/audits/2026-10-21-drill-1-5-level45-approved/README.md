# Aktivasi 28 koreksi indikator 1–5 level 4–5

**ENGINEERING DECISION — persetujuan pengguna, 21 Oktober 2026:** “aku setuju dengan koreksinya, masukkan dan buat generatornya”. Persetujuan ini diterapkan pada 28 koreksi yang sudah disiapkan dan aktivasi generator lokalnya.

28 original hasil koreksi dan generatornya kini tersedia pada bank default. **Indikator 1–5 menjadi 250 original; seluruh 100 soal level 4–5 memiliki generator.** Semua berada pada `DRILL / drill-1`, dengan indikator, level dan nomor sumber asli. Setiap kelompok level 4–5 berisi nomor 1–10 secara berurutan.

| Indikator | Koreksi/generator yang diaktifkan |
|---|---:|
| 1 | 4 |
| 2 | 8 |
| 3 | 3 |
| 4 | 9 |
| 5 | 4 |
| **Total** | **28** |

## Versi dan sumber

- Bank runtime tambahan: `variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/`.
- Original tetap **v2** dan config tetap **v1**, sesuai usulan yang direview. CSV, katalog dan config disalin byte-identik; stimulus, opsi, kunci, isi matematis pembahasan dan batas parameter tidak diubah ketika diaktifkan.
- Metadata runtime menjadi `ACTIVE`, `review_only=false`, `USER_APPROVED_CORRECTION`. Catatan persetujuan menyimpan instruksi pengguna, ruang lingkup, 28 ID dan hash config/usulan koreksi.
- Label editorial seperti “draft koreksi” dibersihkan dari judul pembahasan dan catatan tampilan aktif. Isi perhitungan tetap sama; teks pembahasan yang direview tetap utuh di arsip dan hash-nya dicatat pada metadata runtime. Caption/catatan aktif memakai nama field persetujuan, bukan field usulan.
- Arsip `variant_gen/drafts/2026-10-20-level45-academic/` tetap utuh, termasuk status historis `HOLD_SOURCE`. Arsip ini bukan bank runtime. Teks asli v1, perubahan sebelum/sesudah dan alasan koreksi tetap dapat ditelusuri.
- 1.332 aset sebelumnya diverifikasi tidak berubah. Manifest dibuat sebelum aktivasi dan terpisah dari laporan hasil. Aset kelompok indikator lain dipertahankan.

Generator untuk 28 soal ini sudah ada sebelum persetujuan; aktivasi menggunakan config yang sama. Tidak mengganti config generator lama dan tidak memperluas rentang. Domain masing-masing tetap `k=0..24`, dengan 24 varian efektif setelah penyaringan.

## Verifikasi

- Seluruh 28 original cocok dengan usulan yang disetujui, termasuk versi dan hash; seluruh config runtime cocok byte-identik dengan config draf.
- Pemeriksaan seluruh 700 masukan parameter menghitung jawaban melalui oracle independen. 560 sampel unik diperiksa melalui jalur generate runtime.
- 26 tes fokus generator/integrasi lulus, termasuk akses HTTP untuk 28 generator yang sebelumnya tertahan.
- 7 tes registrasi/isolation workspace lulus.
- 14 tes service lulus; 11 tes PostgreSQL dilewati karena cluster uji tidak dijalankan. Tidak ada perubahan database pada pekerjaan ini.
- Penggabungan katalog diverifikasi menghasilkan 250 original indikator 1–5 dan sepuluh kelompok level 4–5 dengan masing-masing sepuluh soal.

Total indikator 1–5: **238 generator, 10 original konseptual dengan stok manual, dan 2 HOLD lama pada level 1–3**. Kedua HOLD lama tersebut tidak termasuk 28 koreksi yang disetujui.

## Batas persetujuan

Persetujuan pengguna dicatat untuk **koreksi sumber dan penggunaan generator lokal**. Ini tidak menyatakan persetujuan institusional Kurikulum, kalibrasi IRT, kesetaraan kesulitan, atau publikasi database. `self_adjustment_enabled=false` tetap dipertahankan.

Laporan 20 Oktober tetap merekam kondisi historis sebelum persetujuan. Pemeriksaan kondisi aktif setelah persetujuan memakai tes dan catatan aktivasi ini.

## Berkas dan pemakaian

- [Catatan aktivasi, ID, versi dan hash](activation.json)
- [Hasil tes, review dan hash aset aktif](verification.json)
- [Manifest aset sebelum aktivasi](prior-assets-baseline.json)
- [Catatan persetujuan dalam bank](../../../variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/approval.json)
- [Usulan koreksi yang disetujui](../../../variant_gen/drafts/2026-10-20-level45-academic/proposed_corrections.json)

```powershell
python -B variant_gen/cli.py gen pg-1-4-1 s1
python -B -m unittest discover -s variant_gen/tests -p "test_level45*.py" -v
python -B -m unittest discover -s variant_gen/tests -k workspace -v
python -B -m unittest discover -s tests/service -v
```

Restart proses workbench/service lokal yang sudah berjalan agar memuat bank/config tambahan. Revisi berikutnya terhadap isi yang sudah digunakan harus membuat versi baru. Script `activate_level45_approved.py` menolak penimpaan berkas versi existing yang berbeda.
