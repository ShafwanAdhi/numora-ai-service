# Revisi sumber indikator 20–23 — 7 Oktober 2026


> Catatan lanjutan 7 Oktober: fase impor pada laporan ini telah selesai. Seluruh16 revisi kini memiliki generator ACTIVE; lihat [audit implementasi](2026-10-07-revised-20-23-generator-audit.md). Pernyataan belum dibuat di bawah merekam kondisi saat impor.

Dokumen revisi tim kurikulum disalin ke [source-revision-2026-10-07.docx](../../variant_gen/data/drill-1-indicators-20-23/source-revision-2026-10-07.docx). SHA-256: 1edd91abfc4e9a2ad1143cc578d0df8da54becd711b8e0cdb1dc8dc1543608e9. Source lama dan CSV dasar dipertahankan.

Sebanyak16 original yang sebelumnya ditunda diperbarui menjadi versi2 melalui ledger original_revisions.jsonl; metadata menyimpan source baru, pembahasan, catatan transkripsi, serta source/status/alasan sebelumnya. Sebelas konflik sumber dan lima soal frekuensi relatif diperbaiki. Delapan belas soal ditunda lainnya serta stok manualnya dipertahankan.

**Generator belum dibuat:** seluruh16 original memakai generation_status DEFERRED_CONCEPTUAL sebagai status penundaan teknis, source_review_status REVISED_CURRICULUM dan generator_status NOT_IMPLEMENTED. Label DEFERRED_CONCEPTUAL tidak menyatakan soal numerik ini konseptual; reason menegaskan revisi diterima, generator menunggu. Jumlah generator tetap86/120 pada bank20–23.

| ID | Kunci v2 | Status pengerjaan |
|---|---|---|
| pg-20-3-3 | C | Menunggu generator |
| pg-21-2-2 | C | Menunggu generator |
| pg-21-3-1 | C | Menunggu generator |
| pg-21-3-4 | A | Menunggu generator |
| pg-21-3-5 | C | Menunggu generator |
| mcma-21-3-8 | A,C | Menunggu generator |
| kategori-21-3-9 | 1,2,4 | Menunggu generator |
| pg-22-1-1 | C | Menunggu generator |
| mcma-22-1-6 | A,B,D | Menunggu generator |
| mcma-22-1-7 | A,C | Menunggu generator |
| mcma-22-3-8 | A,C,D | Menunggu generator |
| pg-23-3-2 | B | Menunggu generator |
| pg-23-3-5 | C | Menunggu generator |
| mcma-23-3-7 | A,D | Menunggu generator |
| mcma-23-3-8 | A,C,D | Menunggu generator |
| kategori-23-3-9 | 1,2,4 | Menunggu generator |

Tiga keputusan transkripsi mengikuti koreksi final yang dinyatakan di dalam dokumen: pg-20-3-3 memakai100,105,110,115 dengan kunciC; pg-21-2-2 memakai65,68,70,75 dengan kunciC; mcma-21-3-8 memakai pernyataan2 Median data berubah menjadi70. Catatan/header lama yang bertentangan dipertahankan dalam source_text dan DOCX, bukan ditampilkan sebagai kunci final. Pembahasan terakhir soal MCMA tersebut diselaraskan dengan redaksi final tanpa mengubah kesimpulan matematika.

Verifikasi: **27 tes lulus**, yaitu dua tes impor sumber, sepuluh tes bank/generator20–23, dan15 tes HTTP. Perhitungan independen memeriksa seluruh opsi pada16 original revisi. Hash seluruh config, stok konseptual, snapshot, CSV dasar dan source lama tidak berubah. Ada file tes generator revisi yang sudah untracked sebelum tugas ini; file itu tetap utuh dan belum dijalankan sebagai bukti generator selesai.

Seluruh perubahan masih lokal; tidak ada generator baru, commit atau push pada tahap impor ini.
