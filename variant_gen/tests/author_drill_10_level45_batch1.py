"""Indicator 10 C4/C5 authoring; rendered polynomial identities form the oracle."""
import re
from build_drill_1_5_level45_batch1 import Author


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    a.variables['x'] = dict(gen='derived', expr="'{x}' if k == 0 else 'x'")
    if (a.l, a.n) == (4, 3):
        a.allnums({'5': '5+k', '11': '11+3*k', '10': '10+2*k'})
        a.exp = a.explanation('Perkalian faktor memberikan $6x^2-[[11+3*k]]x-[[10+2*k]]=(2x-[[5+k]])(3x+2)$. Hanya A sesuai; perluas setiap opsi untuk membandingkan koefisien.')
    elif (a.l, a.n) == (4, 6):
        a.allnums({'3': '3+k', '5': '5+k', '8': '8+k'})
        a.exp = a.explanation('Ada empat suku berbeda. Koefisien xy adalah $-[[5+k]]$, konstanta $-[[8+k]]$. Suku $[[3+k]]x^2$ dan $-[[5+k]]xy$ berbeda pangkat variabel, sehingga bukan sejenis. A, B, C benar; D salah.')
    elif (a.l, a.n) == (5, 1):
        a.allnums({'3': '3+k', '4': '4', '7': '7+5*k', '23': '23+5*k', '15': '15+5*k'})
        # The inner coefficient 4 is fixed; only the resulting coefficient of x changes.
        a.stem = a.stem.replace('$'+a.var('4', '4')+'x', '$'+a.var('4+2*k', '4')+'x')
        a.options[3] = a.nums(a.options[3], {'8': '8+2*k'})
        a.exp = a.explanation('Distribusikan setiap faktor: $[[3+k]](2x-5y)-2(x-4y)=[[4+2*k]]x-[[7+5*k]]y$. Perkalian $(-2)(-4y)=8y$ bertanda positif. Siswa X benar; hanya B memberi alasan yang tepat.')
    elif (a.l, a.n) == (5, 6):
        # Change the first coefficient only, preserving all distributive sign traps.
        a.stem = a.stem.replace('5a', a.var('5+k', '5')+'a')
        a.options[0] = a.options[0].replace('5a', a.var('5+k', '5')+'a')
        a.options[2] = a.options[2].replace('6a', a.var('6+k', '6')+'a')
        a.options[3] = a.options[3].replace('$8$', '$'+a.var('8+k', '8')+'$')
        a.exp = a.explanation('Buka kurung dengan perubahan tanda: $[[5+k]]a-2b+3(a-4b)-(2a-5b)=[[6+k]]a-9b$. Suku a adalah $[[5+k]]a+3a-2a$, suku b adalah $-9b$. Koefisien a $[[6+k]]$, bukan $[[8+k]]$. A, B, C benar; D salah.')
    else:
        raise ValueError((a.i, a.l, a.n))
    return a


def _math(text):
    return re.findall(r'\$([^$]+)\$', text)


def _poly(text):
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    from sympy import Symbol, expand
    text = text.replace('{', '').replace('}', '').replace('^', '**').replace('×', '*')
    assert re.fullmatch(r'[0-9abxy+*()\-\s]+', text), text
    return expand(parse_expr(text, local_dict={v: Symbol(v) for v in 'abxy'},
                             transformations=standard_transformations+(implicit_multiplication_application,)))


def check_math(qid, candidate):
    from sympy import Poly, Symbol
    _, indicator, level, number = qid.split('-')
    assert int(indicator) == 10
    key = int(level), int(number)
    stem = [_poly(t) for t in _math(candidate['stem'])]
    options = candidate['options']
    chunks = [_math(o['text']) for o in options]
    target = stem[0]
    x, y, a, b = [Symbol(v) for v in 'xyab']
    if key == (4, 3):
        truths = [_poly(c[0]) == target for c in chunks]
        assert sum(truths) == 1
    elif key == (4, 6):
        p = Poly(target, x, y)
        truths = [len(p.terms()) == int(re.search(r'\d+', options[0]['text'])[0]),
                  p.coeff_monomial(x*y) == _poly(chunks[1][-1]),
                  p.coeff_monomial(1) == _poly(chunks[2][-1])]
        t1, t2 = [Poly(_poly(t), x, y) for t in chunks[3][:2]]
        truths.append(t1.monoms() == t2.monoms())
    elif key == (5, 1):
        tx, ty = stem[1] == target, stem[2] == target
        def equation(text):
            sides = [_poly(t) for t in text.split('=')]
            return all(s == sides[0] for s in sides[1:])
        # The first option explicitly asserts X is wrong; the second asserts X is right.
        truths = [not tx and equation(chunks[0][0]) and _poly(chunks[0][0].split('=')[-1]) == target.coeff(y)*y,
                  tx and equation(chunks[1][0]) and _poly(chunks[1][0].split('=')[-1]) == target.coeff(y)*y,
                  ty and False,
                  not tx and not ty and _poly(chunks[3][-1]) == target.coeff(x)*x]
    elif key == (5, 6):
        truths = [_poly(chunks[0][-1]) == target.coeff(a)*a,
                  _poly(chunks[1][-1]) == target.coeff(b)*b,
                  _poly(chunks[2][-1]) == target,
                  _poly(chunks[3][-1]) == target.coeff(a)]
    else:
        raise AssertionError(key)
    assert [bool(o['correct']) for o in options] == [bool(t) for t in truths], (qid, truths)
    # API records append answer summaries; validate the authored explanation itself.
    explanation = _math(re.split(r'\n\n(?:Jawaban:|Penilaian pernyataan:)', candidate['explanation'], maxsplit=1)[0])
    assert explanation, candidate['explanation']
    for expression in explanation:
        if '=' in expression:
            sides = [_poly(t) for t in expression.split('=')]
            assert all(t == sides[0] for t in sides), expression
    if key != (4, 6):
        assert any('=' in t and _poly(t.split('=')[0]) == target for t in explanation)
    else:
        assert [_poly(t) for t in explanation] == [target.coeff(x*y), target.subs({x: 0, y: 0}), target.coeff(x, 2)*x**2, target.coeff(x*y)*x*y]

if __name__ == '__main__':
    import json
    from copy import deepcopy
    from pathlib import Path
    from engine import assemble, build_values
    audit = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    entries = json.loads(audit.read_text(encoding='utf8'))['entries']
    count = 0
    for e in entries:
        if e['indicator'] != 10 or (e['level'], e['source_number']) not in {(4, 3), (4, 6), (5, 1), (5, 6)}:
            continue
        a = author(e)
        cfg = a.config({'hash': 'self-check', 'options': [{'id': chr(65+j)} for j in range(4)]})
        for k in range(31):
            candidate = assemble(cfg, build_values(cfg, lambda n, s: k))
            check_math(a.qid, candidate)
            if k == 0:
                assert candidate['stem'] == a.s['stem']
                assert [o['text'] for o in candidate['options']] == a.s['options']
            for mutation in ('answer', 'explanation'):
                bad = deepcopy(candidate)
                if mutation == 'answer':
                    bad['options'][0]['correct'] = not bad['options'][0]['correct']
                else:
                    bad['explanation'] = '1+1=999'
                try:
                    check_math(a.qid, bad)
                except AssertionError:
                    pass
                else:
                    raise AssertionError((a.qid, k, mutation))
            count += 1
    assert count == 124, count
    print('124 rendered algebra checks passed; four originals exact.')
