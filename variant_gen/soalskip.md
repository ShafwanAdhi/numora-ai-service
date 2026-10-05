# Soal tanpa generator

Inventaris 5 Oktober 2026: **95 soal belum memiliki config**, terdiri dari 92 Drill dan 3 Tryout. Bagian pertama mempertahankan review historis 12 soal indikator16–19; sepuluh di antaranya masih tanpa config. Bagian berikut mencatat HOLD_SOURCE dan DEFERRED_CONCEPTUAL pada bank tambahan.

## Review 12 soal — 4 Oktober 2026

Review ini menilai kelayakan generasi dengan engine sekarang. Config baru masih
memerlukan review Curriculum; keberadaan config bukan kelulusan kesetaraan IRT.
Sepuluh soal tetap belum mempunyai config, dengan alasan dan langkah berikut di bawah.

| Soal | Hasil review | Strategi / batas |
|---|---|---|
| `pg-16-1-1` | Perlu desain konten | Dua lingkaran + satu persegi panjang selalu menunjukkan tabung. Angka komponen adalah fakta struktur, bukan variabel bebas. Butuh template konseptual setara yang disahkan. |
| `pg-16-1-2` | Perlu desain konten | Satu persegi + empat segitiga menentukan limas segi empat. Mengacak jumlah sisi mengubah bangun. Butuh alternatif stimulus dalam kompetensi yang sama. |
| `pg-16-3-2` | Perlu desain konten | Tabung tanpa tutup selalu memakai satu lingkaran dan satu persegi panjang. Dimensi bebas tidak ditanyakan; tambah konteks pengukuran mengubah tugas akademik. |
| `mcma-16-1-6` | Perlu desain konten | Prisma segitiga mempunyai dua alas, tiga sisi tegak, lima komponen. Jangan mengacak fakta ini. Review template konseptual alternatif. |
| `kategori-16-1-9` | Perlu review policy jawaban | Dua pernyataan benar tentang limas segi empat tetap sama. Mengubah distractor saja ditolak oleh aturan `same_answer_as_original`; perlu policy eksplisit atau stimulus alternatif. |
| `kategori-16-2-9` | Perlu review policy jawaban | Identitas limas dan jumlah lima sisi tetap. Variasi pernyataan salah tidak mengubah himpunan teks jawaban benar. |
| `mcma-16-3-6` | **Config dibuat** | Variasikan faktor rusuk `k`; faktor luas dihitung `k²`. Fakta enam sisi dipertahankan. Empat kandidat unik (`k=3..6`); `k=2` mereproduksi original dan ditolak. |
| `pg-17-3-2` | Perlu desain konten | Refleksi sumbu X lalu Y selalu ekuivalen rotasi 180°. Koordinat baru tidak mengubah jawaban. Perlu konfigurasi komposisi/stimulus yang disahkan. |
| `pg-17-3-3` | **Config dibuat** | Koordinat dan sudut dimodelkan. Original 90° dipertahankan; kandidat memakai 180° agar jawaban berbeda. Pilihan 90° searah jarum jam dan 270° berlawanan arah jarum jam ekuivalen, sehingga 270° tidak digenerasikan sebagai jawaban. |
| `mcma-17-1-8` | Perlu review konten | Sifat transformasi adalah fakta konseptual. Pernyataan dilatasi mengubah ukuran perlu mengecualikan `abs(k)=1`; jangan mengesahkan klaim universal tanpa faktor/konteks. |
| `kategori-17-2-10` | Perlu review konten | Sama: faktor dilatasi `1` atau `-1` mempertahankan ukuran. Butuh redaksi eksplisit dan template sebelum generasi. |
| `kategori-17-3-10` | Perlu review policy jawaban | Faktor pada pernyataan salah dapat diubah, tetapi dua pernyataan benar tetap sama. Aturan jawaban berbeda menahan kandidat; faktor luas yang benar harus selalu `k²`. |

Aturan `same_answer_as_original` tetap berlaku. Shuffle opsi bukan varian substantif.
Tidak ada perubahan policy global untuk meloloskan soal yang belum didesain.

## Drill Paket 1, indikator 20?23 ? 5 Oktober 2026

**34 soal belum dibuat generatornya:** 11 konflik sumber (`HOLD_SOURCE`), 23 template konseptual/jawaban tetap (`DEFERRED_CONCEPTUAL`). Original tetap tersedia di UI; generate/regen dan editor config dinonaktifkan. Koreksi akademik belum diterapkan.

Nomor sumber mengikuti dokumen (1?30 per indikator); nomor dalam ID lokal mengikuti level (1?10).

| ID lokal | Indikator / nomor sumber | Status | Alasan |
|---|---|---|---|
| `pg-20-1-1` | 20 / 1 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `mcma-20-1-6` | 20 / 6 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `kategori-20-1-9` | 20 / 9 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `kategori-20-1-10` | 20 / 10 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `pg-20-2-1` | 20 / 11 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `mcma-20-2-7` | 20 / 17 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `kategori-20-2-10` | 20 / 20 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `pg-20-3-3` | 20 / 23 | HOLD_SOURCE | Hasil 110; opsi C dan D duplikat. Koreksi opsi belum disetujui. |
| `pg-20-3-5` | 20 / 25 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `mcma-20-3-8` | 20 / 28 | DEFERRED_CONCEPTUAL | Konsep survei/jenis data/penyajian: membutuhkan skenario setara terkurasi yang direview; shuffle tidak memenuhi same_answer_as_original. |
| `pg-21-2-2` | 21 / 12 | HOLD_SOURCE | Hasil 70; opsi C dan D duplikat. Koreksi opsi belum disetujui. |
| `pg-21-2-5` | 21 / 15 | DEFERRED_CONCEPTUAL | Jawaban ukuran statistik tetap; mengubah data saja tidak memenuhi same_answer_as_original. Template konsep setara perlu review. |
| `pg-21-3-1` | 21 / 21 | HOLD_SOURCE | Stem menyebut nilai 90; mean mengharuskan 89. Koreksi stem belum disetujui. |
| `pg-21-3-4` | 21 / 24 | HOLD_SOURCE | Mean baru 72; tidak ada opsi yang benar. Koreksi opsi belum disetujui. |
| `pg-21-3-5` | 21 / 25 | HOLD_SOURCE | PG memiliki beberapa jawaban benar: median A<B, range B>A, modus berbeda. |
| `mcma-21-3-8` | 21 / 28 | HOLD_SOURCE | Seluruh pernyataan awal salah. Koreksi pernyataan belum disetujui. |
| `kategori-21-3-9` | 21 / 29 | HOLD_SOURCE | Mean 520/7≈74,29; kunci D tidak benar. Koreksi kunci belum disetujui. |
| `pg-22-1-1` | 22 / 1 | HOLD_SOURCE | Mean A=B=80; kunci B bertentangan dengan opsi C dan pembahasan. |
| `pg-22-1-4` | 22 / 4 | DEFERRED_CONCEPTUAL | Jawaban ukuran statistik tetap; mengubah data saja tidak memenuhi same_answer_as_original. Template konsep setara perlu review. |
| `mcma-22-1-6` | 22 / 6 | HOLD_SOURCE | Mean A=B=6; pernyataan 1 salah. Koreksi kunci belum disetujui. |
| `mcma-22-1-7` | 22 / 7 | HOLD_SOURCE | Mean A=74, B=76; pernyataan 1 salah. Pembahasan menjumlahkan B secara keliru. |
| `mcma-22-1-8` | 22 / 8 | DEFERRED_CONCEPTUAL | Dengan median/mean A dan B yang sama, tiga pernyataan benar selalu 1,2,4. Mengubah angka saja tidak lolos same_answer_as_original; perlu template pernyataan baru yang direview. |
| `pg-22-2-3` | 22 / 13 | DEFERRED_CONCEPTUAL | Jawaban ukuran statistik tetap; mengubah data saja tidak memenuhi same_answer_as_original. Template konsep setara perlu review. |
| `pg-22-2-5` | 22 / 15 | DEFERRED_CONCEPTUAL | Alasan konsistensi berdasarkan jangkauan hanya tersedia pada satu opsi; mengganti relasi tidak menghasilkan opsi benar alternatif yang sah. |
| `mcma-22-2-8` | 22 / 18 | DEFERRED_CONCEPTUAL | Pada dua dataset simetris, tiga pernyataan benar memerlukan mean=median kedua kelompok sama dan range B>A; himpunan jawaban tetap. Template pernyataan baru perlu review. |
| `pg-22-3-5` | 22 / 25 | DEFERRED_CONCEPTUAL | Alasan konsistensi berdasarkan jangkauan hanya tersedia pada satu opsi; mengganti relasi tidak menghasilkan opsi benar alternatif yang sah. |
| `mcma-22-3-8` | 22 / 28 | HOLD_SOURCE | Mean A=B=60; pernyataan 1 salah. Koreksi kunci belum disetujui. |
| `pg-23-1-1` | 23 / 1 | DEFERRED_CONCEPTUAL | Peluang kejadian tunggal dadu/koin seimbang tetap. Mengubah nama/seed bukan variasi jawaban; perubahan ruang kejadian perlu review. |
| `pg-23-1-2` | 23 / 2 | DEFERRED_CONCEPTUAL | Peluang kejadian tunggal dadu/koin seimbang tetap. Mengubah nama/seed bukan variasi jawaban; perubahan ruang kejadian perlu review. |
| `pg-23-3-2` | 23 / 22 | DEFERRED_CONCEPTUAL | Istilah mendekati belum memiliki domain/aturan penilaian yang direview. Tidak menetapkan ambang kedekatan baru. |
| `pg-23-3-5` | 23 / 25 | DEFERRED_CONCEPTUAL | Opsi alternatif menggunakan jauh lebih besar tanpa definisi; domain yang membuat opsi itu benar perlu review. Opsi lebih kecil tetap tidak lolos same_answer_as_original. |
| `mcma-23-3-7` | 23 / 27 | DEFERRED_CONCEPTUAL | Istilah mendekati belum memiliki domain/aturan penilaian yang direview. Tidak menetapkan ambang kedekatan baru. |
| `mcma-23-3-8` | 23 / 28 | DEFERRED_CONCEPTUAL | Istilah mendekati belum memiliki domain/aturan penilaian yang direview. Tidak menetapkan ambang kedekatan baru. |
| `kategori-23-3-9` | 23 / 29 | DEFERRED_CONCEPTUAL | Istilah mendekati belum memiliki domain/aturan penilaian yang direview. Tidak menetapkan ambang kedekatan baru. |

Untuk mengaktifkan HOLD_SOURCE: review dan setujui koreksi per soal, catat revisi original melalui ledger, lalu buat config dan verifikasi matematika. Untuk DEFERRED_CONCEPTUAL: review template/skenario setara atau aturan penilaian yang diperlukan; kebijakan `same_answer_as_original` tetap.

[Audit lengkap dan stok generator aktif](../docs/audits/2026-10-05-drill-20-23-generator-audit.md).

## Tryout 1 ? catatan existing

| ID | Status | Alasan |
|---|---|---|
| `tryout-1-b1-q07` | DEFERRED_CONCEPTUAL | Ditunda: inti pertanyaan adalah alasan/sifat tanda kurung; variasi konseptual belum dirancang. |
| `tryout-1-b4-q02` | DEFERRED_CONCEPTUAL | Ditunda: setiap satu mata pada dadu fair enam sisi selalu berpeluang 1/6. |
| `tryout-1-b4-q06` | DEFERRED_CONCEPTUAL | Ditunda: evaluasi bias, sampling, dan tipe data; klaim proporsional pada pembahasan source perlu review. |

## Drill Paket 1, indikator 6–10

150 original: 129 ACTIVE, 12 HOLD_SOURCE, 9 DEFERRED_CONCEPTUAL. Semua 21 soal tanpa generator dicatat berikut. Level 4–5 belum tersedia pada sumber.

| ID | Status | Alasan |
|---|---|---|
| `pg-6-1-5` | HOLD_SOURCE | Header kunci kosong; pembahasan menghasilkan 4,5 liter (opsi C), bukan kunci sumber yang eksplisit. |
| `mcma-6-1-6` | DEFERRED_CONCEPTUAL | Klasifikasi perbandingan murni; teks jawaban benar tetap walaupun angka diubah. |
| `mcma-6-2-6` | DEFERRED_CONCEPTUAL | Klasifikasi senilai/berbalik nilai; teks jawaban benar tetap walaupun angka diubah. |
| `mcma-6-3-6` | DEFERRED_CONCEPTUAL | Klasifikasi hubungan perbandingan; teks jawaban benar tetap walaupun angka diubah. |
| `mcma-6-3-7` | HOLD_SOURCE | Frasa pada hari ke-3 ambigu; jawaban 5,25 hari mengasumsikan tiga hari penuh telah berlalu. |
| `kategori-6-3-9` | DEFERRED_CONCEPTUAL | Satu klaim benar tetap: Vendor Y berbanding lurus. Mengubah biaya tidak mengubah himpunan jawaban benar. |
| `pg-7-1-2` | HOLD_SOURCE | Header kunci kosong; pembahasan menghasilkan Rp35.000 (opsi B), bukan kunci sumber yang eksplisit. |
| `pg-7-1-3` | HOLD_SOURCE | Luas yang dihitung 80 (opsi C), kunci sumber B=72. |
| `kategori-7-1-10` | DEFERRED_CONCEPTUAL | Klaim benar identitas/kontradiksi tetap; perubahan angka tidak lolos same_answer_as_original. |
| `pg-7-2-4` | HOLD_SOURCE | Kontradiksi memerlukan a != -4; opsi berkunci menyebut a != 4. Periksa opsi dan pembahasan lengkap. |
| `kategori-7-2-10` | DEFERRED_CONCEPTUAL | Klaim benar identitas/kontradiksi tetap; perubahan angka tidak lolos same_answer_as_original. |
| `pg-7-3-1` | DEFERRED_CONCEPTUAL | Teks jawaban benar tetap: kedua distributor mempunyai harga dasar yang sama. |
| `pg-7-3-5` | HOLD_SOURCE | XML sumber mengonfirmasi opsi A/B k=4, C/D k=8. Kunci B salah untuk kontradiksi k != 4; opsi duplikat. |
| `mcma-8-2-8` | HOLD_SOURCE | Langkah 4 mencantumkan hasil dengan tanda salah sekaligus alternatif benar; evaluasi kesalahan dan kunci tidak konsisten. |
| `pg-9-1-3` | HOLD_SOURCE | XML sumber mengonfirmasi opsi A/B k=8, C/D k=4. Kunci B adalah sistem berhimpit; tanpa solusi perlu k != 8. |
| `pg-9-1-5` | HOLD_SOURCE | Metode paling efisien tidak didefinisikan; opsi substitusi dan eliminasi sama-sama valid dan memberikan hasil benar. Perjelas kriteria atau opsi sebelum aktivasi. |
| `kategori-9-1-10` | DEFERRED_CONCEPTUAL | Klaim benar jenis grafik tetap; variasi angka saja tidak mengubah jawaban benar. |
| `pg-9-2-5` | HOLD_SOURCE | Metode paling efisien tidak didefinisikan; opsi substitusi dan eliminasi sama-sama valid dan memberikan hasil benar. Perjelas kriteria atau opsi sebelum aktivasi. |
| `pg-9-3-2` | HOLD_SOURCE | Nomor soal dan tingkat kognitif tidak tercantum. ID lokal 2 disimpulkan dari posisi; kunci A eksplisit pada pembahasan. Metadata sumber perlu disahkan. |
| `pg-9-3-4` | HOLD_SOURCE | Metode paling efisien tidak didefinisikan; opsi substitusi dan eliminasi sama-sama valid dan memberikan hasil benar. Perjelas kriteria atau opsi sebelum aktivasi. |
| `kategori-10-2-10` | DEFERRED_CONCEPTUAL | Ketiga klaim ekuivalensi benar dengan teks tetap; variasi angka yang aman belum tersedia. |

Aktivasi HOLD memerlukan konfirmasi/koreksi sumber per soal. Aktivasi DEFERRED memerlukan skenario setara terkurasi yang mengubah jawaban substantif; jangan melonggarkan same_answer_as_original.

[Audit generator aktif](../docs/audits/2026-10-05-drill-6-10-generator-audit.md).

## Drill Paket 1, indikator 11–15

250 original: 223 ACTIVE, 5 HOLD_SOURCE, 22 DEFERRED_CONCEPTUAL. Semua 27 soal tanpa generator dicatat berikut; level 1–5 tersedia.

| ID | Status | Alasan |
|---|---|---|
| `pg-11-1-1` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `mcma-11-1-7` | HOLD_SOURCE | Definisi f hilang pada stem; pembahasan memakai f(x)=x^2-3. Usulan menambahkan definisi; jangan mengasumsikan tanpa ledger. |
| `mcma-11-1-8` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-11-1-9` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-11-2-4` | HOLD_SOURCE | f(g(3))=f(2)=7, opsi B; source key D=11. Usulan key B dengan ledger v2. |
| `mcma-11-2-6` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-11-2-9` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-11-3-9` | HOLD_SOURCE | Istilah akar kuadrat berpotensi principal sqrt versus relasi y^2=x dengan dua akar; pembahasan menghendaki dua akar. Usulan memperjelas relasi y^2=x, bukan fungsi sqrt. |
| `mcma-11-5-6` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-12-2-4` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-12-3-10` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-14-1-1` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `mcma-14-1-6` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-14-1-9` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-14-2-1` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-14-3-1` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-14-4-1` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-14-4-3` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-14-4-10` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-14-5-1` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `kategori-14-5-10` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-15-1-3` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `mcma-15-2-7` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `mcma-15-2-8` | HOLD_SOURCE | Sudut40/65/75 derajat tidak konsisten dengan AB6 dan BC10: AB berhadapan75 tetapi lebih pendek daripada BC yang berhadapan40. Usulan sisi/sudut belum dipilih; HOLD. |
| `pg-15-3-3` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |
| `pg-15-4-2` | HOLD_SOURCE | SAS tidak terpenuhi, tetapi SSA khusus AB6 BC8 angleA40 menentukan satu segitiga; menolak kekongruenan hanya karena bukan SAS keliru. Usulan stem menilai alasan SAS, atau ganti ke SSA ambigu; perlu review. |
| `pg-15-5-3` | DEFERRED_CONCEPTUAL | Definisi/kesimpulan tetap; template konseptual setara belum disepakati. |

[Laporan audit dan batas stok](../docs/audits/2026-10-05-drill-11-15-generator-audit.md).
