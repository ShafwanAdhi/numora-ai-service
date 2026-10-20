# Tahap 4 — Audit akademik indikator 3

**Cakupan disetujui:** indikator 3 saja, 50 entri sumber (5 level × 10 soal). Seluruh stimulus, opsi/pernyataan, kunci, pembahasan, dan catatan diperiksa. L5Q7 mempunyai dua rangkaian opsi yang dicatat sebagai subbagian terpisah; tidak digabung menjadi satu MCMA delapan opsi dan tidak dipilih versi resmi.

| Komponen | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | 47 | 2 | 1 |
| Kunci | 47 | 2 | 1 |
| Pembahasan | 44 | 4 | 2 |

Hitungan per komponen berdiri sendiri. **44 soal tanpa temuan yang menghalangi**; 6 soal perlu tindak lanjut.

Temuan dan usulan **PROPOSED, belum diterapkan/disetujui Kurikulum**:

| Soal | Bukti dan dampak | Usulan |
|---|---|---|
| L5Q7 | Rangkaian awal: A/B/C benar dan D menyatakan klaim “9 cm” salah, sehingga D juga benar. Rangkaian akhir: A/B/C benar, D langsung menyatakan “9 cm” sehingga salah. Header ABD tidak cocok; tambahan ABC hanya cocok versi akhir. | Tetapkan satu versi. Jawaban kondisional: **ABCD untuk opsi meta awal; ABC untuk opsi langsung akhir**. Jangan memilih otomatis. |
| L5Q5 | Evaluasi I dan III sama-sama benar: √82→9, √35→6, selisih 3. Pertanyaan meminta evaluasi pasti benar, bukan yang paling rinci. | Bedakan opsi atau tetapkan kriteria eksplisit; kunci C tidak unik. |
| L4Q5 | Evaluasi I dan III sama-sama sah: √98→10, √45→7, selisih 3. Kata “paling tepat” tidak menjelaskan kewajiban menampilkan desimal antara. | Klarifikasi kriteria/rubrik; jangan menganggap I salah karena ringkas. |
| L1Q3 | Alasan B mengubah 78.000→80.000, tidak mengikuti ribuan terdekat; alasan D memakai 3,5×24.800=86.800, bukan 82.500. | Koreksi alasan opsi pengecoh; **kunci C, Rp81.000, tetap**. |
| L1Q5 | Alasan A menyebut kedua faktor dibulatkan ke bawah untuk 20×6.000; 19→20 justru naik. | Koreksi arah pembulatan; **kunci B, Rp140.000, tetap**. |
| L2Q3 | Alasan opsi D (Rp90.000) menyebut 4×25.000 yang sebenarnya 100.000. | Koreksi alasan opsi pengecoh; **kunci C, Rp87.500, tetap**. |

Catatan minor tanpa perubahan jawaban: pada L2Q4, model A disebut membulatkan semua angka ke bawah meskipun 9,7→10 naik; L4Q3 menyisakan penanda editorial `[cite:12]`; L4Q5/L5Q5 memakai “radian” padahal istilah yang dimaksud **radikan**.

Perhitungan pembulatan memakai pecahan eksak dan **41 uji sel pembulatan akar**, ditambah 5 uji interval dan 5 perbandingan galat estimasi. Uji akar membandingkan kuadrat titik tengah, sehingga tidak bergantung pada pembulatan desimal antara atau asumsi bahwa kuadrat terdekat selalu membuktikan pembulatan akar. Aturan angka 5 dibulatkan naik mengikuti contoh sumber; tempat pembulatan tetap sesuai instruksi tiap soal. Tidak ada rubrik skor kategori baru.

Keluaran: [JSON lengkap 50 entri dan subbagian versi](audit.json), [CSV](entries.csv). Semua opsi memiliki penilaian independen; untuk PG valid dipastikan tepat satu opsi benar. Kunci yang dinyatakan benar cocok dengan hasil independen. Seluruh 859 hash sumber/bank/config/stok/layanan tetap sama.

Reproduksi: `python variant_gen/tests/audit_indicator_03_academic.py`. Tidak ada perubahan sumber, bank aktif, generator, atau pemetaan runtime. Audit ini bukan persetujuan publikasi/kesetaraan kesulitan. **Indikator 4 dan pencocokan generator menunggu instruksi berikutnya.**
