# Handoff bundel lokal gambar varian Tryout

Tanggal: 27 Oktober 2026. Tahap 1–5 lokal selesai; integrasi R2/compute produksi
belum diaktifkan. Instruksi pengguna tahap 5 tidak mencakup upload atau impor DB.

## Cara menghasilkan paket review

Dari root `Numora-ai-service` dengan dependency `requirements-image.txt`:

```powershell
python -B variant_gen/cli.py package-media tryout-1 s1 --output .scratch/tryout-media-s1
```

Output:

```text
questions.json
media-manifest.json
preview.html
images/<sha256>.png
```

Buka `preview.html` dengan seluruh folder tetap bersama. Preview menampilkan 30
soal dan lima gambar; kunci/pembahasan tersedia dalam elemen details khusus
review operator. Ini bukan payload Student dan bukan halaman publik.

`package-gen`, `gen`, workbench, dan service existing tetap memakai perilaku lama.
Tidak ada render/cache disk otomatis. Command baru merupakan ekspor opt-in.

## Kontrak Python

- `cli.preview(bank, configs, qid, seed, *, on_generated=None)`.
- `tryout.generate_package(bank, configs, package_id, seed, *, on_generated=None)`.
- Callback `(original, config, result, record)` menerima hasil generate yang
  sama setelah `make_record`. Collector gambar membaca `result.values` eksak,
  bukan `values_used` yang dapat berisi pembulatan. Satu paket memakai tepat 27
  panggilan engine; tiga konseptual tetap ORIGINAL_ONLY.
- `tryout_media.generate_media_bundle(...) -> MediaBundle`: murni, tidak menulis.
- `tryout_media.write_media_bundle(bundle, output: Path) -> Path`: memvalidasi
  ulang media dan menulis bundel secara atomik. Implementasi filesystem dipisah
  di `tryout_media_io.py` agar tanggung jawab file dan generasi tidak bercampur.

`MediaBundle` memuat `questions`, tuple `images: RenderedImage`, serta
`media_manifest`. Struktur manifest pertanyaan existing tetap versi 1; sidecar
media memiliki `schema_version:1` dan `status:LOCAL_RENDERED`.

## Manifest media dan identitas

Envelope memuat package_id, seed, bundle_id dan lima assets. Saat ekspor,
ditambahkan hash aktual `questions_sha256` dan `preview_sha256`.

Setiap aset memuat:

- question_id, record_id, seed, variant_ver, versi/hash original dan config;
- hash isi record lengkap, selain timestamp operasional created_at;
- asset_id `diagram-1`, placement `STEM`, item_id null, urutan 1;
- marker rencana `[[asset:diagram-1]]` dan alt text tanpa jawaban yang ditanyakan;
- path relatif `images/<sha256>.png`, hash byte, ukuran, lebar/tinggi;
- scene dan binding pecahan eksak, provenance template/font/renderer;
- asset_identity yang mengikat konten soal dengan identitas render gambar.

`bundle_id` mengikat seluruh konten 30 soal dan lima descriptor gambar. Seed atau
record_id saja bukan identitas cukup: config, template, font, renderer, atau
konten berbeda memberi identitas berbeda. PNG identik boleh memiliki nama file
hash identik, tetapi referensi per soal/seed tetap terlacak.

Hash JSON lokal memakai serialisasi `tryout_media.json_bytes`, bukan algoritme
canonical fingerprint payload Numora. Jangan menyalin record_content_sha256 atau
bundle_id ke kolom contentFingerprint canonical; adapter harus membentuk payload
Numora yang benar dan menghitung fingerprint kontrak tersebut secara terpisah.
SHA-256 PNG tetap merupakan hash byte file yang dapat diverifikasi lintas bahasa.

`created_at` dikecualikan hanya dari identitas konten/retry. Ekspor pertama
menyimpan timestamp aktualnya. Retry input sama memeriksa seluruh hash dan isi
stabil, lalu memakai snapshot pertama; tidak menimpa timestamp atau byte lama.
Konten berbeda, file hilang/rusak, atau output parsial ditolak.

Sebelum penulisan, exporter membangun ulang manifest, merender ulang scene yang
dipin tanpa mengacak soal, membandingkan PNG/provenance, dan mencocokkan binding
dengan record. Ini juga mendeteksi perubahan dictionary metadata oleh pemanggil.
Penulisan berlangsung di direktori sementara milik proses pada parent output
yang sama; target final baru muncul sesudah seluruh berkas tervalidasi. Cleanup
rekursif hanya untuk direktori staging tersebut, tidak untuk data pengguna.

## Batas menuju R2 dan database

LOCAL_RENDERED membuktikan artefak lokal, **bukan** receipt VERIFIED. Manifest
tidak berisi bucket, objectKey, signed URL, base64, atau klaim siap publikasi.
Stem di `questions.json` dipertahankan; preview memasang gambar melalui sidecar
STEM. Marker di descriptor adalah rencana penempatan untuk adapter berikutnya,
bukan klaim bahwa importer existing dapat langsung menerima bundel ini.

Integrasi lanjutan perlu kontrak dan implementasi terpisah:

1. **Mapping canonical melalui Numora.** Peta original/family, versi sumber,
   rubric dan versi varian tujuan harus benar. Jangan mengarang UUID atau
   memakai importer original untuk menyamarkan varian sebagai original baru.
   `record_id` lokal memuat tanda titik dua; jangan langsung menganggapnya valid
   sebagai externalId endpoint upload. Identitas upload ditentukan adapter/server.
2. **Upload oleh jalur NestJS.** Reservasi idempotent → PUT pending → completion
   dan verifikasi byte → receipt VERIFIED. Compute tidak mendapat credential
   bucket atau akses browser langsung ke data bisnis.
3. **Versi dan receipt.** contentVersion upload harus cocok dengan versi konten
   varian tujuan; bukan otomatis original_version/config_version/template_version.
   Receipt harus cocok dengan identitas/aset, hash, MIME dan ukuran yang dipin.
4. **Simpan varian secara immutable.** Payload canonical mencakup reference media,
   marker/placement dan fingerprint. Paket/attempt memin UUID versi soal dan key
   gambar tersebut, tanpa mengganti histori atau menimpa objek lama di R2.
5. **Akses siswa.** NestJS tetap memeriksa ownership serta fase WORK/REVIEW dan
   gate Tryout/IRT, lalu memberi signed GET sementara. Gambar tidak digenerate
   ulang ketika siswa GET dan signed URL tidak menjadi identitas permanen.
6. **Kontrak compute.** `numora_service/content.py`, schema kandidat dan service
   generator-v1 saat ini menolak media aktif. Penolakan dipertahankan; dukungan
   baru harus memiliki capability/versi kontrak dan tes di kedua repo. Jangan
   sekadar menghapus guard MEDIA_NOT_SUPPORTED atau membuang aset secara diam-diam.

PostgreSQL dan R2 tidak memiliki transaksi bersama. Upload sukses lalu write DB
gagal harus dapat diulang tanpa membuat versi ganda; jangan menghapus objek
yang masih dirujuk histori. Publikasi/approval akademik tetap proses terpisah.

Rujukan main repo: `docs/api/CONTENT_MEDIA_UPLOADS.md`,
`docs/api/CONTENT_IMPORT_PREVIEW.md`,
`docs/superpowers/specs/2026-10-26-tryout-r2-database-sync-design.md`, ADR-008.

## Batas bukti dan minor

Ekspor lokal dan byte/hash diuji; cloud upload, DB import, Student E2E, Publish,
dan kesetaraan kesulitan belum dibuktikan oleh hasil ini.

Review independen tidak menemukan Critical/Important. Catatan minor: guard
callback memakai equality Python, sehingga perubahan tipe numerik dengan nilai
setara tidak terdeteksi sebagai mutasi; collector internal tidak melakukannya.
Tes path traversal manifest tidak menggantikan tes filesystem junction/symlink;
Windows menolak pembuatan symlink dalam lingkungan pemeriksaan (1314), sehingga
cabang tersebut belum dibuktikan secara end-to-end. Pemeriksaan reparse dan
batas staging tetap ada. Minor tahap sebelumnya tetap dicatat pada laporannya.
