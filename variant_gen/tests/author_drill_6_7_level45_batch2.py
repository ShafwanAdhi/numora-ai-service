"""Eight numeric families; independent rendered-text mathematical oracle."""
import re
from fractions import Fraction
from build_drill_1_5_level45_batch1 import Author

SELECTION = {6: {4: [5, 7]}, 7: {4: [1, 5, 7, 8], 5: [1, 4]}}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved', e['source_projection']), format=e['format'])
    a = Author(e)
    case = (a.i, a.l, a.n)
    if case == (6, 4, 5):
        a.allnums({'180':'180+12*k', '15':'15+k', '45':'45+3*k', '30':'30+2*k'})
        a.stem = a.stem.replace('07.15', '07.' + a.var('15+k', '15'))
        minute = '(75+5*k)%60'
        clock = (a.var('7+(75+5*k)//60', '08') + '.' +
                 a.var("'0' if (75+5*k)%60 < 10 else ''", '') + a.var(minute, '15'))
        a.options[1] = a.options[1].replace('08.15', clock)
        a.exp = a.explanation('Waktu menyusul setelah keberangkatan Y = [[60+4*k]] menit; jarak penyusulan = [[75+5*k]] km. Waktu tiba X = [[3+k/5]] jam; waktu perjalanan Y = [[(180+12*k)/75]] jam. Sisa jarak X saat Y tiba = [[21+7*k/5]] km. Hanya B benar.')
    elif case == (6, 4, 7):
        a.allnums({n: f'{v}*(k+1)' for n, v in [('1.500',1500),('1.200',1200),('200',200),('350',350),('2.600',2600)]})
        a.exp = a.explanation('Laju satu mesin P = [[125*(k+1)]] brosur/jam; Q = [[200*(k+1)]] brosur/jam. Laju gabungan satu P dan satu Q = [[325*(k+1)]]. Hasil dua P dan dua Q selama empat jam = [[2600*(k+1)]]. B dan D benar.')
    elif case == (7, 4, 1):
        a.allnums({'120.000':'120000', '3.000':'3000', '345.000':'345000+3000*k', '75':'75+k', '155':'155+k', '115':'115+k'})
        a.exp = a.explanation('Biaya tetap ditambah biaya per buku dikali jumlah buku. Banyak buku = [[75+k]]. Model dan jumlah pada C benar; A menukar koefisien, B salah tanda, D salah jumlah.')
    elif case == (7, 4, 5):
        a.allnums({'3':'3+k','6':'6+2*k','12':'12+4*k'})
        a.exp = a.explanation('Koefisien setelah penyederhanaan kedua formulasi = [[2]]; konstanta keduanya = [[12+4*k]]. Identik untuk setiap jumlah buku. Hanya D benar.')
    elif case == (7, 4, 7):
        a.allnums({'12':'12+3*k','7':'7+3*k'})
        a.stem = a.stem.replace('2x+4', '2x+' + a.var('4+k', '4'))
        # Equal x coefficients remain fixed; constants stay five apart.
        a.exp = a.explanation('Koefisien ruas kiri = [[4]]; konstanta kiri = [[12+3*k]]; koefisien kanan = [[4]]; konstanta kanan = [[7+3*k]]. Koefisien sama, konstanta berbeda: tidak ada solusi. B dan D benar.')
    elif case == (7, 4, 8):
        a.allnums({n:f'{v}*(k+1)' for n,v in [('30.000',30000),('10.000',10000),('20.000',20000),('70.000',70000)]})
        a.exp = a.explanation('Nilai x = [[20000*(k+1)]]. Tabungan Rani = [[70000*(k+1)]]; Dion = [[70000*(k+1)]]; Sinta = [[70000*(k+1)]]. Ketiganya sama. A, C, D benar.')
    elif case == (7, 5, 1):
        a.allnums({n:f'{v}*(k+1)' for n,v in [('22.000',22000),('2.000',2000),('6.000',6000),('24.000',24000),('1.000',1000)]})
        a.exp = a.explanation('Harga buku Skema A = [[6000*(k+1)]] rupiah; harga buku Skema B = [[6000*(k+1)]] rupiah. Harga sama, selisih nol. Hanya B benar.')
    elif case == (7, 5, 4):
        a.allnums({n:f'{v}*(k+1)' for n,v in [('15.000',15000),('20.000',20000),('18.000',18000),('16.000',16000),('200.000',200000),('180.000',180000),('160.000',160000),('120.000',120000)]})
        a.exp = a.explanation('Jumlah panitia = [[12]]. Total uang = [[200000*(k+1)]] rupiah. Sisa dan kekurangan menghasilkan total yang sama. Hanya A benar.')
    else:
        raise ValueError(case)
    return a


def _nums(text):
    return [Fraction(x.replace('.', '').replace(',', '.')) for x in re.findall(r'\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?', text)]


def check_math(qid, candidate):
    case = tuple(map(int, qid.split('-')[1:]))
    s, o = candidate['stem'], [x['text'] for x in candidate['options']]
    v = _nums(s)
    if case == (6, 4, 5):
        distance, hour, minute, vx, lag, yh, ym, vy = v
        catch = vx*lag/60/(vy-vx)
        arrival_x, arrival_y = distance/vx, lag/60+distance/vy
        catch_hour, catch_minute = _nums(o[1])
        truth = [_nums(o[0])[0] == vy*catch,
                 catch_hour*60+catch_minute == (hour*60+minute+lag+catch*60)%1440,
                 arrival_x < arrival_y, _nums(o[3])[0] == distance-vx*arrival_y]
        expected = [catch*60, vy*catch, arrival_x, distance/vy, distance-vx*arrival_y]
        assert yh*60+ym == (hour*60+minute+lag)%1440
    elif case == (6, 4, 7):
        p, q, output_p, hours_p, output_q, hours_q = v
        rp, rq = output_p/(p*hours_p), output_q/(q*hours_q)
        onep, oneq = _nums(o[0])
        qcount, claimed_q = _nums(o[1])
        cp,cq,total,hours = _nums(o[2])
        target,deadline,np,nq = _nums(o[3])
        truth = [onep*rp > oneq*rq, qcount*rq == claimed_q, (cp*rp+cq*rq)*hours == total, (np*rp+nq*rq)*deadline == target]
        expected = [rp,rq,rp+rq,(2*rp+2*rq)*4]
    elif case == (7, 4, 1):
        fixed, rate, total = v
        answer = (total-fixed)/rate
        truth = []
        for t in o:
            coefficient,constant,rhs,count = _nums(t)
            sign = -1 if 'x-' in t else 1
            truth.append(coefficient == rate and sign*constant == fixed and rhs == total and count == answer)
        expected = [answer]
    elif case == (7, 4, 5):
        outer,inner,subtract,bcoef,bconst = v
        coef,constant = outer-subtract,outer*inner
        xclaim = _nums(o[2])[0]
        dcoef,dconst = _nums(o[3])
        truth = [coef > bcoef or (coef == bcoef and constant > bcoef*bconst), constant != bcoef*bconst,
                 coef != bcoef and coef*xclaim+constant == bcoef*(xclaim+bconst), coef == bcoef == dcoef and constant == bcoef*bconst == dconst]
        expected = [coef,constant]
    elif case == (7, 4, 7):
        outer,inner,add,subtract,rcoef,rconst = v
        coef,constant = outer*inner-subtract,outer*add
        truth = [coef != rcoef and (coef-rcoef)*_nums(o[0])[0] == rconst-constant,
                 _nums(o[1]) == [coef,constant], coef == rcoef and constant == rconst,
                 coef == rcoef and constant != rconst and _nums(o[3]) == [constant,rconst]]
        expected = [coef,constant,rcoef,rconst]
    elif case == (7, 4, 8):
        rc,ra,dc,da,sc,sa = v
        x = (ra+da)/(dc-rc)
        r,d,t = rc*x+ra,dc*x-da,sc*x+sa
        truth = [_nums(o[0])[0] == x, r<t, _nums(o[2])[0] == r, d == t == _nums(o[3])[0]]
        expected = [x,r,d,t]
    elif case == (7, 5, 1):
        books,pencils,total,one,price,bbooks,discount,payment,last = v
        pa,pb = (total-pencils*price)/books,(payment+discount)/bbooks
        truth = [pb-pa == _nums(o[0])[0] and pa<pb, pa == pb == _nums(o[1])[0], pa-pb == _nums(o[2])[0] and pb<pa, pb>pa]
        expected = [pa,pb]
    elif case == (7, 5, 4):
        low,left,high,short = v
        count = (left+short)/(high-low)
        amount = low*count+left
        truth = [_nums(t)[0] == amount for t in o]
        expected = [count,amount]
    else:
        raise ValueError(qid)
    assert [bool(x['correct']) for x in candidate['options']] == truth, (qid, truth, s, o)
    # API records append answer summaries; only the authored rationale is numeric evidence.
    explanation = re.split(r'\n\n(?:Jawaban:|Penilaian pernyataan:)', candidate['explanation'], maxsplit=1)[0]
    assert _nums(explanation) == expected, (qid, _nums(explanation), expected)


if __name__ == '__main__':
    import json
    from copy import deepcopy
    from pathlib import Path
    from engine import assemble, build_values
    from filters import validate_candidate
    audit = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for e in json.loads(audit.read_text(encoding='utf-8'))['entries']:
        if e['source_number'] not in SELECTION.get(e['indicator'],{}).get(e['level'],[]):
            continue
        a = author(e)
        orig = dict(hash='self-check',format=e['format'],stem=a.s['stem'],options=[dict(id=chr(65+j),text=t,correct=a.correct[j]) for j,t in enumerate(a.s['options'])])
        cfg = a.config(orig)
        accepted = []
        for k in range(31):
            c = assemble(cfg,build_values(cfg,lambda name,spec:k))
            check_math(a.qid,c)
            assert len({x['text'] for x in c['options']}) == len(c['options'])
            if k == 0:
                assert c['stem'] == orig['stem']
                assert c['options'] == orig['options']
            if not validate_candidate(c,orig,accepted):
                accepted.append(c)
            for field in ['key','explanation']:
                bad = deepcopy(c)
                if field == 'key':
                    bad['options'][0]['correct'] = not bad['options'][0]['correct']
                else:
                    bad['explanation'] += ' 999999'
                try:
                    check_math(a.qid,bad)
                except AssertionError:
                    pass
                else:
                    raise AssertionError('Oracle accepted corrupted '+field)
            count += 1
        assert len(accepted) >= 20, (a.qid,len(accepted))
    assert count == 248
    print('248 variants verified; exact originals; >=20 accepted per family; corrupted keys/explanations rejected')
