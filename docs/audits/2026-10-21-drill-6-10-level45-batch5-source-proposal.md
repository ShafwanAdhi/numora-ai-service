# Sisa indikator 6–10 level 4–5: usulan revisi lokal

Status: USER_APPROVED / IMPLEMENTED, 21 Oktober 2026. Revisi minimum berikut disetujui pengguna dan diterapkan pada bank lokal tahap 6. [Laporan final](2026-10-21-drill-6-10-level45-batch6/README.md). Dokumen sumber dan audit historis tidak diubah; sumber mentah dan alasan perubahan tersedia dalam metadata. Persetujuan ini bukan approval kurikulum atau kalibrasi IRT.

Tujuh koreksi kunci yang pasti sudah diimplementasikan terpisah: `pg-6-4-1` D (70 menit), `pg-6-5-1` A (16 hari), `pg-6-5-3` B (3 jam), `pg-7-4-3` C (112 cm²), `pg-7-5-5` A (10 × 8 meter), `pg-9-5-2` D (kembalian Rp1.000), `mcma-10-4-7` A,B,D.

## Revisi yang memerlukan keputusan naskah

| ID | Revisi minimum yang diusulkan | Hasil original setelah revisi |
|---|---|---|
| pg-6-4-2 | Nyatakan setiap orang mengonsumsi 1 porsi/hari; sponsor mulai awal hari ke-3 sebelum konsumsi. Ganti opsi C menjadi hari ke-10. | Awal 20 orang; sisa 80; konsumsi bersih 10/hari; habis akhir hari ke-10, C. |
| pg-6-4-4 | Pertahankan pertanyaan durasi; ganti C dari 16 hari menjadi 47/3 hari (15 hari 16 jam). | Sisa 200 jatah-harian untuk 30 ayam; total 9+20/3 hari, C. |
| mcma-6-4-8 | Nyatakan semua kondisi bekerja 5 hari/minggu dengan produktivitas per jam-pekerja yang sama. | 240/(6×8×5)=1 unit/jam-pekerja; X=240, Y=6; A,B,C. |
| kategori-6-4-10 | Ganti 33,3% pada opsi ketiga menjadi 100/3% tepat. Buang deklarasi kunci yang masuk stimulus. | Tambahan minimum 4 pekerja; kenaikan jam tepat 1/3; 1,3 benar. |
| pg-6-5-2 | Ganti B menjadi 1,5 hari; C menjadi 1,25 hari tanpa konversi jam kalender. | Sisa 75 relawan-hari /12=6,25 hari; tambahan 1,25 hari kerja, C. |
| pg-6-5-4 | Nyatakan pekerja tambahan tersedia dengan produktivitas sesuai kelompoknya; tanyakan pemenuhan target dengan pekerja paling sedikit. Ganti D menjadi 10 penjahit kelompok Y. | X=6 dan Y=7,5 potong/orang/hari; minimum 10 pekerja, D. |
| mcma-6-5-8 | Definisikan satu porsi sebagai jatah harian satu ternak; ganti unit opsi D menjadi 600 porsi. | Q=15 hari, R=50 ternak, P=600 porsi; A,C,D. |
| kategori-6-5-10 | Opsi kedua: “Tambahan minimum pekerja agar selesai tepat waktu adalah 3 orang.” Buang deklarasi kunci dari stimulus. | Minimum sebenarnya 2; 1,3 benar. |
| pg-7-4-4 | Andi menyatakan “satu-satunya penyelesaian adalah x=0”; opsi B menyebut klaim tunggal tersebut. | Identitas berlaku semua real; A tunggal benar. |
| mcma-7-5-8 | Bersihkan pengulangan teks/LaTeX; satu harga A=(3x+15000), B=(5x−25000); opsi A ditulis x=20000. | Harga sama Rp75.000, dua kaus Rp150.000; A,B,D. |
| kategori-7-5-9 | Jelaskan 18 buku dipinjam kelompok lain dan tetap; empat buku tambahan dipinjam siswa baru yang masing-masing meminjam dua buku. Buang deklarasi kunci dari stimulus. | n=16, total awal50, siswa baru2 sehingga n=18; 1,3 benar. |
| pg-9-4-1 | Ganti opsi A duplikat menjadi Rp19.000; C cukup Rp18.000 tanpa catatan editorial. | Nasi Rp8.000, minuman Rp5.000; C. |
| pg-9-5-1 | Ganti harga pada opsi A menjadi sepeda air Rp12.500 dan komidi Rp20.000 sehingga alasan A salah. | Harga sebenarnya Rp20.000 dan Rp12.500; B tunggal benar. |
| pg-9-5-5 | Bersihkan pengulangan; C menjadi “Salah, karena panjang 11 meter, lebar 7 meter, luas 77 m²”; pertahankan kunci C. Buang catatan revisi yang bertentangan. | Klaim luas80 salah; C. |
| mcma-9-5-7 | Nyatakan harga satuan sama pada kedua toko; seluruh jumlah barang dihitung per pasang. | Kaus kaki Rp12.500/pasang, sarung tangan Rp15.000/pasang; B,D. |
| pg-10-4-2 | Tanyakan “bentuk Kelompok A dikurangi Kelompok B”; A menjadi 5a−10b+9, C menjadi 5a−10b+15 tanpa catatan editorial. | C tunggal benar. |
| kategori-10-5-9 | Hapus “(dalam ribuan)” dari opsi ketiga; satuan seluruh soal tetap rupiah. Buang deklarasi kunci dari stimulus. | Total 5x²−2; pada x=3 menjadi43 rupiah; 1,3 benar. |

## Soal konseptual

`mcma-7-5-6`: klasifikasi PLSV; sumber valid, kunci A,C. Usulan: stok terbatas melalui mekanisme konseptual yang sudah ada, bukan memaksakan generator numerik tak terbatas. Contoh keluarga tetap membedakan linear satu variabel, kuadrat, linear pecahan, serta dua variabel. Konten stok hanya ditulis jika pilihan stok disetujui; hasil generate runtime tetap tidak disimpan.

## Verifikasi sesudah keputusan

Reproduksi original versi revisi; cek seluruh opsi dan pembahasan dari stimulus hasil render; enumerasi parameter; uji korupsi jawaban; API/workbench tanpa penulisan varian; hash bank/config lama. Soal yang revisinya belum disetujui tidak diaktifkan.
