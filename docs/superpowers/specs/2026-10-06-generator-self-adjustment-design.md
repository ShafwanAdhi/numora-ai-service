# Rancangan penyesuaian otomatis tiap generator

Tanggal rancangan: 6 Oktober 2026. Diperbarui: **7 Oktober 2026**, berdasarkan bank, konfigurasi, dan pemeriksaan terbaru di repo lokal. **Penyesuaian otomatis masih usulan**, belum diterapkan atau diaktifkan untuk penggunaan nyata.

## Tujuan dan keputusan pengguna

Ketika data jawaban siswa cukup dapat dipercaya dan hasil perhitungan menunjukkan varian berbeda dari soal asli yang masih stabil, service AI akan mencoba pengaturan baru yang sudah diizinkan. Sistem membuat calon varian pengganti, memeriksanya, mengumpulkan jawaban siswa, lalu menghitung dan membandingkan hasilnya kembali.

Pengguna memilih **aktivasi otomatis setelah seluruh pemeriksaan lolos menurut aturan yang sudah disetujui sebelumnya**. Aturan dan pilihan pengaturannya disetujui sebelum otomatisasi berjalan; persetujuan tidak perlu diminta ulang untuk setiap percobaan.

Dalam rancangan otomatisasi, soal asli, hasil perhitungan lama, calon varian yang gagal, riwayat pengerjaan, dan skor lama tidak ditimpa. Pekerjaan generator yang sudah berjalan telah menambahkan revisi soal lokal dengan versi baru, konfigurasi generator, pemeriksaan matematika, serta dukungan penampilan rumus; perubahan tersebut berbeda dari penerapan penyesuaian otomatis. Pembaruan dokumen ini tidak mengubah program, Numora, `.env`, atau database. Akses database saat ini tetap hanya membaca. Program penulisan data, penerimaan hasil perhitungan di service AI, uji coba siswa, dan aktivasi otomatis belum dibuat.

## Kondisi repo saat ini

- Ada **679 generator Drill dari 790 soal asli**, naik 33 dari 646 pada rancangan awal. Dari masukan yang bisa dipilih langsung, **364 generator hanya memakai `k`**, **30 hanya memakai `k,t`**, dan **285 memakai masukan lain**. Angka dihitung dari konfigurasi terbaru tiap ID, tanpa menghitung beberapa versi sebagai beberapa generator. Nama dan jumlah masukan tidak membuktikan pengaruhnya terhadap kesulitan.
- Program generator sudah mendukung rentang angka (`range`), daftar pilihan (`choice`), perubahan skala (`scale`), nilai yang dihitung dari angka lain, syarat hasil, pembuatan ulang soal asli, dan pengaturan dengan beberapa versi. Repo AI belum memiliki program penilaian kesulitan berdasarkan jawaban siswa, penyesuaian otomatis, atau kumpulan data uji coba siswa.
- `ConfigStore.load()` langsung memilih versi pengaturan terbaru. Pengaturan percobaan yang dimasukkan ke folder aktif akan langsung dipakai untuk membuat soal, walaupun hasilnya belum diuji. Karena itu, pengaturan percobaan harus disimpan terpisah dari pengaturan aktif.
- `pg-21-1-1`: pilihan `k` adalah `0.5`, `1`, `1.5`, dan `2`; rentang `t` adalah −60 sampai 60. `k=0.5` dan `k=1.5` melanggar syarat bilangan bulat. Dengan batas `t` tersebut, `k=2` tidak bisa membuat kelima nilai berada dalam batas 0 sampai 100. Hanya `k=1` yang memenuhi syarat. Pemeriksaan 100 angka awal (`seed` 1 sampai 100) menghasilkan `k=1` pada seluruh soal. Mengubah peluang pemilihan atau rentang `k` saja tidak efektif untuk penyesuaian.
- `pg-18-3-1`: masukan berupa `r1` dan `k`, dengan jawaban perbandingan luas `k²`. Jari-jari dapat saling menghapus dalam perbandingan, sehingga perubahan jari-jari belum tentu mengubah kesulitan. Pemeriksaan 100 angka awal menghasilkan `k=4`, `k=5`, atau `k=6`; pengaruhnya terhadap kesulitan belum diukur.
- `pg-7-1-1`: banyak nilai dihitung dengan mengalikan angka lain dengan `k`. Jumlah digit atau beban perhitungan mungkin berubah, tetapi pilihan `k` yang banyak belum membuktikan arah perubahan kesulitan atau perubahan kemampuan yang diuji.
- Ada 67 soal asli konseptual dengan 206 varian stok manual. Soal ini tidak memakai generator angka, sehingga tidak diberi pengaturan angka buatan seolah-olah bisa disesuaikan otomatis.

Rekonsiliasi Drill: **679 generator + 67 soal dengan stok manual + 44 soal tanpa keduanya = 790 soal**. Tidak ada tumpang tindih generator dan stok pada hitungan ini. Tryout mempunyai 27 generator dari 30 soal; total kedua aktivitas 706 generator dari 820 soal. Status metadata saja tidak dijadikan bukti bahwa generator tersedia; hitungan memeriksa berkas konfigurasi dan stok yang dapat dimuat.

### Perubahan sumber dan generator sejak rancangan awal

| Cakupan | Generator sekarang | Perubahan yang sudah tersedia | Dampak pada rancangan penyesuaian |
|---|---:|---|---|
| Indikator 1–2 | 34/60 | 17 soal asli menjadi versi 2; belum ditambah generator | Aturan penyesuaian lama tidak langsung berlaku untuk isi revisi. |
| Indikator 3–5 | 64/90 | 24 soal asli menjadi versi 2; belum ditambah generator | Selesaikan generator dan catatan materi terlebih dahulu. Level 4–5 tidak ditambahkan pada bank 1–5. |
| Indikator 6–10 | 140/150 | 11 generator baru untuk soal asli versi 2 | Semua memakai faktor `k` bilangan bulat positif 1–40; pengaruh skalanya terhadap beban pengerjaan belum diukur pada siswa. |
| Indikator 11–15 | 227/250 | 4 generator baru untuk soal asli versi 2 | Masukan angka, nama himpunan, dan nama titik perlu dibedakan menurut kegunaannya; nama saja bukan pengatur kesulitan. |
| Indikator 16–19 | 112/120 | 2 generator sifat transformasi untuk soal asli versi 2 | Faktor transformasi dan posisi pernyataan salah mengubah isi klaim; jangan diperlakukan sebagai pembesaran angka biasa. |
| Indikator 20–23 | 102/120 | 16 generator baru untuk soal asli versi 2 | Ada pergeseran data, pilihan pola data, banyak percobaan, dan frekuensi; tiap masukan memerlukan pemeriksaan pengaruh yang berbeda. |

Sebanyak **40 soal revisi indikator 1–5 belum mempunyai generator**, meskipun sumber barunya sudah diimpor. Label `DEFERRED_CONCEPTUAL` pada kelompok ini berarti ditunda oleh program, bukan penetapan bahwa soalnya konseptual atau memiliki stok manual. Catatan alasan pilihan jawaban salah pada enam soal tetap perlu ditinjau sebelum membuat pembahasan generator.

Empat soal masih ditahan karena masalah sumber: `pg-1-2-1`, `pg-5-3-3`, `mcma-6-3-7`, dan `mcma-15-2-8`. Soal tersebut tidak masuk percobaan penyesuaian. Memperbaiki sumber berarti membuat revisi soal terlebih dahulu, bukan mencari angka lain untuk menutupi kesalahan.

Revisi dicatat melalui `original_revisions.jsonl`; CSV dan arsip sumber sebelumnya tetap tersedia. Konfigurasi baru mengacu pada penanda isi original yang sudah diperbarui. Pemeriksaan mencakup pembuatan ulang original, opsi dan kunci dari teks hasil, batas masukan, pengulangan `seed`, serta akses melalui UI/CLI. Hasil generator diberikan sebagai respons tanpa menyimpan varian siswa. Contoh dan laporan yang disimpan untuk pemeriksaan lokal bukan data kalibrasi atau soal yang sudah diaktifkan di Numora.

Perubahan penampilan rumus kini membedakan nama variabel dari kelompok angka dan nama lingkungan LaTeX. Ini membantu menampilkan soal matriks dengan benar, tetapi bukan masukan untuk mengubah kesulitan.

### Status pemeriksaan masukan

**Audit statis masukan 679 generator selesai pada 7 Oktober 2026:** 1.027 masukan langsung dicatat per generator dengan versi/hash original/config, daftar nilai efektif setelah seluruh penyaringan, kapasitas konten berbeda, jalur dependensi, pembanding dengan masukan lain tetap, dan status persetujuan. Sebanyak 677 domain diperiksa dengan enumerasi penuh; dua domain terbesar mempunyai bukti kapasitas/proyeksi analitik yang dibandingkan dengan enumerasi domain kecil. [Laporan dan batas kesimpulan](../../audits/2026-10-07-generator-input-audit.md), [JSON lengkap](../../audits/2026-10-07-generator-input-audit.json), [CSV per masukan](../../audits/2026-10-07-generator-input-audit.csv).

Pengelompokan utama: 900 masukan angka berpotensi memengaruhi beban, 32 pemilih profil isi untuk review, 72 konteks angka, dua nama himpunan/titik, dan 21 masukan tanpa pilihan efektif atau tanpa perubahan isi. Kelompok kelayakan, pengaruh, tampilan, dan izin tetap dicatat terpisah: semua masukan mempunyai bukti kandidat sesuai aturan runtime, tetapi **nol kontrol penyesuaian otomatis disetujui atau diaktifkan**. Pengaruh statis tetap berlabel PROPOSED; pemeriksaan matematika dan indikator digit bukan bukti kesetaraan kesulitan siswa. Empat HOLD dikecualikan dan 40 revisi tanpa generator tetap dalam antrean.

| Kelompok pemeriksaan | Bukti yang diperlukan | Temuan awal dari pembaruan repo |
|---|---|---|
| Masukan yang menghasilkan soal sesuai syarat | Soal, seluruh opsi, kunci, dan pembahasan benar dalam batas yang ditetapkan | Generator revisi mempunyai pemeriksaan tersendiri; tetap periksa hasil setelah penyaringan dan rentang yang benar-benar terpakai. |
| Masukan yang berpotensi mengubah beban pengerjaan | Perubahan digit, perkalian, pecahan, pola data, atau alasan yang perlu dibaca | Faktor skala 6–10, input fungsi 11–15, pilihan pola data 20–23, serta jumlah percobaan/frekuensi menjadi calon untuk diteliti. Arah perubahan kesulitan belum ditetapkan. |
| Masukan yang hanya mengubah tampilan angka atau konteks | Langkah dan hubungan yang diperlukan siswa tetap sama | Nama himpunan/titik hanya tampilan. Pergeseran seluruh data atau jari-jari yang saling menghapus dalam perbandingan juga belum tentu mengubah beban. |
| Belum menyediakan pilihan penyesuaian | Tidak ada pilihan yang disetujui untuk masalah yang ditemukan, atau pilihan tidak efektif | Seluruh generator belum mempunyai aturan penyesuaian otomatis yang disetujui; `k` pada `pg-21-1-1` tetap hanya efektif pada nilai 1. |

Kelompok tersebut merupakan empat pertanyaan pemeriksaan, bukan empat hitungan yang saling terpisah. Satu masukan dapat memenuhi syarat matematika sekaligus berpotensi mengubah beban; persetujuan otomatis tetap dicatat terpisah. Catat hasil **per masukan dalam setiap generator**, bukan memberi satu kesimpulan untuk semua masukan hanya karena nama generatornya sama.

Pemeriksaan angka di atas hanya menunjukkan apakah generator memenuhi syaratnya. Pengaruh terhadap kesulitan tetap perlu dibuktikan dari jawaban siswa. Jika pilihan angkanya sedikit, periksa seluruh pilihan. Pemeriksaan sebagian pilihan tidak membuktikan bahwa seluruh kemungkinan hasil memenuhi syarat.

## Pilihan pendekatan

| Pendekatan | Kelebihan | Masalah |
|---|---|---|
| Menaikkan atau menurunkan semua angka dengan persentase tetap | Sederhana | Pengaruh bisa nol atau berlawanan, syarat soal bisa dilanggar, kemampuan soal membedakan siswa belum ditangani |
| **Pilihan pengaturan yang sudah disetujui untuk tiap generator, lalu dicoba dalam batas tertentu berdasarkan data siswa** | Memakai program yang sudah ada; perubahan dan alasannya bisa diperiksa; pengaruhnya diuji | Tiap generator perlu diperiksa dan diuji; soal pengganti yang cocok belum tentu ditemukan |
| Model prediksi atau AI pembuat teks mengubah rumus, kalimat, dan pilihan jawaban salah | Bisa mengubah lebih banyak bagian soal | Memerlukan data pelatihan, pemeriksaan materi, dan sistem tambahan; belum diperlukan pada tahap awal |

Rekomendasi: pendekatan kedua. Gunakan **satu program penyesuaian bersama**, dengan aturan dan pilihan pengaturan masing-masing generator. Tidak perlu membuat 679 program penyesuaian terpisah atau menambah satu program setiap kali jumlah generator bertambah.

## 1. Aturan tiap generator

Setiap aturan mempunyai versi dan berlaku untuk **ID soal, versi serta penanda isi soal asli, penanda pengaturan dasar, bentuk soal, aturan pemberian skor, cara perhitungan dari jawaban siswa, dan aturan pemeriksaan kesetaraan** tertentu. Penanda isi (`hash`) membantu memastikan bahwa isi yang diperiksa masih sama. Jika salah satu bagian tersebut berubah, data dan keputusan lama tidak langsung berlaku untuk versi baru.

Isi minimum:

| Bagian | Isi |
|---|---|
| Identitas | Versi aturan, soal asli dan pengaturan dasar yang dituju, aturan pemberian skor, serta catatan persetujuan |
| Bagian soal yang wajib tetap | Kemampuan yang diuji, cara berpikir yang benar-benar dibutuhkan siswa, jumlah langkah, data dan pilihan jawaban, satuan, konteks, rumus, serta pola jawaban benar |
| Masukan yang boleh diubah | Angka masukan tertentu yang bisa dipilih langsung, batas nilai yang sesuai materi, serta pilihan pengaturan percobaan yang sudah diperiksa |
| Pilihan pengaturan | ID tetap, perubahan masukan, perkiraan beban pengerjaan, cara memeriksa beban tersebut, dan dugaan pengaruhnya jika ada |
| Syarat kesetaraan | Mengacu pada aturan pemeriksaan mutu data dan kesetaraan soal yang sama; tidak membuat batas penerimaan berbeda-beda di setiap file |
| Batas percobaan | Jumlah pilihan pengaturan dan calon varian, jumlah siswa baru, jumlah percobaan, lama pengerjaan, serta alasan berhenti |

“Pilihan pengaturan” berarti kumpulan pengaturan masukan yang sudah diperiksa dan disetujui. Program hanya boleh mengubah bagian pemilihan angka yang diizinkan, misalnya `range`, `values`, atau `factor`, serta `step` jika disetujui.

Program penyesuaian **tidak boleh mengubah** rumus untuk menghitung nilai dari angka lain, kalimat soal, pilihan jawaban, rumus jawaban benar, syarat soal, penyaring hasil, cara menampilkan soal, `original_values`, atau `original_hash`. Perubahan bagian materi soal memerlukan rancangan dan persetujuan versi baru.

Nilai yang dihitung dari angka lain selalu dihitung ulang oleh generator yang sudah ada. Percobaan tetap harus berada dalam batas nilai yang sesuai materi dan sudah disetujui. **Setelah soal selesai dibuat**, periksa apakah angkanya memenuhi syarat, berapa banyak soal berbeda yang bisa dibuat, apakah pilihan jawaban bertabrakan, apakah kunci dan pembahasan benar, serta apakah beban pengerjaannya sesuai. Rentang angka dalam file pengaturan saja tidak cukup menjamin hasil akhirnya.

Contoh masukan yang perlu diteliti; pengaruh terhadap kesulitan belum disetujui sebagai fakta:

| Generator | Masukan yang dapat dicoba | Hal yang wajib tetap | Penilaian awal |
|---|---|---|---|
| `pg-7-1-1` | Pilihan `k` tertentu yang mengubah jumlah digit atau perhitungan | Bentuk persamaan, alasan tiap pilihan jawaban, satuan, dan jumlah langkah | Uji pengaruhnya; `k` lebih besar belum tentu lebih sulit |
| `pg-18-3-1` | Pilihan `k` dari `{4,5,6}`; jari-jari untuk variasi tambahan | Hubungan jari-jari dan luas `k²`, bentuk soal, dan kunci | Periksa pengaruh `k`; perubahan jari-jari belum tentu berguna untuk penyesuaian kesulitan |
| `pg-21-1-1` | Pilihan `t` tertentu; `k` saat ini tidak efektif | Lima data, batas 0 sampai 100, tugas menghitung rata-rata, dan pola data | Jangan mengandalkan `k`; jika `t` juga tidak berpengaruh, perlu rancangan pengaturan baru |
| 11 generator revisi indikator 6–10 | Pilihan `k` bilangan bulat positif dalam 1–40 | Bentuk persamaan/pertidaksamaan/sistem, alasan tiap opsi, satuan, langkah, dan syarat hasil | Perubahan skala bisa mengubah digit atau saling menghapus; periksa tiap soal. Nilai nol, negatif, dan pecahan tidak diizinkan oleh konfigurasi saat ini. |
| `mcma-11-1-7` | Input positif 2–5, besar input negatif 3–6, konstanta 2–7 | Tetap dua input, kuadrat lalu pengurangan, hasil positif, empat pernyataan dan dua benar | Calon pengatur beban aritmetika; input positif harus lebih kecil dari besar input negatif. |
| `pg-11-2-4` | Koefisien 2–4, konstanta 2–5, pengurang 1–3, input 3–7 | Dua fungsi linear, dua substitusi, hasil fungsi dalam positif, satu jawaban benar | Uji beban perkalian dan pengurangan tanpa menambah langkah. |
| `kategori-11-3-9` | Tiga akar berbeda dan terurut dari 1–7 | Tiga kuadrat positif, enam akar positif-negatif, hubungan maju/balik dan pola kunci | Nama himpunan hanya tampilan. Mengganti akar belum membuktikan perubahan kesulitan konsep fungsi. |
| `pg-15-4-2` | Sisi pendek 4–9, sisi panjang 7–12, sudut 30–60° kelipatan 5 | Sisi yang berhadapan dengan sudut lebih panjang, sudut lancip, hanya satu segitiga mungkin; menilai alasan kongruensi | Nama titik hanya tampilan. Jangan memasukkan kasus dua segitiga atau mewajibkan perhitungan trigonometri yang sebelumnya tidak diminta. |
| `mcma-17-1-8`, `kategori-17-2-10` | Faktor `{-4,-3,-2,-0.5,0.5,2,3,4}` dan posisi pernyataan salah | Menilai sifat transformasi, jumlah pernyataan benar, tanpa menghitung koordinat | Posisi pernyataan salah bukan pengatur kesulitan yang sudah terbukti. Domain saat ini terbatas pada 32/24 kandidat berbeda. |
| Generator revisi indikator 20–23 | Pergeseran data, pilihan pola data, banyak siswa/percobaan, rata-rata dan frekuensi sesuai konfigurasi masing-masing | Ukuran kelompok data, hubungan statistik yang diminta, batas nilai per soal, hasil hitungan bulat bila disyaratkan, dan jumlah jawaban benar | Pergeseran data dan perubahan pola tidak disamakan. Periksa nilai efektif setelah syarat dan penyaringan jawaban diterapkan. |

Tidak semua generator langsung diaktifkan untuk penyesuaian. Jika belum ada masukan yang boleh diubah, gunakan status `NO_APPROVED_CONTROL`. Jika pengaturan yang dicoba tidak berpengaruh, gunakan `NO_EFFECT`. Keduanya menghentikan percobaan otomatis dan mencatat kebutuhan rancangan baru. Batas angka tidak diperluas tanpa persetujuan.

Masukan yang tersedia pada konfigurasi sekarang **tidak otomatis berarti boleh diubah oleh penyesuaian otomatis**. Rentang di tabel adalah batas konfigurasi yang diperiksa, bukan pilihan penyesuaian yang telah disetujui. Syarat seperti sisi panjang lebih besar, hasil positif, bilangan bulat, serta jumlah jawaban benar tetap berlaku pada setiap percobaan. Jika semua pilihan gagal, hentikan percobaan; jangan melonggarkan syarat atau memperluas rentang.

Pada generator relasi dan kongruensi revisi 11–15, nama himpunan/titik ikut berubah agar teks jawaban memenuhi pemeriksaan generator yang sudah ada. Nama baru dengan seluruh bilangan sama seperti original ditolak. Perubahan nama tidak boleh dihitung sebagai bukti bahwa suatu pilihan pengaturan berhasil mengubah kesulitan. Untuk stok manual konseptual, pengecualian `same_answer_as_original` tetap mengikuti alur stok, bukan otomatis diterapkan pada generator.

## 2. Memeriksa data dan perbedaan soal

“Jawaban siswa cukup” berarti datanya memenuhi aturan mutu, bukan sekadar jumlah pengerjaan sudah banyak. Pemeriksaan mencakup:

- Siswa yang berbeda dan memenuhi syarat; pengerjaan berulang tidak dihitung sebagai siswa baru.
- Apakah siswa pernah melihat soal tersebut sebelumnya.
- Kesamaan versi soal dan aturan pemberian skor.
- Apakah perhitungan sudah mencapai hasil yang stabil dan cukup teliti.
- Variasi jawaban dan kategori skor, serta keterwakilan tingkat kemampuan siswa yang diperlukan.
- Kecocokan cara perhitungan dengan pola jawaban yang ditemukan.
- Apakah jawaban antarsoal saling terkait di luar pengaruh kemampuan siswa.

Jumlah minimum 30 dalam sumber hanya menjadi titik mulai analisis. Jumlah itu belum menjamin hasil perhitungan dapat dipercaya atau soal mendapat status `PASS`.

Soal asli dan varian harus memakai **skala pengukuran yang bisa dibandingkan, dengan soal acuan yang masih stabil**, sesuai penggunaan Drill. Angka dari dua perhitungan terpisah tidak boleh langsung dibandingkan tanpa memastikan skalanya setara. Hasil Tryout juga tidak langsung dipakai sebagai acuan Drill. Soal acuan, cara perhitungan, aturan pemberian skor, dan pengaturan uji coba ditetapkan selama pengujian.

Jika hasil soal asli atau soal acuan ikut bergeser, penyesuaian ditahan sampai acuannya diperbaiki. Sistem tidak boleh menyesuaikan varian agar mengikuti soal asli yang keliru atau acuan yang sedang bergeser.

Untuk PG, gunakan model perhitungan **2PL** dan periksa:

- `a`: kemampuan soal membedakan siswa berdasarkan tingkat kemampuan mereka.
- `b`: tingkat kesulitan soal.
- Peluang menjawab benar pada berbagai tingkat kemampuan siswa (`theta`) dalam rentang yang disepakati.

Untuk PGK, gunakan model perhitungan **GPCM** dengan aturan pemberian skor yang sudah disetujui. Periksa kemampuan soal membedakan siswa, tingkat kesulitan untuk mencapai tiap kategori skor, serta perkiraan skor pada berbagai tingkat kemampuan setelah disetarakan ke rentang skor yang sama. Soal MCMA/KATEGORI tidak boleh dianggap sebagai kumpulan soal benar-salah yang berdiri sendiri.

Contoh membaca selisih kesulitan: `Δb=b_variant−b_original`. Nilai positif berarti varian lebih sulit; nilai negatif berarti lebih mudah, selama skalanya sama.

Selisih tersebut masih mempunyai rentang ketidakpastian: hasil dari data siswa belum tentu sama persis dengan nilai sebenarnya. Perhitungannya harus memperhatikan hubungan antara hasil soal asli dan varian jika keduanya dihitung bersama, atau memakai cara penghitungan ulang dengan sampel data yang dapat dipertanggungjawabkan. Jangan hanya memakai ukuran ketidakpastian soal asli atau langsung menganggap kedua hasil tidak saling berhubungan.

| Hasil pemeriksaan | Tindakan sistem |
|---|---|
| Semua syarat mutu data dan kesetaraan soal terpenuhi | `PASS`: lanjut memeriksa kelayakan penggunaan soal |
| Data yang dapat dipercaya membuktikan selisih penting di luar batas yang disetujui | `DRIFT`: cari pilihan pengaturan pengganti |
| Rentang ketidakpastian terlalu lebar atau melintasi batas keputusan | `INSUFFICIENT`: tunggu tambahan data; jangan mengubah pengaturan karena variasi data yang belum meyakinkan |
| Skala, aturan pemberian skor, atau cara perhitungan tidak bisa dibandingkan | `NOT_COMPARABLE`: tahan penyesuaian |
| Soal acuan tidak stabil | `HOLD_BASELINE`: tunggu perbaikan acuan |
| Kunci, kecocokan perhitungan, pola jawaban, atau kategori skor bermasalah | `ANOMALY`: hentikan otomatisasi terkait dan periksa masalahnya |

Selisih `b` yang membaik tidak membenarkan penurunan `a` atau memburuknya pola peluang jawaban dan kategori skor. **Semua syarat harus lolos bersamaan.** Nilai gabungan atau rata-rata yang baik tidak boleh menutupi satu pemeriksaan yang gagal. Perbedaan `a` bisa berkaitan dengan pilihan jawaban salah atau kalimat yang membingungkan. Hanya pilihan pengaturan yang sudah disetujui untuk masalah tersebut yang boleh dicoba.

Dokumen ini belum menetapkan angka baru untuk batas selisih, tingkat keyakinan hasil, keterwakilan kemampuan siswa, kecocokan perhitungan, atau batas percobaan. Semuanya perlu dimasukkan ke aturan berversi yang disetujui tim data, penyusun materi, dan produk. Contoh perubahan 10–20% dan lima kali percobaan ulang pada PDF tidak otomatis menjadi aturan penggunaan nyata.

## 3. Alur penyesuaian otomatis

1. Terima hasil perhitungan yang mencatat dengan tepat calon varian dan penanda isinya, soal asli, pengaturan generator, angka awal (`seed`), aturan pemberian skor, skala pengukuran, kumpulan data siswa, dan aturan pemeriksaan yang dipakai. Pemberitahuan yang terkirim dua kali atau hasil yang sudah tidak berlaku tidak membuat percobaan baru.
2. Periksa mutu data dan kestabilan soal acuan. Penyesuaian hanya dimulai jika statusnya `DRIFT` dan ada masukan yang boleh diubah.
3. Pilih **satu pilihan pengaturan yang belum dicoba**. Dahulukan pengaturan yang pengaruhnya didukung data relevan. Pertimbangan materi boleh membantu menentukan urutan percobaan, tetapi belum membuktikan pengaruhnya pada siswa. Jika arah pengaruh belum diketahui, coba pilihan yang sudah disetujui dalam batas percobaan yang ditetapkan.
4. Buat pengaturan percobaan baru di luar folder aktif. Buat calon varian dengan angka awal tetap agar hasilnya bisa dibuat ulang. Simpan isi, kunci, pembahasan, serta catatan asal pembuatannya. Calon varian mendapat ID baru; versi dan penanda isinya tetap sama selama uji coba.
5. Jalankan pemeriksaan yang sudah tersedia: pembuatan ulang soal asli, pemeriksaan matematika, kesamaan kemampuan dan langkah pengerjaan yang diuji, serta beban pengerjaan yang dijanjikan pengaturan. Soal yang gagal pemeriksaan ini tidak dikirim ke siswa. Catat alasan penolakan. Pilihan angka tertentu bisa lebih sering ditolak daripada yang lain, sehingga pola soal yang benar-benar berhasil dibuat dapat berbeda dari pilihan awalnya.
6. Service utama menjadwalkan uji coba sesuai aturan yang sudah disetujui, dengan siswa baru yang memenuhi syarat dan soal acuan Drill yang sudah ditetapkan. Banyak siswa mengerjakan **calon varian yang sama**; sistem tidak membuat soal berbeda untuk setiap siswa. Uji coba tidak mengubah XP atau catatan penguasaan materi. Aturan siswa melihat soal dan pembahasannya mengikuti ketentuan service utama.
7. Tunggu data jawaban untuk calon varian baru. Jawaban pada calon varian lama tidak boleh dipakai untuk menghitung tingkat kesulitan soal yang isinya sudah berubah. Hitung kembali hasilnya dan bandingkan pada skala serta aturan yang sesuai.
8. Jika `PASS`, periksa kelayakan paket dan pembagian soal kepada siswa. Setelah semua syarat terpenuhi, Numora mengaktifkan isi dan versi yang telah diuji secara otomatis. Jika masih `DRIFT`, ulangi langkah 3 selama batas percobaan belum habis. Jika `INSUFFICIENT`, tunggu tambahan data sesuai tenggat; jangan terus membuat calon varian baru.

Tahap awal cukup memakai daftar pilihan pengaturan yang terbatas. Belum perlu menambah program pencarian terbaik atau model pembelajaran mesin. Besar dan arah perubahan ditentukan oleh aturan serta data, bukan anggapan umum bahwa “`b` terlalu tinggi berarti semua angka harus diturunkan”. Pengaturan yang sudah diuji tidak diulang dengan masukan dan data yang sama; data baru dapat menjadi alasan pemeriksaan ulang.

Untuk gabungan keluarga generator, soal asli, dan kondisi pengujian yang sama, hanya boleh ada satu proses penyesuaian aktif. Sistem memastikan satu pekerjaan tidak dijalankan ganda. Pengulangan karena gangguan teknis memakai masukan yang sama; percobaan penyesuaian berikutnya membuat pengaturan, calon varian, dan masukan baru.

Jika izin pengerjaan kedaluwarsa, pengaturan atau aturan berubah, soal acuan berganti, atau versi aktif berubah, hasil lama tidak boleh langsung diaktifkan.

Alasan berhenti atau menunggu harus dicatat:

| Status | Arti |
|---|---|
| `PASS` | Calon varian lolos pemeriksaan yang diperlukan pada tahap ini |
| `INSUFFICIENT` | Data belum cukup meyakinkan; tunggu sesuai batas waktu |
| `NOT_COMPARABLE` | Hasil soal asli dan varian belum bisa dibandingkan |
| `HOLD_BASELINE` | Soal acuan perlu diperbaiki atau dipastikan stabil |
| `ANOMALY` | Ada masalah pada soal, jawaban, atau hasil perhitungan yang perlu diperiksa |
| `NO_APPROVED_CONTROL` | Belum ada masukan yang disetujui untuk diubah |
| `NO_EFFECT` | Pengaturan yang dicoba tidak memberi pengaruh yang diperlukan |
| `NO_FEASIBLE_CANDIDATE` | Tidak ditemukan calon varian yang memenuhi syarat |
| `BUDGET_EXHAUSTED` | Batas percobaan, siswa, waktu, atau sumber daya yang disetujui sudah habis |
| `STALE_CONTEXT` | Hasil sudah tidak berlaku karena kondisi atau versi berubah |

Penyesuaian otomatis tidak menjamin soal pengganti yang cocok selalu ditemukan.

## 4. Membedakan satu varian dan seluruh hasil generator

Satu varian yang berbeda cukup untuk memulai **percobaan pengganti varian tersebut**. Hasil itu belum membuktikan bahwa seluruh soal buatan generator mempunyai masalah yang sama. Satu varian yang mendapat `PASS` juga tidak membuat semua hasil generator otomatis lolos.

Program boleh mencari pilihan pengaturan yang menjanjikan dari beberapa varian dan uji coba yang bisa dibandingkan, sambil memperhatikan ketidakpastian hasil dan perbedaan antarsoal. Hasil satu angka awal tidak langsung menjadi alasan untuk mengubah seluruh rentang angka generator.

Pilihan pengaturan yang didahulukan untuk pembuatan soal berikutnya hanya boleh diperbarui jika aturan sudah menetapkan data dan batas percobaan yang diperlukan. Setiap calon varian baru tetap harus lolos pemeriksaannya sendiri.

Saat diaktifkan, service utama memberikan **isi soal tersimpan yang benar-benar diuji**, bukan membuat soal baru dengan angka awal berbeda setelah menerima `PASS`. Sesi pengerjaan yang sudah berjalan dan skor lama tetap memakai versi semula.

Konfigurasi yang sama boleh dipakai dengan `seed` baru untuk membuat **calon** varian berikutnya dalam batas yang sama. Seed berbeda bisa menghasilkan isi yang sama, terutama pada domain yang kecil; beberapa permintaan UI/CLI saat ini tidak menyimpan daftar varian sebelumnya untuk mencegah pengulangan lintas permintaan. Karena itu, rancangan penyebaran perlu membandingkan isi calon terhadap daftar soal tersimpan sebelum memasukkannya ke uji coba. Lolos pemeriksaan matematika, mempunyai penanda asal yang lengkap, atau berada dalam konfigurasi yang sama belum berarti lolos pemeriksaan kesulitan siswa.

## 5. Pembagian pekerjaan dua repo

| Repo | Tanggung jawab dalam rancangan |
|---|---|
| Numora-ai-service | Aturan dan pilihan pengaturan generator; pembuatan serta pemeriksaan calon varian; penerimaan dan pengolahan hasil perhitungan dari jawaban siswa; perbandingan dengan soal asli; keputusan penyesuaian; catatan hasil percobaan |
| Numora | Sumber resmi isi soal dan aturan pemberian skor; siswa, uji coba, dan riwayat siswa melihat soal; masukan uji coba yang ditetapkan; persetujuan aturan; pemeriksaan kelayakan penggunaan; aktivasi dan pembagian soal |

Gunakan rancangan Numora yang sudah ada untuk permintaan kerja, pembagian tugas, penyimpanan hasil, dan catatan bukti, termasuk `adjustment_iterations` untuk mencatat percobaan penyesuaian. Program pemrosesan saat ini berfokus pada `CALIBRATE_TRYOUT`. Alur `COMPARE_VARIANTS` dan penyesuaian Drill belum selesai dibuat. Repo AI tidak perlu mempunyai database kedua atau rangkaian perubahan struktur database tersendiri.

Pemberitahuan dan status dalam dokumen ini menjelaskan pertukaran data yang perlu disepakati saat kedua service dihubungkan. Belum ada jalur penerimaan atau penulisan data baru yang diaktifkan. Tab DB dengan akses operator yang luas tetap hanya membaca saat ini. Program penerimaan hasil dan aktivasi otomatis memerlukan pekerjaan terpisah sesuai pembagian tanggung jawab kedua repo.

Stok konseptual ditangani terpisah: pilih stok pengganti yang sudah lolos atau perbaiki isinya secara manual sebelum digunakan. Perbaikan stok tidak dianggap sebagai perubahan pengaturan angka generator otomatis.

## 6. Rencana penyebaran paket Drill

**Mulai dengan satu paket original dan satu paket varian.** Tambahkan paket varian kedua, ketiga, lalu keempat secara bertahap, sesuai kemampuan mengumpulkan data yang dapat dipercaya untuk setiap soal. Jumlah paket aktif mengikuti jumlah siswa yang memenuhi syarat pengujian.

Rencana ini berlaku untuk pengujian varian Drill pada bab, subbab, dan level yang sesuai. Paket percobaan diberi label uji coba. Pengerjaannya tidak mengubah XP, bintang, penguasaan materi, atau akses belajar; pembahasan dibuka setelah pengumpulan data uji coba ditutup. Varian untuk penggunaan reguler tetap harus lolos pemeriksaan soal dan paket.

### Perbandingan dua pilihan

Pilihan satu paket varian memusatkan pengumpulan jawaban, sehingga pemeriksaan setiap varian lebih cepat memperoleh data. Pilihan empat paket varian menguji lebih banyak varian sekaligus, tetapi jawaban untuk setiap varian lebih sedikit jika jumlah siswanya sama.

Contoh berikut memakai **1.000 siswa baru yang memenuhi syarat, masing-masing mengerjakan satu paket, dengan pembagian rata**. Angka dan pembagian ini hanya ilustrasi, bukan jumlah minimum atau aturan pembagian yang sudah ditetapkan.

| Pilihan | Siswa pada paket original | Siswa per paket varian |
|---|---:|---:|
| 1 paket original + 1 paket varian | 500 | 500 |
| 1 paket original + 4 paket varian | 200 | 200 |

Jawaban dari empat varian berbeda tidak digabung seolah-olah berasal dari satu soal yang sama. Setiap soal dan versi mempunyai data pemeriksaannya sendiri. Jumlah jawaban saja juga belum cukup: mutu data, ketelitian hasil, dan keterwakilan kemampuan siswa tetap diperiksa sesuai bagian 2.

### Tahapan penyebaran

1. **Pastikan soal original dan soal acuan layak.** Periksa isi, kunci, pembahasan, serta hasil perhitungan dari jawaban siswa. Jika datanya belum dapat dipercaya, mulai dengan pengumpulan jawaban original dahulu. Perbandingan dengan varian dibuka setelah soal asli yang diuji dan soal acuannya memenuhi syarat serta stabil.
2. **Buka satu paket original dan satu paket varian.** Kedua paket memakai soal acuan yang sama. Bagian lain berisi soal original pada paket pertama dan varian pasangannya pada paket kedua. Topik, level, bentuk soal, jumlah soal, serta aturan pemberian skor dibuat sebanding.
3. **Bagikan secara acak dalam kelas dan periode yang sama.** Setiap siswa mendapat salah satu paket. Pilihan paket disimpan agar memuat ulang halaman atau melanjutkan pengerjaan tidak mengubah paket. Untuk data pengujian bersih, gunakan siswa yang belum melihat soal yang diuji, versi lain dari soal yang sama, soal acuan yang dipakai, atau pembahasannya. Siswa yang mengikuti pengumpulan data original sebelumnya tidak otomatis memenuhi syarat untuk pengujian pasangan soal yang sama.
4. **Pertahankan isi paket selama pengumpulan data.** Soal acuan memakai isi dan aturan skor yang sama pada semua paket, serta tidak ikut disesuaikan otomatis. Banyak siswa mengerjakan varian tersimpan yang sama; angka awal (`seed`) tidak diganti untuk setiap siswa. Versi paket, isi soal, kunci, dan aturan skor dicatat untuk setiap pengerjaan.
5. **Periksa dan sesuaikan per soal.** Kesulitan rata-rata paket tidak membuktikan semua soalnya setara. Soal yang terbukti bermasalah dibuatkan calon varian pengganti melalui alur pada bagian 3. Isi baru membutuhkan jawaban baru. Setelah seluruh pemeriksaan soal dan paket lolos, Numora mengaktifkan versi pengganti secara otomatis menurut aturan yang sudah disetujui. Paket yang sedang dikerjakan, jawaban lama, dan skor lama tetap memakai versi sebelumnya.
6. **Tambah paket varian secara bertahap.** Tambahkan paket kedua, lalu ketiga dan keempat ketika pembagian siswa masih memungkinkan setiap soal memperoleh data yang dapat dipercaya dalam waktu yang disetujui. Pertahankan kelompok original sebagai pembanding pada periode pengujian yang sama. Jika data per varian terlalu lambat terkumpul, tunda pembukaan paket berikutnya.

Penambahan paket tidak otomatis diizinkan hanya karena satu varian sudah lolos. Setiap varian baru tetap diperiksa sendiri, termasuk jika dibuat dari pengaturan generator yang sama dengan `seed` berbeda. Untuk soal asli dan kondisi pengujian yang sama, penyesuaian tetap diatur oleh satu proses bersama sesuai bagian 3 agar beberapa paket tidak menjalankan perubahan yang saling bertabrakan.

Jika soal asli atau acuan bergeser, perbandingan dan penyesuaian ditahan sampai masalah acuan ditangani. Jika jawaban belum cukup meyakinkan, tunggu tambahan data sesuai tenggat. Keduanya tidak menjadi alasan untuk terus mengganti isi paket.

## 7. Urutan pekerjaan yang disarankan

1. **Lengkapi pemeriksaan masukan 679 generator.** Jumlah, nama, domain efektif, kapasitas dan pengelompokan statis per masukan sudah dilengkapi pada laporan 7 Oktober 2026; persetujuan kontrol dan bukti kesulitan siswa tetap belum tersedia. Gunakan pemeriksaan revisi 6–10, 11–15, 16–19, dan 20–23 sebagai bukti awal. Kelompokkan masukan yang bisa menghasilkan soal sesuai syarat, yang berpotensi mengubah beban pengerjaan, yang hanya mengubah tampilan angka atau konteks, dan yang belum menyediakan pilihan penyesuaian. Sertakan rentang efektif setelah penyaringan, kapasitas varian berbeda, versi original/config yang diperiksa, dan status persetujuan. Empat soal HOLD tidak diikutkan; 40 revisi tanpa generator masuk antrean setelah generatornya selesai. Penyesuaian tetap tidak aktif jika belum disetujui. Jangan memperluas batas angka secara otomatis.

   **Status: selesai untuk config/batas sekarang — 7 Oktober 2026.** [Audit per 1.027 masukan](../../audits/2026-10-07-generator-input-audit.md) menutup domain efektif dan kapasitas seluruh 679 generator. Persetujuan kontrol serta bukti pengaruh dari siswa tetap OPEN; langkah 2–4 belum dikerjakan.
2. **Buat versi awal untuk beberapa keluarga generator yang mewakili kondisi berbeda.** Pilih setelah pemeriksaan, bukan berdasarkan nama `k`. Siapkan pilihan pengaturan, pemeriksaan matematika, dan bagian soal yang wajib tetap. Gunakan hasil perhitungan buatan yang diberi label sebagai simulasi untuk menguji perpindahan status dan alur kerja. Simulasi hanya menguji program, bukan membuktikan kesulitan pada siswa.
3. **Lengkapi perhitungan dan uji coba nyata.** Siapkan penerimaan hasil, perhitungan kesulitan dan daya pembeda, pemeriksaan kelayakan data siswa, soal acuan Drill, serta aturan pemeriksaan mutu data dan kesetaraan soal. Ikuti tahapan penyebaran pada bagian 6. Pembuatan jalur penerimaan data, alat operator, dan pemasangan program di server belum dilakukan dalam pekerjaan dokumen ini.
4. **Aktifkan otomatis sesuai pilihan pengguna.** Numora mengaktifkan calon varian yang benar-benar diuji setelah pemeriksaan soal, paket, pembagian soal, keberlakuan hasil, dan persetujuan aturan semuanya lolos. Pantau setelah aktivasi. Jika hasil penggunaan nyata bergeser, pembagian soal baru dapat dihentikan sesuai aturan.

Hal minimum yang harus terbukti saat program dibuat:

- Perbedaan yang terbukti dari data valid memulai satu percobaan pengganti.
- Data yang belum meyakinkan atau soal acuan yang bergeser tidak mengubah pengaturan.
- Pemberitahuan ganda tidak menghasilkan pekerjaan ganda.
- Batas masukan dan rumus yang wajib tetap tidak dilanggar.
- Calon varian baru tidak memakai jawaban dari isi soal lama.
- Hasil yang sudah tidak berlaku tidak diaktifkan.
- Proses berhenti saat batas percobaan habis.
- Satu varian yang lolos tidak meluluskan seluruh generator.
- Pembagian paket tetap saat pengerjaan dilanjutkan; soal acuan tidak ikut disesuaikan; data tiap varian dan versi tetap dibedakan.
- Aktivasi tidak mengubah riwayat pengerjaan atau skor lama.
- Data contoh untuk pengujian program tidak diam-diam menetapkan batas penerimaan yang belum disetujui.

## Acuan

- [Konsep dari PDF dan pemeriksaan mutu](../../../../Numora/docs/data/QUESTION_VARIANT_IRT_KNOWLEDGE_2026-10-02.md), khusus bagian 6.
- [Penyimpanan data dan pembagian tanggung jawab](../../../../Numora/docs/data/VARIANT_IRT_DATABASE.md).
- [Rancangan pembagian pekerjaan Tryout](../../../../Numora/docs/development/IRT_V3_RUNBOOK.md).
- [Aturan generator yang sudah ada](../../GENERATOR.md), [susunan service AI](../../ARCHITECTURE.md).
- [Impor revisi indikator 1–5](../../audits/2026-10-07-drill-1-5-source-revision.md), [generator revisi 6–10](../../audits/2026-10-07-revised-6-10-generator-audit.md), [generator revisi 11–15](../../audits/2026-10-07-revised-11-15-generator-audit.md).
- [Revisi dan generator 16–19](../../audits/2026-10-07-drill-16-19-source-revision.md), [generator revisi 20–23](../../audits/2026-10-07-revised-20-23-generator-audit.md), [daftar soal tanpa generator](../../../variant_gen/soalskip.md).

## Status dokumen

Rancangan sudah mencatat kebutuhan pengguna dan aktivasi otomatis, batas pekerjaan saat ini, pilihan angka yang memenuhi syarat, kestabilan soal acuan, ketidakpastian hasil, perlindungan soal asli dan riwayat, pencatatan versi, perbedaan satu varian dan seluruh generator, penyebaran paket secara bertahap, serta pemeriksaan sebelum soal digunakan. Pembaruan 7 Oktober memasukkan 33 generator baru, revisi sumber 1–5, 679 generator aktif yang tersedia, serta audit lengkap domain/kapasitas dan pengelompokan statis 1.027 masukan. Audit tidak mengesahkan kontrol otomatis atau pengaruh kesulitan dari respons siswa.

Aturan materi dan perhitungan dari jawaban siswa yang belum disetujui masih harus ditetapkan sebelum program dibuat. Dokumen ini tidak mengisi batas tersebut dengan angka buatan. Belum ada rencana implementasi terperinci, kode penyesuaian otomatis, atau uji coba kesulitan dengan siswa.
