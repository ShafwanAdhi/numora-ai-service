"""Safe formula evaluation and template rendering.

This is the ONLY place where strings coming from a config are evaluated.
  * no eval(), no str.format(): formulas go through a whitelisted AST walker,
    templates only substitute declared {name} placeholders;
  * arithmetic is exact (Fraction): 22/7 * 49 is exactly 154, never 154.00000000000003.
"""
import ast
import math
import re
from fractions import Fraction
from functools import lru_cache

MAX_LEN = 300          # max characters in one formula
MAX_NODES = 150        # max AST nodes in one formula
MAX_EXPONENT = 12      # a ** b only for small integer b
MAX_ABS = 10 ** 12     # any intermediate or final number above this rejects the draw


class ExprError(Exception):
    """The CONFIG is wrong (bad syntax, unknown name, forbidden construct). Abort, never retry."""


class RejectDraw(Exception):
    """This DRAW is unusable (division by zero, number too large, filter failed). Try the next draw."""


# ----------------------------------------------------------------- numbers
def is_num(x):
    return isinstance(x, (int, Fraction)) and not isinstance(x, bool)


def norm(x):
    """Fraction with denominator 1 -> int. Everything else unchanged."""
    if isinstance(x, Fraction) and x.denominator == 1:
        return int(x)
    return x


def to_num(x):
    """Config literal -> exact number. Floats go through str so 3.14 is exactly 157/50."""
    if isinstance(x, bool):
        raise ExprError(f"not a number: {x!r}")
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return norm(Fraction(str(x)))
    if isinstance(x, Fraction):
        return norm(x)
    raise ExprError(f"not a number: {x!r}")


def _num(x):
    if not is_num(x):
        raise ExprError(f"arithmetic on a non-number: {x!r}")
    return Fraction(x)


def round_half_up(x):
    x = Fraction(x)
    return math.floor(x + Fraction(1, 2)) if x >= 0 else -math.floor(-x + Fraction(1, 2))


def json_number(x):
    """Value -> something JSON can store (int, float or str)."""
    x = norm(x)
    if isinstance(x, Fraction):
        return round(float(x), 6)
    return x


# --------------------------------------------------------------- functions
def _round(x, nd=0):
    x, nd = _num(x), _num(nd)
    if nd.denominator != 1 or not 0 <= nd <= 6:
        raise ExprError("round(x, n): n must be an integer 0..6")
    scale = Fraction(10) ** int(nd)
    return Fraction(round_half_up(x * scale)) / scale


def _sqrt(x):
    x = _num(x)
    if x < 0:
        raise RejectDraw("sqrt of a negative number")
    n, d = x.numerator, x.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    if rn * rn == n and rd * rd == d:
        return Fraction(rn, rd)
    return Fraction(math.sqrt(float(x))).limit_denominator(10 ** 9)


def _gcd(a, b):
    a, b = _num(a), _num(b)
    if a.denominator != 1 or b.denominator != 1:
        raise ExprError("gcd needs integers")
    return Fraction(math.gcd(int(a), int(b)))


FUNCS = {
    "abs": lambda x: abs(_num(x)),
    "min": lambda *a: min(_num(x) for x in a),
    "max": lambda *a: max(_num(x) for x in a),
    "round": _round,                      # round HALF UP (school rounding), optional digits
    "floor": lambda x: Fraction(math.floor(_num(x))),
    "ceil": lambda x: Fraction(math.ceil(_num(x))),
    "sqrt": _sqrt,                        # exact when the root is rational
    "gcd": _gcd,
}

# ---------------------------------------------------------------- parsing
_ALLOWED = (
    ast.Expression, ast.Constant, ast.Name, ast.Load, ast.UnaryOp, ast.BinOp, ast.BoolOp,
    ast.Compare, ast.IfExp, ast.Call,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
)


@lru_cache(maxsize=4096)
def parse(expr):
    """Validate a formula. Returns (tree, frozenset_of_variable_names). Raises ExprError."""
    if not isinstance(expr, str) or not expr.strip():
        raise ExprError(f"formula must be a non-empty string, got {expr!r}")
    if len(expr) > MAX_LEN:
        raise ExprError(f"formula longer than {MAX_LEN} characters")
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        raise ExprError(f"syntax error in '{expr}': {e.msg}")
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_NODES:
        raise ExprError(f"formula too complex: '{expr}'")
    func_nodes = set()
    for n in nodes:
        if not isinstance(n, _ALLOWED):
            raise ExprError(f"forbidden construct '{type(n).__name__}' in '{expr}'")
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name) or n.func.id not in FUNCS or n.keywords:
                raise ExprError(f"only these functions are allowed: {sorted(FUNCS)} (in '{expr}')")
            func_nodes.add(id(n.func))
    names = frozenset(n.id for n in nodes if isinstance(n, ast.Name) and id(n) not in func_nodes)
    return tree, names


def expr_names(expr):
    return parse(expr)[1]


# -------------------------------------------------------------- evaluation
def _check(x):
    if isinstance(x, Fraction) and abs(x) > MAX_ABS:
        raise RejectDraw("number too large")
    return x


def _pow(a, b):
    if b.denominator != 1 or abs(b) > MAX_EXPONENT:
        raise ExprError(f"exponent must be an integer between -{MAX_EXPONENT} and {MAX_EXPONENT}")
    if a == 0 and b < 0:
        raise RejectDraw("zero to a negative power")
    return a ** int(b)


_BIN = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: Fraction(a // b),
    ast.Mod: lambda a, b: a % b,
    ast.Pow: _pow,
}


def _ordered(op, a, b):
    if not ((is_num(a) and is_num(b)) or (isinstance(a, str) and isinstance(b, str))):
        raise ExprError("cannot order-compare these values")
    return {ast.Lt: a < b, ast.LtE: a <= b, ast.Gt: a > b, ast.GtE: a >= b}[type(op)]


def _ev(node, names):
    t = type(node)
    if t is ast.Expression:
        return _ev(node.body, names)
    if t is ast.Constant:
        v = node.value
        if isinstance(v, bool) or isinstance(v, str):
            return v
        if isinstance(v, int):
            return Fraction(v)
        if isinstance(v, float):
            return Fraction(str(v))
        raise ExprError(f"unsupported constant {v!r}")
    if t is ast.Name:
        if node.id not in names:
            raise ExprError(f"unknown variable '{node.id}'")
        v = names[node.id]
        return Fraction(v) if is_num(v) else v
    if t is ast.UnaryOp:
        v = _ev(node.operand, names)
        if isinstance(node.op, ast.Not):
            return not v
        v = _num(v)
        return -v if isinstance(node.op, ast.USub) else v
    if t is ast.BinOp:
        a, b = _num(_ev(node.left, names)), _num(_ev(node.right, names))
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and b == 0:
            raise RejectDraw("division by zero")
        return _check(_BIN[type(node.op)](a, b))
    if t is ast.BoolOp:
        is_and = isinstance(node.op, ast.And)
        v = None
        for sub in node.values:
            v = _ev(sub, names)
            if is_and and not v:
                return v
            if not is_and and v:
                return v
        return v
    if t is ast.Compare:
        left = _ev(node.left, names)
        for op, comp in zip(node.ops, node.comparators):
            right = _ev(comp, names)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            else:
                ok = _ordered(op, left, right)
            if not ok:
                return False
            left = right
        return True
    if t is ast.IfExp:
        return _ev(node.body, names) if _ev(node.test, names) else _ev(node.orelse, names)
    if t is ast.Call:
        args = [_ev(a, names) for a in node.args]
        return _check(FUNCS[node.func.id](*args))
    raise ExprError(f"forbidden construct '{t.__name__}'")


def evaluate(expr, names):
    """Evaluate a validated formula against {name: value}. Returns int / Fraction / str / bool."""
    tree, _ = parse(expr)
    try:
        return norm(_ev(tree, names))
    except (ZeroDivisionError, OverflowError, ValueError) as e:
        raise RejectDraw(f"math error: {e}")
    except TypeError as e:
        raise ExprError(f"type error in '{expr}': {e}")


# --------------------------------------------------------------- rendering
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def placeholders(template):
    return set(PLACEHOLDER.findall(template))


def format_number(x, group=True, decimals=2):
    """Indonesian style: 1.570  /  3,14  /  -2. Trailing zeros are dropped."""
    x = Fraction(x)
    scale = 10 ** decimals
    scaled = round_half_up(abs(x) * scale)
    neg = x < 0 and scaled != 0
    ip, fp = divmod(scaled, scale)
    s = f"{ip:,}".replace(",", ".") if group else str(ip)
    if decimals and fp:
        s += "," + str(fp).zfill(decimals).rstrip("0")
    return ("-" if neg else "") + s


def format_fraction(value):
    value = Fraction(value)
    whole, remainder = divmod(abs(value.numerator), value.denominator)
    text = str(whole) if not remainder else (f"{whole} " if whole else "") + f"{remainder}/{value.denominator}"
    return ("-" if value < 0 else "") + text


def render(template, values, fmts=None):
    """Substitute {name} placeholders. Unknown names raise ExprError (nothing is silently left)."""
    fmts = fmts or {}

    def sub(m):
        name = m.group(1)
        if name not in values:
            raise ExprError(f"template uses undeclared placeholder '{{{name}}}'")
        v = values[name]
        if fmts.get(name, {}).get("fmt") == "mixed" and not is_num(v):
            raise ExprError(f"mixed format requires a number: {name}")
        if is_num(v):
            f = fmts.get(name, {})
            if f.get("fmt") == "mixed":
                return format_fraction(v)
            return format_number(v, group=f.get("fmt", "id") != "raw", decimals=f.get("decimals", 2))
        return str(v)

    return PLACEHOLDER.sub(sub, template)
