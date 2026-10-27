# Impor Tryout original lokal dan gambar R2

Pekerjaan dimulai 26 Oktober 2026. Waktu upload aktual tersedia pada `verifiedAt` setiap receipt UTC.

**ENGINEERING DECISION — instruksi pengguna:** periksa relasi R2/gambar, masukkan Tryout lokal ke database, dan siapkan rencana penyelarasan penyajian gambar.

**Persetujuan eksplisit:** “Unggah 5 gambar dan impor 30 soal sebagai DRAFT”. Tidak ada persetujuan Publish atau perubahan paket/hasil lama.

## Hasil

| Item | Hasil |
|---|---|
| Target | Database development yang sudah dikonfigurasi bersama kedua repo |
| Paket | `f757ccab-8f74-4846-954c-ffcd7753ffc5` |
| Family / versi paket | `NUMORA-AI-TRYOUT-1` / 1 |
| Namespace sumber | `NUMORA_AI_TRYOUT_1` |
| Status | **DRAFT**, non-demo, belum dipublikasikan |
| Original | **30**: 18 PG, 6 MCMA, 6 Kategori |
| Distribusi bab | Bab 1: 8, Bab 2: 8, Bab 3: 7, Bab 4: 7 |
| Gambar | **5 PNG VERIFIED**, total 825.624 byte |
| Lokasi gambar | Bab 3 soal 2/3/4/6; Bab 4 soal 5 |
| Jadwal rilis/tutup | Belum ditetapkan; keduanya null |
| Hasil generator/stok varian yang diimpor | **0** |

Semua soal adalah original efektif dari bank lokal, termasuk revisi ledger yang sudah ada. Opsi, kunci, label kategori, pembahasan dan provenance dipertahankan. Lima stimulus ditambah marker `[[asset:diagram-1]]` pada posisi gambar STEM; file bank lokal tidak diubah.

## Hubungan R2 dan database

R2 menyimpan byte PNG. Database menyimpan receipt VERIFIED dan manifest pada `question_versions.media`: ID aset, penempatan, bucket, object key, SHA256, MIME, ukuran dan alt text. Database tidak menyimpan signed URL/base64.

Upload memakai layanan existing: reservasi idempotent → signed PUT ke `_pending` → verifikasi byte/ukuran/MIME/hash → penyalinan server ke key final → receipt VERIFIED. Key final:

```text
question-media/{localQuestionId}/v1/diagram-1-{sha256}.png
```

Kelima hash juga sudah ditemukan pada impor lain, tetapi receipt lama tidak dipakai lintas identitas soal. Operasi ini membuat lima receipt yang cocok dengan ID soal lokal. Aset lama tidak ditimpa/dihapus. Objek sementara mengikuti pipeline existing; skrip ini tidak mengubah lifecycle/retensi bucket.

Flag upload di `.env` tidak diubah. Izin upload diaktifkan hanya pada konfigurasi proses operator yang telah disetujui. Pembacaan signed GET existing tidak bergantung pada flag upload.

## Impor dan histori

Impor memakai `ContentPackagesService` dan `ContentImportService` Numora, dengan operator Content Admin development yang sudah ada dan diverifikasi ACTIVE. Tidak menulis ulang aturan domain melalui SQL manual, tidak mengubah skema, dan tidak memanggil Publish.

Sebelum commit, satu transaksi lengkap dijalankan lalu di-rollback. Commit sebenarnya membuat satu paket baru dan 30 keluarga/versi baru secara atomik. Semua lima receipt harus siap sebelum paket diimpor. Idempotency key terikat pada isi; pemanggilan ulang mengembalikan paket/versi yang sama.

| Data | Sebelum | Sesudah |
|---|---:|---:|
| Keluarga original Tryout database | 300 | 330 |
| Paket Tryout database | 13 | 14 |
| Paket Tryout PUBLISHED | 7 | 7 |
| Paket Tryout DRAFT | 6 | 7 |
| Receipt media VERIFIED | 50 | 55 |

Hash baris terdahulu pada keluarga soal, varian, versi, paket/item, attempt/item/jawaban, XP, identitas/versi/laporan impor dan receipt media dipertahankan. Snapshot ID/hash sebelum operasi berada pada `.scratch/tryout-database-r2/before.json` yang diabaikan Git; digest snapshot dipin di preflight. Paket, jawaban dan hasil lama tidak diganti.

## Verifikasi

- Validasi kontrak 30 soal dan hubungan 5 file/marker/hash sebelum write.
- Target development dipatok pada fingerprint alamat database yang sudah direview; mode write menolak baseline/preflight yang hilang atau berubah.
- Pencocokan isi/opsi/kunci/kategori/pembahasan/media, urutan 1–30 dan DRAFT pada transaksi impor.
- Verifikasi independen Python membandingkan 30 baris database dengan loader original lokal, bukan hanya membandingkan payload impor dengan dirinya sendiri.
- Lima signed GET nyata berhasil diunduh kembali dan hash byte cocok dengan PNG lokal.
- Repeat importer dalam transaksi dan pemanggilan ulang `--apply` setelah commit tidak menambah duplikasi.
- 3 tes operator lulus; 16 tes existing terkait storage R2, upload media dan validasi impor lulus. Build API, lint dan formatting file baru lulus.
- Browser/login siswa dan deployment tidak diuji. Paket DRAFT ini memang belum muncul pada Tryout siswa. Uji akses siswa dilakukan setelah proses review/Publish yang terpisah.

## Rencana penyajian gambar

Alur yang sudah tersedia: item attempt memin UUID versi soal → NestJS memeriksa hak akses dan fase WORK/REVIEW → mengambil object key versi tersebut → memberi signed GET → `AssessmentRichText` merender marker gambar.

Rencana lanjutan menggunakan pipeline itu, bukan membuat service sinkronisasi baru. Fokusnya: pengikatan versi receipt, pemeriksaan objek menjelang Publish, renewal URL kedaluwarsa, status error gambar, pengujian histori/IRT gate, dan rekonsiliasi read-only. Gambar original tidak otomatis boleh dipakai pada varian yang mengubah angka/geometri.

- [Design dan alur DB/R2](../../../../Numora/docs/superpowers/specs/2026-10-26-tryout-r2-database-sync-design.md)
- [Implementation plan task demi task](../../../../Numora/docs/superpowers/plans/2026-10-26-tryout-r2-database-sync.md)

**PROPOSED:** task lanjutan belum diimplementasikan oleh pekerjaan ini. Review akademik, penetapan waktu rilis dan Publish tetap tindakan terpisah.

## Berkas bukti dan reproduksi

- [Ringkasan](summary.json)
- [Ringkasan pengujian dan hash skrip/artifact](verification.json)
- [Payload sumber dan pemetaan gambar](import-input.json)
- [Preflight dan digest baseline](preflight.json)
- [Lima receipt VERIFIED](media-receipts.json)
- [Simulasi rollback](dry-run-result.json)
- [Commit dan pemetaan UUID versi](apply-result.json)
- [Verifikasi setelah commit](verify-result.json)
- [Verifikasi independen terhadap original lokal](independent-source-verification.json)
- [CSV soal lokal → versi database](question-database-map.csv)

Skrip: repo AI `tools/prepare_tryout_database_import.py`, repo utama `apps/api/scripts/import-local-tryout.cjs` dan tesnya. Mode `--check`, `--upload`, `--dry-run`, `--apply`, dan `--verify` memisahkan pemeriksaan/upload/commit. Jalankan pada environment development yang tepat; jangan mengganti namespace atau input untuk mengakali pemeriksaan idempotensi.

```powershell
# Root repo utama, verifikasi read-only terhadap paket yang sudah diimpor:
node --env-file=.env apps/api/scripts/import-local-tryout.cjs --verify
node --test apps/api/scripts/import-local-tryout.test.cjs
```
