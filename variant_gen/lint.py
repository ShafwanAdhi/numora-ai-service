"""lint: check a config BEFORE using it.
  1. schema + original_hash;  2. the config, fed the original's values, must rebuild the original
  exactly (stem, every option, key);  3. sample N seeds in memory (store untouched) and report
  failures and how many DISTINCT variants the config can really produce."""
from collections import Counter

from config_store import validate_config
from engine import GenerationError, assemble, build_values, cand_from_record, generate
from expr import ExprError, RejectDraw, to_num


def _txt(s):
    return " ".join(str(s).split())


def reproduce_original(orig, cfg):
    problems, warnings = [], []
    ov = {k: (to_num(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
          for k, v in cfg["original_values"].items()}
    source = lambda name, spec: ov[name]
    try:
        values = build_values(cfg, source)
    except RejectDraw as e:
        warnings.append(f"the original's own values fail this config's rules ({e})")
        values = build_values(cfg, source, check=False)
    cand = assemble(cfg, values)
    if _txt(cand["stem"]) != _txt(orig["stem"]):
        problems.append(f"stem differs:\n      config  : {cand['stem']}\n      original: {orig['stem']}")
    for c, o in zip(cand["options"], orig["options"]):
        if _txt(c["text"]) != _txt(o["text"]):
            problems.append(f"option {o['id']} text differs: config '{c['text']}' vs original '{o['text']}'")
        if c["correct"] != o["correct"]:
            problems.append(f"option {o['id']} correctness differs: config {c['correct']} vs original {o['correct']}")
    return problems, warnings


def run_lint(orig, cfg, n=100):
    """Returns (ok, lines)."""
    lines, ok = [], True
    errs = validate_config(cfg, orig)
    if errs:
        return False, [f"  [x] config problems:"] + [f"      - {e}" for e in errs]
    lines.append("  [ok] schema and original_hash")
    try:
        problems, warnings = reproduce_original(orig, cfg)
    except (ExprError, RejectDraw) as e:
        return False, lines + [f"  [x] could not rebuild the original: {e}"]
    if problems:
        ok = False
        lines += ["  [x] config does NOT reproduce the original:"] + [f"      - {p}" for p in problems]
    else:
        lines.append("  [ok] reproduces the original exactly (stem, options, key)")
    lines += [f"  [!] {w}" for w in warnings]

    made, fails, draws, rej = [], 0, [], Counter()
    for seed in range(1, n + 1):
        try:
            r = generate(orig, cfg, seed, made)
        except GenerationError as e:
            fails += 1
            rej.update(e.rejections)
            continue
        made.append(r.cand)
        draws.append(r.draws_used)
        rej.update(r.rejections)
    lines.append(f"  sampled seeds 1..{n}: {len(made)} generated, {fails} failed "
                 f"(avg draws {sum(draws) / len(draws):.1f})" if draws else f"  sampled seeds 1..{n}: all {n} failed")
    if fails:
        lines.append(f"  [!] {fails} seeds hit max_draws: this config probably holds only ~{len(made)} distinct variants")
    if rej:
        lines.append("  most common rejections: " + ", ".join(f"{k} x{v}" for k, v in rej.most_common(4)))
    if not made:
        ok = False
    return ok, lines
