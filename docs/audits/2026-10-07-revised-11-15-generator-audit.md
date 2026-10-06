# Generator revisi indikator 11–15 — 7 Oktober 2026

Empat soal original versi 2 kini memiliki generator v1. Alur UI/CLI yang ada membaca konfigurasi dan status aktifnya; tidak ada perubahan mesin generator, akses database, atau penyimpanan varian siswa. Penyesuaian otomatis tetap tidak aktif. Batas angka berikut ditetapkan pada konfigurasi, tanpa perluasan otomatis.

| ID | Masukan yang dapat diubah | Syarat yang dipertahankan |
|---|---|---|
| `mcma-11-1-7` | Input positif 2–5, besar input negatif 3–6, konstanta 2–7 | Input positif lebih kecil dari besar input negatif; hasil keduanya positif. Tetap kuadrat lalu pengurangan, dua input berbeda, empat pernyataan, dua benar. |
| `pg-11-2-4` | Koefisien 2–4, konstanta 2–5, pengurang 1–3, input 3–7 | Hasil fungsi dalam positif. Tetap dua fungsi linear, dua langkah substitusi, empat opsi berbeda, satu benar. |
| `kategori-11-3-9` | Tiga akar berbeda dari 1–7; nama himpunan A/B, C/D, P/Q | Akar diurutkan; tetap tiga kuadrat positif dan enam akar positif-negatif. Relasi maju bukan fungsi, relasi balik fungsi, dua input boleh mempunyai hasil sama. |
| `pg-15-4-2` | Sisi pendek 4–9 cm, sisi panjang 7–12 cm, sudut 30–60° kelipatan 5; nama titik | Sisi yang berhadapan dengan sudut diketahui lebih panjang; sudut lancip. Tetap satu segitiga yang mungkin dan pertanyaan menilai alasan sisi-sudut-sisi, bukan menolak kesimpulan kongruen. |

Nama himpunan/titik hanya mengubah tampilan. Varian yang memakai nama baru tetapi seluruh bilangannya sama dengan original ditolak melalui syarat konfigurasi. Nama baru juga membuat teks jawaban benar berbeda, sesuai pemeriksaan generator yang sudah ada; pemeriksaan tersebut tidak dilonggarkan. Perubahan bilangan mempertahankan pola tugas, bukan menambah langkah atau kasus baru.

Kesetaraan beban pengerjaan diperiksa dari jumlah input, anggota himpunan, langkah, opsi, dan kasus geometri. Kesetaraan tingkat kesulitan berdasarkan respons siswa belum dapat dipastikan tanpa data respons dan kalibrasi.

## Hasil pemeriksaan

- Keempat konfigurasi membangun ulang stem, setiap opsi, dan kunci original v2 secara tepat.
- Masing-masing menghasilkan 20 varian unik: **80 varian teruji**. Ini jumlah sampel pemeriksaan, bukan batas stok generator.
- Kebenaran jawaban diperiksa dari teks soal yang dihasilkan, terpisah dari rumus konfigurasi.
- Tes menelusuri seluruh kombinasi masukan dalam batas yang diizinkan, termasuk ujung rentang; tambahan 100 seed per generator diperiksa. Seed yang sama menghasilkan varian yang sama.
- Catatan hasil varian menyertakan original versi 2, konfigurasi versi 1, penanda isi, indikator, level, kunci, dan pembahasan.
- **21 tes indikator 11–15 lulus.** Sumber lama, seluruh konfigurasi sebelumnya, dan stok manual tetap utuh: **701 berkas** cocok dengan penanda isi sebelum pekerjaan ini.
- **158 tes keseluruhan lulus**, exit code 0. Tes UI mencakup empat generator baru melalui permintaan HTTP, pengulangan seed, penolakan soal yang ditahan, serta memastikan database dan penyimpanan varian tidak dipakai. Tes penolakan lama diperbarui menggunakan `mcma-15-2-8`, karena `pg-11-2-4` kini sudah aktif.

```powershell
python -B -m unittest discover -s variant_gen/tests -q
```

[Laporan per generator](../../variant_gen/data/drill-1-indicators-11-15/revision-generator-audit.json), [contoh hasil](../../variant_gen/data/drill-1-indicators-11-15/revision-generator-examples.json), dan [tes seluruh masukan](../../variant_gen/tests/test_drill_11_15_revisions.py).

## Soal yang tetap ditahan

`mcma-15-2-8` tidak dibuatkan generator. Sudut A=75°, B=65°, C=40° dan AB=6 cm memerlukan BC sekitar 9,0163 cm, sedangkan sumber menulis tepat 9 cm tanpa keterangan pembulatan. Isi revisi tetap tersimpan, status `HOLD_SOURCE` dipertahankan, dan pembuatan varian tetap ditolak. Rincian ada pada [riwayat impor](2026-10-07-drill-11-15-source-revision.md).

Bank indikator 11–15: **227 generator + 22 soal dengan stok manual + 1 soal ditahan = 250 soal**. Stok manual global tetap 67 soal dengan 206 varian. Penghitungan repo saat pemeriksaan: **679 generator Drill + 67 soal dengan stok + 44 tanpa keduanya = 790 soal**; jumlah ini juga mencakup pembaruan indikator lain yang sudah tersedia.
