# Revisi sumber indikator 11–15 — 7 Oktober 2026

Catatan berikut merekam tahap impor sebelum pembuatan generator. Tahap berikutnya sudah selesai: empat generator aktif, satu soal tetap ditahan. Status dan pemeriksaan terkini ada pada [laporan generator revisi](2026-10-07-revised-11-15-generator-audit.md).

Dokumen tim kurikulum telah dimasukkan ke [arsip revisi](../../variant_gen/data/drill-1-indicators-11-15/source-revision-2026-10-07.docx). SHA-256: `2ea7ebb8e96b8a210ce0368210cd0539f38e57b96bdfd022dd715438f61ba5c6`. Dokumen merupakan bahan soal; catatan di dalamnya tidak dijalankan sebagai perintah program.

Seluruh 250 soal dicocokkan berdasarkan indikator, level, dan nomor soal. Tepat **5 soal berubah**, semuanya berasal dari daftar soal yang ditahan karena masalah sumber. Sebanyak **245 soal lain tidak berubah**, termasuk 22 soal tanpa generator yang sudah memakai stok manual.

Lima revisi disimpan sebagai soal versi 2 melalui [catatan revisi](../../variant_gen/data/drill-1-indicators-11-15/original_revisions.jsonl). CSV dasar dan dokumen sumber lama tetap utuh. Catatan tersebut menyimpan isi serta keterangan sumber sebelumnya; metadata aktif mencatat dokumen baru, pembahasan, alasan penundaan, dan status pemeriksaan.

## Hasil per soal

| ID | Perubahan | Kunci versi 2 | Hasil pemeriksaan |
|---|---|---|---|
| `mcma-11-1-7` | Menambahkan definisi `f(x) = x² − 3` yang sebelumnya hilang | A,C | `f(2)=1` dan `f(−3)=6`; menunggu generator |
| `pg-11-2-4` | Mengganti kunci D menjadi B | B | `g(3)=2`, kemudian `f(2)=7`; menunggu generator |
| `kategori-11-3-9` | Memperjelas pasangan melalui `y²=x` dan `x=y²`, sehingga tidak rancu dengan fungsi akar utama | 2 | A Salah, B Benar, C Salah; menunggu generator |
| `mcma-15-2-8` | Sudut A menjadi 75°, BC menjadi 9 cm, dan klaim QR menjadi 13,5 cm | B,D, masih klaim sumber | Urutan panjang sisi sudah diperbaiki, tetapi panjang sisi belum cocok persis dengan sudut; tetap ditahan |
| `pg-15-4-2` | Pertanyaan menilai alasan sisi-sudut-sisi Rani; pembahasan mengakui kedua segitiga tetap kongruen dengan alasan lain | D | Sudut A bukan sudut di antara AB dan BC. Data sisi 6 dan 8 serta sudut A 40° hanya memungkinkan satu segitiga; menunggu generator |

Pada `kategori-11-3-9`, tiap anggota A mempunyai dua pasangan di B, sehingga hubungan A ke B bukan fungsi. Sebaliknya, tiap anggota B mempunyai satu pasangan di A. Dua anggota domain mempunyai hasil yang sama tidak melanggar syarat fungsi.

## Masalah yang masih tersisa

Pada `mcma-15-2-8`, sudut A=75° dan B=65° menghasilkan C=40°. Jika AB tepat 6 cm, panjang BC yang cocok dengan ketiga sudut adalah sekitar **9,0163 cm**, bukan tepat 9 cm:

`BC = AB × sin(A) / sin(C) = 6 × sin(75°) / sin(40°)`.

Dokumen belum menyatakan bahwa panjang sisi merupakan pembulatan. Nilai sumber tetap disimpan sebagaimana diberikan, tanpa mengganti 9 menjadi 9,0163 secara otomatis. Soal tetap ditahan sampai tim kurikulum memperbaiki nilai atau menjelaskan pembulatannya. Kunci B,D cocok dengan hitungan proporsi yang tertulis, tetapi itu belum membuat seluruh kondisi segitiga konsisten.

## Status setelah impor

- Empat soal memakai `source_review_status = REVISED_CURRICULUM`, `generator_status = NOT_IMPLEMENTED`, dan `generation_status = DEFERRED_CONCEPTUAL`.
- `DEFERRED_CONCEPTUAL` dipakai sebagai label penundaan yang sudah tersedia; pada tahap ini artinya generator belum dibuat, bukan penetapan bahwa semua soal tersebut konseptual.
- `mcma-15-2-8` memakai `source_review_status = REVISED_NEEDS_REVIEW`, `generator_status = NOT_IMPLEMENTED`, dan `generation_status = HOLD_SOURCE`.
- Bank 11–15 tetap mempunyai **223 generator dari 250 soal**. Total Drill tetap **664 generator**.
- Stok manual tetap **67 soal asli dengan 206 varian**. Lima soal revisi ini tidak mengubah stok yang sudah ada.

Pembuatan generator merupakan tahap berikutnya. Pada tahap impor ini, kelima soal dapat dibaca melalui bank lokal tetapi pembuatan variannya masih ditolak.

## Pemeriksaan

[Tes impor sumber](../../variant_gen/tests/test_drill_11_15_source_revision.py) memeriksa arsip dan penanda isi kedua dokumen, soal versi 2, kunci fungsi dan hubungan antarhimpunan, masalah geometri yang masih ditahan, penolakan pembuatan varian sebelum generator tersedia, serta stok manual yang tetap dapat dibaca.

```powershell
python -B -m unittest discover -s variant_gen/tests -p test_drill_11_15_source_revision.py -q
```

Hasil: **3 tes lulus**. Pemeriksaan sebelum impor memastikan 245 soal lain sama dengan kondisi sebelumnya. Pemeriksaan penanda isi sesudah impor memastikan pengaturan generator, stok manual, CSV dasar, katalog, dan sumber lama tetap sama.

Pemeriksaan gabungan indikator 11–15: **19 tes lulus**. Tes audit lama membaca isi sebelum revisi dari catatan revisi, sehingga audit historis tetap diperiksa terhadap versi sumbernya. Pemeriksaan seluruh `variant_gen/tests`: **152 tes lulus**; pemeriksaan terpisah indikator 6–10: **13 tes lulus**. Sebanyak **701 berkas** pengaturan generator, stok manual, serta sumber dasar tetap mempunyai penanda isi yang sama. Tautan lokal dokumentasi valid; `git diff --check` tidak menemukan masalah spasi.
