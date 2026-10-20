"""Batch-three capacity and inequality families; rendered arithmetic oracle."""
import math
import re
from build_drill_1_5_level45_batch1 import Author

SELECTION = {(8, 4, 5), (8, 4, 7), (8, 4, 8)}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    key = (a.i, a.l, a.n)
    if key == (8, 4, 5):
        a.allnums({'800': '800+25*k', '30': '30+k', '810': '810+25*k',
                   '32': '32+k', '29': '29+k', '785': '785+25*k', '28': '28+k'})
        exp = ('Maksimum kotak = [[29+k]]. Beban maksimum aman = [[785+25*k]] kg; '
               'satu kotak tambahan memberi [[810+25*k]] kg, melebihi kapasitas [[800+25*k]] kg. '
               'A melampaui kapasitas; B mengabaikan sopir; C benar; D belum maksimum.')
    elif key == (8, 4, 7):
        a.stem = a.stem.replace('≥13', '≥' + a.var('13+3*k', '13'))
        a.options = [a.nums(t, {'3': '3+k', '4': '4+k'}) for t in a.options]
        exp = ('Batas maksimum = [[-3-k]]. Nilai uji = [[-4-k]]. '
               'Pembagian dengan bilangan negatif membalik ≥ menjadi ≤. '
               'B dan C benar; A salah arah. D salah: batas termasuk, lingkaran harus penuh dengan panah ke kiri.')
    elif key == (8, 4, 8):
        a.stem = a.stem.replace('2x-3', '2x-' + a.var('3+k', '3')).replace('<1', '<' + a.var('1+k', '1'))
        a.options[0] = a.options[0].replace('-6', '-' + a.var('6+2*k', '6'))
        a.options[2] = a.options[2].replace('-7', a.var('-7-3*k', '-7'))
        exp = ('Konstanta ruas kiri = [[-6-2*k]]. Batas bawah = [[-7-3*k]]. '
               'Ruas kiri adalah -x ditambah konstanta tersebut. Penyelesaian x lebih besar secara ketat '
               'daripada batas bawah. A dan C benar. B salah: penyederhanaan tidak membalik tanda; '
               'pembagian dengan bilangan negatif membalik tanda. D benar karena nol lebih besar daripada batas bawah.')
    else:
        raise ValueError(key)
    a.exp = a.explanation(exp)
    return a


def numbers(text):
    return [float(v.replace('.', '').replace(',', '.')) for v in
            re.findall(r'-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?', text)]


def check_math(qid, candidate):
    """Compute bounds from displayed stimulus, then check each displayed claim."""
    key = tuple(map(int, qid.split('-')[1:]))
    s = candidate['stem']
    t = [o['text'] for o in candidate['options']]
    exp = candidate['explanation']
    if key == (8, 4, 5):
        cap, driver, weight = numbers(s)
        maximum = math.floor((cap-driver)/weight)
        n, w, repeated, d, total = numbers(t[0])
        assert w == weight and d == driver and w*repeated+d == total and n == repeated
        a = n == maximum and total <= cap
        n, c, w, quotient = numbers(t[1])
        assert c == cap and w == weight and c/w == quotient
        b = n == maximum and n == quotient and weight*n+driver <= cap
        n, w, repeated, d, total, c = numbers(t[2])
        assert w == weight and d == driver and n == repeated and w*n+d == total and c == cap
        c_truth = n == maximum and total <= cap
        n, c = numbers(t[3])
        truth = [a, b, c_truth, n == maximum and c == cap]
        assert numbers(exp)[:4] == [maximum, weight*maximum+driver, weight*(maximum+1)+driver, cap]
    elif key == (8, 4, 7):
        c, coefficient, rhs = map(float, re.search(r'\$(\d+)-(\d+)x≥(\d+)\$', s).groups())
        bound = (c-rhs)/coefficient
        truth = [numbers(t[0]) == [bound] and '≤' in t[0],
                 numbers(t[1]) == [bound] and '≤' in t[1],
                 c-coefficient*numbers(t[2])[0] >= rhs,
                 numbers(t[3]) == [bound] and 'penuh' in t[3] and 'kiri' in t[3]]
        assert numbers(exp)[:2] == [bound, numbers(t[2])[0]] and 'lingkaran harus penuh' in exp
    elif key == (8, 4, 8):
        a, b, c, d, rhs = map(float, re.search(r'\$(\d+)\((\d+)x-(\d+)\)-(\d+)x<(\d+)\$', s).groups())
        coefficient, constant = a*b-d, -a*c
        bound = (rhs-constant)/coefficient
        constant_claim = numbers(t[0])[0]
        test = numbers(t[3])[0]
        truth = [coefficient == -1 and constant_claim == constant,
                 False, numbers(t[2]) == [bound] and '>' in t[2] and coefficient < 0,
                 coefficient*test+constant < rhs]
        assert numbers(exp)[:2] == [constant, bound] and 'penyederhanaan tidak membalik tanda' in exp
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
        if tuple(e[z] for z in ('indicator', 'level', 'source_number')) not in SELECTION:
            continue
        a = author(e)
        orig = {'hash': 'self-check', 'format': a.s['format'], 'stem': a.s['stem'],
                'options': [{'id': chr(65+j), 'text': v, 'correct': a.correct[j]}
                            for j, v in enumerate(a.s['options'])]}
        cfg = a.config(orig)
        accepted = []
        for k in range(31):
            candidate = assemble(cfg, build_values(cfg, lambda name, spec: k))
            check_math(a.qid, candidate)
            if k == 0:
                assert candidate['stem'] == a.s['stem']
                assert [o['text'] for o in candidate['options']] == a.s['options']
                assert [o['correct'] for o in candidate['options']] == a.correct
            elif not validate_candidate(candidate, orig, accepted):
                accepted.append(candidate)
            count += 1
        assert len(accepted) >= 20, (a.qid, len(accepted))
    assert count == 93
    print('93 variants: mathematics, explanations, exact originals; >=20 accepted per family')
