"""Independent math checks of rendered questions. No config expression/key oracle."""
import ast
import re
from collections import Counter
from fractions import Fraction as F
from math import ceil, floor


def nums(text):
    return [F(s.replace('.', '').replace(',', '.'))
            for s in re.findall(r'(?<!\^)\d+(?:\.\d{3})*(?:,\d+)?', text)]


def signed(text):
    text = text.replace('−', '-')
    return [F(s.replace('.', '').replace(',', '.'))
            for s in re.findall(r'(?<!\^)-?\d+(?:\.\d{3})*(?:,\d+)?', text)]


class Poly(dict):
    """Small exact coefficient oracle, including monomial rational cancellation."""
    def __add__(self, other):
        other = aspoly(other); out = Poly(self)
        for powers, coefficient in other.items():
            out[powers] = out.get(powers, F(0)) + coefficient
        return Poly({p: c for p, c in out.items() if c})

    __radd__ = __add__

    def __neg__(self):
        return Poly({p: -c for p, c in self.items()})

    def __sub__(self, other):
        return self + -aspoly(other)

    def __mul__(self, other):
        out = Poly()
        for p, c in self.items():
            for q, d in aspoly(other).items():
                powers = Counter(dict(p)); powers.update(dict(q))
                key = tuple(sorted((name, degree) for name, degree in powers.items() if degree))
                out = out + Poly({key: c*d})
        return out

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = aspoly(other)
        assert len(other) == 1, 'oracle supports monomial denominators only'
        (powers, coefficient), = other.items()
        return self * Poly({tuple((n, -d) for n, d in powers): 1/coefficient})


def aspoly(value):
    return value if isinstance(value, Poly) else Poly({(): F(value)}) if value else Poly()


def poly(text):
    text = text.strip().rstrip('.,').replace('−', '-').replace('²', '^2').replace('×', '*')
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'\d+(?:\.\d{3})+(?:,\d+)?', lambda m: m[0].replace('.', ''), text)
    text = re.sub(r'(?<=\d),(?=\d)', '.', text).replace('^', '**')
    text = re.sub(r'(?<=[0-9)])(?=[a-z(])|(?<=[a-z])(?=[a-z(])', '*', text)
    def walk(node):
        if isinstance(node, ast.Constant):
            return aspoly(F(str(node.value)))
        if isinstance(node, ast.Name):
            assert len(node.id) == 1
            return Poly({((node.id, 1),): F(1)})
        if isinstance(node, ast.UnaryOp):
            return -walk(node.operand) if isinstance(node.op, ast.USub) else walk(node.operand)
        if isinstance(node, ast.BinOp):
            a, b = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add): return a+b
            if isinstance(node.op, ast.Sub): return a-b
            if isinstance(node.op, ast.Mult): return a*b
            if isinstance(node.op, ast.Div): return a/b
            if isinstance(node.op, ast.Pow):
                degree = b.get((), 0); assert degree.denominator == 1 and 0 <= degree <= 4
                out = aspoly(1)
                for _ in range(int(degree)): out = out*a
                return out
        raise AssertionError('unsupported oracle expression: '+text)
    return walk(ast.parse(text, mode='eval').body)


def substitute(expression, **values):
    out = Poly()
    for powers, c in expression.items():
        rest = []
        for name, degree in powers:
            if name in values: c *= F(values[name])**degree
            else: rest.append((name, degree))
        out = out + Poly({tuple(rest): c})
    return out


def equation(text):
    left, right = text.split('=', 1)
    return poly(left)-poly(right)


def equations(text):
    return re.findall(r'([0-9a-z()+*/^.,−\-]+\s*=\s*[0-9a-z()+*/^.,−\-]+)', text)


def linear_solution(expression, variable='x'):
    assert not (set(expression)-{(), ((variable, 1),)})
    a, b = expression.get(((variable, 1),), F(0)), expression.get((), F(0))
    return -b/a if a else 'ALL' if not b else 'EMPTY'


def linear_one(expression):
    names = {n for powers in expression for n, _ in powers}
    return len(names) == 1 and all(sum(d for _, d in powers) <= 1 for powers in expression)


def claim_solution(text, variable='x'):
    return F(re.search(variable+r'=([−\-]?\d+(?:\.\d{3})*(?:,\d+)?)', text)[1]
             .replace('−', '-').replace('.', '').replace(',', '.'))


def inequalities(text):
    return [s.strip() for s in re.findall(
        r'(?<![a-zA-Z])([0-9(xyk−\-][0-9xykabpmncrt()+*/^.,−\- ]*[≤≥<>]\s*[0-9xykabpmncrt()+*/^.,−\-]+)', text)]


def inequality(text):
    left, op, right = re.split(r'([≤≥<>])', text)
    expression = poly(left)-poly(right)
    names = {name for powers in expression for name, _ in powers}
    if not names:
        value = expression.get((), 0)
        return ('ALL' if {'<': value < 0, '>': value > 0, '≤': value <= 0, '≥': value >= 0}[op] else 'EMPTY', None)
    assert len(names) == 1 and linear_one(expression)
    name = next(iter(names)); a = expression[((name, 1),)]
    threshold = -expression.get((), F(0))/a
    if a < 0: op = {'<': '>', '>': '<', '≤': '≥', '≥': '≤'}[op]
    return op, threshold


def contains(bound, value):
    op, endpoint = bound
    if op in ('ALL', 'EMPTY'): return op == 'ALL'
    return {'<': value < endpoint, '>': value > endpoint,
            '≤': value <= endpoint, '≥': value >= endpoint}[op]


def row_of(text):
    e = equation(text)
    assert not (set(e)-{(), (('x', 1),), (('y', 1),)})
    return e.get((('x', 1),), F(0)), e.get((('y', 1),), F(0)), -e.get((), F(0))


def system(first, second):
    a, b, e = first; c, d, f = second; det = a*d-b*c
    if det:
        return (e*d-b*f)/det, (a*f-e*c)/det
    if (not a and not b and e) or (not c and not d and f): return 'EMPTY'
    return 'ALL' if a*f == c*e and b*f == d*e else 'EMPTY'


def point_satisfies(row, point):
    a, b, c = row
    return a*point[0]+b*point[1] == c


def divide(numerator, denominator):
    """Exact univariate long division; returns quotient and remainder."""
    numerator, denominator = Poly(numerator), Poly(denominator)
    quotient = Poly()
    def degree(p): return max((dict(m).get('x', 0) for m in p), default=-1)
    d = degree(denominator)
    assert denominator and d >= 0
    lead = denominator.get((('x', d),) if d else (), 0)
    while numerator and degree(numerator) >= d:
        n = degree(numerator); key = (('x', n),) if n else ()
        term = Poly({(('x', n-d),) if n-d else (): numerator[key]/lead})
        quotient = quotient+term; numerator = numerator-term*denominator
    return quotient, numerator


def coefficient(expression, name, degree=1):
    out = Poly()
    for powers, c in expression.items():
        if dict(powers).get(name, 0) == degree:
            out = out+Poly({tuple((n,d) for n,d in powers if n != name): c})
    return out


def after(text, marker):
    return text.split(marker, 1)[1].strip().rstrip('.')


def geometry_value(test, length, width):
    # Check the shape has a positive domain; numeric substitutions must lie in it.
    large = 1+10*sum(abs(v) for p in (length,width) for v in p.values())
    test.assertGreater(substitute(length,x=large).get((),0),0)
    test.assertGreater(substitute(width,x=large).get((),0),0)


def check_math(test, orig, result):
    q = orig['id']; cand = result.cand
    s = nums(cand['stem']); opts = cand['options']; n = [nums(o['text']) for o in opts]
    flags = None
    if q == 'pg-6-1-1':
        amount, flour, sugar, target = s
        answer = target / amount * (flour - sugar)
        flags = [x[0] == answer for x in n]
    elif q == 'pg-6-1-5':
        fuel, duration, area, target = s
        test.assertGreater(fuel, 0); test.assertGreater(area, 0)
        flags = [x[0] == fuel*target/area for x in n]
    elif q == 'pg-7-1-2':
        extra, deduction = s
        flags = [x[0] == (extra+deduction)/2 for x in n]
    elif q in ('pg-7-2-4', 'pg-7-3-5'):
        variable = 'a' if q == 'pg-7-2-4' else 'k'
        model = equation(equations(cand['stem'])[0])
        test.assertNotIn((('x', 1),), model)
        critical = linear_solution(model, variable)
        flags = []
        for option in opts:
            match = re.search(variable+r'≠(-?\d+)', option['text'])
            flags.append(bool(match) and F(match[1]) == critical)
        test.assertEqual(linear_solution(substitute(model, **{variable: critical})), 'ALL')
        test.assertEqual(linear_solution(substitute(model, **{variable: critical+1})), 'EMPTY')
    elif q == 'mcma-8-2-8':
        es = inequalities(cand['stem']); actual = inequality(es[0])
        def difference(text):
            left, op, right = re.split(r'([<>])', text.strip(' $'))
            test.assertEqual(op, '<')
            return poly(left)-poly(right)
        step3 = cand['stem'].split('Langkah 3: ', 1)[1].split('\n', 1)[0]
        group, reduced = step3.split(r'\implies')
        first_ok = difference(es[1]) == 6*difference(es[0]) and difference(es[2]) == difference(es[1])
        third_ok = difference(group) == difference(es[2]) and difference(reduced) == difference(group)
        divisor = difference(reduced).get((('x', 1),), 0)
        bad = inequality(es[-1])
        flags = [first_ok, third_ok,
                 divisor < 0 and signed(opts[2]['text'])[-1] == divisor and bad[0] != actual[0] and bad[1] == actual[1],
                 inequality(inequalities(opts[3]['text'])[0]) == actual]
    elif q == 'pg-9-1-3':
        first, symbolic = equations(cand['stem'])[:2]
        a, b, total = row_of(first)
        model = equation(symbolic)
        ratio = model[(('x', 1),)]/a
        test.assertEqual(model[(('y', 1),)], b*ratio)
        test.assertEqual(model[(('k', 1),)], -1)
        critical = ratio*total
        flags = [bool(m := re.search(r'k≠(-?\d+)', o['text'])) and F(m[1]) == critical for o in opts]
    elif q in ('pg-9-1-5', 'pg-9-2-5', 'pg-9-3-4'):
        eqs = equations(cand['stem'])[:2]
        x, y = system(*(row_of(e) for e in eqs))
        test.assertGreater(x, 0); test.assertGreater(y, 0)
        test.assertIn('paling langsung', cand['stem'])
        if q == 'pg-9-3-4':
            flags = []
            for option in opts:
                point = re.search(r'titik potong \((\d+),(\d+)\)', option['text'])
                direct = 'mengganti nilai y pada Persamaan 2' in option['text']
                expression = re.search(r'dengan \(([^()]+)\)', option['text'])
                flags.append(direct and expression is not None and poly(expression[1]) == poly(eqs[0].split('=')[1])
                             and tuple(map(F, point.groups())) == (x, y))
        else:
            variable, answer = ('y', y) if q == 'pg-9-1-5' else ('x', x)
            flags = [o['text'].startswith('Substitusi,') and claim_solution(o['text'], variable) == answer for o in opts]
    elif q == 'pg-9-3-2':
        a, b, e = row_of(equations(cand['stem'])[0])
        c, d, f = row_of(equations(cand['stem'])[1])
        test.assertNotEqual(a*d-b*c, 0)
        test.assertTrue(all(v > 0 for v in system((a,b,e), (c,d,f))))
        flags = []
        for option in opts:
            text = option['text']
            numerator, denominator = map(F, re.search(r'\\frac\{(-?\d+)\}\{(-?\d+)\}', text).groups())
            blocks = re.findall(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}', text)
            test.assertEqual(len(blocks), 3)
            matrix = [F(v.strip())*numerator/denominator for v in re.split(r'&|\\\\', blocks[1])]
            rhs = [F(v.strip().replace('.', '')) for v in blocks[2].split(r'\\')]
            p, r, t, u = matrix
            flags.append([a*p+b*t, a*r+b*u, c*p+d*t, c*r+d*u] == [1,0,0,1] and rhs == [e,f])
    elif q == 'pg-6-1-2':
        speed, oldtime, newtime = s
        flags = [x[0] == speed * oldtime / newtime for x in n]
    elif q in ('pg-6-1-3', 'pg-6-3-5'):
        deadline, workers, elapsed, pause = s[:4]
        test.assertGreater(deadline - elapsed - pause, 0)
        answer = workers * (deadline - elapsed) / (deadline - elapsed - pause) - workers
        test.assertEqual(answer.denominator, 1)
        flags = [x[0] == answer for x in n]
    elif q == 'pg-6-1-4':
        _, scale, width, length = s
        flags = [x[0] == 2 * (width + length) * scale / 100 for x in n]
    elif q == 'pg-6-2-1':
        count, orange, sugar, target, _ = s
        answer = target / count * (orange - sugar / 1000)
        flags = [x[0] == answer for x in n]
    elif q == 'pg-6-2-2':
        speed, duration, earlier = s
        test.assertGreater(duration - earlier, 0)
        flags = [x[0] == speed * duration / (duration - earlier) for x in n]
    elif q == 'pg-6-2-3':
        count, students, deadline, elapsed, departed = s
        test.assertGreater(students - departed, 0)
        answer = elapsed + students * (deadline - elapsed) / (students - departed)
        flags = [x[0] + x[1] / 60 == answer for x in n]
    elif q == 'pg-6-2-4':
        units, minutes, pages, target, deadline = s
        rate = pages / (units * minutes)
        flags = [x[0] == ceil(target / (deadline * rate)) for x in n]
    elif q == 'pg-6-2-5':
        students, mass, days, target, deadline = s
        rate = mass / (students * days)
        flags = [x[0] == target / (deadline * rate) for x in n]
    elif q == 'pg-6-3-1':
        units, pages, minutes, newunits, factor, newtime = s
        rate = pages / (units * minutes)
        flags = [x[0] == newunits * rate * factor * newtime - pages for x in n]
    elif q == 'pg-6-3-2':
        distance, speeda, litresa, kma, speedb, litresb, kmb = s
        flags = [x[0] == distance * (litresb / kmb - litresa / kma) for x in n]
    elif q == 'pg-6-3-3':
        students, panels, days, target, deadline = s
        flags = [x[0] == target * students * days / (panels * deadline) - students for x in n]
    elif q == 'pg-6-3-4':
        distance, speed, first, pause = s
        remaining = distance / speed - first / speed - pause / 60
        test.assertGreater(remaining, 0)
        flags = [x[0] == (distance - first) / remaining for x in n]
    elif q == 'mcma-6-1-7':
        pa, ta, pb, tb = s; ra, rb = pa / ta, pb / tb
        flags = [n[0][0] == ra, n[1][1] == rb * n[1][0],
                 n[2][0] / ra < n[2][0] / rb, rb > ra]
    elif q == 'mcma-6-1-8':
        students, share, absent = s; total = students * share
        test.assertGreater(students - absent, 0)
        test.assertEqual(students.denominator, 1)
        actual = total / (students - absent)
        flags = [n[0][0] == total, total > 0, n[2][0] == actual, n[3][0] == actual - share]
    elif q == 'kategori-6-1-9':
        x1, x2, x3, y1, y2, y3, a, b, c, d, e, f = s
        direct = y1/x1 == y2/x2 == y3/x3
        inverse = a*d == b*e == c*f
        flags = [direct and n[0][0] == y1/x1, inverse and n[1][0] == a*d,
                 n[2][1] == a*d/n[2][0]]
    elif q == 'kategori-6-1-10':
        speed, time, fuel, distance_per = s; distance = speed*time
        flags = [n[0][0] == distance, n[1][1] == distance/n[1][0],
                 n[2][0] == 2*distance*fuel/distance_per]
    elif q == 'mcma-6-2-7':
        la, da, lb, db, distance = s; ea, eb = da/la, db/lb
        flags = [n[0][0] == distance/ea, eb > ea,
                 n[2][1] == distance/eb-distance/ea, n[3] == [ea, eb]]
    elif q == 'mcma-6-2-8':
        students, days, elapsed, joined = s
        remaining = days-elapsed; actual = students*remaining/(students+joined)
        flags = [n[0] == [joined, students, remaining], n[1] == [joined, actual],
                 n[2] == [joined, remaining-actual], n[3][1] == days]
    elif q == 'kategori-6-2-9':
        trees, time, students, spacing = s; rate = trees/(time*students)
        flags = [n[0][1] == rate*n[0][0]*n[0][2],
                 n[1][2] == n[1][0]/(rate*n[1][1]), False]
    elif q == 'kategori-6-2-10':
        units, repeated, days, cost, added, newdays = s; rate = cost/(units*days)
        flags = [n[0][-1] == rate, n[1][-1] == (units+added)*newdays*rate, False]
    elif q == 'mcma-6-3-8':
        one, scale, length, width = s
        newscale = n[3][1]
        flags = [n[0] == [length, width], n[1][0] == 2*(length+width)*scale/100,
                 n[2][1] == scale**2, n[3][2] == (scale/newscale)**2]
    elif q == 'kategori-6-3-10':
        workers, units, days = s; rate = units/(workers*days)
        flags = [n[0][2] == n[0][0]/(n[0][1]*rate),
                 n[1][1]/n[1][2] == rate, n[2][2] == n[2][1]/(n[2][0]*rate)]
    elif q in ('pg-7-1-1', 'pg-7-2-1'):
        if q == 'pg-7-1-1':
            count, _, extra, total = s[:4]
            model = count*poly('x')+extra-total
        else:
            count, discount, total = s[:3]
            model = count*poly('x')-discount-total
        answer = linear_solution(model)
        flags = [equation(equations(o['text'])[0]) == model and nums(o['text'])[-1] == answer for o in opts]
    elif q in ('pg-7-1-4', 'pg-7-2-2'):
        solution = linear_solution(equation(equations(cand['stem'])[0]))
        requested = re.search(r'Nilai dari (.+?) adalah', cand['stem'])[1]
        answer = substitute(poly(requested), x=solution).get((), F(0))
        flags = [signed(o['text'])[0] == answer for o in opts]
    elif q == 'pg-7-1-5':
        flags = [x[0] == s[0]/3+1 for x in n]
    elif q == 'mcma-7-1-6':
        flags = [linear_one(equation(equations(o['text'])[0])) for o in opts]
    elif q in ('mcma-7-1-7', 'mcma-7-2-7'):
        eq = [equation(e) for e in equations(cand['stem'])]
        solutions = [linear_solution(e) for e in eq]
        flags = [solutions[0] == 'ALL', solutions[1] == 'EMPTY',
                 solutions[2] == claim_solution(opts[2]['text']), solutions[1] == solutions[2]]
    elif q == 'mcma-7-1-8':
        ratio, total = s; young = (total-8)/(ratio+1); old = ratio*young
        model = poly('(x+4)+(3x+4)')-total
        flags = [equation(equations(opts[0]['text'])[0]) == model,
                 n[1][0] == young, n[2][0] == old, n[3][0] == old-young]
    elif q == 'kategori-7-1-9':
        count, leftover, total = s
        flags = [equation(equations(opts[0]['text'])[0]) == count*poly('x')+leftover-total,
                 n[1] == [total, leftover, count], n[2][-1] == (total-leftover)/count]
    elif q in ('pg-7-1-3', 'pg-7-2-3', 'pg-7-3-4'):
        expressions = re.findall(r'\(([^()]+)\)', cand['stem'])
        length, width = map(poly, expressions[:2])
        model = 2*(length+width)-(4*poly(expressions[2]) if q == 'pg-7-3-4' else s[-1])
        solution = linear_solution(model)
        length = substitute(length, x=solution).get((), 0)
        width = substitute(width, x=solution).get((), 0)
        test.assertGreater(length, 0); test.assertGreater(width, 0)
        flags = [x[0] == length*width for x in n]
    elif q == 'pg-7-2-5':
        difference, pastsum, future = s
        answer = (pastsum+6+difference)/2+future
        flags = [x[0] == answer for x in n]
    elif q == 'mcma-7-2-6':
        eq = [equation(equations(o['text'])[0]) for o in opts]
        ce = [equation(e) for e in equations(opts[2]['text'])]
        flags = [linear_one(eq[0]) and linear_solution(eq[0]) == claim_solution(opts[0]['text']),
                 linear_one(eq[1]), ce[1] == 3*ce[0], linear_one(eq[3])]
    elif q == 'mcma-7-2-8':
        total = s[0]; first = (total-6)/3
        test.assertEqual(first % 2, 1)
        flags = [equation(equations(opts[0]['text'])[0]) == 3*poly('n')+6-total,
                 n[1][0] == first, n[2][0] == 4, n[3][0] == 2*first+4]
    elif q == 'kategori-7-2-9':
        count, _, extra, total = s
        flags = [equation(equations(opts[0]['text'])[0]) == count*poly('x')+extra-total,
                 n[1][-3:] == [total, extra, count], n[2][-1] == (total-extra)/count]
    elif q == 'pg-7-3-2':
        left = poly(equations(cand['stem'])[0].split('=')[0])
        answer = sum(left.values())
        flags = [signed(o['text'])[0] == answer for o in opts]
    elif q == 'pg-7-3-3':
        eq = equations(cand['stem']); correct = linear_solution(equation(eq[0]))
        test.assertEqual(linear_solution(equation(eq[1])), correct)
        test.assertEqual(linear_solution(equation(eq[2])), correct)
        test.assertNotEqual(linear_solution(equation(eq[3])), correct)
        flags = [x == [3, correct] for x in n]
    elif q == 'mcma-7-3-6':
        eq = [equation(e) for e in equations(cand['stem'])]
        flags = [linear_one(eq[0]) and linear_solution(eq[0]) == claim_solution(opts[0]['text']),
                 not linear_one(eq[1]), linear_one(eq[2]), linear_solution(eq[3]) == 'ALL']
    elif q == 'mcma-7-3-7':
        extra, total = s; andi = (total/3-extra)/2; budi = andi+extra; cici = 2*(andi+budi)
        flags = [equation(equations(opts[0]['text'])[0]) == 6*poly('x')+3*extra-total,
                 n[1][0] == andi, n[2][0] == budi, n[3][0] == cici]
    elif q == 'mcma-7-3-8':
        eq = equations(cand['stem'])
        pairs = [[poly(s) for s in e.split('=')] for e in eq]
        flags = [[poly(s) for s in equations(opts[0]['text'])[0].split('=')] == pairs[0],
                 linear_solution(pairs[0][0]-pairs[0][1]) == 'ALL',
                 [poly(s) for s in equations(opts[2]['text'])[0].split('=')] == pairs[1],
                 linear_solution(pairs[1][0]-pairs[1][1]) == 'EMPTY']
    elif q == 'kategori-7-3-9':
        fiction, nonfiction, extra, total = s
        model = (fiction+nonfiction)*poly('x')+nonfiction*extra-total
        each = linear_solution(model); test.assertEqual(each.denominator, 1)
        flags = [equation(equations(opts[0]['text'])[0]) == model,
                 n[1][-1] == each, n[2][-1] == fiction*each*n[2][-2]]
    elif q == 'kategori-7-3-10':
        model = equation(equations(cand['stem'])[0]); a, b, c = [signed(o['text']) for o in opts]
        flags = [linear_solution(substitute(model, m=a[0])) == 'ALL',
                 linear_solution(substitute(model, m=b[0])) == b[1],
                 linear_solution(substitute(model, m=c[0])) == c[1]]
    elif q in ('pg-8-1-1', 'pg-8-2-1'):
        budget, fixed, price = s if q == 'pg-8-1-1' else [s[0], s[2], s[3]]
        answer = floor((budget-fixed)/price)
        flags = [x[0] == answer for x in n]
    elif q in ('pg-8-1-2', 'pg-8-2-2'):
        answer = inequality(inequalities(cand['stem'])[0])
        flags = [inequality(inequalities(o['text'])[0]) == answer for o in opts]
    elif q == 'pg-8-1-3':
        length, width = map(poly, [e for e in re.findall(r'\(([^()]+)\)', cand['stem']) if 'x' in e][:2])
        boundary = linear_solution(2*(length+width)-s[-1])
        test.assertGreater(substitute(width, x=boundary).get((), 0), 0)
        answer = substitute(length, x=boundary).get((), 0)
        flags = [x[0] == answer for x in n]
    elif q in ('pg-8-1-4', 'pg-8-2-4'):
        op, endpoint = inequality(inequalities(cand['stem'])[0])
        flags = [('kiri' in o['text']) == (op in ('<', '≤'))
                 and ('kosong' in o['text']) == (op in ('<', '>'))
                 and signed(o['text'])[0] == endpoint for o in opts]
    elif q == 'pg-8-1-5':
        capacity, driver, box = s
        model = box*poly('n')+driver-capacity
        maximum = floor((capacity-driver)/box)
        flags = []
        for o in opts:
            matches = inequalities(o['text'])
            flags.append(bool(matches) and inequality(matches[0]) == ('≤', (capacity-driver)/box)
                         and nums(o['text'])[-1] == maximum)
    elif q == 'mcma-8-1-6':
        target = inequality(inequalities(cand['stem'])[0])
        flags = []
        for o in opts:
            e = inequalities(o['text'])[0]; left, op, right = re.split(r'([≤≥<>])', e)
            expression = poly(left)-poly(right)
            flags.append(linear_one(expression) and inequality(e) == target)
    elif q in ('mcma-8-1-7', 'mcma-8-2-7'):
        if q == 'mcma-8-1-7': count, *rest = s; scores = rest[:3]; tests, target = rest[3:5]
        else: count = s[0]; scores = s[1:5]; tests, target = s[5:7]
        total = tests*target; minimum = total-sum(scores)
        model = (aspoly(sum(scores))+poly('x'))/tests-target
        e = inequalities(opts[0]['text'])[0]; left, op, right = re.split(r'([≤≥<>])', e)
        flags = [poly(left)-poly(right) == model and op == '≥', n[1][-1] == total,
                 n[2][-1] == minimum, (sum(scores)+n[3][0])/tests >= target]
    elif q == 'mcma-8-1-8':
        es = inequalities(cand['stem']); answer = inequality(es[0])
        first_left, _, _ = re.split(r'([≤≥<>])', es[0])
        bad_left, _, _ = re.split(r'([≤≥<>])', es[1])
        flags = [poly(first_left) != poly(bad_left), inequality(es[2]) == inequality(es[3]),
                 inequality(es[3])[0] != inequality(es[4])[0],
                 inequality(inequalities(opts[3]['text'])[0]) == answer]
    elif q == 'kategori-8-1-9':
        budget, _, fixed, price = s
        flags = [inequality(inequalities(opts[0]['text'])[0]) == ('≤', (budget-fixed)/price),
                 n[1][0] == floor((budget-fixed)/price), n[2][-1] == budget-fixed-price*n[2][0]]
    elif q == 'kategori-8-1-10':
        answer = inequality(inequalities(cand['stem'])[0])
        flags = [inequality(inequalities(opts[0]['text'])[0]) == answer,
                 inequality(inequalities(opts[1]['text'])[0]) == answer,
                 answer == ('≥', n[2][0]) and 'terisi penuh' in opts[2]['text'] and 'kanan' in opts[2]['text']]
    elif q == 'pg-8-2-3':
        basea, ratea, baseb, rateb = s; bound = ('>', (basea-baseb)/(rateb-ratea))
        flags = [inequality(e[0]) == bound if (e := inequalities(o['text'])) else False for o in opts]
    elif q == 'pg-8-2-5':
        length, width = map(poly, re.findall(r'\(([^()]+)\)', cand['stem'])[:2])
        upper = linear_solution(2*(length+width)-s[-2]); lower = linear_solution(width-s[-1])
        flags = [False, False, n[2] == [lower, upper], n[3] == [lower, upper]]
    elif q == 'mcma-8-2-6':
        flags = []
        for o in opts:
            es = inequalities(o['text']); left, _, right = re.split(r'([≤≥<>])', es[0])
            expression = poly(left)-poly(right)
            flags.append(linear_one(expression) and len(es) == 2 and inequality(es[0]) == inequality(es[1]))
    elif q == 'kategori-8-2-9':
        capacity, driver, box = s
        flags = [inequality(inequalities(opts[0]['text'])[0]) == ('≤', (capacity-driver)/box),
                 n[1][0] == floor((capacity-driver)/box), n[2][-1] == capacity-driver-box*n[2][0]]
    elif q == 'kategori-8-2-10':
        a, b = [inequality(e) for e in inequalities(cand['stem'])]
        integers = range(ceil(a[1]), ceil(b[1]))
        flags = [inequality(inequalities(opts[0]['text'])[0]) == a,
                 inequality(inequalities(opts[1]['text'])[0]) == b, not bool(integers)]
    elif q == 'pg-8-3-1':
        bx, rx, by, ry, budget = s; answer = floor((budget-by)/ry)-floor((budget-bx)/rx)
        flags = [x[0] == answer for x in n]
    elif q == 'pg-8-3-2':
        es = inequalities(cand['stem']); actual = inequality(es[0])
        first_ok = inequality(es[1]) == actual
        second_ok = inequality(es[2]) == actual
        third_bad = inequality(es[-1]) != actual
        flags = [not third_bad and contains(actual, 0), not first_ok,
                 third_bad and not contains(actual, 0), not second_ok]
    elif q == 'pg-8-3-3':
        a, b = [inequality(e) for e in inequalities(cand['stem'])]
        flags = [x == [a[1], b[1]] and 'kiri angka' in o['text'] and
                 re.findall(r'lingkaran (penuh|kosong)', o['text']) == ['penuh', 'kosong']
                 for x, o in zip(n, opts)]
    elif q == 'pg-8-3-4':
        e, target = inequalities(cand['stem'])
        model = poly(re.split(r'[≤≥<>]', e)[0])-poly(re.split(r'[≤≥<>]', e)[1])
        desired = inequality(target)
        flags = []
        for o in opts:
            k = claim_solution(o['text'], 'k'); reduced = substitute(model, k=k)
            a = reduced.get((('x', 1),), 0)
            flags.append(a < 0 and -reduced.get((), 0)/a == desired[1])
    elif q == 'pg-8-3-5':
        tests, target = s[:2]; first, second, maximum = s[5], s[7], s[8]
        lower = max(tests*target-first-second, second)
        flags = [x == [lower, maximum] for x in n]
    elif q == 'mcma-8-3-6':
        es = inequalities(cand['stem']); eq = equations(cand['stem'])[0]
        flags = [inequality(es[0])[0] == 'ALL', inequality(es[1]) == inequality(inequalities(opts[1]['text'])[0]),
                 linear_solution(equation(eq)) == 'ALL', inequality(es[2]) == inequality(inequalities(opts[3]['text'])[0])]
    elif q == 'mcma-8-3-7':
        es = inequalities(cand['stem']); answer = inequality(es[0])
        flags = [answer[0] == 'ALL' and inequality(es[1])[0] == 'ALL',
                 inequality(es[2])[0] == 'ALL', inequality(inequalities(opts[2]['text'])[0])[0] == 'ALL', answer[0] == 'ALL']
    elif q == 'mcma-8-3-8':
        capacity, teachers, teacher_weight, student_weight, boxes, box_weight = s
        fixed = teacher_weight+boxes*box_weight
        flags = [inequality(inequalities(opts[0]['text'])[0]) == ('≤', (capacity-fixed)/student_weight),
                 n[1][0] == floor((capacity-fixed)/student_weight),
                 n[2][-1] == capacity-fixed-n[2][0]*student_weight, fixed == capacity]
    elif q == 'kategori-8-3-9':
        es = inequalities(cand['stem']); actual = inequality(es[0])
        flags = [inequality(es[2]) != actual,
                 inequality(inequalities(opts[1]['text'])[0]) == actual,
                 contains(actual, signed(opts[2]['text'])[0])]
    elif q == 'kategori-8-3-10':
        fixed, price, budget, minimum = s; maximum = floor((budget-fixed)/price)
        flags = [n[0][0] == maximum, n[1] == [minimum, maximum],
                 n[2][0] >= minimum and n[2][0] > maximum]
    elif q in ('pg-9-1-1', 'pg-9-2-1', 'pg-9-3-1'):
        a, b, e, c, d, f = s[:6]; x, y = system((a,b,e), (c,d,f))
        test.assertGreater(x, 0); test.assertGreater(y, 0)
        required = s[6]*x+s[7]*y
        if q == 'pg-9-2-1': required = s[8]-required
        if q == 'pg-9-3-1':
            difference = required-s[8]*e
            flags = [('lebih murah' in o['text']) == (difference < 0) and n[i][0] == abs(difference)
                     for i,o in enumerate(opts)]
        else: flags = [v[0] == required for v in n]
    elif q in ('pg-9-1-2', 'pg-9-2-2'):
        a, b, e, c, d, f = s
        flags = [v == [a,b,c,d,e,f] for v in n]
    elif q in ('pg-9-1-4', 'pg-9-2-3'):
        perimeter, difference = s
        if q == 'pg-9-1-4': length, width = (perimeter/2+difference)/2, (perimeter/2-difference)/2
        else: width = (perimeter/2-difference)/3; length = 2*width+difference
        test.assertGreater(length, 0); test.assertGreater(width, 0)
        flags = [v[0] == length*width for v in n]
    elif q in ('mcma-9-1-6', 'mcma-9-2-6'):
        if q == 'mcma-9-1-6': first, second = tuple(s[1:4]), tuple(s[5:8])
        else: first, second = tuple(s[:3]), tuple(s[3:6])
        x, y = system(first, second)
        flags = [n[0][-1] == x, n[1][-1] == y, n[2][-1] == y-x,
                 n[3][-1] == n[3][0]*x+n[3][1]*y]
    elif q in ('mcma-9-1-7', 'mcma-9-2-7', 'mcma-9-3-6'):
        rows = [row_of(e) for e in equations(cand['stem'])]
        a,b,c = rows[0]
        if q == 'mcma-9-1-7': intercept = [F(0), c/b]; point = signed(opts[2]['text'])[-2:]
        elif q == 'mcma-9-2-7': intercept = [c/a, F(0)]; point = signed(opts[2]['text'])[-2:]
        else: intercept = [c/a,F(0),F(0),c/b]; point = signed(opts[2]['text'])
        flags = [system(rows[0],rows[1]) == 'ALL', system(rows[0],rows[2]) == 'EMPTY', point == intercept,
                 (rows[1][0]*rows[2][0]+rows[1][1]*rows[2][1] == 0) if q == 'mcma-9-3-6'
                 else isinstance(system(rows[1],rows[2]), tuple)]
    elif q == 'mcma-9-1-8':
        total, diff = s; x,y = system((1,1,total),(1,-1,diff))
        model = [poly('x+y')-total, poly('x-y')-diff]
        flags = [[equation(e) for e in equations(opts[0]['text'])] == model,
                 n[1][0] == x, n[2][0] == y, n[3][0]/n[3][1] == x/y]
    elif q in ('kategori-9-1-9', 'kategori-9-2-9'):
        x,y = system(tuple(s[:3]),tuple(s[3:6]))
        flags = [n[0][-1] == x, n[1][-1] == y, n[2][-1] == n[2][0]*x+n[2][1]*y]
    elif q == 'pg-9-2-4':
        eqs = equations(cand['stem']); first = row_of(eqs[0]); second = equation(eqs[1])
        flags = []
        for o in opts:
            k = claim_solution(o['text'],'k'); p = substitute(second,k=k)
            row = (p.get((('x',1),),0),p.get((('y',1),),0),-p.get((),0))
            flags.append(system(first,row) == 'EMPTY')
    elif q == 'mcma-9-2-8':
        count, capital, _, pricea, _, priceb = s
        a,b = system((F(1),F(1),count),(pricea,priceb,capital))
        test.assertEqual(a.denominator,1); test.assertEqual(b.denominator,1)
        income = n[2][0]*a+n[2][1]*b
        flags = [n[0][0] == a, n[1][0] == b, n[2][-1] == income, n[3][0] == income-capital]
    elif q == 'kategori-9-2-10':
        diff,total = s[:2]; first,second = [row_of(e) for e in equations(cand['stem'])[:2]]
        x,y = system(first,second)
        flags = [first == (1,-1,diff) and second == (1,1,total), n[1][0] == x,
                 s[-2] != y and s[-1] != x and s[-2] == x and s[-1] == y]
    elif q == 'pg-9-3-3':
        eq1,eq2 = [equation(e) for e in equations(cand['stem'])]
        ratio = eq2[(('x',1),)]/eq1[(('x',1),)]
        a = -eq2[(('y',1),)]/ratio; b = -eq1.get((),0)*ratio
        flags = [signed(o['text'])[0] == a+b for o in opts]
    elif q == 'pg-9-3-5':
        perfirst,stray,persecond,empty = s
        tents = (stray+persecond*empty)/(persecond-perfirst); students = perfirst*tents+stray
        test.assertEqual(tents.denominator,1); test.assertEqual(students.denominator,1)
        test.assertGreater(tents-empty,0)
        flags = [v == [students,tents] for v in n]
    elif q == 'mcma-9-3-7':
        x,y = system(tuple(s[:3]),tuple(s[3:6]))
        flags = [n[0][1] == x and n[0][3] == y, n[1][-1] == x-y,
                 n[2][-1] == n[2][0]*x+n[2][1]*y, n[3][0]*x > n[3][1]*y]
    elif q == 'mcma-9-3-8':
        first,second = [row_of(e) for e in equations(cand['stem'])[:2]]; x,y = system(first,second)
        wrong = n[3][:2]
        flags = [first[1]+second[1] == 0 and first[1]-second[1] != 0,
                 n[1][0] == x, n[2][0] == y, point_satisfies(first,wrong) and not point_satisfies(second,wrong)]
    elif q == 'kategori-9-3-9':
        rows = [row_of(e) for e in equations(cand['stem'])]
        ratios_a = [n[0][i]/n[0][i+1] for i in (0,2,4)]
        ratios_b = [signed(opts[1]['text'])[i]/signed(opts[1]['text'])[i+1] for i in (0,2,4)]
        flags = [system(rows[0],rows[1]) == 'ALL' and len(set(ratios_a)) == 1,
                 system(rows[2],rows[3]) == 'EMPTY' and ratios_b[0] == ratios_b[1] != ratios_b[2],
                 system(rows[4],rows[5]) == tuple(n[2])]
    elif q == 'kategori-9-3-10':
        _,diff, regular,vip,total = s
        r,v = system((F(-1),F(1),diff),(regular,vip,total))
        actual = [poly('v-r')-diff, regular*poly('r')+vip*poly('v')-total]
        flags = [[equation(e) for e in equations(opts[0]['text'])] == actual, n[1][-1] == r, n[2][-1] == v]
    elif q in ('pg-10-1-1', 'pg-10-2-1'):
        terms = [poly(e) for e in re.findall(r'\(([^()]+)\)',cand['stem'])]
        a,b = map(F,re.search(r'berupa (\d+) .*? dan (\d+) ',cand['stem']).groups())
        actual = a*terms[0]+b*terms[1]-terms[2]
        flags = [poly(o['text']) == actual for o in opts]
    elif q in ('pg-10-1-2', 'pg-10-2-2'):
        area,length = [poly(e) for e in re.findall(r'\(([^()]+)\)m',cand['stem'])]
        width,remainder = divide(area,length); test.assertFalse(remainder)
        geometry_value(test,length,width)
        actual = 2*(length+width)
        flags = [poly(o['text'].removesuffix('m')) == actual for o in opts]
    elif q == 'pg-10-1-3':
        first,second = [poly(e) for e in re.findall(r'\(([^()]+)\)',cand['stem'])]
        a,b = [F(v) for v in re.findall(r'(\d+) kali',cand['stem'])]
        flags = [poly(o['text']) == a*first+b*second for o in opts]
    elif q == 'pg-10-1-4':
        actual = poly(re.search(r'bentuk aljabar (.+?)\. Setelah',cand['stem'])[1])
        answer = actual.get((('x',1),('y',1)),0)
        flags = [signed(o['text'])[0] == answer for o in opts]
    elif q in ('pg-10-1-5', 'pg-10-2-4'):
        actual = poly(re.search(r'bentuk aljabar (.+?)\.',cand['stem'])[1])
        student = [poly(e) for e in re.findall(r'Hasil [A-Za-z]+: (.+)',cand['stem'])]
        forms = [poly(after(o['text'],'dengan')) for o in opts]
        flags = [forms[0] == actual and student[0] == actual, forms[1] == actual and student[1] == actual,
                 forms[2] == actual and all(p != actual for p in student),
                 forms[3] == actual and all(p != actual for p in student)]
    elif q in ('mcma-10-1-6', 'mcma-10-2-6'):
        flags = []
        for o in opts:
            a,b = re.search(r'dari (.+?) adalah (.+)',o['text']).groups()
            flags.append(poly(a) == poly(b))
    elif q == 'mcma-10-1-7':
        monday,tuesday,sold = [poly(e) for e in re.findall(r'Hari \w+:.*?sebanyak (.+?)\.',cand['stem'])]
        remaining = monday+tuesday-sold
        flags = [poly(after(opts[0]['text'],'adalah')) == monday,
                 poly(after(opts[1]['text'],'adalah')) == monday+tuesday,
                 poly(after(opts[2]['text'],'adalah')) == remaining,
                 signed(opts[3]['text'])[-1] == remaining.get((('q',1),),0)]
    elif q == 'mcma-10-1-8':
        actual = poly(re.search(r'kompleks: (.+?)\.',cand['stem'])[1])
        flags = [poly(after(opts[0]['text'],'adalah')) == actual,
                 signed(opts[1]['text'])[-1] == actual.get((('x',1),),0),
                 signed(opts[2]['text'])[-1] == actual.get((),0),
                 poly(after(opts[3]['text'],'dengan')) == actual]
    elif q == 'kategori-10-1-9':
        land,pond = [poly(e) for e in re.findall(r'\(([^()]+)\)',cand['stem'])]
        geometry_value(test,land,pond)
        area1,area2 = land*land,pond*pond
        flags = [poly(re.search(r'\(([^()]+)\)m',o['text'])[1]) == actual
                 for o,actual in zip(opts,(area1,area2,area1-area2))]
    elif q in ('kategori-10-1-10', 'mcma-10-2-8'):
        expression = re.search(r'(?:pecahan aljabar|pecahan) (.+?) \(dengan',cand['stem'])[1]
        actual = poly(expression); numerator = poly(expression.split('/')[0])
        test.assertIn('x,y≠0',cand['stem'])
        factored = poly(after(opts[0]['text'],'menjadi'))
        simplified = poly(after(opts[1]['text'],'sederhana' if q == 'kategori-10-1-10' else 'dengan'))
        x,y = claim_solution(opts[2]['text'],'x'),claim_solution(opts[2]['text'],'y')
        value = substitute(actual,x=x,y=y).get((),0)
        flags = [factored == numerator, simplified == actual, signed(opts[2]['text'])[-1] == value]
        if q == 'mcma-10-2-8': flags.append(signed(opts[3]['text'])[-1] == actual.get((('x',1),),0))
    elif q == 'pg-10-2-3':
        areas = [F(a)*poly(b) for a,b in re.findall(r'([0-9.,]+)\(([^()]+)\)m\^2',cand['stem'])]
        actual = areas[1]-areas[0]
        flags = [poly(o['text'].removesuffix('m^2')) == actual for o in opts]
    elif q == 'pg-10-2-5':
        factors = re.findall(r'\(([^()]+)\)',cand['stem'])
        a,b,added = [poly(e) for e in factors]
        target = poly(re.search(r'menghasilkan bentuk aljabar (.+?)\.',cand['stem'])[1])
        flags = [substitute(a*b+added,a=claim_solution(o['text'],'a')) == target for o in opts]
    elif q == 'mcma-10-2-7':
        a,b = [poly(e) for e in re.findall(r'[AB]=(.+)',cand['stem'])]
        flags = [poly(after(opts[0]['text'],'adalah')) == a+b,
                 poly(after(opts[1]['text'],'adalah')) == a-b,
                 signed(opts[2]['text'])[-1] == (a+b).get((('x',1),),0),
                 signed(opts[3]['text'])[-1] == (a-b).get((),0)]
    elif q == 'kategori-10-2-9':
        area,width = [poly(e) for e in re.findall(r'\(([^()]+)\)m',cand['stem'])]
        length,remainder = divide(area,width); test.assertFalse(remainder)
        perimeter = 2*(length+width)
        x = claim_solution(opts[2]['text']); test.assertGreater(substitute(length,x=x).get((),0),0)
        flags = [poly(re.search(r'\(([^()]+)\)m',opts[0]['text'])[1]) == length,
                 poly(re.search(r'\(([^()]+)\)m',opts[1]['text'])[1]) == perimeter,
                 signed(opts[2]['text'])[-1] == substitute(perimeter,x=x).get((),0)]
    elif q == 'pg-10-3-1':
        p,qexpr = [poly(e) for e in re.findall(r'[PQ]=(.+)',cand['stem'])]
        actual = p-qexpr
        flags = [poly(re.search(r'\(([^()]+)\)',o['text'])[1]) == actual
                 and ('linear' in o['text']) == (all(sum(d for _,d in powers) <= 1 for powers in actual))
                 for o in opts]
    elif q == 'pg-10-3-2':
        area,length,width = [poly(e) for e in re.findall(r'\(([^()]+)\)m',cand['stem'])]
        test.assertEqual(area,length*width); geometry_value(test,length,width)
        increase = s[-1]; perimeter = 2*(length+width)
        change = perimeter.get((('x',1),),0)*increase
        flags = [v and v[0] == change and 'bergantung' not in o['text'] for v,o in zip(n,opts)]
        flags = [bool(v) for v in flags]
    elif q == 'pg-10-3-3':
        factors = [poly(e) for e in re.findall(r'\(([^()]+)\)',cand['stem'])]
        target = poly(re.search(r'ekuivalen dengan bentuk aljabar (.+?)\. Nilai',cand['stem'])[1])
        difference = factors[0]*factors[1]-target
        m = linear_solution(substitute(difference,x=0),'m')
        parameter_n = linear_solution(coefficient(substitute(difference,m=m),'x'),'n')
        test.assertFalse(substitute(difference,m=m,n=parameter_n))
        flags = [signed(o['text'])[0] == m*m-parameter_n*parameter_n for o in opts]
    elif q == 'pg-10-3-4':
        expression = re.search(r'bentuk aljabar (.+?) melalui',cand['stem'])[1]
        actual = poly(expression)
        quotient_text = re.search(r'^(.+?)/\(([^()]+)\)\+',expression)
        quotient = poly(quotient_text[1])/poly(quotient_text[2])
        step1 = poly(re.search(r'Langkah 1:.+?= (.+)',cand['stem'])[1])
        step2 = poly(re.search(r'Langkah 2:.+?= (.+)',cand['stem'])[1])
        flags = [step1 != quotient and poly(after(opts[0]['text'],'hasil akhir yang benar adalah')) == actual,
                 poly(after(opts[1]['text'],'seharusnya')) == step2,
                 step1 == quotient, poly(after(opts[3]['text'],'seharusnya')) == Poly()]
    elif q == 'pg-10-3-5':
        side,length,width = [poly(e) for e in re.findall(r'[spl]=\(([^()]+)\)m',cand['stem'])]
        square,rectangle = 4*side,2*(length+width)
        claimed = poly(re.search(r'yaitu \(([^()]+)\)m',opts[0]['text'])[1])
        difference = square-rectangle
        flags = [square == rectangle == claimed, False if not difference else None,
                 difference == aspoly(-n[2][0]), bool(difference) and substitute(difference,x=0) == Poly()]
    elif q == 'mcma-10-3-6':
        p,qexpr = re.search(r'P=(.+?) dan Q=(.+?)\.(?=\s|$)',cand['stem']).groups(); p,qexpr = poly(p),poly(qexpr)
        x = claim_solution(opts[2]['text'])
        values = signed(opts[1]['text'])
        flags = [p == qexpr, values == [qexpr.get((('x',2),),0),qexpr.get((('x',1),),0),qexpr.get((),0)],
                 signed(opts[2]['text'])[-1] == substitute(p,x=x).get((),0), not bool(p-qexpr)]
    elif q == 'mcma-10-3-7':
        actual = poly(re.search(r'bentuk kuadrat (.+?)\.(?=\s|$)',cand['stem'])[1])
        first,second = re.search(r'dari (.+?) adalah (.+)',opts[0]['text']).groups()
        factor = poly(re.search(r'\(([^()]+)\)',opts[1]['text'])[1])
        _,remainder = divide(actual,factor)
        x = claim_solution(opts[2]['text'])
        falsefactor = poly(after(opts[3]['text'],'dengan'))
        flags = [poly(first) == actual == poly(second), not bool(remainder),
                 substitute(actual,x=x).get((),0) == signed(opts[2]['text'])[-1], actual == falsefactor]
    elif q == 'mcma-10-3-8':
        a,b = [poly(e) for e in re.findall(r'[AB]=(.+)',cand['stem'])]
        flags = [poly(after(opts[0]['text'],'menjadi')) == a, a == b, not bool(a-b),
                 signed(opts[3]['text'])[-1] == a.get((('y',1),),0)]
    elif q == 'kategori-10-3-9':
        actual = poly(re.search(r'ekspresi aljabar (.+?)\.',cand['stem'])[1])
        square,rhs = re.search(r'dari (.+?) adalah (.+)',opts[0]['text']).groups()
        source,claim = re.search(r'dari (.+?) adalah (.+)',opts[1]['text']).groups()
        x = claim_solution(opts[2]['text'])
        flags = [poly(square) == poly(rhs), poly(source) == actual == poly(claim),
                 substitute(actual,x=x).get((),0) == signed(opts[2]['text'])[-1]]
    elif q == 'kategori-10-3-10':
        length,width,base,height = [poly(e) for e in re.findall(r'[plat]=\(([^()]+)\)m',cand['stem'])]
        geometry_value(test,length,width); geometry_value(test,base,height)
        area1,area2 = length*width,base*height/F(2)
        flags = [poly(re.search(r'\(([^()]+)\)m',o['text'])[1]) == actual
                 for o,actual in zip(opts,(area1,area2,area2-area1))]
    test.assertIsNotNone(flags, 'independent oracle missing: '+q)
    test.assertEqual([o['correct'] for o in opts], flags, (q, cand))
