"""Eight audited originals: numeric families and rendered-text math checks."""
import re
from fractions import Fraction

from build_drill_1_5_level45_batch1 import Author


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved', e['source_projection']), format=e['format'])
    a = Author(e)
    case = (a.i, a.l, a.n)
    if case == (6, 4, 3):
        a.allnums({'480': '480*(k+1)', '900': '(900+50*k)*(k+1)',
                   '6': '6+k', '8': '8', '18': '18+k', '24': '24+k'})
        a.options[1] = a.var('8+k', '8') + ' unit'
        a.exp = a.explanation('Laju tiap mesin = [[480*(k+1)]]/(12*8) = [[5*(k+1)]]. '
                             'Total mesin = [[(900+50*k)*(k+1)]]/(10*[[5*(k+1)]]) = [[18+k]]. '
                             'Tambahan = [[18+k]] - 12 = [[6+k]] unit. Opsi A benar; opsi lain bukan tambahan yang dibutuhkan.')
    elif case == (6, 4, 6):
        a.allnums({'500': '500+100*k', '80': '4*4*(500+100*k)/100',
                   '900': '2*6*3*((500+100*k)/100)**2',
                   '400': '(4*(500+100*k)/100)**2'})
        a.exp = a.explanation('Faktor panjang ke meter = [[(500+100*k)/100]]. '
                             'Keliling A = [[16*(500+100*k)/100]] meter; luas A = [[16*((500+100*k)/100)**2]] meter persegi. '
                             'Luas B = [[18*((500+100*k)/100)**2]] meter persegi, setengah klaim B. '
                             'Rasio keliling tetap 16:18 = 8:9 karena semua panjang dikali faktor sama. A, C, D benar.')
    elif case == (6, 5, 5):
        a.allnums({'24': '24*(k+1)', '30': '30*(k+1)', '3': '3*(k+1)', '6': '6*(k+1)'})
        a.exp = a.explanation('Waktu Rute 1 = [[24*(k+1)]]/40*60 = [[36*(k+1)]] menit. '
                             'Waktu Rute 2 = [[30*(k+1)]]/60*60 = [[30*(k+1)]] menit. '
                             'Rute 2 lebih cepat [[6*(k+1)]] menit, bukan lebih lambat atau setengah selisih itu. B benar.')
    elif case == (6, 5, 6):
        a.allnums({'25.000': '25000*(k+1)', '3': '3*(k+1)', '4': '4*(k+1)'})
        # Only the distance claim varies; the time remains one hour.
        a.options[1] = a.options[1].replace('$1km$', '$' + a.var('k+1', '1') + 'km$')
        a.exp = a.explanation('Jarak A = 12*[[25000*(k+1)]]/100000 = [[3*(k+1)]] km. '
                             'Jarak B = 16*[[25000*(k+1)]]/100000 = [[4*(k+1)]] km. '
                             'Selisih = [[k+1]] km; rasio tetap 12:16 = 3:4. '
                             'Waktu B = [[4*(k+1)]]/[[4*(k+1)]] = 1 jam. A, B, D benar; C salah.')
    elif case == (7, 4, 2):
        a.allnums({'80.000': '80000', '140.000': '140000+5000*k',
                   '10': '10+k', '12': '12+k', '14': '14+k', '15': '15+k'})
        a.exp = a.explanation('Persamaan dana: 80000 + 15000d = [[140000+5000*k]] + 10000d. '
                             'Maka 5000d = [[60000+5000*k]], sehingga d = [[12+k]] hari. B benar; nilai lain tidak menyamakan dana.')
    elif case == (7, 4, 9):
        a.allnums({'17.000': '17000*(k+1)', '2.000': '2000*(k+1)',
                   '6.000': '6000*(k+1)', '30.000': '30000*(k+1)'})
        a.exp = a.explanation('Model 3b + [[2000*(k+1)]] = [[17000*(k+1)]] benar. '
                             'Harga buku b = ([[17000*(k+1)]] - [[2000*(k+1)]])/3 = [[5000*(k+1)]]. '
                             'Klaim harga [[6000*(k+1)]] salah. Enam buku memerlukan [[30000*(k+1)]], tepat sama dengan uang tersedia. Pernyataan 1 dan 3 benar.')
    elif case == (7, 5, 2):
        a.allnums({'10.000': '10000*(k+1)', '160.000': '160000*(k+1)',
                   '25.000': '25000*(k+1)', '40.000': '40000*(k+1)',
                   '50.000': '50000*(k+1)', '20.000': '20000*(k+1)'})
        a.exp = a.explanation('Misalkan reguler r; VIP = 2r + [[10000*(k+1)]]. '
                             '3r + 2(2r + [[10000*(k+1)]]) = [[160000*(k+1)]]. '
                             '7r = [[140000*(k+1)]], r = [[20000*(k+1)]], VIP = [[50000*(k+1)]], '
                             'selisih = [[30000*(k+1)]]. Hanya C benar.')
    elif case == (7, 5, 7):
        a.stem = a.stem.replace('2(3x-1)+5=6x+8',
            '2(3x-' + a.var('k+1', '1') + ')+' + a.var('2*k+5', '5') + '=6x+' + a.var('k+8', '8'))
        a.options[3] = a.options[3].replace('3=8', '3=' + a.var('k+8', '8'))
        a.exp = a.explanation('Distribusi memberi 6x - [[2*(k+1)]] + [[2*k+5]] = 6x + 3. '
                             'Persamaan setara dengan 3 = [[k+8]], kontradiksi. Tidak ada penyelesaian; '
                             'bukan solusi tunggal atau tak hingga solusi. B dan D benar.')
    else:
        raise ValueError(case)
    return a


def _nums(text):
    return [Fraction(x.replace('.', '').replace(',', '.')) for x in
            re.findall(r'\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?', text)]


def check_math(qid, candidate):
    """Recompute claims from rendered operands; no generator values consulted."""
    _, i, l, n = qid.split('-')
    case = tuple(map(int, (i, l, n)))
    s = candidate['stem']
    o = [x['text'] for x in candidate['options']]
    v = _nums(s)
    if case == (6, 4, 3):
        machines, output, hours, target, deadline = v
        answer = target * machines * hours / (output * deadline) - machines
        truth = [_nums(t)[0] == answer for t in o]
    elif case == (6, 4, 6):
        _, scale, side, length, width = v
        factor = scale / 100
        truth = [_nums(o[0])[0] == 4*side*factor,
                 _nums(o[1])[0] == length*width*factor**2,
                 'sama dengan' in o[2], _nums(o[3])[0] == (side*factor)**2]
    elif case == (6, 5, 5):
        _, d1, speed1, _, d2, speed2 = v[:6]
        delta = 60*(d1/speed1-d2/speed2)
        truth = [_nums(t)[0] == abs(delta) and ('Lebih cepat' in t) == (delta > 0) for t in o]
    elif case == (6, 5, 6):
        _, scale, length_a, length_b = v
        da, db = length_a*scale/100000, length_b*scale/100000
        speed, time = _nums(o[3])
        truth = [_nums(o[0])[0] == da, _nums(o[1])[0] == db-da,
                 'sama dengan' in o[2] and 'berbeda' not in o[2], db/speed == time]
    elif case == (7, 4, 2):
        initial_a, rate_a, initial_b, rate_b = v
        answer = (initial_b-initial_a)/(rate_a-rate_b)
        truth = [_nums(t)[0] == answer for t in o]
    elif case == (7, 4, 9):
        count, _, total, _, ruler, _ = v
        books, model_ruler, model_total = _nums(o[0])
        price = (total-ruler)/count
        cash, quantity = _nums(o[2])
        truth = [books == count and model_ruler == ruler and model_total == total,
                 _nums(o[1])[-1] == price, cash >= quantity*price]
    elif case == (7, 5, 2):
        # The word 'dua' fixes the VIP multiplier at two; counts follow the surcharge.
        _, _, extra, regular_count, vip_count, total = v
        regular = (total-vip_count*extra)/(regular_count+2*vip_count)
        vip = 2*regular+extra
        truth = [_nums(o[0])[-1] == regular, _nums(o[1])[-1] == vip,
                 _nums(o[2])[-1] == vip, _nums(o[3])[-1] == vip-regular]
    elif case == (7, 5, 7):
        outer, inner, subtract, add, rhs_coefficient, rhs_constant = v
        coefficient, constant = outer*inner, add-outer*subtract
        simplified = _nums(o[1])
        contradiction = _nums(o[3])
        solution = _nums(o[0])[-1]
        truth = [coefficient != rhs_coefficient and (rhs_coefficient-coefficient)*solution == constant-rhs_constant,
                 simplified == [coefficient, constant], coefficient == rhs_coefficient and constant == rhs_constant,
                 coefficient == rhs_coefficient and constant != rhs_constant and contradiction == [constant, rhs_constant]]
    else:
        raise ValueError(qid)
    actual = [bool(x['correct']) for x in candidate['options']]
    assert actual == truth, (qid, actual, truth, s, o)


if __name__ == '__main__':
    import json
    from copy import deepcopy
    from pathlib import Path
    from engine import assemble, build_values

    selection = {6: {4: [3, 6], 5: [5, 6]}, 7: {4: [2, 9], 5: [2, 7]}}
    audit = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for entry in json.loads(audit.read_text(encoding='utf-8'))['entries']:
        if entry['source_number'] not in selection.get(entry['indicator'], {}).get(entry['level'], []):
            continue
        a = author(entry)
        original = {'hash': 'self-check', 'options': [
            {'id': str(j+1) if entry['format'] == 'KATEGORI' else chr(65+j)}
            for j in range(len(a.options))]}
        config = a.config(original)
        for k in range(31):
            candidate = assemble(config, build_values(config, lambda name, spec: k))
            check_math(a.qid, candidate)
            assert len({o['text'] for o in candidate['options']}) == len(candidate['options'])
            if k == 0:
                assert candidate['stem'] == a.s['stem']
                assert [o['text'] for o in candidate['options']] == a.s['options']
            bad = deepcopy(candidate)
            bad['options'][0]['correct'] = not bad['options'][0]['correct']
            try:
                check_math(a.qid, bad)
            except AssertionError:
                pass
            else:
                raise AssertionError('Oracle accepted an inverted truth value')
            count += 1
    assert count == 248
    print('248 variants: exact originals, distinct options, independent math, corrupted keys rejected')
