# Impor revisi original Drill Paket 1 indikator 6–10

7 Oktober 2026. Tahap ini hanya menerima sumber revisi; tidak membuat atau mengaktifkan generator, mengakses database, commit, atau push.

## Sumber dan cakupan

- Arsip: [source-revision-2026-10-07.docx](../../variant_gen/data/drill-1-indicators-6-10/source-revision-2026-10-07.docx).
- SHA-256: `db7bfd87fb1649b4ad63090a32ae225af14ac888fa26b384bb192a4d9cfa3c69`.
- Dokumen memuat 150 soal, indikator 6–10, level 1–3. Level 4–5 belum tercantum meskipun header menyebut lima level.
- Seluruh 21 ID dalam daftar skip dibandingkan. Dua belas original yang sebelumnya HOLD diperbarui menjadi v2 melalui `original_revisions.jsonl`; CSV dan dokumen awal dipertahankan.
- Sebanyak 138 original lain tetap identik. Perbedaan pada tiga soal konseptual hanya format rupiah/spasi; stok manual tidak diubah.

## Original yang diperbarui

| ID | Kunci revisi | Hasil review |
|---|---|---|
| `pg-6-1-5` | C | Kunci tersedia; kebutuhan bensin 4,5 liter. |
| `mcma-6-3-7` | A,B,C dari sumber | Tetap HOLD_SOURCE; konflik waktu dan hitungan belum selesai. |
| `pg-7-1-2` | B | Kunci tersedia; harga Rp35.000. |
| `pg-7-1-3` | C | Kunci sesuai luas 80. |
| `pg-7-2-4` | C | Opsi diperbaiki menjadi a ≠ −4. |
| `pg-7-3-5` | C | Opsi unik; kontradiksi k ≠ 4. |
| `mcma-8-2-8` | A,B,C,D | Langkah salah kini tunggal; solusi x > −13/7. |
| `pg-9-1-3` | C | Opsi unik; tanpa solusi k ≠ 8. |
| `pg-9-1-5` | A | Kriteria metode langsung tanpa menulis ulang persamaan diperjelas. |
| `pg-9-2-5` | B | Kriteria metode diperjelas. |
| `pg-9-3-2` | A | Nomor 2 dan tingkat C3 eksplisit; invers matriks sesuai. |
| `pg-9-3-4` | A | Kriteria metode diperjelas. |

Sebelas revisi diterima memakai `source_review_status=REVISED_CURRICULUM`, `generator_status=NOT_IMPLEMENTED`. Label runtime lama `DEFERRED_CONCEPTUAL` digunakan sebagai penundaan teknis, bukan penggolongan soal sebagai konseptual. Jumlah generator numerik tetap 129; metadata mencatat 129 ACTIVE, 20 DEFERRED_CONCEPTUAL, 1 HOLD_SOURCE.

## Konflik yang tersisa

`mcma-6-3-7`: pernyataan C menyebut persediaan cukup **5 hari**. Pada awal hari ke-3, dua hari penuh berlalu: `(60−6×2)/8 = 6` hari. Setelah tiga hari penuh: `(60−6×3)/8 = 5,25` hari. Pembahasan sumber mencampur kedua waktu, menulis `42/8 = 5`, serta masih memuat “wait”. Kunci A,B,C disalin sebagai klaim sumber, belum disahkan. Tidak dilakukan koreksi diam-diam.

## Pemeriksaan

Loader mendukung revisi kunci PG historis yang kosong dengan tetap memeriksa provenance, versi, dan kunci replacement. Tes mencakup arsip, 12 original v2, kunci revisi, metadata, tidak adanya konfigurasi generator baru, serta penolakan provenance yang diubah. Pengujian sumber lama disesuaikan dengan original efektif v2.

- `python -B -m unittest discover -s variant_gen/tests -p 'test_drill_6_10*.py' -v`: 15 tes lulus.
- Suite lengkap: 152 tes dijalankan; lima kegagalan subtest di `test_drill_11_15.test_saved_audit_matches_configs_and_replays_math`. Audit lama masih mencatat hash sebelum revisi untuk `mcma-11-1-7`, `pg-11-2-4`, `kategori-11-3-9`, `mcma-15-2-8`, dan `pg-15-4-2`. File bank/audit 11–15 tidak diubah dalam tugas ini.
- `git diff --check` untuk file terlacak yang disentuh tugas ini: lulus.
