# variant_gen

Generates question variants from an original (CSV) plus a per-question JSON config.
IRT is not part of this; record fields leave room for it later.

## Commands
```
python cli.py gen   pg-18-3-1 s5         # generate seed 5 (s1-20 = a range). Never overwrites an existing seed.
python cli.py regen pg-18-3-1 s5         # new version of seed 5 with the NEWEST config
python cli.py regen pg-18-3-1 s5 --reason "bad numbers"   # re-roll with the same config
python cli.py view  pg-18-3-1 s5 v2      # stored variant (latest if v omitted). s0 = the original
python cli.py lint  pg-18-3-1 --n 100    # check a config before using it
python cli.py hash  pg-18-3-1            # original's hash, to paste into a new config
python cli.py export pg-18-3-1 s5 --mapping mapping.json  # JSON envelope for Numora import
```
Add `--json` for JSON output. `s5`, `seed5` and `5` are all accepted. Tests: `python -m unittest discover -s tests`.

## Rules the system enforces
* Seed 0 is the original. It is read-only (`bank.py` has no write path), `regen s0` is refused.
* A variant can never equal the original: same content, **or the same correct answer**, is rejected.
  It also can't duplicate any other stored variant (option order is ignored when comparing).
* `gen` never overwrites. `regen` appends variant v+1 (`replacement_of` points back); old versions stay.
  `regen` needs a newer config version or `--reason`.
* A config version that already produced variants must not be edited: change it and `gen`/`regen` stop.
  Save the change as the next version (`v2.json`).
* Each `gen` tries up to `max_draws` (default 200) random draws. If none passes every filter, constraint
  and validator, it fails with the top rejection reasons and **stores nothing**.
* Same question + seed + draw always gives the same numbers. Each variable has its own RNG, so editing one
  variable's range does not reshuffle the others. (Duplicate checks look at what is already stored, so
  the stored snapshot, not a re-run, is the source of truth; `view` reads the snapshot.)
* Static numbers in the stem (pi, "6 buah persegi") are plain text in the template; only `{placeholders}` vary.

## Config (configs/<question_id>/v<N>.json)
| key | meaning |
|---|---|
| `original_hash` | from `cli.py hash`; if the original changes, the config is refused |
| `original_values` | the original's variable values; `lint` rebuilds the original from them and must match exactly |
| `shuffle` | `false` keep option order, `true` random order (ids relabeled A,B,C / 1,2,3; key follows) |
| `max_draws` | optional, default 200 |
| `variables` | ordered; a variable may use earlier ones |
| `constraints` | formulas that must be true, e.g. `"p < q"`, `"q % 7 == 0"`; failing draws are redrawn |
| `stem`, `options` | templates with `{name}`; option `correct` is `true`/`false` or a formula (e.g. `"vol == alas*t2"`) |
| `explanation` | required solution template; rendered with the candidate's values and saved with the actual shuffled answer key |

Variable kinds (`gen`):
* `range`: `{"range":[lo,hi], "step":s}`, values are multiples of `step` (default 1; decimals fine: `0.5`)
* `choice`: `{"values":[...]}`, numbers or text (`["Pak Budi","Bu Siti"]`)
* `scale`: `{"base":12, "factor":[0.75,1.5], "step":1}`, original value x random factor, rounded to `step`
* `derived`: `{"expr":"3.14*r*r*t"}`, a formula; use `a if cond else b` for if-else

Per-variable filters: `"filters": ["nominus","positive","nozero","nodec","step100"]`, plus `"min"`, `"max"`,
`"step"`. Display: `"fmt":"id"` (default, `1.570` / `3,14`) or `"raw"` (no thousands dot), `"decimals"` (default 2).

Formulas allow `+ - * / // % **`, comparisons, `and/or/not`, `if/else`, and `abs min max round floor ceil sqrt gcd`.
Arithmetic is exact (fractions), `round` is half-up. Nothing else is evaluated (no `eval`).

Global validators (always on, `filters.py`): same option count as the original; options distinct; no unresolved
`{placeholder}`; PG exactly one correct; MCMA at least one and same count as the original; KATEGORI same count
as the original (0..all is legal); not same as original; not same correct answer as original; not a duplicate.

## Output record
`question_id, seed, variant_ver, config_ver, draws_used, values_used, stem, options[{id,text}], key,
explanation, format, cognitive_level, original_hash, original_version, replacement_of, regen_reason, created_at, config_hash`

## Numora handoff

`export` reads the stored snapshot, not the latest config, and prints the draft
`Numora/packages/contracts/questions/question-variant.schema.json` envelope:
`questionExternalId`, `variantExternalId`, `payload`, `answer`, `explanation`, `generation`.
It does not insert or publish anything in Numora. Import and academic review remain
Numora responsibilities; exports carry `generation.reviewStatus = REVIEW`.

Supply a mapping JSON object from Numora containing `questionExternalId`,
`originalHash`, `originalVersion`, `familyId`, `parentQuestionVersionId`,
`scoringRubricVersionId`, and optionally `generationWaveItemId`. The first three
must match the stored original; canonical IDs must be non-zero UUIDs supplied by
Numora. This offline check cannot prove those IDs exist or belong together: the
Numora importer must check that relationship against its database and pinned rubric.
The generator never invents canonical IDs or derives them from the local seed.

PG exports one correct option ID; MCMA exports the correct option IDs; KATEGORI
exports the truth value of **every** statement, including false statements.
Use `export <question_id> <seed> <version> --mapping ...` for a historical version.

Existing JSONL snapshots remain unchanged. Three already-used configurations have
new v2 files with explanations and current bank hashes; their v1 files are preserved.
Older stored variants without explanations cannot be exported. Run `regen` with
the new config to produce a new snapshot; `gen` on an existing seed still returns
the original stored snapshot. Solution templates still require Curriculum review.

## Layout
`cli.py` commands | `bank.py` originals (read-only) | `config_store.py` configs + schema check | `engine.py` pipeline
| `randomizer.py` variable generators | `expr.py` safe formulas, templates, number format | `filters.py` all accept/reject
rules | `store.py` append-only variants (`store/variants.jsonl`) | `lint.py` config checker | `handoff.py` Numora export

## Coverage and corrections — 4 October 2026

110 of 120 originals now have a config: 56/60 PG, 34/36 MCMA, 20/24 KATEGORI.
All 60 area/volume questions (groups 18–19) are covered. The 12 skipped questions
were reviewed in `soalskip.md`; two now have configs, ten require content/policy review.
Config availability does not approve Curriculum templates or empirical equivalence.

The latest configs for `kategori-16-3-10` and `pg-16-1-4` enforce cone slant height
greater than radius and square-pyramid face area greater than a quarter of base area.
Their v1 files stay intact. `pg-16-3-5` v2 constructs area/perimeter from a 3–4–5
right triangle instead of drawing incompatible values independently.

`data/original_revisions.jsonl` preserves the previous CSV row and its replacement.
`bank.py` applies this optional ledger after reading the CSV, checks source identity,
content hash and sequential versions, then exposes the revised read-only original.
Copy the ledger with the CSV when exporting the bank; a CSV-only copy is the old source.
This leaves the source CSV and stored variant snapshots intact.

Two local original corrections are version 2, pending Curriculum review:

* `pg-16-3-5`: two right-triangle bases total 12 cm² at perimeter 12 cm; total
  prism surface is 132 cm² at height 10 cm. The former 24 cm² is impossible.
* `mcma-19-3-6`: compare separate cube/pyramid solids; a 15 cm high pyramid
  cannot be inside a cube with 10 cm sides. Numbers and answer key stay the same.

New configs derive solutions and statement truth from generated values. Constraints
cover shape fit, positive dimensions, exact currency/unit conversions and displayed
precision. Decimal rounding in `mcma-19-3-8` is explicit in its explanation.

ponytail: conceptual questions keep the current different-answer rule; the reviewed
rotation config generates 180° candidates, the cube-scaling config has four unique
candidates. Broader conceptual templates require Curriculum/policy review.

Run `python -B -m unittest discover -s tests -v`. Geometry and bank coverage checks
are in `tests/test_bank_coverage.py`; tests generate candidates in memory/temp stores.
