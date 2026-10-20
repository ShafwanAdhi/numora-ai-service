# Generator indikator 16?19 level 4?5: tahap pertama

Tanggal: 21 Oktober 2026. Target disepakati 27 dari 80 original baru (**33,75%**).

**27 generator config v1 aktif: 24 PG, 2 MCMA, 1 KATEGORI.** Tidak ada perubahan redaksi, opsi, kunci atau versi original; metadata generator_status pada 27 soal menjadi IMPLEMENTED. Keempat belas HOLD tetap ditahan; stok konseptual existing tidak berubah.

| Indikator | Generator baru | Total generator / 50 original |
|---|---:|---:|
| 16 | 2 | 26 |
| 17 | 8 | 36 |
| 18 | 9 | 39 |
| 19 | 8 | 38 |
| **Total** | **27** | **139 / 200** |

Sisa 53 original baru: 39 lolos audit belum mempunyai generator/stok, 14 HOLD_SOURCE. Kelompok 39 belum diklasifikasikan final numerik/konseptual. Di luar tambahan ini, delapan soal konseptual existing tetap memiliki 22 stok VERIFIED.

## Domain dan pemeriksaan

- k=0..30; faktor skala positif k+1. k=0 mereproduksi original persis. Homoteti mempertahankan bentuk dan tingkat tugas; panjang/koordinat linear, luas kuadrat, volume kubik. Sudut, faktor dilatasi yang ditanyakan dan pi yang ditentukan sumber tetap sesuai per soal.
- 837 input lengkap diperiksa dari teks hasil render, bukan nilai derived config. Setiap generator mempunyai 30 varian unik valid selain original: total810 dalam domain yang diperiksa.
- Oracle menghitung ulang jawaban, mengevaluasi opsi/pernyataan, memeriksa jumlah jawaban benar serta hasil numerik pembahasan. Mutasi kunci setiap opsi, angka jawaban benar, dan hasil pembahasan ditolak.
- Sepuluh seed dengan daftar kandidat terdahulu per soal lolos; seed sama deterministik. Semua27 POST /api/generate berhasil, database dipagari dalam tes, berkas penyimpanan hasil tidak dibuat.
- Rancangan sengaja dibatasi pada satu faktor skala per keluarga. Permintaan Generate dapat diulang; keragaman unik default tetap30 per soal, bukan tak terbatas. Perlu audit baru sebelum memperluas dimensi/rentang.
- Penulisan Word c{m} direproduksi saat k=0, dinormalisasi menjadi cm pada varian agar tidak menyerupai placeholder. Koordinat memakai koma pemisah komponen; desimal Indonesia diperlakukan terpisah.
- Tidak ada dependensi atau jalur runtime baru. Config existing, engine dan endpoint dipakai langsung. Self-adjustment tetap nonaktif, belum approval kurikulum/kalibrasi IRT.

Bukti hanya berupa hitungan, hash config dan hash signature pada [evidence.json](evidence.json). Tidak menyimpan isi varian.

## Daftar generator

| ID | Domain | Varian unik valid |
|---|---|---:|
| `pg-16-5-4` | k=0..30 | 30 |
| `kategori-16-5-10` | k=0..30 | 30 |
| `pg-17-4-1` | k=0..30 | 30 |
| `pg-17-4-2` | k=0..30 | 30 |
| `pg-17-4-3` | k=0..30 | 30 |
| `pg-17-4-4` | k=0..30 | 30 |
| `pg-17-4-5` | k=0..30 | 30 |
| `pg-17-5-2` | k=0..30 | 30 |
| `pg-17-5-4` | k=0..30 | 30 |
| `pg-17-5-5` | k=0..30 | 30 |
| `pg-18-4-1` | k=0..30 | 30 |
| `pg-18-4-2` | k=0..30 | 30 |
| `pg-18-4-4` | k=0..30 | 30 |
| `pg-18-4-5` | k=0..30 | 30 |
| `mcma-18-4-6` | k=0..30 | 30 |
| `pg-18-5-1` | k=0..30 | 30 |
| `pg-18-5-2` | k=0..30 | 30 |
| `pg-18-5-4` | k=0..30 | 30 |
| `pg-18-5-5` | k=0..30 | 30 |
| `pg-19-4-1` | k=0..30 | 30 |
| `pg-19-4-2` | k=0..30 | 30 |
| `pg-19-4-3` | k=0..30 | 30 |
| `pg-19-4-4` | k=0..30 | 30 |
| `mcma-19-4-6` | k=0..30 | 30 |
| `pg-19-5-1` | k=0..30 | 30 |
| `pg-19-5-3` | k=0..30 | 30 |
| `pg-19-5-4` | k=0..30 | 30 |

## Reproduksi

```powershell
python -B variant_gen/tests/author_drill_16_19_level45_batch1.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_16_19_level45_batch1.py
```

Uji khusus2 lulus; uji impor3, katalog2, cakupan bank9 lulus. Uji antarmuka umum17 lulus. Total33 tes lulus; git diff --check lulus. Builder dapat diulang; menolak menimpa config yang berubah. Importer sumber mengenali generator yang sudah terpasang.
