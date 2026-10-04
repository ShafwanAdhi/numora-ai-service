# Interface AI: paket dan varian dari database Numora

Status: IMPLEMENTED — dua tab sesuai permintaan pengguna; verifikasi DB live menunggu kredensial.

## Tujuan dan izin

Pengguna ingin interface `Numora-ai-service` membaca paket soal dan varian yang
sudah diunggah ke database bersama. Pengguna mengizinkan perubahan repo Numora
yang diperlukan untuk integrasi ini; perubahan harus minimal dan dapat ditinjau.
Isi bank lokal tidak dicocokkan dengan soal demo database.

USER CLARIFICATION — 4 Oktober 2026: backend service AI boleh mengakses
PostgreSQL langsung. Pengguna akan mengisi kredensial sendiri; sediakan `.env`
kosong yang di-ignore dan `.env.example` tanpa secret. Tidak ada koneksi live
atau penyalinan kredensial Numora yang diperlukan dalam tahap persiapan.

USER CLARIFICATION — akses tidak dibatasi aplikasi ke role atau view compute.
Backend boleh membaca tabel database langsung memakai kredensial yang diisi
pengguna. Privilege PostgreSQL/RLS yang sudah berlaku tetap mengikuti akun itu;
aplikasi tidak mengubah grants, roles, atau RLS. Tahap ini hanya SELECT, tanpa
program create/update/delete maupun perubahan schema.

Keberhasilan: buka tab DB Utama, pilih paket berdasarkan nama,
baca item versi yang benar-benar ada dalam paket, lalu lihat original dan varian
dalam keluarga item tersebut. Muat ulang menampilkan upload terbaru.

## Pendekatan terpilih

Baca PostgreSQL langsung dari backend Python existing, tanpa perantara API
Numora. Sesuai instruksi terbaru pengguna, gunakan tabel yang diperlukan,
bukan membatasi akses ke views/role compute pada ADR-011. Browser hanya
menghubungi backend Python, bukan Supabase Data API atau PostgreSQL.

## Perubahan Numora

Tidak diperlukan perubahan repo utama atau migrasi untuk tahap baca ini.
Metadata berasal dari `public.assessment_packages`; item dari
`public.package_items`; konten dan keluarga dari `public.question_versions`
dan `public.question_variants`. Gunakan LEFT JOIN untuk menampilkan paket kosong
dan membaca `version_number` langsung dari tabel versi.

Metadata paket mencakup `id`, `family_code`, `package_version`, `name`,
`assessment_type`, `purpose`, `status`, `is_demo`, `chapter_id`, `level_id`,
`variant_index`, dan jumlah item yang dihitung saat query. Metadata nama/status
tidak dianggap izin distribusi; DRAFT dan demo tetap terlihat oleh workbench.

## Backend service AI

Gunakan `psycopg` dan `python-dotenv` yang sudah tersedia pada environment;
cantumkan dependency untuk setup mesin/VPS berikutnya. Hindari ORM tambahan.

Konfigurasi `DATABASE_URL` berasal dari environment service AI atau `.env`
repo AI yang di-ignore. Tidak otomatis menyalin kredensial repo Numora.
Koneksi cloud wajib TLS. Gunakan akun pada DATABASE_URL tanpa memaksakan nama
role atau whitelist view. Jangan membuat akun atau mengubah privilege secara
otomatis. Pengguna mengisi kredensial sendiri; verifikasi live menunggu isian itu.

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

Semua endpoint hanya membaca tabel yang diperlukan. Pagination adalah cara
penyajian data, bukan pembatasan hak akses: seluruh hasil dapat ditelusuri, tanpa
batas maksimum page size tambahan yang dibuat aplikasi. Detail paket
membaca metadata dan item dalam satu transaksi dengan snapshot konsisten.
Item yang referensi kontennya tidak tersedia tidak dihilangkan diam-diam:
tampilkan indikator konten tidak tersedia pada posisi item tersebut.

Jika konfigurasi belum ada, tabel/schema tidak sesuai, privilege akun kurang,
atau DB tidak dapat dihubungi, tampilkan pesan Indonesia yang aman dan langkah
setup yang relevan. Generator lokal tetap dapat digunakan.

## Interface existing

Tambahkan dua tab utama `Service AI` / `DB Utama`, dengan Service AI
sebagai default. Pergantian tab menyembunyikan panel tanpa membuang draft config;
keyboard ArrowLeft/ArrowRight/Home/End dan atribut ARIA didukung. Pertahankan katalog lokal, edit config, Generate, Regen.

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
10. Regresi Python dan tes terarah endpoint/UI lulus; query diuji pada fixture
    PostgreSQL lokal terisolasi. Verifikasi live hanya setelah pengguna mengisi
    kredensial, dengan query read-only; tidak melakukan migrasi/provisioning.

## Pengiriman dan batas operasional

Pertahankan perubahan pengguna yang sudah ada pada kedua repo. Hasil kode,
dependency manifest, contoh environment tanpa secret, tes, dan panduan setup
disiapkan dahulu. Pemeriksaan DB live memakai kredensial yang pengguna isi.
Tidak ada DDL, perubahan grant, atau provisioning credential dalam tahap ini.

Tidak membuat IRT engine, compute consumer, upload/import soal, auto-adjust,
atau endpoint siswa baru dalam pekerjaan ini.
