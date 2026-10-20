"""Final indicator-10 batch: source-faithful variants with rendered algebra checks."""
import re
from build_drill_1_5_level45_batch1 import Author
from author_drill_10_level45_batch1 import _math

SELECTION = {(4, 1), (4, 4), (4, 9), (4, 10), (5, 2), (5, 4), (5, 7), (5, 10)}


def _map_math(a,text,mapping,keep_power=False):
    def change(m):
        t = m[1].replace('^{2}', '^POWER') if keep_power else m[1]
        return '$'+a.nums(t,mapping).replace('^POWER','^{2}')+'$'
    return re.sub(r'\$([^$]+)\$',change,text)

def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    for name in ('x', 'a', 'y'):
        a.variables[name] = dict(gen='derived', expr=repr('{'+name+'}')+" if k == 0 else "+repr(name))
    key = a.l, a.n
    if key == (4, 1):
        a.stem = a.nums(a.stem, {'5':'5+k'})
        a.options = [a.nums(t, {'4':'4+k','8':'8+2*k'}) for t in a.options]
        a.exp = a.explanation('Keliling adalah $2((3x+[[5+k]])+(2x-1))=10x+[[8+2*k]]$. B benar; A lupa faktor 2; C dan D tidak sesuai.')
    elif key == (4, 4):
        mapping = {'3':'3+2*k','9':'(3+2*k)**2','6':'(3+2*k)*(2+k)'}
        a.stem = _map_math(a, a.stem, mapping)
        a.options = [_map_math(a,t,mapping) for t in a.options]
        a.stem = a.stem.replace('x+2', 'x+'+a.var('2+k','2'))
        a.options = [t.replace('x+2', 'x+'+a.var('2+k','2')) for t in a.options]
        a.exp = a.explanation('Faktorisasi pembilang $4x^2-[[(3+2*k)**2]]=(2x-[[3+2*k]])(2x+[[3+2*k]])$. Penyebut $2x^2+x-[[(3+2*k)*(2+k)]]=(2x-[[3+2*k]])(x+[[2+k]])$. Hasil $\\frac{4x^2-[[(3+2*k)**2]]}{2x^2+x-[[(3+2*k)*(2+k)]]}=\\frac{2x+[[3+2*k]]}{x+[[2+k]]}$. Domain asal: x != -[[2+k]] dan x != [[(3+2*k)/2]]. D benar: langkah 4 menyalin faktor yang salah.')
    elif key == (4, 9):
        a.allnums({'5.000':'5000+100*k','2.000':'2000+100*k','19.000':'19000+500*k'})
        a.answer_value(0, '19000+500*k', ' rupiah untuk belanja Rani')
        a.exp = a.explanation('Total $(3x+2y)+(2x+4y)=5x+6y$. Selisih $(3x+2y)-(2x+4y)=x-2y$. Belanja Rani $3*[[5000+100*k]]+2*[[2000+100*k]]=[[19000+500*k]]$. Pernyataan 1 dan 3 benar, 2 salah.')
    elif key == (4, 10):
        a.allnums({'4':'4+k','8':'2*(4+k)','12':'3*(4+k)','24':'6*(4+k)'})
        a.exp = a.explanation('Komutatif $3a+5b=5b+3a$. Distributif $[[4+k]](2x-3y)=[[2*(4+k)]]x-[[3*(4+k)]]y$. Asosiatif $(2x*3y)*[[4+k]]z=[[6*(4+k)]]xyz$. Pengurangan tidak komutatif: 5-3 berbeda dari 3-5. Pernyataan 1 dan 2 benar, 3 salah.')
    elif key == (5, 2):
        # Vary the shared a coefficient while preserving the three identities.
        a.stem = a.stem.replace('2(3a', '2('+a.var('3+3*k','3')+'a').replace('3(3a', '3('+a.var('3+2*k','3')+'a')
        # Both expansions have coefficient 9+6k for a.
        # Inner coefficient of the second summand stays 1.
        a.stem = a.stem.replace('9a', a.var('9+6*k','9')+'a')
        a.answer_value(2, '11+6*k', ' saat a=b=1')
        a.exp = a.explanation('Formulasi 1 $2([[3+3*k]]a+4b)+3(a-2b)=[[9+6*k]]a+2b$. Formulasi 3 $3([[3+2*k]]a+b)-b=[[9+6*k]]a+2b$. Ketiganya identik. Pada a=b=1 nilainya [[11+6*k]]. C benar.')
    elif key == (5, 4):
        mapping = {'2':'2+k','3':'3+k','5':'5+2*k','6':'(2+k)*(3+k)','9':'(3+k)**2'}
        a.stem = _map_math(a,a.stem,mapping,True)
        a.options = [_map_math(a,t,mapping,True) for t in a.options]
        a.exp = a.explanation('Pembilang $x^2-[[5+2*k]]x+[[(2+k)*(3+k)]]=(x-[[2+k]])(x-[[3+k]])$. Penyebut $x^2-[[(3+k)**2]]=(x-[[3+k]])(x+[[3+k]])$. Hasil $\\frac{x^2-[[5+2*k]]x+[[(2+k)*(3+k)]]}{x^2-[[(3+k)**2]]}=\\frac{x-[[2+k]]}{x+[[3+k]]}$. Domain asal: x != -[[3+k]] dan x != [[3+k]]. D benar: suku x tidak boleh dicoret dari penjumlahan.')
    elif key == (5, 7):
        a.allnums({'5':'5+k','7':'7+2*k','15':'3*(5+k)','10':'2*(5+k)'})
        a.exp = a.explanation('Distribusi $(2x-3)(x+[[5+k]])=2x^2+[[7+2*k]]x-[[3*(5+k)]]$. Suku luar $2x*[[5+k]]=[[2*(5+k)]]x$; suku dalam $(-3)*x=-3x$. C menukar posisi luar dan dalam, sehingga salah. B dan D benar; A salah tanda faktor kedua.')
    elif key == (5, 10):
        # Keep universal identities; change the coefficient of y consistently.
        def scale(t):
            return re.sub(r'\$([^$]+)\$', lambda m: '$'+m[1].replace('y', a.var("'y' if k == 0 else '('",'y')+a.var('k+1','')+a.var("'*y)'",''))+'$', t)
        a.stem = scale(a.stem)
        a.options = [scale(t) for t in a.options]
        a.answer_value(0, '(k+2)**2', ' untuk identitas I saat x=y=1')
        a.exp = a.explanation('Kuadrat jumlah $(x+[[k+1]]y)^2=x^2+[[2*(k+1)]]xy+[[(k+1)**2]]y^2$. Kuadrat selisih $(x-[[k+1]]y)^2=x^2-[[2*(k+1)]]xy+[[(k+1)**2]]y^2$. Selisih kuadrat $(x+[[k+1]]y)(x-[[k+1]]y)=x^2-[[(k+1)**2]]y^2$. Pernyataan 1 dan 2 benar, 3 salah. Nilai identitas I saat x=y=1 adalah [[(k+2)**2]].')
    else:
        raise ValueError(key)
    return a


def _poly(text):
    from sympy import Symbol, cancel
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, rationalize
    text = text.replace('meter','').replace('Ãƒâ€”','*')
    while '\\frac' in text:
        start = text.index('\\frac')
        pos = start+5
        groups = []
        for _ in range(2):
            assert text[pos] == '{', text
            begin = pos+1
            depth = 1
            pos += 1
            while depth:
                depth += (text[pos] == '{')-(text[pos] == '}')
                pos += 1
            groups.append(text[begin:pos-1])
        text = text[:start]+'(('+groups[0]+')/('+groups[1]+'))'+text[pos:]
    text = re.sub(r'(?<=\d)\.(?=\d{3})','',text).replace('{','').replace('}','').replace('^','**')
    assert re.fullmatch(r'[0-9.abcxyz+*/()\-\s]+',text), text
    return cancel(parse_expr(text, local_dict={v:Symbol(v) for v in 'abcxyz'}, transformations=standard_transformations+(implicit_multiplication_application,rationalize,)))


def check_math(qid, c):
    from sympy import Symbol, denom, together, solve
    key = tuple(map(int,qid.split('-')[-2:]))
    chunks = [_math(o['text']) for o in c['options']]
    stem = _math(c['stem'])
    exptext = re.split(r'\n\n(?:Jawaban:|Penilaian pernyataan:)',c['explanation'],maxsplit=1)[0]
    exp = _math(exptext)
    equations = [_poly(t.split("=")[0]) for t in exp if "=" in t]
    assert exp
    for eq in exp:
        if '=' in eq:
            sides = [_poly(t) for t in eq.split('=')]
            assert all(s == sides[0] for s in sides), eq
    x,y = Symbol('x'),Symbol('y')
    if key == (4,1):
        target = 2*(_poly(stem[0])+_poly(stem[1]))
        truths = [_poly(t[0]) == target for t in chunks]
        assert target in equations
    elif key in {(4,4),(5,4)}:
        target = _poly(stem[0])
        assert _poly(exp[-1].split('=')[0]) == target
        # Original denominator roots must remain excluded after cancellation.
        assert re.findall(r'Langkah ([1-4]):',c['stem']) == ['1','2','3','4']
        from sympy import cancel
        assert cancel(_poly(stem[1]) / _poly(stem[2])) == target
        raw = stem[0]
        denominator = raw[raw.index('}{')+2:-1]
        roots = solve(_poly(denominator),x)
        exclusions = re.findall(r'x != (-?[0-9.,]+)',exptext)
        assert sorted(roots) == sorted(_poly(t.rstrip('.').replace(',','.')) for t in exclusions), (roots,exclusions)
        # Each claim must refer to the actual step, including its rationale.
        for step, option in enumerate(c['options'], 1):
            assert option['text'].startswith(f'Langkah {step} salah'), option
        assert 'tidak boleh' in c['options'][2]['text']
        assert _poly(stem[1]) == _poly(exp[0].split('=')[0])
        assert _poly(chunks[0][0]) != _poly(stem[1])
        truths = [False,False,False,True]
        if key == (4,4):
            assert len(chunks[3]) == 2
            assert _poly(chunks[3][0]) == target
            assert 'sisa faktor pembilang' in c['options'][3]['text']
            assert cancel(_poly(chunks[3][1]) - _poly(stem[1]) / _poly(stem[3])) == 0
        else:
            assert _poly(stem[4]) == target
            assert len(chunks[3]) == 2
            assert _poly(chunks[3][1]) == target
            assert 'bukan faktor perkalian sehingga tidak boleh dicoret' in c['options'][3]['text']
    elif key == (4,9):
        total = _poly(chunks[0][0]); difference = _poly(chunks[1][0])
        xv = _poly(chunks[2][0].split('=')[1]); yv = _poly(chunks[2][1].split('=')[1])
        amount = int(re.search(r'Rp([\d.]+)', c['options'][2]['text'])[1].replace('.',''))
        assert total in equations and 3*xv+2*yv in equations
        truths = [total==5*x+6*y,difference==x-2*y,3*xv+2*yv==amount]
        if 'hasil:' in c['options'][0]['text']:
            assert int(re.search(r'hasil: ([\d.]+)',c['options'][0]['text'])[1].replace('.','')) == amount
    elif key == (4,10):
        assert _poly(chunks[1][0]) in equations
        truths = [all(_poly(t)==_poly(chunks[0][0].split('=')[0]) for t in chunks[0][0].split('=')),_poly(chunks[1][0])==_poly(chunks[1][1]),False]
    elif key == (5,2):
        p = [_poly(t) for t in stem]
        assert p[0] in equations
        truths = [p[0]==p[1] and p[1]!=p[2],p[1]==p[2] and p[0]!=p[1],p[0]==p[1]==p[2],all(p[i]!=p[j] for i,j in ((0,1),(0,2),(1,2)))]
        if 'hasil:' in c['options'][2]['text']:
            assert int(re.search(r'hasil: ([\d.]+)',c['options'][2]['text'])[1].replace('.','')) == p[0].subs({Symbol('a'):1,Symbol('b'):1})
    elif key == (5,7):
        target = _poly(stem[0])
        factors = re.fullmatch(r'\(2x-3\)\(x\+(\d+)\)',chunks[1][0])
        assert factors, chunks[1]
        outer, inner = 2*int(factors[1])*x, -3*x
        claim_inner, claim_outer = [_poly(t) for t in chunks[2]]
        truths = [_poly(chunks[0][0])==target,_poly(chunks[1][0])==target,claim_inner==inner and claim_outer==outer,_poly(chunks[3][0])==_poly(chunks[3][1])==target]
        assert _poly(exp[0].split('=')[0])==target
    elif key == (5,10):
        assert all(_poly(t.split('=')[0]) in equations for t in stem)
        truths = [all(_poly(t.split('=')[0])==_poly(t.split('=')[1]) for t in stem[:2]),_poly(stem[2].split('=')[0])==_poly(stem[2].split('=')[1]),_poly(chunks[2][0])==_poly(chunks[2][1])]
        if 'hasil:' in c['options'][0]['text']:
            assert int(re.search(r'hasil: ([\d.]+)',c['options'][0]['text'])[1].replace('.','')) == _poly(stem[0].split('=')[0]).subs({x:1,y:1})
    else:
        raise AssertionError(key)
    assert [bool(o['correct']) for o in c['options']] == [bool(t) for t in truths], (qid,truths)


if __name__ == '__main__':
    import json
    from pathlib import Path
    from engine import assemble, build_values
    from filters import validate_candidate
    path = Path(__file__).resolve().parents[2]/'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for e in json.loads(path.read_text(encoding='utf8'))['entries']:
        if e['indicator'] != 10 or (e['level'],e['source_number']) not in SELECTION:
            continue
        a = author(e)
        cfg = a.config({'hash':'self-check','options':[{'id':chr(65+j)} for j in range(len(a.options))]})
        accepted = []
        for k in range(31):
            c = assemble(cfg,build_values(cfg,lambda n,s:k))
            check_math(a.qid,c)
            if k == 0:
                assert c['stem']==a.s['stem'],(a.qid,c['stem'])
                assert [o['text'] for o in c['options']]==a.s['options']
                assert [o['correct'] for o in c['options']]==a.correct
                orig = dict(c,format=e['format'])
            else:
                reasons=validate_candidate(c,orig,accepted)
                assert not reasons,(a.qid,k,reasons)
                accepted.append(c)
            from copy import deepcopy
            for field in ('answer', 'explanation'):
                bad = deepcopy(c)
                if field == 'answer':
                    bad['options'][0]['correct'] = not bad['options'][0]['correct']
                else:
                    bad['explanation'] = '$1+1=999$'
                try:
                    check_math(a.qid,bad)
                except AssertionError:
                    pass
                else:
                    raise AssertionError((a.qid,k,field))
            count += 1
        assert len(accepted)>=20
    assert count==248,count
    print('248 rendered checks passed; eight originals exact; 240 distinct variants accepted.')



