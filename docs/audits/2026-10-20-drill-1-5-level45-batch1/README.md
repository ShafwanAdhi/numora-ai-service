# Generator indikator 1-5 level 4-5 - tahap pertama

**ENGINEERING DECISION - instruksi pengguna, 20 Oktober 2026:** implementasikan 33 dari 100 soal original baru, mengikuti pembagian yang disetujui. Tahap ini selesai pada 33 ID; 67 sisanya tetap antrean. Tidak mengubah generator level 1-3 atau kelompok indikator lain.

## Cakupan

| Indikator | Level 4: nomor sumber | Level 5: nomor sumber | Generator |
|---|---|---|---:|
| 1 | 2, 3, 6, 9 | 1, 6, 9 | 7 |
| 2 | 4, 6, 8 | 1, 2, 6, 8 | 7 |
| 3 | 1, 2, 6, 9 | 1, 6, 9 | 7 |
| 4 | 1, 6, 9 | 1, 6, 10 | 6 |
| 5 | 1, 6, 9 | 1, 6, 9 | 6 |

Total: **33 original/config v1**, 17 level 4 dan 16 level 5; 13 PG, 12 MCMA, 8 KATEGORI. Semua pilihan memiliki hasil audit akademik VALID/CORRECT/CORRECT. Sumber: arsip indikator 1-5 tanggal 19 Oktober, SHA256 `0e868995fdeb3fe035b625c3bb8252424a2be7dea4dfe48413af79ede18f1147`.

Bank lokal tambahan berada di `variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch1/`. Katalog menggunakan `activity=DRILL`, `package_id=drill-1`, indikator dan level sumber asli. Sepuluh kelompok level masih parsial; jangan dianggap sepuluh soal lengkap per level. ID/nomor sumber tidak dipadatkan. Seluruh original lama tetap identik. Workspace kini 853 original (823 Drill, 30 Tryout) dan 779 generator (752 Drill, 27 Tryout).

## Perilaku dan batas

- Engine dan bahasa config existing digunakan tanpa evaluator/dependensi baru. Hanya pendaftaran bank default yang berubah; custom bank tetap standalone. Workbench, CLI dan katalog service melihat penambahan ini setelah proses di-restart.
- `original_values` mereproduksi stimulus, opsi dan kunci; redaksi original, pembahasan, caption kunci, catatan dan lokasi DOCX disimpan terpisah dalam metadata. Satu pecahan simbolik LaTeX a/b disajikan sebagai `(a)/(b)` agar tidak terbaca sebagai placeholder; bentuk matematikanya sama, raw source utuh.
- Pembahasan generator merupakan penjelasan parametrik baru yang dihitung dan diperiksa, bukan klaim identik verbatim dengan pembahasan original. Nilai original dapat dilihat melalui CLI `view ... s0` atau panel original workbench.
- Pada klasifikasi bilangan, radikan varian dapat menjadi kuadrat sempurna sehingga kunci klasifikasi berubah. Pada beberapa laporan analisis, label klaim benar ikut berpindah; klaim dan angka di stimulus tetap konsisten. Pada MCMA pembulatan, status pernyataan berubah sambil mempertahankan jumlah benar.
- Dua opsi PG yang awalnya hanya alasan kualitatif menyertakan hasil numerik pada varian agar jawaban menyatakan hasil perhitungan spesifik. Guard `same_answer_as_original`, hash, opsi berbeda dan jumlah benar tidak dilonggarkan.
- Parameter `k` menggunakan domain eksplisit, bukan penyesuaian otomatis. Kapasitas setelah constraints dan validator dihitung dengan enumerasi seluruh domain; seed berbeda tidak menjamin varian berbeda. Ini generator deterministik berhingga, bukan stok konseptual manual.
- **PROPOSED / belum disetujui Kurikulum:** rentang dan varian belum merupakan persetujuan publikasi, kesetaraan beban pengerjaan atau kalibrasi IRT. Ada keluarga yang menaikkan ukuran bilangan/kompleksitas faktorisasi; label level diwarisi dari sumber dan belum membuktikan kesulitan ekuivalen. `approval_status=NOT_CURRICULUM_APPROVED`, `self_adjustment_enabled=false`. Tidak ada import/publikasi DB utama, perubahan API/kontrak, atau penyesuaian rentang generator lama.

## Bukti pemeriksaan

- Seluruh **1.091 kombinasi input** dienumerasi. Semua kandidat yang memenuhi constraints, termasuk nilai original, diperiksa dengan oracle terpisah yang membaca teks rendered, tidak membaca `values_used` atau evaluator produksi.
- Oracle memakai Fraction, pembulatan half-up, akar Decimal 60 digit, perbandingan kuadrat eksak, FPB/KPK, kalender, rasio dan laju satuan. Semua opsi/pernyataan diberi nilai independen; hasil dan langkah utama pembahasan dibandingkan dengan perhitungan tersebut.
- Kapasitas efektif **999 varian** sebagai jumlah kapasitas per keluarga, minimum 25 dan maksimum 49 per generator. Ini bukan 999 soal original tambahan.
- **660 sampel unik** (20 per generator, seed 1-20 dengan pembanding in-memory) dan **1.650 sampel tambahan** (seed 201-250, dipanggil ulang untuk determinisme) lolos.
- Tes mutasi menolak kunci terbalik, pembahasan salah, klaim angka salah, radikan/operand yang tidak sesuai stimulus, KPK/FPB dengan operand lama dan alasan penyederhanaan rasio yang tidak sah.
- Seluruh 33 original/config dapat dibaca dan dipanggil melalui HTTP workbench; hasil diperiksa oracle, database dimock menolak koneksi dan store sementara tetap tidak dibuat.
- Hash **901 berkas terdahulu** berupa bank/config/stok, sumber masuk, audit awal dan layanan/kontrak tetap sama. Daftar baseline lengkap dan hash setiap config/bank tercantum dalam JSON.
- Review kode kedua menemukan operand KPK/FPB yang belum mengikuti stimulus dan alasan rasio yang terlalu umum; keduanya diperbaiki dan diberi tes regresi. Audit juga diuji ulang tanpa baseline `.scratch`, menggunakan baseline yang dibundel di JSON.

## Hasil verifikasi akhir

- `python -B -m unittest discover -s variant_gen/tests -q`: **194 tes lulus**, termasuk delapan tes batch baru dan regresi bank/generator lama.
- `python -B -m unittest discover -s tests/service -q`: **13 tes lulus, 11 tes PostgreSQL dilewati** karena memerlukan cluster terisolasi yang dimigrasikan. Tidak ada skema, kontrak atau operasi database yang diubah dalam tugas ini.
- `git diff --check`: lulus. Repo service utama tetap bersih; perubahan lokal pengguna yang sudah ada pada dokumen dan audit sebelumnya dipertahankan.

## Domain dan kapasitas per soal

`k` adalah indeks/input generator, bukan rentang angka langsung pada stimulus. Formula yang mengubahnya menjadi angka soal tersimpan dalam config v1 yang di-hash. Daftar input efektif lengkap dan alasan penyaringan ada pada `audit.json`.

| ID | Domain k yang dideklarasikan | Input efektif | Kapasitas varian |
|---|---|---:|---:|
| pg-1-4-2 | 0-30 (31 nilai) | 30 | 30 |
| pg-1-4-3 | 0-30 (31 nilai) | 30 | 30 |
| mcma-1-4-6 | 0-30 (31 nilai) | 30 | 30 |
| kategori-1-4-9 | 0-30 (31 nilai) | 30 | 30 |
| pg-1-5-1 | 0-30 (31 nilai) | 30 | 30 |
| mcma-1-5-6 | 0-30 (31 nilai) | 30 | 30 |
| kategori-1-5-9 | 0-30 (31 nilai) | 30 | 30 |
| pg-2-4-4 | 0-30 (31 nilai) | 30 | 30 |
| mcma-2-4-6 | 0-30 (31 nilai) | 30 | 30 |
| mcma-2-4-8 | 0-30 (31 nilai) | 30 | 30 |
| pg-2-5-1 | 0-30 (31 nilai) | 30 | 30 |
| pg-2-5-2 | 0-30 (31 nilai) | 25 | 25 |
| mcma-2-5-6 | 0-30 (31 nilai) | 30 | 30 |
| mcma-2-5-8 | 0-30 (31 nilai) | 30 | 30 |
| pg-3-4-1 | 0-30 (31 nilai) | 30 | 30 |
| pg-3-4-2 | 0-100 (101 nilai) | 49 | 49 |
| mcma-3-4-6 | 0-30 (31 nilai) | 28 | 28 |
| kategori-3-4-9 | 0-30 (31 nilai) | 30 | 30 |
| pg-3-5-1 | 0-30 (31 nilai) | 30 | 30 |
| mcma-3-5-6 | 0-30 (31 nilai) | 29 | 29 |
| kategori-3-5-9 | 0-30 (31 nilai) | 30 | 30 |
| pg-4-4-1 | 0-28 (29 nilai) | 28 | 28 |
| mcma-4-4-6 | 0-132 (31 nilai); pilihan/step | 30 | 30 |
| kategori-4-4-9 | 0-30 (31 nilai) | 30 | 30 |
| pg-4-5-1 | 0-30 (31 nilai) | 30 | 30 |
| mcma-4-5-6 | 0-30 (31 nilai) | 30 | 30 |
| kategori-4-5-10 | 0-30 (31 nilai) | 30 | 30 |
| pg-5-4-1 | 0-30 (31 nilai) | 30 | 30 |
| mcma-5-4-6 | 0-60 (31 nilai); pilihan/step | 30 | 30 |
| kategori-5-4-9 | 0-30 (31 nilai) | 30 | 30 |
| pg-5-5-1 | 0-30 (31 nilai) | 30 | 30 |
| mcma-5-5-6 | 0-60 (31 nilai); pilihan/step | 30 | 30 |
| kategori-5-5-9 | 0-30 (31 nilai) | 30 | 30 |

## Antrean dan cara verifikasi

**67 soal belum dikerjakan**: 39 tanpa temuan akademik penghalang masuk batch generator berikutnya; 28 perlu tindak lanjut akademik. Daftar lengkap berada di [pending.csv](pending.csv). Pembuatan generator berikutnya menunggu instruksi pengguna. Tidak memperbaiki soal tertahan secara sepihak.

```powershell
python -B variant_gen/tests/build_drill_1_5_level45_batch1.py
python -B variant_gen/tests/audit_drill_1_5_level45_batch1.py
python -B -m unittest discover -s variant_gen/tests -v
python -B -m unittest discover -s tests/service -v
python -B variant_gen/cli.py gen pg-1-4-3 s1
```

Perintah dijalankan dari root Numora-ai-service. Builder hanya menyusun asset v1 batch yang belum dirilis ini; perubahan setelah digunakan harus membuat versi baru. Audit dapat direplay tanpa `.scratch`; baseline tersimpan dalam `audit.json`.

[JSON lengkap dan 660 contoh](audit.json) - [CSV 33 generator](entries.csv) - [CSV antrean](pending.csv).
