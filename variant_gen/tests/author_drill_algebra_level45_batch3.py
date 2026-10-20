"""Batch-three algebra families; exact rendered mathematics checked independently."""
import ast
import re
from fractions import Fraction
from build_drill_1_5_level45_batch1 import Author

SELECTION = {(7, 5, 3), (9, 4, 10), (10, 5, 5)}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    key = (a.i, a.l, a.n)
    if key == (7, 5, 3):
        a.allnums({'4': '4+2*k', '2': '2+k'})
        a.stem = a.stem.replace(a.var('2+k', '2') + 'x', '2x')
        exp = 'Kedua ruas menjadi $[[4+2*k]]x-[[2+k]]$. Identitas berlaku untuk semua bilangan real x; hanya Siswa B benar, opsi D.'
    elif key == (9, 4, 10):
        a.allnums({'10': '10+2*k', '14': '14+2*k', '7': '7+k', '3': '3+k'})
        a.options[1] = a.options[1].replace('(7,3)', '(' + a.var('7+k', '7') + ',' + a.var('3+k', '3') + ')')
        exp = 'Penjumlahan memberi $2x=[[14+2*k]]$, sehingga x = [[7+k]] dan y = [[3+k]]. Determinan -2 tidak nol; titik potong tunggal. Pernyataan 1 dan 2 benar; 3 salah.'
    elif key == (10, 5, 5):
        for old, expr, literal in [('2x+3', '2+k', '2'), ('4x', '4+k', '4'), ('3x', '3+k', '3')]:
            replacement = a.var(expr, literal) + ('x+3' if old == '2x+3' else 'x')
            a.stem = a.stem.replace(old, replacement)
            a.options = [t.replace(old, replacement) for t in a.options]
        exp = 'Baris ketiga = baris pertama + 2 kali beda = $[[4+k]]x+1$. Baris kedua = $[[3+k]]x+2$. Untuk x bilangan bulat minimal 2, jumlah kursi positif dan bertambah. Hanya A benar; mengalikan baris pertama dengan 3 bukan rumus baris ketiga.'
    else:
        raise ValueError(key)
    a.exp = a.explanation(exp)
    return a


def value(expression, x):
    """Parse displayed arithmetic with exact fractions, without runtime eval."""
    expression = expression.replace('{x}', 'x').replace(' ', '')
    expression = re.sub(r'(\d|\))(?=[x(])', r'\1*', expression)
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return Fraction(node.value)
        if isinstance(node, ast.Name) and node.id == 'x':
            return Fraction(x)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
        raise AssertionError(expression)
    return visit(ast.parse(expression, mode='eval').body)


def same(left, right):
    return all(value(left, x) == value(right, x) for x in (0, 1, 2))


def check_math(qid, candidate):
    key = tuple(map(int, qid.split('-')[1:]))
    s = candidate['stem']
    t = [o['text'] for o in candidate['options']]
    exp = re.split(r'\n\n(?:Jawaban:|Penilaian pernyataan:)', candidate['explanation'])[0]
    if key == (7, 5, 3):
        left, right = re.search(r'\$([^$]+)\$', s)[1].split('=')
        identity = same(left, right)
        constant = value(left, 0) - value(right, 0)
        slope = value(left, 1) - value(right, 1) - constant
        no_solution = slope == 0 and constant != 0
        residual_left, residual_right = re.search(r'\$([^$]+)\$', t[0])[1].split('=')
        single = re.findall(r'\$([^$]+)\$', t[2])[-1].split('=')[1]
        option_left, option_right = re.findall(r'\$([^$]+)\$', t[3])[0].split('=')
        truth = [no_solution and value(residual_left,0)-value(residual_right,0) == constant,
                 no_solution and slope == 0,
                 slope != 0 and value(single,0) == -constant/slope,
                 identity and same(left, option_left) and same(right, option_right)]
        shown = re.search(r'\$([^$]+)\$', exp)[1]
        assert same(shown, left) and 'semua bilangan real' in exp
    elif key == (9, 4, 10):
        total, difference = map(int, re.search(r'x\+y=(\d+)\$\n\$x-y=(\d+)', s).groups())
        x, y = Fraction(total+difference, 2), Fraction(total-difference, 2)
        coefficient, rhs, claim = map(int, re.search(r'(\d+)x = (\d+) \\implies x = (\d+)', t[0]).groups())
        pair_match = re.search(r'\((\d+),(\d+)\)', t[1])
        assert pair_match, t[1]
        pair = tuple(map(int, pair_match.groups()))
        truth = [coefficient == 2 and rhs == total+difference and claim == x, pair == (x,y), False]
        assert re.search(r'2x=(\d+)', exp)[1] == str(total+difference)
        assert tuple(map(int, re.search(r'x = (\d+) dan y = (\d+)', exp).groups())) == (x,y)
        assert 'Determinan -2' in exp
    elif key == (10, 5, 5):
        assert re.search(r'baris ke-(\d+)', s)[1] == '3'
        assert all(re.search(r'baris ke-(\d+)', text)[1] == '3' for text in t[:2])
        first = re.search(r'pertama memuat \$([^$]+)\$', s)[1]
        difference = re.search(r'bertambah \$([^$]+)\$', s)[1]
        claim = re.findall(r'\$([^$]+)\$', s)[-1]
        target = '('+first+')+2('+difference+')'
        chain = re.search(r'\$([^$]+)\$', t[0])[1].lstrip('=').split('=')
        second, third = [re.search(r'\$([^$]+)\$', text)[1] for text in t[1:3]]
        truth = [same(claim,target) and all(same(part,target) for part in chain), not same(claim,target) and same(second,target), not same(claim,target) and same(third,target), same(claim,target) and same('3('+first+')',target)]
        shown = re.findall(r'\$([^$]+)\$', exp)
        assert same(shown[0], target) and same(shown[1], '('+first+')+('+difference+')')
        assert value(first,2)>0 and value(difference,2)>0
    else:
        raise ValueError(qid)
    assert [bool(o['correct']) for o in candidate['options']] == truth, (qid, s, t, truth)
    return truth


if __name__ == '__main__':
    import json
    from pathlib import Path
    from engine import assemble, build_values
    from filters import validate_candidate
    path = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for e in json.loads(path.read_text(encoding='utf8'))['entries']:
        if tuple(e[z] for z in ('indicator','level','source_number')) not in SELECTION: continue
        a = author(e)
        orig = {'hash':'self-check','format':a.s['format'],'stem':a.s['stem'],'options':[{'id':str(j+1) if a.s['format']=='KATEGORI' else chr(65+j),'text':v,'correct':a.correct[j]} for j,v in enumerate(a.s['options'])]}
        cfg = a.config(orig)
        accepted = []
        for k in range(31):
            candidate = assemble(cfg, build_values(cfg, lambda name,spec:k))
            check_math(a.qid, candidate)
            for suffix in ('\n\nJawaban: A', '\n\nPenilaian pernyataan: 1 Benar'):
                check_math(a.qid, dict(candidate, explanation=candidate['explanation']+suffix))
            if k == 0:
                assert candidate['stem'] == a.s['stem']
                assert [o['text'] for o in candidate['options']] == a.s['options']
                assert [o['correct'] for o in candidate['options']] == a.correct
            elif not validate_candidate(candidate, orig, accepted): accepted.append(candidate)
            count += 1
        assert len(accepted) >= 20, (a.qid, len(accepted))
    assert count == 93
    print('93 variants: mathematics, explanations, exact originals; >=20 accepted per family')
