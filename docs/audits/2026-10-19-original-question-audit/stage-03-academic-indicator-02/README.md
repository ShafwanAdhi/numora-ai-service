# Tahap 3 — Audit akademik indikator 2

Cakupan: **50 soal indikator 2 saja**, lima level × sepuluh soal. Semua opsi/pernyataan, kunci, langkah pembahasan, serta catatan diperiksa. Tidak mencocokkan generator dan tidak mengubah sumber atau bank.

| Komponen | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | 46 | 1 | 3 |
| Kunci | 43 | 3 | 4 |
| Pembahasan | 35 | 11 | 4 |

Hitungan per komponen terpisah. **35 soal tanpa temuan yang menghalangi**, termasuk catatan minor domain/redaksi. Sebanyak 15 soal memerlukan tindak lanjut; kesalahan alasan distractor dihitung karena pembahasan diperiksa seluruhnya, walaupun kunci akhirnya benar.

Temuan utama dan usulan **PROPOSED, belum diterapkan/disetujui Kurikulum**:

| Soal | Temuan | Tindak lanjut |
|---|---|---|
| L4Q2 | (5+6−3)√3=8√3, bukan6√3. | Usulan kunci **B**, bukanC; koreksi pembahasan. |
| L4Q9 | (3/4+1,25)×0,4=0,8; pernyataan kondisional b benar. | Usulan kategori **Benar, Benar, Benar** untuk teks sekarang; atau ubah b agar menilai keabsahan prosedur. |
| L5Q9 | (4/5+1,5)×0,2=0,46; masalah semantik sama. | Usulan **Benar, Benar, Benar** untuk teks sekarang; jangan mengganti pertanyaan tentang hasil menjadi penilaian prosedur. |
| L2Q3 | 2,33jam=139,8menit, bukan140; belum7periode20menit lengkap. C sah jika memakai7periode yang juga tertulis. | Tetapkan140menit/2jam20menit; tidak membulatkan otomatis. |
| L4Q1 | AnalisisI/II sama-sama sah; kurung tambahan tidak wajib. | Perjelas kriteria pemilihan tunggal atau ubah opsi. |
| L4Q5 | LangkahA sah (hasil3); B juga sah dan lebih rinci. OpsiA benar, sementaraC mengutamakan rincian tanpa kriteria jelas. | Klarifikasi kriteria/rubrik atau bedakan opsi. |
| L3Q7 | D menyatakan mempermudah rekapitulasi tanpa ukuran objektif. | Ganti dengan pernyataan terukur atau minta kriteria Kurikulum. |
| L3Q1 | Baris tengah pembahasan mengganti−40.000 menjadi+40.000 sebelum kembali ke hasil110.000. | Koreksi tanda; kunciB tetap. |
| L4Q3 | Rumus umum pangkat dari pangkat salah tulis; perhitungan numeriknya benar. | Tulis (a^m)^n=a^(mn); hasil2^8 tetap. |

Enam soal lain memerlukan koreksi alasan distractor/catatan: **L1Q1, L1Q2, L1Q5, L2Q1, L4Q10, L5Q10**. Contoh: lupa es krim padaL1Q1 memberi24.500, bukan20.500; padaL4Q10,15√2÷3=5√2, bukan10√2. Detail semua kesalahan, dampak, dan usulan ada per soal di JSON/CSV.

Domain a,b≠0 padaL4Q7 serta x,y≠0 padaL5Q7 perlu ditulis eksplisit; penyederhanaannya benar pada domain asal. L5Q5 perlu memperjelas penulisan konversi basis yang disebut dalam alasan opsiC; kunciC tetap satu-satunya opsi yang dapat diterima di antara opsi yang tersedia.

Bukti: [JSON lengkap 50 soal](audit.json), [CSV](entries.csv). Validasi mencakup cakupan unik, seluruh opsi, kecocokan kunci yang dinyatakan benar, PG valid tepat satu jawaban, serta 13 pemeriksaan hitung eksak. Semua 859 hash sumber/bank/config/stok/layanan tetap sama.

Reproduksi: `python variant_gen/tests/audit_indicator_02_academic.py`. Hasil ini audit akademik, bukan persetujuan publikasi atau kesetaraan kesulitan. **Indikator 3 menunggu instruksi berikutnya.**
