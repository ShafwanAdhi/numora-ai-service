# Database Package Browser Implementation Plan

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execute inline in the current session; preserve existing user changes.

**Goal:** Interface AI membaca paket bernama beserta versi soal dan varian melalui koneksi PostgreSQL langsung dari backend Python.

**Architecture:** Python membaca tabel PostgreSQL langsung dalam transaksi read-only; UI existing menambahkan mode database. Kredensial hanya berasal dari environment/.env repo AI yang pengguna isi sendiri. Tidak diperlukan perubahan Numora, migrasi, atau pembatasan role/view oleh aplikasi.

**Tech Stack:** Python standard-library HTTP server, psycopg, python-dotenv, existing HTML/JavaScript, PostgreSQL, existing unittest.

**Spec:** `../specs/2026-10-04-database-package-browser-design.md`

## Global Constraints

- Bank lokal adalah default dan harus bekerja tanpa DATABASE_URL.
- Baca tabel PostgreSQL langsung; tanpa Supabase Data API di browser. Aplikasi tidak membatasi akses ke role/view tertentu.
- Cloud wajib TLS; akun/privilege mengikuti DATABASE_URL pengguna, tanpa mengubah grants/RLS.
- Semua request DB read-only; koneksi dan query memiliki timeout 5 detik.
- UUID dan pagination divalidasi; pagination hanya penyajian, tanpa batas maksimum page size buatan aplikasi.
- Snapshot paket menggunakan versi yang dipin, bukan otomatis konten terbaru.
- Tidak ada migrasi cloud, provisioning credential, upload, scoring, atau IRT dalam eksekusi plan.
- Jangan menimpa perubahan pengguna atau menyalin secret repo utama.

## Review Focus

- Paket kosong harus muncul melalui LEFT JOIN/count item, bukan hanya paket yang sudah berisi soal.
- Pergantian versi source tidak mengganti item historis yang dipin paket.
- Error driver/permission tidak boleh membocorkan DSN atau menghilangkan mode lokal.
- Edit config lokal belum disimpan harus dilindungi saat beralih sumber.
- Konten/media dari DB harus dirender sebagai teks; HTML dan URL berbahaya tidak dieksekusi.

## File map

Numora: hanya sumber referensi schema; tidak diperlukan perubahan untuk tahap ini.

AI: `.env` ignored dan `.env.example` sudah disiapkan; tambahkan `requirements.txt`, `variant_gen/database.py`, `variant_gen/tests/test_database.py`; perluas `variant_gen/webui.py`, `variant_gen/webui.html`, `variant_gen/tests/test_webui.py`, `variant_gen/README.md`.

### Task 1: Backend Python dan konfigurasi

**Interface:** `database.status() -> dict`; `database.packages(assessment_type: str | None, limit: int = 50, offset: int = 0) -> dict`; `database.package(package_id: str, limit: int = 100, offset: int = 0) -> dict`; `database.family(family_id: str, limit: int = 100, offset: int = 0) -> dict`. Page envelope: `{items, total, limit, offset}`; detail paket menambahkan `package`.

**HTTP:** endpoint GET `/api/database/status`, `/api/database/packages`, `/api/database/package`, `/api/database/family` pada spec. JSON API menggunakan camelCase. Missing config/unreachable DB/schema unavailable menghasilkan error aman 503; input invalid 400; paket tidak ada 404. Query-string key berulang ditolak.

- [ ] Tambahkan `test_database.py` dan perluas `test_webui.py`: no-config tidak memanggil connect; UUID/filter/limit/offset invalid tidak menjalankan SQL; kredensial palsu di pesan driver tidak muncul di respons; transaksi dikonfigurasi read-only; metadata Decimal/UUID/JSON dapat dikirim; paket kosong dan item missing-content tidak hilang. Gunakan unittest/mock existing, tanpa framework baru.
- [ ] Jalankan `python -B -m unittest discover -s tests -p test_database.py -v` dari variant_gen; tes gagal karena modul/endpoint belum tersedia.
- [ ] Tambahkan `database.py` memakai psycopg dengan dict rows, short-lived connection, TLS validation, transaction isolation REPEATABLE READ/read-only, connect_timeout=5, statement_timeout=5000. Baca assessment_packages/package_items/question_versions/question_variants dengan SQL parameterized, LEFT JOIN dan urutan deterministic. Pilih kolom eksplisit; tidak menambahkan generic SQL console.
- [ ] Load `.env` root AI dengan python-dotenv, tanpa override environment proses. Tidak menghubungkan DB saat startup server. Status memeriksa kesiapan hanya saat endpoint dipanggil. Secret tidak pernah dipaparkan.
- [ ] Cantumkan versi dependency installed yang kompatibel dalam requirements.txt; dokumentasikan setup dan DATABASE_URL. Jangan menginstal paket baru jika dependency sudah tersedia.
- [ ] Tambahkan routing GET database pada webui.py sebelum routing lokal; pertahankan Host/Origin, localhost binding, fungsi generator dan perubahan pengguna. Tidak menambahkan endpoint POST DB.
- [ ] Uji query pada PostgreSQL lokal terisolasi dengan fixture paket kosong, pinned v1 ketika v2 tersedia, original/varian, serta akun yang dapat membaca tabel tanpa role compute. Verifikasi transaksi read-only menolak mutasi pada fixture; jangan menjalankan query mutasi di database pengguna.
- [ ] Jalankan seluruh `python -B -m unittest discover -s tests -v` dari variant_gen; semua lulus. Commit hanya file/diff task sendiri jika aman terhadap perubahan pengguna.

### Task 2: UI sumber database

**Consumes:** endpoint/envelope Task 1. Render pinned package item dahulu; opsi anggota keluarga menampilkan kind, versionNumber, ID dan parent asli yang tersedia.

- [ ] Perluas tes HTTP existing untuk HTML source selector dan endpoint read-only. Siapkan browser check pada server lokal; dataset fixture mencakup paket kosong, historical pinned version, varian, konten dengan markup, no-config, safe DB failure.
- [ ] Tambahkan dua tab utama Service AI/DB Utama, panel paket dengan filter aktivitas/nama/status/demo, Muat ulang, pagination; panel detail item/family hanya-baca. Pertahankan UI dan filter katalog lokal existing.
- [ ] Gunakan DOM textContent untuk konten/opsi/kunci/pembahasan/media metadata. Jangan render HTML database atau URL media aktif. Media ditampilkan sebagai metadata teks pada versi pertama.
- [ ] Lindungi edit config lokal sebelum source switch. Disable interaksi saat load; error tidak meninggalkan paket lama seolah baru; empty state tidak menawarkan Generate. Tombol generator/config hanya muncul pada mode lokal.
- [ ] Jalankan regresi Python dan browser checks: paket kosong, refresh menerima upload baru, pinned v1 tidak berubah saat v2 tersedia, lineage kosong jujur, DB failure tetap mengizinkan bank lokal, source switch menghormati edit belum disimpan, teks markup tidak dieksekusi, keyboard/label/loading dapat digunakan.
- [ ] Perbarui README: install dependency, isi .env, jalankan webui.py; tanpa prasyarat view baru atau migration. Akun membutuhkan SELECT sesuai query; aplikasi tidak mengubah hak akses. SSH tunnel untuk VPS; interface untuk operator, bukan siswa.
- [ ] Periksa git diff kedua repo, git check-ignore .env, serta secret-free contoh environment. Jangan menjalankan koneksi live sebelum pengguna mengisi credential. Laporkan hasil tes lokal dan batas live secara eksplisit.

## Handoff

Template environment sudah disiapkan atas instruksi pengguna. Instruksi terbaru menghapus rencana view/migrasi dan pembatasan role compute. Tahap ini hanya membaca, tanpa program create/update/delete. Implementasi aplikasi dimulai setelah review plan; rekomendasi eksekusi inline karena backend dan UI memakai kontrak yang sama. Tidak melakukan parallel agent work tanpa pilihan eksplisit pengguna.
