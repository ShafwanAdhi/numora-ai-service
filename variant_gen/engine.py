"""One variant = one pipeline: draw variables -> filters -> derived -> constraints -> render ->
(shuffle) -> global validators. Anything that fails just means "try the next draw"; after
max_draws failed draws generation stops with an error and NOTHING is stored."""
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone

from config_store import DEFAULT_MAX_DRAWS, ConfigError, validate_config
from expr import RejectDraw, evaluate, is_num, json_number, norm, render, to_num
from filters import check_variable, validate_candidate
from randomizer import draw_variable, rng_for


class GenerationError(Exception):
    def __init__(self, limit, rejections):
        self.limit, self.rejections = limit, rejections
        top = ", ".join(f"{k} x{v}" for k, v in rejections.most_common(5)) or "none"
        super().__init__(f"no acceptable variant within {limit} draws. Top rejection reasons: {top}")


@dataclass
class Result:
    values: dict
    cand: dict
    draws_used: int
    rejections: Counter


def build_values(cfg, source, check=True):
    """Resolve every variable in declared order. source(name, spec) supplies non-derived values
    (random draw in generation, original_values in lint). Derived variables are formulas."""
    values = {}
    for name, spec in cfg["variables"].items():
        v = evaluate(spec["expr"], values) if spec["gen"] == "derived" else source(name, spec)
        if check:
            bad = check_variable(name, spec, v)
            if bad:
                raise RejectDraw(bad[0])
        values[name] = v
    if check:
        for c in cfg.get("constraints", []):
            if not evaluate(c, values):
                raise RejectDraw(f"constraint failed: {c}")
    return values


def assemble(cfg, values):
    fmts = {n: {"fmt": s.get("fmt", "id"), "decimals": s.get("decimals", 2)} for n, s in cfg["variables"].items()}
    options = []
    for o in cfg["options"]:
        corr = o["correct"]
        if isinstance(corr, str):
            corr = bool(evaluate(corr, values))
        options.append({"id": o["id"], "text": render(o["text"], values, fmts), "correct": bool(corr)})
    return {"stem": render(cfg["stem"], values, fmts), "options": options,
            "explanation": render(cfg["explanation"], values, fmts)}


def shuffle_options(cand, rng, ids):
    """Random order, then relabel A,B,C.. (or 1,2,3..) by position. The key follows the options."""
    rng.shuffle(cand["options"])
    for o, i in zip(cand["options"], ids):
        o["id"] = i


def key_of(cand):
    return ",".join(o["id"] for o in cand["options"] if o["correct"])


def cand_from_record(rec):
    ok = set(k for k in rec["key"].split(",") if k)
    return {"stem": rec["stem"], "options": [{"id": o["id"], "text": o["text"], "correct": o["id"] in ok}
                                              for o in rec["options"]]}


def generate(orig, cfg, seed, others):
    """Generate one candidate; others is an optional in-memory comparison set for audits."""
    if orig.get("metadata", {}).get("generation_status", "ACTIVE") != "ACTIVE":
        raise ConfigError(orig["metadata"]["reason"])
    qid, limit = orig["id"], cfg.get("max_draws", DEFAULT_MAX_DRAWS)
    problems = validate_config(cfg, orig)
    if problems:
        raise ConfigError("; ".join(problems))
    ids = [o["id"] for o in orig["options"]]
    rejections = Counter()
    for draw in range(limit):
        def source(name, spec, d=draw):
            return draw_variable(name, spec, rng_for(qid, seed, d, name))
        try:
            values = build_values(cfg, source)
            cand = assemble(cfg, values)
            if cfg.get("shuffle"):
                shuffle_options(cand, rng_for(qid, seed, draw, "__shuffle__"), ids)
        except RejectDraw as e:
            rejections[str(e)] += 1
            continue
        problems = validate_candidate(cand, orig, others)
        if problems:
            rejections.update(problems)
            continue
        return Result(values, cand, draw + 1, rejections)
    raise GenerationError(limit, rejections)


def make_record(orig, cfg, cfg_hash, seed, ver, result, replacement_of=None, reason=None):
    c = result.cand
    labels = orig.get("metadata", {}).get("category_labels", ["Benar", "Salah"])
    if orig["format"] == "PG":
        answers = "Jawaban: " + "; ".join(f"{o['id']}. {o['text']}" for o in c["options"] if o["correct"])
    else:
        answers = "Penilaian pernyataan: " + "; ".join(
            f"{o['id']}: {labels[0] if o['correct'] else labels[1]} — {o['text']}" for o in c["options"])
    return {
        "record_id": f"{orig['id']}:s{seed}:v{ver}",
        "question_id": orig["id"], "seed": seed, "variant_ver": ver,
        **({"classification": orig["classification"]} if "classification" in orig else {}),
        **({"metadata": {k:v for k,v in orig["metadata"].items() if k not in ("source_text", "original_explanation")}} if "metadata" in orig else {}),
        "config_ver": cfg["config_version"], "config_hash": cfg_hash, "draws_used": result.draws_used,
        "format": orig["format"], "cognitive_level": orig["cognitive_level"],
        "values_used": {k: (json_number(v) if is_num(v) else v) for k, v in result.values.items()},
        "stem": c["stem"], "options": [{"id": o["id"], "text": o["text"]} for o in c["options"]],
        "key": key_of(c),
        **({"answer_categories": {o["id"]: labels[0] if o["correct"] else labels[1] for o in c["options"]}}
           if orig["format"] == "KATEGORI" and labels != ["Benar", "Salah"] else {}),
        "explanation": c["explanation"] + "\n\n" + answers,
        "original_hash": orig["hash"], "original_version": orig["version"],
        "replacement_of": replacement_of, "regen_reason": reason,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def original_record(orig):
    """Seed 0 = the original, shown in the same shape as a variant (never stored, never changed)."""
    labels = orig.get("metadata", {}).get("category_labels", ["Benar", "Salah"])
    return {
        "record_id": f"{orig['id']}:s0", "question_id": orig["id"], "seed": 0, "variant_ver": None,
        **({"classification": orig["classification"]} if "classification" in orig else {}),
        **({"metadata": orig["metadata"]} if "metadata" in orig else {}),
        "config_ver": None, "draws_used": None, "format": orig["format"], "cognitive_level": orig["cognitive_level"],
        "values_used": {}, "stem": orig["stem"],
        "options": [{"id": o["id"], "text": o["text"]} for o in orig["options"]],
        "key": key_of(orig), "original_hash": orig["hash"], "original_version": orig["version"],
        **({"answer_categories": {o["id"]: labels[0] if o["correct"] else labels[1] for o in orig["options"]}}
           if orig["format"] == "KATEGORI" and labels != ["Benar", "Salah"] else {}),
        **({"explanation": orig["metadata"]["original_explanation"]} if orig.get("metadata", {}).get("original_explanation") else {}),
    }
