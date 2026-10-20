# Tahap 6 — Pencocokan original dan generator indikator 1–5

Cakupan: **250 entri sumber indikator 1–5** dicari lintas ID/level terhadap **790 original Drill aktif** setelah ledger revisi diterapkan. Bank aktif indikator 1–5 sendiri berisi **150 original**, seluruhnya pada level 1–3. Sumber baru juga menyediakan **100 entri level 4–5**. Tidak ada pemetaan runtime atau konten yang diubah.

| Hasil identitas konten | Entri |
|---|---:|
| Identik seluruh isi setelah normalisasi tampilan yang dibatasi | 143 |
| Inti soal identik, tetapi pembahasan/caption kunci/catatan berbeda | 4 |
| Belum ada identitas terverifikasi | 103 |

Identik seluruh isi mensyaratkan format, stimulus/pertanyaan, urutan opsi/pernyataan, kunci semantis, label kategori, caption kunci tertulis, pembahasan, dan catatan cocok. Tidak menggunakan original_hash sebagai bukti identitas penuh: hash itu tidak mencakup pembahasan. Perbandingan menyimpan isi dan perbedaan per komponen, versi original, hash isi lengkap, serta hash berkas pembanding.

**103 entri yang belum identik** terdiri dari 100 entri level 4–5 tanpa pasangan identik, I5 L3Q5 yang benar-benar berbeda redaksi stimulus/pembahasan, dan dua kasus representasi bilangan campuran (I3 L1Q3/L2Q3) yang belum dipastikan. Dua kasus terakhir memiliki kandidat original/generator lama; tidak disimpulkan bahwa sama sekali tidak ada template terkait. Tidak ada kecocokan historis tambahan yang menggantikan kecocokan versi aktif.

| Ketersediaan untuk isi sumber baru | Entri |
|---|---:|
| Inti cocok dengan generator terverifikasi | 135 |
| Inti cocok, hanya stok manual | 10 |
| Inti cocok, original masih HOLD tanpa generator | 2 |
| Belum ada generator yang terbukti cocok untuk isi ini | 103 |

Artinya **115 entri belum mempunyai generator yang terbukti cocok untuk versinya**: 103 belum memiliki identitas terverifikasi + 10 stok manual + 2 original HOLD. Ini tidak berarti 115 keluarga generator harus dibuat: kemiripan konsep belum membuktikan kecocokan, dan beberapa kasus perlu perbaikan atau penyesuaian terlebih dahulu.

Pemeriksaan 150 original pembanding indikator 1–5 menemukan **138 konfigurasi generator** dan 12 tanpa konfigurasi. Seluruh 138 lulus validasi config, reproduksi original, serta uji panggil deterministik berulang dengan seed tercatat. **135** keluarga generator tersebut terbukti cocok dengan inti sumber baru; 3 lainnya terkait kandidat yang isinya belum identik/terverifikasi. Uji ini membuktikan konfigurasi dan reproduksi, bukan kebenaran akademik semua varian atau kesetaraan kesulitan.

| Rekomendasi setelah mempertimbangkan audit akademik | Entri |
|---|---:|
| Gunakan generator existing | 123 |
| Review pembahasan/caption dahulu | 2 |
| Stok manual saja | 9 |
| Antrean update atau bangun generator | 74 |
| Perlu tindak lanjut akademik sebelum penggunaan | 42 |

Rekomendasi tersebut **PROPOSED, bukan persetujuan Kurikulum**. Ketersediaan generator tetap dicatat walaupun soal tertahan secara akademik. Sebanyak 42 entri memiliki tindak lanjut akademik dari tahap sebelumnya; tidak semuanya berarti soal tidak valid—sebagian hanya memerlukan koreksi alasan opsi.

| Kasus penting | Hasil |
|---|---|
| I1 L2Q1 / pg-1-2-1 | Inti cocok, tetapi sumber baru memperbaiki pembahasan persentase yang membuat original lama HOLD. Belum ada generator; masuk antrean setelah revisi original disetujui. HOLD runtime tidak diubah. |
| I3 L1Q6 / mcma-3-1-6 | Inti dan generator cocok; pembahasan berbeda pada penulisan desimal 81,00 versus 81. Disimpan sebagai perbedaan, tidak disederhanakan otomatis. |
| I4 L1Q7 / mcma-4-1-7 | Inti dan generator cocok; pembahasan berbeda pada teks waktu detikcom-60 versus detik ke-60. Perlu review pembahasan; bukan alasan otomatis membuat generator baru. |
| I5 L3Q3 / pg-5-3-3 | Inti cocok dengan original HOLD tanpa generator, tetapi caption kunci lama menyebut 24 liter/menit walaupun yang ditanya selisih 4. Pembahasan/catatan juga berubah; audit akademik masih menahan asumsi volume awal. |
| I5 L3Q5 / pg-5-3-5 | Ada kandidat original/generator terverifikasi untuk versi aktif lama, tetapi stimulus dan pembahasan baru berubah. Kandidat bukan bukti identitas; perlu update/review untuk versi baru. |
| I3 L1Q3 dan L2Q3 | Notasi campuran Word versus penulisan bank 3(1)/(4) atau 3(1)/(2) belum dianggap identik. Generator lama tersedia; identitas perlu review notasi/provenance. |

Sepuluh stok manual terdapat pada pg-1-1-4, mcma-1-1-8, kategori-1-1-10, kategori-1-2-10, kategori-1-3-10, pg-2-2-5, pg-2-3-1, pg-2-3-4, pg-2-3-5, dan pg-5-2-4. Satu di antaranya masih memerlukan tindak lanjut akademik, sehingga rekomendasi stok manual langsung hanya sembilan.

Normalisasi hanya mengatasi tampilan yang dibatasi: whitespace, delimiter/pangkat/akar/pecahan Word–LaTeX, subskrip, angka campuran yang eksplisit, sen nol pada mata uang, dan susunan tabel dengan urutan sel tetap. Pengelompokan pangkat dipertahankan; x^(a+b) tidak disamakan dengan x^a+b. Tidak menghitung bentuk akar menjadi angka, tidak mengubah angka/satuan/tanda, dan tidak menukar opsi. Kandidat kemiripan tidak pernah diberi label identik.

Semua pasangan yang benar-benar cocok memiliki pembahasan tersendiri dalam metadata original yang dipin. Kasus 118 original lama tanpa pembahasan berasal dari kelompok lain dan tidak menjadi pasangan cocok pada bagian ini; tidak ada pembahasan buatan generator yang dipakai sebagai pengganti sumber.

Keluaran: [JSON lengkap](matching.json), [CSV 250 entri](entries.csv), [tanpa generator terverifikasi](without-verified-generator.csv), [stok manual](manual-stock-only.csv), [review/penyesuaian](review-or-adjustment.csv), [tindak lanjut akademik](held.csv), dan [identitas/pemetaan belum terverifikasi](unconfirmed-mapping.csv). Daftar terakhir mencakup konten baru juga; kemunculan di sana tidak berarti kandidat sudah dipastikan sebagai pasangan.

Git HEAD pembanding: `c6ca8f8822e49587ae1dadda15d086546a6795bc`. Isi working tree dipin terpisah karena ada berkas lokal yang belum di-commit. Seluruh 859 hash sumber/bank/config/stok/layanan tetap sama. Tidak ada publikasi, perubahan bank/generator, penyesuaian rentang, atau aktivasi otomatis.

Reproduksi: `python variant_gen/tests/match_indicators_01_05.py`. Pengujian batas identitas: `python -m unittest discover -s variant_gen/tests -p test_match_indicators_01_05.py`.

**Bagian pencocokan indikator 1–5 selesai sebagai laporan; pekerjaan indikator berikutnya menunggu instruksi.**
