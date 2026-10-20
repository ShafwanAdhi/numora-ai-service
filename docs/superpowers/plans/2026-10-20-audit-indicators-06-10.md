# Validasi dan audit indikator 6–10

**Goal:** memeriksa seluruh 250 soal dari DOCX intake, dengan bukti struktur, solusi independen, opsi, kunci, pembahasan, dan usulan koreksi.

**Architecture:** gunakan pembaca DOCX existing untuk lokasi dan penomoran, bandingkan dengan XML arsip; audit matematika dibagi per indikator. Review sementara tidak dipakai sebagai oracle karena ditemukan temuan dari soal lain.

**Tech Stack:** Python stdlib, XML/ZIP, Fraction, JSON/CSV/Markdown.

**Spec:** permintaan pengguna 20 Oktober 2026 dan rencana audit original indikator 1–23 yang dilampirkan.

## Batas

- Tidak mengubah sumber, bank aktif, config, API, database, atau pemetaan runtime.
- Tidak menafsirkan keberhasilan generator sebagai bukti akademik.
- Pembahasan inline, opsi ganda dan sumber rusak diperiksa pada paragraf asli; ketidakpastian dinyatakan.
- Proposal koreksi terpisah dari isi sumber; tidak mengklaim persetujuan Kurikulum/IRT.
- Perubahan pengguna terdahulu dipertahankan; tidak commit/push tanpa permintaan.

## Pelaksanaan

- [x] Tahap 7: verifikasi hash, seluruh paragraf/OMML/tabel/penomoran dan 250 posisi unik; simpan `stage-07-extraction-06-10/`.
- [x] Tahap 8: audit independen 100 soal I6–7, 100 soal I8–9, dan 50 soal I10; simpan part JSON dan pemeriksa reproduksinya.
- [x] Gabungkan 250 entri ke JSON/CSV/README, pisahkan status soal/kunci/pembahasan dan daftar tindak lanjut.
- [x] Jalankan pemeriksa struktur, konsistensi coverage/status/kunci, dan hash sebelum/sesudah; review perbedaan dari review sementara.

## Hasil

250 soal; 218 VALID, 10 INVALID, 22 UNCERTAIN. Sebanyak 70 entri memiliki temuan (58 dengan status komponen nonbersih; 12 catatan tambahan). Seluruh 910 hash input terlindungi tetap sama. Lima skrip validasi/audit berhasil direproduksi; 6 tes baru dan 8 tes batas audit/pencocokan lama lulus. Review pemeriksa memperbaiki provenance, batas indeks akhir, opsi terpotong, bukti bersyarat, serta kesesuaian artefak per soal.

Keluaran: [validasi struktur](../../audits/2026-10-19-original-question-audit/stage-07-extraction-06-10/README.md), [audit akademik](../../audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/README.md). Semua usulan koreksi tetap PROPOSED; tidak diterapkan ke sumber/bank/generator. Belum commit/push.

## Fokus review

Temuan salah identitas; opsi asli bercampur enumerasi stimulus; pembahasan berada di baris kunci; PG mempunyai lebih dari satu jawaban; pertidaksamaan/domain/satuan dan asumsi konteks.
