# Audit dan impor original indikator 20-23 level 4-5

Tanggal: 21 Oktober 2026. Seluruh **80 original** diimpor ke bank lokal aktif: **67 ACTIVE, 13 HOLD_SOURCE**. Tidak membuat generator, stok, revisi jawaban, atau perubahan database utama.

| Indikator | Original baru | ACTIVE | HOLD | Total original aktif lokal |
|---|---:|---:|---:|---:|
| 20 | 20 | 20 | 0 | 50 |
| 21 | 20 | 16 | 4 | 50 |
| 22 | 20 | 17 | 3 | 50 |
| 23 | 20 | 14 | 6 | 50 |
| Total | 80 | 67 | 13 | 200 |

## Struktur dan pemetaan

Bank tambahan: `variant_gen/data/drill-1-indicators-20-23-levels-4-5/`. Loader default CLI/workbench/service memuat folder ini bersama bank lama. Struktur: Drill > Paket 1 (`drill-1`) > indikator > level > soal. Kini masing-masing indikator20-23 lengkap lima level dengan sepuluh original per level.

Nomor sumber tidak diubah: 31-40 menjadi posisi1-10 level4, 41-50 menjadi posisi1-10 level5. Contoh sumber indikator20 soal36 menjadi `mcma-20-4-6`; metadata tetap menyimpan `source_number=36`. Label kognitif C4/C5 disalin dari heading setiap soal, bukan ditebak dari level. Bank lama120 original level1-3 tidak ditulis ulang; kesamaan isinya dengan revisi dokumen masuk terbaru bukan cakupan impor ini.

80 tambahan terdiri atas40 PG,24 MCMA,16 KATEGORI. Semua MCMA mempertahankan lima opsi; PG indikator23 juga mempertahankan lima opsi. Kunci MCMA tidak dipotong menjadi opsi pertama. Label kategori, tanda pilihan pada tabel sumber, stem, semua tabel data dan pembahasan tetap tersedia dalam format runtime. Tanda kunci pada tabel kategori tidak masuk teks opsi siswa. Kalimat pertanyaan setelah daftar rancangan pada pg-20-5-1 ditempatkan kembali ke stem; kalimat sumber tetap utuh.

Parser intake khusus memakai stdlib, tanpa mengubah parser audit historis. HTML tabel sumber diubah menjadi tabel Markdown dengan urutan dan nilai sel sama. Judul bagian soal berikutnya dilepas dari pembahasan soal sebelumnya. Seluruh raw source, deklarasi kunci, lokasi paragraf/blok dan SHA256 DOCX dipertahankan dalam metadata. Dokumen diperlakukan sebagai data, bukan instruksi operasional.

## Audit dan daftar HOLD

Setiap soal ditinjau dari stimulus dan semua opsi, kemudian dibandingkan dengan kunci serta pembahasan. Perhitungan mean/median/mode/range dan peluang dihitung ulang; penilaian survei memeriksa relevansi variabel, representativitas, bias, pemilihan diagram dan klaim sebab-akibat. Hasil bukan sekadar salinan putusan audit lama. Bukti per soal: [audit.json](../../../variant_gen/data/drill-1-indicators-20-23-levels-4-5/audit.json).

Kunci primer sumber tetap dipakai dalam CSV, termasuk ketika salah. Koreksi yang tertulis di bagian pembahasan tidak otomatis menggantikan kunci. Soal demikian masuk HOLD agar tidak dianggap siap generate. Jawaban independen pada persoalan asumsi bersifat bersyarat, bukan kunci pengganti.

| ID runtime | Nomor sumber | Temuan dan tindak lanjut |
|---|---:|---|
| `kategori-21-4-9` | 39 | WRONG_KEY_AND_EXPLANATION: median data adalah25, sehingga B benar. Kunci/tabel memberi B Salah, pembahasan juga menyebut median25 tetapi menyimpulkan B salah. Himpunan benar1234, bukan134. |
| `kategori-21-4-10` | 40 | CONFLICTING_KEY: rerata kedua kelompok3; median2 dan3; jangkauan6 dan2. Hanya D tepat. Kunci/tabel124 bertentangan dengan data dan koreksi pada pembahasan yang memilih4. |
| `mcma-21-5-6` | 46 | CONFLICTING_KEY: jumlah400/5=80, jadi opsi B benar. Kunci awal A,C,D menghilangkan B; pembahasan kemudian mengoreksi menjadi A,B,C,D. |
| `mcma-21-5-7` | 47 | CONFLICTING_KEY: rerata kedua kelompok400/5=80, sehingga C salah. Kunci awal A,B,C,E bertentangan dengan koreksi pembahasan A,B,E. |
| `pg-22-4-3` | 33 | WRONG_KEY_AND_CORRECTION: opsi D benar karena rerata kedua kelompok4. Kunci awal A salah; pembahasan salah menyatakan tidak ada opsi benar, lalu mengusulkan perubahan A yang akan menduplikasi D. |
| `mcma-22-4-7` | 37 | CONFLICTING_KEY: kelompok Q berisi3,4,5,6,7 tanpa modus tunggal. E salah. Kunci awal A,B,D,E bertentangan dengan koreksi pembahasan A,B,D. |
| `kategori-22-4-9` | 39 | CONFLICTING_KEY: rerata kedua kelompok20, sehingga B salah. Kunci/tabel123 bertentangan dengan koreksi pembahasan13. |
| `pg-23-4-5` | 35 | MISSING_FAIRNESS: stimulus tidak menyebut koin seimbang. Frekuensi relatif0.65 tidak menetapkan peluang teoretis; opsi C memakai peluang0.5 yang mensyaratkan koin seimbang. Tegaskan asumsi pada stimulus. |
| `mcma-23-4-7` | 37 | UNSTATED_ROUNDING:28/60=0.4666..., bukan tepat0.47 pada opsi B. Pembahasan memakai sekitar0.47, stimulus/opsi tidak. KunciABC menganggap pembulatan yang belum dinyatakan; kunci eksakAC. |
| `pg-23-5-3` | 43 | MISSING_MODEL: peluang tepat satu gambar adalah1/2 hanya untuk dua lemparan independen koin seimbang. Stimulus tidak menetapkan kedua asumsi; ruang sampel empat hasil saja tidak menjamin peluang setara. |
| `pg-23-5-4` | 44 | MISSING_FAIRNESS: stimulus tidak menyebut dadu seimbang. Peluang genap0.5 pada opsi C memerlukan asumsi tersebut; frekuensi relatif162/300 tidak menetapkannya. |
| `mcma-23-5-7` | 47 | MISSING_FAIRNESS: stimulus tidak menyebut koin seimbang. A,B,C benar empiris; D tidak dapat dinilai salah secara pasti karena peluang koin yang tidak diketahui dapat saja0.575. Tegaskan model sebelum memakai kunciABC. |
| `mcma-23-5-8` | 48 | MISSING_RANDOM_DRAW: peluang4/10 pada opsi A membutuhkan pengambilan acak seragam. Stimulus hanya menyebut mengambil satu bola dan pengembalian, belum menyatakan acak/seragam. Frekuensi relatifB,C tetap benar; tegaskan mekanisme untuk kunciABC. |

Tujuh HOLD indikator21-22 merupakan kesalahan/konflik kunci atau pembahasan. Enam HOLD indikator23 terdiri atas satu pembulatan tidak dinyatakan dan lima model peluang belum eksplisit (koin/dadu seimbang, lemparan independen, atau pengambilan acak seragam). Asumsi standar dapat menjadi revisi minimum berikutnya, tetapi tidak disisipkan diam-diam pada tahap impor ini.

`ACTIVE` berarti lolos audit sumber lokal, bukan persetujuan kurikulum, kesetaraan IRT, publikasi siswa, atau ketersediaan generator. Semua80 berstatus `NOT_CURRICULUM_APPROVED`, `generator_status=NOT_IMPLEMENTED`, dan self-adjustment nonaktif. Pembagian final generator numerik versus stok konseptual belum dilakukan.

## Verifikasi

- 3.064 paragraf hasil ekstraksi dicocokkan dengan XML DOCX: tidak ada perbedaan teks setelah mengabaikan whitespace. SHA256 sumber tetap `74a6f81a2c65ed9f11fc824f1f999c13fb79faa2887cf5db9311df9b85a19e57`.
- 80 ID unik,10 per indikator/level,200 original total indikator20-23. Metadata, pembahasan, lima opsi, label kategori, tabel data dan kunci primer diperiksa.
- HTTP GET berhasil untuk semua80 original;13 permintaan generate soal HOLD ditolak. Tidak ada panggilan database atau berkas hasil runtime.
- Import ulang byte-identik. Percobaan menimpa output yang telah diedit ditolak sebelum penulisan.
- **44 tes lulus**: intake baru5,bank20-23 existing10,katalog2,stok konseptual10,workbench17. Bukti ringkas dan hash output: [evidence.json](evidence.json).

```powershell
python -B variant_gen/tests/import_drill_20_23_level45.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_20_23_level45_import.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_20_23.py
```

Restart workbench yang sudah berjalan untuk memuat80 original baru. Generator/stok lama indikator20-23 tetap102 generator dan18 konseptual/50 stok. Tambahan80 belum memiliki generator/stok:67 menunggu tahap berikutnya,13 menunggu penuntasan temuan sumber.
