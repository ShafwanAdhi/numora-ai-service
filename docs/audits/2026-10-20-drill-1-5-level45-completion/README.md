# Penyelesaian generator indikator 1-5 level 4-5

Dilanjutkan dan diverifikasi 21 Oktober 2026; nama folder mempertahankan tanggal awal pekerjaan.

**ENGINEERING DECISION - instruksi pengguna:** selesaikan 67 soal setelah tahap pertama 33 soal. Untuk 28 soal dengan temuan akademik, siapkan usulan koreksi dan generator terpisah untuk review; belum aktif.

**Cakupan 100 keluarga: 72 generator lokal dan 28 generator draf terkarantina.** Tahap ini menambah 39 generator lokal dan 28 draf. Tidak ada publikasi atau perubahan database.

| Indikator | Generator lokal baru | Generator draf |
|---|---:|---:|
| 1 | 9 | 4 |
| 2 | 5 | 8 |
| 3 | 10 | 3 |
| 4 | 5 | 9 |
| 5 | 10 | 4 |

## Pemisahan dan versi

- Bank tambahan lokal: `variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch2/`. 39 original v1 memakai config v1. Posisi tetap `DRILL / drill-1 / indikator / level / nomor sumber`; katalog tahap pertama dan kedua digabung berdasarkan kelompok yang sama, lalu diurutkan menurut nomor sumber.
- Draf: `variant_gen/drafts/2026-10-20-level45-academic/`. 28 usulan original v2 dan config v1 tidak dimuat oleh bank atau config default. `HOLD_SOURCE`, `review_only=true`, `approval_status=PROPOSED_NOT_APPROVED`; generate langsung tetap ditolak. Audit memakai salinan sementara di memori untuk memeriksa matematikanya.
- `proposed_corrections.json` menyimpan isi sumber v1, isi usulan v2, perubahan setiap komponen, temuan audit awal dan alasan koreksi. Ini usulan review, bukan revisi Kurikulum yang telah disetujui.
- 33 original/config tahap pertama dan aset pekerjaan indikator 6-10 yang sudah ada dipertahankan. Angka pada laporan tahap pertama adalah snapshot historis. Tiga aset bank indikator 11-15/stok dan kode terkait berubah oleh pekerjaan lain selama jeda; manifest resume mencatat hash sebelum/sesudahnya. Klaim hash tetap sama berlaku sejak snapshot resume ini.

## Bukti verifikasi

- 1675 kombinasi parameter diperiksa menyeluruh, termasuk nilai original. Oracle terpisah menghitung dari teks soal yang sudah dirender; tidak membaca nilai tersembunyi generator.
- Kapasitas efektif gabungan keluarga baru: 1608 varian; minimum 24 per keluarga. Setiap keluarga memiliki sedikitnya 20 masukan matematis berbeda di bagian inti stimulus. Label tambahan tidak dihitung sebagai perubahan matematika.
- 1340 sampel unik (20 per keluarga) dan 3350 sampel seed 201-250 diperiksa; pemanggilan ulang seed yang sama harus identik.
- Hash 1203 aset sebelumnya tetap sama. Baseline, hash sumber, original/config, rentang deklaratif dan efektif, penolakan serta contoh tersedia dalam JSON.
- Tes meliputi reproduksi original, mutasi kunci dan pembahasan, penggabungan paket, urutan sumber, serta pemisahan draf dari katalog dan generate workbench tanpa database/penyimpanan hasil.

## Batas persetujuan

**PROPOSED:** seluruh rentang dan keluarga varian baru belum mendapat persetujuan Kurikulum atau kalibrasi IRT. Generator lokal memakai `NOT_CURRICULUM_APPROVED`; draf memakai `PROPOSED_NOT_APPROVED`. `self_adjustment_enabled=false`. Tidak memperluas batas generator lama secara otomatis. Perubahan angka maupun penerapan konsep dapat mengubah beban pengerjaan; label level sumber bukan bukti kesetaraan kesulitan.

## Berkas review dan reproduksi

- [JSON lengkap, hash, rentang dan contoh](audit.json)
- [Semua 67 keluarga](entries.csv)
- [39 generator lokal baru](local-generators.csv)
- [28 generator draf](academic-drafts.csv)
- [Ringkasan perubahan dan alasan koreksi](correction-review.csv)
- [Usulan koreksi sebelum/sesudah](../../../variant_gen/drafts/2026-10-20-level45-academic/proposed_corrections.json)

```powershell
python -B variant_gen/tests/build_level45_completion.py
python -B variant_gen/tests/audit_level45_completion.py
python -B -m unittest discover -s variant_gen/tests -p "test_level45*.py" -v
python -B -m unittest discover -s variant_gen/tests -v
python -B -m unittest discover -s tests/service -v
```

Builder adalah penyusunan aset offline yang belum dirilis. Jangan menjalankannya untuk menimpa versi yang sudah digunakan; revisi berikutnya harus membuat versi baru. Audit membaca manifest masukan `resume-2026-10-21-baseline.json` yang dibekukan sebelum build; tidak memakai `.scratch` atau keluarannya sendiri sebagai baseline.
