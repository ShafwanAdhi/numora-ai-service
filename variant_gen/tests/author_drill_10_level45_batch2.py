"""Second indicator-10 batch; rendered polynomial identities are the oracle."""
import re
from build_drill_1_5_level45_batch1 import Author
from author_drill_10_level45_batch1 import _math, _poly as _base_poly


def _poly(text):
    return _base_poly(re.sub(r'(?<=\d)\.(?=\d{3}(?:\D|$))', '', text))

SELECTION = {(4, 5), (4, 8), (5, 3), (5, 8)}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    for name in ('x', 'a', 'm'):
        a.variables[name] = dict(gen='derived', expr=repr('{'+name+'}')+" if k == 0 else "+repr(name))
    if (a.l, a.n) == (4, 5):
        a.allnums({'4': '4+2*k', '5': '5+k', '10': '10+2*k', '16': '16+8*k', '8': '8+4*k'})
        a.exp = a.explanation('Distribusikan kedua bentuk: $3(2x-[[4+2*k]])+[[4+2*k]](x+1)=[[10+2*k]]x-[[8+4*k]]$. Bentuk II $2([[5+k]]x-[[4+2*k]])=[[10+2*k]]x-[[8+4*k]]$. Keduanya ekuivalen untuk setiap x; Andi benar, Budi salah. A salah pada konstanta; C salah tanda; D salah karena kesetaraan berlaku untuk semua x.')
    elif (a.l, a.n) == (4, 8):
        a.stem = a.stem.replace('16', a.var('(4+k)**2', '16')).replace('(a-4)(a+4)', '(a-'+a.var('4+k', '4')+')(a+'+a.var('4+k', '4')+')')
        for attr in ('stem',):
            a.stem = a.stem.replace('2{x}^{2}+5x-3=(2x-1)(x+3)', a.nums('2{x}^{2}+5x-3=(2x-1)(x+3)', {'5':'5+2*k','3':'3+k'}))
        a.options[3] = a.nums(a.options[3], {'3':'3+k','5':'5+2*k','6':'6+2*k'})
        a.exp = a.explanation('Selisih kuadrat: $a^2-[[(4+k)**2]]=(a-[[4+k]])(a+[[4+k]])$. Kuadrat sempurna: $x^2+6x+9=(x+3)^2$. Distribusi: $(2x-1)(x+[[3+k]])=2x^2+[[5+2*k]]x-[[3+k]]$. Hubungan iv salah karena $(x-2)(x+3)=x^2+x-6$. A, C, D benar; B salah.')
    elif (a.l, a.n) == (5, 3):
        a.allnums({'3':'3+k','12':'4*(3+k)','9':'(3+k)**2'})
        a.exp = a.explanation('Kuadrat sempurna: $4x^2-[[4*(3+k)]]x+[[(3+k)**2]]=(2x-[[3+k]])^2$. Suku tengah sama dengan dua kali hasil kali 2x dan -[[3+k]]. A benar. B menghasilkan selisih kuadrat tanpa suku tengah; C memiliki koefisien x berbeda; D salah karena faktorisasi tersedia.')
    elif (a.l, a.n) == (5, 8):
        a.allnums({'3':'3+k','12':'4*(3+k)','9':'(3+k)**2','24':'8*(3+k)'})
        a.exp = a.explanation('Penjabaran pertama: $(2x+[[3+k]])^2=4x^2+[[4*(3+k)]]x+[[(3+k)**2]]$. Penjabaran kedua: $(2x-[[3+k]])^2=4x^2-[[4*(3+k)]]x+[[(3+k)**2]]$. Selisih: $(2x+[[3+k]])^2-(2x-[[3+k]])^2=[[8*(3+k)]]x$. A, C, D benar; B salah karena konstanta kuadrat selalu positif.')
    else:
        raise ValueError((a.i, a.l, a.n))
    return a


def _equal(text):
    sides = [_poly(t) for t in text.split('=')]
    return all(t == sides[0] for t in sides[1:])


def check_math(qid, candidate):
    from sympy import Symbol
    _, indicator, level, number = qid.split('-')
    assert int(indicator) == 10
    key = int(level), int(number)
    stem = _math(candidate['stem'])
    chunks = [_math(o['text']) for o in candidate['options']]
    if key == (4, 5):
        p, q = [_poly(t) for t in stem[1:3]]
        x = Symbol('x')
        truths = [p != q and _poly(chunks[0][0]) == p and _poly(chunks[0][1]) == q,
                  p == q and _poly(chunks[1][0]) == p,
                  p != q and p.subs(x, 0) == _poly(chunks[2][0]),
                  p != q and (p-q).subs(x, 0) == 0]
        target = p
    elif key == (4, 8):
        relations = [_equal(t) for t in stem]
        truths = [relations[0], relations[3], relations[1] and _equal(chunks[2][0]), relations[2] and _equal(chunks[3][0])]
        target = _poly(stem[0].split('=')[0])
    elif key == (5, 3):
        target = _poly(stem[0])
        truths = [_poly(chunks[j][0]) == target for j in range(3)] + [False]
    elif key == (5, 8):
        p, q = [_poly(t) for t in stem[1:3]]
        truths = [_poly(chunks[0][0]) == _poly(chunks[0][1]),
                  _poly(chunks[1][0]) == _poly(chunks[1][1]),
                  p == _poly(chunks[2][0]), p == q]
        target = p
    else:
        raise AssertionError(key)
    assert [bool(o['correct']) for o in candidate['options']] == [bool(t) for t in truths], (qid, truths)
    exp = _math(re.split(r'\n\n(?:Jawaban:|Penilaian pernyataan:)', candidate['explanation'], maxsplit=1)[0])
    assert exp and any('=' in t and _poly(t.split('=')[0]) == target for t in exp)
    assert all(_equal(t) for t in exp if '=' in t), exp


if __name__ == '__main__':
    import json
    from pathlib import Path
    from copy import deepcopy
    from engine import assemble, build_values
    from filters import validate_candidate
    path = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for e in json.loads(path.read_text(encoding='utf8'))['entries']:
        if e['indicator'] != 10 or (e['level'], e['source_number']) not in SELECTION:
            continue
        a = author(e)
        cfg = a.config({'hash':'self-check','options':[{'id':chr(65+j)} for j in range(4)]})
        accepted = []
        for k in range(31):
            c = assemble(cfg, build_values(cfg, lambda n, s: k))
            check_math(a.qid, c)
            if k == 0:
                assert c['stem'] == a.s['stem']
                assert [o['text'] for o in c['options']] == a.s['options']
                assert [o['correct'] for o in c['options']] == a.correct
                orig = dict(c, format=e['format'])
            else:
                reasons = validate_candidate(c, orig, accepted)
                assert not reasons, (a.qid, k, reasons)
                accepted.append(c)
            for field in ('answer', 'explanation'):
                bad = deepcopy(c)
                if field == 'answer':
                    bad['options'][0]['correct'] = not bad['options'][0]['correct']
                else:
                    bad['explanation'] = '$1+1=999$'
                try:
                    check_math(a.qid, bad)
                except AssertionError:
                    pass
                else:
                    raise AssertionError((a.qid, k, field))
            count += 1
        assert len(accepted) >= 20
    assert count == 124, count
    print('124 rendered algebra checks passed; four originals exact; 120 distinct candidates accepted.')
