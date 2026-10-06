# Generator revisi Drill Paket 1 indikator 6–10

Sebelas original v2 yang diterima kini mempunyai konfigurasi v1. Bank menjadi **140 ACTIVE, 9 DEFERRED_CONCEPTUAL, 1 HOLD_SOURCE** dari 150 original. Sembilan soal konseptual tetap memakai stok manual. Level 4–5 belum tersedia.

Original CSV, ledger revisi, arsip DOCX, dan kunci sumber tidak diubah. Generator memakai engine JSON/Fraction yang sudah tersedia; tidak menambah dependensi atau fungsi runtime per soal. UI/CLI memuat konfigurasi baru otomatis setelah proses dimulai ulang.

## Parameter dan bukti matematika

Parameter konfigurasi `k` adalah faktor skala integer positif; default 1–40, `original_values.k=1`. Untuk soal dengan simbol matematika bernama k, faktor ini hanya parameter internal; simbol k pada stimulus tetap konstanta yang ditanyakan.

| ID | Yang divariasikan | Pemeriksaan independen seluruh opsi |
|---|---|---|
| `pg-6-1-5` | Bensin awal dan opsi volume | Bensin × luas target / luas awal. |
| `pg-7-1-2` | Tambahan/pengurangan saldo dan opsi | Persamaan x + tambahan = 3x − pengurangan. |
| `pg-7-1-3` | Konstanta ukuran, keliling, opsi luas | Solusi x, panjang/lebar positif, luas hasil perkalian. |
| `pg-7-2-4` | Ruas kanan dan nilai kritis a | Koefisien x hilang; kontradiksi kecuali satu nilai a. |
| `pg-7-3-5` | Konstanta di kurung, nilai kritis k | Penyederhanaan identitas/kontradiksi. |
| `mcma-8-2-8` | Konstanta pecahan dan seluruh langkah | KPK, distributif, pengelompokan, pembalikan tanda, batas solusi. |
| `pg-9-1-3` | Konstanta garis pertama, nilai kritis k | Koefisien sebanding; garis berhimpit pada satu nilai k. |
| `pg-9-1-5` | Konstanta sistem dan nilai y | Solusi sistem serta syarat metode langsung tanpa menulis ulang. |
| `pg-9-2-5` | Biaya tetap dan jumlah kaus impas | Titik potong dengan x integer positif; substitusi langsung dua bentuk y. |
| `pg-9-3-2` | Vektor penerimaan | Setiap matriks kandidat dikalikan matriks koefisien; harus menghasilkan identitas dan vektor ruas kanan yang sesuai. |
| `pg-9-3-4` | Konstanta sistem, langkah, koordinat | Substitusi eksplisit pada persamaan kedua dan titik potong. |

Semua original direproduksi tepat, termasuk format rupiah, desimal, dan LaTeX matriks. Placeholder kini memakai nama variabel sah; grup angka LaTeX serta nama environment setelah `\begin`/`\end` dipertahankan. Variabel tak dikenal tetap ditolak.

## Verifikasi

- Seluruh 40 nilai default per soal, termasuk reproduksi original: 440 pemeriksaan matematika.
- Seed 1–20 menghasilkan 20 kandidat unik per soal, dibandingkan hanya dalam memori.
- Seed independen 201–400: 2.200 hasil lulus oracle matematika, tanpa kegagalan generasi.
- Nol, negatif, dan pecahan ditolak oleh filter parameter.
- HTTP: 11 soal tersedia sebagai generator, lint lulus, seed berulang konsisten, seed 0 ditolak untuk generate; perubahan config v1→v2 diuji dalam direktori sementara.
- Hasil generate tidak disimpan. Respons memuat original v2, config, seed, opsi, kunci, dan pembahasan. Database tidak diakses.

Tes: `python -B -m unittest discover -s variant_gen/tests -p 'test_drill_6_10*.py' -v` dan `python -B -m unittest discover -s variant_gen/tests -p test_webui.py -k revised_6_10 -v`.

Suite lengkap terbaru: **158 tes lulus dalam 93,158 detik**. Browser Playwright memeriksa seluruh 11 ID melalui filter aktivitas/paket/indikator/level, tombol Generate, editor config, pembahasan, dan generate berulang dengan seed 11. Soal HOLD menampilkan alasan serta tombol Generate nonaktif; Regen tidak tersedia. Browser tidak mencatat error/warning.

`ponytail:` satu faktor skala memberi 39 nilai nonoriginal per soal pada konfigurasi default. Generate dapat diulang tanpa batas request, tetapi hasil dapat berulang. Tambahkan parameter independen dengan review matematika bila diperlukan lebih banyak varian unik; jangan melonggarkan validator jawaban.

## Soal yang tetap ditahan

`mcma-6-3-7` tidak mempunyai config. Konflik waktunya dan klaim `42/8 = 5` belum diperbaiki; generate/lint/config save tetap ditolak. [Provenance dan temuan sumber](2026-10-07-drill-6-10-source-revision.md).
