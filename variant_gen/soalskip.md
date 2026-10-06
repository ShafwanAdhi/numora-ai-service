# Soal tanpa generator

## Pembaruan stok konseptual — lengkap 6 Oktober 2026

**67/67 original konseptual Drill telah memiliki 206 varian manual VERIFIED**, bukan generator. Dua puluh soal mempunyai empat varian, 32 mempunyai tiga, 15 mempunyai dua. Semua 67 telah dibandingkan dengan original untuk variasi dan beban tugas; hasil review/perbaikan serta alasan pembatasan: [audit lengkap](../docs/audits/2026-10-06-conceptual-stock-audit.md).

`same_answer_as_original` berlaku pada generator numerik, tetapi dikecualikan khusus stok konseptual. Status metadata dan alasan historis di bawah dipertahankan sebagai riwayat. DEFERRED_CONCEPTUAL menolak generator/config; stok VERIFIED tetap dapat dibaca. Penggunaan ulang tidak menghabiskan stok.

Rekonsiliasi Drill: 646 generator + 67 original dengan stok + 77 review sumber = 790. Masih 144 Drill tanpa **generator**, namun hanya77 belum memiliki generator maupun stok. Tiga Tryout tanpa generator/stok tetap di luar cakupan konseptual Drill.

| ID konseptual | Stok VERIFIED |
|---|---:|
| `kategori-1-1-10` | 3 |
| `kategori-1-2-10` | 4 |
| `kategori-1-3-10` | 4 |
| `kategori-10-2-10` | 3 |
| `kategori-11-1-9` | 4 |
| `kategori-11-2-9` | 4 |
| `kategori-12-3-10` | 3 |
| `kategori-14-1-9` | 3 |
| `kategori-14-4-10` | 3 |
| `kategori-14-5-10` | 3 |
| `kategori-16-1-9` | 3 |
| `kategori-16-2-9` | 3 |
| `kategori-17-3-10` | 3 |
| `kategori-20-1-10` | 3 |
| `kategori-20-1-9` | 4 |
| `kategori-20-2-10` | 4 |
| `kategori-6-3-9` | 3 |
| `kategori-7-1-10` | 2 |
| `kategori-7-2-10` | 3 |
| `kategori-9-1-10` | 4 |
| `mcma-1-1-8` | 4 |
| `mcma-11-1-8` | 4 |
| `mcma-11-2-6` | 4 |
| `mcma-11-5-6` | 4 |
| `mcma-14-1-6` | 4 |
| `mcma-15-2-7` | 3 |
| `mcma-16-1-6` | 3 |
| `mcma-20-1-6` | 3 |
| `mcma-20-2-7` | 2 |
| `mcma-20-3-8` | 3 |
| `mcma-22-1-8` | 2 |
| `mcma-22-2-8` | 2 |
| `mcma-6-1-6` | 4 |
| `mcma-6-2-6` | 4 |
| `mcma-6-3-6` | 4 |
| `pg-1-1-4` | 3 |
| `pg-11-1-1` | 4 |
| `pg-12-2-4` | 3 |
| `pg-14-1-1` | 4 |
| `pg-14-2-1` | 3 |
| `pg-14-3-1` | 3 |
| `pg-14-4-1` | 3 |
| `pg-14-4-3` | 2 |
| `pg-14-5-1` | 3 |
| `pg-15-1-3` | 2 |
| `pg-15-3-3` | 2 |
| `pg-15-5-3` | 3 |
| `pg-16-1-1` | 2 |
| `pg-16-1-2` | 3 |
| `pg-16-3-2` | 2 |
| `pg-17-3-2` | 3 |
| `pg-2-2-5` | 2 |
| `pg-2-3-1` | 4 |
| `pg-2-3-4` | 3 |
| `pg-2-3-5` | 2 |
| `pg-20-1-1` | 4 |
| `pg-20-2-1` | 2 |
| `pg-20-3-5` | 3 |
| `pg-21-2-5` | 2 |
| `pg-22-1-4` | 3 |
| `pg-22-2-3` | 3 |
| `pg-22-2-5` | 3 |
| `pg-22-3-5` | 3 |
| `pg-23-1-1` | 2 |
| `pg-23-1-2` | 2 |
| `pg-5-2-4` | 3 |
| `pg-7-3-1` | 4 |

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

## Drill Paket 1, indikator 20–23 — alasan ditinjau ulang 6 Oktober 2026

**34 soal belum memiliki generator: 11 konflik sumber dan 23 soal yang desain variannya belum diimplementasikan.** Status di bawah mengikuti metadata saat ini. `DEFERRED_CONCEPTUAL` adalah label penundaan sistem; sebagian soal berlabel ini tetap memerlukan perhitungan dan bukan soal murni konseptual.

Alasan dibedakan menjadi masalah pada original dan kekurangan generator. Jawaban tetap bukan bukti bahwa soal tidak dapat dibuat variannya. Varian konseptual dapat memakai stok template terbatas, sesuai pilihan pengguna sebelumnya. Untuk ID yang sudah tersedia pada tabel pembaruan, stok manual kini dapat dibaca ulang tanpa habis; sisanya menunggu tahap kedua.

Aturan generator saat ini, `same_answer_as_original`, menolak kandidat dengan teks jawaban benar yang sama dengan original. Aturan ini menjelaskan penolakan teknis, bukan ketidaklayakan akademik suatu varian. Mengganti nama atau mengacak opsi saja tidak cukup; stimulus, pernyataan, dan alasan jawabannya perlu dirancang bersama.

Nomor sumber mengikuti dokumen (1–30 per indikator); nomor dalam ID lokal mengikuti level (1–10). Kolom langkah berikut merupakan usulan, belum diterapkan pada original/config.

### Indikator 20: pengumpulan dan penyajian data

| ID lokal / nomor sumber | Status | Alasan spesifik | Langkah berikut |
|---|---|---|---|
| `pg-20-1-1` / 1 | DEFERRED_CONCEPTUAL | Pertanyaan menilai kecocokan instrumen dengan tujuan survei olahraga favorit. Tidak ada angka untuk diacak; generator skenario dan opsi survei belum dibuat. | Siapkan stok tujuan survei dan empat pertanyaan terkait; tepat satu pertanyaan langsung mengukur tujuan. |
| `mcma-20-1-6` / 6 | DEFERRED_CONCEPTUAL | Pertanyaan 1, 2, dan 4 mengukur kebiasaan internet untuk belajar; pertanyaan tentang penemu internet tidak relevan. Mengganti durasi saja tidak mengubah relevansi. | Variasikan tujuan dan isi empat pertanyaan dalam template terbatas; pertahankan tiga pertanyaan relevan. |
| `kategori-20-1-9` / 9 | DEFERRED_CONCEPTUAL | Jam belajar dan jumlah saudara menghasilkan data kuantitatif; mata pelajaran favorit menghasilkan data kualitatif. Generator belum memiliki bank pertanyaan beserta jenis datanya. | Buat stok pertanyaan numerik/kategori; setiap pertanyaan memiliki label Kuantitatif atau Kualitatif yang eksplisit. |
| `kategori-20-1-10` / 10 | DEFERRED_CONCEPTUAL | Pernyataan tentang fungsi diagram batang, tabel, dan diagram lingkaran merupakan fakta konsep. Original tidak memiliki parameter numerik. | Susun stok pernyataan benar/salah tentang kegunaan penyajian data; setiap kombinasi diperiksa beserta pembahasannya. |
| `pg-20-2-1` / 11 | DEFERRED_CONCEPTUAL | Tujuan meminta alasan memilih sepeda motor; hanya opsi B langsung menanyakan alasan. Penggantian merek atau harga tidak menghasilkan tugas baru. | Variasikan keputusan yang diteliti dan empat pertanyaannya; bedakan alasan dari kepemilikan, atribut, dan biaya. |
| `mcma-20-2-7` / 17 | DEFERRED_CONCEPTUAL | Original meminta penyajian jumlah peminat ekstrakurikuler: batang, lingkaran, dan tabel diterima; paragraf tanpa angka tidak memadai. Mengganti jumlah peminat tidak mengubah isi opsi. | Buat template tujuan penyajian beserta opsi yang sesuai. Untuk diagram lingkaran, nyatakan kategori membentuk bagian dari keseluruhan yang sama. |
| `kategori-20-2-10` / 20 | DEFERRED_CONCEPTUAL | Frekuensi membawa bekal dan kebiasaan membawa bekal relevan; makanan favorit dan uang saku tidak langsung mengukur tujuan. Generator tujuan/pertanyaan belum tersedia. | Siapkan stok empat pertanyaan per tujuan, masing-masing dengan label Sesuai/Tidak Sesuai; pertahankan jumlah pernyataan original. |
| `pg-20-3-3` / 23 | HOLD_SOURCE | Nilai baru = 6 × 85 − 400 = 110. Opsi C dan D sama-sama 110, sehingga PG memiliki dua jawaban benar. | Usulan DOCX: opsi 100, 105, 110, 115; kunci C. Catat koreksi original sebelum membuat generator mean/data tambahan. |
| `pg-20-3-5` / 25 | DEFERRED_CONCEPTUAL | Penelitian hubungan waktu media sosial dan waktu belajar membutuhkan dua pengukuran durasi. Hanya opsi C memuat keduanya; generator pasangan variabel belum dibuat. | Variasikan pasangan variabel dan instrumen pengukurannya; satu opsi harus memperoleh kedua data pada responden yang sama. |
| `mcma-20-3-8` / 28 | DEFERRED_CONCEPTUAL | Tiga pertanyaan mengukur kepuasan atas fasilitas perpustakaan; warna favorit tidak relevan. Tidak tersedia generator aspek kepuasan dan distractor. | Susun stok objek layanan, tiga aspek kepuasan relevan, serta satu pertanyaan di luar tujuan. |

### Indikator 21: ukuran pemusatan dan penyebaran

| ID lokal / nomor sumber | Status | Alasan spesifik | Langkah berikut |
|---|---|---|---|
| `pg-21-2-2` / 12 | HOLD_SOURCE | Bilangan kelima = 5 × 72 − (65 + 70 + 75 + 80) = 70. Opsi C dan D identik, sehingga jawaban PG tidak unik. | Usulan DOCX: opsi 65, 68, 70, 75; kunci C. Revisi opsi/kunci lalu parameterkan mean dan empat bilangan. |
| `pg-21-2-5` / 15 | DEFERRED_CONCEPTUAL | Pada data 1, 2, 2, 3, 7, pertanyaan meminta ukuran yang paling dipengaruhi pencilan, yaitu Mean. Angka dapat divariasikan, tetapi teks jawaban tetap ditolak aturan generator saat ini. | Rancang template interpretasi pencilan dengan pembahasan dampak pada mean/median/modus; tentukan perlakuan varian dengan jawaban konsep tetap. |
| `pg-21-3-1` / 21 | HOLD_SOURCE | Stimulus menyebut nilai siswa baru 90, tetapi mean baru mengharuskan 7 × 77 − 6 × 75 = 89. Stimulus dan perhitungan bertentangan. | Hapus informasi nilai 90 yang sedang ditanyakan; pertahankan data mean dan kunci C = 89 setelah revisi dicatat. |
| `pg-21-3-4` / 24 | HOLD_SOURCE | Data baru 60, 65, 70, 75, 90 memiliki mean 360/5 = 72. Opsi 74, 75, 76, 78 tidak memuat hasil benar. | Usulan DOCX: opsi 72, 74, 76, 78; kunci A. Revisi opsi sebelum membuat generator perubahan satu nilai. |
| `pg-21-3-5` / 25 | HOLD_SOURCE | B benar (median 75 < 80), C benar (jangkauan 10 < 30), dan D benar (modus A = 75 dan 80; B = 80). Frasa “paling tepat” tidak menentukan satu jawaban. | Jika tetap PG dengan kunci C, ubah B dan D menjadi klaim yang jelas salah; periksa ulang seluruh opsi. |
| `mcma-21-3-8` / 28 | HOLD_SOURCE | Setelah 50 diganti 90, median berubah 60 menjadi 70; modus tetap 60; jangkauan tetap 30; jumlah data tetap 5. Seluruh pernyataan awal salah, bertentangan dengan kunci 1 dan 3. | Usulan DOCX: pernyataan 1 “Modus tetap 60”, pernyataan 3 “Nilai terbesar bertambah dari 80 menjadi 90”; keduanya benar. Catat revisi pernyataan. |
| `kategori-21-3-9` / 29 | HOLD_SOURCE | Mean = 520/7 ≈ 74,29, bukan 75,71. Pernyataan D salah, tetapi kunci sumber melabelinya Benar. | Usulan DOCX: kunci A/B Benar, C/D Salah; pertahankan isi pernyataan lalu revisi label D. |

### Indikator 22: perbandingan dua kelompok data

| ID lokal / nomor sumber | Status | Alasan spesifik | Langkah berikut |
|---|---|---|---|
| `pg-22-1-1` / 1 | HOLD_SOURCE | Jumlah A dan B masing-masing 400; mean keduanya 80. Kunci B “Mean B lebih besar” salah; opsi C sesuai perhitungan dan pembahasan. | Revisi kunci menjadi C, lalu buat generator relasi mean dengan opsi unik. |
| `pg-22-1-4` / 4 | DEFERRED_CONCEPTUAL | Pertanyaan meminta nama ukuran penyebaran, yaitu Jangkauan. Mengubah dataset tidak mengubah jawaban konsep tersebut. | Siapkan template memilih/menginterpretasikan ukuran statistik; jawaban konsep tetap memerlukan perlakuan stok template yang belum tersedia. |
| `mcma-22-1-6` / 6 | HOLD_SOURCE | Mean A = B = 6, sehingga pernyataan 1 salah. Median A = 5 < 6 dan jangkauan A = 6 > 4; hanya 2 dan 4 benar. | Usulan DOCX: revisi kunci menjadi 2 dan 4; setelah itu jumlah jawaban benar generator mengikuti original yang direvisi. |
| `mcma-22-1-7` / 7 | HOLD_SOURCE | Jumlah A = 370 dan B = 380; mean 74 dan 76. Pernyataan 1 salah; hanya pernyataan 3 (jangkauan sama-sama 30) benar. Pembahasan juga salah menjumlahkan B. | Revisi kunci menjadi 3 dan perbaiki pembahasan, atau revisi pernyataan jika ingin tetap dua jawaban benar; tentukan satu versi original. |
| `mcma-22-1-8` / 8 | DEFERRED_CONCEPTUAL | Ini soal numerik, bukan konsep murni. Original memiliki mean/median sama-sama 6, jangkauan B lebih besar, dan modus A = 5 serta 7. Menskalakan semua angka mempertahankan teks klaim benar 1, 2, dan 4; generator dataset dengan pola lain belum dibuat. | Variasikan dataset sekaligus pernyataan statistik yang dihitung, bukan sekadar menskalakan semua angka; audit pola benar/salah dan jumlah jawaban benar. |
| `pg-22-2-3` / 13 | DEFERRED_CONCEPTUAL | Stimulus A memiliki pencilan 50; pertanyaan memilih ukuran nilai tengah yang lebih stabil, yaitu Median. Generator pemilihan ukuran belum dibuat; skala angka saja mempertahankan teks jawaban. | Buat template dataset dengan pencilan dan alasan pemilihan ukuran; pastikan pilihan ukuran memiliki kriteria yang eksplisit. |
| `pg-22-2-5` / 15 | DEFERRED_CONCEPTUAL | Ini soal perbandingan numerik: jangkauan A = 8 dan B = 28. Hanya C memberi alasan konsistensi yang sah; jika B dibuat lebih konsisten, tidak ada opsi “B karena jangkauannya lebih kecil”. | Parameterkan kelompok dan jangkauan pada opsi alasan yang benar; sediakan distractor berbasis mean/maksimum yang tetap salah. |
| `mcma-22-2-8` / 18 | DEFERRED_CONCEPTUAL | Ini soal numerik. Pernyataan 1 (mean sama) dan 4 (mean B lebih besar) tidak bisa sama-sama benar. Pada dataset simetris yang dipakai, mean = median; mengubah mean juga menggugurkan pernyataan 2. Generator belum memodelkan dataset alternatif dengan tiga klaim benar. | Gunakan dataset yang tidak harus simetris atau parameterkan isi klaim; hitung mean, median, dan jangkauan masing-masing untuk memeriksa seluruh opsi. |
| `pg-22-3-5` / 25 | DEFERRED_CONCEPTUAL | Ini soal numerik: jangkauan A = 8 dan B = 44. Hanya B mengaitkan konsistensi dengan jangkauan; opsi lain tidak menyediakan alasan benar saat kelompok lebih konsisten berubah. | Parameterkan kelompok yang lebih konsisten dan isi opsi jangkauan; pertahankan dasar penilaian yang dinyatakan pada stimulus. |
| `mcma-22-3-8` / 28 | HOLD_SOURCE | Mean kedua kelompok 60, sehingga pernyataan 1 salah. Median sama-sama 60; jangkauan A = 40 dan B = 20. Hanya 3 dan 4 benar. | Usulan DOCX: revisi kunci menjadi 3 dan 4 sebelum membuat generator perbandingan dataset. |

### Indikator 23: peluang dan frekuensi relatif

| ID lokal / nomor sumber | Status | Alasan spesifik | Langkah berikut |
|---|---|---|---|
| `pg-23-1-1` / 1 | DEFERRED_CONCEPTUAL | Mengganti mata dadu 4 menjadi satu mata lain tetap menghasilkan 1/6 pada dadu seimbang. Generator belum memvariasikan banyak hasil yang memenuhi kejadian. | Parameterkan himpunan kejadian, misalnya genap atau lebih dari suatu angka; hitung banyak hasil/6 dan pastikan tepat satu opsi benar. |
| `pg-23-1-2` / 2 | DEFERRED_CONCEPTUAL | Mengganti sisi gambar menjadi angka pada koin seimbang tetap menghasilkan 1/2. Soal satu lemparan tidak memiliki parameter jumlah hasil yang bebas. | Gunakan stok template kejadian sederhana dengan ruang sampel eksplisit; penambahan jumlah lemparan harus diperiksa agar tingkat kesulitan tetap sesuai. |
| `pg-23-3-2` / 22 | DEFERRED_CONCEPTUAL | Ini soal interpretasi numerik: 106/200 = 0,53, selisih 0,03 dari 0,5. Kata “mendekati” tidak menetapkan batas untuk menilai seluruh kandidat baru; selain A, opsi lain tidak menjadi kesimpulan valid hanya dengan mengubah angka. | Tetapkan kriteria kedekatan pada stimulus/template dan rancang opsi kesimpulan alternatif; jangan menganggap semua rasio dekat berdasarkan ambang tersembunyi. |
| `pg-23-3-5` / 25 | DEFERRED_CONCEPTUAL | Ini soal numerik dengan hasil pasti: 35/240 < 1/6. Untuk rasio lebih besar, opsi A memakai “jauh lebih besar” tanpa batas; untuk rasio sama persis, opsi B sudah dapat menjadi jawaban benar. Kemampuan membuat kandidat baru belum diuji, bukan bukti soal tidak dapat digenerasikan. | Uji kandidat frekuensi relatif = peluang teoretis (jumlah lemparan kelipatan 6, kemunculan = n/6); jika memakai kasus lebih besar, ganti “jauh lebih besar” dengan perbandingan eksplisit. |
| `mcma-23-3-7` / 27 | DEFERRED_CONCEPTUAL | Ini soal numerik: 212/400 = 0,53; opsi 1 benar dan 2 salah. Klaim 3 “mendekati 0,5” belum memiliki batas untuk kandidat baru. Peluang teoretis tidak berubah menjadi rasio hasil percobaan pada opsi 4. | Parameterkan banyak percobaan, kemunculan, dan dua rasio opsi; berikan kriteria kedekatan eksplisit serta hitung semua klaim. |
| `mcma-23-3-8` / 28 | DEFERRED_CONCEPTUAL | Ini soal numerik: 247/500 = 0,494, komplemennya 0,506. Klaim 3 memakai “mendekati” tanpa batas; klaim 4 merupakan rumus yang tetap benar. Generator rasio dan penilaian kedekatan belum tersedia. | Parameterkan n dan kemunculan; turunkan rasio/komplemen serta aturan kedekatan. Pertahankan rumus frekuensi relatif dan tiga jawaban benar. |
| `kategori-23-3-9` / 29 | DEFERRED_CONCEPTUAL | Ini soal numerik: 147/300 = 0,49, sedangkan peluang ganjil = 3/6 = 0,5. Klaim B memakai “mendekati” tanpa batas; klaim C menyamakan peluang teoretis dengan rasio empiris. | Parameterkan hitungan dan nilai rasio pernyataan A/C; jelaskan kriteria kedekatan untuk B. Klaim D tentang hasil yang tidak harus persis sama tetap dipertahankan. |

Untuk `HOLD_SOURCE`, selesaikan konflik stimulus/opsi/kunci/pembahasan dan catat versi original yang dipilih sebelum generasi. Beberapa DOCX sudah memuat usulan koreksi; tabel menyebutkannya secara eksplisit tanpa menerapkannya otomatis.

Untuk `DEFERRED_CONCEPTUAL`, kerjakan desain generator atau stok template sesuai kendala per soal. Label penundaan saat ini tidak menyatakan bahwa semua 23 soal murni konseptual atau mustahil dibuat variannya. Status, metadata, serta hasil audit lama belum diubah oleh revisi dokumentasi ini.

[Audit sebelumnya dan stok generator aktif](../docs/audits/2026-10-05-drill-20-23-generator-audit.md).

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

## Drill Paket1 indikator1–2, level1–3 — 5 Oktober 2026

60 original;34 generator aktif;17 HOLD_SOURCE;9 DEFERRED_CONCEPTUAL. Tidak menerapkan usulan koreksi dari pembahasan DOCX. Indikator3–5 belum diimpor; level4–5 di luar scope.

| ID | Status | Alasan | Syarat aktivasi |
|---|---|---|---|
| `pg-1-1-4` | DEFERRED_CONCEPTUAL | Sifat Distributif tetap menjadi teks jawaban benar; perubahan nominal saja tidak lolos same_answer_as_original. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `pg-1-1-5` | HOLD_SOURCE | Pembahasan DOCX menulis Wadah X:3,5°C dan -13/4=3,25°C, bertentangan dengan stimulus -3,5°C dan hasil -3,25°C. Tanda minus pembahasan perlu disahkan; tidak dikoreksi diam-diam. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `mcma-1-1-8` | DEFERRED_CONCEPTUAL | Empat klaim sifat operasi universal tetap; tidak ada parameter numerik yang mengubah jawaban substantif. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `kategori-1-1-10` | DEFERRED_CONCEPTUAL | Klaim sifat distributif/komutatif tetap, teks jawaban benar tidak berubah oleh nominal transaksi. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `pg-1-2-1` | HOLD_SOURCE | Kerugian paling besar adalah Kelompok3 (-0,62), bukan PakDimas (-3/5=-0,60). | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-1-2-3` | HOLD_SOURCE | Opsi B dan C sama-sama benar: sqrt2>0 dan -4/3<-1,3<-1,25; PG tidak unik. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `mcma-1-2-6` | HOLD_SOURCE | Header A,B,C; nilai -sqrt(8) paling dingin sehingga klaim B salah. Pembahasan eksplisit menyimpulkan A,C. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `kategori-1-2-10` | DEFERRED_CONCEPTUAL | Hipotesis struktur bilangan universal tetap; template konseptual setara belum tersedia. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `pg-1-3-1` | HOLD_SOURCE | Urutan benar -2,65 < -sqrt7 < -13/5 < -2,4; AnalisisII menukar dua nilai pertama, tidak ada opsi urutan benar. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-1-3-5` | HOLD_SOURCE | Opsi A,B,D benar: r=-2,35 < p=-2,25 < q=-sqrt5; PG tidak unik. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `mcma-1-3-6` | HOLD_SOURCE | Header A,B,C; W=Y=-3,2 lebih kecil dari X=-sqrt(10), sehingga klaim B salah. Pembahasan menyimpulkan A,C. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `kategori-1-3-10` | DEFERRED_CONCEPTUAL | Hipotesis struktur bilangan universal tetap; template konseptual setara belum tersedia. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `pg-2-1-1` | HOLD_SOURCE | Saldo dari stimulus 38.500 tidak ada pada opsi; header B=18.500 mengikuti usulan revisi saldo awal dalam pembahasan. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-1-2` | HOLD_SOURCE | Nilai benar 49, opsi B dan C duplikat, header C menyebut 19. PG tidak memiliki jawaban unik. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-1-3` | HOLD_SOURCE | Diagonal dari stimulus 2sqrt(30), tidak ada pada opsi. Pembahasan mengusulkan beberapa rekonstruksi, bukan original final tunggal. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-1-5` | HOLD_SOURCE | Tagihan setelah diskon 104.000 sedangkan pembayaran 100.000; tidak ada kembalian positif 42.000. Pembahasan mengusulkan perubahan jumlah barang/pembayaran/diskon. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-2-1` | HOLD_SOURCE | Perhitungan dan opsi B=51.500 cocok, tetapi caption header B menyebut 21.500. Perbedaan klaim kunci sumber harus dicatat/disahkan. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-2-2` | HOLD_SOURCE | 3sqrt(20)-sqrt(45)=3sqrt(5) pada opsi A, bukan header B=4sqrt(5); hasil akhir pembahasan memuat akar kosong. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-2-4` | HOLD_SOURCE | Opsi B dan C sama-sama LangkahII; header C juga memuat ekspresi, bukan nama langkah. PG duplikat. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-2-5` | DEFERRED_CONCEPTUAL | Jawaban berupa alasan distributif AnalisisI tetap; recipe mengubah siapa yang benar perlu rancangan langkah alternatif. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `mcma-2-2-6` | HOLD_SOURCE | Kebenaran i,ii,iv adalah A,B,D, bukan header A,C,D; 3^(2*3)=729 bukan243. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `mcma-2-2-7` | HOLD_SOURCE | Klaim D metode lebih efisien tidak menentukan ukuran efisiensi; kedua metode memakai dua operasi. Kriteria penilaian perlu disahkan. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |
| `pg-2-3-1` | DEFERRED_CONCEPTUAL | Jawaban berupa alasan tanda cashback AnalisisII tetap; perubahan nominal tidak mengubah teks jawaban benar. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `pg-2-3-4` | DEFERRED_CONCEPTUAL | Jawaban SiswaC tetap; variasi langkah antar siswa yang mengubah jawaban substantif belum dirancang. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `pg-2-3-5` | DEFERRED_CONCEPTUAL | Jawaban berupa alasan distributif AnalisisI tetap; perubahan nominal tidak mengubah teks jawaban benar. | Desain template setara dengan jawaban substantif berubah; audit seluruh opsi. |
| `mcma-2-3-6` | HOLD_SOURCE | Header A,C,D bertentangan dengan kebenaran i,ii,iv: A,B,D. Pembahasan menyebut koreksi kunci eksplisit. | Original/opsi/kunci atau aturan penilaian perlu disahkan, lalu audit ulang. |

## Drill Paket1 indikator3–5, level1–3 — 6 Oktober 2026

90 original;64 aktif;25 HOLD_SOURCE;1 DEFERRED_CONCEPTUAL. Tidak mengoreksi akademik sumber.

| ID | Status | Alasan | Syarat aktivasi |
|---|---|---|---|
| `pg-3-1-2` | HOLD_SOURCE | Lahan persegi luas45m2 mempunyai diagonal sqrt(90), bukan sqrt(45); premis geometri bertentangan dengan besaran yang diminta. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-3-1-3` | HOLD_SOURCE | Stem hanya membulatkan harga satuan:3,25*25.000=81.250 tidak ada pada opsi. Pembahasan menambahkan pembulatan total tanpa instruksi stem. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-3-1-5` | HOLD_SOURCE | Aturan pembulatan operand menghasilkan20*7.000=140.000 tetapi kunci130.000 memakai pembulatan hasil riil; aturan estimasi tidak tunggal. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-3-2-2` | HOLD_SOURCE | Lahan persegi luas52m2 mempunyai diagonal sqrt(104), bukan sqrt(52); premis geometri bertentangan dengan panjang papan. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-3-2-3` | HOLD_SOURCE | Pembulatan harga satuan menghasilkan3,5*25.000=87.500 tanpa opsi yang sesuai. Pembahasan menambahkan pembulatan total dan mengizinkan87.000/88.000; kunci87.000 tidak tunggal. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-3-2-4` | HOLD_SOURCE | Hasil riil59,4*19,8/9,7=121,249484... membulat menjadi121,25. Stem dan opsi B menyatakan121,26; pembahasan menyatakan121,25. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `mcma-3-2-7` | HOLD_SOURCE | Luas ubin persegi20,32,48cm2 disamakan dengan diagonal sqrt(20),sqrt(32),sqrt(48); diagonal seharusnya sqrt(dua kali luas). | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `mcma-3-2-8` | HOLD_SOURCE | Opsi C menyatakan semua komponen dibulatkan ke atas, tetapi12 botol dibulatkan menjadi10. Klaim alasan yang dikunci benar adalah salah. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-3-2-9` | HOLD_SOURCE | Kunci sumber menyatakan(b) SALAH, tetapi2,45 dibulatkan ke satuan menjadi2 sehingga(b) BENAR. Instruksi koreksi dalam pembahasan tidak diterapkan. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-3-3-3` | HOLD_SOURCE | Total riil415.800. Opsi C450.000 dan D420.000 sama-sama batas atas aman; D lebih dekat. Stem tidak mensyaratkan kedua operand dibulatkan ke atas, sehingga kunci C tidak tunggal. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-4-1-1` | HOLD_SOURCE | Header kunci B menyebut12 hari; KPK(12,18)=36 hari sesuai opsi C dan pembahasan. Kunci akademik perlu disahkan. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `mcma-4-1-8` | HOLD_SOURCE | Stem tidak menetapkan jumlah kantong maksimum.14 kantong sama isi sah memuat6 buku,4 pensil,2 penggaris;3 buku per kantong hanya berlaku jika memakai28 kantong. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-4-1-9` | HOLD_SOURCE | Stem tidak menetapkan jumlah piring maksimum.9 piring sama isi sah memuat8 bolu dan10 lapis; selisih2, bukan1 pada kunci. Pembahasan mengasumsikan18 piring. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-4-1-10` | HOLD_SOURCE | Stem meminta potongan sama panjang, tanpa syarat terpanjang. Potongan5cm menghasilkan9 potongan dari pita pertama, bukan3. Kunci mengasumsikan panjang15cm. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-4-2-2` | HOLD_SOURCE | Beras,gula,minyak dapat dibagi dalam massa pecahan. Tanpa syarat isi tiap paket berupa kg bulat, jumlah paket tidak mempunyai maksimum12 seperti kunci. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-4-2-5` | HOLD_SOURCE | Caption header C menyebut2^2*3=12, tetapi opsi C dan pembahasan2^2*3^2=36. Instruksi koreksi dalam DOCX adalah konten sumber, bukan izin mengganti kunci akademik. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `mcma-4-2-8` | HOLD_SOURCE | Stem tidak menetapkan jumlah ruangan maksimum.12 ruangan sama isi sah mendapat6 tetikus dan8 papan ketik; kunci3 dan4 mengasumsikan24 ruangan. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-4-2-9` | HOLD_SOURCE | Stem tidak menetapkan jumlah kardus maksimum.9 kardus sama isi sah memuat6 botol apel dan8 jeruk; total14, bukan7. Kunci mengasumsikan18 kardus. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-4-2-10` | HOLD_SOURCE | Stem meminta potongan sama panjang, tanpa syarat terpanjang. Pita60/90cm dipotong15cm menghasilkan10 potongan, bukan5. Kunci mengasumsikan panjang30cm. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-4-3-1` | HOLD_SOURCE | Analisis I dan III sama-sama benar:60 hari setelah1 Maret adalah30 April. PG tidak boleh memilih III saja. Stem juga menyebut3 analisis tetapi mencantumkan4. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `mcma-4-3-8` | HOLD_SOURCE | Stem tidak menetapkan jumlah kelompok maksimum.8 kelompok sama isi sah mendapat10 pak kertas dan14 botol; kunci5 dan7 mengasumsikan16 kelompok. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-4-3-9` | HOLD_SOURCE | Stem tidak menetapkan jumlah kotak maksimum.6 kotak sama isi sah memuat10 mikroskop dan14 kaca; total24, bukan12. Kunci mengasumsikan12 kotak. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `kategori-4-3-10` | HOLD_SOURCE | Stem meminta potongan sama panjang, tanpa syarat terpanjang. Pita75/105cm dipotong5cm menghasilkan36 potongan, bukan12. Kunci mengasumsikan panjang15cm. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-5-1-5` | HOLD_SOURCE | Stem/opsi B/pembahasan meminta6liter, caption header B menyebut240kilometer. Unit dan makna kunci bertentangan. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
| `pg-5-2-4` | DEFERRED_CONCEPTUAL | Jawaban original AnalisisII tetap. Mengubah harga agar AnalisisI benar mengesahkan alasan membandingkan harga total tanpa harga satuan; profil unit setara membuat opsi C dan D sama-sama benar. Template analisis alternatif setara belum tersedia. | Rancang analisis alternatif setara tanpa mengesahkan alasan salah atau beberapa opsi PG benar. |
| `pg-5-3-3` | HOLD_SOURCE | Selisih debit4liter/menit pada opsi B; caption header B menyebut24liter/menit yaitu debitQ, bukan selisih. | Sahkan stimulus/opsi/kunci/pembahasan atau asumsi pembagian, lalu audit ulang. |
