#!/usr/bin/env python3
"""Question variant generator.

  python cli.py gen   pg-18-3-1 s5          generate seed 5 (s1-20 = a range). Never overwrites.
  python cli.py regen pg-18-3-1 s5          new version of seed 5 (needs a newer config, or --reason)
  python cli.py view  pg-18-3-1 s5 [v2]     show a stored variant (latest if v omitted); s0 = original
  python cli.py lint  pg-18-3-1 [--n 100]   check a config before using it
  python cli.py hash  pg-18-3-1             print the original's hash (for writing a new config)
"""
import argparse
import json
import re
import sys
from pathlib import Path

from bank import BankError, OriginalBank
from config_store import ConfigError, ConfigStore, validate_config
from engine import GenerationError, cand_from_record, generate, make_record, original_record
from expr import ExprError
from lint import run_lint
from store import StoreError, VariantStore
from handoff import export_record

HERE = Path(__file__).resolve().parent
KNOWN_ERRORS = (BankError, ConfigError, GenerationError, StoreError, ExprError)


def parse_seeds(tok):
    m = re.fullmatch(r"(\d+)(?:-s?(\d+))?", re.sub(r"^(seed|s)", "", tok.lower()))
    if not m:
        raise ValueError(f"bad seed '{tok}' (use s5, seed5, 5 or s1-20)")
    a, b = int(m.group(1)), int(m.group(2) or m.group(1))
    if b < a or b - a > 999:
        raise ValueError("bad seed range (max 1000 seeds at once)")
    return list(range(a, b + 1))


def parse_ver(tok):
    m = re.fullmatch(r"v?(\d+)", tok.lower())
    if not m:
        raise ValueError(f"bad version '{tok}' (use v2 or 2)")
    return int(m.group(1))


def show(rec, as_json):
    if as_json:
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return
    if rec["seed"] == 0:
        print(f"{rec['question_id']} | seed 0 (ORIGINAL, read-only) | {rec['format']} {rec['cognitive_level']}")
    else:
        extra = f" | replaces v{rec['replacement_of']}" if rec.get("replacement_of") else ""
        print(f"{rec['question_id']} | seed {rec['seed']} | variant v{rec['variant_ver']} | "
              f"config v{rec['config_ver']} | draws {rec['draws_used']}{extra}")
        print("values: " + ", ".join(f"{k}={v}" for k, v in rec["values_used"].items()))
    print("-" * 60)
    print(rec["stem"])
    for o in rec["options"]:
        print(f"  {o['id']}. {o['text']}")
    print(f"key: {rec['key']}")
    if rec.get("explanation"):
        print("pembahasan: " + rec["explanation"])
    print()


def load_config(configs, store, orig):
    """Newest config, validated, and checked not to have been edited after it produced variants."""
    cfg, h = configs.load(orig["id"])
    errs = validate_config(cfg, orig)
    if errs:
        raise ConfigError(f"config v{cfg['config_version']} has problems (run lint):\n  - " + "\n  - ".join(errs))
    for r in store.for_question(orig["id"]):
        if r["config_ver"] == cfg["config_version"] and r["config_hash"] != h:
            raise ConfigError(f"config v{cfg['config_version']} was edited after variants were generated from it. "
                              f"Revert it and save your change as v{cfg['config_version'] + 1}.")
    return cfg, h


def others_for(store, qid, seed):
    """Candidates a new variant of `seed` must not duplicate: every OTHER seed's latest variant,
    plus all earlier versions of this same seed."""
    out = [cand_from_record(r) for s, r in store.latest_by_seed(qid).items() if s != seed]
    out += [cand_from_record(r) for r in store.versions_of_seed(qid, seed)]
    return out


def cmd_gen(a, bank, configs, store):
    orig, bad = bank.get(a.question_id), 0
    for seed in parse_seeds(a.seeds):
        try:
            if seed == 0:
                show(original_record(orig), a.json)
                continue
            existing = store.get(orig["id"], seed)
            if existing:
                print(f"(seed {seed} already exists - showing stored v{existing['variant_ver']}, nothing overwritten)",
                      file=sys.stderr)
                show(existing, a.json)
                continue
            cfg, h = load_config(configs, store, orig)
            res = generate(orig, cfg, seed, others_for(store, orig["id"], seed))
            rec = make_record(orig, cfg, h, seed, 1, res)
            store.append(rec)
            show(rec, a.json)
        except KNOWN_ERRORS as e:
            bad += 1
            print(f"error (seed {seed}): {e}", file=sys.stderr)
    return 1 if bad else 0


def cmd_regen(a, bank, configs, store):
    orig = bank.get(a.question_id)
    (seed,) = parse_seeds(a.seed)
    if seed == 0:
        raise StoreError("seed 0 is the original and can never be regenerated")
    prev = store.get(orig["id"], seed)
    if not prev:
        raise StoreError(f"seed {seed} has no variant yet - use gen first")
    cfg, h = load_config(configs, store, orig)
    reason = (a.reason or "").strip() or None
    if cfg["config_version"] < prev["config_ver"]:
        raise ConfigError("regen cannot use an older config version")
    if cfg["config_version"] == prev["config_ver"] and not reason:
        raise ConfigError("regen with the same config requires a non-empty --reason")
    res = generate(orig, cfg, seed, others_for(store, orig["id"], seed))
    reason = reason or "new config"
    rec = make_record(orig, cfg, h, seed, prev["variant_ver"] + 1, res, prev["variant_ver"], reason)
    store.append(rec)
    show(rec, a.json)
    return 0


def cmd_view(a, bank, configs, store):
    orig = bank.get(a.question_id)
    (seed,) = parse_seeds(a.seed)
    if seed == 0:
        show(original_record(orig), a.json)
        return 0
    ver = parse_ver(a.ver) if a.ver else None
    rec = store.get(orig["id"], seed, ver)
    if not rec:
        have = [f"v{r['variant_ver']}" for r in store.versions_of_seed(orig["id"], seed)]
        raise StoreError(f"no stored variant for seed {seed}" + (f" {a.ver}" if a.ver else "")
                         + (f" (have: {', '.join(have)})" if have else ""))
    show(rec, a.json)
    return 0


def cmd_lint(a, bank, configs, store):
    orig = bank.get(a.question_id)
    cfg, _ = configs.load(orig["id"])
    print(f"lint {orig['id']} (config v{cfg['config_version']})")
    ok, lines = run_lint(orig, cfg, a.n)
    print("\n".join(lines))
    return 0 if ok else 1


def cmd_hash(a, bank, configs, store):
    print(bank.get(a.question_id)["hash"])
    return 0


def cmd_export(a, bank, configs, store):
    (seed,) = parse_seeds(a.seed)
    rec = store.get(a.question_id, seed, parse_ver(a.ver) if a.ver else None)
    if not rec:
        raise StoreError("no stored variant; generate a non-zero seed first")
    try:
        mapping = json.loads(Path(a.mapping).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise StoreError(f"cannot read mapping: {error}") from error
    print(json.dumps(export_record(rec, mapping), ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--bank", default=HERE / "data" / "q0_bank.csv")
    common.add_argument("--configs", default=HERE / "configs")
    common.add_argument("--store", default=HERE / "store" / "variants.jsonl")
    common.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap = argparse.ArgumentParser(prog="variant_gen", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("gen", parents=[common]); p.add_argument("question_id"); p.add_argument("seeds"); p.set_defaults(fn=cmd_gen)
    p = sub.add_parser("regen", parents=[common]); p.add_argument("question_id"); p.add_argument("seed")
    p.add_argument("--reason", default=None); p.set_defaults(fn=cmd_regen)
    p = sub.add_parser("view", parents=[common]); p.add_argument("question_id"); p.add_argument("seed")
    p.add_argument("ver", nargs="?"); p.set_defaults(fn=cmd_view)
    p = sub.add_parser("lint", parents=[common]); p.add_argument("question_id")
    p.add_argument("--n", type=int, default=100); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("hash", parents=[common]); p.add_argument("question_id"); p.set_defaults(fn=cmd_hash)
    p = sub.add_parser("export", parents=[common]); p.add_argument("question_id"); p.add_argument("seed")
    p.add_argument("ver", nargs="?"); p.add_argument("--mapping", required=True); p.set_defaults(fn=cmd_export)
    a = ap.parse_args(argv)
    try:
        return a.fn(a, OriginalBank(a.bank), ConfigStore(a.configs), VariantStore(a.store))
    except (ValueError, *KNOWN_ERRORS) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
