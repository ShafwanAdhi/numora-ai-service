# Progres tahap1 — indikator1–2, level1–3

Scope terbaru pengguna menggantikan rencana awal: indikator1–5 hanya level1–3; implementasi sekarang1–2. Runtime60 soal/6 kelompok. Indikator3–5 belum diimpor; tahap berikutnya90 soal. DOCX mentah utuh sebagai provenance, level4–5 tidak diimpor.

Task1: complete —60 original dengan raw source/key/explanation/SHA.34 ACTIVE,17 HOLD_SOURCE,9 DEFERRED_CONCEPTUAL.26 skipped dicatat per ID di soalskip.
Task2: complete —18 generator indikator1, original reproduction dan20 hasil unik per soal.
Task3: complete —16 generator indikator2, original reproduction dan20 hasil unik per soal.
Task4: complete — CLI/UI lifecycle dan guards lulus; audit34 PASS/26 SKIP,680 stok sampling dan1.700 accepted seed201–250; browser filter/format/idempotent/HOLD/DEFERRED lulus,0 error/warning. Review akhir selesai, semua Important diperbaiki. Full suite akhir108 tes PASS/99,763detik,exit0. Seluruh1.012 kandidat constraint-valid lolos oracle yang diperketat. Diff whitespace bersih. Browser final lulus,0 error/warning.

Baseline97 tes PASS/151,153detik; suite awal105 PASS/179,876detik; suite antara106 PASS/135,752detik.10 tes khusus terbaru PASS/1,358detik. Preflight605 file bank/config/store existing identik.

Review: source conflict pg-1-1-5 verified in raw XML → HOLD, new uncommitted config removed; test source_scope RED→GREEN. Oracle equivalence/model/modified-formula/explanation gaps → targeted mutation RED→GREEN. Stronger explanation check exposed mcma-2-1-8 wrong left-to-right formula; config now ((24k−12k)/3+2)×(−5k). pg-1-1-1 radical signs and pg-1-3-4 conditional prose fixed with RED→GREEN. Minor stale progress resolved here; no deferred minor.

Keputusan: branch feat/drill-1-2 pada checkout existing; tanpa worktree/commit otomatis. Alasannya preserve perubahan pengguna; biaya bila salah: checkout pengguna tetap di branch feature, perlu switch setelah menyimpan perubahan. Original ambigu/kunci caption/pembahasan bertentangan tetap HOLD, tanpa koreksi akademik; biaya bila salah: satu soal valid tertunda sampai review sumber. Domain generator bounded; biaya: stok unik dapat habis, perlu perluas parameter dan audit ulang bila dibutuhkan. Tidak menyentuh Numora/DB/.env/user store; scratch/audit memakai store sementara.
