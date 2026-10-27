# Penggantian isi Tryout lokal ke database sistem

Tanggal: 27 Oktober 2026. **ENGINEERING DECISION — instruksi pengguna:**
“ganti 30 soal tryout yang ada di database saat ini dengan 30 soal try out yang
ada di lokal. push ke database”. Penggantian diterapkan pada database development
yang dipakai checkout sistem, dengan target dan alamat koneksi yang dipin.

## Hasil

- Paket tetap **`f757ccab-8f74-4846-954c-ffcd7753ffc5`**, family
  `NUMORA-AI-TRYOUT-1`, versi paket 1.
- Nama menjadi **Tryout 1 - Varian lokal seed 1 (30 soal)**.
- Content revision berubah **1 → 2**, status tetap **DRAFT**.
- 30 referensi soal sesuai bundel seed 1: **27 VARIANT + 3 ORIGINAL konseptual**.
- Format: 18 PG, 6 MCMA, 6 Kategori.
- Lima PNG varian di R2 terverifikasi dan direferensikan pada versi soal yang
  sesuai. Byte yang didownload melalui signed GET cocok dengan hash lokal.
- Tidak membuat keluarga soal baru atau menyamarkan varian sebagai original.
  Seluruh varian mempunyai parent original dan provenance generator/impor.
- Original versi lama, riwayat attempt/hasil/XP dan paket Tryout lain tetap utuh.
  Paket target tidak memiliki attempt pada saat penggantian.
- Tidak memublikasikan paket, mengubah schema, kontrak compute, atau deployment.

Sumber adalah `docs/audits/2026-10-27-tryout-image-variants/stage-5/bundle-s1/`,
bundle ID `083125b756f4107d143ade49f3ccd824f3be1fdb6ab1ed7d9a70eff6c8e92162`.
Yang diganti adalah susunan paket DRAFT tersebut, bukan seluruh paket Tryout
lain dalam database atau byte original yang diperlukan untuk histori/generator.

## Verifikasi

- Enam tes operator memeriksa sumber, opsi/kunci yang berubah, pemetaan gambar
  silang, target salah dan kompatibilitas identitas keluarga pada Admin.
- Dry-run transaksi penuh lulus lalu di-rollback sebelum penerapan nyata.
- Service `ContentPackagesService.detailWithin` membaca seluruh 30 soal dan
  lolos validasi simpan DRAFT/media. Provenance tersedia untuk review Admin.
- Pemeriksaan hash baris lama dijalankan di dalam transaksi sebelum commit dan
  setelahnya; perubahan yang diizinkan hanya paket target dan susunan itemnya.
- `--verify` lulus, termasuk lima download R2 nyata.
- Pemeriksaan Python/psycopg read-only terpisah mencocokkan teks, seluruh opsi,
  kunci, pembahasan, format, urutan, hash gambar dan lineage dengan bundel lokal.
- Pengulangan apply memakai varian yang sama dan tidak menaikkan revisi lagi.

Bukti: `preflight.json`, `dry-run-result.json`, `apply-result.json`,
`verify-result.json`, `independent-source-verification.json`, `verification.json`.
Backup metadata paket/susunan lama dan hash baris disimpan pada direktori lokal
yang diabaikan Git `.scratch/tryout-local-replacement/`; tidak berisi token atau
signed URL dalam laporan publik.

## Adapter dan keputusan integrasi

Operator sekali jalan memakai service upload/completion media NestJS dan
`ContentPackagesService.update` untuk pergantian susunan paket. Penyimpanan
27 versi VARIANT dan provenance berlangsung dalam transaksi yang sama.
Penolakan media pada compute service v1 tidak dinonaktifkan; ini bukan aktivasi
pipeline generator otomatis atau persetujuan akademik/publikasi.

Review independen menemukan dua isu sebelum apply, keduanya diperbaiki:

1. Admin merekonstruksi externalId dari identitas keluarga original. Karena itu
   aset database/receipt memakai externalId original yang sama dengan keluarga,
   dengan assetId baru berbasis hash bundel. Marker baru hanya mengikat gambar;
   teks akademik tetap sama dengan lokal.
2. Endpoint review membutuhkan provenance `content_import_versions`. Dibuat
   satu laporan impor lokal yang jujur menyebut `LOCAL_GENERATOR_VARIANTS`, serta
   27 provenance versi pada identitas keluarga existing. Kind versi tetap VARIANT.

Laporan impor mengikuti mekanisme immutable existing: dimulai dengan report
kosong dan disegel satu kali dalam transaksi. Tidak ada trigger/guard dimatikan.

Pada preflight awal, lima aset beridentitas LTV sudah sempat diverifikasi, lalu
tidak dipakai setelah penyesuaian identitas keluarga untuk Admin. Lima aset final
memakai identitas yang benar; aset preflight tidak direferensikan paket dan tidak
dihapus otomatis. Laporan receipt mempertahankan jejak keduanya; cleanup orphan
tetap pekerjaan rekonsiliasi terpisah, bukan penghapusan historis.

Script utama: repo Numora `apps/api/scripts/replace-local-tryout.cjs`.
Persiapan/verifikasi mandiri: `tools/prepare_tryout_local_replacement.py` dan
`tools/verify_tryout_local_replacement.py` pada repo AI. Tidak commit/push Git.
