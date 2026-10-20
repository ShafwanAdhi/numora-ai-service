# Tahap 2 — Audit akademik indikator 1

**Cakupan disetujui:** 50 soal indikator 1 saja (5 level × 10 soal). Tidak melakukan pencocokan original/generator, perubahan soal, publikasi, atau audit indikator lain dalam tahap ini.

Seluruh stimulus, opsi/pernyataan, kunci, pembahasan, dan catatan dibaca. Solusi independen dan penilaian seluruh opsi tersedia per soal, termasuk yang tidak memiliki satu jawaban final. Perbandingan angka utama memakai pecahan eksak/batas kuadrat; tidak ada aturan pembulatan baru. Kategori dinilai per pernyataan tanpa mengarang rubrik skor.

| Komponen | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | 46 | 3 | 1 |
| Kunci | 46 | 2 | 2 |
| Pembahasan | 46 | 2 | 2 |

Hitungan setiap baris berdiri sendiri, bukan dijumlahkan menjadi jumlah soal bermasalah. Ada **5 soal yang membutuhkan tindak lanjut**, termasuk satu soal yang hanya memerlukan koreksi alasan distractor.

| Lokasi | Bukti dan dampak | Usulan (PROPOSED, belum diterapkan) |
|---|---|---|
| L4 soal 1 | Urutan A,C,B,D benar; Analisis I dan II sama. Opsi A dan B sama-sama merujuk Analisis I; header B menyebut Analisis II. PG tidak unik. Pembahasan urutan benar, tetapi tidak membuat kunci menjadi unik. | Bedakan analisis/opsi, samakan label kunci, pastikan tepat satu opsi benar. |
| L5 soal 2 | Definisi awal a=2√2 irasional; definisi akhir a=0 rasional. Beberapa rancangan dan label evaluasi bercampur. C hanya benar jika blok akhir dipilih. | Kurikulum menetapkan satu versi; hapus rancangan lain setelah keputusan. Tidak memilih otomatis. |
| L5 soal 5 | B=C=−0,8 dan A=−0,85. Evaluasi A serta B sama-sama benar. Pembahasan memilih B karena paling lengkap, sedangkan stem tidak meminta itu. | Perbaiki opsi atau tetapkan kriteria pertanyaan secara eksplisit. |
| L5 soal 7 | A/B benar dan C salah secara hitung; D “mempermudah rekapitulasi” tidak memiliki kriteria objektif. | Ganti D dengan klaim terukur atau minta klarifikasi Kurikulum. |
| L1 soal 5 | Kunci A dan urutan X,Y,Z benar. Alasan distractor D menyebut Z,X,Y sebagai kebalikan, padahal kebalikannya Z,Y,X. | Koreksi alasan distractor; tidak perlu mengganti jawaban A. |

Empat pembahasan tentang sifat operasi (L1Q10, L2Q7, L3Q7, L4Q7) mendapat catatan redaksional: ketidakkomutatifan/ketidakasosiatifan berarti kesamaan **tidak selalu** berlaku, bukan tidak pernah berlaku. Contoh khusus pengurangan dapat sama ketika a=b atau c=0. Jawaban pada data soal tetap benar. Catatan pembagian di L2Q8, L3Q8, L4Q8, L5Q8 sebaiknya menuliskan syarat a≠0 pada 0/a=0; domain opsi sumber sendiri sudah jelas.

Sebanyak **45 soal tidak memiliki temuan akademik yang menghalangi** pada pemeriksaan ini; itu bukan persetujuan Kurikulum atau bukti kesetaraan kesulitan. Status per komponen dan bukti lokasi paragraf tersimpan di [JSON lengkap](audit.json), serta [CSV 50 soal](entries.csv).

Validasi: cakupan 50 posisi unik, panjang vektor penilaian sesuai opsi, seluruh kunci berstatus benar cocok dengan solusi independen, semua PG valid mempunyai tepat satu opsi benar, perhitungan eksak lulus, dan 859 hash berkas sumber/bank/config/stok/layanan tetap sama. Reproduksi: `python variant_gen/tests/audit_indicator_01_academic.py`.

**Indikator 2 dan pencocokan generator menunggu instruksi berikutnya.**
