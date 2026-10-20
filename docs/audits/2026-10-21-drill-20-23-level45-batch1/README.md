# 27 generator indikator 20-23 level 4-5

21 Oktober 2026. Tahap pertama **27/80 original (33,75%)** selesai. Semua 27 dipilih dari67 ACTIVE hasil audit, tanpa merevisi original atau membuka13 HOLD. Sisanya **53 soal:40 menunggu generator/stok,13 HOLD_SOURCE**. Penetapan konseptual untuk40 soal tersisa belum final.

## Cakupan indikator 20-23 keseluruhan

| Indikator | Original | Generator tambahan | Generator total | Konseptual dengan stok | Stok | Menunggu | HOLD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20 | 50 | 3 | 24 | 9 | 28 | 17 | 0 |
| 21 | 50 | 8 | 37 | 1 | 2 | 8 | 4 |
| 22 | 50 | 6 | 30 | 6 | 16 | 11 | 3 |
| 23 | 50 | 10 | 38 | 2 | 4 | 4 | 6 |
| Total | 200 | 27 | 129 | 18 | 50 | 40 | 13 |

Tetap Drill > Paket 1 (`drill-1`) > indikator > level > soal. Nomor runtime1-10 per level; nomor sumber31-50 tetap dalam metadata. Config JSON v1 memakai engine yang sudah ada; tidak ada dependensi atau layanan baru.

## Cara variasi dan batas

- Statistik: translasi data mempertahankan urutan, relasi mean/median/modus dan perbandingan jangkauan. Nilai ujian terpilih tetap0-100; hitungan buku/pengunjung dan waktu tetap bilangan bulat positif. Total, klaim opsi dan pembahasan ikut dihitung ulang.
- Beberapa jawaban kualitatif diberi hasil statistik yang relevan pada varian, misalnya rerata kedua kelompok atau rerata baru. Parameter reproduksi sumber tidak menambahkan teks tersebut. Ini menjaga keterkaitan jawaban dengan data baru.
- Peluang empiris: jumlah kejadian atau distribusi diubah dengan total frekuensi tetap konsisten. Peluang berada pada0-1. Pecahan varian eksak dipakai untuk rasio yang tidak memiliki desimal berhenti; tidak menyisipkan pembulatan implisit. Opsi sumber yang eksplisit mengatakan sekitar tetap diuji dengan toleransi setengah unit digit desimal terakhir.
- Domain default **k=1..30** menghasilkan 30 varian unik valid per soal; k=0 mereproduksi original. Permintaan generate dapat diulang tanpa menyimpan hasil; bukan jaminan varian unik tak terbatas. Perlu audit domain baru sebelum memperluas rentang.

Semua 27 memiliki stimulus, opsi, kunci dan pembahasan yang diuji. Jumlah opsi PG/MCMA serta label kategori mengikuti original, termasuk lima opsi indikator23. Config dapat dibaca melalui workbench; generasi memakai endpoint yang sudah tersedia. Status approval tetap `NOT_CURRICULUM_APPROVED`, self-adjustment nonaktif; belum mengklaim kalibrasi IRT.

## Daftar generator

| ID runtime | Nomor sumber | Domain diuji | Varian unik |
|---|---:|---:|---:|
| `mcma-20-4-7` | 37 | 31 | 30 |
| `kategori-20-4-9` | 39 | 31 | 30 |
| `pg-20-5-5` | 45 | 31 | 30 |
| `pg-21-4-1` | 31 | 31 | 30 |
| `pg-21-4-2` | 32 | 31 | 30 |
| `pg-21-4-3` | 33 | 31 | 30 |
| `pg-21-4-5` | 35 | 31 | 30 |
| `mcma-21-4-6` | 36 | 31 | 30 |
| `mcma-21-4-7` | 37 | 31 | 30 |
| `pg-21-5-4` | 44 | 31 | 30 |
| `kategori-21-5-9` | 49 | 31 | 30 |
| `pg-22-4-1` | 31 | 31 | 30 |
| `pg-22-4-2` | 32 | 31 | 30 |
| `pg-22-4-4` | 34 | 31 | 30 |
| `mcma-22-4-6` | 36 | 31 | 30 |
| `mcma-22-4-8` | 38 | 31 | 30 |
| `kategori-22-5-10` | 50 | 31 | 30 |
| `pg-23-4-1` | 31 | 31 | 30 |
| `pg-23-4-2` | 32 | 31 | 30 |
| `pg-23-4-3` | 33 | 31 | 30 |
| `pg-23-4-4` | 34 | 31 | 30 |
| `mcma-23-4-6` | 36 | 31 | 30 |
| `kategori-23-4-9` | 39 | 31 | 30 |
| `kategori-23-4-10` | 40 | 31 | 30 |
| `pg-23-5-1` | 41 | 31 | 30 |
| `mcma-23-5-6` | 46 | 31 | 30 |
| `kategori-23-5-10` | 50 | 31 | 30 |

## Bukti verifikasi

**47 tes lulus**: batch baru3,intake5,bank20-23 existing10,stok konseptual10,katalog2,workbench17.

- Seluruh 837 input diuji dengan oracle independen berbasis `Fraction` dan statistik dari stimulus/opsi yang sudah dirender, bukan nilai internal config. Ada 810 varian unik valid.
- Reproduksi 27 original persis untuk stem, opsi dan kunci. Sepuluh seeded draws per soal valid dan deterministik. Kunci yang dibalik, angka opsi benar yang dirusak, dan hasil pembahasan yang dirusak ditolak oracle.
- POST generate seluruh 27 soal berhasil. GET 80 original dan penolakan generate 13 HOLD tetap lulus regresi. Uji baru menolak akses database dengan mock; tidak terbentuk berkas hasil runtime.
- Authoring dijalankan ulang: config tetap identik, tidak membuat versi baru. Config yang telah diedit tidak ditimpa diam-diam.
- Hash CSV original, audit intake, katalog dan DOCX tetap sesuai snapshot impor. Metadata hanya mengubah `generator_status` pada 27 ID menjadi `IMPLEMENTED`; stok tidak ditambahkan atau diubah.

Bukti hitungan, hash config dan hash original: [evidence.json](evidence.json). Tidak menyimpan badan varian numerik.

```powershell
python -B -m unittest discover -s variant_gen/tests -p test_drill_20_23_level45_batch1.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_20_23_level45_import.py
python -B variant_gen/tests/author_drill_20_23_level45_batch1.py
```

Importer sumber historis tetap membentuk snapshot metadata sebelum generator; jangan memakainya untuk menimpa metadata terbaru. Guard overwrite menolak perubahan tersebut. Tes intake membandingkan sumber tetap identik sambil menerima status IMPLEMENTED berdasarkan config yang tersedia. Database Numora tidak diubah; hasil runtime tidak disimpan. Restart workbench yang masih berjalan sebelum memeriksa config baru.
