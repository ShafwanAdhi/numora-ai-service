"""Six audited families, rendered-text oracles, exact normalized originals."""
import re
from fractions import Fraction
from build_drill_1_5_level45_batch1 import Author

SELECTION = {6: {4: [9], 5: [7, 9]}, 7: {4: [6, 10], 5: [10]}}


def prepare(e):
    e = dict(e)
    s = dict(e['source_projection'], format=e['format'])
    if e['format'] == 'KATEGORI':
        s['stem'] = re.sub(r'^(?:\([a-z]\) (?:BENAR|SALAH)\n)+', '', s['stem'])
    e['source_projection'] = s
    return e


def author(e):
    a = Author(prepare(e))
    case = (a.i, a.l, a.n)
    if case == (6, 4, 9):
        a.allnums({'200':'200*(k+1)', '800':'800*(k+1)', '300':'300*(k+1)', '900':'900*(k+1)', '2':'2*(k+1)', '500':'500*(k+1)'})
        a.answer_value(0, '1000*(k+1)', ' ml total Alpha')
        a.exp = a.explanation('Total Alpha = [[1000*(k+1)]] ml; total Beta = [[1200*(k+1)]] ml. Konsentrasi Alpha = 1/5; Beta = 1/4. Sirup untuk target = [[500*(k+1)]] ml. Alpha kurang manis; benar, salah, benar.')
    elif case == (6, 5, 7):
        a.allnums({'150.000':'150000*(k+1)', '250.000':'250000*(k+1)', '450.000':'450000*(k+1)'})
        a.exp = a.explanation('Tarif Hemat = [[15000*(k+1)]] rupiah per meter persegi. Tarif Cepat tepat = [[250000*(k+1)]]/15 rupiah per meter persegi, lebih mahal. Kecepatan Cepat = 7,5 meter persegi per jam. Biaya target Hemat = [[450000*(k+1)]]. Waktu target Cepat = 6 jam. B dan C benar.')
    elif case == (6, 5, 9):
        a.allnums({'60':'60*(k+1)', '90':'90*(k+1)', '5':'5*(k+1)'})
        a.exp = a.explanation('Debit satu kran = [[5*(k+1)]]. Waktu Kolam Y = 4,5 jam; waktu Kolam X dengan dua kran = 6 jam. Benar, salah, benar.')
    elif case == (7, 4, 6):
        a.options[0] = a.nums(a.options[0], {'9':'9+k'})
        a.options[1] = a.nums(a.options[1], {'5':'5+4*k'})
        a.options[2] = a.nums(a.options[2], {'5':'5+k'})
        a.exp = a.explanation('Solusi A = [[10+k]]; solusi B = [[0.5+k]]; solusi C = [[7+2*k]]. Ketiganya berderajat satu dengan satu variabel setelah disederhanakan. D memiliki dua variabel.')
    elif case in ((7, 4, 10), (7, 5, 10)):
        if a.l == 4:
            a.stem = a.stem.replace('x+3', 'x+'+a.var('3+k','3')).replace('2x+6', '2x+'+a.var('6+2*k','6'))
            a.stem = a.stem.replace('3x+5','3x+'+a.var('5+k','5')).replace('3x-2','3x-'+a.var('2+k','2'))
            a.stem = a.stem.replace('4x-8','4x-'+a.var('8+4*k','8'))
            a.options[2] = a.nums(a.options[2], {'2':'2+k'})
            identity, left, right, solution = '6+2*k','5+k','2+k','2+k'
        else:
            a.stem = a.stem.replace('x-2','x-'+a.var('2+k','2')).replace('5x-10','5x-'+a.var('10+5*k','10'))
            a.stem = a.stem.replace('2x+7','2x+'+a.var('7+k','7')).replace('2x-3','2x-'+a.var('3+k','3'))
            a.stem = a.stem.replace('3x-12','3x-'+a.var('12+3*k','12'))
            a.options[1] = a.nums(a.options[1], {'7':'7+k','3':'3+k'})
            identity, left, right, solution = '10+5*k','7+k','3+k','4+k'
        a.answer_value(0, identity, ' konstanta mutlak kedua ruas')
        a.answer_value(1, '('+left+')+('+right+')', ' selisih konstanta')
        a.exp = a.explanation('Konstanta mutlak identitas = [['+identity+']]. Selisih konstanta kontradiksi = [[('+left+')+('+right+')]]. Solusi tunggal persamaan terakhir = [['+solution+']]. Identitas berlaku untuk semua real; kontradiksi tanpa solusi; persamaan terakhir tepat satu solusi. Benar, benar, salah.')
    else:
        raise ValueError(case)
    # Original mathematical braces are literal source text, plain letters in variants.
    for name in ('m', 'x', 'a'):
        if any('{'+name+'}' in t for t in [a.stem,*a.options]):
            a.variables[name] = dict(gen='derived', expr=repr('{'+name+'}')+" if k == 0 else "+repr(name))
    return a


def _nums(text):
    return [Fraction(t.replace('.', '').replace(',', '.')) for t in re.findall(r'\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?', text)]


def check_math(qid, c):
    case = tuple(map(int,qid.split('-')[1:]))
    s,o = c['stem'],[t['text'] for t in c['options']]
    v = _nums(s)
    base = [t.split(' (hasil: ')[0] for t in o]
    if case == (6,4,9):
        ap,aw,bp,bw = v
        rn,rd = _nums(base[0]); liters,syrup = _nums(base[2])
        truth = [ap/(ap+aw)==rn/rd,ap/(ap+aw)>bp/(bp+bw),liters*1000*bp/(bp+bw)==syrup]
        expected = [ap+aw,bp+bw,1,5,1,4,syrup]
        witness = {0:ap+aw}
    elif case == (6,5,7):
        ah,power,at,ac,ba,power2,bt,bc = v
        assert power == power2 == 2
        speed = _nums(base[1])[0]
        target,_,cost = _nums(base[2]); target2,_,hours = _nums(base[3])
        truth = [ac/ah>bc/ba,ba/bt==speed,target*ac/ah==cost,target2*bt/ba==hours]
        expected = [ac/ah,bc,ba,speed,cost,target2*bt/ba]
        witness = {}
    elif case == (6,5,9):
        cap,power,n,t,cap2,power2,n2 = v
        one,flow,power3 = _nums(base[0]); limit = _nums(base[1])[0]; taps,hours = _nums(base[2])
        rate = cap/n/t
        assert power==power2==power3==3
        truth = [one==1 and flow==rate,cap2/n2/rate<limit,cap/taps/rate==hours]
        expected = [rate,cap2/n2/rate,cap/taps/rate]
        witness = {}
    elif case == (7,4,6):
        outer,inner,plus,rcoef,rhs = _nums(base[0])
        p1,bcoef,bconst,p2,rconst = _nums(base[1])
        coef,const,den,right = _nums(base[2]); dc,dy,dr = _nums(base[3])
        truth = [outer!=rcoef,p1==p2 and bcoef!=0,coef!=0 and den!=0,False]
        assert dc and dy
        expected = [(rhs+outer*inner-plus)/(outer-rcoef),(bconst-rconst)/bcoef,(den*right-const)/coef]
        witness = {}
    elif case in ((7,4,10),(7,5,10)):
        outer,inner,coef,constant,lc,left,rc,right,third,sub,zero = v
        signed = inner if '(x+' in s else -inner
        identity = outer==coef and outer*signed==(constant if '(x+' in s else -constant)
        contradiction = lc==rc and left!=-right
        solution = sub/third
        if case[1]==4:
            pos,neg = _nums(base[2]); thirdtruth = pos == -neg == solution and pos == -pos
        else:
            claimleft,claimright = _nums(base[1]); assert [claimleft,claimright]==[left,right]
            thirdtruth = third==0 and sub!=0
        truth = [identity,contradiction,thirdtruth]
        expected = [abs(outer*signed),left+right,solution]
        witness = {0:expected[0],1:expected[1]}
    else:
        raise ValueError(qid)
    assert [bool(t['correct']) for t in c['options']]==truth,(qid,truth,s,o)
    for j,t in enumerate(o):
        if j in witness and ((case == (6,4,9) and ap != 200) or (case == (7,4,10) and constant != 6) or (case == (7,5,10) and constant != 10)):
            assert ' (hasil: ' in t,(qid,j,'missing mathematical witness')
        if ' (hasil: ' in t:
            assert _nums(t.split(' (hasil: ')[1]) == [witness[j]],(qid,t,witness)
    exp = re.split(r'\n\n(?:Jawaban:|Penilaian pernyataan:)',c['explanation'],maxsplit=1)[0]
    assert _nums(exp)==expected,(qid,_nums(exp),expected)


if __name__ == '__main__':
    import json
    from copy import deepcopy
    from pathlib import Path
    from engine import assemble,build_values
    from filters import validate_candidate
    audit = Path(__file__).resolve().parents[2]/'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count = 0
    for e in json.loads(audit.read_text(encoding='utf8'))['entries']:
        if e['source_number'] not in SELECTION.get(e['indicator'],{}).get(e['level'],[]): continue
        a = author(e)
        orig = dict(hash='selfcheck',format=e['format'],stem=a.s['stem'],options=[dict(id=chr(65+j),text=t,correct=a.correct[j]) for j,t in enumerate(a.s['options'])])
        cfg = a.config(orig)
        accepted=[]
        for k in range(31):
            c=assemble(cfg,build_values(cfg,lambda name,spec:k))
            check_math(a.qid,c)
            if k==0: assert c['stem']==orig['stem'] and c['options']==orig['options'],a.qid
            if not validate_candidate(c,orig,accepted): accepted.append(c)
            for field in ('key','explanation'):
                bad=deepcopy(c)
                if field=='key': bad['options'][0]['correct']=not bad['options'][0]['correct']
                else: bad['explanation']+=' 999999'
                try: check_math(a.qid,bad)
                except AssertionError: pass
                else: raise AssertionError('Oracle accepted corrupted '+field)
            count+=1
        assert len(accepted)>=20,(a.qid,len(accepted))
    assert count==186,count
    print('186 variants verified; exact normalized originals; >=20 accepted per family; corrupted keys/explanations rejected')
