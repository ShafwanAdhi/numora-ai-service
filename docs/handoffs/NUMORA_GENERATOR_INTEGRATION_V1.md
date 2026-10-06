# Handoff integrasi generator Numora v1

7 Oktober 2026 — **ENGINEERING IMPLEMENTATION: service Python.**

Repo: `D:\Dev\numora-ai-service`. Commit source service, kontrak, fixture dan tes:
`3a0f21eb8b59f45f836efc74b2ef985c31bdb188`. Handoff/indeks dokumentasi
ditambahkan dalam commit berikutnya. Baseline sebelum integrasi:
`ba7af91d0221d7dfa0f72056a8f185b856d82c86` (tidak berisi service ini).

## Target dan artifact

Admin memilih original → Generate → preview → **Simpan draft**. Generate menyimpan
kandidat compute; Simpan draft di pusat membuat varian canonical DRAFT. Tidak
membuat keluarga ORIGINAL baru, scoring, kalibrasi, paket atau publikasi.

V1 menghasilkan satu kandidat/request: PG, MCMA, KATEGORI teks, LaTeX dan label
kategori khusus. Stok manual/media aktif belum dilayani execution. Engine, CLI,
dan workbench existing tetap stateless. Tidak ada migrasi atau shared Supabase
yang diubah oleh implementasi ini.

Artifact:

- `numora_service/`: API, adapter, config registration, repository, executor.
- `contracts/generator-service-v1/`: notification/response/candidate/registration
  schemas, OpenAPI, fingerprint dan candidate fixtures.
- `requirements-service.lock`, `requirements-service-test.txt`: dependencies pin.
- `tests/service/`: API/content, fingerprint Node.js, PostgreSQL lokal.
- `deploy/numora-generator.service`, `service.env.example`: contoh operasional.
- `docs/audits/generator-service-v1.md`: bukti dan batas verifikasi.

Kontrak HTTP **generator-service-v1**; notifikasi/artifact compute tetap **v3**.
Kontrak importer JSON existing tidak diganti.

## API dan error

| Method/path | Hasil |
|---|---|
| GET `/health/live` | Status proses, tanpa token |
| GET `/health/ready` | Bank/config/stok, role/principal/views compute; token wajib |
| GET `/api/v1/generators` | Katalog lokal/provenance; token wajib |
| POST `/api/v1/compute/execute` | Execute/replay current authorized dispatch; token wajib |

Header `Authorization: Bearer <NUMORA_GENERATOR_TOKEN>`. POST JSON maksimal
16 KiB termasuk chunked body. Browser memanggil NestJS, bukan service ini.
Tidak ada endpoint edit config atau browser DB di API produksi ini.

Body sesuai notifikasi compute v3 existing, tambahan field ditolak:

```json
{
  "contractVersion": 3,
  "requestId": "00000000-0000-4000-8000-000000000001",
  "inputDigest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "dispatchGeneration": 1
}
```

ID/hash contoh adalah **TEST ONLY**. Seed, config, konten dan mapping tidak
dikirim lewat body ini; service membacanya dari view main-owned.

Respons: `serviceContract`, `requestId`, `dispatchGeneration`, `executionId`,
`status`, `failureCode`, `artifactId`, `artifactDigest`, `candidateIds`.
HTTP 202 untuk RUNNING; 200 untuk SUCCEEDED/FAILED/EXPIRED. Status gagal yang
dibaca ulang tetap HTTP 200; pusat membaca field status. Payload/kunci tidak
ditampilkan di respons transport; pusat membaca kandidat DB untuk preview.

Problem JSON: `type`, `title`, `status`, `code`; tidak mengirim exception mentah.
Kode penting: UNAUTHORIZED (401), INVALID_NOTIFICATION (422), JSON_REQUIRED (415),
BODY_TOO_LARGE (413), STALE_DISPATCH/INPUT_DIGEST_MISMATCH/CONFIG_PIN_MISMATCH/
SOURCE_MAPPING_MISMATCH/SOURCE_CONTENT_MISMATCH/CONFIG_APPROVAL_MISMATCH/
RUBRIC_MISMATCH/STALE_EXECUTION (409), MEDIA_NOT_SUPPORTED/UNSUPPORTED_REQUEST/
UNSUPPORTED_TARGET_COUNT (422), GENERATION_TIMEOUT (504), GENERATOR_DISABLED/
GENERATOR_NOT_CONFIGURED/UNSAFE_COMPUTE_ROLE/COMPUTE_DATABASE_ERROR (503).

Katalog memperlihatkan `generator`, `stock`, `held`, `unavailable`. Katalog lokal
bukan daftar generator yang telah dipetakan ke DB: pusat menyaring berdasarkan
mapping/approval. Jumlah mengikuti asset checkout, bukan angka hardcoded.

## Registrasi original/config

Prerequisite: original canonical dan keluarga, rubric SEALED, measurement context
yang sah. Tidak menebak mapping kurikulum dari angka ID lokal.

Manifest registration memuat `serviceContract` dan `items` dengan:
`questionExternalId`, `configVersion`, `parentQuestionVersionId`, `familyId`,
`rubricVersionId`, `contextId`. Semua UUID canonical disediakan Numora.

```powershell
.\.venv\Scripts\python.exe -B -m numora_service.register mapping.json --dry-run
.\.venv\Scripts\python.exe -B -m numora_service.register mapping.json --apply --seal
```

Tanpa flag: dry-run membaca DB/hitung digest tanpa write. `--apply` membuat config
DRAFT; `--apply --seal` menyegel snapshot teknis. **SEALED bukan approval akademik.**
CLI tidak menulis public/approval/canonical. Seluruh batch atomik; replay identik
memakai row existing, identitas sama dengan isi berbeda ditolak. Jika ada revisi
sumber/rubric/context, registrasikan mapping baru sesuai provenance.

`generator_configs.parameters` berisi tepat:

- `serviceContract`, `questionExternalId`, `originalVersion`, `originalHash`;
- `parentQuestionVersionId`, `familyId`, `rubricVersionId`, `contextId`;
- `sourceFingerprint`, `configVersion`, `configHash`, `config` snapshot lengkap.

Identitas DB config mencakup source/context; versi config lokal bukan identitas
global. `curriculum_limits={}`: service tidak menyatakan approval batas tambahan.
Domain/constraints berasal dari snapshot dan harus direview pada approval Numora.
Digest registration dihitung memakai `irt_compute.payload_digest(parameters)`.
Output UUID/digest dipakai untuk main-owned configuration approval.

Kesamaan source membandingkan tipe, teks LF, urutan/ID opsi, kategori/label, kunci.
Kategori memakai ID canonical source. Explanation source harus lengkap tetapi
tidak masuk fingerprint kesamaan original; explanation varian berasal dari config.
Difficulty/rubric diwarisi source canonical; taxonomy tidak dibuat generator.

Request menggunakan snapshot DB; config terbaru di filesystem tidak mengubahnya.
Bank/ledger lokal tetap harus cocok versi/hash source yang dipin. Deploy bank baru
yang tidak cocok menahan request lama, bukan diam-diam mengganti original.

## Prepare dan execution

Pusat membuat authorized wave APPROVED/RUNNING, item dengan original/config/
context/approval pin, `target_count=1` dan constraints:

```json
{ "serviceContract": "generator-service-v1", "seed": 5 }
```

Seed dibentuk backend, integer 1..1.000.000.000, immutable selama retry.
Request `GENERATE_VARIANTS`, version 3, wave item dan configuration pins sah;
tidak memakai snapshot siswa. Prepare request/outbox/digest dan dispatch 1 atomik.

Service memvalidasi token, role/principal, latest dispatch/digest, wave/target,
sealed config + digest, mapping/sumber, approval scoped dan rubric. Claim memakai
advisory lock request, attempt, dispatch dan fencing existing. Dispatch yang telah
dipakai hanya membaca status: tidak generate dua kali.

Lease 60 detik; heartbeat 15 detik; subprocess generator dibatasi 30 detik.
Input/approval diperiksa kembali sebelum persistence. Satu transaksi menulis:

1. Generation run pin config/original/wave/execution.
2. Kandidat CONTENT_VALID dengan parent, payload dan provenance.
3. Artifact GENERATE_VARIANTS sequence 1, tepat satu candidateId.
4. Run/execution SUCCEEDED.

DB trigger menetapkan digest/sealed_at kandidat dan digest artifact. Provenance
run/candidate parameter_values: ID/hash/versi original/config, seed, drawsUsed,
valuesUsed. Tidak menambahkan provenance ke content payload.
CONTENT_VALID hanya validasi generator, bukan kesetaraan IRT/approval Curriculum.

Timeout menghentikan subprocess dan menandai FAILED jika lease sah. Crash dapat
meninggalkan RUNNING sampai expiry; replay menandai EXPIRED lalu membaca status.
Retry membutuhkan **dispatch generation baru dari main**, dengan input/seed sama.
HTTP putus setelah commit: replay mengembalikan UUID yang sama. Jika hasil commit
tidak diketahui, worker memeriksa DB; jangan membuat request/seed baru otomatis.
Timeout HTTP worker 45 detik. Main recheck approval saat acceptance/import;
approval yang dicabut sesudah generation tidak otomatis menyetujui kandidat.

## Payload dan hash

Payload sama persis dengan field `measurement_import_guard`:
`questionType`, `stem`, `optionsOrStatements`, `answerKey`, `explanation`, `media`,
`difficulty`, `rubricVersionId`, `contentFingerprint`.

Rich text `{text}`; collection `{options:[{id,content:{text}}],categories:[...]}`.
PG memakai `optionId`, MCMA `optionIds`, kategori `categoryByStatementId` lengkap.
Label kategori khusus tetap dipertahankan. V1 `media=[]`. UUID canonical bukan
record_id generator. Gunakan renderer/validator konten pusat existing.

Content fingerprint: SHA-256 UTF-8 compact JSON, key rekursif diurutkan dengan
UTF-16 JavaScript. Hash seluruh field payload kecuali contentFingerprint.
Domain hash berisi string/null/boolean/integer/list/object; float ditolak.
Integer harus aman lintas bahasa (abs <= 2^53-1). Ikuti fixture Python/TypeScript
yang diserahkan; helper siap pakai `fingerprint.ts`. Notifikasi menolak key JSON
duplikat dan bukan integer, termasuk 1.0 pada parsing Python.

Tiga hash berbeda:

- Hash source/config lokal existing: 16 karakter.
- Content/source fingerprint canonical: 64 karakter compact JSON.
- Digest DB: 64 karakter PostgreSQL jsonb::text, bukan compact JSON.

Jangan menghitung payloadDigest/artifactDigest dengan algoritma content fingerprint.
Jangan mengubah sealed payload ketika import; koreksi membuat versi berikutnya.

## Pekerjaan Numora pusat

1. **Migrasi forward dispatch guard:** guard 0018 masih membatasi CALIBRATE_TRYOUT.
   Izinkan GENERATE_VARIANTS dengan guard actor/sequence/current dispatch/retry
   tetap berlaku. Jangan mengedit migrasi historis atau menonaktifkan trigger.
2. Catalog mapped dan Admin prepare/list/detail/retry, Content Admin authorization,
   idempotensi, original/config/rubric/context/seed pin. API prepare mengembalikan
   202 setelah durable write. Reuse generation/request/outbox/dispatch existing.
3. Worker transport HTTP khusus GENERATE_VARIANTS, outbox recovery durable. Jalur
   CALIBRATE_TRYOUT/Redis tetap berlaku. Error pre-claim ditampilkan sebagai input/
   transport failure, tidak mengarang execution FAILED. Perubahan pin perlu request baru.
4. Acceptance current SUCCEEDED execution dengan digest/version/kind/sequence,
   SEALED artifact, tepat satu declared candidate, approval, konten/fingerprint/
   lineage/rubric. Main menerima execution tanpa READY/distribution otomatis.
5. Preview kandidat read-only, renderer existing; tidak membuat attempt, scoring,
   XP, exposure atau evidence IRT. Jangan menggunakan importer ORIGINAL existing.
6. Simpan draft: lock candidate/keluarga, dedupe content fingerprint per keluarga,
   buat VARIANT + versi DRAFT + candidate_imports atomik. Isi/rubric/parent persis
   kandidat. Repeated save mengembalikan UUID existing. Foreign/undeclared ditolak.
7. UI Generate/status/retry/preview/save dan feature flag default false. Publikasi
   tetap lewat lifecycle existing pada tahap berikutnya.

Aturan Tryout/intake diperbarui 7 Oktober; gunakan validator/konteks produk aktif,
bukan persyaratan metadata lama. V1 compute tetap membutuhkan canonical source,
rubric dan context sah; context TRYOUT existing memin batch. Jangan mengarang
context pengganti hanya untuk melewati constraint.

## Setup, test dan activation

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-service-test.txt
.\.venv\Scripts\python.exe -B -m numora_service --port 8770
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/service -p test_content.py -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/service -p test_api.py -v
node tests/service/check_fingerprints.mjs
node tests/service/check_numora_contract.mjs
.\.venv\Scripts\python.exe -B tests/service/check_postgres.py
.\.venv\Scripts\python.exe -B -m unittest discover -s variant_gen/tests -v
```

Harness memerlukan NUMORA_REPO_PATH (default D:/Dev/Numora), built migrator
packages/database/dist/integrated-migrations.js, Node, dan POSTGRES_BIN atau
embedded PostgreSQL repo pusat. Membuat cluster temporary localhost sendiri,
menjalankan migrator canonical, role main/compute terpisah, lalu cleanup cluster
miliknya. Tidak membaca .env atau memakai shared DB.
Checker lintas repo juga memerlukan built API content-import.validation.js,
Ajv/ajv-formats existing repo pusat. Helper TypeScript dijalankan dengan Node 24;
repo pusat dapat mengompilasi helper menggunakan pipeline TypeScript existing.

Harness membuktikan guard asli menolak generation, lalu memperluas guard lokal
**TEST ONLY** untuk connected test. Itu bukan production migration atau bukti UI
pusat. Hasil tes final/batasnya ada di audit terpisah.

Environment service: NUMORA_GENERATOR_ENABLED=false default, token random minimal
32 karakter, COMPUTE_DATABASE_URL, COMPUTE_SERVICE_PRINCIPAL_ID. Merge contoh
service.env.example tanpa menimpa .env existing. DATABASE_URL tetap browser lama.

Login compute non-owner tanpa SUPERUSER/CREATEDB/CREATEROLE/BYPASSRLS, hanya
numora_irt_runtime, tanpa CREATE schema/write canonical; enabled principal.
Main login terpisah. Remote TLS verify-full dan CA terpercaya lewat sslrootcert.
Direct connection atau session pooler sesuai jaringan; prepared statements
dimatikan. [Dokumentasi koneksi Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres).

Contoh systemd bind localhost 8770; worker mengakses lewat reverse proxy TLS atau
jaringan privat. EnvironmentFile server 0600; token tidak masuk frontend/Git/log.
Access log HTTP dimatikan. Aktivasi menunggu migrasi pusat, role/principal/token,
mapping/approval sah, dan tes kedua repo. Health/live bukan readiness activation.
Belum ada deploy atau aktivasi shared pada pekerjaan ini.

## Runbook deployment

1. Buat user OS `numora-generator`, checkout revision yang direview di
   `/opt/numora-ai-service`, Python >=3.11 dan `.venv`; instal
   `requirements-service.txt` (lock lengkap, tanpa test dependencies).
2. Siapkan login compute/principal melalui owner migrasi Numora. Simpan env pada
   `/etc/numora-generator.env` permission 0600 milik root; systemd membaca sebelum
   drop privilege. Pastikan role tidak memiliki write tabel public atau DDL.
3. Review bank/config yang dipin dan manifest operator. Dry-run, apply/seal lalu
   approval resmi main. Uji tiga format fixture terisolasi dahulu; jangan import
   seluruh bank atau membuat approval/UUID canonical otomatis.
4. Pasang unit `deploy/numora-generator.service`, reload systemd dan start dengan
   flag default false. `/health/live` harus 200; ready masih 503 selama disabled.
5. Setelah backend/worker/acceptance/UI pusat dan migrasi sudah diuji, isi flag
   true dan restart unit. Health/ready dengan Bearer token harus 200. Aktifkan
   feature flag pusat, lalu lakukan satu generate/preview/save DRAFT Staging.
6. Worker memakai token server, timeout45s, TLS/private routing. Service tetap
   bind localhost. Reverse proxy membatasi body16KiB, timeout minimal45s dan
   akses jaringan worker; jangan forward token/soal ke access logs/frontend.
7. Monitor log `numora.generator`: request_id, execution_id, status/failure_code,
   duration_ms saja. Replay/restart tidak mengganti execution terminal. FAILED/
   EXPIRED dipulihkan lewat retry dispatch main, bukan SQL edit compute.
8. Rollback: matikan flag pusat dan service, pertahankan row compute/canonical
   untuk audit; deploy revision source yang cocok pin. Jangan hapus histori atau
   mengubah sealed payload untuk melewati guard.
