# Drill Paket 1 Indikator 11–15 Implementation Plan

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task inline. Steps use checkbox (`- [ ]`) syntax for tracking. No subagent delegation required.

**Goal:** Memasukkan 250 original Drill Paket 1 indikator 11–15 dan menyediakan
generator terverifikasi per soal layak melalui CLI/workbench, seed, regen,
config editor, riwayat dan ekspor individual lokal.

**Architecture:** Bank sumber baru terisolasi, digabung oleh loader workspace
existing. Generator berupa config per ID pada engine existing; status sumber,
validasi, store JSONL dan UI digunakan ulang. Koreksi akademik dicatat sebagai
revisi setelah disepakati, tanpa menulis DB Numora.

**Tech Stack:** Python/stdlib, Fraction, unittest, JSON/CSV/JSONL,
HTML/JavaScript workbench existing; Playwright untuk verifikasi browser.

**Spec:** [Rancangan](../specs/2026-10-05-drill-11-15-generator-design.md).
**Inventory:** [250 soal dan status usulan](../specs/2026-10-05-drill-11-15-source-inventory.json).

## Global Constraints

- Rencana saja sampai pengguna meminta implementasi. Tidak commit/push saat planning.
- Tidak menyentuh database Numora, repo Numora, `.env`, atau store pengguna.
- 250 originals, 125 PG/75 MCMA/50 KATEGORI; 25 groups × 10 soal; level 1–5.
- ID `{pg|mcma|kategori}-{11..15}-{1..5}-{1..10}` sesuai format soal sumber.
- `activity=DRILL`, `package_id=drill-1`, nama `Paket 1`; hierarchy paket > indikator > level > soal.
- Cognitive labels sumber: `C3`, `C3 & C4`, `C4`, `C4 & C5`, `C5`.
- Runtime statuses `ACTIVE`, `HOLD_SOURCE`, `DEFERRED_CONCEPTUAL`; nonaktif wajib reason.
- 223 CANDIDATE/22 DEFERRED/5 HOLD adalah triase awal, bukan janji jumlah config.
- `MAX_LEN=300`, `MAX_NODES=150`, `MAX_EXPONENT=12`, `MAX_ABS=10**12` tetap.
- Tidak melemahkan `same_answer_as_original` atau duplicate/answer validators.
- Tidak ada dependency baru, LLM runtime, evaluator umum baru, atau 250 fungsi Python.
- Stok konseptual/reuse, generator paket Drill, Pretest, IRT dan deployment di luar scope.
- Pertahankan semua bank/config/riwayat existing, termasuk perubahan 20–23.

## Review Focus

1. Pecahan/pangkat OMML, singleton `{ 1 }`/`{ a }`, dan mixed cognitive labels:
   literal ter-render benar, sumber utuh, canonical export campuran diblokir (task 1/7).
2. HOLD disertai config buatan atau cached seed: gen/regen/lint/save tetap menolak,
   view tetap tersedia, tidak append record (task 1/7).
3. Cardinality range/nama siswa/kategori jawaban tetap setelah angka berubah:
   variasi harus mengubah teks jawaban benar secara matematis (task 2/5/6).
4. Ambang `>` vs `>=`, endpoints interval, batas exponent dan pembulatan:
   hasil minimal exact, distractor tidak bertabrakan setelah formatting (task 3/4).
5. Segitiga mustahil, SSA ambigu/tunggal, hasil benar dengan alasan salah:
   validasi model geometri dan seluruh klaim, bukan sekadar arithmetic (task 5/6).

## File map dan kontrak

Create `variant_gen/data/drill-1-indicators-11-15/{source.docx,q0_bank.csv,
question_catalog.json,question_metadata.json}`. Create ledger
`original_revisions.jsonl` hanya untuk koreksi yang telah disepakati.
Create `variant_gen/configs/<ACTIVE-question-id>/v1.json`.
Create **satu** `variant_gen/tests/test_drill_11_15.py` memakai unittest.
Create audit akhir `docs/audits/2026-10-05-drill-11-15-generator-audit.{json,md}`.

Modify `variant_gen/bank.py` untuk whitelist bank; `variant_gen/cli.py` hanya
jika cached gen melewati guard; `variant_gen/webui.py`/`webui.html` hanya jika
guard/status/filter belum memadai; `variant_gen/handoff.py` untuk validasi
cognitiveLevel canonical. Modify `variant_gen/tests/test_catalog.py`,
`test_variant_gen.py`, `test_tryout.py`, `test_drill_20_23.py`, `test_webui.py`
hanya pada asumsi coverage/integrasi yang terdampak. Update `readme.md`,
`docs/OPERATIONS.md`, `docs/GENERATOR.md`, `docs/README.md` sesuai hasil final.
Tidak ada kebutuhan awal mengubah `expr.py`, `filters.py`, `database.py`.

Interfaces existing yang dipertahankan:

- `OriginalBank(path)`; `.ids()`, `.catalog()`, `.get(qid)` menghasilkan copy.
- `load_workspace_bank(path, additional_paths=None)`; default merge,
  custom standalone, duplicate IDs ditolak.
- `ConfigStore(root).load(qid, version=None) -> (cfg, hash)`;
  `validate_config(cfg, orig) -> list[str]`.
- `build_values(cfg, source, check=True) -> dict`, `assemble(cfg, values) -> dict`;
  `generate(orig, cfg, seed, others) -> Result(values, cand, draws_used, rejections)`.
- `reproduce_original(orig, cfg) -> (problems, warnings)`;
  `run_lint(orig, cfg, n=100) -> (ok, lines)`.
- `make_record(...)`, `original_record(orig)`, `VariantStore(path)` dan
  `others_for(store, qid, seed)` existing; jangan membuat store alternatif.
- `export_record(record, mapping) -> dict`; invalid canonical cognitive label
  menghasilkan `StoreError`, mapping/hash/version/UUID checks tetap berlaku.
- `webui.make_server(port=8765, bank=..., configs=..., store=...)` existing;
  baca signature terbaru sebelum menggunakan keyword tambahan.

Setiap task generator menggunakan manifest status final task 1, bukan angka
223 hardcoded. Oracle berada di file tes: hitung model dari parameter bebas
secara independen memakai Fraction/formula akademik, cocokkan teks opsi,
seluruh flags correct dan angka di pembahasan. Jangan memanggil evaluator
config untuk menghitung expected answer.

### Task 1: Audit original, bank dan loader

**Files:** data folder baru; bank.py; test_drill_11_15.py;
inventory JSON untuk kontrak per ID; cli.py jika cached guard memerlukan fix.
**Consumes:** DOCX/SHA/inventory; loader/status existing.
**Produces:** 250 originals/classification/status final dan 25 groups; bank
dapat dipakai standalone atau default merge; ledger hanya koreksi disepakati.

- [ ] Catat status Git dan hash bank/config/store sebelum eksekusi. Baca ulang
  perubahan workspace 20–23; jangan menimpa/men-stash perubahan pengguna.
- [ ] Audit 250 stem/opsi/kunci/pembahasan melalui OMML dan dokumen asli.
  Lengkapi inventory tiap ID dengan domain, variabel, invariant, strategi
  distractor/oracle, risiko finite. Tahan lima temuan spec; konflik tambahan
  menjadi HOLD dengan reason. Tidak memilih koreksi geometri akademik sendiri.
- [ ] Tulis `test_bank_identity_and_source`, `test_catalog_complete`,
  `test_workspace_merge_and_isolation`, `test_status_guards`,
  `test_literal_set_and_omml_formatting`. Assertions inti:

  ```python
  bank = OriginalBank(BANK)
  self.assertEqual(len(bank.ids()), 250)
  self.assertEqual(len(set(bank.ids())), 250)
  self.assertEqual(len(bank.catalog()), 25)
  self.assertEqual({len(g['question_ids']) for g in bank.catalog()}, {10})
  self.assertEqual(Counter(bank.get(q)['format'] for q in bank.ids()),
                   {'PG': 125, 'MCMA': 75, 'KATEGORI': 50})
  self.assertEqual(bank.get('pg-11-2-1')['cognitive_level'], 'C3 & C4')
  self.assertEqual(bank.get('pg-11-4-1')['cognitive_level'], 'C4 & C5')
  ```

  Pin SHA source spec; identity source `(indicator,level,number)` unik;
  KATEGORI A/B/C→1/2/3; source explanation nonempty. Test malformed status,
  reason kosong, duplicate IDs/catalog classification. Buat fixture config
  dan cached record untuk HOLD; backend tidak boleh melewati status guard.
  Pin singleton render `{ {member} }`→`{ 1 }`; validator tidak menganggapnya
  placeholder unresolved; OMML pecahan/pangkat/subskrip tidak hilang.
- [ ] Run `python -B -m unittest discover -s variant_gen/tests -p test_drill_11_15.py -v`;
  expected FAIL karena bank/integrasi baru belum tersedia, bukan error import tak terkait.
- [ ] Arsipkan source.docx dengan SHA sesuai; tulis bank/catalog/metadata,
  normalisasi format sesuai spec. Tambahkan hanya bank baru ke whitelist
  `load_workspace_bank`; gunakan status guards existing dan perbaiki cached
  gen jika perlu. Jangan membuat runtime status CANDIDATE.
- [ ] Run command task ini; expected seluruh tes task 1 PASS, originals lama
  hash/version tidak berubah. Coverage default memakai union bank yang ada;
  tes bank tertentu memakai `OriginalBank` atau explicit extras terisolasi.

### Task 2: Generator indikator 11 — relasi dan fungsi

**Files:** configs ID11 ACTIVE; test_drill_11_15.py.
**Consumes:** bank/status/domain per ID task 1; generate/lint existing.
**Produces:** config lengkap variabel/constraints/stem/options/explanation/original_values/hash.

- [ ] Tulis `test_indicator_11_reproduction`, `test_indicator_11_oracles`,
  `test_range_cardinality_changes`. Anchor original: `pg-11-1-4`=11;
  `pg-11-2-2` range [1,10]; `pg-11-3-2` range {-1,0,3}, cardinality3;
  `pg-11-3-4`=17; `pg-11-3-5` pertama lebih murah hari5, hari4 sama;
  `pg-11-4-3`=19; `kategori-11-5-9` jumlah fungsi3→2 adalah8;
  `kategori-11-5-10` tarif sama pada3km. Pin semua statement benar/salah.
  Cari minimal dua nilai cardinality dan teks jawaban benar valid di domain
  `pg-11-3-2`; translasi simetris saja harus gagal test variasi.
- [ ] Run task test command; expected FAIL karena config ID11 belum ada.
- [ ] Tulis config tiap ACTIVE dari kontrak inventory; konstruk domain/pasangan
  secara scalar, komposisi sesuai urutan, kuadrat memeriksa vertex/endpoints.
  Pertahankan tiga HOLD indikator11 sampai koreksinya disepakati.
- [ ] Run task test command; expected reproduction `( [], [] )`, oracle semua
  ACTIVE PASS dan perubahan jawaban cardinality nyata. Audit penjelasan selain lint.

### Task 3: Generator indikator 12 — barisan

**Files:** configs ID12 ACTIVE; test_drill_11_15.py.
**Consumes/Produces:** kontrak task 2 dengan source ID12; tidak bergantung config ID11.

- [ ] Tulis `test_indicator_12_reproduction`, `test_indicator_12_oracles`,
  `test_sequence_threshold_boundaries`. Anchor: `pg-12-1-1` berikut21,25;
  `pg-12-1-3` U8=-9; `pg-12-1-5` bulan12=375000;
  `pg-12-2-2` Un=4n−1; `pg-12-2-5` pertama >300 bulan14 (bulan13=300);
  `pg-12-3-3` indeks7,nilai23; `pg-12-3-5` pertama >1000 hari7;
  `pg-12-4-3` U6=192; `pg-12-4-4` negatif pertama U7 (U6=0);
  `pg-12-5-2` gajiB>A tahun6 (tahun5 sama); `pg-12-5-3` U8=4374;
  `kategori-12-4-10` U6=1/3 exact. Pin metadata Fraction vs tampilan mixed.
- [ ] Run task test command; expected missing-config FAIL untuk ID12.
- [ ] Tulis config barisan aritmetika/geometri; minimal-index constraints
  memeriksa suku saat n dan n−1, bukan menebak threshold. Batasi eksponen
  maksimal12 tanpa mengurangi domain sumber yang sah; bentuk tertutup linear
  dipakai untuk indeks besar. Probe report/siswa mengubah truth assignment.
- [ ] Run task test command; expected ID12 ACTIVE PASS, original warnings kosong;
  negative/zero boundary, rasio pecahan, formatting distractor teruji.

### Task 4: Generator indikator 13 — deret

**Files:** configs ID13 ACTIVE; test_drill_11_15.py.
**Consumes/Produces:** kontrak task 2 dengan source ID13.

- [ ] Tulis `test_indicator_13_reproduction`, `test_indicator_13_oracles`,
  `test_series_interval_and_threshold`. Anchor: `pg-13-1-1` U4=12,S4=30;
  `pg-13-1-3` S10=185; `pg-13-2-3` S6=1456;
  `pg-13-2-5` minimal total>=1juta bulan7 (bulan6=900000);
  `pg-13-3-1` U6=32,S6=102; `pg-13-3-3` kelipatan6 pada100<k<300
  adalah102..294,33 suku,jumlah6534; `pg-13-3-5` hari15,S14=73.5,S15=82.5;
  `pg-13-4-5` S16=2800,S17=3060; `mcma-13-4-8` total49.2juta/48.6juta,
  selisih600000; `pg-13-5-3` U15=94,S15=780;
  `pg-13-5-4` totalgeometri1023000; `kategori-13-5-10` S10=5115000.
  Test endpoint300 tidak ikut, exact half-units, r=1 domain policy,
  evaluasi semua klaim siswa dan batas nilai intermediate.
- [ ] Run task test command; expected missing-config FAIL untuk ID13.
- [ ] Tulis config deret closed-form dan constraints n/n−1. Jika rasio1 sah,
  tangani jumlah n*a tanpa divide-by-zero; jika bukan tujuan soal, larang
  rasio1 secara eksplisit. Jangan memakai float untuk expected totals.
- [ ] Run task test command; expected semua ID13 ACTIVE PASS dan laporan
  batas endpoint/threshold/pembulatan sesuai sumber efektif.

### Task 5: Generator indikator 14 — sudut

**Files:** configs ID14 ACTIVE; test_drill_11_15.py.
**Consumes/Produces:** kontrak task 2 dengan source ID14.

- [ ] Tulis `test_indicator_14_reproduction`, `test_indicator_14_oracles`,
  `test_angle_topology_and_student_reports`. Model source: p di atas q,
  parallel, transversal; sudut1 kiriatas,2 kananatas,3 kiribawah,4 kananbawah;
  A1=A4=B1=B4=θ, lainnya180−θ. Pin topology sehadap/berseberangan/sepihak,
  bukan inferensi hubungan dari angka yang kebetulan sama saja.
  Anchor: `pg-14-1-4` x35,max70; `pg-14-2-2` x26,A4=88;
  `pg-14-2-3` x20,B4=75; `pg-14-3-2` x20,B3=65;
  `pg-14-4-2` x38,B4=86; `pg-14-4-4` x30,selisih35;
  `pg-14-5-3` x30,B4=110,Rina benar; `pg-14-5-4` x25,60/70/50,lancip;
  `kategori-14-5-9` puncak60,flags false/false/true.
  Test hasil angka benar tetapi alasan salah dinilai salah; winner laporan
  dan klasifikasi dapat berganti melalui konstruksi sudut sah.
- [ ] Run task test command; expected missing-config FAIL untuk ID14.
- [ ] Tulis config dari θ/x/koefisien yang menghasilkan sudut positif valid;
  klaim/alasan serta penugasan siswa diturunkan dari model. Tanpa gambar
  sumber, pertahankan uraian posisi lengkap; tidak perlu image generation.
- [ ] Run task test command; expected ID14 ACTIVE PASS, semua sudut valid,
  tepat satu PG benar, MCMA/KATEGORI seluruh truth values benar.

### Task 6: Generator indikator 15 — Pythagoras/kesebangunan

**Files:** configs ID15 ACTIVE; test_drill_11_15.py.
**Consumes/Produces:** kontrak task 2 dengan source ID15; kedua HOLD tetap nonaktif.

- [ ] Tulis `test_indicator_15_reproduction`, `test_indicator_15_oracles`,
  `test_geometry_consistency_and_winner`. Anchor: `pg-15-1-2` sisi8;
  `pg-15-2-1` tinggi16.5 termasuk tangan1.5;
  `pg-15-2-2` x5,sisi5/12/13,keliling30; `pg-15-2-5` luas125;
  `pg-15-3-1` keliling68; `pg-15-3-4` BD=9;
  `pg-15-3-5` luas62.5km²; `pg-15-4-1` tinggi15,luas120;
  `pg-15-4-3` AC12.5; `pg-15-4-4` lampu4.8;
  `pg-15-5-2` sisi24,Cici benar; `pg-15-5-5` jarak90km;
  `mcma-15-5-8` rasio luas9:16; `kategori-15-5-9` rasio luas1:2500.
  Test triangle inequality, law-of-sines coherence, correspondence,
  squared unit conversion, dan minimal dua winner sah `pg-15-5-2`.
  Pin `mcma-15-2-8` data tidak konsisten dan `pg-15-4-2` SSA source hanya
  satu solusi: sinC=6*sin40°/8; supplementary branch tidak memenuhi total180.
- [ ] Run task test command; expected missing-config FAIL untuk ID15.
- [ ] Tulis config triple/scaled triples dan rasio yang menjaga model geometri.
  Variasikan laporan/metode siswa, bukan hanya angka/nama kosmetik.
  Jangan mengaktifkan dua HOLD geometri dengan alasan arithmetic-nya cocok.
- [ ] Run task test command; expected ID15 ACTIVE PASS; HOLD masih ditolak;
  jawaban benar/distractor/pembahasan memenuhi model dan unit.

### Task 7: Alur CLI/workbench, history dan ekspor

**Files:** test_drill_11_15.py; test_webui.py; handoff.py;
cli.py/webui.py/webui.html hanya jika guard/filter masih kurang.
**Consumes:** bank merged, config ACTIVE, CLI/HTTP/store/mapping existing.
**Produces:** semua ID terlihat sesuai hierarchy, seed/config/regen/history
berfungsi, canonical label invalid ditolak tanpa DB.

- [ ] Tulis `test_cli_history_and_status`, `test_http_drill_11_15`,
  `test_export_cognitive_label_and_literal_set` pada suite existing/baru.
  Temp store/config saja; mock koneksi DB agar setiap akses gagal test.
  Assert gen seed0 original; gen seed baru append v1; gen seed sama tidak
  append; regen sama config perlu reason; regen v2 tidak mengubah v1;
  config-save invalid tidak menulis file; valid save menambah versi.
  HOLD/DEFERRED gen/regen/lint/save ditolak, termasuk cached seed dan config
  buatan; view original/history boleh. Mapping dummy asli-format nonzero
  UUID fixture valid untuk test; tidak diklaim sebagai ID produksi.
  `C3` export berhasil, `C3 & C4`/`C4 & C5`/label invalid raise StoreError;
  singleton explanation `{ 1 }` tidak dianggap placeholder; unresolved
  `{missing}` tetap ditolak; mismatch originalHash/version tetap ditolak.
- [ ] Run `python -B -m unittest discover -s variant_gen/tests -p test_webui.py -v`
  dan task test command; expected FAIL hanya gap integrasi yang disebut.
- [ ] Implementasi guard minimum yang masih kurang. `handoff.export_record`
  memvalidasi cognitive label `C1`..`C6`; source labels tetap disimpan utuh,
  tanpa otomatis memilih label tunggal. UI memakai filter/status existing.
- [ ] Run kedua command; expected PASS. Jalankan server dengan salinan config
  dan temp store, browser hanya tab Service AI. Verifikasi Paket1/indikator11–15/
  level1–5 masing-masing10; original/variant berdampingan; seed, regen,
  config validation/save, history, alasan status, dirty draft serta keyboard
  tetap bekerja. Jangan membuka tab DB atau membuat canonical production mapping.

### Task 8: Audit kapasitas, regresi dan dokumentasi final

**Files:** test_drill_11_15.py; tests coverage yang terdampak; audit JSON/MD;
readme.md; docs/OPERATIONS.md, GENERATOR.md, README.md.
**Consumes:** seluruh task; inventory/status final; snapshots task 1.
**Produces:** evidence manifest per ID, command penggunaan, hasil regresi,
daftar HOLD/DEFERRED/finite limits yang jujur.

- [ ] Tulis `test_all_active_configs_and_sampling`: setiap ACTIVE tepat punya
  config, validate_config=[], reproduce_original=([],[]), explanation/oracle
  lulus; nonaktif tidak memiliki config aktif. Sampling seeds1..200 sampai
  target20 varian unik, `others` bertambah tiap sukses. Setiap hasil harus
  lolos oracle, duplicate/same-answer rules; minimal satu hasil per ACTIVE.
  `GenerationError` dicatat tanpa append. Determinisme diuji pada seed/config/
  others identik; timestamps tidak dijadikan pembanding determinisme.
- [ ] Run task test command; expected FAIL bila coverage/status/oracle kurang.
  Perbaiki config/status berdasarkan bukti, tidak mengurangi validator agar hijau.
- [ ] Buat audit per ID: source/effective version/hash, status+reason,
  config/hash, seed sukses/gagal, distinct count, rejection reasons,
  sampling PASS(>=20)/SHORT(1..19)/FAIL(0 atau oracle invalid), finite-domain
  rationale dan corrections. Sampling SHORT bukan bukti stok habis;
  laporkan warning original separately. FAIL tidak boleh tetap ACTIVE.
- [ ] Update coverage tests yang men-scan semua config agar memakai merged bank;
  tes bank standalone mempertahankan jumlah lokal. Update test20–23 default
  union supaya bank11–15 tidak dianggap regresi. Jangan mengganti seluruh
  expected counts dengan angka gabungan tanpa menguji identity per bank.
- [ ] Run `python -B -m unittest discover -s variant_gen/tests -v`;
  expected semua PASS, tidak ada koneksi DB, config invalid atau audit FAIL.
  Run `git diff --check`; expected exit0. Cocokkan snapshot store/bank/config
  existing task1 untuk membuktikan data lama dipertahankan.
- [ ] Update docs berdasarkan hasil ACTIVE final, bukan target223. Berikan
  contoh `view pg-11-1-4 s0`, `lint pg-11-1-4 --n 20`, `gen`/`regen` dengan
  temp store; cakupan levels penuh bank ini, status dan batas ekspor campuran.
  Link audit dari docs/README.md. Tinjau diff hanya file task ini; jangan
  stage user store/perubahan 20–23 otomatis. Commit/push di luar planning.

## Handoff

Belum ada implementasi yang diizinkan pada tahap ini. Rekomendasi setelah
rencana ditinjau: eksekusi inline memakai `superpowers:executing-plans`, karena
bank/config/guard saling berbagi state workspace. Audit lima HOLD dapat tetap
tertunda tanpa menghalangi generator soal lain yang telah terverifikasi.
