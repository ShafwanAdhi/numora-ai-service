# Revisi sumber indikator 16–19 — 7 Oktober 2026

**ENGINEERING DECISION — instruksi pengguna:** salin revisi Curriculum ke repo lokal dan perbarui original yang sebelumnya diskip; jangan membuat generator. Dokumen sumber adalah `revisi_banksoal_indikator16-19.docx`, disalin verbatim ke [arsip DOCX](../../variant_gen/data/drill-1-indicators-16-19/source-revision-2026-10-07.docx).

SHA-256 sumber dan salinan: `b18b5681976b79f780489f25b15a1ce6d48441101193f6ca6211987b0dd33a83`.

## Konteks dan cakupan

Aturan produk mengikuti PRD Numora v0.6 dan klarifikasi pemilik, bukan angka historis rancangan IRT atau sumber soal. Bank lokal Service AI terpisah dari database canonical Numora; komputasi IRT belum tersedia. Impor ini tidak membuat generator, konfigurasi, stok, publikasi, atau penulisan database.

Dokumen berisi 120 soal: indikator 16–19, masing-masing Level 1–3 dengan 10 soal per level. Header menyebut lima level, tetapi soal Level 4–5 tidak tersedia. Sepuluh soal yang tidak memiliki generator di bank dasar diperiksa terhadap dokumen. Dua mempunyai revisi eksplisit:

| ID | Versi | Kunci | Bagian sumber yang dipilih |
|---|---|---|---|
| `mcma-17-1-8` | 1 → 2 | A,C,D | “Revisi Soal 8”, setelah soal lama; kondisi faktor skala, pernyataan dilatasi, dan pembahasan revisi. |
| `kategori-17-2-10` | 1 → 2 | 1,2 | “Soal 10 (Hasil Revisi)”, bukan soal lama; kondisi faktor skala, pernyataan dilatasi, dan pembahasan revisi. |

Stem, opsi, kunci, dan pembahasan diimpor dari bagian revisi yang dipilih. Label A/B/C pada tabel kategori dinormalisasi menjadi ID 1/2/3 mengikuti format bank existing. Kunci tidak berubah. Dua revisi ditambahkan ke ledger `variant_gen/data/original_revisions.jsonl`, tanpa mengubah dua revisi lama yang telah ada. Metadata baru mencatat sumber, hash, teks sumber, pembahasan dan catatan transkripsi. Status `DEFERRED_CONCEPTUAL` / `NOT_IMPLEMENTED` menahan generasi.

Delapan original lain tetap karena substansi dan kuncinya sesuai sumber: `pg-16-1-1`, `pg-16-1-2`, `pg-16-3-2`, `pg-17-3-2`, `mcma-16-1-6`, `kategori-16-1-9`, `kategori-16-2-9`, dan `kategori-17-3-10`. Perbedaan format angka/kata, spasi, atau simbol derajat tidak membuat revisi akademik baru. Seluruh kutipan soal skip tersimpan pada [snapshot review sumber](../../variant_gen/data/drill-1-indicators-16-19/skipped-source-review.json); DOCX tetap menjadi sumber asli.

## Catatan transkripsi dan batas approval

- Stem revisi menyebut `k≠1` dan `k≠0`; pernyataan dilatasi menyebut `|k|≠1`. Keduanya disalin sebagaimana diberikan. **OPEN / review Curriculum:** penyelarasan cakupan `k=-1` antara stem dan pernyataan, jika dibutuhkan, harus menjadi revisi baru; importer tidak memperluas syarat sendiri.
- Pembahasan sumber `pg-17-3-2` memuat koordinat `(-,x-y)` yang tampak salah ketik. Kutipan sumber mempertahankannya; original/kunci existing tidak diubah atau diberi pembahasan baru dari teks tersebut.
- Revisi sumber tidak menyatakan kelulusan kesetaraan IRT, kesiapan publikasi, atau ketersediaan generator. Generator dan seluruh stok konseptual yang sudah ada tetap menggunakan versi/pin existing.

## Verifikasi

Hash arsip sama dengan file Downloads. Bank dimuat ulang: 120 original bank dasar dan 820 original workspace; versi, opsi, kunci, simbol matematika, provenance, dan penolakan generasi kedua ID terverifikasi. Dua baris ledger lama tetap identik byte demi byte. Perbandingan hash asset existing memastikan CSV dasar, konfigurasi, stok, dan data indikator 20–23 tidak berubah oleh impor ini. File lokal `test_drill_20_23_revisions.py` terpantau berubah di luar impor ini dan tidak ditimpa.

Suite existing lulus: `test_bank_coverage.py` (9), `test_catalog.py` (2), `test_conceptual_stock.py` (10), dan `test_webui.py` (15), total 36 tes. Snapshot memuat sepuluh soal skip. `git diff --check` untuk berkas tracked yang diubah oleh impor ini lulus.

Perubahan terbatas pada repo lokal; tidak ada commit, push, atau perubahan database.

## Aktivasi dua generator setelah persetujuan desain

**ENGINEERING DECISION — disetujui pengguna:** buat generator hanya untuk `mcma-17-1-8` dan `kategori-17-2-10`, memakai engine JSON existing. Instruksi awal menunda generator berlaku pada tahap impor di atas; pengguna kemudian meminta implementasi dan menyetujui desain variasi sifat transformasi.

Config v1 dipin ke hash original v2, tanpa mengubah ledger, CSV, maupun source DOCX. Metadata kedua ID diaktifkan (`ACTIVE` / `IMPLEMENTED`); provenance, teks sumber, pembahasan Curriculum dan catatan transkripsi tetap. `original_values` mereproduksi stem, semua opsi dan kunci original v2, termasuk redaksi simbolik sumber. Mode reproduksi hanya dipakai lint; generasi memilih mode varian.

Varian menggunakan faktor `{-4,-3,-2,-0.5,0.5,2,3,4}` dengan satu pernyataan salah. Klaim bentuk/ukuran diubah sesuai sifat transformasi, bukan sekadar mengacak opsi. Tugas tetap memilih sifat transformasi (MCMA) atau menilai benar/salah (Kategori); tidak menambahkan perhitungan koordinat. Delapan faktor dan empat/tiga posisi salah menghasilkan tepat 32/24 kandidat berbeda. Jumlah jawaban benar tetap 3/4 dan 2/3. Kunci serta pembahasan tiap pernyataan dihitung bersama klaim. Nilai `0`, `1`, dan `-1` ditolak; cakupan `k=-1` pada original sumber tetap sebagai catatan Curriculum, tidak diubah diam-diam.

Tes `test_transform_property_generators.py` mula-mula gagal karena kedua config belum ada, kemudian lulus setelah implementasi. Pemeriksaan mencakup seluruh 56 kombinasi, kebenaran klaim berdasarkan teks hasil render, jumlah jawaban benar, pernyataan pembahasan, reproduksi original, penolakan faktor tidak valid, determinisme 100 seed per ID, provenance record, dan penolakan kandidat duplikat setelah domain habis. Domain terbatas: seed berbeda tidak menjamin varian unik. Implementasi ini tidak menyatakan kelulusan kesetaraan IRT.

Verifikasi akhir: seluruh suite `python -B -m unittest discover -s variant_gen/tests -v` lulus (147 tes). CLI lint kedua ID lulus, masing-masing menghasilkan seluruh 32/24 kandidat unik di memori tanpa kegagalan. GET `/api/question` mengenali mode generator, dan POST `/api/generate` menghasilkan original-version 2/config-version 1 dengan konten yang sama pada pengulangan seed; integrasi lokal tidak mengakses database atau menulis store. Hash asset data/config yang sudah ada tidak berubah; dua config baru dan aktivasi metadata terbatas pada kedua ID yang disetujui.
