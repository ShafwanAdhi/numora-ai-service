"""All accept/reject rules live here.

Two kinds:
  1. variable filters  - applied to each variable's value, named in the config
                         ("filters": ["nominus", "nodec", "step100"], plus "min"/"max"/"step" keys);
  2. global validators - applied to every finished candidate, always, no config needed
                         (not-the-same-as-original, no duplicates, exactly one correct for PG, ...).

Both only ever return reasons; the engine decides to try the next draw.
"""
import re
from fractions import Fraction

from expr import PLACEHOLDER, is_num, to_num

# --------------------------------------------------------- variable filters
VAR_FILTERS = {
    "nominus": lambda v: v >= 0,                      # no negative numbers
    "positive": lambda v: v > 0,                      # strictly > 0
    "nozero": lambda v: v != 0,
    "nodec": lambda v: Fraction(v).denominator == 1,  # whole numbers only
}
STEP_RE = re.compile(r"^step(\d+(?:\.\d+)?)$")        # "step100" -> multiple of 100


def is_valid_filter(name):
    return name in VAR_FILTERS or bool(STEP_RE.match(name))


def _passes(name, value):
    if name in VAR_FILTERS:
        return VAR_FILTERS[name](value)
    step = Fraction(STEP_RE.match(name).group(1))
    return Fraction(value) % step == 0


def check_variable(name, spec, value):
    """Return a list of failure reasons for one variable value (empty = ok)."""
    reasons = []
    numeric = is_num(value)
    for f in spec.get("filters", []):
        if not numeric:
            reasons.append(f"filter:{name}:{f} (value is not a number)")
        elif not _passes(f, value):
            reasons.append(f"filter:{name}:{f}")
    if numeric:
        if "min" in spec and value < to_num(spec["min"]):
            reasons.append(f"filter:{name}:min")
        if "max" in spec and value > to_num(spec["max"]):
            reasons.append(f"filter:{name}:max")
        if "step" in spec and Fraction(value) % Fraction(to_num(spec["step"])) != 0:
            reasons.append(f"filter:{name}:step")
    return reasons


# ------------------------------------------------------- global validators
def _n(s):
    return " ".join(str(s).split()).casefold()


def signature(stem, options):
    """Order-independent identity of a question: stem + set of (option text, is_correct)."""
    return (_n(stem), tuple(sorted((_n(o["text"]), bool(o["correct"])) for o in options)))


def correct_set(options):
    return frozenset(_n(o["text"]) for o in options if o["correct"])


def validate_candidate(cand, orig, others, *, allow_same_answer=False):
    """cand/orig: {stem, options:[{id,text,correct}], ...}. others: candidates that already exist.
    Returns a list of failure codes (empty = candidate is acceptable)."""
    p = []
    opts = cand["options"]
    fmt = orig["format"]

    if len(opts) != len(orig["options"]):
        p.append("option_count_differs_from_original")
    if not cand["stem"].strip() or any(not o["text"].strip() for o in opts):
        p.append("empty_text")
    if PLACEHOLDER.search(cand["stem"]) or any(PLACEHOLDER.search(o["text"]) for o in opts):
        p.append("unresolved_placeholder")
    if "explanation" in cand:
        if not cand["explanation"].strip():
            p.append("empty_explanation")
        if PLACEHOLDER.search(cand["explanation"]):
            p.append("unresolved_explanation_placeholder")
    texts = [_n(o["text"]) for o in opts]
    if len(set(texts)) != len(texts):
        p.append("options_not_distinct")

    n_ok = sum(1 for o in opts if o["correct"])
    n_orig = sum(1 for o in orig["options"] if o["correct"])
    if fmt == "PG" and n_ok != 1:
        p.append("pg_needs_exactly_one_correct")
    elif fmt == "MCMA" and (n_ok < 1 or n_ok != n_orig):
        p.append("mcma_correct_count_differs_from_original")
    elif fmt == "KATEGORI" and n_ok != n_orig:   # 0..all is legal, but keep the original's count
        p.append("kategori_correct_count_differs_from_original")

    sig = signature(cand["stem"], opts)
    if sig == signature(orig["stem"], orig["options"]):
        p.append("same_as_original")
    if not allow_same_answer and correct_set(opts) == correct_set(orig["options"]):
        p.append("same_answer_as_original")
    for o in others:
        if signature(o["stem"], o["options"]) == sig:
            p.append("duplicate_of_existing_variant")
            break
    return p
