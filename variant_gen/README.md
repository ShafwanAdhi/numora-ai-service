# variant_gen

Generates question variants from an original (CSV) plus a per-question JSON config.
IRT is not part of this; record fields leave room for it later.

## Commands
```
python cli.py gen   PG-18-3-1 s5         # generate seed 5 (s1-20 = a range). Never overwrites an existing seed.
python cli.py regen PG-18-3-1 s5         # new version of seed 5 with the NEWEST config
python cli.py regen PG-18-3-1 s5 --reason "bad numbers"   # re-roll with the same config
python cli.py view  PG-18-3-1 s5 v2      # stored variant (latest if v omitted). s0 = the original
python cli.py lint  PG-18-3-1 --n 100    # check a config before using it
python cli.py hash  PG-18-3-1            # original's hash, to paste into a new config
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
`{placeholder}`; PG exactly one correct; MCMA at least one and same count as the original; Kategori same count
as the original (0..all is legal); not same as original; not same correct answer as original; not a duplicate.

## Output record
`question_id, seed, variant_ver, config_ver, draws_used, values_used, stem, options[{id,text}], key,
format, cognitive_level, original_hash, original_version, replacement_of, regen_reason, created_at, config_hash`

## Layout
`cli.py` commands | `bank.py` originals (read-only) | `config_store.py` configs + schema check | `engine.py` pipeline
| `randomizer.py` variable generators | `expr.py` safe formulas, templates, number format | `filters.py` all accept/reject
rules | `store.py` append-only variants (`store/variants.jsonl`) | `lint.py` config checker
