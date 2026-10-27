# Generator gambar Drill indikator 16-19 Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement one approved stage per user instruction. Do not continue to another stage automatically.

**Goal:** gambar lokal sembilan keluarga soal Drill mengikuti generator atau
stok existing, tanpa perubahan aturan akademik dan domain generator.

**Architecture:** gunakan fasilitas image_variants/callback existing dan adapter
Drill terpisah. Pertahankan ilustrasi sumber yang sesuai; gambar ulang diagram
yang bertentangan dengan versi aktif. Identitas konten dan template dipin.

**Tech Stack:** Python, OOXML/ZIP, JSON/CSV; tahap renderer memakai Pillow dan
font existing. Workbench memakai HTTPServer dan HTML/JavaScript existing.

**Spec:** [Desain yang disetujui](../specs/2026-10-27-drill-image-variants-design.md).

## Global constraints

- Satu tahap per instruksi; laporan menjadi checkpoint sebelum tahap berikutnya.
- Tidak mengubah bank, revisi, config/domain/filter, stok, opsi/kunci/pembahasan.
- Tidak ada DB/R2, publikasi, atau perubahan approval/IRT/self-adjustment.
- Kerjakan di workspace terisolasi; salin hanya delta milik tugas ke repo lokal.
- Jangan commit, reset, atau memasukkan perubahan pengguna yang tidak terkait.

## Review focus

- Nama imageN berubah sementara byte tetap; cocokkan hash dan paragraf sumber.
- Original aktif sudah direvisi; sumber bukan pengganti konten aktif.
- Original numerik k=0 bukan kandidat varian; gunakan record original existing.
- pg-16-5-5: v9 bukan tinggi segitiga; kunci original D/varian C tetap.
- Empat keluarga stok memerlukan 12 skenario; stok tanpa tutup tidak boleh memakai net tertutup.

## Tahap 1 - Arsip dan pemetaan

- [x] Arsipkan DOCX verbatim, semua 14 media, dan XML/relationship sumber.
- [x] Kaitkan setiap placement dengan indikator/level/nomor/kemunculan, paragraf dan body block.
- [x] Buat JSON/CSV yang membedakan sembilan diagram dari lima rumus/simbol.
- [x] Pin original lengkap, versi/hash original dan config, serta delapan stok.
- [x] Periksa domain existing tanpa mengubahnya; ini bukan audit akademik baru.
- [x] Bekukan hash bank/revisi/config/stok/template Tryout dan runtime pembanding.
- [x] Verifikasi arsip, rekonstruksi pemetaan, CSV/JSON dan kesamaan hash sebelum/sesudah.
- [x] Simpan rencana, bukti, status, serta perintah verifikasi lokal.

**Keluaran:** inventory-stage1 dan arsip; renderer_status NOT_IMPLEMENTED.

## Tahap 2 - Lima template numerik

- [x] Tulis tes binding/pin serta error terlebih dahulu dan amati kegagalan.
- [x] Tambah template/font/provenance melalui image_variants, adapter terpisah.
- [x] Gambar ulang net tabung/kerucut/limas yang salah; bersihkan label dua ilustrasi yang dipertahankan.
- [x] Preview lima original serta semua 150 kombinasi varian; periksa nilai eksak, geometri dan label terbesar.
- [x] Buktikan accepted Result hanya digenerate sekali; renderer gagal tidak mencoba angka lain.

## Tahap 3 - Diagram konseptual

- [x] Tulis tes untuk empat original dan delapan stok, termasuk pin yang salah.
- [x] Buat 12 skenario deterministik dengan bidang/sambungan/tutup/panel sesuai isi.
- [x] Cocokkan diagram dan alt text dengan opsi/kunci tanpa menambahkan jawaban.
- [x] Periksa gambar langsung; tidak membuat generator angka konseptual.

## Tahap 4 - Interface lokal

- [x] Uji kompatibilitas request Tryout lama sebelum implementasi.
- [x] Tambahkan aktivitas, soal, mode Original/Generator/Stok dan kontrol relevan.
- [x] Perluas GET katalog dan POST generator dengan stock_variant_id eksplisit.
- [x] Pertahankan respons record/image, guard Host/Origin, penanganan stale response dan PNG download.
- [x] Periksa state loading/error/empty/access rejection dan tampilan desktop/mobile.

## Tahap 5 - Verifikasi dan review lokal

- [x] Tambahkan ekspor Drill opt-in: record, manifest, PNG, preview; tidak mengubah paket Tryout.
- [x] Verifikasi seluruh domain/skenario, rumus geometri dan hash unduhan.
- [x] Jalankan regresi generator, Tryout, workbench; bandingkan hash protected input.
- [x] Lakukan review independen, perbaiki temuan, dan dokumentasikan batas/hasil.

Tahap 2 selesai dengan adapter/template baru yang opt-in; runtime existing tetap.
Tahap 3-4 selesai atas instruksi pengguna untuk lanjut sampai tahap 4.
Tahap 5 selesai atas instruksi pengguna, termasuk seluruh 167 pilihan melalui
form interface. Tidak ada perubahan runtime pada checkpoint Tahap 1.
