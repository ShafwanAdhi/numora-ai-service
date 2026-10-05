# Audit Drill Paket 1, indikator 6–10

Sumber: 150 soal. SHA-256: `f736431733803c68f7de09d53285cd80ec6be6d63b56459664489f4d49d954c2`.

**129 ACTIVE, 12 HOLD_SOURCE, 9 DEFERRED_CONCEPTUAL**. Level 4–5 belum ada pada sumber.

Seluruh ACTIVE mereproduksi original, mencapai 20 variant unik pada seed 1–200, dan lolos oracle matematika independen untuk semua opsi. Audit seed 201–400: 25800 hasil diterima, 0 kegagalan generasi.

Audit menggunakan memori/store sementara; tidak mengakses database atau menulis snapshot pengguna. Tidak ada koreksi akademik sumber.

ponytail: recipe memakai satu parameter terbatas. Umumnya 39 nilai nonoriginal; hasil audit unik adalah stok teramati, bukan janji stok tanpa batas. Tambahkan parameter independen yang direview jika kebutuhan stok meningkat. Shuffle tidak dihitung sebagai variasi substantif.

Pembahasan original mempertahankan teks sumber; notasi Word yang datar bisa berbeda dari notasi variant. Raw DOCX dan source_text disimpan untuk pemeriksaan.

Temuan minor ditunda: pg-8-1-5, kategori-8-2-9, mcma-8-3-8 dapat menghasilkan berat manusia tidak realistis karena penskalaan. Matematika benar; rentang konteks perlu dikurasi sebelum penggunaan produksi.

Verifikasi: `python -B -m unittest discover -s variant_gen/tests`. Rincian soal ditunda: [soalskip.md](../../variant_gen/soalskip.md).

| ID | Status | Stok gate | Unik seed 201–400 | Alasan |
|---|---|---:|---:|---|
| `pg-6-1-1` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-1-2` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-1-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-1-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-1-5` | HOLD_SOURCE | — | — | Header kunci kosong; pembahasan menghasilkan 4,5 liter (opsi C), bukan kunci sumber yang eksplisit. |
| `mcma-6-1-6` | DEFERRED_CONCEPTUAL | — | — | Klasifikasi perbandingan murni; teks jawaban benar tetap walaupun angka diubah. |
| `mcma-6-1-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-6-1-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-6-1-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-6-1-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-2-1` | ACTIVE | 20 | 37 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-2-2` | ACTIVE | 20 | 40 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-2-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-2-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-2-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-6-2-6` | DEFERRED_CONCEPTUAL | — | — | Klasifikasi senilai/berbalik nilai; teks jawaban benar tetap walaupun angka diubah. |
| `mcma-6-2-7` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-6-2-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-6-2-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-6-2-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-3-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-3-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-3-3` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-3-4` | ACTIVE | 20 | 40 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-6-3-5` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-6-3-6` | DEFERRED_CONCEPTUAL | — | — | Klasifikasi hubungan perbandingan; teks jawaban benar tetap walaupun angka diubah. |
| `mcma-6-3-7` | HOLD_SOURCE | — | — | Frasa pada hari ke-3 ambigu; jawaban 5,25 hari mengasumsikan tiga hari penuh telah berlalu. |
| `mcma-6-3-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-6-3-9` | DEFERRED_CONCEPTUAL | — | — | Satu klaim benar tetap: Vendor Y berbanding lurus. Mengubah biaya tidak mengubah himpunan jawaban benar. |
| `kategori-6-3-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-1-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-1-2` | HOLD_SOURCE | — | — | Header kunci kosong; pembahasan menghasilkan Rp35.000 (opsi B), bukan kunci sumber yang eksplisit. |
| `pg-7-1-3` | HOLD_SOURCE | — | — | Luas yang dihitung 80 (opsi C), kunci sumber B=72. |
| `pg-7-1-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-1-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-1-6` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-1-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-1-8` | ACTIVE | 20 | 29 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-7-1-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-7-1-10` | DEFERRED_CONCEPTUAL | — | — | Klaim benar identitas/kontradiksi tetap; perubahan angka tidak lolos same_answer_as_original. |
| `pg-7-2-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-2-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-2-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-2-4` | HOLD_SOURCE | — | — | Kontradiksi memerlukan a != -4; opsi berkunci menyebut a != 4. Periksa opsi dan pembahasan lengkap. |
| `pg-7-2-5` | ACTIVE | 20 | 29 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-2-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-2-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-2-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-7-2-9` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-7-2-10` | DEFERRED_CONCEPTUAL | — | — | Klaim benar identitas/kontradiksi tetap; perubahan angka tidak lolos same_answer_as_original. |
| `pg-7-3-1` | DEFERRED_CONCEPTUAL | — | — | Teks jawaban benar tetap: kedua distributor mempunyai harga dasar yang sama. |
| `pg-7-3-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-3-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-3-4` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-7-3-5` | HOLD_SOURCE | — | — | XML sumber mengonfirmasi opsi A/B k=4, C/D k=8. Kunci B salah untuk kontradiksi k != 4; opsi duplikat. |
| `mcma-7-3-6` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-3-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-7-3-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-7-3-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-7-3-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-1-1` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-1-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-1-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-1-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-1-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-1-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-1-7` | ACTIVE | 20 | 35 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-1-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-8-1-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-8-1-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-2-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-2-2` | ACTIVE | 20 | 37 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-2-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-2-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-2-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-2-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-2-7` | ACTIVE | 20 | 31 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-2-8` | HOLD_SOURCE | — | — | Langkah 4 mencantumkan hasil dengan tanda salah sekaligus alternatif benar; evaluasi kesalahan dan kunci tidak konsisten. |
| `kategori-8-2-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-8-2-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-3-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-3-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-3-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-3-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-8-3-5` | ACTIVE | 20 | 31 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-3-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-3-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-8-3-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-8-3-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-8-3-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-1-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-1-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-1-3` | HOLD_SOURCE | — | — | XML sumber mengonfirmasi opsi A/B k=8, C/D k=4. Kunci B adalah sistem berhimpit; tanpa solusi perlu k != 8. |
| `pg-9-1-4` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-1-5` | HOLD_SOURCE | — | — | Metode paling efisien tidak didefinisikan; opsi substitusi dan eliminasi sama-sama valid dan memberikan hasil benar. Perjelas kriteria atau opsi sebelum aktivasi. |
| `mcma-9-1-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-1-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-1-8` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-9-1-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-9-1-10` | DEFERRED_CONCEPTUAL | — | — | Klaim benar jenis grafik tetap; variasi angka saja tidak mengubah jawaban benar. |
| `pg-9-2-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-2-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-2-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-2-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-2-5` | HOLD_SOURCE | — | — | Metode paling efisien tidak didefinisikan; opsi substitusi dan eliminasi sama-sama valid dan memberikan hasil benar. Perjelas kriteria atau opsi sebelum aktivasi. |
| `mcma-9-2-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-2-7` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-2-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-9-2-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-9-2-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-3-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-3-2` | HOLD_SOURCE | — | — | Nomor soal dan tingkat kognitif tidak tercantum. ID lokal 2 disimpulkan dari posisi; kunci A eksplisit pada pembahasan. Metadata sumber perlu disahkan. |
| `pg-9-3-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-9-3-4` | HOLD_SOURCE | — | — | Metode paling efisien tidak didefinisikan; opsi substitusi dan eliminasi sama-sama valid dan memberikan hasil benar. Perjelas kriteria atau opsi sebelum aktivasi. |
| `pg-9-3-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-3-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-3-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-9-3-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-9-3-9` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-9-3-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-1-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-1-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-1-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-1-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-1-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-1-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-1-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-1-8` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-10-1-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-10-1-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-2-1` | ACTIVE | 20 | 38 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-2-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-2-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-2-4` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-2-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-2-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-2-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-2-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-10-2-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-10-2-10` | DEFERRED_CONCEPTUAL | — | — | Ketiga klaim ekuivalensi benar dengan teks tetap; variasi angka yang aman belum tersedia. |
| `pg-10-3-1` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-3-2` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-3-3` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-3-4` | ACTIVE | 20 | 37 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `pg-10-3-5` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-3-6` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-3-7` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `mcma-10-3-8` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-10-3-9` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
| `kategori-10-3-10` | ACTIVE | 20 | 39 | Reproduksi dan seluruh opsi lolos oracle independen. |
