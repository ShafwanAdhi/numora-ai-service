# Audit kesesuaian gambar original dengan generator Tryout

Tanggal pemeriksaan: 27 Oktober 2026. Cakupan: paket lokal `tryout-1`.

**Klarifikasi pengguna setelah audit:** angka dan ekspresi pada gambar boleh
diganti mengikuti generator; yang ingin dipertahankan adalah bentuk dasarnya.
Alternatif membekukan angka atau menjadikan gambar sebagai kondisi acuan di
bawah bukan pendekatan yang dipilih. Rancangan berikutnya memakai label dinamis
dan posisi air parametrik: [design gambar varian](../../superpowers/specs/2026-10-27-tryout-image-variants-design.md).

Audit ini menilai apa yang terjadi **jika gambar original dipakai kembali pada
varian**. Ini bukan pernyataan bahwa pipeline runtime sudah memasangkan gambar
tersebut dengan semua varian. Tidak ada perubahan bank, config, gambar, DB,
R2, atau kebijakan generator. Rekomendasi berikut berstatus **PROPOSED**, belum
diterapkan dan belum merupakan persetujuan akademik.

## Hasil pemeriksaan

- 30 original: 27 mempunyai generator; 3 konseptual tidak mempunyai generator.
- 22 generator tidak terkait gambar tertanam pada DOCX yang diperiksa.
- Kelima generator yang terkait gambar mempunyai masukan yang berpotensi
  bertentangan dengan angka atau ekspresi yang tercetak di gambar.
- Semua 27 config terbaru lolos validasi dan reproduksi original efektif.
- 540 keluaran diperiksa: seed 1–20 per generator, menggunakan oracle matematika
  existing yang menghitung hasil secara terpisah dari ekspresi config.
- Dari 100 sampel untuk lima soal bergambar, 99 mempunyai perbedaan label.
  Ini hasil sampel, bukan estimasi probabilitas ataupun kapasitas menyeluruh.
- Hash seluruh berkas bank Tryout, semua versi config Tryout, dan arsip/gambar
  incoming yang diperiksa sama sebelum dan sesudah audit.

Config terbaru: `tryout-1-b2-q01` menggunakan v2; 26 generator lainnya v1.
SHA-256 berkas dan hash semantik config/original tercantum dalam `audit.json`.

## Batas toleransi

Perbedaan proporsi gambar perspektif atau skematis dapat diterima jika siswa
tidak diminta mengukur gambar, hubungan geometri tetap benar, dan sifat
skematisnya jelas. Pernyataan “gambar tidak berskala” tidak menyelesaikan dua
label eksplisit yang berbeda untuk ukuran atau sudut yang sama.

Contoh: bentuk persegi panjang yang tidak persis mengikuti perbandingan sisi
berbeda dari tulisan `20 m` pada gambar yang bertentangan dengan `40 m` pada
narasi. Warna, pohon, kursi, dan wajah dadu dalam ilustrasi bukan otomatis data
soal; jangan memperlakukan ilustrasi dadu sebagai hasil lemparan aktual.

## Lima generator bergambar

| ID | Label gambar | Masukan dan turunannya yang terkait | Kesesuaian jika config sekarang tetap dipakai | Cara mempertahankan berkas gambar |
|---|---|---|---|---|
| `tryout-1-b3-q02` | Panjang 20 m; lebar/diameter 14 m | `p` 15–80; `r` 7/14/21/28; `width=2*r`; syarat `p>width` | Angka ukuran dapat bertentangan. Seluruh 20 sampel berbeda dari label. | Kunci `p=20,r=7`; tidak tersisa masukan bebas sehingga tidak menghasilkan varian baru pada pola soal sekarang. Alternatif: jadikan gambar ukuran acuan lalu tanyakan taman hasil pembesaran yang dinyatakan eksplisit. |
| `tryout-1-b3-q03` | `(3x+15)°` dua kali; `(5x−25)°`; 50° | `x` 5–25, `a` 2–5, `b` 5–20, `c` 6–9, `other` 30–75 langkah 5; `offset`, `angle`, `ans` | Koefisien `c` tidak pernah 5 saat generasi, sehingga tidak ada keluaran yang cocok seluruh label. Hasil numerik yang kebetulan sama tidak menjadikan ekspresinya cocok. | Ekspresi tetap memaksa x=20, sudut A=75°, B=50°, C=55°; tidak ada variasi soal yang sama. Alternatif: pertanyaan baru yang secara eksplisit meminta keadaan hipotetis setelah salah satu sudut diubah. |
| `tryout-1-b3-q04` | Dua rusuk 12 cm; tinggi total 18 cm; tinggi air 2/3 | `s` 6–30 langkah 3, `h` 9–45 langkah 3, `p` 1/2, `q=3`; `ratio`, `sw`, `hw` | Perubahan sisi/tinggi bertentangan dengan label. Perubahan rasio ke 1/3 juga bertentangan dengan keterangan 2/3 dan posisi arsiran. | Kunci semua nilai yang tercetak: tidak tersisa variasi. Alternatif: gambar sebagai wadah acuan, pembesaran seluruh ukuran linear dengan faktor yang disebut jelas, dan rasio air tetap 2/3. |
| `tryout-1-b3-q06` | Radius 7 dm dua kali; diameter 14 dm; tinggi tabung 10 dm; balok 15×12×12 dm | `r` 7/14/21; `h` 8–25; `p` 10–35; `l` 10–30; `t` 8–30. `threshold` 500–12000 langkah 50 tidak tertulis di gambar. | Kelima dimensi bebas dapat bertentangan. Radius kubah/tabung dan diameter harus terikat pada nilai `r` yang sama. | Kunci dimensi dan variasikan `threshold`: secara matematika dapat dibuat, tetapi semua 226 nilai yang lolos batas kubah ditolak validator saat ini karena jawaban benar tidak berubah. Alternatif: perluas pola pernyataan benar secara terkontrol, atau gunakan pembesaran rancangan acuan. |
| `tryout-1-b4-q05` | 180 pada kartu dan `n=180 kali` | `times` 72–720 langkah 36; `threshold` 8–12 tidak ada di gambar | Perubahan `times` bertentangan dengan dua label 180. Wajah dadu yang tergambar tidak membatasi percobaan yang mungkin. | Kunci `times=180`, variasikan `threshold`. Empat kandidat berbeda lolos semua validator sekarang: 8, 9, 11, 12. |

Pada gambar sudut, posisi garis dan bentuk segitiga juga merupakan sketsa;
jangan menyimpulkan nilai sudut dengan mengukur piksel. Masalah yang dibuktikan
audit ini adalah perubahan **label**, bukan pengukuran kemiringan gambar.

## Pemeriksaan mempertahankan seluruh label

Eksperimen menggunakan nilai yang disuntikkan dalam memori; config tidak diubah.
Seluruh domain `threshold` diperiksa untuk soal tangki dan dadu. Untuk tiga
soal lain, seluruh masukan dasar sudah ditentukan oleh label gambar.

| Soal | Kandidat cocok gambar yang diterima validator sekarang | Alasan |
|---|---:|---|
| Taman | 0 | Kandidat yang sama dengan original dan jawaban benar yang sama ditolak. |
| Sudut | 0 | Selain penolakan original/jawaban sama, `c=5` di luar domain generasi sekarang. |
| Limas | 0 | Kandidat original dan jawaban benar yang sama ditolak. |
| Tangki | 0 | 5 nilai threshold gagal syarat `hem<threshold`; 226 lainnya gagal `same_answer_as_original`. Salah satunya juga sama dengan original. |
| Dadu | 4 | Threshold 8,9,11,12 memberi frekuensi harapan 75,50,15,5; threshold 10 kembali menjadi original. |

Validator membandingkan **isi opsi jawaban benar**, bukan sekadar huruf kunci.
Mengubah opsi salah pada soal tangki tidak mengubah isi opsi benar A, B, dan D.
Karena itu, solusi membekukan dimensi tangki memerlukan perubahan pola soal atau
keputusan eksplisit mengenai aturan jawaban sama; audit tidak mengubah aturan.

Empat variasi dadu merupakan kapasitas untuk pembatasan/pola ini, bukan bukti
kesetaraan kesulitan atau persetujuan publikasi. Menambahkan pembatasan pada
generator tetap perlu config versi baru; audit tidak mengaktifkannya.

## Inventaris tanpa gambar

Seluruh masukan dasar generator berikut diperiksa dan dicatat dalam CSV/JSON.
Tidak ada gambar tertanam yang terpetakan ke soal-soal ini pada sumber DOCX
yang diperiksa, sehingga tidak ditemukan hubungan nilai generator–gambar.
Ini bukan audit akademik baru menyeluruh ataupun pernyataan tentang sumber lain.

| Bab | Generator tanpa gambar | Jumlah |
|---|---|---:|
| 1 | Soal 1,2,3,4,5,6,8 | 7 |
| 2 | Soal 1,2,3,4,5,6,7,8 | 8 |
| 3 | Soal 1,5,7 | 3 |
| 4 | Soal 1,3,4,7 | 4 |

Tanpa generator dan tanpa gambar: Bab 1 Soal 7; Bab 4 Soal 2 dan 6. Ketiganya
berstatus konseptual; tidak dihitung sebagai generator yang sudah diperiksa.

## Rekomendasi agar tidak mengganti gambar

1. Untuk pola soal sekarang, dadu dapat mempertahankan gambar dengan
   `times=180`. Empat kandidat tersisa sudah dibuktikan melalui enumerasi.
2. Untuk empat gambar lainnya, mempertahankan original sebagai stok manual
   merupakan pilihan yang langsung konsisten tanpa perubahan soal atau gambar.
3. Jika tetap menginginkan variasi, gambar dapat dipakai sebagai **gambar acuan**,
   lalu narasi secara eksplisit menanyakan perubahan dari keadaan acuan tersebut.
   Ini usulan revisi soal/generator, bukan toleransi pada label yang bertentangan.

Contoh usulan, bukan perubahan aktif:

- Taman: “Gambar menunjukkan taman awal. Seluruh ukuran linear diperbesar dua
  kali. Berapa luas taman yang baru?” Label 20 dan 14 tetap benar untuk acuan.
- Limas: wadah pada gambar adalah acuan; semua ukuran linear diperbesar dua kali
  dan air tetap mencapai 2/3 tinggi. Volume air baru = 256×2³ = 2048 cm³.
- Tangki: kedua rancangan acuan dibesarkan dua kali. Seluruh dimensi aktual harus
  diturunkan dari satu faktor yang sama, bukan diacak secara independen.
- Sudut: sudut pada gambar menjadi keadaan awal, kemudian sudut B diperbesar
  dengan besar tertentu sementara sudut A tetap; tanyakan sudut C yang baru.

Pendekatan acuan mempertahankan aset PNG/R2, tetapi mengubah tuntutan pengerjaan
dan perlu review akademik, kunci/pembahasan, dan versi soal/config yang baru.
Jangan menerapkannya hanya dengan catatan umum “abaikan angka pada gambar”.

## Bukti dan reproduksi

- `audit.json`: seluruh 30 entri, masukan dasar, binding label, versi/hash,
  contoh seed, hasil pemeriksaan batas, serta hash sebelum/sesudah.
- `entries.csv`: ringkasan per soal untuk penyaringan.
- `audit.py`: audit yang dapat diulang dari root repo AI:

  ```powershell
  python docs/audits/2026-10-27-tryout-image-compatibility/audit.py
  ```

Audit tidak memanggil database/R2 dan tidak menguji tampilan browser ataupun
publikasi paket. Pemeriksaan varian memakai oracle existing `check_math` untuk
paket Tryout; keberhasilannya tidak menggantikan review akademik gambar.
