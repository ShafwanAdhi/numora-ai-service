# Penyelesaian indikator 16-19 level 4-5 - 21 Oktober 2026

Sisa **53 dari 80 original** selesai: **38 generator numerik + 15 konseptual dengan 30 stok editorial**. Bersama 27 generator tahap pertama, seluruh 80 original terlayani: **65 generator, 15 konseptual/30 stok, 0 HOLD**.

## Cakupan keseluruhan indikator 16-19

| Indikator | Original | Generator | Konseptual | Stok editorial |
|---|---:|---:|---:|---:|
| 16 | 50 | 33 | 17 | 38 |
| 17 | 50 | 46 | 4 | 10 |
| 18 | 50 | 50 | 0 | 0 |
| 19 | 50 | 48 | 2 | 4 |
| Total | 200 | 177 | 23 | 52 |

Struktur tetap Drill > Paket 1 (`drill-1`) > indikator > level > soal. Tiap indikator mempunyai lima level, masing-masing sepuluh original. Config v1 memakai engine yang sudah ada; tidak ada dependensi baru.

## Revisi lokal sumber

14 original HOLD direvisi v1 menjadi v2 lewat `variant_gen/data/drill-1-indicators-16-19-levels-4-5/original_revisions.jsonl`. CSV dan DOCX mentah tidak diubah. Ledger menyimpan baris dan metadata sebelum/sesudah, alasan, versi dan hash sumber. Audit impor lama tetap snapshot historis.

| ID | Koreksi lokal |
|---|---|
| pg-16-4-1 | Gambar tabung utuh diganti uraian net; ukuran tetap. |
| pg-16-4-3 | Gambar kerucut utuh dihilangkan; uraian ukuran menjadi sumber soal. |
| pg-16-4-4 | Diagram bertentangan diganti teks sisi alas 12 cm, tinggi segitiga 10 cm; mengikuti pembahasan dan kunci 384 cm2. |
| mcma-16-4-6 | Bedakan net empat segitiga dan bangun empat titik sudut; kunci ABD diperbaiki menjadi ABC. |
| mcma-16-4-7 | Gambar utuh diganti uraian net tabung tertutup. |
| kategori-16-4-9 | Tepat n segitiga dinyatakan sebagai sisi tegak, karena alas juga segitiga saat n=3. |
| pg-16-5-1 | Diagram tak berukuran diganti data sambungan eksplisit; rancangan C tetap salah. |
| mcma-17-4-6 | Pembahasan transformasi diperbaiki; stimulus, opsi dan kunci tetap. |
| kategori-17-4-9 | Notasi translasi rusak menjadi T(-2,5); pembahasan diperbaiki. |
| pg-17-5-1 | Meminta seluruh kemungkinan faktor skala agar +/-3 menjadi jawaban tunggal. |
| pg-17-5-3 | Refleksi sumbu Y dinyatakan eksplisit; jenis transformasi tidak ditebak dari satu pasangan titik. |
| kategori-17-5-9 | Notasi opsi diperbaiki menjadi (-2,-2) dan klaim salah (-10,2); hasil dilatasi sebenarnya (-10,4). |
| kategori-17-5-10 | Klaim orientasi ambigu diganti invariansi luas 20 cm2 saat rotasi. |
| kategori-19-5-10 | Tambah tinggi awal >5 cm agar pengurangan tinggi sah. |

Seluruh revisi berstatus `NOT_CURRICULUM_APPROVED`, self-adjustment tidak aktif. `VERIFIED` pada stok berarti pemeriksaan engineering isi/kunci, bukan persetujuan kurikulum atau kalibrasi IRT.

Untuk pg-16-5-3 dan pg-16-5-5, parameter sumber tetap memakai gambar asli; varian memakai data ukuran teks agar label gambar tidak kedaluwarsa. pg-19-5-5 menghitung selisih kapasitas eksak sebelum pembulatan dua desimal, bukan mengalikan angka sumber yang sudah dibulatkan.

## Generator, stok dan penyimpanan

Masing-masing 38 config mempunyai 30 varian unik valid, di luar parameter reproduksi sumber. Rentang eksplisit menjaga validitas; ini bukan jaminan varian unik tak terbatas atau kesulitan setara IRT. Permintaan generate tetap dapat diulang; hasil numerik hanya dikembalikan, tidak disimpan. Domain dapat diperluas setelah audit tambahan.

Stok konseptual merupakan inventaris editorial statis: dua item per original, kunci/pembahasan dan catatan variasi tersedia. Workbench memilih stok melalui `stock_variant`; pemilihan ulang mengembalikan item sama, tanpa menghabiskan stok atau mencatat konsumsi pengguna. Hasil runtime tidak disimpan. Tidak ada perubahan database Numora maupun impor/publikasi ke layanan utama.

## Bukti pemeriksaan

- Seluruh 1.178 input parameter diuji dari stimulus/opsi yang telah dirender; 1.140 varian unik valid. Oracle memeriksa rumus, kunci, klaim opsi dan hasil pembahasan. Mutasi kunci, angka opsi benar, dan hasil pembahasan ditolak.
- API generate seluruh 38 soal lulus. Stok seluruh 15 soal dipilih dengan urutan 1,2,1; pemakaian ulang identik, indeks 3 ditolak. Database dipasang mock yang menolak akses; tidak ada berkas hasil runtime.
- 49 tes lulus: completion (3), batch1 (2), impor (3), stok konseptual (10), revisi11-15 (3), katalog (2), coverage (9), webui (17).
- Builder dijalankan ulang: 0 revisi baru, 0 stok tambahan. Config yang berubah tidak ditimpa diam-diam. Importer sumber historis tidak dijalankan ulang karena akan menimpa asumsi metadata sebelum revisi.
- Bukti hitungan, daftar config/hash, daftar stok, revisi dan SHA256 sumber: [evidence.json](evidence.json). Tidak menyimpan badan varian numerik.

Uji ulang dari root repo:

```powershell
python -B -m unittest discover -s variant_gen/tests -p test_drill_16_19_level45_completion.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_16_19_level45_import.py
python -B -m unittest discover -s variant_gen/tests -p test_conceptual_stock.py
```
