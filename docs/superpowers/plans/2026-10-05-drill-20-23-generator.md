# Drill Paket 1 Indikator 20–23 Implementation Plan

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


> **For agentic workers:** REQUIRED SUB-SKILL: gunakan superpowers:executing-plans untuk eksekusi inline setelah pengguna mereview plan. Checkbox mencatat langkah. Plan ini belum mengimplementasikan produk.

**Goal:** Generator lokal indikator20–23 terhubung dari original sampai snapshot
dan UI, dengan audit seluruh120 soal serta status jelas untuk konten tertahan.

**Architecture:** Tambah satu bank Drill terpisah pada loader workspace existing;
pakai config per soal dan engine existing. Perluasan hanya untuk status source,
label kategori, dan pemakaian metadata di UI. Tidak membangun generator/paket baru.

**Tech Stack:** Python stdlib CSV/JSON/Fraction/statistics/Counter/hashlib/unittest,
HTML/CSS/JS existing. Tidak menambah dependency.

**Spec:** [Rancangan dan keputusan sumber](../specs/2026-10-05-drill-20-23-generator-design.md).
**Source inventory:** [120 blok source](../specs/2026-10-05-drill-20-23-source-inventory.json).
**Status:** PROPOSED; implementasi menunggu review plan, koreksi akademik belum disetujui.

## Global Constraints

- Target DRILL Paket1, bukan Tryout; package_id `drill-1`.
- Source SHA-256 `2129f33e8ecc524e4c489b668798e8db0393f4b01348bf964cf1a8d420160575`.
- 120 original: 60 PG,36 MCMA,24 KATEGORI; empat indikator×tiga level×sepuluh.
- Nomor source1–30; ID lokal nomor1–10 per level. Cognitive source mixed label dipertahankan.
- Level4–5 belum tersedia; tidak membuat original pengganti agar blueprint terlihat lengkap.
- Tidak mengakses DB/SQL, mengubah Numora, mempublikasikan soal, atau menghitung IRT/scoring.
- Utamakan config/loader/format mixed existing; tidak membuat importer DOCX generik atau120 fungsi Python.
- Raw source dipertahankan; source bermasalah HOLD sampai koreksi direview, revisi lewat ledger.
- `same_answer_as_original` global tetap; shuffle bukan variasi substantif.
- ACTIVE diuji target20 unique pada seeds1..200; kekurangan dicatat perID, bukan ditutup dengan klaim lint lulus.
- Tes menulis ke temp stores/configs; legacy Drill/Tryout/config/snapshot pengguna tidak ditulis ulang.
- Satu writer lokal; tidak menjanjikan transaksi/concurrent writers baru.

## Review Focus

1. Angka nomor soal reset per indikator; label level2 C3 & C4 dan metadata paket harus tetap source (task1).
2. Opsi PG duplicate, kontradiksi stem, kunci MCMA salah, dan lebih dari satu opsi benar (task1/4).
3. Kualitatif tidak berarti jawaban salah; semua category answers dan hash label harus terjaga (task2).
4. Mode ties/no mode, perubahan median setelah replace, mean exact versus display-rounded, peluang tetap (task3/4).
5. Soal HOLD/config buatan tak boleh melewati guard, UI dirty/status aman dan generator tidak menghubungi DB (task1/5).

## File map

Create `variant_gen/data/drill-1-indicators-20-23/{source.docx,q0_bank.csv,
question_catalog.json,question_metadata.json,original_revisions.jsonl}`;
ledger hanya berisi koreksi yang disepakati. Create config
`variant_gen/configs/{pg|mcma|kategori}-{20..23}-{1..3}-{1..10}/v1.json`
hanya untuk ID ACTIVE yang format/nomornya benar.
Create `variant_gen/tests/test_drill_20_23.py`,
`variant_gen/tests/check_drill_20_23_browser.js`, dan audit akhir
`docs/audits/2026-10-05-drill-20-23-generator-audit.{json,md}`.
Modify bank.py,engine.py,webui.py,webui.html,handoff.py,README.md,
tests/test_catalog.py dan tests/test_webui.py hanya bila dibutuhkan integrasi.
cli.py/config_store.py hanya jika guard/config validation existing belum cukup.
Jangan mengubah database.py atau repo Numora.

## Kontrak yang dipakai

- `OriginalBank(path)`: membaca satu source bank, ledger dan metadata.
- `load_workspace_bank(path, additional_paths=None)`: default menambah bank baru
  sambil mempertahankan extras existing; custom path standalone; duplicate-ID rejection.
- Metadata: `source_number`, `source_document_sha256`, `source_text`,
  `original_explanation`, `generation_status`, optional reason/notes/category_labels.
- Status allowed: ACTIVE,HOLD_SOURCE,DEFERRED_CONCEPTUAL. Dua status terakhir
  wajib reason; format dan lokasi metadata harus mengikuti loader existing.
- `generate(orig,cfg,seed,others)`: menolak non-ACTIVE bila metadata status ada;
  legacy original tanpa status tetap kompatibel. Gunakan ConfigError existing.
- `make_record(...)` dan `original_record(orig)`: optional answer_categories
  untuk KATEGORI berlabel khusus; map seluruh statement_id ke label nyata.
- `original_hash(orig)`: optional nondefault category_labels masuk fingerprint;
  hash lama/default Benar/Salah tidak berubah.
- CLI gen/regen/view/lint dan GET/POST lokal existing dipakai ulang; tidak ada
  endpoint DB baru atau output path bebas dari browser.

### Task 1: Audit sumber dan bank lokal terisolasi

**Files:** data/drill-1-indicators-20-23/*; bank.py; cli.py/config_store.py jika
guard existing memerlukan penyesuaian; tests/test_drill_20_23.py.

- [ ] Rekam git status dan hash bank/config/store sebelum eksekusi. Checkout
  berisi perubahan Tryout pengguna; baca loader/metadata terbaru dan pertahankan
  perubahan itu. Cocokkan source hash sebelum mengarsipkan source.docx.
- [ ] Audit setiap opsi/kunci pada seluruh120 blok inventory. Susun source review
  perID: ACTIVE/HOLD_SOURCE/DEFERRED_CONCEPTUAL, strategi varian, dan alasan.
  Tabel koreksi spec adalah temuan awal; jangan memakai instruksi source sebagai
  persetujuan. Apply koreksi hanya yang pengguna sepakati; sisanya HOLD.
- [ ] Tulis `test_new_bank_identity_and_catalog`:120 originals; formats60/36/24;
  setiap indikator/level1–3 tepat10; catalog20 groups,8 empty; activityDRILL,
  package_iddrill-1; source20Q23→pg-20-3-3; nomor source tetap23; level2 label
  C3 & C4. Unknown catalog ID/duplicate classification/source metadata ditolak.
- [ ] Tulis `test_workspace_preserves_existing_banks`: standalone legacy Drill
  tetap120; standalone baru120; default workspace menambah tepat120 ID baru,
  mempertahankan seluruh Tryout existing; custom bank tidak digabung otomatis.
- [ ] Tulis `test_hold_guards_and_revisions`: raw duplicate opts dipertahankan,
  ledger approved menaikkan version/hash dan tidak menghapus raw source; status
  HOLD menolak generate/regen/config save termasuk forged config, tanpa append.
- [ ] Run `python -B -m unittest discover -s tests -p test_drill_20_23.py -v`
  dari variant_gen. Expected: FAIL karena bank/metadata baru belum tersedia.
- [ ] Transkripsikan120 source rows dan metadata; tabel jadi multiline text
  berlabel, bukan deretan angka yang kehilangan header/satuan. Pernyataan MCMA
  satu paragraf dipisah menurut identifier; header checkbox tidak jadi opsi.
  ID internal statement1..n dipetakan ke source A/B/C dalam provenance bila perlu.
  Pembahasan original disimpan pada original_explanation, bukan kolom yang diabaikan.
- [ ] Tambah bank baru pada default extras existing. Perluas validasi metadata
  status dengan HOLD_SOURCE dan guard pusat generate/config-save. Run focused
  tests sampai PASS, kemudian regresi catalog/webui/tryout pada kondisi checkout.

### Task 2: Label kategori yang mempertahankan makna source

**Files:** bank.py,engine.py,webui.html,handoff.py; tests/test_drill_20_23.py.

- [ ] Tulis `test_custom_category_labels`: kategori-20-1-9 labels
  [Kuantitatif,Kualitatif], answers {1:Kuantitatif,2:Kualitatif,3:Kuantitatif};
  kategori-20-2-10 [Sesuai,Tidak Sesuai], answers1/3Sesuai dan2/4Tidak Sesuai.
  Original/variant explanation dan JSON memuat semua label, tidak menyebut
  jawaban Kualitatif sebagai salah. Duplicate/empty labels atau labels di PG ditolak.
- [ ] Tulis `test_category_hash_and_legacy`: mengganti label nondefault mengubah
  original_hash; config hash binding gagal setelah perubahan label; binary
  original lama tetap hash/output Benar/Salah identik. Historical record labels
  dibaca dari snapshot, tidak diganti memakai metadata latest.
- [ ] Tulis `test_nonboolean_category_export_is_explicit`: export_record menolak
  custom-label record dengan StoreError yang menjelaskan kontrak boolean;
  lokal JSON tetap menyimpan answer_categories penuh; legacy export tetap lulus.
- [ ] Run focused tests, Expected FAIL. Implement dua label optional pada
  metadata, hash, answer_categories, pembahasan dan renderer existing. Tidak
  membangun sistem scoring/rubrik kategori atau mengubah kontrak Numora.
- [ ] Run focused tests dan test_variant_gen.py. Expected PASS.

### Task 3: Config indikator20 dan21

**Files:** configs untuk source20/21 ACTIVE; tests/test_drill_20_23.py.

- [ ] Tulis `test_indicator20_oracles`: sum buku[4,6,3,7,5]=25; mean
  [70,80,75,85,90]=80; source20Q26 groupA mean78/B80, median80, range20/40,
  max90/100 sehingga MCMA2/3/4 benar. Periksa frekuensi tabel, jumlah total,
  proporsi persentase/sudut, statement all-true; jangan memakai evaluate engine
  sebagai oracle. Konteks survei/type-data memerlukan approved context cases.
- [ ] Tulis `test_indicator21_oracles`: mean[70,75,80,85,90]=80;
  median[6,8,7,9,10,8,5]=8; mode[2,3,4,3,5,3,6]={3}; range[12,15,18,20,25]=13.
  Nilai hilang pada mean80,[70,75,80,85,x] adalah90. Oracle source21Q29 total520,
  mean520/7; mode80/median75/range15; jangan membenarkan75,71.
- [ ] Tulis `test_source_conflicts_stay_hold`: source21Q21 disclosed90 versus
  implied89, source21Q25 PG multi-true, raw source21Q28 zero true. Approved
  corrections diuji sesuai ledger; belum approved tidak membuat config ACTIVE.
- [ ] Run focused FAIL; buat per-question config dari dataset/relationships
  terlebih dahulu. Gunakan scalar variables, choice/range/derived, min/max,
  Fraction, constraints existing. Mean/median/mode dihitung dengan oracle stdlib
  statistics/Counter di tes. Tidak perlu evaluator statistik generik.
- [ ] Per config: original_values mereproduksi original efektif, penjelasan
  nonempty, domain/unit/rounding jelas. Numeric data tidak dikocok hingga
  kehilangan sorting/multiplicity/unique mode; distractor harus distinct.
- [ ] Run focused PASS; generate kandidat banyak seed di memory dan cek oracle
  semua opsi/pernyataan, bukan hanya nomor kunci. Domain tidak diubah diam-diam
  untuk memenuhi target stock; alasan ketidakcukupan masuk audit perID.

### Task 4: Config indikator22 dan23

**Files:** configs untuk source22/23 ACTIVE; tests/test_drill_20_23.py.

- [ ] Tulis `test_indicator22_oracles`: source22Q6 mean6/6, median5/6,
  range6/4, true2/4. Q8 multimodeA={5,7}, median6/6, range2/4. Q17 mean76/80,
  median80/80, range10/40, groupB no unique mode. Q28 mean60/60 danrange40/20,
  true3/4. Uji equal means, swapped relation, range0, no mode/multimode, dan
  false inferensi variance dari range. PG harus exactly one true independently.
- [ ] Tulis `test_indicator23_oracles`:3red/5total=3/5; observed4/20=1/5;
  28/50=14/25=0,56; expected60×1/6=10;120×1/2=60;147/300=49/100.
  Observed15/120=1/8 < theoretical1/6. Oracle enumerate die faces, Fraction;
  theoretical coin tetap1/2 setelah212/400 observations.
- [ ] Uji observed0/trials dan observedtrials/trials, denominator0 ditolak,
  outcomes<=total, expected integer bila sourcecount integer, reduced fractions
  dengan fmt mixed existing, equality memakai Fraction sebelum display rounding.
  Approximation “mendekati” hanya untuk domain template yang direview.
- [ ] Tulis `test_fixed_answer_templates_are_honest`: pg-23-1-2 tetap HOLD/
  DEFERRED bila belum ada approved substantive strategy; shuffle/salin konteks
  tidak dilaporkan sukses. Tidak mengganti fair coin dengan biased coin tanpa review.
- [ ] Run focused FAIL; buat configs untuk ACTIVE, termasuk perubahan relasi
  pembanding PG22 yang diizinkan template. Kunci derived, bukan fixed kecuali
  hubungan matematis konstruksi membuktikannya. Run focused PASS dan oracle
  banyak seed. Status conceptual dan source review tercatat secara terpisah.

### Task 5: UI end-to-end, audit stock, dokumentasi

**Files:** webui.py,webui.html,tests/test_webui.py,
tests/check_drill_20_23_browser.js,README.md,tests/test_catalog.py,
docs/audits/2026-10-05-drill-20-23-generator-audit.{json,md}.

- [ ] Tulis HTTP tests filter Drill/Paket1 mencakup indikator16–23; source20–23
  level4–5 empty; original explanation/status/custom categories terlihat.
  Generate ACTIVE→JSONL, gen same seed→same snapshot, regen→v2 dengan v1
  terjaga, lint draft→no writes, config save→new version/stale409.
- [ ] Patch/mock database connect pada tes generator agar any connection gagal.
  HOLD/DEFERRED menolak generator/save di HTTP juga; seed0/bool/path traversal/
  Host/Origin protections existing tetap. Counts dihitung dari workspace bank
  aktual; jangan mengganti hardcoded120 menjadi angka global yang juga cepat basi.
- [ ] Run FAIL. Integrasikan status/metadata pada response/UI existing. Perbaiki
  note katalog yang menyebut jumlah/hilang secara statis, tampilkan source_number
  dan alasan held. Dua tab, layout bersama, dirty guard, UI Tryout existing
  dipertahankan. Render tabel/label/text dengan textContent.
- [ ] Browser memakai temp configs/store, DB routes mocked. Cek indikator20–23,
  original/variant, seed/history/config, kategori berlabel tepat, disabled HOLD,
  empty level, dirty draft, keyboard tabs, safe markup dan viewport390px.
- [ ] Audit per ACTIVE: reproduce_original tanpa error; sample seeds1..200 di
  memory sampai20 unique, oracle independent setiap candidate; laporkan actual
  successes/rejections/STOCK_REVIEW. HOLD/DEFERRED dihitung terpisah. Audit
  tidak mengisi store pengguna dan tidak mengklaim120 config selesai jika kurang.
- [ ] Run `python -B -m unittest discover -s tests -v`; Expected semua PASS,
  termasuk Tryout existing. Run CLI gen/regen/view dengan --bank bank baru dan
  --store temp; verify actual snapshots/options/key/explanation/classification.
- [ ] Hash legacy Drill/Tryout/config/store pengguna sama dengan preflight;
  `git diff --check` clean. Review independen sebelum klaim selesai. Jangan
  stage/commit perubahan pengguna atau workspace lain secara otomatis.
- [ ] README menunjukkan source120, jumlahACTIVE/HOLD/DEFERRED/stock aktual,
  koreksi yang disetujui, command dari root AI, alur Service AI, dan scope lokal.

## Self-review

- [x] Latest user correction menetapkan DRILL/Paket1; plan Tryout sebelumnya tidak diubah.
- [x] Source120 dibandingkan dengan blueprint200; missing level4–5 tidak diarang.
- [x] Tabel source, mixed cognitive label, raw corrections dan category labels punya owner task.
- [x] Reuse loader/metadata/mixed yang sudah ada; tidak menduplikasi implementasi Tryout.
- [x] Same-answer policy, stock target, source HOLD, exact arithmetic dan history punya verifikasi.
- [x] Seluruh endpoint generator/tes tidak membutuhkan DB; repo Numora tanpa perubahan.

## Handoff

Review plan dahulu. Rekomendasi eksekusi inline/native karena bank, config,
snapshot dan UI memakai kontrak yang sama. Koreksi akademik pending pada
tabel spec dapat disetujui perID atau dibiarkan HOLD; tidak ada penundaan diam-diam.
Implementasi belum dimulai. Plan teknis ini tidak menganggap perubahan kebijakan
same-answer atau approval Curriculum sebagai bagian dari izin implementasi.
