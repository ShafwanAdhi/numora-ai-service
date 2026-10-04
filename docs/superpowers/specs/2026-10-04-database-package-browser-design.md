# Interface AI: paket dan varian dari database Numora

Status: PROPOSED — spesifikasi untuk review sebelum implementasi.

## Tujuan dan izin

Pengguna ingin interface `Numora-ai-service` membaca paket soal dan varian yang
sudah diunggah ke database bersama. Pengguna mengizinkan perubahan repo Numora
yang diperlukan untuk integrasi ini; perubahan harus minimal dan dapat ditinjau.
Isi bank lokal tidak dicocokkan dengan soal demo database.

Keberhasilan: pilih sumber Database Numora, pilih paket berdasarkan nama,
baca item versi yang benar-benar ada dalam paket, lalu lihat original dan varian
dalam keluarga item tersebut. Muat ulang menampilkan upload terbaru.

## Pendekatan terpilih

Perluas antarmuka baca database sesuai ADR-011, lalu konsumsi melalui backend
Python existing. Browser tidak mengakses Supabase Data API atau PostgreSQL.

Alternatif yang dipertimbangkan:

- Views existing saja: perubahan lebih sedikit, tetapi nama/status paket dan
  paket kosong tidak tersedia pada view item saat ini.
- Akses tabel public langsung: membutuhkan privilege lebih luas dan melanggar
  batas compute yang sudah ditetapkan; tidak dipilih.
- View katalog tambahan: metadata lengkap, privilege terbatas, perubahan Numora
  hanya migrasi dan dokumentasi/tes terkait. Ini pendekatan terpilih.

## Perubahan Numora

Tambahkan migrasi maju melalui migration stream Numora. Jangan mengubah
migrasi historis atau data existing.

1. Buat `public.irt_input_package_catalog_v3`: satu baris per paket, termasuk
   paket yang belum mempunyai item. Kolom: `id`, `family_code`,
   `package_version`, `name`, `assessment_type`, `purpose`, `status`,
   `is_demo`, `chapter_id`, `level_id`, `variant_index`, `item_count`.
   `item_count` dihitung dari `package_items`; tidak menambahkan counter durable.
2. Tambahkan `version_number` pada akhir kolom view
   `public.irt_input_content_v3`. Urutan/nama kolom existing tetap kompatibel.
3. Grant SELECT view katalog kepada `numora_irt_runtime` dan
   `numora_main_runtime`; cabut privilege PUBLIC dan role Data API yang ada.
   Tidak memberi compute akses langsung ke tabel public.
4. Dokumentasikan tambahan kontrak view dan pemeriksaan privilege.

Migrasi tersebut tidak mengubah lifecycle assessment, scoring, XP, distribusi,
validasi konten, atau gate publikasi. Metadata nama/status paket tidak dianggap
izin distribusi. Paket DRAFT dan demo boleh dibaca oleh workbench internal.

## Backend service AI

Gunakan `psycopg` dan `python-dotenv` yang sudah tersedia pada environment;
cantumkan dependency untuk setup mesin/VPS berikutnya. Hindari ORM tambahan.

Konfigurasi `DATABASE_URL` berasal dari environment service AI atau `.env`
repo AI yang di-ignore. Tidak otomatis menyalin kredensial repo Numora.
Koneksi cloud wajib TLS. Runtime memakai LOGIN terpisah dengan role
`numora_irt_runtime`, bukan akun migration owner. Akun runtime harus disediakan
operator bila belum ada; koneksi live tidak diklaim selesai tanpa akun tersebut.

Gunakan koneksi pendek per request, transaksi read-only, connect timeout dan
statement timeout. Query SQL tetap dan parameterized; UUID, jenis aktivitas,
limit, offset divalidasi di batas HTTP. Jangan mengirim DSN, kredensial, stack
trace, atau pesan mentah driver kepada browser/log.

Endpoint internal workbench:

- `GET /api/database/status`: konfigurasi/kesiapan koneksi tanpa secret.
- `GET /api/database/packages?type=DRILL&limit=50&offset=0`: katalog,
  pagination, nama, status, versi, demo, jumlah item. Filter aktivitas opsional
  menerima DRILL, TRYOUT, PRETEST, PVP.
- `GET /api/database/package?id=<uuid>&limit=100&offset=0`: metadata paket
  dan item sesuai `display_order`, terikat `question_version_id` paket.
- `GET /api/database/family?id=<uuid>&limit=100&offset=0`: seluruh versi
  original/varian keluarga tersebut, dengan lineage yang benar-benar tersimpan.

Semua endpoint hanya membaca views. Daftar menggunakan pagination, batas
maksimum 100 baris per request, dan jumlah total untuk navigasi. Detail paket
membaca metadata dan item dalam satu transaksi dengan snapshot konsisten.
Item yang referensi kontennya tidak tersedia tidak dihilangkan diam-diam:
tampilkan indikator konten tidak tersedia pada posisi item tersebut.

Jika konfigurasi belum ada, view/migrasi belum tersedia, privilege kurang,
atau DB tidak dapat dihubungi, tampilkan pesan Indonesia yang aman dan langkah
setup yang relevan. Generator lokal tetap dapat digunakan.

## Interface existing

Tambahkan pemilih sumber `Bank lokal` / `Database Numora` dengan Bank lokal
sebagai default. Pertahankan katalog lokal, edit config, Generate, Regen.

Mode database menampilkan:

- Filter aktivitas, pilihan paket berlabel nama/versi/status/demo, Muat ulang.
- Daftar item sesuai urutan paket dan konten konkret versi yang dipin.
- Pilihan anggota keluarga: ORIGINAL/VARIANT, version number dan ID versi.
- Stem, opsi/pernyataan, kunci, pembahasan, metadata content/validation state.
- Metadata media sebagai teks/link yang aman; jangan menyisipkan HTML mentah
  atau menganggap media JSON adalah konten yang dapat dieksekusi.
- Pagination katalog/item/versi, loading, empty, error, dan retry.

Beralih sumber tetap melindungi edit config lokal yang belum disimpan.
Mode database tidak menawarkan Generate, Regen, atau edit/upload soal DB.
Data database tidak otomatis dimasukkan ke bank/config lokal.

Pertahankan localhost binding dan pemeriksaan Host/Origin existing. Kunci dan
pembahasan hanya untuk workbench internal ini. Akses dari VPS melalui SSH
tunnel; publikasi UI ke internet memerlukan autentikasi terpisah di luar scope.

## Kriteria penerimaan

1. Bank lokal tetap berfungsi tanpa `DATABASE_URL`.
2. Paket bernama/status/demo yang tersedia di DB dapat dilihat; paket kosong
   tampil dengan jumlah nol dan empty state.
3. Paket menampilkan versi item yang dipin, bukan versi terbaru yang berbeda.
4. Original, varian, dan versi historis dibedakan. Parent kosong ditampilkan
   sebagai lineage belum tersedia, tidak dibuat-buat.
5. Upload baru muncul setelah Muat ulang tanpa restart atau sinkronisasi CSV.
6. UUID/filter/pagination invalid ditolak; query tidak menerima SQL dari input.
7. Transaksi baca dan privilege runtime diverifikasi; tidak ada mutasi data.
8. Tidak ada kredensial atau error DB mentah di respons, HTML, atau log.
9. Empty/error/timeout/permission denied ditangani tanpa merusak mode lokal.
10. Regresi Python dan tes terarah endpoint/UI lulus; migrasi/privilege diuji
    pada PostgreSQL lokal terisolasi. Verifikasi live hanya setelah migrasi
    tersedia dan runtime credentials valid, dengan query read-only.

## Pengiriman dan batas operasional

Pertahankan perubahan pengguna yang sudah ada pada kedua repo. Hasil kode,
migrasi, dependency manifest, contoh environment tanpa secret, tes, dan panduan
setup disiapkan dahulu. Pemeriksaan DB live memakai input runtime yang diberikan
operator. Eksekusi migrasi shared/cloud dan provisioning credential adalah
operasi tersendiri; izin mengubah repo Numora tidak otomatis mengizinkan DDL live.

Tidak membuat IRT engine, compute consumer, upload/import soal, auto-adjust,
atau endpoint siswa baru dalam pekerjaan ini.
