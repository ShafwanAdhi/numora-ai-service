# Tahap 5 selesai untuk gambar Drill

**ENGINEERING DECISION - instruksi pengguna:** selesaikan tahap berikutnya dan
pastikan soal bergambar dapat diuji melalui interface. Seluruh tahap 1-5 lokal
selesai. Tidak ada upload R2, penulisan database, publikasi, atau perubahan
aturan generator/akademik.

## Uji langsung melalui interface

Buka **http://127.0.0.1:8765/image-variants**, pilih **Aktivitas: Drill**,
pilih soal, kemudian mode Original, Generator, atau Stok yang tersedia.
Generator menggunakan seed; Stok dipilih melalui identitas stok. Unduh PNG
melalui tombol pada hasil. Kunci dan pembahasan tersedia untuk review operator.

Seluruh pilihan diuji menggunakan formulir browser sungguhan, bukan hanya
memanggil endpoint. Teks, kunci, mode, identitas original/stok, kontrol yang
aktif, dan SHA-256 hasil unduhan dibandingkan dengan paket review.

| Soal | Pilihan yang diuji di interface | Status |
|---|---|---|
| pg-16-4-1 | 1 original + 30 varian numerik | PASS |
| pg-16-4-2 | 1 original + 2 stok | PASS |
| pg-16-4-3 | 1 original + 30 varian numerik | PASS |
| pg-16-4-4 | 1 original + 30 varian numerik | PASS |
| mcma-16-4-6 | 1 original + 2 stok | PASS |
| mcma-16-4-7 | 1 original + 2 stok | PASS |
| pg-16-5-1 | 1 original + 2 stok | PASS |
| pg-16-5-3 | 1 original + 30 varian numerik | PASS |
| pg-16-5-5 | 1 original + 30 varian numerik | PASS |

Total **167 kombinasi untuk sembilan keluarga soal**, termasuk sembilan
original. Ini bukan 167 original baru. Semua diagram dari DOCX indikator 16-19
berada di indikator 16; lima aset lain adalah potongan rumus/simbol yang telah
diinventarisasi dan tidak dibuatkan generator diagram tersendiri.

[Bukti per pilihan interface](stage-5/interface-proof.json),
[desktop](stage-5/desktop.png), dan [mobile](stage-5/mobile.png).
Tryout tetap tersedia pada aktivitas Tryout dan format request lamanya tetap.

## Ekspor review lokal

[Preview lengkap](stage-5/review-full/preview.html) berisi lima original numerik,
150 varian numerik, empat original konseptual, serta delapan stok: 167 record
dan **163 PNG unik**. PNG boleh dipakai ulang ketika gambarnya memang sama;
provenance tiap record tetap terpisah.

Bundle ID:
`c948bf0bfd6f8b71514aaff0fefac3b1dfed7438a90b4e42c65c1e2e0e89ddc3`.

Dari root Numora-ai-service:

```powershell
# Seluruh domain dan stok:
python -B tools/export_drill_image_review.py --output .scratch/drill-image-review-full
# Satu varian per keluarga numerik, beserta semua original/stok: 22 record.
python -B tools/export_drill_image_review.py --seed 7 --output .scratch/drill-image-review-s7
# Verifikasi tanpa generate ulang atau menulis, kecuali --report diminta:
python -B tools/verify_drill_image_review.py --input .scratch/drill-image-review-full
```

Output: `questions.json`, `media-manifest.json`, `preview.html`, serta
`images/<sha256>.png`. Jenis dokumen **DRILL_IMAGE_REVIEW**, bukan paket Tryout,
payload database, atau receipt R2. Manifest tidak menyimpan base64 maupun URL
sementara. Base64 hanya digunakan pada respons HTTP preview existing.

Generator existing mencari seed untuk semua k=1..30; gambar dibuat dari accepted
Result yang sama hanya saat ditemukan k baru. Tidak ada pengundian ulang untuk
memperbaiki gambar, perluasan domain, atau perubahan syarat penyaringan.

Penulisan bersifat eksplisit dan atomik menggunakan utilitas file writer
existing. Retry dengan isi stabil sama mempertahankan snapshot pertama,
termasuk timestamp original ekspor; target berbeda, rusak, atau tidak lengkap
ditolak. Tidak ada penimpaan otomatis. Format/kontrak paket Tryout tidak diubah.

## Verifikasi akhir

- **104 tes terkait lulus**: 10 ekspor baru, 22 numerik/konseptual Drill,
  44 image/bundle, 14 Tryout, 10 mode/workbench gambar, serta 4 stateless.
- **155 pemeriksaan matematika numerik** dan **12 pemeriksaan skenario
  konseptual** lulus: [bukti](stage-5/academic-proof.json).
- **167 pilihan interface** pada sembilan keluarga lulus, termasuk seluruh
  original, seluruh domain varian numerik, serta delapan stok.
- Review independen menemukan satu celah penting dan dua temuan kecil pada
  verifier ekspor. Semua diperbaiki melalui tes RED-GREEN dan regrade lulus.
  Verifier kini mengikat alt text, dimensi, panjang byte dan question_id ke
  provenance, memeriksa identitas kasus, serta kesamaan seed pada mode satu seed.
- Hash sumber, bank/revisi, config/domain/filter, stok, template/font, renderer,
  dan interface existing tetap. Modul ekspor baru bersifat opt-in.
- Identitas paket Tryout seed 1 tetap
  `083125b756f4107d143ade49f3ccd824f3be1fdb6ab1ed7d9a70eff6c8e92162`.

[verification-stage5.json](verification-stage5.json) mencatat hasil dan hash
artefak. Hasil akademik ini merupakan pemeriksaan engineering lokal; status
persetujuan kurikulum, self-adjustment, dan kesetaraan IRT tidak diubah.

Untuk mengulang pengujian seluruh interface dengan workbench berjalan:

```powershell
python -B tools/test_drill_review_interface.py --bundle .scratch/drill-image-review-full --output .scratch/drill-interface-proof.json
```

Perintah browser memerlukan npx/Playwright CLI; tidak memasang framework tes
baru dalam proyek dan tidak menulis data ke sistem utama.
