# Audit generator Drill indikator 11–15

Implementasi divalidasi pada worktree `feat/drill-11-15` dan telah diintegrasikan ke checkout interface `Numora-ai-service`. Bank terpisah dimuat melalui
`load_workspace_bank` bersama bank lama. Seluruh 25 kelompok indikator/level
berisi 10 original: 250 soal (125 PG, 75 MCMA, 50 KATEGORI).

| Indikator | Generator aktif |
|---|---:|
| 11 — relasi/fungsi | 41 |
| 12 — barisan | 48 |
| 13 — deret | 50 |
| 14 — sudut | 40 |
| 15 — Pythagoras/kesebangunan | 44 |
| Total | 223 |

Sumber: `variant_gen/data/drill-1-indicators-11-15/source.docx`, SHA-256
`08b30681b07398eaea08331029f8c6934d576aaa31294a6529fd8ac69dff5383`.
CSV, metadata, label kognitif, kunci dan pembahasan sumber dipertahankan.

## Bukti yang dapat diulang

- [Audit per ID](../../variant_gen/data/drill-1-indicators-11-15/audit.json):
  hash/version original dan config, domain parameter, seed berhasil/gagal,
  alasan rejection, serta hasil oracle. Target 20 varian berbeda, seeds 1–200.
- [Contoh hasil](../../variant_gen/data/drill-1-indicators-11-15/examples.json):
  15 snapshot contoh, masing-masing format pada masing-masing indikator.
  Ini fixture audit; snapshot operator tetap berada di store lokal.
- [Oracle independen](../../variant_gen/tests/drill_11_15_math.py): memakai
  `Fraction`, data stem/opsi yang sudah dirender, penjumlahan suku eksplisit,
  model posisi sudut, dan persamaan geometri. Tidak membaca ekspresi turunan
  config untuk menentukan jawaban. Semua opsi diuji, termasuk opsi salah.
- Tes parameter memeriksa ujung domain, kasus sudut sama, pergantian winner,
  dan syarat batas indeks. Tes HTTP memakai store/config sementara dan menolak
  koneksi database. CLI/UI mempertahankan history dan original seed 0.

Hasil sampling: **217 PASS**, **6 SHORT**, **0 FAIL**, **27 SKIP**.
SHORT berarti stok yang ditemukan di bawah target; bukan bukti stok seluruh
domain sudah habis. Tidak ada fallback yang menggunakan ulang jawaban/soal.

| Generator SHORT | Varian unik ditemukan |
|---|---:|
| `pg-11-3-2` | 10 |
| `pg-11-3-4` | 18 |
| `pg-11-4-2` | 14 |
| `pg-11-4-3` | 18 |
| `mcma-11-5-7` | 18 |
| `mcma-15-1-6` | 18 |

Aturan “teks jawaban benar berbeda” membatasi kapasitas, termasuk pada jumlah
anggota range. Sampling menambah setiap hasil ke daftar pembanding, sehingga
varian yang berhasil benar-benar unik terhadap original dan hasil sebelumnya.

## Soal yang tidak diaktifkan

Lima `HOLD_SOURCE` memerlukan keputusan akademik:

- `mcma-11-1-7`: rumus f tidak diberikan.
- `pg-11-2-4`: kunci sumber tidak sesuai hasil komposisi.
- `kategori-11-3-9`: makna relasi akar kuadrat ambigu.
- `mcma-15-2-8`: data panjang/sudut segitiga tidak konsisten.
- `pg-15-4-2`: data SSA tidak mendukung klaim dua solusi sumber.

Sebanyak 22 `DEFERRED_CONCEPTUAL` tetap dapat dibaca, tetapi tidak memiliki
generator. Alasan per ID ada pada metadata/audit. Tidak ada koreksi sumber
yang diterapkan diam-diam. Ini cakupan yang disepakati dalam spec: seluruh
223 soal ACTIVE memiliki generator; 27 soal lain tetap memiliki guard.

## Perbaikan dari validasi

- Jumlah suku `mcma-13-2-7` tetap 20 ketika amplitudo deret berubah.
- Koma prosa dipisahkan dari kurung rumus pada tiga config.
- `pg-14-5-4` mengecualikan parameter yang membuat dua sudut sama,
  karena opsi menyatakan ketiga sudut berbeda.
- `pg-14-1-5` mengecualikan parameter yang membuat dua opsi PG sama.
- Review independen menemukan empat klaim yang belum berubah dengan benar:
  nilai pembanding negatif pada `pg-11-5-4`, penyebut langkah pembagian pada
  `mcma-12-5-7`, jumlah potongan pada `pg-13-2-4`, dan rasio serta konstanta
  identitas penjumlahan pada `mcma-13-5-7`. Keempat config diperbaiki;
  oracle kini memeriksa klaim dan langkah hitung tersebut.
- Tinggi siswa pada `pg-15-1-5` dan `pg-15-4-4` tetap realistis ketika
  parameter berubah; hasil dan pengecoh disesuaikan dengan rasio baru.
- Pembahasan `pg-15-2-3` dan `mcma-15-1-8` menjelaskan SAS/SSS/AAA,
  menggantikan pembahasan Pythagoras umum yang tidak sesuai pertanyaan.
- Ekspor kanonik hanya menerima label tunggal C1–C6; `C3 & C4` dan
  `C4 & C5` tetap disimpan utuh secara lokal sampai klasifikasi disahkan.

Pembahasan config berisi metode dan penilaian opsi, sementara pembahasan
original mempertahankan uraian sumber. Pemeriksaan numerik bukan approval
kurikulum maupun bukti kesetaraan kesulitan/IRT. Mayoritas variasi memakai
amplitudo positif; generator tertentu mengubah indeks, rasio, range, atau
penilaian laporan. Variasi nama tidak membuktikan variasi tingkat kesulitan.

## Perintah

Audit tersimpan diuji ulang: hash config harus sesuai, lalu seluruh seed
berhasil diputar ulang dengan daftar pembanding yang sama dan oracle terbaru.
Browser Workbench diperiksa pada store/config sementara: generate,
regenerate, history, validasi/simpan config, dan tombol nonaktif untuk
HOLD_SOURCE. Bukti UI tersedia di `output/playwright/drill-11-regen.yml`,
`drill-11-config.yml`, dan `drill-15-hold.yml`. Tidak ada error konsol browser.

Dari root worktree:

```powershell
python -B variant_gen/cli.py view pg-11-1-4 s0
python -B variant_gen/cli.py lint pg-11-1-4 --n 20
python -B variant_gen/cli.py gen pg-11-1-4 s1 --store "$env:TEMP/numora-11-15-demo.jsonl"
python -B variant_gen/cli.py regen pg-11-1-4 s1 --reason "review lokal" --store "$env:TEMP/numora-11-15-demo.jsonl"
python -B -m unittest discover -s variant_gen/tests -v
python -B variant_gen/tests/audit_drill_11_15.py --output variant_gen/data/drill-1-indicators-11-15/audit.json
python -B variant_gen/webui.py
```

Workbench: Service AI > Drill > Paket 1 > indikator 11–15 > level 1–5.
Seluruh output tetap lokal; API produksi, publikasi database, generate LLM,
self-adjusting dan IRT berada di luar implementasi ini.
