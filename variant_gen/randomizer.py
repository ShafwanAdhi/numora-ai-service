"""Variable generators. Each one gets its OWN seeded RNG, so changing one variable's range in a new
config does not reshuffle the values of the other variables for the same seed."""
import hashlib
import math
import random
from fractions import Fraction

from expr import ExprError, is_num, norm, round_half_up, to_num


def rng_for(qid, seed, draw, label):
    h = hashlib.sha256(f"{qid}|{seed}|{draw}|{label}".encode()).digest()   # stable across runs (unlike hash())
    return random.Random(int.from_bytes(h[:8], "big"))


def draw_variable(name, spec, rng):
    """gen = range | choice | scale. ('derived' is computed by the engine, not drawn.)"""
    gen = spec["gen"]
    if gen == "range":
        lo, hi = (Fraction(to_num(x)) for x in spec["range"])
        step = Fraction(to_num(spec.get("step", 1)))
        kmin, kmax = math.ceil(lo / step), math.floor(hi / step)      # values are multiples of step
        if kmin > kmax:
            raise ExprError(f"variable '{name}': no multiple of {step} inside {spec['range']}")
        return norm(rng.randint(kmin, kmax) * step)
    if gen == "choice":
        v = rng.choice(spec["values"])
        return to_num(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
    if gen == "scale":                                                 # original value * factor range
        base = Fraction(to_num(spec["base"]))
        flo, fhi = (Fraction(to_num(x)) for x in spec["factor"])
        step = Fraction(to_num(spec.get("step", 1)))
        f = flo + (fhi - flo) * Fraction(rng.randint(0, 1000), 1000)
        return norm(round_half_up(base * f / step) * step)
    raise ExprError(f"variable '{name}': unknown gen '{gen}'")
