# Penggantian bank Drill database — 22 Oktober 2026

**ENGINEERING DECISION — instruksi pemilik:** hapus bank Drill lama, ganti dengan original efektif di repo lokal, terbitkan agar tersedia pada Drill and Practice. Operasi telah di-commit ke database yang dikonfigurasi bersama oleh `.env` Numora dan Numora-ai-service. Tidak ada commit/push Git atau deployment aplikasi.

| Data | Sebelum | Sesudah |
|---|---:|---:|
| Keluarga original Drill | 120 | 1.150 |
| Versi konten Drill, termasuk versi historis | 240 | 1.150 |
| Paket Drill PUBLISHED | 12 | 115 |
| Jalur indikator Drill | 4 | 23 |
| Level berisi paket Drill | 12 | 115 |
| Varian hasil generator yang diimpor | 0 | 0 |

Setiap indikator 1–23 mempunyai 5 level, masing-masing 10 original. Format: 575 PG, 345 MCMA, 230 Kategori. Semua keluarga/versi baru READY dan CONTENT_VALID, paket PUBLISHED, non-demo, REGULAR. Termasuk 83 original konseptual; stok editorial dan hasil generator tidak diimpor.

Sumber: `load_workspace_bank(variant_gen/data/q0_bank.csv)`, seluruh subbank terdaftar, serta `original_revisions.jsonl`. Impor memakai revisi efektif terbaru, termasuk 16 revisi HOLD yang telah diselesaikan. ID lokal, hash original, nomor versi, klasifikasi, kunci dan provenance disimpan melalui namespace `NUMORA_AI_DRILL_1`.

Pembahasan: 1.032 dari metadata lokal, 110 direproduksi pada nilai original konfigurasi tanpa pengacakan, 7 dari transkripsi sumber lokal impor sebelumnya, 1 koreksi pembahasan `pg-17-3-2` yang sudah diterima sebelumnya. Isi soal, opsi, kunci, label kategori dan pembahasan database dicocokkan dengan payload sumber.

## Publikasi dan struktur siswa

23 subbab operasional `SC-DRILL-IND-001` sampai `SC-DRILL-IND-023` dipetakan ke empat bab yang sudah ada. Setiap subbab memiliki lima level READY. Kompetensi indikator dipetakan ke jalur baru; subbab/level lama tetap tersimpan untuk referensi, berstatus DRAFT agar jalur Drill kosong tidak ditampilkan.

Penerimaan operasional menggunakan izin pemilik, difficulty `OWNER_ACCEPTED_UNCALIBRATED`. Bukan klaim persetujuan kurikulum atau kalibrasi IRT. Kebijakan khusus yang telah didukung runtime Numora, `DRILL_CH3_OWNER_ACCEPTED_2026_10_07` versi 1, digunakan kembali setelah paket/riwayat lama terkait dihapus. Allowlist-nya diganti dengan 115 UUID paket baru; konfigurasi dan audit mencatat instruksi penggantian/publikasi tanggal 22 Oktober. Rubrik yang sudah disegel digunakan kembali bila bentuk dan jumlah keputusan sama.

PG memakai benar/salah; MCMA memakai proporsi keputusan memilih/tidak memilih yang benar; Kategori memakai proporsi pernyataan yang dikategorikan benar. Level 1 terbuka, level berikutnya mengikuti mastery 80%. Tidak ada pembukaan semua level secara massal bagi pengguna.

## Dampak penghapusan

| Data terkait bank lama yang dihapus | Jumlah |
|---|---:|
| Attempt Drill | 4 |
| Item attempt / jawaban Drill | 40 / 30 |
| Catatan XP Drill | 3 |
| Progress level terkait | 3 |
| Paket PvP yang memakai versi soal lama | 11 |
| Match PvP terkait | 11 |
| Item match / pemain / jawaban PvP | 110 / 19 / 16 |
| Manifest / item pengiriman / exposure | 39 / 102 / 102 |
| Event analytics / outbox terkait | 105 / 105 |

Paket PvP lama tidak diterbitkan ulang oleh operasi ini; bank PvP perlu disiapkan kembali sebelum fitur tersebut memakai paket baru. Snapshot leaderboard historis yang telah tersimpan dipertahankan; ledger XP Drill terkait dihapus bersama attempt-nya. Audit dan laporan impor lama dipertahankan sebagai jejak operasi.

300 keluarga soal Tryout, 13 paket Tryout (7 PUBLISHED, 6 DRAFT), 5 attempt Tryout GRADED, jawaban, hasil dan XP yang tidak terkait reset dipertahankan. Hash setiap baris di luar cakupan penghapusan tetap sama, dengan pengecualian perubahan master pembelajaran dan kebijakan yang dijelaskan di atas.

## Backup dan batas operasi

Backup data lokal: `.scratch/drill-reset-backup-20261022-154036/`. Berisi 116 tabel, 5.808 baris sebelum reset, binary COPY terkompresi, SHA-256, manifest kolom, constraint, trigger dan fungsi. Pemulihan setiap tabel ke clone sementara diuji: jumlah baris dan hash binary hasil salinan kembali identik. Pengujian ini memverifikasi pemulihan data per tabel pada skema saat ini, bukan instalasi database baru dari nol. Backup mengandung data pengguna; tetap lokal dan diabaikan Git.

Penghapusan dan pengisian dilakukan dalam satu transaksi, didahului simulasi rollback dan pemeriksaan kecocokan backup. Tabel terdampak dikunci. Hanya trigger pengguna pada tabel terdampak yang dinonaktifkan sementara untuk reset yang diizinkan; foreign key tetap aktif. Seluruh status trigger dipulihkan sebelum commit; tidak ada perubahan skema permanen.

Manifest payload: `5e16fcf3f092ece921373624c633ded8d06bb060baa3ca1204fe816900972c0e`.

## Verifikasi

- Validasi kontrak impor dan decoder runtime: 1.150 soal.
- Pencocokan isi, kunci, versi, hash, urutan, indikator dan level sesudah commit: 1.150 soal.
- Kelayakan distribusi dan allowlist kebijakan: 115 paket.
- Pengujian penilaian runtime dari konten database: 1.150 jawaban sempurna, 1.150 jawaban kosong, 575 jawaban parsial MCMA/Kategori.
- Pengujian layanan siswa: 8 paket/80 soal, mencakup empat bab serta level 1–5 pada indikator 1. Katalog menampilkan 23 indikator/115 level; level 2 awalnya ditolak sebagai LEVEL_LOCKED. Sepuluh penyimpanan jawaban pertama melewati layanan `saveAnswer`; 70 jawaban lainnya diisi sebagai fixture langsung di transaksi pengujian. Seluruh start/submit memakai layanan Numora sebenarnya; penilaian parsial, penjelasan, XP, tujuh unlock berikutnya, submit ulang tanpa XP ganda, pengulangan pool yang sama dan penolakan peran Teacher lulus. Semua fixture, exposure, event dan XP uji di-rollback; jumlah baris operasional kembali sama.

Skrip operator lokal dalam `.scratch/`: `prepare_drill_reset.py`, `validate_drill_reset.cjs`, `drill_reset_scope.py`, `backup_drill_database.py`, `reset_drill_database.py`, `audit_drill_database_runtime.cjs`, `check_drill_reset_student.cjs`. Hasil apply, inventaris dan pengujian tersimpan di direktori yang sama. Jangan menjalankan ulang `--apply` pada bank yang sudah diganti; identitas deterministik dan pemeriksaan backup sengaja menggagalkan pengulangan.

Verifikasi layanan memakai kode Numora lokal dan database terkonfigurasi. Login/browser siswa dan deployment VPS tidak diuji oleh operasi ini.
