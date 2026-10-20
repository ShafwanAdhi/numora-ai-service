# Batch kedua generator indikator 20-23 level 4-5

21 Oktober 2026. Tambahan **27 generator**, sehingga **54/80 original baru (67,5%)** memiliki generator. Sisanya **13 menunggu generator/stok dan 13 HOLD_SOURCE**. Tidak ada revisi original, tambahan stok konseptual, perubahan engine, atau perubahan database.

## Cakupan seluruh indikator 20-23

| Indikator | Original | Tambahan batch ini | Generator total | Konseptual dengan stok | Stok | Menunggu | HOLD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20 | 50 | 4 | 28 | 9 | 28 | 13 | 0 |
| 21 | 50 | 8 | 45 | 1 | 2 | 0 | 4 |
| 22 | 50 | 11 | 41 | 6 | 16 | 0 | 3 |
| 23 | 50 | 4 | 42 | 2 | 4 | 0 | 6 |
| Total | 200 | 27 | 156 | 18 | 50 | 13 | 13 |

Struktur tetap Drill > Paket 1 > indikator > level > soal. Nomor runtime 1-10, nomor sumber 31-50 tetap tersimpan. Status `NOT_CURRICULUM_APPROVED` dan self-adjustment nonaktif tetap dipertahankan; hasil ini tidak menyatakan kesetaraan IRT.

## Variasi dan batas

- Tabel: jumlah buku, responden, dan proporsi diubah konsisten; total kategori dan kelompok terbesar diperiksa kembali. Pemilihan diagram tetap menguji pemahaman kategori nominal, meskipun angkanya berubah.
- Statistik: translasi mempertahankan urutan dan perbandingan ukuran pusat/penyebaran; skala waktu positif juga mengubah jangkauan. Semua nilai ujian tetap 0-100, pendapatan positif, waktu belajar harian tidak melampaui 24 jam. Opsi yang memuat angka ikut diperbarui.
- Jawaban kualitatif tertentu menyertakan hasil hitungan yang relevan pada varian. Saat mereproduksi sumber, anotasi tidak ditambahkan. Ini mengikuti pola batch pertama dan memenuhi validator jawaban engine yang sudah ada.
- Peluang: jumlah percobaan, kejadian, frekuensi relatif, dan klaim diperbarui bersama. Perbandingan kedekatan dengan peluang teoretis diperiksa untuk seluruh domain. Rasio berulang ditulis sebagai pecahan eksak; opsi sumber dengan kata "sekitar" diuji sesuai ketelitian tiga desimalnya.
- **30 varian unik valid per soal**, domain k=1..30; k=0 mereproduksi stem, opsi, dan kunci original. Permintaan generate dapat diulang tanpa menyimpan hasil. Domain ini terbatas, bukan jaminan keunikan tanpa batas; perlu audit sebelum memperluasnya.

## Verifikasi

**50 tes lulus**: batch kedua 3, batch pertama 3, intake 5, bank existing 10, stok konseptual 10, katalog 2, workbench 17.

- 837 input diperiksa oracle independen dari stimulus/opsi yang sudah dirender, menggunakan `Fraction` dan statistik; 810 varian unik valid.
- 270 seeded draws valid dan deterministik. Pembalikan kunci, kerusakan angka opsi benar, dan kerusakan hasil utama pembahasan ditolak oracle.
- POST `/api/generate` berhasil untuk 27 soal. Akses database ditolak oleh mock dan tidak terbentuk berkas hasil runtime. Regresi mencakup pembacaan 80 original dan penolakan generate 13 HOLD.
- Authoring ulang idempotent. CSV, audit intake, katalog, stok, dan konfigurasi 27 soal batch pertama tetap identik berdasarkan hash. Metadata hanya mengubah 27 `generator_status` menjadi `IMPLEMENTED`.
- Tes cakupan batch pertama kini memeriksa 27 ID batch tersebut, sehingga penambahan batch berikutnya tidak menggagalkan pemeriksaan historis.

Bukti hash dan seluruh ID: [evidence.json](evidence.json). Berkas tersebut tidak menyimpan badan soal varian. [Laporan batch pertama](../2026-10-21-drill-20-23-level45-batch1/README.md) tetap merupakan snapshot historis.

```powershell
python -B -m unittest discover -s variant_gen/tests -p test_drill_20_23_level45_batch2.py
python -B variant_gen/tests/author_drill_20_23_level45_batch2.py
```

Restart workbench yang masih berjalan untuk memuat konfigurasi baru. Jangan menjalankan importer sumber untuk menimpa metadata terbaru; guard overwrite tetap menolak perubahan tersebut.

## Sisa pekerjaan

13 soal ACTIVE yang belum memiliki generator/stok semuanya berada pada indikator 20. Meliputi evaluasi pertanyaan survei, keterwakilan sampel, sebab-akibat, serta pemilihan penyajian. Penentuan generator numerik atau stok konseptualnya belum dilakukan pada tahap ini. Daftar ID ada pada `pending_ids` di evidence.

13 HOLD tetap mengikuti audit sumber: indikator 21 sebanyak 4, indikator 22 sebanyak 3, indikator 23 sebanyak 6. Kunci yang berkonflik, pembulatan yang tidak dinyatakan, dan asumsi model peluang yang belum lengkap tidak diubah pada batch ini.
