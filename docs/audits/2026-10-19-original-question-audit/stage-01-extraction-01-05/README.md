# Tahap 1 — Validasi ekstraksi indikator 1–5

**Cakupan disetujui:** struktur ekstraksi saja. Audit akademik dan pencocokan generator menunggu instruksi terpisah. Artefak audit lain di direktori induk masih hasil sementara, bukan laporan final.

Arsip: `docs/sources/incoming/2026-10-19-indikator-1-5/source.docx`  
SHA-256: `0e868995fdeb3fe035b625c3bb8252424a2be7dea4dfe48413af79ede18f1147`

| Pemeriksaan | Hasil |
|---|---:|
| Entri / posisi unik | 250 / 250 |
| Cakupan | 5 indikator × 5 level × 10 soal |
| PG / MCMA / Kategori | 125 / 75 / 50 |
| Paragraf dibandingkan dengan XML Word | 10.092 |
| Tabel diperiksa, termasuk span dan merge | 55 (53 dalam soal, 2 pengantar) |
| Persamaan OMML dibandingkan dengan XML arsip | 4.019 |
| Gambar tertanam | 0 |
| Struktur dapat dipisahkan / perlu review batas versi | 248 / 2 |

Seluruh teks paragraf cocok dengan proyeksi XML Word menggunakan representasi LaTeX intake; seluruh XML OMML tersimpan cocok dengan arsip. Penomoran otomatis dipulihkan dari numbering/styles Word dan disimpan bersama lokasi paragraf; teks intake asli tetap dipertahankan. Tabel, label kategori, dan posisi sumber tidak diratakan atau dihapus dari bukti JSON. Tidak ada posisi soal yang hilang atau berulang pada kelompok ini.

**Dua batas versi belum dapat diputuskan:**

- I1 level 5 soal 2: beberapa definisi `a` dan dua rangkaian evaluasi bercampur dalam satu entri (termasuk catatan `eh wait`). Semua teks dipertahankan, tidak dipilih versi akhir.
- I3 level 5 soal 7: dua rangkaian A–D serta kunci tambahan bercampur. Delapan teks opsi tersimpan sebagai bukti dua rangkaian, bukan dianggap satu soal delapan opsi yang siap digunakan.

**Catatan pemisahan sumber:** I1 level 2 soal 1 memuat catatan koreksi opsi dalam pembahasan; I2 level 4 soal 9 memuat catatan koreksi kunci; I4 level 4 soal 5 memuat deskripsi panjang setelah huruf kunci. Teks-teks tersebut dipertahankan pada bagiannya dan perlu dinilai pada audit akademik. Belum ada keputusan kebenaran kunci atau pembahasan.

Pemeriksaan ini membuktikan kesetiaan struktur/teks, bukan kebenaran matematika atau ketepatan tampilan visual setiap persamaan. Label `STRUCTURE_VERIFIED` tidak berarti soal valid secara akademik.

Keluaran: [CSV 250 entri](entries.csv), [JSON komponen dan bukti](validation.json). Reproduksi: `python variant_gen/tests/validate_intake_01_05.py`.

Seluruh 859 berkas sumber/bank/config/stok/layanan yang dibekukan tetap memiliki hash yang sama; tidak ada perubahan runtime. **Tahap berikutnya belum dikerjakan dalam bagian ini.**
