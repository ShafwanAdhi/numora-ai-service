# Rencana generator Drill Paket1 indikator1–5

Scope pengguna: level1–3 saja; implementasi pertama indikator1–2. Rencana ini menggantikan usulan220 soal/all-level sebelumnya. Spec: [desain](../specs/2026-10-05-drill-1-5-generator-design.md). Eksekusi inline memakai superpowers:executing-plans; satu reviewer akhir.

1. Audit dan import60 original indikator1–2,6 grup; raw DOCX dan metadata provenance. Tandai konflik tanpa koreksi sumber. Catat semua skipped.
2. Generator indikator1 berbasis JSON existing. Reproduksi original, semua opsi diperiksa oracle independen,20 hasil unik per ACTIVE.
3. Generator indikator2 dengan kontrak sama. Operasi, akar sederhana, pangkat dan unit dihitung ulang dari teks. Tidak memperluas evaluator.
4. Registrasi bank ke CLI/UI; lifecycle local-store/HOLD/cache/history. Audit seed201–250, browser smoke, suite penuh, dokumentasi dan review read-only. Verifikasi hash semua data/config/store lama.

Indikator3–5:90 sumber level1–3, tahap berikutnya; belum import atau generator sekarang. Level4–5 di luar scope. Tidak menulis DB/Numora/.env/user store, tidak menambah dependency, tidak commit/push.

Ledger eksekusi: [progres](2026-10-05-drill-1-2-generator-progress.md).

Tahap indikator3–5 kini diimplementasikan; lihat [rencana lanjutan](2026-10-06-drill-3-5-generator.md) dan [progres](2026-10-06-drill-3-5-generator-progress.md). Catatan tahapberikut di atas adalah scope pada fase1–2.
