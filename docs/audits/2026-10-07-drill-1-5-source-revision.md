# Impor revisi original Drill Paket 1 indikator 1–5

7 Oktober 2026. Impor sumber lokal saja; generator tidak dibuat/diaktifkan, database tidak diakses, tidak commit/push.

## Sumber dan cakupan

Dokumen `C:/Users/shafw/Downloads/revisi_banksoal_indikator1-5.docx` diarsipkan utuh pada kedua bank:

- [Arsip indikator 1–2](../../variant_gen/data/drill-1-indicators-1-2/source-revision-2026-10-07.docx).
- [Arsip indikator 3–5](../../variant_gen/data/drill-1-indicators-3-5/source-revision-2026-10-07.docx).
- SHA-256: `c2f41c6800e990d6cbc96a07cb83d3abe1bd25e0ebe874f2be5f666beda2a3b1`.

Dokumen memuat 220 soal: indikator 1,2,4 memiliki level 1–5; indikator 3 level 1–4; indikator 5 level 1–3. Indikator 3 level 4 diberi catatan penyusun “BELUM DIBENERIN JANGAN DICOPY DULU”. Catatan tersebut diperlakukan sebagai informasi kesiapan sumber, bukan instruksi dari pengguna.

Cakupan tugas mengikuti daftar skip pada bank yang sudah ada: 52 ID level 1–3, terdiri dari 42 HOLD_SOURCE dan 10 original konseptual dengan stok manual. Sebanyak 70 soal di level tambahan disimpan dalam arsip DOCX; tidak ditambahkan ke katalog/bank pada tahap ini.

Hasil: **41 original v2** melalui ledger `original_revisions.jsonl` (17 pada bank 1–2, 24 pada bank 3–5). Satu soal tetap original v1 karena isinya belum berubah. Sebanyak **108 original lain tetap identik**, termasuk 98 generator aktif dan 10 soal konseptual; perbedaan konseptual hanya format rupiah/spasi. CSV dasar, katalog, sumber awal, semua config, serta stok manual dipertahankan.

## Original yang direvisi

Semua baris berikut belum mempunyai generator. Label runtime `DEFERRED_CONCEPTUAL` untuk 40 revisi yang diterima merupakan penundaan teknis, bukan penilaian bahwa soal tersebut konseptual.

| ID | Kunci sumber revisi | Status review |
|---|---|---|
| `pg-1-1-5` | A | Revisi diimpor; tanda suhu pembahasan diperbaiki. |
| `pg-1-2-1` | D | Tetap HOLD; konversi persentase pembahasan masih salah. |
| `pg-1-2-3` | B | Opsi kini memiliki satu jawaban benar. |
| `mcma-1-2-6` | A,C | Header sesuai evaluasi; label sumber berubah menjadi C4. |
| `pg-1-3-1` | B | Analisis II memuat urutan yang benar. |
| `pg-1-3-5` | D | Opsi kini memiliki satu jawaban benar. |
| `mcma-1-3-6` | A,C | Header sesuai evaluasi. |
| `pg-2-1-1` | B | Saldo awal Rp30.000; hasil Rp18.500. Catatan distraktor. |
| `pg-2-1-2` | B | Skor 49; opsi unik. |
| `pg-2-1-3` | C | Ukuran taman menghasilkan diagonal 6sqrt(3). |
| `pg-2-1-5` | A | Pembayaran Rp150.000; kembalian Rp42.000. Catatan distraktor. |
| `pg-2-2-1` | B | Header sesuai saldo Rp51.500. Catatan distraktor. |
| `pg-2-2-2` | A | Selisih 3sqrt(5); header diperbaiki. |
| `pg-2-2-4` | B | Langkah II; opsi unik. |
| `mcma-2-2-6` | A,B,D | Header sesuai eksponen/akar. |
| `mcma-2-2-7` | A,B | Klaim efisiensi diganti jumlah langkah yang terukur. |
| `mcma-2-3-6` | A,B,D | Header sesuai eksponen/akar. |
| `pg-3-1-2` | C | Mengukur sisi persegi, bukan diagonal; hasil 6,7 m. |
| `pg-3-1-3` | C | Dua tahap pembulatan eksplisit; hasil Rp81.000. Catatan distraktor. |
| `pg-3-1-5` | B | Pembulatan operand eksplisit; hasil Rp140.000. Catatan distraktor. |
| `pg-3-2-2` | C | Mengukur sisi persegi, bukan diagonal; hasil 7,2 m. |
| `pg-3-2-3` | C | Harga satuan dibulatkan; hasil Rp87.500. Catatan distraktor. |
| `pg-3-2-4` | B | Nilai riil dibulatkan 121,25, bukan 121,26. |
| `mcma-3-2-7` | A,B,D | Mengukur sisi ubin, bukan diagonal. |
| `mcma-3-2-8` | B,C | Jumlah minuman menjadi 8; komponen estimasi dibulatkan naik. Label kognitif diwarisi. |
| `kategori-3-2-9` | 1,3 | Klaim (b) menjadi 3 kg sehingga SALAH sesuai kunci. |
| `pg-3-3-3` | C | Kedua operand wajib dibulatkan ke atas. |
| `pg-4-1-1` | C | Header sesuai KPK 36 hari. |
| `mcma-4-1-8` | A,B,D | Jumlah kantong maksimum eksplisit. |
| `kategori-4-1-9` | 1,3 | Jumlah piring maksimum eksplisit. |
| `kategori-4-1-10` | 1,2 | Potongan pita terpanjang eksplisit. |
| `pg-4-2-2` | B | Isi kg bilangan bulat eksplisit. |
| `pg-4-2-5` | C | Header sesuai FPB 2^2×3^2. |
| `mcma-4-2-8` | B,C | Jumlah ruangan maksimum eksplisit. |
| `kategori-4-2-9` | 1,3 | Jumlah kardus maksimum eksplisit. |
| `kategori-4-2-10` | 1,2 | Potongan pita terpanjang eksplisit. |
| `pg-4-3-1` | C | Analisis tanggal unik; 1 Maret + 60 hari = 30 April. |
| `mcma-4-3-8` | B,C | Jumlah kelompok maksimum eksplisit. |
| `kategori-4-3-9` | 1,3 | Jumlah kotak maksimum eksplisit. |
| `kategori-4-3-10` | 1,2 | Potongan pita terpanjang eksplisit. |
| `pg-5-1-5` | B | Header sesuai volume 6 liter. |

## Konflik dan catatan sumber

- `pg-1-2-1`: kunci D benar untuk kerugian −0,62, tetapi pembahasan menulis **−58% = 0,58%**. Nilai yang benar −0,58. Revisi disimpan sebagai v2, tetap HOLD_SOURCE sampai pembahasan diperbaiki.
- `pg-5-3-3`: header tetap **B. 24 liter/menit**, sedangkan selisih `(480/20)−(300/15)=4` liter/menit pada opsi B dan pembahasan. 24 adalah debit selang Q. Isi original tidak berubah; tetap v1/HOLD_SOURCE, provenance review diperbarui.
- `mcma-3-2-8`: revisi tidak memuat `Level Kognitif`. Label bank C4 dipertahankan dari sumber awal dengan `cognitive_label_provenance=INHERITED_PREVIOUS_SOURCE`; label baru tidak disimpulkan dari posisi level.
- Enam soal mempunyai alasan distraktor yang belum konsisten meskipun solusi utama/kuncinya benar: `pg-2-1-1`, `pg-2-1-5`, `pg-2-2-1`, `pg-3-1-3`, `pg-3-1-5`, `pg-3-2-3`. Rincian tersimpan pada `source_review_notes`. Teks sumber tidak diperbaiki diam-diam; catatan ini perlu ditinjau sebelum membuat pembahasan generator.

## Status sesudah impor

| Bank | Original | ACTIVE | DEFERRED_CONCEPTUAL | HOLD_SOURCE |
|---|---:|---:|---:|---:|
| Indikator 1–2 | 60 | 34 | 25 | 1 |
| Indikator 3–5 | 90 | 64 | 25 | 1 |
| Total | 150 | 98 | 50 | 2 |

Jumlah generator tidak bertambah. Ledger menyimpan original/replacement lengkap, metadata sebelum/sesudah, versi, alasan, nama arsip, dan SHA-256. Transkripsi mempertahankan pecahan, akar, tabel, serta pengelompokan pangkat OMML. Katalog tetap Paket 1 > indikator > level 1–3 > soal.

Tes impor: `python -B -m unittest discover -s variant_gen/tests -p test_drill_1_5_source_revisions.py -v` — dua tes lulus. Impor diuji dahulu pada bank sementara; 108 original tidak direvisi dibandingkan dengan kondisi sebelum impor.

Verifikasi lengkap: `python -B -m unittest discover -s variant_gen/tests -v` — 160 tes lulus (86,513 detik). Ekspektasi status lama pada tes indikator 5 diperbarui untuk `pg-5-1-5`; pemeriksaan ketiadaan config tetap berlaku. Snapshot SHA-256 mencakup 721 berkas lama: 719 tetap identik, hanya dua metadata bank yang berubah sesuai cakupan. `git diff --check` lulus.
