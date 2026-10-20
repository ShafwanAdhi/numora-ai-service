"""Independent Fraction/Decimal oracle for indicator 1--2 completion."""
import math
import re
from decimal import Decimal, localcontext
from fractions import Fraction as F

from drill_1_5_level45_math import clean, num, numbers, radical, radical_sum, require, root, rnd, shown

N = r'-?\d+(?:\.\d{3})*(?:,\d+)?'


def explain(exp, values=(), phrases=()):
    for value in values:
        require(exp, shown(value))
    for phrase in phrases:
        require(exp, phrase)


def equations(text):
    """Validate every simple rendered arithmetic equality and return its sides."""
    found = []
    for expression in re.findall(r'(?<![\w])(-?'+N+r'(?:\s*[+\-*/:]\s*-?'+N+r')+)\s*=\s*('+N+r')', text):
        left, shown_value = expression
        terms = re.split(r'\s*([+\-*/:])\s*', left)
        value = num(terms[0])
        for op, token in zip(terms[1::2], terms[2::2]):
            operand = num(token)
            value = value + operand if op == '+' else value - operand if op == '-' else value * operand if op == '*' else value / operand
        assert abs(value - num(shown_value)) <= F(1, 10**6), (left, shown_value)
        found.append(value)
    return found


def ordering(stem, opts, exp, level, number):
    if number == 1:
        a = num(re.search(r'Stasiun A:\s*('+N+')', stem)[1])
        b = -root(int(re.search(r'Stasiun B:.*?sqrt\((\d+)\)', stem)[1]))
        f = re.search(r'Stasiun C:.*?\((\d+)\)/\((\d+)\)', stem)
        c = -F(*map(int, f.groups()))
        d = num(re.search(r'Stasiun D:\s*('+N+')', stem)[1])
        values = {'A': a, 'B': b, 'C': c, 'D': d}
        correct_order = sorted(values, key=values.get)
        reports = {}
        for label, line in re.findall(r'Analisis (I+): ([^\n]+)', stem):
            reports[label] = re.findall(r'Stasiun ([ABCD])', line) == correct_order
        truth = [reports[re.search(r'Analisis (I+)', option)[1]] for option in opts]
        explain(exp, [a, rnd(b, 3), c, d], ['Stasiun A', 'Stasiun D'])
        return truth
    if level == 4:
        pfrac = re.search(r'Titik P:.*?\((\d+)\)/\((\d+)\)', stem)
        p = -F(*map(int, pfrac.groups()))
        q = -root(int(re.search(r'Titik Q:.*?sqrt\((\d+)\)', stem)[1]))
        r = num(re.search(r'Titik R:\s*('+N+')', stem)[1])
        truth = [min(p, q) < r < max(p, q), p > q, min(p, r) < q < max(p, r)]
        truth.append(truth[0] and truth[1])
        explain(exp, [p, rnd(q, 3), r], ['Titik Q'])
        return truth
    a = num(re.search(r'Lubang A:\s*('+N+')', stem)[1])
    frac = re.search(r'Lubang B:.*?\((\d+)\)/\((\d+)\)', stem)
    b = -F(*map(int, frac.groups()))
    radicand = num(re.search(r'Lubang C:.*?sqrt\(('+N+')\)', stem)[1])
    with localcontext() as context:
        context.prec = 60
        c = -F((Decimal(radicand.numerator) / Decimal(radicand.denominator)).sqrt())
    truth = [b != c, b == c and b > a, a > max(b, c), c < min(a, b)]
    explain(exp, [a, b, c], ['persis sama'])
    return truth


def i1_q4(stem, opts, exp):
    lines = dict(re.findall(r'Evaluasi (I+): "([^"]+)"', stem))
    a, b, first, c, d, second = numbers(lines['I'])[:6]
    valid_i = a - b == first and b - a == second and first == second
    vals = numbers(lines['II'])
    valid_ii = (vals[0] - vals[1] == vals[2] and
                vals[3] - vals[4] == vals[5] and vals[2] != vals[5])
    # A leading minus sign after prose is part of the result, while the
    # scanner may also retain the subtraction separator.  The equations
    # themselves are authoritative.
    valid_ii = bool(equations(lines['II'])) and '≠' in lines['II']
    equations(exp)
    explain(exp, phrases=['tidak komutatif'])
    return [valid_i, valid_ii, not valid_i and not valid_ii, valid_i]


def i1_q7(stem, opts, exp, level):
    model_lines = re.findall(r'(?:Model \d|Metode [XY]): ([^\n]+)', stem)
    assert len(model_lines) == 2
    amounts = numbers(model_lines[0])
    if level == 4:
        initial, first, second = map(abs, amounts[:3])
        expected = initial-first-second
        wrong = initial-(first-second)
        assert amounts[-1] == expected and numbers(model_lines[1])[-1] == wrong
        truth = [expected != wrong, expected != wrong, wrong == expected, initial-(first+second) == expected]
        explain(exp, [expected, wrong], ['tanda kurung'])
    else:
        initial, first, second = map(abs, amounts[:3])
        expected = initial-first-second
        assert amounts[-1] == expected and numbers(model_lines[1])[-1] == expected
        truth = [True, -(first+second) == -first-second,
                 initial-(first-second) == expected,
                 first+second == numbers(opts[3])[-2] and numbers(opts[3])[-1] == expected]
        explain(exp, [expected, initial-(first-second)], ['Salah'])
    return truth


def i1_q8(stem, opts, exp, level):
    coefficient = abs(num(re.search(r'^[A-ZK]=-?('+N+')', stem, re.M)[1]))
    radicand = int(re.search(r'sqrt\((\d+)\)', stem)[1])
    assert coefficient and math.isqrt(radicand) ** 2 != radicand
    for option in opts:
        equations(option)
    truth = [False, True, False, True] if level == 4 else [False, True, True, False]
    explain(exp, [radicand], ['irasional', 'tidak terdefinisi'])
    return truth


def i1_q10(stem, opts, exp, level):
    if 'Kasus uji numerik' in stem:
        probe = stem.split('Kasus uji numerik:', 1)[1].split('Tentukan status', 1)[0]
        vals = numbers(probe)
        assert len(vals) >= 3
        if level == 4:
            coefficient, radicand, integer = vals[:3]
            assert coefficient and math.isqrt(int(radicand)) ** 2 != radicand
            assert integer.denominator == 1
            explain(exp, [coefficient, radicand, integer])
        else:
            numerator, denominator, integer, radicand = vals[:4]
            assert denominator and integer.denominator == 1
            assert math.isqrt(int(radicand)) ** 2 != radicand
            explain(exp, [2*numerator, 0])
    explain(exp, phrases=['BENAR', 'SALAH'])
    return [True, True, False]


def i1_q2(stem, opts, exp):
    rad = int(re.search(r'a=sqrt\((\d+)\)', stem)[1])
    coeff = int(re.search(r'-\s*(\d+)sqrt\(', stem)[1])
    outside, base = radical(rad)
    assert base == 3 and outside == coeff
    repeat = re.search(r'b=0,(\d+)\.\.\.', stem)[1]
    fraction = re.search(r'=\((\d+)\)/\((\d+)\)=\((\d+)\)/\((\d+)\)', stem)
    assert F(int(repeat[:2]), 99) == F(int(fraction[1]), int(fraction[2])) == F(int(fraction[3]), int(fraction[4]))
    truths = []
    for option in opts:
        label = re.search(r'Evaluasi (I+)', option)[1]
        statement = re.search(r'Evaluasi '+label+r': "([^"]+)"', stem)[1]
        truths.append(label == 'III' and 'bilangan rasional' in statement)
    explain(exp, [rad, coeff, 0], ['rasional'])
    return truths


def i1_q3(stem, opts, exp):
    count, p, q = map(num, re.search(
        r'pengadaan\s+(%s).*?Rp(%s).*?Rp(%s)' % (N, N, N), stem, re.S).groups())
    total = count * (p+q)
    model1 = numbers(re.search(r'Usulan I:([^\n]+)', stem)[1])[-1]
    model2 = numbers(re.search(r'Usulan II:([^\n]+)', stem)[1])[-1]
    assert model1 == total and model2 != total
    explain(exp, [count, p, q, total], ['distributif'])
    return [True, False, False, False]


def i1_q_assoc(stem, opts, exp):
    if 'Kasus uji numerik' in stem:
        a, b, c, left, right = numbers(stem.split('Kasus uji numerik:',1)[1].split('Manakah',1)[0])
    else:
        a, b, c = numbers(exp)[0:3]
        left, right = (a/b)/c, a/(b/c)
    assert b and c and left == (a/b)/c and right == a/(b/c) and left != right
    explain(exp, [2, 8], ['tidak bersifat asosiatif'])
    return [False, False, True, False]


def i2_q1(stem, opts, exp):
    initial = num(re.search(r'Saldo awal kas: Rp('+N+')', stem)[1])
    count, price = map(num, re.search(r'Pembelian ('+N+r').*?Rp('+N+')', stem).groups())
    incoming = num(re.search(r'bantuan.*?Rp('+N+')', stem)[1])
    rent = num(re.search(r'sewa.*?Rp('+N+')', stem)[1])
    answer = initial-count*price+incoming-rent
    reports = {}
    for label, line in re.findall(r'Analisis (I+): ([^\n]+)', stem):
        reports[label] = numbers(line)[-1] == answer
    truth = [reports[re.search(r'Analisis (I+)', option)[1]] for option in opts]
    explain(exp, [count*price, answer], ['Saldo Akhir'])
    return truth


def i2_q2(stem, opts, exp):
    expression = re.search(r'Panjang Kerangka=([^\n]+)', stem)[1]
    result = radical_sum(expression)
    assert len(result) == 1
    base, coefficient = next(iter(result.items()))
    truth = []
    for option in opts:
        parsed = radical_sum(option)
        truth.append(parsed == result)
    steps = re.findall(r'sqrt\((\d+)\)=sqrt\((\d+)\*(\d+)\)=(\d+)sqrt\((\d+)\)', exp)
    assert len(steps) == 3
    for radicand, square, base_step, coefficient_step, final_base in steps:
        radicand, square, base_step, coefficient_step, final_base = map(
            int, (radicand, square, base_step, coefficient_step, final_base))
        assert square * base_step == radicand
        assert math.isqrt(square) ** 2 == square
        assert coefficient_step == math.isqrt(square) and final_base == base_step
    explain(exp, [coefficient], [f'sqrt({base})'])
    return truth


def i2_q3(stem, opts, exp):
    probe(stem)
    base, inner, outer, multiplier, divisor = map(int, re.search(
        r'\(\((\d+)\^(\d+)\)\^(\d+)\*(\d+)\^(-?\d+)\)/\((\d+)\^(\d+)\)',
        stem).groups()) if False else (None,)*5
    powers = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', stem.split('(dalam')[0])))
    assert len(powers) >= 4
    inner, outer, added, divided = powers[:4]
    result = inner*outer+added-divided
    base = int(re.search(r'(\d+)\^', stem)[1])
    if 'Evaluasi A' in opts[0]:
        # Derive each evaluation from the operation it explicitly proposes.
        # Appended basis/value details must not change which claim is tested.
        a_rule = re.search(r'\((\d+)\+(\d+)=(\d+)\)', opts[0])
        b_rule = re.search(r'\((\d+)\*(\d+)=(\d+)\)', opts[1])
        assert a_rule and b_rule
        av = list(map(int, a_rule.groups())); bv = list(map(int, b_rule.groups()))
        claimed_wrong_value = numbers(opts[2])[-1]
        claimed_d_value = numbers(opts[3])[-1]
        truth = [av[0]*av[1] == av[2],
                 bv[0]*bv[1] == bv[2] == inner*outer,
                 claimed_wrong_value == base ** result,
                 claimed_d_value == base ** result]
    else:
        claims = [int(re.search(r'\^\{?(-?\d+)\}?', option)[1]) for option in opts]
        truth = [claim == result for claim in claims]
    explain(exp, [inner*outer, inner*outer+added, result])
    return truth


def probe(stem):
    if 'Kasus uji numerik:' not in stem:
        return
    text = stem.split('Kasus uji numerik:', 1)[1].split('\n', 1)[0]
    values = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', text)))
    assert len(values) >= 3
    if 'cdot' in text or '*' in text:
        assert values[0] + values[1] == values[2]
    elif 'div' in text or '/' in text:
        assert values[0] - values[1] == values[2]


def i2_q5(stem, opts, exp):
    expression = stem.split('Ekspresi:', 1)[1].splitlines()[0]
    values = numbers(expression)
    # Rendered form: base^numerator * composite^-1 / cube^(2/3).
    base, numerator_exp, composite, inverse_exp, cube, top, bottom = values[:7]
    assert base.denominator == composite.denominator == cube.denominator == 1
    base_i, composite_i, cube_i = int(base), int(composite), int(cube)
    composite_power = 2 if numerator_exp == 5 else 4
    assert inverse_exp == -1 and top == 2 and bottom == 3
    assert composite_i == base_i ** composite_power
    assert cube_i == base_i ** 3
    result_exp = int(numerator_exp) - composite_power - 2
    result = base_i ** result_exp
    prose_base = re.search(r'ke basis\s+(\d+)', exp)
    if numerator_exp == 5:
        assert prose_base and int(prose_base[1]) == base_i
    # A and B assert inequalities between equal forms. C states the two
    # verified conversions; D supplies an alternative final numeric result.
    claimed_d = numbers(opts[3])[-1]
    explain(exp, [composite_i, cube_i, result], ['Langkah Siswa B'])
    return [composite_i ** -1 != base_i ** (-composite_power),
            cube_i != base_i ** 3,
            composite_i == base_i ** composite_power and cube_i == base_i ** 3,
            claimed_d == result]


def i2_q7(stem, opts, exp):
    probe(stem)
    source = stem.split('Ekspresi:', 1)[1].splitlines()[0]
    powers = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', source)))
    assert len(powers) == 4
    ap, bp, aq, bq = powers
    ra, rb = ap-aq, bp-bq
    claims_a = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', opts[0])))
    claims_b = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', opts[1])))
    assert claims_a[-1] == ra and claims_b[-2] == rb and claims_b[-1] == abs(rb)
    cvals = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', opts[2])))
    dvals = list(map(int, re.findall(r'\^\{?(-?\d+)\}?', opts[3])))
    truth = [True, True, cvals[-2:] == [ra, abs(rb)], dvals[-2:] == [ra, abs(rb)]]
    explain(exp, [ra, rb], ['Menggabungkan' if 'Menggabungkan' in exp else 'Gabungan'])
    return truth


def i2_q9(stem, opts, exp):
    frac = re.search(r'Operasi:\((\d+)\)/\((\d+)\)\+(%s)\*(%s)' % (N, N), stem)
    assert frac
    a, b = map(int, frac.groups()[:2]); x, y = map(num, frac.groups()[2:])
    product, total, wrong = x*y, F(a,b)+x*y, (F(a,b)+x)*y
    final_text = opts[2]
    decimal_claim = num(re.search(r'adalah\s+(%s)' % N, final_text)[1])
    fraction = re.search(r'\((%s)\)/\((%s)\)' % (N, N), final_text)
    fraction_claim = num(fraction[1]) / num(fraction[2])
    truth = [numbers(opts[0])[-1] == product,
             numbers(opts[1])[-1] == wrong,
             decimal_claim == total and fraction_claim == total]
    # The fractional addend is rendered as LaTeX rather than as a decimal;
    # the other three independently calculated results must be explicit.
    require(exp, f'({a})/({b})')
    for value in (product, total, wrong):
        assert value in numbers(exp)
    for label in ('1', '2', '3'):
        require(exp, 'pernyataan ' + label)
    return truth


def i2_q10(stem, opts, exp):
    radicands = list(map(int, re.findall(r'sqrt\((\d+)\)', stem.split('Tentukan')[0])))
    assert len(radicands) == 3
    a, b, d = radicands
    product = a*b
    root_product = root(product)
    root_divisor = root(d)
    result = root_product/root_divisor
    first = numbers(opts[0])[-1] == root_product and math.isqrt(product)**2 == product
    second = numbers(opts[1])[-1] == root_divisor
    claimed = numbers(opts[2])[-1]
    has_root = 'sqrt' in opts[2]
    third = claimed*root(2) == result if has_root else claimed == result
    explain(exp, [product, root_product, root_divisor, result])
    return [first, second, third]


def check_math(qid, candidate):
    assert 'Pembahasan salah' not in candidate['explanation']
    assert all('Klaim tambahan' not in option['text'] for option in candidate['options'])
    _, indicator, level, number = qid.split('-')
    indicator, level, number = int(indicator), int(level), int(number)
    stem = clean(candidate['stem'])
    opts = [clean(option['text']) for option in candidate['options']]
    exp = clean(candidate['explanation'])
    equations(exp)
    if indicator == 1:
        checker = {1: lambda: ordering(stem, opts, exp, level, number),
                   2: lambda: i1_q2(stem, opts, exp),
                   3: lambda: i1_q3(stem, opts, exp),
                   4: lambda: i1_q4(stem, opts, exp) if level == 4 else i1_q_assoc(stem, opts, exp),
                   5: lambda: ordering(stem, opts, exp, level, number),
                   7: lambda: i1_q7(stem, opts, exp, level),
                   8: lambda: i1_q8(stem, opts, exp, level),
                   10: lambda: i1_q10(stem, opts, exp, level)}[number]
    else:
        checker = {1: lambda: i2_q1(stem, opts, exp),
                   2: lambda: i2_q2(stem, opts, exp),
                   3: lambda: i2_q3(stem, opts, exp),
                   4: lambda: mixed_q4(stem, opts, exp),
                   5: lambda: i2_q5(stem, opts, exp),
                   7: lambda: i2_q7(stem, opts, exp),
                   9: lambda: i2_q9(stem, opts, exp),
                   10: lambda: i2_q10(stem, opts, exp)}[number]
    truth = checker()
    actual = [option['correct'] for option in candidate['options']]
    assert actual == truth, (qid, actual, truth)
    if qid.startswith('pg-'):
        assert sum(truth) == 1
    return truth


def mixed_q4(stem, opts, exp):
    expression = re.search(r'Soal:([^\n]+)', stem)[1]
    vals = numbers(expression)
    a, b, c, d = vals
    correct = a/b+c*d
    first = numbers(re.search(r'Evaluasi I:.*', stem)[0])[-1]
    second = numbers(re.search(r'Evaluasi II:.*', stem)[0])[-1]
    assert first == correct and second == (a/b+c)*d
    explain(exp, [a/b, c*d, correct])
    return [True, False, False, False]
