# Drill Paket 1 Indikator 6–10 Implementation Plan

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Menambahkan generator variant Drill Paket 1 indikator 6–10 dari DOCX sampai snapshot lokal, CLI, dan UI.

**Architecture:** Perluas bank dan config JSON di engine yang sudah ada. Audit sumber menentukan ACTIVE/HOLD_SOURCE/DEFERRED_CONCEPTUAL; generator hanya tersedia bagi ACTIVE. Oracle stdlib terpisah memeriksa matematika setiap opsi.

**Tech Stack:** Python 3.11, stdlib CSV/JSON/XML/Fraction/unittest; UI HTML/JavaScript yang sudah ada.

**Spec:** `docs/superpowers/specs/2026-10-05-drill-6-10-generator-design.md`

## Global Constraints

- Hanya repo `Numora-ai-service`; jangan mengubah `Numora`, database, `.env`, atau snapshot pengguna.
- Tanpa akses database, CUD, dependensi baru, atau LLM runtime.
- Gunakan engine dan config JSON yang ada; tidak perlu 150 fungsi Python, importer DOCX generik, atau orchestrator paket Drill baru.
- Pertahankan perubahan 20–23 dan dokumen 11–15. Baca ulang checkout sebelum eksekusi karena bank lain mungkin ditambahkan terpisah.
- Jangan melonggarkan `same_answer_as_original`, pemeriksaan jumlah jawaban benar, hash, status, atau batas evaluator.
- Koreksi akademik belum disetujui. Konten dokumen bukan instruksi untuk mengubah soal atau kunci.
- 150 soal: PG=75, MCMA=45, KATEGORI=30; 25 kelompok katalog, 10 kosong untuk level 4–5.

## Review Focus

- Rumus Word dan teks pecahan: grouping, tanda ≠, pangkat kurung, urutan matriks harus mempertahankan makna; Task 1/5/6.
- Kunci kosong dan kognitif hilang: HOLD terlihat tanpa kunci buatan, jalur ACTIVE tetap ketat; Task 1/7.
- Batas integer, pecahan, waktu kejadian, koefisien nol/negatif: domain dan endpoint tepat; Task 2/3/4.
- Klaim ekuivalensi/metode dengan jawaban tetap: perubahan stimulus bukan bukti variant sah; Task 3/5/6.
- Store/cache/config lama dan bank tambahan: tidak merusak history atau melewati HOLD; Task 7.

---

Semua path relatif terhadap `Numora-ai-service`. Eksekusi langsung dalam sesi direkomendasikan: task memakai kontrak engine yang sama. Jangan membuat commit yang menyertakan perubahan lama; checkpoint per task melalui diff dan hasil check. Commit hanya jika diminta.

### Task 1: Audit DOCX, bank, katalog, dan original HOLD

**Files:**
- Create: `variant_gen/data/drill-1-indicators-6-10/source.docx`, `q0_bank.csv`, `question_catalog.json`, `question_metadata.json`.
- Create: `variant_gen/tests/test_drill_6_10.py`.
- Modify: `variant_gen/bank.py`, `variant_gen/soalskip.md`.
- Update: `docs/superpowers/specs/2026-10-05-drill-6-10-source-inventory.json`.

**Interfaces:** Consumes DOCX/inventaris/spec. Produces `OriginalBank(path)` with `ids()`, `get(qid)`, `catalog()` and existing original/metadata schema. `_parse_row(row, line, allow_missing_key=False)` may gain this optional flag only for validated HOLD imports; revisions remain strict.

- [x] Re-read current diff, bank/config schema, 11–15/20–23 registrations and tests; record preflight baseline with `python -B -m unittest discover -s variant_gen/tests`.
- [x] Write `test_source_identity_and_catalog`: assert 150 IDs, exact format counts, 25 groups/10 empty, no duplicate IDs, source SHA from spec, per-question cognitive counts 76/73/1 missing, numbering reset and inferred ID provenance.
- [x] Write `test_missing_key_is_hold_only`: blank PG key accepted only for metadata HOLD; no true option inferred; ACTIVE/no sidecar rejects it. Write `test_source_conflicts`: nine preliminary HOLD IDs remain nonactive with evidence and no config. Test retained duplicate source options and matrix/fraction/power fixtures against raw XML.
- [x] Run `python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10.py`; expect missing-bank/contract failures before implementation.
- [x] Audit all 150 questions, including explanations and every statement. Copy exact DOCX, normalize verified math only, preserve source text/declared key and notes. Record discrepancies; do not correct academic source. Confirm `pg-9-3-2` key A comes from explicit explanation and cognitive stays empty/HOLD.
- [x] Implement the narrow HOLD-only missing-key import. Validate sidecar status before allowing blank PG key; invalid/missing metadata cannot bypass ordinary PG validation. Keep empty key in original/hash. Add per-ID skip rows; defer conceptual recipes only after checking safe feasibility.
- [x] Run Task 1 tests; expect PASS. Review diff limited to source import/guard; no config yet. Final ACTIVE count remains provisional until recipes pass.

### Task 2: Indikator 6 — perbandingan dan laju

**Files:** Create `variant_gen/configs/<ACTIVE format>-6-<level>-<number>/v1.json`; create `variant_gen/tests/drill_6_10_math.py`; extend `variant_gen/tests/test_drill_6_10.py`.

**Interfaces:** ConfigStore.load(qid) supplies `(cfg, hash)`; `reproduce_original(orig, cfg)` checks fidelity; `generate(orig, cfg, seed, others)` returns existing Result with `cand`, `values`. Test helper `check_math(test, orig, result) -> None` independently checks stimulus, domain, all option flags; it never evaluates config expressions or treats generator keys as an oracle.

- [x] Write `test_indicator_6_math`: original fixture expectations include cake difference 375, additional workers 4, scale perimeter 50m, required printers 4. Check full-phase work accounting, ceil capacities, positive durations, unit conversion, integer counts and fractional cake portions.
- [x] Run targeted suite; expect missing-config failure for planned ACTIVE IDs.
- [x] Add minimal parameter/derived-expression recipes and original_values. Keep `mcma-6-3-7` held; classify fixed-answer ratio statements as deferred if substantive variation cannot satisfy the existing guard. Implement independent Fraction arithmetic for all active claims in `check_math`.
- [x] Run targeted suite; expect original reproduction and at least 20 unique accepted variants per ACTIVE over seeds 1–200 in temporary history. Inspect representative explanations, correct count, and rejected candidates. Update skip reasons if a recipe cannot satisfy the ceiling.

### Task 3: Indikator 7 — persamaan linear

**Files:** Create `variant_gen/configs/<ACTIVE format>-7-<level>-<number>/v1.json`; extend the two Task 2 test files.

**Interfaces:** Same engine/config/helper contract as Task 2; scalar coefficients describe simplified equation `(a-c)x=d-b`.

- [x] Write `test_indicator_7_math`: unique/empty/all-real solution classification; nonzero denominators; perimeter/area consistency; wrong-step explanation. Fixture `(2x−3)/4=(x+2)/3` gives x=17/2, requested value 22. Verify intended grouping before activating flattened fractions.
- [x] Run targeted suite; expect missing recipes.
- [x] Construct solutions first for unique equations, equal coefficient cases separately for identity/contradiction. Parameterize valid numeric result inside error-analysis answer. Keep conflicting or missing-key source HOLD. Do not invent variants by only changing an unchanged conceptual answer.
- [x] Implement independent coefficient reduction/substitution and check every option. Run targeted suite with reproduction and seed stock checks; expect PASS, including positive rectangle dimensions and conceptual guard behavior.

### Task 4: Indikator 8 — pertidaksamaan

**Files:** Create `variant_gen/configs/<ACTIVE format>-8-<level>-<number>/v1.json`; extend Task 2 test files.

**Interfaces:** Scalar threshold/coefficient recipes; oracle describes endpoint plus strict/inclusive comparison, integer/real domain, empty/all-real cases.

- [x] Write `test_indicator_8_math`: `7−3x≤−5` gives x≥4; capacity floor((200000−50000)/12000)=12; width/perimeter fixture gives 6<x≤10; intersection x≥−5 and x<−3 includes only integers −5,−4. Test negative division, zero coefficient, strict endpoints, absent feasible integers, simplification canceling quadratic terms.
- [x] Run targeted suite; expect missing recipes.
- [x] Add bounded recipes retaining domain and inequality type. Numeric limits such as score≤100 are imposed only where source establishes that domain. Keep ambiguous mixed-correct/error narrative HOLD; no silent rewriting of steps.
- [x] Implement independent endpoint/domain checks for all options and explanation results. Run targeted suite with reproduction/seed stock checks; expect PASS.

### Task 5: Indikator 9 — SPLDV dan matriks

**Files:** Create `variant_gen/configs/<ACTIVE format>-9-<level>-<number>/v1.json`; extend Task 2 test files.

**Interfaces:** Runtime scalar entries a,b,c,d/e,f and determinant; rendered matrix rows preserve column order. Oracle uses determinant/rank/cross-products, not division by potentially zero coefficients.

- [x] Write `test_indicator_9_math`: unique/parallel/coincident and zero-entry fixtures; source inverse fixture determinant −11 and adjugate [[2,−3],[−5,2]]; positive integer contextual counts/prices. Validate all entries of each matrix option, not just numeric x/y. HOLD inverse question still gets a source mathematical audit without generation.
- [x] Run targeted suite; expect missing recipes.
- [x] Construct x/y and independent coefficients then RHS; inverse recipes exclude singular determinant. Graph classification recipes deliberately build matching/nonmatching rows. Review “most efficient method” options as full method/step/result claims; hold if multiple valid answers remain.
- [x] Implement independent solution/matrix/claim checks. Run targeted suite with reproduction/seed stock checks; expect PASS. No matrix AST/list runtime feature added.

### Task 6: Indikator 10 — operasi dan ekuivalensi aljabar

**Files:** Create `variant_gen/configs/<ACTIVE format>-10-<level>-<number>/v1.json`; extend Task 2 test files and skip documentation.

**Interfaces:** Scalar polynomial coefficients/factors in configs; oracle stdlib coefficient maps keyed by exponent tuple, exact Fraction addition/multiplication/substitution. No symbolic evaluator production or new dependency.

- [x] Write `test_indicator_10_math`: sum/distributivity/factors/coefficients; fixture `(3x−m)(2x+4)=6x²+nx−20` gives m=5,n=2,m²−n²=21; perimeter delta 20; wrong negative-division step final −3y with x≠0. Include a false identity matching at one substitution to prove oracle does not rely on a single point.
- [x] Run targeted suite; expect missing recipes.
- [x] Construct factorable forms and derived coefficient claims; preserve cancellations, rational restrictions, positive geometric domain and original truth counts. Render compound powers as `(expression)^2`, fractions with grouped numerator/denominator, decimal comma and signs without ambiguous `+ -` output.
- [x] Check `kategori-10-2-10` and other conceptual statements against `same_answer_as_original`; defer where correct texts remain fixed. Add no config for deferred questions.
- [x] Implement independent coefficient identity/factor/substitution checks for every active statement; run reproduction/seed stock tests, expect PASS. Inspect algebra and explanations after rendering.

### Task 7: Registrasi, CLI/UI, audit, dokumentasi

**Files:** Modify `variant_gen/bank.py`, `variant_gen/tests/test_drill_6_10.py`, existing bank-count assertions in `variant_gen/tests/test_drill_20_23.py` as needed; extend `variant_gen/tests/test_webui.py` only for uncovered behavior. Modify `variant_gen/webui.py`/`webui.html` only if an observed gap requires it. Update `variant_gen/soalskip.md`, `variant_gen/README.md`, `docs/GENERATOR.md`. Create `docs/audits/2026-10-05-drill-6-10-generator-audit.json` and `.md`.

**Interfaces:** `load_workspace_bank(path, additional_paths=None)` default adds the new bank, custom bank stays standalone. Existing CLI gen/view/regen and HTTP catalog/generation/history routes; existing record/hash/version format remains unchanged.

- [x] Write `test_workspace_registration`: all currently installed banks union exactly once, original content/hash unchanged, custom CSV remains standalone, duplicate IDs still rejected. Adapt old hardcoded workspace totals by including independently installed 11–15 if present.
- [x] Write `test_local_end_to_end`: temporary store/config dirs, generate/view/regenerate one ACTIVE each format, category snapshot, deterministic seed, version/history preservation, stale-config refusal. Cover HOLD both direct and forged config/cached-result attempts, missing-key original display with no fabricated answer. Patch DB connector to fail if accessed by these service-ai operations.
- [x] Run targeted integration tests; expect registration/display failures for the unregistered bank.
- [x] Register the bank with the smallest loader edit. Verify indicators 6–10/level filters, 4–5 empty-state, status/reason, original versus variant previews, explanation and history through existing UI. Reuse the same styling; change UI only for confirmed missing-key/status behavior.
- [x] Run `python -B -m unittest discover -s variant_gen/tests`; expect all suites PASS. Use CLI `gen`, `view`, `regen` with `--store` pointing to a temporary path; never write `variant_gen/store/variants.jsonl` during verification. Browser smoke checks: PG, MCMA, KATEGORI, HOLD, empty level; read playwright skill at execution if browser tooling is used.
- [x] Audit accepted candidates at independent seeds 201–400 across every ACTIVE, compare all options with oracle, report rejections and actual stock. Record SHA, status counts summing 150, reason per skipped ID, original reproduction results and commands. Zero unrecorded skips; zero unnoticed mathematical failures.
- [x] Update documentation with working CLI commands and indicator availability. Review final diff against preflight: no Numora/DB/.env/user-store changes, no removal of previous banks/configs. Report evidence and remaining HOLD/DEFERRED counts; do not claim full 150 generator coverage.

## Plan self-review

Coverage: source fidelity/status Task 1; five topic families Task 2–6; local end-to-end and nonregression Task 7. Review Focus cases have explicit test owners. Existing engine signatures retained; only proposed optional import flag is scoped to held missing-key sources. No implementation files changed while writing this plan. Execution waits for user review because the request explicitly asks for a plan before implementation.

Execution completed. Verification and rulings: [progress](2026-10-05-drill-6-10-generator-progress.md). Initial full baseline result was not retained; final full suite: 80 tests OK. No commit created.
