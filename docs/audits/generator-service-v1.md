# Verifikasi generator-service-v1

7 Oktober 2026. Repo service `D:\Dev\numora-ai-service`, baseline
`ba7af91d0221d7dfa0f72056a8f185b856d82c86`. Tes menggunakan Python .venv,
Node24.14.1, dependency lock service, dan migrasi resmi checkout Numora lokal.
Tidak ada shared/cloud database yang dipakai atau diubah.

## Hasil

| Pemeriksaan | Hasil |
|---|---|
| Content/adapter/mapping/process (`test_content.py`) | 9 tes, PASS |
| FastAPI/auth/body/error/catalog (`test_api.py`) | 4 tes, PASS |
| PostgreSQL role/guard/HTTP (`check_postgres.py`) | 11 tes, PASS; run final15.783s |
| Legacy engine/CLI/workbench (`variant_gen/tests`) | 178 tes, PASS;152.854s |
| TypeScript helper | 7 fingerprint +4 candidate fixtures cocok |
| Canonical/digest aktual Numora +Ajv | 7 fingerprint cocok;4 schema dikompilasi;4 kandidat valid |
| Dependency closure (`pip check`) | No broken requirements found |
| Whitespace (`git diff --check`) | PASS |

Total unit/integration/regression **202 tes lulus**. Fixture lintas bahasa
merupakan pemeriksaan tambahan, bukan tambahan jumlah unittest.

Perintah lengkap dan prasyarat ada di
[handoff](../handoffs/NUMORA_GENERATOR_INTEGRATION_V1.md). Artifact kontrak dapat
direproduksi dengan `python -B tests/service/build_contract_artifacts.py`;
fixture sintetis TEST ONLY tidak membutuhkan atau membuat data canonical nyata.

## Bukti lokal

Harness membuat cluster temporary yang hanya bind127.0.0.1, database
`generator_test_<UUID>`, menjalankan integrated migrator Numora, dan membuat
dua login non-owner yang mewarisi numora_main_runtime/numora_irt_runtime.
Cluster dimatikan dan dihapus sesudah tes.

Run final menghasilkan kandidat, acceptance dan canonical VARIANT DRAFT dengan:

```json
{
  "parentOriginalVersionId": "54392721-d174-4216-8fd2-e9a01217d15a",
  "candidateId": "7b19e5b8-c8ba-4fa1-ae14-13aab93dc5ac",
  "draftVersionId": "8286dfa8-4dc2-4a0c-9552-2b3cf3990c25"
}
```

Semua ID ini **TEST ONLY**, sudah dihapus bersama cluster. Assertion memastikan
status DRAFT, parent tepat, Simpan draft berulang menghasilkan ID existing dan
hanya satu VARIANT pada keluarga fixture. Versi ORIGINAL tetap satu.

Tes HTTP menjalankan Uvicorn nyata di loopback, dengan engine spawn nyata dan
persistence PostgreSQL. Hasil commit kemudian dibaca kembali oleh repository/
executor baru: simulasi restart/respons yang tidak diterima pemanggil menghasilkan
execution/candidate yang sama. Tes tidak memutus TCP secara fisik setelah commit.

## Cakupan penolakan dan recovery

- PG/MCMA/kategori boolean/custom, kategori source ID stabil, LaTeX LF serta
  fingerprint UTF-16 ordering. Tidak mengklaim QA visual renderer UI pusat.
- Manifest/hash/mapping/sumber salah ditolak; snapshot config DB tetap dipakai
  saat config latest lokal tidak tersedia. Wrong rubric/config status/target
  diperiksa validator task; wave target dibekukan oleh guard DB nyata.
- Tanpa token/injected fields/duplicate JSON keys/oversized body/bukan JSON
  ditolak. Exception/token tidak dikembalikan kepada caller.
- Claim bersamaan hanya satu execution, replay dispatch tanpa kandidat kedua,
  digest/dispatch stale ditolak. FAILED/EXPIRED butuh dispatch baru.
- Timeout subprocess, heartbeat callback gagal, child cleanup, expiry, fencing
  salah dan stale lease tidak menghasilkan kandidat. Crash hidup disimulasikan
  lewat claim tanpa finish lalu expiry; bukan fault injection OS/service manager.
- Approval dicabut sebelum persistence: gagal. Exception setelah candidate insert
  sebelum artifact: transaksi rollback tanpa kandidat parsial.
- Compute tidak dapat membaca users atau menulis canonical/DDL; main tidak bisa
  menulis config compute. Owner atau compute login dengan grant UPDATE canonical
  tambahan ditolak readiness.
- Import sebelum acceptance, payload berubah, parent asing, kandidat yang tidak
  dideklarasikan artifact ditolak oleh guard migrasi canonical nyata. Sealed
  candidate tidak bisa diubah. SQL fixture acceptance/import hanya pengujian
  kontrak, bukan implementation API Admin pusat.

## Batas sebelum activation

Guard dispatch canonical0018 saat ini hanya menerima CALIBRATE_TRYOUT. Tes
pertama membuktikan penolakan GENERATE_VARIANTS; sesudah itu harness memperluas
function **hanya di database disposable TEST ONLY**, dengan guards lainnya tetap.
Tidak ada migrasi/trigger checkout pusat atau shared environment yang diedit.
Numora wajib membuat migrasi forward sebelum activation generation HTTP.

Pekerjaan pusat yang belum diverifikasi: actual Admin auth/subrole endpoints,
prepare/list/status/retry/outbox worker HTTP, full acceptance policy,
renderer/preview UI, API idempotensi dan dedupe fingerprint antar kandidat dalam
keluarga, audit attempt/XP/IRT keseluruhan, serta e2e dua repo setelah migrasi.
Staging/private TLS/reverse proxy/systemd belum dideploy. Feature flag default
false. Keseluruhan tahap produk belum selesai sampai UI pusat terbukti bekerja.

Perubahan bank/CLI/workbench dari sesi lain tetap dipertahankan. Rename
`.env.example` menjadi `.env copy.example` bukan bagian integrasi service;
gunakan `service.env.example` untuk tambahan env compute tanpa menimpa .env.
