# Impor original Drill Paket 1 Bab 3 ke database Numora

> **STATUS TERBARU — 7 Oktober 2026:** pemilik proyek kemudian meminta penerimaan langsung **khusus sekali ini**. Semua 12 paket kini PUBLISHED, menunjuk 120 versi accepted READY baru; DRAFT di bawah adalah histori impor awal. Policy khusus berisi allowlist UUID paket; MCMA/Kategori dapat dikerjakan Student. Indikator 19 kini memakai subbab Volume Bangun Ruang tersendiri. Pembahasan accepted `pg-17-3-2` dikoreksi. [Keputusan, scope dan verifikasi Student](https://github.com/ayiinee/Numora/blob/fix/drill-chapter3-owner-acceptance/docs/development/DRILL_CHAPTER3_OWNER_EXCEPTION.md). Pemeriksaan seluruh 12 paket/120 soal, parsial, XP, unlock dan submit ulang lulus; data uji di-rollback.

**ENGINEERING DECISION — instruksi pengguna, 7 Oktober 2026:** impor dahulu soal lokal indikator 16–19; laporkan kendala runtime. Tidak memperluas integrasi runtime atau menerbitkan paket.

Impor sudah committed pada database yang dikonfigurasi oleh `.env` Numora. Koneksi AI dan Numora menunjuk target yang sama. Hasil: **120 keluarga soal ORIGINAL berklasifikasi DRILL, 120 versi database, 12 paket DRAFT, 120 package items**. Komposisi: 60 PG, 36 MCMA, 24 Kategori. Tidak ada varian atau stok konseptual yang diimpor.

Namespace stabil: `NUMORA_AI_DRILL_1`. Kode keluarga paket: `DRILL_1_IND_<indikator>_L<level>`, versi paket 1. ID lokal menjadi `content_import_identities.external_id`; ID database tetap UUID. Versi original lokal dan hash disimpan dalam provenance, terpisah dari nomor versi database. Sebanyak 116 original memakai versi sumber 1, empat memakai versi sumber 2.

## Sumber dan pembahasan

Original efektif dibaca lewat `OriginalBank` dari `variant_gen/data/q0_bank.csv`, katalog, metadata, dan `original_revisions.jsonl`. Stem, opsi/pernyataan dan kunci dipertahankan. Empat revisi ikut dipin: `pg-16-3-5`, `mcma-17-1-8`, `kategori-17-2-10`, `mcma-19-3-6`; alasan/provenance revisi disimpan.

CSV tidak memuat pembahasan lengkap. Dua pembahasan memakai metadata revisi Curriculum; 110 memakai template config existing yang diisi **original_values**, tanpa sampling seed atau shuffle; delapan ditranskripsi dari pembahasan dokumen sumber. Kunci hasil reproduksi config diperiksa sama dengan original. Asal pembahasan tercatat pada `provenance.explanationOrigin`. Seluruhnya masih DRAFT, memerlukan review; hasil ini bukan pengesahan akademik atau kesetaraan IRT.

Dokumen pembahasan: `Blueprint Draft Soal Drill (1).docx`, SHA-256 `e09aaca5b84c331a5711afce7f0ce498be46530a6a59d2bbf4f21f4d605e18b6`. Konten bank lokal berupa teks; media DOCX tidak diunggah. Transkripsi matematika memakai struktur pecahan, pangkat dan akar OMML. Pembahasan sumber `pg-17-3-2` masih memiliki salah ketik koordinat yang telah dicatat dalam [audit sumber](2026-10-07-drill-16-19-source-revision.md); perlu review sebelum publikasi. Dua koreksi lokal lama serta cakupan faktor skala pada revisi indikator 17 juga mempertahankan status perlu review dari audit tersebut.

## Paket tersimpan

Setiap baris berisi 10 soal dengan urutan lokal 1–10. Level 4–5 tidak dibuatkan paket karena katalog lokal masih kosong.

| Indikator | Subbab Numora | Level | UUID paket |
|---|---|---:|---|
| 16 | SC-OG | 1 | 694a48b4-03de-4254-a443-210c196d3528 |
| 16 | SC-OG | 2 | fa2d8843-62da-48a0-815e-ddb80d1534e5 |
| 16 | SC-OG | 3 | bc4f2a8e-3670-4a9e-a321-cc9435a9b0fd |
| 17 | SC-TG | 1 | 8c3cb363-8d68-4044-8550-c2de2e9f28fe |
| 17 | SC-TG | 2 | 12aafccb-52b2-4d03-9ac0-06dd100da5a8 |
| 17 | SC-TG | 3 | a656f8e9-1910-468d-84fb-6798bca2398a |
| 18 | SC-PENG | 1 | 0853cc60-3f65-4030-8dc5-a199d8219126 |
| 18 | SC-PENG | 2 | a02d4872-2a1a-46e5-80b5-e45220593f9b |
| 18 | SC-PENG | 3 | ba6765c5-d62a-48b4-b73a-078276ed83f0 |
| 19 | SC-PENG | 1 | 7f3a2052-6b81-40f9-ad6e-8f750f0093e9 |
| 19 | SC-PENG | 2 | 5e8be7e3-7b46-40a4-80bd-8c78cf70cf18 |
| 19 | SC-PENG | 3 | 7bb671ae-c46f-43fc-b227-df32b2b15000 |

## Jalur baca dan verifikasi

Impor menggunakan `ContentPackagesService.create` dan `ContentImportService.import` Numora, dalam satu transaksi luar untuk seluruh 12 paket. Audit dan provenance bawaan service ikut tersimpan. Tidak ada perubahan schema, taxonomy, status review, kebijakan penilaian atau histori existing.

Simulasi 120 soal dibatalkan sebelum apply. Pengulangan setiap request diuji mengembalikan report identik tanpa versi ganda. Apply memeriksa seluruh 12 paket dengan `ContentPackagesService.detail`: masing-masing 10 soal, `canSaveDraft=true`, `canPublish=false`. Fingerprint seluruh row existing pada tabel konten/kurikulum/paket/impor diperiksa tetap sama.

Verifikasi setelah commit membandingkan seluruh 120 stem, opsi, kunci, pembahasan, hash/versi original, urutan dan UUID terhadap payload impor. `ContentPackagesService.list` menemukan seluruh 12 paket. Preview nyata melalui `ContentPreviewService` memuat 10 soal, menyimpan jawaban PG/MCMA/Kategori, submit dan membaca kunci/pembahasan; skor tetap null. Transaksi sesi uji dibatalkan sehingga tidak meninggalkan sesi preview.

Build database dan API lulus. Tidak ada perubahan kode generator. Verifikasi ini menguji service dan persistence; tidak mengklaim pengujian browser atau sesi Student.

Flag lokal `Numora/.env`: `CONTENT_IMPORT_PREVIEW_ENABLED=true`. Restart API yang sudah berjalan agar membaca flag. Admin dengan kemampuan content dapat membuka `/admin/content/imports`, memilih Drill lalu paket terkait. Endpoint baca: `GET /api/v1/admin/content/packages?usageType=DRILL` dan `GET /api/v1/admin/content/packages/:id`.

## Kendala runtime yang tersisa

- Semua konten masih DRAFT, difficulty belum ditentukan, review Admin/Curriculum belum dicatat. Master kompetensi/level terkait juga masih DRAFT.
- Checklist service mengembalikan blocker `REVIEW`, `BLUEPRINT`, `RUNTIME`, `PUBLICATION`. Publikasi versi impor masih diproteksi.
- Runtime Drill masih menolak MCMA/Kategori dengan `PGK_SCORING_PENDING`. Rubrik Tryout yang tersedia tidak otomatis menjadi rubrik Drill.
- Progress dan paket aktif Drill memakai subbab/level. Indikator 18–19 sama-sama berada di `SC-PENG`; constraint MVP mengizinkan satu paket reguler non-demo terbit per level. Pemisahan DRAFT per indikator tidak mengubah model progress. Komposisi blueprint atau perubahan model perlu diputuskan sebelum publikasi; indikator 16 juga berada dalam subbab yang mencakup indikator 14–15.
- Sumber lokal level 4–5 belum berisi soal. Impor ini tidak mengisi konten yang belum tersedia.

Pemeriksaan lokal yang dapat diulang tanpa meninggalkan data uji:

```powershell
node --env-file=../Numora/.env .scratch/import_chapter3.cjs --verify
```

Skrip operasi dan mapping lengkap 120 UUID berada pada `.scratch/`, diabaikan Git. Identitas canonical tetap tersimpan di database, dapat dibaca kembali melalui tabel impor/service Numora.
