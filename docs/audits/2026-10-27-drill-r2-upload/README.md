# Upload sembilan gambar original Drill ke R2

**ENGINEERING DECISION - instruksi pengguna:** "gas masukkan 9 gambar soal drill
ke r2". Upload ini mencakup satu gambar **original** untuk masing-masing sembilan
soal, bukan seluruh 163 gambar unik varian/stok. Tidak ada perubahan konten soal,
referensi media question_versions, susunan paket, atau publikasi.

## Hasil

Sembilan aset tersimpan pada bucket `numora-bucket` melalui service upload
NestJS existing: reserve, PUT ke pending, pemeriksaan byte, finalisasi,
dan receipt VERIFIED. Kesembilan object final diunduh ulang melalui signed GET;
HTTP 200, panjang byte dan SHA-256 cocok dengan PNG lokal.

| Soal | Versi konten aset | Status |
|---|---|---|
| pg-16-4-1 | 2 | VERIFIED |
| pg-16-4-2 | 1 | VERIFIED |
| pg-16-4-3 | 2 | VERIFIED |
| pg-16-4-4 | 2 | VERIFIED |
| mcma-16-4-6 | 2 | VERIFIED |
| mcma-16-4-7 | 2 | VERIFIED |
| pg-16-5-1 | 2 | VERIFIED |
| pg-16-5-3 | 1 | VERIFIED |
| pg-16-5-5 | 1 | VERIFIED |

Object key mengikuti kontrak existing:

```text
question-media/{question_id}/v{contentVersion}/drill-original-c948bf0bfd6f8b71-diagram-1-{sha256}.png
```

Sumber adalah sembilan entri `mode:original` dari bundle review lokal
`c948bf0bfd6f8b71514aaff0fefac3b1dfed7438a90b4e42c65c1e2e0e89ddc3`.
Versi dan originalHash sudah dicocokkan dengan original database development
sebelum reservasi. Asset ID baru dan SHA pada key mencegah penimpaan gambar lain.

## Bukti dan batas

- [Preflight, pemetaan gambar dan snapshot versi/paket](preflight.json).
- [Sembilan receipt R2](media-receipts.json), tanpa signed URL.
- [Hasil upload dan download verification](upload-result.json).
- [Pengecekan ulang read-only](verify-result.json).

DB yang digunakan adalah proyek development existing. Hanya service upload
yang menulis reservasi/receipt pada `content_media_uploads` dan audit log yang
terkait. Tidak ada migrasi, penulisan question_versions, paket, atau approval.
Hash seluruh sembilan versi soal dan package_items yang mereferensikannya tetap
sama dengan baseline.

**Aset sudah tersedia di R2, tetapi belum dihubungkan ke media versi soal dalam
database.** Upload bukan publikasi atau aktivasi tampilan siswa. Interface
lokal tetap memakai renderer lokal existing; tahap ini tidak mengganti alurnya
menjadi pembacaan R2.

Operator eksplisit (dari root Numora-ai-service):

```powershell
node --test tools/upload_drill_original_images.test.cjs
node tools/upload_drill_original_images.cjs --check
node tools/upload_drill_original_images.cjs --verify
# --upload hanya untuk menjalankan/retry upload yang sudah diotorisasi.
```

Empat tes operator lulus: memilih hanya sembilan original, menolak cakupan
kurang/duplikat, memeriksa bundle/versi/byte gambar, dan normalisasi snapshot
driver DB menjadi JSON. Upaya awal berhenti sebelum reservasi karena perbedaan
tipe Result/Array pada snapshot; diperbaiki dengan tes RED-GREEN sebelum upload.
Idempotency key dipin per externalId, assetId, versi dan SHA; retry memakai
receipt VERIFIED existing tanpa PUT ulang.
