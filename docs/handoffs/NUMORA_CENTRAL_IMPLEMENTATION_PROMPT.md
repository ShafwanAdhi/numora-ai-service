# Prompt implementasi di Numora pusat

Salin ke chat yang bekerja di `D:\Dev\Numora`. Commit service/kontrak/fixture/tes:
`3a0f21eb8b59f45f836efc74b2ef985c31bdb188` di repo `D:\Dev\numora-ai-service`.
Handoff ini ditambahkan pada commit dokumentasi berikutnya. Baseline
`ba7af91d0221d7dfa0f72056a8f185b856d82c86` belum berisi service ini.

```text
Implementasikan integrasi generator v1 di repo Numora pusat sampai alur Admin
Generate → preview → Simpan draft bekerja dengan service Python nyata.

Source service/kontrak/fixture/tes telah tersedia pada commit
3a0f21eb8b59f45f836efc74b2ef985c31bdb188 repo D:\Dev\numora-ai-service.
Gunakan checkout yang juga berisi commit handoff dokumentasi sesudahnya.

Baca AGENTS.md, urutan dokumen wajib, konteks produk/intake terkini, ADR-011,
VARIANT_IRT_DATABASE.md, measurement-contract.ts, measurement-handoff.ts,
dan D:\Dev\numora-ai-service\docs\handoffs\NUMORA_GENERATOR_INTEGRATION_V1.md.
Baca docs\audits\generator-service-v1.md serta schema/fixture pada
D:\Dev\numora-ai-service\contracts\generator-service-v1.

Target: Content Admin memilih original mapped, Generate, melihat kandidat,
kemudian klik Simpan draft. Kandidat compute disimpan saat generate, canonical
VARIANT DRAFT hanya setelah Simpan draft. Reuse renderer dan authorization
existing; audience Super Admin/Content Data Moderation. UI tidak meminta UUID/hash.

Jangan membuat ulang service Python atau memakai importer ORIGINAL existing
untuk varian. Cocokkan semantik JSON Numora, actual DB import guard, dan fingerprint
fixture. Digest DB jsonb::text berbeda dari content fingerprint compact JSON.
Canonical import mempertahankan payload kandidat persis.

Implementasikan mapping original/config dan approval main-owned, catalog mapped,
prepare/list/detail/retry, worker HTTP GENERATE_VARIANTS, acceptance artifact,
preview read-only dan Simpan draft atomik/idempotent. Prepare memin original,
config, rubric, context, seed dan target 1. Config register CLI berada pada
irt_compute.generator_configs. Approval tetap public/main-owned. Constraints
wave item: {serviceContract:'generator-service-v1',seed:<integer 1..1000000000>}.

Request/outbox/dispatch tetap compute v3. Admin prepare 202 setelah durable write.
Worker mengirim notifikasi berisi contractVersion/requestId/inputDigest/
dispatchGeneration saja ke POST /api/v1/compute/execute; timeout HTTP 45 detik.
GET /health/ready dan /api/v1/generators memakai Bearer token khusus server.
Respons service ID/status, bukan soal. Read kandidat dari DB untuk preview.

Service claim execution, generate subprocess, tulis run/kandidat/artifact dan
SUCCEEDED. Replay dispatch sama tidak generate lagi. FAILED/EXPIRED butuh dispatch
generation baru dengan input/seed sama. Bila koneksi putus, periksa DB sebelum
notif ulang. Pertahankan transport Redis CALIBRATE_TRYOUT; HTTP khusus generation.

MIGRASI FORWARD wajib: measurement_dispatch_guard existing 0018 hanya menerima
CALIBRATE_TRYOUT. Izinkan GENERATE_VARIANTS juga dengan guard active Admin,
sequence/current dispatch/retry/fencing tetap berlaku. Jangan mengedit migrasi
historis atau disable trigger. Reuse tabel existing; migrasi tambahan mapping/
idempotensi bila diperlukan tetap milik Numora. Main tidak mendapat write compute,
compute tidak mendapat write canonical. Runtime bukan owner/service_role.

Main menerima hanya current SUCCEEDED execution dengan digest/approval sah,
sealed artifact GENERATE_VARIANTS sequence 1, tepat satu declared candidate,
konten/fingerprint/source/rubric/lineage valid. Accept sebelum canonical import.
Preview tidak membuat attempt/scoring/XP/exposure/evidence IRT. CONTENT_VALID
bukan READY/distribution/academic equivalence.

Simpan draft: lock candidate/keluarga, dedupe fingerprint konten per keluarga,
buat question_variants kind VARIANT dengan original_variant_id, versi DRAFT
memin parent/rubric serta isi payload persis, candidate_imports atomik. Repeated
save mengembalikan UUID existing. Koreksi selanjutnya membuat versi baru.

Cakupan v1: PG/MCMA/KATEGORI teks, kategori custom dan LaTeX, satu kandidat/request.
Stok manual, media aktif, paket otomatis, kalibrasi/publikasi tidak termasuk.
Pertahankan histori assessment dan ketentuan produk terkini. Jangan mengarang
mapping Curriculum, rubric, approval atau context.

Feature flag default false. Uji PostgreSQL lokal terisolasi dengan restricted
main/compute logins dan service Python nyata. Service harness memakai perluasan
dispatch guard TEST ONLY; buat migrasi pusat yang benar. Perluas tes ke API/UI
Admin nyata: auth/subrole, wrong source/config/rubric, stale dispatch/digest,
parallel calls, timeout/crash/expiry/retry, lost HTTP response, revoke approval,
rollback, undeclared artifact candidate, tampered payload, foreign lineage,
duplicate save/content, tidak ada publication/XP/history rewrite. Jalankan
contracts/generated types, lint/typecheck/build dan regresi IRT/content relevan.
Tes tidak menarget shared/cloud DB. SQL fixture service bukan bukti UI selesai.

Laporkan perubahan, hasil tes, migrasi, serta prasyarat activation Staging.
Selesaikan implementasi lokal dan hasil reviewable sebelum activation shared.
```
