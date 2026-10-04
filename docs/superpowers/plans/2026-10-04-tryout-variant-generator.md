# Tryout Variant Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans untuk implementasi inline task-by-task. Langkah memakai checkbox; jangan mulai sebelum pengguna mereview plan. Review independen dilakukan setelah implementasi.

**Goal:** 30 original Tryout 1 tercatat, 27 generator numerik/analitis lengkap,
tiga soal konseptual ditunda; seed, config, pembahasan, penyimpanan, preview dan
ekspor lokal bekerja tanpa menyentuh database Numora.

**Architecture:** Pakai engine config existing, bank Tryout terpisah, loader
workspace menggabungkan aktivitas tanpa mengubah bank Drill. Satu orchestrator
paket mem-pin snapshot; UI existing memakai metadata Tryout/bab.

**Tech Stack:** Python 3.11, stdlib CSV/JSON/Fraction/hashlib/pathlib/unittest,
HTML/CSS/JS existing; tidak menambah dependency atau framework tes.

**Spec:** [Rancangan dan matriks 30 soal](../specs/2026-10-04-tryout-variant-generator-design.md).

**Status:** IMPLEMENTED; validated locally. Native execution used:
task saling bergantung dan engine existing cukup, tidak membutuhkan tim implementer.

## Global Constraints

- Tidak melakukan SQL, migrasi, impor, publikasi, scoring siswa, perubahan jadwal Tryout, atau komputasi IRT.
- Tidak menambah dependency generator; utamakan engine/config existing.
- Konseptual Drill dan mekanisme reuse stok di luar perubahan tahap ini.
- ID `tryout-1-b{chapter}-q{number:02d}`; package_id `tryout-1`; nama `Tryout 1`.
- 30 original: 18 PG,6 MCMA,6 KATEGORI; source C3/C4/C5=8/15/7.
- 27 aktif: 17 PG,5 MCMA,5 KATEGORI; C3/C4/C5=7/14/6.
- Deferred: b1-q07,b4-q02,b4-q06; original tetap terlihat, tanpa generator.
- Source SHA-256 `64F0D359B2507038B80D0B829E4DF7A402EED7A6AC3BBEA7A2AC06F9036BCB2F`.
- Config harus mereproduksi original efektif; original koreksi memakai ledger, bukan overwrite.
- Snapshot lama, Drill CSV/config, file pengguna, tab database existing tidak ditulis ulang.
- Semua tes memakai temp stores/config copies; tidak membutuhkan DB aktif.
- Jangan mengubah same_answer_as_original global atau mengklaim max_draws sebagai stok habis.
- Ekspor tanpa canonical mapping adalah LOCAL_PREVIEW; kontrak Numora dengan mapping adalah REVIEW.
- Satu writer lokal; tidak menjanjikan transaksi JSONL atau concurrent writing.

## Review Focus

1. ID soal reset per bab, pemilihan default/custom bank, metadata chapter vs indikator: uji task 1.
2. Malformed Word/LaTeX, kesalahan source, pecahan exact, formatting negatif: uji task 1/2.
3. Distractor bertabrakan, semua opsi MCMA/KATEGORI benar, batas floor/sudut/mean: oracle task 3–6.
4. Partial append saat crash, seed existing, regen mengubah latest: manifest harus pinned; uji task 7.
5. Dirty config, aktivitas kosong/deferred, injection, database accidentally queried: uji task 8.

## File ownership dan interfaces

Create `variant_gen/data/tryout-1/{source.docx,q0_bank.csv,question_catalog.json,
original_revisions.jsonl,question_metadata.json}`; `variant_gen/configs/tryout-1-b*/v1.json`
untuk 27 aktif; `variant_gen/tryout.py`; `variant_gen/tests/test_tryout.py`.
Modify bank.py,cli.py,expr.py,config_store.py,webui.py,webui.html,README.md dan
tests existing hanya di lokasi yang perlu. Tidak mengedit repo Numora.

- `load_workspace_bank(path, additional_paths=None) -> OriginalBank`: default
  workspace membaca bank Drill + Tryout; custom path standalone; paths explicit
  digabung dengan duplicate-ID rejection. `OriginalBank(path)` existing unchanged.
- Metadata original: `classification` berupa activity/package_id/chapter untuk
  TRYOUT; source number/difficulty/status/reason tersedia via metadata per soal.
  DRILL tetap indicator/source_level. Validasi metadata menunjuk ID yang ada.
- `format_fraction(value) -> str`: Fraction reduced, mixed bila >=1, negatif
  memakai satu tanda minus, integer tanpa pecahan; hanya dipakai fmt="mixed".
- `generate_package(bank, configs, store, package_id, seed, output_path) -> dict`:
  manifest 30 ordered entries. Manifest output_path adalah file untuk satu package+seed;
  existing manifest berbeda identitas ditolak, existing identik dipakai ulang.
- CLI `package-gen tryout-1 s5 --output path.json --json` memanggil generate_package.
  CLI `package-export path.json --output preview.json` memberi LOCAL_PREVIEW.
  CLI export individual existing tetap memakai canonical mapping.
- HTTP `POST /api/tryout/generate-package` payload `{package_id,seed}`;
  server memilih path di samping store, bukan menerima arbitrary output path dari browser.

### Task 1: Import original dan katalog Tryout terisolasi

**Files:** data/tryout-1/*; bank.py; cli.py; webui.py; tests/test_tryout.py;
update assertions default workspace di tests/test_webui.py bila perlu.

- [x] Catat git status, hash CSV/config/snapshot yang sudah ada. Baca source hash
  sebelum menyalin. Review koreksi b2-q04 dan redaksi b4-q04 bersama pengguna
  melalui plan; jangan menerapkan revisi akademik belum disepakati.
- [x] Tulis regression `test_tryout_bank_identity_and_originals`: tepat 30 ID;
  bab 8/8/7/7; format 18/6/6; source cognitive 8/15/7; deferred tepat tiga;
  seluruh nomor source unik dalam bab. Asserta corrected b2-q04 key C/16.000 v2,
  ledger menyimpan source key B/15.000 v1. b4-q04 efektif mengukur range.
- [x] Tulis `test_workspace_loader_isolates_banks`: OriginalBank Drill tetap120;
  default workspace150; custom CSV tidak dicampur; duplicate ID/unknown metadata
  ditolak; original hashes dan revisions Drill tetap sama.
- [x] Run `python -B -m unittest discover -s tests -p test_tryout.py -v`; cek
  failing sebab bank/loader belum ada.
- [x] Transkripsi 30 soal beserta opsi/kunci/pembahasan ke bank/source metadata,
  raw docx verbatim; gunakan ledger untuk koreksi yang disepakati. Jangan membuat
  importer DOCX generik untuk satu dokumen. Label PGK dipetakan berdasarkan
  bentuknya ke MCMA atau KATEGORI, bukan berdasarkan kata PGK saja.
- [x] Implement loader, chapter catalog, status/reason. CLI/UI default memakai
  loader; standalone API OriginalBank tetap kompatibel. Run test sampai PASS;
  `python -B -m unittest discover -s tests -v` untuk regresi sebelum lanjut.
- [x] Commit task hanya bila eksekusi di branch terisolasi dan diotorisasi; stage
  file task ini saja, tidak mengambil docs/config/store pengguna yang sudah berubah.

### Task 2: Representasi pecahan exact tanpa perubahan format lama

**Files:** expr.py; config_store.py; tests/test_tryout.py.

- [x] Tulis `test_mixed_fraction_rendering` dengan `Fraction(13,3)` → `4 1/3`,
  `Fraction(-13,3)` → `-4 1/3`, `Fraction(2,6)` → `1/3`, `6/3` → `2`, zero→`0`;
  render id/raw tetap hasil existing. fmt mixed untuk text harus ditolak jika invalid.
- [x] Run focused test, pastikan FAIL; implement format_fraction dan opt-in fmt
  mixed pada render/schema. Tidak menambah evaluator/fungsi formula generik.
- [x] Run focused test dan test_variant_gen.py sampai PASS. Gunakan numerator,
  denominator/gcd pada template rasio geometry; rounded display hanya untuk
  kasus yang source memang meminta/menampilkan pembulatan.

### Task 3: Tujuh generator Bab Bilangan

**Files:** configs/tryout-1-b1-q{01..06,08}/v1.json; tests/test_tryout.py.

- [x] Tulis `test_bilangan_generators`: semua tujuh config reproduksi original
  efektif, nonempty explanation, seed repeatable in-memory; tidak ada config q07.
  Oracle Fraction independen memeriksa addition, subtraction, precedence, exact
  division, invers dan diskon. Cek exactly two true pada q06 dan q08.
- [x] Pin original q03 Budi=-44,Andi=16; q04 result=1; q05 x=9 dan wrong13/3;
  q08 discount60.000,net240.000,total260.000. Uji negative/zero hasil suhu,
  divide-by-zero rejection, distractor collision rejection, uang nonnegative.
- [x] Run focused FAIL; buat config minimal menurut matriks spec. Domain input
  cukup untuk 20 kandidat unik; q04 assignment siswa benar berubah sehingga
  variasi tidak hanya mengganti angka sambil selalu kunci Budi.
- [x] Run oracle/reproduce tests PASS. Jangan memodifikasi validator global agar
  config yang kurang bervariasi lolos.

### Task 4: Delapan generator Bab Aljabar

**Files:** configs/tryout-1-b2-q{01..08}/v1.json; tests/test_tryout.py.

- [x] Tulis `test_aljabar_generators`: oracle koefisien polinom, sequence sums,
  floor budget, SPLDV, finite domain/range; tidak memakai engine evaluate untuk
  membuktikan kunci hasil engine. Determinan0 dan harga<=0 harus rejected.
- [x] Pin q01 coefficient18,const7; q02 U10=51; q03 max8; corrected q04 sum16.000;
  q05 range13/16/19/22 ribu dan6 jam di luar domain; q06 A60.000,B30.000,
  all four true; q07 U5=40.000,S5=150.000,mean30.000,all three true;
  q08 coefficient2,const22,P(3)=28.
- [x] Uji budget quotient exact dan remainder>0, domain boundary in/out, opsi
  range false dan transaksi valid, sign error polynomial, all-true export shape.
- [x] Run FAIL; buat delapan configs, memilih harga/x terlebih dahulu lalu derive
  totals, bukan mengacak sistem yang dapat unsolvable. Run focused PASS.

### Task 5: Tujuh generator Bab Geometri

**Files:** configs/tryout-1-b3-q{01..07}/v1.json; tests/test_tryout.py.

- [x] Tulis `test_geometri_generators`: oracle koordinat, area, angle sum,
  similarity cubed, photo ratios, sphere/cylinder, dilation.
- [x] Pin originals: q01(1,0); q02 area357; q03 angle55; q04 water256;
  q05 height48,bottom8,area ratio16/25,remainder864 (D960 false);
  q06 cylinder1540,hemisphere2156/3,total6776/3,box2160,difference296/3
  tampil98,67; q07 R'(-4,-8),area24,hypotenuse10.
- [x] Uji triangle fit, zero/negative angles, water ratio0/1/above1 rejection,
  negative scale, wrong use k versus k^2/k^3, photo margin bawah nonpositive,
  comparisons exact sebelum rounding. Pertahankan pola correctness original.
- [x] Run FAIL; buat tujuh configs mengikuti spec; run focused PASS. Gunakan
  triple Pythagoras/rational construction, bukan random dimensi tidak konsisten.

### Task 6: Lima generator Bab Data & Peluang

**Files:** configs/tryout-1-b4-q{01,03,04,05,07}/v1.json; tests/test_tryout.py.

- [x] Tulis `test_data_generators`: oracle collections.Counter/statistics/Fraction;
  enumerasi 36 pasangan dadu di tes, bukan copy formula config.
- [x] Pin q01 mode80; q03 N20,weighted total54,mean27/10,qualifying12,percent60;
  q04 witness X[72,75,78,81,84],Y[65,75,75,85,90] memenuhi summaries source;
  q05 counts sum7=6,doubles6,sum>=10=6,prime sums15 sehingga expected30/75;
  q07 a3,b11,median6,mean7,range9,median setelah max19 tetap6.
- [x] Uji no/tied mode rejection untuk q01, mean yang exact pada batas kategori,
  frequencies positive, dataset witness seluruh skor0..100, swapped class range,
  strictly increasing integers dan no unique mode q07. q02/q06 deferred no configs.
- [x] Run FAIL; buat lima configs menurut spec. Corrected q04 membandingkan
  rentang, tidak menyatakan range membuktikan variance. Run focused PASS.

### Task 7: Generasi paket pinned dan ekspor lokal

**Files:** tryout.py; cli.py; tests/test_tryout.py; handoff.py hanya jika metadata
lokal perlu ditambahkan pada generation, jangan mengubah required contract.

- [x] Tulis `test_package_generation_and_pinning`: manifest30 entries,27 VARIANT,
  3 ORIGINAL_ONLY dengan reason; source order benar; idempotent package+seed tidak
  append; regen individual tidak mengubah manifest existing; new package seed
  menghasilkan snapshot lain. Deferred tidak berpura-pura sukses generator.
- [x] Tulis `test_package_partial_failure_and_export`: invalid config menghentikan
  sebelum persist baru; failure saat append di fixture mempertahankan snapshot sah,
  tanpa manifest sukses, retry melanjutkan. Existing output beda identity ditolak.
  LOCAL_PREVIEW tanpa fabricated canonical UUID; mapped export pins historical
  record dan truth values untuk false maupun all-true statements. Status REVIEW.
- [x] Run FAIL; implement generate_package dengan validation/generation in-memory
  sebelum append, load_config immutability guard existing, others_for duplicate
  rules. Manifest temp file→atomic replace, satu writer. Tidak swallow errors
  sebagai reuse/exhausted. Pastikan parent/version/hash record masih tepat.
- [x] Tambahkan package-gen/package-export CLI interfaces di atas. Run focused
  PASS; jalankan command end-to-end dengan temp stores/output, bukan store pengguna.

### Task 8: UI Tryout, audit akhir, handoff

**Files:** webui.py; webui.html; tests/test_webui.py; tests/check_webui_browser.js
jika harness existing sesuai; README.md; tests/test_tryout.py.

- [x] HTTP regression Tryout package30 dengan bab8/8/7/7, generate/regen/config
  per active ID, deferred Generate rejected tanpa writes, malformed/path traversal/
  seed0/bool/origin JSON tetap rejected. Mock database connection supaya setiap
  test generator gagal bila tak sengaja memanggil DB.
- [x] Run FAIL; tambahkan endpoint package dan UI button Generate paket, preview
  manifest/status entries. Tryout memakai Bab; indikator/level hanya Drill.
  No extra route untuk SQL/write DB. Output path fixed server-side di temp fixture.
- [x] Browser: Tryout1 original/varian, chapter filters, deferred reason/buttons,
  seed/package preview, regen/history, config save/lint, dirty cancellation saat
  ganti aktivitas, error state tidak mempertahankan selection salah, mobile390px,
  unsafe markup rendered as text. Test di server dengan temp config/store.
- [x] `python -B -m unittest discover -s tests -v` PASS. Audit setiap 27 config:
  reproduce_original no failures, lalu seeds1..200 sampai20 unique valid in-memory;
  setiap kandidat dicek oracle, bukan hanya lolos engine. Laporkan capacity failure
  per ID; jangan menyimpulkan kapasitas exact dari sampling. Tidak memperluas
  domain tanpa menjaga constraints/kompetensi.
- [x] Cek hashes original Drill/config/store pengguna unchanged; `git diff --check`
  clean. Review independen perubahan generator dan schema/catalog; tangani blocker.
- [x] README: command/UI,27active/3deferred,source corrections,LOCAL_PREVIEW vs
  contract export,scope noDB,kapasitas audit. Tidak publish/commit file pengguna.

## Self-review sebelum diserahkan

- [x] Semua30 soal terinventaris; 27 aktif/3 deferred dan counts konsisten.
- [x] Input source matematika/format, dua koreksi utama dan satu warning deferred
  memiliki task; koreksi akademik ditandai untuk review, bukan diterapkan sekarang.
- [x] Task memakai bank/engine/store existing dan interface named; tidak ada
  placeholder function, dependency baru, migrasi, atau kebutuhan DB.
- [x] Default/custom bank, frac, all-true, threshold, crash/idempotency, UI dirty
  memiliki tes dengan expected values dan owner task.
- [x] Seed manifest/history dan export review tidak mengarang canonical IDs.
- [x] Tidak menyebut sampling sebagai exact capacity atau kode yang belum ditulis
  sebagai sudah selesai. Plan tidak mengimplementasikan fitur.

## Review pengguna sebelum execution

Konfirmasi desain penundaan b1-q07,b4-q02,b4-q06 dan koreksi b2-q04/b4-q04
melalui review plan. Rekomendasi execution: inline/native, lalu reviewer independen.
Jika pengguna belum memerintahkan implementasi setelah review, berhenti pada plan.
