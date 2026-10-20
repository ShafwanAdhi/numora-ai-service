# Tahap 5 — Audit akademik indikator 4–5

Cakupan disetujui: **100 soal indikator 4–5 saja**. Bagian selanjutnya akan mencakup lima indikator per audit, sesuai instruksi terbaru; indikator 6–10 menunggu instruksi.

| Indikator | Entri | Tanpa temuan yang menghalangi | Perlu tindak lanjut |
|---|---:|---:|---:|
| 4 | 50 | 41 | 9 |
| 5 | 50 | 43 | 7 |

Seluruh opsi/pernyataan, kunci, pembahasan, dan catatan diperiksa. Sepuluh tabel data dibaca langsung dan disertakan dalam JSON. Jawaban bersyarat diberi label khusus; kunci yang benar secara hitung tidak otomatis mengesahkan asumsi yang hilang.

| Komponen (100 soal) | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | 88 | 1 | 11 |
| Kunci | 87 | 2 | 11 |
| Pembahasan | 85 | 5 | 10 |

Hitungan per komponen berdiri sendiri. Ini pemeriksaan akademik, bukan persetujuan publikasi atau kesetaraan kesulitan. Semua usulan berikut **PROPOSED, belum diterapkan/disetujui Kurikulum**.

| Lokasi | Temuan utama dan usulan |
|---|---|
| I4 L4Q5 | Konteks ubin/lantai bercampur balok/kubus; header tentang 300/900 rusak. KPK 60 benar tetapi model geometri dan besaran yang ditanya harus ditetapkan ulang. Panjang rusuk dan jumlah balok jangan disamakan. |
| I4 L5Q5 | Jadwal awal 42 hari, usulan I 14 hari, usulan II 36 hari. B benar terhadap I, D benar terhadap jadwal awal 42 hari. Tegaskan acuan: kedua usulan tidak memperpanjang jadwal awal. |
| I4 L4Q4,L4Q8,L5Q4,L5Q8,L5Q9 | Maksimum memakai FPB memerlukan komposisi setiap kelompok/kotak yang sama. Syarat ini belum tertulis; tambahkan sebelum mengesahkan kunci. |
| I4 L5Q4 | Huruf C menunjuk Regu B, tetapi caption memakai Evaluasi III yang tidak didefinisikan. Perjelas menjadi C. Laporan Regu B, setelah syarat pembagian sama diperjelas. Ini bukan kesalahan huruf yang sudah terbukti. |
| I5 L5Q4 | Harga Alfa Rp4.000/buku, Beta Rp3.700/buku, hemat Rp300. Evaluasi Y berada pada **opsi B**, bukan header C. Pembahasan harga benar; usulan kunci B. |
| I5 L1Q3, L2Q3, L3Q3, L4Q3, L5Q3 | Kapasitas/waktu hanya memberi debit bila pengisian dari kosong tanpa aliran lain. Volume awal belum disebutkan. Jawaban kondisional masing-masing 25, 18, selisih 4, selisih 5, dan Keran B 30 > Keran A 25 liter/menit. Tambahkan kondisi pengisian; bukan koreksi angka otomatis. |
| I4 L4Q7 | Pembahasan menyebut detik 48, seharusnya menit 48. Kunci ABD tetap. |
| I4 L4Q8 | Catatan tentang membagi 9 dengan 3 tidak membuktikan jumlah wadah maksimum 27. Jelaskan kenaikan 9×3 dan keterbagian kedua barang. |
| I4 L5Q7 | Catatan 300/72=4,16 seharusnya 25/6≈4,1667; jumlah kejadian mengambil bilangan bulat ke bawah (4), bukan pembulatan terdekat. |
| I5 L3Q3 | Angka 4 hilang pada baris selisih 24−20; tercantum benar pada alasan opsi berikutnya. Lengkapi persamaan. |
| I5 L4Q10 | Catatan 108/8 menghasilkan 13,5 jam, bukan 14 tanpa pembulatan tambahan. Waktu benar 108/9=12 jam. |

Catatan minor lain: jumlah jadwal/siswa tidak konsisten pada I4L3Q1/I4L4Q1; spasi pada 90 cm di I4L4Q10; pengulangan kata denah pada I5L1Q2; I5L1Q4 sudah memberikan harga Rp31.500 yang ditanyakan sehingga tidak mengharuskan perhitungan rasio. Detail bukti dan usulan per soal tersedia pada keluaran.

Asumsi ideal yang belum tertulis dibedakan dari kesalahan hitung. Misalnya, bak 450 liter yang sudah berisi 90 liter hanya menerima 360 liter selama 18 menit: debit 20 liter/menit, bukan 25. Pembagian 96 laki-laki dan 120 perempuan juga bisa menjadi 96 kelompok campuran tidak identik, sehingga 24 bukan maksimum tanpa syarat keseragaman.

[JSON lengkap dan bukti eksak](audit.json) · [CSV 100 soal](entries.csv). Verifikasi meliputi 100 posisi unik, penilaian semua opsi, kecocokan kunci yang dinyatakan benar, PG valid satu jawaban, enumerasi pembagi/kelipatan dan kejadian, kalender, rasio, satuan, dan sepuluh tabel data.

Seluruh 859 hash sumber/bank/config/stok/layanan tetap sama. Tidak ada perubahan API, database, bank aktif, generator, atau pemetaan runtime. Reproduksi: `python variant_gen/tests/audit_indicators_04_05_academic.py`.

**Berhenti di indikator 5. Bagian berikutnya: indikator 6–10, menunggu instruksi.**
