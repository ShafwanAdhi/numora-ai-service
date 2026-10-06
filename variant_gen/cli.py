#!/usr/bin/env python3
"""Question variant generator.

  python cli.py gen   pg-18-3-1 s5          generate seed 5 (s1-20 = a range), output only
  python cli.py view  pg-18-3-1 s5          generate a preview; s0 = original
  python cli.py lint  pg-18-3-1 [--n 100]   check a config before using it
  python cli.py hash  pg-18-3-1             print the original's hash (for writing a new config)
"""
import argparse
import json
import re
import sys
from pathlib import Path

from bank import BankError, OriginalBank, load_workspace_bank
from config_store import ConfigError, ConfigStore, validate_config
from engine import GenerationError, generate, make_record, original_record
from expr import ExprError
from lint import run_lint
from store import StoreError
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
    metadata = rec.get("metadata", {})
    held = metadata.get("generation_status") == "HOLD_SOURCE"
    if metadata.get("generation_status"):
        print("status: " + metadata["generation_status"])
    if metadata.get("reason"):
        print(metadata["reason"])
    print(rec["stem"])
    for o in rec["options"]:
        print(f"  {o['id']}. {o['text']}")
    if rec.get("answer_categories"):
        print("kategori: " + "; ".join(f"{qid}: {label}" for qid,label in rec["answer_categories"].items()))
    else:
        print(f"{'key sumber (belum disahkan)' if held else 'key'}: {rec['key'] or 'Belum tersedia'}")
    if rec.get("explanation"):
        print(("pembahasan sumber (belum disahkan): " if held else "pembahasan: ") + rec["explanation"])
    print()


def load_config(configs, orig):
    """Load and validate the newest config; no variant history is retained."""
    cfg, h = configs.load(orig["id"])
    errs = validate_config(cfg, orig)
    if errs:
        raise ConfigError(f"config v{cfg['config_version']} has problems (run lint):\n  - " + "\n  - ".join(errs))
    return cfg, h


def preview(bank, configs, qid, seed):
    orig = bank.get(qid)
    if seed == 0:
        return original_record(orig)
    cfg, h = load_config(configs, orig)
    return make_record(orig, cfg, h, seed, 1, generate(orig, cfg, seed, []))


def cmd_gen(a, bank, configs):
    orig, bad = bank.get(a.question_id), 0
    for seed in parse_seeds(a.seeds):
        try:
            show(preview(bank, configs, orig['id'], seed), a.json)
        except KNOWN_ERRORS as e:
            bad += 1
            print(f"error (seed {seed}): {e}", file=sys.stderr)
    return 1 if bad else 0


def cmd_view(a, bank, configs):
    (seed,) = parse_seeds(a.seed)
    show(preview(bank, configs, a.question_id, seed), a.json)
    return 0


def cmd_lint(a, bank, configs):
    orig = bank.get(a.question_id)
    cfg, _ = configs.load(orig["id"])
    print(f"lint {orig['id']} (config v{cfg['config_version']})")
    ok, lines = run_lint(orig, cfg, a.n)
    print("\n".join(lines))
    return 0 if ok else 1


def cmd_hash(a, bank, configs):
    print(bank.get(a.question_id)["hash"])
    return 0


def cmd_export(a, bank, configs):
    (seed,) = parse_seeds(a.seed)
    if seed == 0:
        raise StoreError("export requires a non-zero variant seed")
    rec = preview(bank, configs, a.question_id, seed)
    try:
        mapping = json.loads(Path(a.mapping).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise StoreError(f"cannot read mapping: {error}") from error
    print(json.dumps(export_record(rec, mapping), ensure_ascii=False, indent=2))
    return 0


def cmd_package_gen(a, bank, configs):
    from tryout import generate_package
    (seed,) = parse_seeds(a.seed)
    result=generate_package(bank,configs,a.package_id,seed)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--bank", default=HERE / "data" / "q0_bank.csv")
    common.add_argument("--configs", default=HERE / "configs")
    common.add_argument("--store", help=argparse.SUPPRESS)  # Legacy argument, ignored; no file is read/written.
    common.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap = argparse.ArgumentParser(prog="variant_gen", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("gen", parents=[common]); p.add_argument("question_id"); p.add_argument("seeds"); p.set_defaults(fn=cmd_gen)
    p = sub.add_parser("view", parents=[common]); p.add_argument("question_id"); p.add_argument("seed")
    p.set_defaults(fn=cmd_view)
    p = sub.add_parser("lint", parents=[common]); p.add_argument("question_id")
    p.add_argument("--n", type=int, default=100); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("hash", parents=[common]); p.add_argument("question_id"); p.set_defaults(fn=cmd_hash)
    p = sub.add_parser("export", parents=[common]); p.add_argument("question_id"); p.add_argument("seed")
    p.add_argument("--mapping", required=True); p.set_defaults(fn=cmd_export)
    p=sub.add_parser('package-gen',parents=[common]);p.add_argument('package_id');p.add_argument('seed')
    p.set_defaults(fn=cmd_package_gen)
    a = ap.parse_args(argv)
    try:
        return a.fn(a, load_workspace_bank(a.bank), ConfigStore(a.configs))
    except (OSError, ValueError, *KNOWN_ERRORS) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
