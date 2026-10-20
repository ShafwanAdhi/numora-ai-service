# Tahap 7 — Validasi ekstraksi indikator 6–10

**250 posisi unik**; 5 indikator × 5 level × 10 soal. Hash DOCX sesuai manifest.

Seluruh 5775 paragraf, 56 tabel (termasuk span/merge), 2277 persamaan OMML dibandingkan dengan XML arsip. Tidak ada gambar tertanam.

Status proyeksi: {'STRUCTURE_VERIFIED': 229, 'REVIEW_REQUIRED': 21}. Opsi berlebih dan pembahasan yang tidak terpisah otomatis ditandai REVIEW_REQUIRED; bukan dianggap hilang atau dipilih salah satu secara otomatis. Penomoran asli dan seluruh paragraf dipertahankan dalam JSON.

Validasi ini membuktikan kesetiaan struktur, bukan kebenaran akademik. Pembacaan batas yang ditandai dan audit matematika tersedia pada [tahap 8](../stage-08-academic-indicators-06-10/README.md).

XML OMML tersimpan identik dengan arsip; proyeksi teks memakai LaTeX intake yang sama, sehingga bukan pembuktian independen kesetaraan LaTeX–OMML. Makna notasi ditinjau pada audit akademik.

Hash 910 berkas sumber/bank/config/layanan tetap sama. [JSON](validation.json) · [CSV](entries.csv).

Reproduksi: `python -B variant_gen/tests/validate_intake_06_10.py`.
