# Audit dan impor original indikator 20-23 level 4-5

> Execute inline with superpowers:executing-plans. User already authorized audit and import; no additional approval checkpoint.

**Goal:** Audit 80 archived originals, then expose them through the local bank and workbench.
**Architecture:** Separate source-only CSV, metadata, catalog and per-question audit. Existing loader merges this folder with the unchanged 120 level 1-3 originals.
**Tech Stack:** Python standard library; existing bank, catalog and HTTP workbench.
**Spec:** User request: audit, lalu impor ke bank aktif. Source: `docs/sources/incoming/2026-10-19-indikator-20-23/`.

## Constraints and review focus

- No database writes, generators, stocks, source corrections, publication, commit or push.
- Keep source numbers 31-50; map runtime positions to 1-10 per level.
- Preserve five-option MCMA and PG; retain category labels and every data table.
- Keep primary declared key, even when explanation proposes another; mark contradictions HOLD_SOURCE.
- Preserve original DOCX hash, raw source, cognitive labels, source locations and old bank contents.
- ACTIVE means source audit passed locally, not curriculum approval or IRT calibration.

## Tasks

- [x] Add failing tests: 80 originals; 10 per indicator/level; table preservation; complete MCMA keys; conflicts held; all 200 originals visible; no DB/storage writes.
- [x] Audit each question independently; record option truth sets, derivations, assumptions and precise blocking issues.
- [x] Implement source-specific importer using existing extraction and stdlib. Validate all files before writes; refuse changed output overwrites.
- [x] Add loader path. Run importer twice; verify unchanged output hashes on second run.
- [x] Run new tests, existing indicators20-23, catalog, stock, workbench coverage. Document current totals and HOLD list; preserve historical snapshots.

## Execution ledger

- Ruling: separate folder avoids rewriting established level1-3 bank and historical intake tests.
- Ruling: repair extraction structure only; do not apply mathematical corrections embedded in explanations to the primary source key.

- Result:80 imported,67 ACTIVE,13 HOLD;44 tests pass. No source corrections, generators, stocks or DB writes.
