# Kondisi repository - 7 Oktober 2026

Checkout aktif mempunyai820 original/746 config: Drill790 original/719 config, Tryout30 original/27 config. Pretest belum memiliki bank lokal. Katalog mencakup tujuh bank dan109 kelompok; level4-5 baru tersedia pada indikator11-15.

Drill:719 generator +67 original dengan206 stok manual VERIFIED +4 HOLD =790. Tryout:27 generator +3 original dengan9 stok manual VERIFIED =30. Total stok70 original/215 varian; hanya4 Drill HOLD belum mempunyai generator maupun stok. [Audit Tryout](2026-10-07-tryout-conceptual-stock-audit.md). Generate paket Tryout tetap ORIGINAL_ONLY untuk ketiga soal konseptual; stok tersedia per soal pada UI/CLI.

Bank1-5:150 original,138 ACTIVE,10 konseptual dengan stok manual,2 HOLD_SOURCE. [Empat puluh generator revisi](2026-10-07-revised-1-5-generator-audit.md) memakai original v2/config v1, diverifikasi pada domain default dan20 varian unik per soal. Suite terbaru172 tes dalam100,233 detik,OK; browser memeriksa seluruh40 ID baru. Hasil generate tidak disimpan.

Bank6-10:150 original,140 ACTIVE,9 DEFERRED_CONCEPTUAL dengan stok manual,1 HOLD_SOURCE. Sebelas generator revisi baru sudah tersedia melalui CLI/UI; `mcma-6-3-7` tetap ditahan. [Audit revisi](2026-10-07-revised-6-10-generator-audit.md). Suite terbaru158 tes dalam93,158 detik,OK; browser memeriksa Generate untuk seluruh11 ID revisi6-10.

Bank20-23:120 original,102 ACTIVE,18 DEFERRED_CONCEPTUAL,0 HOLD_SOURCE. Seluruh16 revisi Curriculum memakai original v2/config v1. [Audit generator revisi](2026-10-07-revised-20-23-generator-audit.md). Bank16-19 kini memiliki112/120 config; [dua generator indikator17](2026-10-07-drill-16-19-source-revision.md) ditangani terpisah.

Generate CLI/Service AI stateless: hasil hanya dalam respons/tampilan, tanpa akses database atau riwayat varian. Stok manual dapat dibaca ulang. Fixture audit tersimpan terpisah sebagai bukti pemeriksaan. IRT dan API produksi antar-VPS belum diimplementasikan.

Verifikasi historis sebelum revisi1-5: suite gabungan147 tes dalam82,736 detik,OK. Audit16 generator20-23:320 kandidat unik dan1600 pemeriksaan seed tambahan lulus. Browser Generate seluruh16 ID berhasil. Audit5-6 Oktober tetap arsip historis.

Pekerjaan lokal belum di-commit/push. Dokumen self-adjustment existing dan pekerjaan di luar indikator20-23 dipertahankan.
