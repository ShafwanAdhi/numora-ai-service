"""Four audited I8 C5 families; rendered arithmetic checked independently."""
import re
from build_drill_1_5_level45_batch1 import Author

SELECTION = {(8, 5, n) for n in (3, 5, 9, 10)}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    assert (a.i, a.l, a.n) in SELECTION
    if a.n == 3:
        # Only mathematical spans: step labels remain fixed.
        mapping = {'5': '5+k', '10': '10+2*k', '6': '6+2*k', '14': '14+2*k', '7': '7+k'}
        def math(m):
            return '$' + a.nums(m[1], mapping) + '$'
        a.stem = re.sub(r'\$([^$]+)\$', math, a.stem)
        a.options = [re.sub(r'\$([^$]+)\$', math, t) for t in a.options]
        exp = 'Batas solusi x < [[-7-k]]. Langkah 1, 2, 3 benar; Langkah 4 salah karena pembagian dengan -2 membalik tanda > menjadi <. Hanya C benar.'
    elif a.n == 5:
        a.allnums({'500': '500+30*k', '16': '16+k', '530': '530+30*k', '18': '18+k', '12': '12+k'})
        exp = 'Maksimum [[15+k]] karung. Beban [[16+k]] karung adalah [[530+30*k]] kg, melebihi kapasitas [[500+30*k]] kg. Hanya B benar.'
    elif a.n == 9:
        a.allnums({'140': '140+3*k', '26': '26+k', '25': '25+k'})
        exp = 'Maksimum [[25+k]] kotak; beban pada maksimum [[140+3*k]] kg. Model 3x+65≤[[140+3*k]] benar. Pernyataan 1 dan 3 benar; pernyataan 2 salah.'
    else:
        a.allnums({'8': '8+2*k', '4': '4+k'})
        exp = 'Batas [[-4-k]]. Formulasi I memiliki satu solusi x=[[-4-k]]; Formulasi II memiliki x≥[[-4-k]], tak hingga solusi. Pembagian dengan -2 membalik tanda ≤ menjadi ≥. Pernyataan 1 dan 2 benar; 3 salah.'
    a.exp = a.explanation(exp)
    return a


def numbers(text):
    return [float(v.replace('.', '').replace(',', '.')) for v in re.findall(r'-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?', text)]


def check_math(qid, candidate):
    """Derive solutions from displayed premises; inspect every displayed numeric claim."""
    key = tuple(map(int, qid.split('-')[1:]))
    assert key in SELECTION
    s = candidate['stem']
    t = [o['text'] for o in candidate['options']]
    exp = candidate['explanation']
    n = key[2]
    if n == 3:
        equations = re.findall(r'\$([^$]+)\$', s)
        c, a, b, r = map(float, re.fullmatch(r'(\d+)-(\d+)\(x\+(\d+)\)>(\d+)', equations[0]).groups())
        bound = (c-a*b-r)/a
        assert numbers(equations[1]) == [c, -a, -a*b, r]
        assert numbers(equations[2]) == [-a, c-a*b, r]
        assert numbers(equations[3]) == [-a, r-c+a*b]
        assert all('>' in v and '<' not in v for v in equations)
        assert equations[4].startswith('x>') and numbers(equations[4]) == [bound]
        assert [numbers(v) for v in t] == [[1,c,-a,a*b,r], [3,-a,2], [4,bound,-a], [1,4]]
        truth = [False, False, 'x<' in t[2] and 'dibalik' in t[2], False]
        assert numbers(exp)[0] == bound and 'membalik tanda > menjadi <' in exp
    elif n == 5:
        a, fixed, capacity, load = numbers(s)
        maximum = int((capacity-fixed)//a)
        total = a*load+fixed
        v = [numbers(x) for x in t]
        assert v == [[load,capacity], [load,a,load,fixed,total,capacity], [maximum+3], [maximum-3]]
        assert '≤' in s and 'kg>' in t[1] and t[1].count('=') == 2
        truth = [total==capacity and total<=capacity, total>capacity, total<=capacity and v[2][0]==maximum, total>capacity and v[3][0]==maximum]
        assert numbers(exp)[:4] == [maximum,load,total,capacity]
    elif n == 9:
        weight, driver, capacity = numbers(s)
        maximum = int((capacity-driver)//weight)
        v = [numbers(x) for x in t]
        assert v == [[weight,driver,capacity], [maximum+1], [maximum]]
        truth = [v[0]==[weight,driver,capacity] and '≤' in t[0], v[1][0]==maximum, weight*v[2][0]+driver<=capacity]
        assert numbers(exp)[:5] == [maximum,weight*maximum+driver,weight,driver,capacity]
    else:
        a, b, c, d = numbers(s)
        assert a == c < 0 and b == d
        assert re.search(r'Formulasi I \(PLSV\): \$-\d+x=\d+\$', s)
        assert re.search(r'Formulasi II \(PtLSV\): \$-\d+x≤\d+\$', s)
        bound = b/a
        v = [numbers(x) for x in t]
        assert v == [[bound], [bound,a], []]
        truth = [v[0][0]==bound and 'tunggal' in t[0], v[1][0]==bound and '≥' in t[1] and 'berubah arah' in t[1], False]
        assert numbers(exp)[:3] == [bound,bound,bound] and 'tak hingga solusi' in exp
    assert [bool(o['correct']) for o in candidate['options']] == truth, (qid, truth)
    return truth


if __name__ == '__main__':
    import json
    from pathlib import Path
    from engine import assemble, build_values
    from filters import validate_candidate
    path = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for e in json.loads(path.read_text(encoding='utf8'))['entries']:
        if tuple(e[z] for z in ('indicator','level','source_number')) not in SELECTION:
            continue
        a = author(e)
        orig = {'hash':'self-check', 'format':a.s['format'], 'stem':a.s['stem'], 'options':[{'id':str(j+1) if a.s['format']=='KATEGORI' else chr(65+j), 'text':v, 'correct':a.correct[j]} for j,v in enumerate(a.s['options'])]}
        cfg = a.config(orig)
        accepted = []
        for k in range(31):
            candidate = assemble(cfg, build_values(cfg, lambda name,spec:k))
            check_math(a.qid, candidate)
            check_math(a.qid, dict(candidate, explanation=candidate['explanation']+'\nJawaban: ringkasan API'))
            if k == 0:
                assert candidate['stem'] == orig['stem']
                assert candidate['options'] == orig['options']
            elif not validate_candidate(candidate, orig, accepted):
                accepted.append(candidate)
            count += 1
        assert len(accepted) >= 20, (a.qid,len(accepted))
    assert count == 124
    print('124 variants: mathematics, explanations, exact originals; >=20 accepted per family')
