"""Independent rendered-text oracle. Does not import production math/config evaluation.

Fractions and integer square comparisons are exact. Decimal roots are calculated
at 60-digit precision, with explicit half-up rounding and strict interval checks.
"""
import ast
import math
import re
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction as F

NUM = r'-?\d+(?:\.\d{3})*(?:,\d+)?'


def num(s):
    return F(s.replace('.', '').replace(',', '.'))


def numbers(s):
    return [num(x) for x in re.findall(NUM, s)]


def clean(s):
    s = re.sub(r'(?<!\d)\d{1,3}(?:\.\d{3})+(?!\d)', lambda m: m[0].replace('.', ''), s)
    s = re.sub(r'\\+sqrt\{\s*([^{}]+?)\s*\}', r'sqrt(\1)', s)
    s = re.sub(r'\\+frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\+(?:left|right)', '', s)
    s = re.sub(r'\{(\d+)\}', r'\1', s)
    return s.replace('$', '').replace('×', '*').replace('⋅', '*').replace('−', '-').replace('°', '')


def rnd(x, places=0):
    x = F(x)
    scale = 10**places
    v = x * scale
    return F(math.floor(v + F(1, 2)) if v >= 0 else -math.floor(-v + F(1, 2)), scale)


def root(n):
    with localcontext() as ctx:
        ctx.prec = 60
        return F(Decimal(n).sqrt())


def shown(x):
    x = rnd(x, 6)
    n, rem = divmod(abs(x.numerator), x.denominator)
    out = f'{n:,}'.replace(',', '.')
    if rem:
        out += ',' + str(int(F(rem, x.denominator)*10**6)).zfill(6).rstrip('0')
    return ('-' if x < 0 else '') + out


def require(explanation, text):
    assert ' '.join(clean(text).split()).casefold() in ' '.join(clean(explanation).split()).casefold(), (text, explanation)


def calc(expression):
    """Small test-only scalar arithmetic parser, separate from the config evaluator."""
    expression = clean(expression).replace(':', '/').replace('^', '**')
    expression = re.sub(NUM.removeprefix('-?'), lambda m: '(' + str(num(m[0])) + ')', expression)
    tree = ast.parse(expression.strip(), mode='eval')

    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and type(n.value) is int: return F(n.value)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -ev(n.operand) if isinstance(n.op, ast.USub) else ev(n.operand)
        if isinstance(n, ast.BinOp):
            x, y = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Add): return x+y
            if isinstance(n.op, ast.Sub): return x-y
            if isinstance(n.op, ast.Mult): return x*y
            if isinstance(n.op, ast.Div): return x/y
            if isinstance(n.op, ast.Pow):
                assert y.denominator == 1 and 0 <= y <= 12
                return x**int(y)
        raise AssertionError(ast.dump(n))
    return ev(tree)


def chain(line):
    sides = line.split('=')
    vals = [calc(s) for s in sides]
    assert all(v == vals[0] for v in vals), (line, vals)
    return vals[0]


def radical(n):
    n = int(n)
    for d in range(math.isqrt(n), 0, -1):
        if n % (d*d) == 0: return d, n//(d*d)
    raise AssertionError(n)


def radical_sum(s):
    terms = re.findall(r'([+-]?)\s*(\d*)\s*sqrt\((\d+)\)', clean(s))
    assert terms, s
    answer = {}
    for sign, c, n in terms:
        d, b = radical(int(n))
        answer[b] = answer.get(b, 0) + (-1 if sign == '-' else 1)*int(c or 1)*d
    return {b: c for b, c in answer.items() if c}


def check_math(qid, candidate):
    _, i, l, n = qid.split('-'); i, l, n = int(i), int(l), int(n)
    stem = clean(candidate['stem'])
    opts = [clean(o['text']) for o in candidate['options']]
    exp = clean(candidate['explanation'])
    truths = None
    if i == 1 and n == 2:
        a, b = map(int, re.findall(r'sqrt\((\d+)\)', stem)[:2])
        da, ba = radical(a); db, bb = radical(b)
        assert ba == bb
        irrational = ba != 1 and da != db
        repeats = re.search(r'y=0,(\d+)\.\.\.', stem)[1]
        assert len(repeats) == 6 and repeats[:2]*3 == repeats
        truths = [False, not irrational, irrational, False]
        require(exp, f'Radikan dasar = {shown(b)}')
        require(exp, f'x = sqrt({shown(b)})')
        require(exp, f'blok berulang {int(repeats[:2])}/99')
    elif i == 1 and n == 3:
        match = re.search(r'pembelian ('+NUM+r') set.*?Rp('+NUM+r').*?Rp('+NUM+r')', stem, re.S)
        count, p, q = map(num, match.groups())
        # Independently evaluate each proposed model, not its stored key.
        truths = [calc(t) == count*(p+q) for t in opts]
        require(exp, f'Biaya = {shown(count)} * ({shown(p)} + {shown(q)}) = {shown(count*(p+q))}')
    elif i == 1 and n == 6:
        negative = num(re.search(r'\{('+NUM+r');', stem)[1])
        square = int(re.search(r'sqrt\((\d+)\)', stem)[1])
        frac = re.search(r'\((\d+)\)/\((\d+)\)', stem)
        p, q = map(int, frac.groups())
        assert negative < 0 and negative.denominator == 1
        assert math.isqrt(square)**2 == square
        assert numbers(opts[0])[0] == negative
        assert int(re.search(r'sqrt\((\d+)\)', opts[1])[1]) == square
        opfrac = re.search(r'\((\d+)\)/\((\d+)\)', opts[2])
        assert tuple(map(int, opfrac.groups())) == (p, q)
        if l == 4:
            decimal = num(re.search(r'desimal berhenti\s*('+NUM+r')', opts[2])[1])
            assert decimal == F(p, q)
            require(exp, f'{p}/4 = {shown(F(p,q))}')
        else:
            require(exp, f'{p}/7 adalah pecahan rasional')
            assert 'sqrt(2)' in opts[3] and math.isqrt(2)**2 != 2
        truths = [True, False, True, True]
        require(exp, f'sqrt({shown(square)}) = {math.isqrt(square)}')
        require(exp, f'-{abs(int(negative))}')
    elif i == 1 and n in (1, 9):
        if n == 1:
            p = num(re.search(r'Saluran P:\s*('+NUM+')', stem)[1])
            q = -root(int(re.search(r'Saluran Q:.*?sqrt\((\d+)\)', stem)[1]))
            rmatch = re.search(r'Saluran R:.*?\((\d+)\)/\((\d+)\)', stem)
            r = -F(*map(int, rmatch.groups()))
            positions = dict(P=p, Q=q, R=r)
            proper = sorted(positions, key=positions.get)
            results = {}
            for label, line in re.findall(r'Evaluasi ([IV]+): ([^\n]+)', stem):
                order = re.findall(r'Saluran ([PQR])', line)
                assert sorted(order) == ['P', 'Q', 'R']
                # Check the echoed value accompanying each name as well as its order.
                for name, value in re.findall(r'Saluran ([PQR]) \((.*?) m\)', line):
                    if 'sqrt' in value:
                        actual = -root(int(re.search(r'sqrt\((\d+)\)', value)[1]))
                    elif '/' in value:
                        actual = calc(value)
                    else: actual = num(value)
                    assert actual == positions[name]
                results[label] = order == proper
            truths = [results[t.replace('Evaluasi ', '')] for t in opts]
            require(exp, f'P = {shown(p)}')
            require(exp, f'R = -{int(-r*5)}/5')
        elif l == 4:
            a = num(re.search(r'Larutan A:\s*('+NUM+')', stem)[1])
            frac = re.search(r'Larutan B:.*?\((\d+)\)/\((\d+)\)', stem)
            b = -F(*map(int, frac.groups()))
            rad = int(re.search(r'Larutan C:.*?sqrt\((\d+)\)', stem)[1]); c = -root(rad)
            vals = numbers(opts[0]); assert vals[-1] == b
            assert numbers(opts[1])[0] == a and numbers(opts[1])[1] == b
            truths = [True, a < b, b < a < c]
            require(exp, f'A = {shown(a)}')
            require(exp, f'= {shown(b)}')
            require(exp, f'C = -sqrt({shown(rad)})')
        else:
            a = num(re.search(r'Sampel 1:\s*('+NUM+')', stem)[1])
            frac = re.search(r'Sampel 2:.*?\((\d+)\)/\((\d+)\)', stem)
            b = -F(*map(int, frac.groups()))
            rad = int(re.search(r'Sampel 3:.*?sqrt\((\d+)\)', stem)[1]); c = -root(rad)
            # The source's displayed approximation is rounded to three decimals.
            approx = num(re.search(r'≈\s*('+NUM+')', opts[1])[1]); assert approx == rnd(c, 3)
            truths = [a == b, c < a, a == b and a < c]
            require(exp, f'Sampel 1 = Sampel 2 = {shown(a)}')
            require(exp, f'Sampel 3 = -sqrt({shown(rad)})')
    elif i == 2 and n == 4:
        expression = re.search(r'Soal:([^\n]+)', stem)[1]
        correct = calc(expression)
        first = num(re.search(r'Evaluasi I:.*?adalah ('+NUM+')', stem)[1])
        second = num(re.search(r'Evaluasi II:.*?adalah ('+NUM+')', stem)[1])
        assert first == correct
        a, b, c, d = numbers(expression)
        assert second == (a/b+c)*d
        truths = [first == correct, False, False, False]
        if 'hasil:' in opts[0]: assert num(re.search(r'hasil: ('+NUM+')', opts[0])[1]) == correct
        require(exp, f'Hasil benar = {shown(correct)}')
        require(exp, f'Hasil cara berurutan yang keliru = {shown(second)}')
    elif i == 2 and n == 6:
        expr = re.search(r'Ekspresi:([^\n]+)', stem)[1]
        terms = re.findall(r'(\d*)sqrt\((\d+)\)', expr)
        assert len(terms) == 3
        first = radical_sum((terms[0][0] or '1')+'sqrt('+terms[0][1]+')')
        third = radical_sum('sqrt('+terms[2][1]+')')
        total = radical_sum(expr)
        truths = []
        for j, t in enumerate(opts):
            target = (first if j == 0 else radical_sum('sqrt('+terms[1][1]+')') if j == 1
                      else third if j == 2 else total)
            if j < 3:
                assert radical_sum(t.split('adalah ', 1)[0]) == target, 'Option echoes a different operand'
            claim = t.split('adalah ', 1)[1].split('"')[0].strip().rstrip('.')
            claimed = radical_sum(claim)
            truths.append(claimed == target)
        assert len(total) == 1
        coef = next(iter(total.values())); first_coef = next(iter(first.values()))
        require(exp, f'Koefisien suku pertama = {shown(first_coef)}')
        require(exp, f'= {shown(coef)}. A, C, D benar')
    elif i == 2 and n == 8:
        transaction = stem.split('Dua bentuk model')[0]
        x, p, y, q, d = numbers(transaction)
        first, second = x*p, y*q
        actual = first+second-d
        model_lines = re.findall(r'Model (?:[12]|I|II): (.+)', stem)
        assert len(model_lines) == 2
        assert chain(model_lines[0]) == actual
        assert chain(model_lines[1]) == x*(p+y)*q-d
        assert model_lines[0] != model_lines[1]
        claims = [numbers(t)[-1] for t in opts[2:]]
        truths = [False, True, claims[0] == actual, claims[1] == actual]
        require(exp, f'Belanja pertama = {shown(first)}')
        require(exp, f'Belanja kedua = {shown(second)}')
        require(exp, f'Sebelum potongan = {shown(first+second)}')
        require(exp, f'Potongan = {shown(d)}')
        require(exp, f'Pengeluaran akhir = {shown(actual)}')
    elif i == 2 and n == 1:
        initial = num(re.search(r'Uang awal di kas: Rp('+NUM+')', stem)[1])
        amount, price = map(num, re.search(r'Pembelian ('+NUM+r') pak.*?Rp('+NUM+')', stem).groups())
        incoming = num(re.search(r'pendaftaran.*?Rp('+NUM+')', stem)[1])
        out = num(re.search(r'konsumsi.*?Rp('+NUM+')', stem)[1])
        answer = initial-amount*price+incoming-out
        reports = {}
        for label, expression in re.findall(r'Evaluasi ([IV]+): (.+)', stem):
            value = chain(expression)
            reports[label] = value == answer
        assert sum(reports.values()) == 1
        truths = [reports[t.replace('Evaluasi ', '')] for t in opts]
        require(exp, f'Biaya buku = {shown(amount)} * {shown(price)} = {shown(amount*price)}')
        require(exp, f'Saldo akhir = {shown(initial)} - {shown(amount*price)} + {shown(incoming)} - {shown(out)} = {shown(answer)}')
    elif i == 2 and n == 2:
        expr = re.search(r'Panjang Pipa=([^\n]+)', stem)[1]
        roots = list(map(int, re.findall(r'sqrt\((\d+)\)', expr)))
        u, v, w = [radical(x) for x in roots]
        assert u[1] == v[1] == w[1] == 2
        coef = u[0]+v[0]-w[0]
        wrong = int(re.search(r'Evaluasi X:.*?sqrt\((\d+)\)', stem)[1])
        assert wrong == roots[0]+roots[1]-roots[2]
        assert wrong != coef*coef*2, 'Wrong evaluation accidentally became numerically correct'
        correct_claim = int(re.search(r'Evaluasi Y:.*?adalah (\d+)sqrt', stem)[1])
        assert coef == correct_claim
        false_claim = int(re.search(r'adalah (\d+)sqrt', opts[3])[1]); assert false_claim != coef
        truths = [False, False, True, False]
        if 'hasil:' in opts[2]: assert num(re.search(r'hasil: ('+NUM+')', opts[2])[1]) == coef
        require(exp, f'Koefisien akar sejenis = {u[0]} + {v[0]} - {w[0]} = {coef}')
        require(exp, f'Hasil = {coef}*sqrt(2) meter')
    elif i == 3 and n == 1:
        value = numbers(stem.split('Laporan')[0])[0]
        thousand, hundred = rnd(value/1000)*1000, rnd(value/100)*100
        results = {}
        for label, line in re.findall(r'(?:Analisis|Evaluasi) ([IV]+): (.+)', stem):
            results[label] = numbers(line) == [thousand, hundred]
        truths = [results[t.split()[-1]] for t in opts]
        require(exp, f'ribuan = {shown(thousand)}')
        require(exp, f'ratusan = {shown(hundred)}')
        require(exp, f'data {shown(value)}')
    elif i == 3 and n == 2:
        rads = list(map(int, re.findall(r'sqrt\((\d+)\)', stem)[:2]))
        pair = [rnd(root(r), 1) for r in rads]
        truths = [numbers(t) == pair for t in opts]
        for rad, val in zip(rads, pair):
            assert (val-F(1,20))**2 <= rad < (val+F(1,20))**2
            require(exp, f'sqrt({rad}) dibulatkan menjadi {shown(val)} m')
    elif i == 3 and n == 6:
        lines = dict(re.findall(r'\((i|ii|iii|iv)\) ([^\n]+)', stem))
        x, claimed = numbers(lines['i'])
        match = re.search(r'sqrt\((\d+)\).*?adalah ('+NUM+')', lines['ii'])
        rad, claim2 = int(match[1]), num(match[2])
        r3, lo, hi = numbers(lines['iii'])
        x4, y4, est = numbers(lines['iv'])
        r1, r2 = rnd(x,1), rnd(root(rad),1)
        expected4 = rnd(x4/100)*100*rnd(y4/100)*100
        truths = [claimed == r1, claim2 == r2, lo*lo < r3 < hi*hi, est == expected4]
        require(exp, f'(i) Nilai pembulatan yang benar = {shown(r1)}')
        require(exp, f'(ii) Aproksimasi akar yang benar = {shown(r2)}')
        require(exp, f'Batas akar = {shown(lo)} dan {shown(hi)}')
        require(exp, f'(iv) Hasil estimasi = {shown(expected4)}')
    elif i == 3 and n == 9:
        masses = [num(x) for x in re.findall(r'Bahan [XYZABC]: ('+NUM+')', stem)]
        assert len(masses) == 3
        x, y, z = masses
        v0, v1 = numbers(opts[0]), numbers(opts[1])
        assert v0[0] == x and v1[0] == y
        total = sum(rnd(v,1) for v in masses)
        truths = [v0[-1] == rnd(x,1), v1[-1] == rnd(y), numbers(opts[2])[-1] == total]
        require(exp, f'Massa pertama ke persepuluhan = {shown(rnd(x,1))}')
        require(exp, f'Massa kedua ke satuan = {shown(rnd(y))}')
        require(exp, f'Massa kedua ke persepuluhan = {shown(rnd(y,1))}')
        require(exp, f'Total estimasi = {shown(total)}')
    elif i == 4 and n == 1 and l == 4:
        from datetime import date, timedelta
        intervals = list(map(int, re.findall(r'setiap (\d+) hari', stem)))
        assert len(intervals) == 3
        period = math.lcm(*intervals)
        start_day = int(re.search(r'pada tanggal (\d+) Mei', stem)[1])
        start = date(2026,5,start_day)
        months = {'Mei':5,'Juni':6,'Juli':7,'Agustus':8}
        results = {}
        for label, line in re.findall(r'Analisis ([IV]+): (.+)', stem):
            calculation, ds, month = re.search(r'terjadi (.+?) hari setelah .*?yaitu tanggal (\d+) (\w+)', line).groups()
            delta = chain(calculation)
            results[label] = delta == 2*period and date(2026,months[month],int(ds)) == start+timedelta(days=int(delta))
        truths = [results[t.split()[-1]] for t in opts]
        require(exp, f'KPK(6,8,12) = {period} hari')
        require(exp, f'Tanggal mulai = {start_day} Mei')
        require(exp, f'(3-1)*{period} = {2*period} hari')
    elif i == 4 and n == 1:
        intervals = list(map(int, re.findall(r'setiap (\d+) detik', stem)))
        period = math.lcm(*intervals)
        claim1 = int(re.search(r'Evaluasi I:.*?ke-(\d+)', stem)[1])
        claim2 = int(re.search(r'Evaluasi II:.*?ke-(\d+)', stem)[1])
        operands, proof = re.search(r'KPK\(([^)]+)\)=(\d+)', stem).groups()
        assert [int(x) for x in operands.split(',')] == intervals
        assert int(proof) == period
        assert claim1 != period and claim2 == period
        assert numbers(opts[1]) == [period, *intervals]
        assert chain(re.search(r'karena (.*)', opts[3])[1]) == math.prod(intervals)
        truths = [False, True, False, False]
        require(exp, f'= {shown(period)} detik')
        require(exp, f'Klaim {shown(claim1)} salah')
    elif i == 4 and n == 6:
        a, b, c = map(int, numbers(stem.split('Seorang siswa')[0].replace(',', ' ')))
        gcd, lcm = math.gcd(a,b,c), math.lcm(a,b,c)
        for text in opts:
            for operands in re.findall(r'(?:FPB|KPK)\(([^)]+)\)', text):
                assert [int(x) for x in operands.split(',')] == [a,b,c], 'FPB/KPK echoes stale operands'
        expression = re.search(r'adalah (.+?)(?:"|\.|$)', opts[0])[1].strip()
        factored = calc(expression)
        target = int(re.search(r'dari (\d+)', opts[0])[1])
        assert target in (a,b,c)
        claims = []
        for t in opts[1:]:
            claims.append(numbers(t)[-1])
        truths = [factored == target, claims[0] == gcd, claims[1] == gcd, claims[2] == lcm]
        require(exp, f'KPK = {shown(lcm)}')
        if l == 4: require(exp, f'FPB = {shown(gcd)}')
        else: require(exp, f') = {shown(gcd)} karena')
    elif i == 4 and n in (9,10):
        a, b = map(int,numbers(stem)[:2]); g = math.gcd(a,b)
        if n == 9:
            claims = [numbers(t)[-1] for t in opts]
            truths = [claims[0] == g, claims[1] == b//g, claims[2] == (a+b)//g]
            require(exp, f') = {g}')
            require(exp, f'Minuman per kantong = {a//g}, makanan per kantong = {b//g}; total = {(a+b)//g}')
        else:
            truths = [numbers(opts[0])[-1] == g, numbers(opts[1])[-1] == (a+b)//g, b//g == 2*(a//g)]
            assert numbers(opts[2])[:2] == [b,a]
            require(exp, f') = {g} cm')
            require(exp, f'Jumlah potongan = {a//g}+{b//g} = {(a+b)//g}')
    elif i == 5 and n == 1:
        limit = 'Dua siswa' if l == 4 else 'Dua anggota'
        a,b,c,d = numbers(stem.split(limit)[0])
        same = a/b == c/d
        assert same and a/b == F(1,3)
        if l == 4:
            match = re.search(r'Analisis ([IV]+): Campuran A dan Campuran B keduanya', stem)
            assert match
            truths = [t == 'Analisis '+match[1] for t in opts]
            require(exp, f'Campuran A = {shown(a)}:{shown(b)} = 1:3')
            require(exp, f'Campuran B = {shown(c)}:{shown(d)} = 1:3')
        else:
            match = re.search(r'Evaluasi ([AB]): "Racikan X dan Racikan Y memiliki', stem)
            assert match
            truths = [t == 'Evaluasi '+match[1] for t in opts]
            require(exp, f'Racikan X = {shown(a)}:{shown(b)} = 1:3')
            require(exp, f'Racikan Y = {shown(c)}:{shown(d)} = 1:3')
    elif i == 5 and n == 6:
        first = 'Kotak A:' if l == 4 else 'Tempat I:'
        second = 'Kotak B:' if l == 4 else 'Tempat II:'
        a,b = numbers(stem.split(first)[1].splitlines()[0])
        c,d = numbers(stem.split(second)[1].splitlines()[0])
        def ratio(t):
            x,y = map(int,re.search(r'(\d+):(\d+)',t).groups())
            return F(x,y)
        truths = [ratio(opts[0]) == a/b, ratio(opts[1]) == c/d, a/b == c/d, ratio(opts[3]) == a/(a+b)]
        reduced = F(a,b)
        require(exp, f'= {reduced.numerator}:{reduced.denominator}')
        redtotal = F(a,a+b)
        require(exp, f'Rasio merah ke total = {redtotal.numerator}:{redtotal.denominator}')
        shown_num, shown_den = map(int,re.search(r'(\d+):(\d+)', opts[3]).groups())
        assert shown_num % 2 == shown_den % 2 == 1 and shown_den-shown_num == 2
        assert math.gcd(shown_num,shown_den) == 1
        require(exp, 'kedua suku ganjil dan selisihnya 2, sehingga FPB keduanya 1')
    elif i == 5 and n == 9:
        rows = re.findall(r'Paket [XYAB]: berisi (\d+) \w+ seharga Rp('+NUM+')', stem)
        assert len(rows) == 2
        a,p,b,q = num(rows[0][0]),num(rows[0][1]),num(rows[1][0]),num(rows[1][1])
        x,y = p/a,q/b
        claims = [num(re.search(r'Rp('+NUM+')',t)[1]) for t in opts[:2]]
        truths = [claims[0] == x, claims[1] == y, y < x]
        unit = 'lembar' if l == 4 else 'kotak'
        first,second = ('X','Y') if l == 4 else ('A','B')
        require(exp, f'Harga {first} per {unit} = {shown(x)}')
        require(exp, f'Harga {second} per {unit} = {shown(y)}')
        require(exp, f'Selisih = {shown(x-y)}')
    assert truths is not None, qid
    actual = [o['correct'] for o in candidate['options']]
    assert actual == truths, (qid, actual, truths, candidate)
    if qid.startswith('pg-'): assert sum(truths) == 1, (qid, truths)
    return truths
