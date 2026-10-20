"""Independent rendered-text oracle for indicator 3 completion questions."""
import re
from fractions import Fraction as F

from drill_1_5_level45_math import clean, num, numbers, require, root, rnd, shown

N = r'-?\d+(?:\.\d{3})*(?:,\d+)?'


def roots(text):
    answer = []
    for value in map(int, re.findall(r'sqrt\((\d+)\)', text)):
        if value not in answer:
            answer.append(value)
    return answer


def close(actual, expected, tolerance=F(1, 100)):
    assert abs(actual - expected) <= tolerance, (actual, expected)


def explain(exp, values, phrases=()):
    for value in values:
        require(exp, shown(value))
    for phrase in phrases:
        require(exp, phrase)


def n3(stem, opts, exp):
    match = re.search(
        r'(?:Operasi|Hitungan) Riil:\s*\((%s)\*(%s)\)/\((%s)\)='
        r'\((%s)\)/\((%s)\).*?(%s)' % ((N,) * 6), stem, re.S)
    assert match
    a, b, divisor, product, divisor_echo, displayed = map(num, match.groups())
    assert a * b == product and divisor == divisor_echo
    real = product / divisor
    close(displayed, real)
    models = []
    for group in re.findall(
            r'\((%s)\*(%s)\)/\((%s)\)=\((%s)\)/\((%s)\)=(%s)'
            % ((N,) * 6), stem):
        x, y, d, p, d_echo, result = map(num, group)
        assert x * y == p and d == d_echo and p / d == result
        models.append((x, result))
    assert len(models) == 2
    distances = [abs(model[1] - real) for model in models]
    assert distances[0] != distances[1]
    assert numbers(opts[0])[0] == a
    assert models[1][0] in numbers(opts[1]) and models[1][1] in numbers(opts[1])
    assert displayed in numbers(opts[1]) and models[0][0] in numbers(opts[2])
    explain(exp, [displayed, models[0][1], models[1][1]], ['Galat mutlak'])
    assert numbers(exp) == [displayed, models[0][1], models[1][1]]
    return [distances[0] < distances[1], distances[1] < distances[0], False, False]


def n4(stem, opts, exp):
    count, price = map(num, re.search(
        r'pengadaan\s+(%s).*?Rp(%s)' % (N, N), stem, re.S).groups())
    real = count * price
    proposals = []
    for group in re.findall(r'Dihitung dengan\s*\(?(%s)\*(%s)=(%s)\)?' %
                            (N, N, N), stem):
        x, y, total = map(num, group)
        assert x * y == total
        proposals.append(total)
    assert len(proposals) == 2
    assert num(re.search(r'total riil \(Rp(%s)' % N, stem)[1]) == real
    safe = proposals[1] >= real and proposals[0] < real
    if numbers(opts[1]):
        assert numbers(opts[1])[-1] == proposals[1]
    explain(exp, [real, *proposals], ['batas atas'])
    assert numbers(exp) == [real, *proposals]
    return [not safe, safe, False, False]


def n5(stem, opts, exp):
    radicands = roots(stem)
    assert len(radicands) >= 3
    lo, hi = radicands[:2]
    rounded_lo, rounded_hi = rnd(root(lo)), rnd(root(hi))
    delta = rounded_hi - rounded_lo
    evaluations = {}
    for label, text in re.findall(r'Evaluasi (I+): "([^"]+)"', stem):
        vals = numbers(text)
        if label in ('I', 'III'):
            assert len(vals) >= 3
            evaluations[label] = tuple(vals[-3:]) == (rounded_hi, rounded_lo, delta)
            if label == 'III':
                approximations = [num(x) for x in re.findall(
                    r'(%s)\s*(?:→|->|arrow)' % N, text)]
                assert len(approximations) == 2
                close(approximations[0], root(hi), F(1, 1000))
                close(approximations[1], root(lo), F(1, 1000))
        else:
            compound = re.search(
                r'sqrt\((\d+)-(\d+)\)=sqrt\((\d+)\).*?(%s)' % N, text)
            assert compound
            a, b, difference = map(int, compound.groups()[:3])
            claim = num(compound.group(4))
            assert a == hi and b == lo and difference == hi - lo
            evaluations[label] = claim == rnd(root(difference)) == delta
    truth = [evaluations['I'], evaluations['II'], evaluations['III'],
             evaluations['II'] and evaluations['III']]
    if numbers(opts[2]):
        assert numbers(opts[2])[-1] == delta
    explain(exp, [rounded_lo, rounded_hi, delta],
            ['Radikan tidak boleh dikurangkan'])
    assert numbers(exp) == [rounded_lo, rounded_hi, delta, delta-1]
    return truth


def n7(stem, opts, exp):
    stimulus = roots(stem)
    assert len(stimulus) == 3
    truth, expected = [], []
    for index, option in enumerate(opts):
        match = re.search(r'sqrt\((\d+)\)', option)
        assert match
        radicand = int(match[1])
        assert radicand == stimulus[min(index, 2)]
        target = rnd(root(radicand), 1 if 'persepuluhan' in option else 0)
        expected.append(target)
        truth.append(numbers(option)[-1] == target)
    explain(exp, expected[:3], ['half-up'])
    assert numbers(exp) == expected[:3]
    return truth


def n8(stem, opts, exp):
    c1, p1, c2, p2 = map(num, re.search(
        r'Membeli\s+(%s).*?Rp(%s).*?dan\s+(%s).*?Rp(%s)' %
        (N, N, N, N), stem, re.S).groups())
    real = c1 * p1 + c2 * p2
    models = []
    for group in re.findall(
            r'\((%s)\*(%s)\)\+\((%s)\*(%s)\)=(%s)\+(%s)=(%s)'
            % ((N,) * 7), stem):
        a, b, d, e, ab, de, total = map(num, group)
        assert a * b == ab and d * e == de and ab + de == total
        models.append(total)
    assert len(models) == 2
    assert models[0] in numbers(opts[1])
    assert models[0] in numbers(opts[2]) and models[1] in numbers(opts[3])
    explain(exp, [real, *models], ['batas atas'])
    assert numbers(exp) == [real, *models]
    return [abs(models[1] - real) < abs(models[0] - real),
            models[0] >= real, real < models[0], real < models[1]]


def n10(stem, opts, exp):
    radicands = list(map(int, re.findall(r'sqrt\((\d+)\)', stem)[:2]))
    assert len(radicands) == 2
    first, second = radicands
    targets = [rnd(root(first), 1), rnd(root(second)),
               rnd(root(first)) + rnd(root(second))]
    truth = []
    for index, option in enumerate(opts):
        expected_roots = [first] if index == 0 else [second] if index == 1 else []
        assert roots(option) == expected_roots
        truth.append(numbers(option)[-1] == targets[min(index, 2)])
    explain(exp, targets, ['bukan'])
    assert numbers(exp) == [*targets,targets[2]-1,F(1),F(2)]
    return truth


def n2(stem, opts, exp):
    radicands = list(map(int, re.findall(r'sqrt\((\d+)\)', stem)[:2]))
    assert len(radicands) == 2
    x, y = radicands
    rounded = (rnd(root(x), 1), rnd(root(y), 1))
    evaluations = {}
    for label, text in re.findall(r'Evaluasi ([XY]): "([^"]+)"', stem):
        evaluations[label] = tuple(numbers(text)[-2:]) == rounded
    for option in opts:
        for base, power, value in re.findall(r'(%s)\^(\d+)=(%s)' % (N, N), option):
            assert num(base) ** int(power) == num(value)
    assert rounded[0] in numbers(opts[2]) and rounded[1] in numbers(opts[2])
    for radicand, value in zip((x, y), rounded):
        distance = abs(value ** 2 - radicand)
        assert distance <= min(abs((value - F(1, 10)) ** 2 - radicand),
                               abs((value + F(1, 10)) ** 2 - radicand))
    final = num(re.search(r'menjadi\s+(%s)' % N, opts[3])[1])
    explain(exp, [x, rounded[0], y, rounded[1]], ['batas tengah'])
    assert numbers(exp) == [x,rounded[0],y,rounded[1]]
    return [evaluations['X'], evaluations['X'], evaluations['Y'],
            rounded[0] == rounded[1] == final]


def check_math(qid, candidate):
    number = int(qid.split('-')[-1])
    stem = clean(candidate['stem'])
    opts = [clean(option['text']) for option in candidate['options']]
    exp = clean(candidate['explanation'])
    truth = {2: n2, 3: n3, 4: n4, 5: n5, 7: n7, 8: n8, 10: n10}[number](
        stem, opts, exp)
    actual = [option['correct'] for option in candidate['options']]
    assert actual == truth, (qid, actual, truth)
    if qid.startswith('pg-'):
        assert sum(truth) == 1, (qid, truth)
    return truth
