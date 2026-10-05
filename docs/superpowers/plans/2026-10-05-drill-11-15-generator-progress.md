# Hasil implementasi generator Drill 11–15

Rujukan: [rencana](2026-10-05-drill-11-15-generator.md) dan
[laporan audit](../../audits/2026-10-05-drill-11-15-generator-audit.md).

Implementasi dilanjutkan pada worktree `feat/drill-11-15`; pekerjaan penulis
sebelumnya dipertahankan. Seluruh 223 soal berstatus ACTIVE memiliki config
dan lolos reproduksi original serta validasi matematika. Bank berisi 250
original; 5 HOLD_SOURCE dan 22 DEFERRED_CONCEPTUAL tetap dijaga dari generasi.

| Tahap | Hasil |
|---|---|
| 1 — bank/catalog/metadata | 250 original; 25 kelompok, 10 soal per kelompok; sumber tidak diubah |
| 2 — indikator 11 | 41 generator aktif, reproduksi dan oracle lulus |
| 3 — indikator 12 | 48 generator aktif, reproduksi dan oracle lulus |
| 4 — indikator 13 | 50 generator aktif, reproduksi dan oracle lulus |
| 5 — indikator 14 | 40 generator aktif, termasuk pemeriksaan sudut batas |
| 6 — indikator 15 | 44 generator aktif, termasuk rasio dan syarat kekongruenan |
| 7 — CLI/UI/lifecycle | Generate, regenerate, history, save config, stale hash dan guard diuji dengan data sementara |
| 8 — audit/review/handoff | Oracle independen, audit hash/seed, contoh hasil, review dan dokumentasi tersedia |

Verifikasi terakhir: `python -B -m unittest discover -s variant_gen/tests -v`
meluluskan **83 tes** dalam 78,147 detik. Tes dapat diulang dengan perintah di atas. `git diff --check` keluar dengan kode 0.
Sampling target 20 variant unik, batas 200 seed: 217 PASS, 6 SHORT,
0 FAIL, 27 SKIP. Audit seluruh seed berhasil diputar ulang dengan config
dan oracle terakhir; hash config cocok. SHORT tidak menyatakan seluruh
domain telah habis.

Review independen menemukan empat masalah penting pada klaim/aritmetika
opsi dan dua masalah tambahan pada dimensi manusia/pembahasan geometri.
Semuanya diperbaiki dan diuji ulang. Oracle diperluas untuk memeriksa
langkah pembagian, jumlah potongan, konstanta rasio, dan pembanding negatif.
Pembahasan seluruh bank belum diaudit sebagai materi ajar; validasi ini
tidak menetapkan tingkat kesulitan atau parameter IRT.

Implementasi dari worktree telah diintegrasikan ke checkout aktif bersama pekerjaan 6–10. Config JSON yang telah diverifikasi tersedia di `variant_gen/configs/`; CLI/UI memakai engine bersama. Script authoring dan log lokal worktree adalah artefak sesi yang tidak dibutuhkan untuk menjalankan checkout dari Git. Untuk mengubah config, buat versi berikutnya melalui editor atau workflow pada [referensi generator](../../GENERATOR.md).

Integrasi interface: 377 file bank/config/store yang sudah ada diperiksa berdasarkan SHA-256 dan dipertahankan. Loader checkout aktif kini berisi 670 original dan 575 config, termasuk seluruh indikator 6–23. Tes HTTP indikator 11–15 ditambahkan tanpa mengganti tes 6–10. Review integrasi menemukan kesalahan indentasi tes yang kemudian diperbaiki.

Verifikasi setelah integrasi: 97 tes lolos (62,321 detik); server interface direstart pada localhost:8765. API live memuat 25 kelompok indikator 11–15 dan 250 original. Browser menampilkan pilihan indikator 6–23 dan level 1–5 untuk 11–15.

## Status integrasi repo

Catatan tes/branch di atas merupakan bukti sesi implementasi pada waktunya. Implementasi yang tersedia telah digabungkan di checkout `main`; [laporan kondisi repo](../../audits/2026-10-05-repository-status.md) menjadi acuan inventaris dan verifikasi gabungan saat publikasi. IRT, generasi LLM, self-adjusting dan publikasi database tetap belum tersedia.
