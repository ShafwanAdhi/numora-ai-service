# Audit dan impor Pretest Bab 1–4

Tanggal: 2026-10-28. **80 original, 4 paket, 35 gambar sumber; tanpa generator.**

ENGINEERING DECISION — instruksi pemilik: audit seluruh pretest lalu masukkan database. Impor DRAFT tidak berarti publikasi/persetujuan Curriculum. Sumber dan kunci dipertahankan; usulan koreksi terpisah.

Hasil: {'DRAFT_AUDITED': 66, 'DRAFT_WITH_CLARIFICATION': 12, 'HOLD_FOR_ACADEMIC_REVIEW': 2}. Dua temuan utama: Bab 3 soal 5 (kunci SSA), Bab 4 soal 8 (inferensi penyebaran dari jangkauan). Lihat laporan per bab, audit.csv dan audit.json untuk bukti seluruh opsi/pernyataan.

Keempat rekap kunci lampiran cocok dengan kunci pada soal. Komposisi tiap bab: 10 PG, 6 MCMA, 4 Kategori; C3=5, C4=10, C5=5. Semua 35 gambar ditinjau langsung: label dan konteks cocok, tidak ada temuan angka/diagram yang mengubah jawaban. Proporsi ilustrasi tidak dipakai sebagai data ukur.

Pemetaan menggunakan master indikator existing; kode sumber seperti 15.3 disimpan utuh sebagai provenance. Akhiran bukan otomatis level Drill. sourceLevelNumber dan levelId kosong. Difficulty EASY/MEDIUM/HARD hanya mengikuti label Mudah/Sedang/Sulit dalam DOCX, bukan kalibrasi IRT.

Batas audit: pemeriksaan akademik oleh agen beserta bukti per entri, bukan pengesahan tim Curriculum atau validasi psikometrik. Asumsi dadu adil, produktivitas seragam, bahasa estimasi dan rubrik tidak dilengkapi diam-diam. Status DB/R2 dicatat pada hasil operator setelah operasi; keberadaan input ini belum membuktikan impor.

## Hasil database dan R2

**COMMITTED_AND_VERIFIED ? 28 Oktober 2026.** Database development sistem sudah berisi empat paket PRETEST DRAFT, masing-masing 20 original. Seluruh 35 gambar mempunyai receipt R2 VERIFIED; signed GET diunduh dan hash byte diperiksa ulang. Tidak ada publikasi, aktivasi siswa, generator, varian tambahan, atau koreksi sumber.

| Bab | Paket UUID | Original | Tanpa temuan material | Catatan | Review akademik |
|---|---|---:|---:|---:|---:|
| 1 | `ba11cea2-929d-4c1d-98ad-8703dfd16262` | 20 | 19 | 1 | 0 |
| 2 | `6b51c9fa-ed80-41cf-931a-05e9a5e6f4bd` | 20 | 17 | 3 | 0 |
| 3 | `8589e53d-444b-4f67-b163-71bd24c69037` | 20 | 18 | 1 | 1 |
| 4 | `9219f548-09cd-4e77-adbd-7fb7931a22bb` | 20 | 12 | 7 | 1 |

`database-dry-run-result.json` membuktikan rollback tanpa tambahan soal/paket. `database-apply-result.json` dan `database-verify-result.json` menunjukkan 80 versi original serta pembacaan ulang setelah commit; jumlah semua tabel yang dipantau tidak berubah saat verifikasi/idempotent replay. Kunci, urutan, opsi/pernyataan, pembahasan, provenance audit, dan manifest gambar diperiksa terhadap input. Fingerprint baris existing pada tabel yang dipantau tetap sama, termasuk attempt, jawaban dan ledger XP.

Tabel internal `question_variants` memang menyimpan satu baris `kind=ORIGINAL` per soal; ini tidak berarti dibuat varian hasil generator. PG memakai pin rubric single-choice existing dari trigger database; MCMA/Kategori tetap tanpa rubric baru. Tidak ada perubahan formula scoring.

## Cara memeriksa ulang

Di repo AI-service: `python tools/prepare_pretest_import.test.py`. Di repo utama: `node --test apps/api/scripts/import-local-pretest.test.cjs`, lalu `node --env-file=.env apps/api/scripts/import-local-pretest.cjs --verify`. Operator menolak target selain development yang dipin, input/hash sumber berubah, status terbit, atau receipt tidak cocok. `taxonomy-snapshot.json` membekukan pemetaan master saat preflight.

## Batas sebelum publikasi

Bab 3 soal 5 dan Bab 4 soal 8 tetap memakai kunci sumber pada DRAFT, disertai `HOLD_FOR_ACADEMIC_REVIEW`. Usulan koreksi belum diterapkan. Label audit HOLD adalah provenance dan belum menjadi aturan blok publikasi tersendiri; perbaiki serta setujui versi konten sebelum ada pekerjaan publikasi. Dua belas catatan asumsi/redaksi lainnya tercatat per entri, termasuk vektor Bab 3 soal 8. Tidak ada persetujuan Curriculum yang dicatat oleh operator.

## Verifikasi teknis

Tiga tes konversi, empat tes operator, 18 tes unit backend, typecheck/build API, serta lint/format berkas yang berubah lulus. Sebanyak 19 tes integrasi opsional tidak dijalankan karena TEST_DATABASE_URL tidak tersedia; pengujian transaksi pada target memakai dry-run rollback terkontrol, disusul commit dan verifikasi nyata. Semua 970 ekspresi matematika berhasil dirender. Snapshot 1.207 berkas runtime/bank/config dan 91 berkas sumber tetap cocok. Lihat `verification.json`, `math-render-check.json`, `independent-review.json`, dan `transport-normalization-review.json`. Status STAGED_ONLY pada arsip incoming adalah status historis saat intake; hasil impor terkini berada dalam direktori audit ini.
