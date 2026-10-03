"""Config files: configs/<question_id>/v<N>.json. A new version is a new file; a version that has
already produced variants must never be edited (the engine checks this with a content hash)."""
import hashlib
import json
import re
from pathlib import Path

from expr import ExprError, expr_names, parse, placeholders, to_num
from filters import is_valid_filter

DEFAULT_MAX_DRAWS = 200
GENS = {
    "range": ({"range"}, {"step"}),
    "choice": ({"values"}, set()),
    "scale": ({"base", "factor"}, {"step"}),
    "derived": ({"expr"}, set()),
}
COMMON_KEYS = {"gen", "filters", "min", "max", "step", "fmt", "decimals"}
REQUIRED_TOP = ("question_id", "config_version", "original_hash", "original_values", "variables", "stem", "options")


class ConfigError(Exception):
    pass


def config_hash(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


class ConfigStore:
    def __init__(self, root):
        self.root = Path(root)

    def versions(self, qid):
        d = self.root / qid
        if not d.is_dir():
            return []
        return sorted(int(m.group(1)) for p in d.glob("v*.json") if (m := re.fullmatch(r"v(\d+)\.json", p.name)))

    def load(self, qid, version=None):
        vs = self.versions(qid)
        if not vs:
            raise ConfigError(f"no config found for '{qid}' (expected configs/{qid}/v1.json)")
        version = vs[-1] if version is None else version
        path = self.root / qid / f"v{version}.json"
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise ConfigError(f"cannot read {path}: {e}")
        if cfg.get("config_version") != version or cfg.get("question_id") != qid:
            raise ConfigError(f"{path}: question_id/config_version inside the file do not match its location")
        return cfg, config_hash(cfg)


def validate_config(cfg, orig):
    """Return a list of human-readable problems (empty list = config is well-formed)."""
    errs = []
    for k in REQUIRED_TOP:
        if k not in cfg:
            errs.append(f"missing '{k}'")
    if errs:
        return errs
    if cfg["original_hash"] != orig["hash"]:
        errs.append(f"original_hash {cfg['original_hash']} != current {orig['hash']}: "
                    f"the original changed since this config was written")
    md = cfg.get("max_draws", DEFAULT_MAX_DRAWS)
    if not isinstance(md, int) or isinstance(md, bool) or not 1 <= md <= 10000:
        errs.append("max_draws must be an integer 1..10000")
    if not isinstance(cfg.get("shuffle", False), bool):
        errs.append("shuffle must be true or false")

    defined = []
    for name, spec in cfg["variables"].items():
        gen = spec.get("gen")
        if gen not in GENS:
            errs.append(f"variable '{name}': gen must be one of {sorted(GENS)}")
            continue
        need, extra = GENS[gen]
        for k in need:
            if k not in spec:
                errs.append(f"variable '{name}' ({gen}) needs '{k}'")
        for k in set(spec) - need - extra - COMMON_KEYS:
            errs.append(f"variable '{name}': unknown key '{k}'")
        for f in spec.get("filters", []):
            if not is_valid_filter(f):
                errs.append(f"variable '{name}': unknown filter '{f}'")
        try:
            if gen == "derived":
                bad = expr_names(spec["expr"]) - set(defined)
                if bad:
                    errs.append(f"variable '{name}': uses {sorted(bad)} before they are defined")
            elif gen == "range":
                lo, hi = spec["range"]; to_num(lo); to_num(hi)
            elif gen == "choice" and not spec["values"]:
                errs.append(f"variable '{name}': 'values' is empty")
            elif gen == "scale":
                to_num(spec["base"]); [to_num(x) for x in spec["factor"]]
        except (ExprError, ValueError, TypeError) as e:
            errs.append(f"variable '{name}': {e}")
        if gen != "derived" and name not in cfg["original_values"]:
            errs.append(f"original_values is missing '{name}'")
        defined.append(name)
    allv = set(defined)

    for c in cfg.get("constraints", []):
        try:
            bad = expr_names(c) - allv
            if bad:
                errs.append(f"constraint '{c}': unknown variables {sorted(bad)}")
        except ExprError as e:
            errs.append(f"constraint: {e}")

    def check_tpl(label, tpl):
        bad = placeholders(tpl) - allv
        if bad:
            errs.append(f"{label}: undeclared placeholders {sorted(bad)}")

    check_tpl("stem", cfg["stem"])
    opts = cfg["options"]
    if len(opts) != len(orig["options"]):
        errs.append(f"config has {len(opts)} options, the original has {len(orig['options'])}")
    for i, o in enumerate(opts):
        if i < len(orig["options"]) and o.get("id") != orig["options"][i]["id"]:
            errs.append(f"option {i + 1}: id '{o.get('id')}' should be '{orig['options'][i]['id']}' (same order as the original)")
        if "text" not in o or "correct" not in o:
            errs.append(f"option {i + 1}: needs 'text' and 'correct'")
            continue
        check_tpl(f"option {o.get('id')}", o["text"])
        c = o["correct"]
        if isinstance(c, str):
            try:
                bad = expr_names(c) - allv
                if bad:
                    errs.append(f"option {o['id']} correct-formula: unknown variables {sorted(bad)}")
            except ExprError as e:
                errs.append(f"option {o['id']} correct-formula: {e}")
        elif not isinstance(c, bool):
            errs.append(f"option {o['id']}: 'correct' must be true, false or a formula string")
    return errs
