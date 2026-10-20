"""Numeric authoring and independent rendered mathematics for batch two, indicators 8–9."""
import re
from build_drill_1_5_level45_batch1 import Author

SELECTION = {(8,4,2),(8,4,3),(8,5,1),(8,5,7),(9,4,5),(9,4,6),(9,4,7),(9,5,9)}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    key = (a.i,a.l,a.n)
    def swap(old, expr, literal):
        token = a.var(expr, literal)
        a.stem = a.stem.replace(old, token)
        a.options = [t.replace(old, token) for t in a.options]
    if key == (8,4,2):
        swap('220', '220+2*k', '220')
        swap('130', '130+k', '130')
        swap('90', '90+k', '90')
        exp = 'Batas minimum = [[130+k]]. Tanda ≥ memuat batas: lingkaran penuh, panah kanan. Hanya C benar.'
    elif key == (8,4,3):
        a.stem = a.stem.replace('+14', '+' + a.var('14+5*k','14'))
        for j,t in enumerate(a.options):
            a.options[j] = t.replace('3', a.var('3+k','3'))
        exp = 'Batas maksimum = [[-3-k]]. Membagi dengan -5 membalik ≥ menjadi ≤. Hanya A benar.'
    elif key == (8,5,1):
        a.allnums({'600.000':'600000+16000*k','30':'30+k','37':'floor((600000+16000*k)/16000)', '28':'28+k','37,5':'(600000+16000*k)/16000'})
        exp = 'Maksimum paket = [[30+k]]. Biaya total = [[16000*(30+k)+120000]], sama dengan anggaran. Biaya tetap wajib dihitung; hanya B benar.'
    elif key == (8,5,7):
        swap('11','11+2*k','11')
        swap('-3','-3-k','-3')
        swap('-5','-5-k','-5')
        exp = 'Batas maksimum = [[-3-k]]. Tanda ≤ memakai lingkaran penuh. Nilai [[-5-k]] memenuhi pertidaksamaan. B dan D benar; A dan C salah.'
    elif key == (9,4,5):
        token = a.var('1+k','1')
        a.stem = a.stem.replace('2y-1','2y-'+token)
        a.options = [t.replace('2y-1','2y-'+token) for t in a.options]
        swap('27','27+7*k','27')
        exp = 'Solusi: x = [[5+k]], y = [[3+k]]. Substitusi langsung tersedia karena x terisolasi. Hanya C benar; efisiensi tidak mensyaratkan y positif.'
    elif key == (9,4,6):
        a.allnums({'19.000':'19000+500*k','18.000':'18000+600*k','5.000':'5000+100*k','2.000':'2000+100*k'})
        exp = 'Solusi: x = [[5000+100*k]], y = [[2000+100*k]]. Model sesuai pembelian; x lebih mahal daripada y. A, B, C benar; D salah.'
    elif key == (9,4,7):
        a.stem = a.stem.replace('2x-y=4','2x-y='+a.var('4+k','4')).replace('x+2y=12','x+2y='+a.var('12+3*k','12'))
        a.options[0] = a.options[0].replace('$4$', '$'+a.var('4+k','4')+'$')
        a.options[1] = a.options[1].replace('$2$', '$'+a.var('2+k','2')+'$')
        a.options[2] = a.options[2].replace('$4$', '$'+a.var('4+k','4')+'$')
        a.options[3] = a.options[3].replace('(4,4)', '('+a.var('4+k','4')+','+a.var('4+k','4')+')')
        exp = 'Solusi: x = [[4+k]], y = [[4+k]]. Determinan 5 tidak nol, sehingga pasangan tersebut titik potong tunggal. A, C, D benar; B salah.'
    elif key == (9,5,9):
        a.allnums({'27.000':'27000+500*k','16.000':'16000+300*k','7.000':'7000+100*k','5.000':'5000+100*k'})
        exp = 'Solusi: x = [[6000+100*k]], y = [[5000+100*k]]. Model sesuai pembelian. Pernyataan 1 dan 3 benar; 2 salah karena harga buku yang diklaim terlalu tinggi.'
    else:
        raise ValueError(key)
    a.exp = a.explanation(exp)
    return a


_NUM = r'-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?'
def numbers(text):
    return [float(v.replace('.','').replace(',','.')) for v in re.findall(_NUM,text)]


def check_math(qid, candidate):
    """Solve displayed equations, evaluate displayed claims and explanation independently."""
    key = tuple(map(int,qid.split('-')[1:]))
    s = candidate['stem']; t = [o['text'] for o in candidate['options']]
    exp = candidate['explanation']
    if key == (8,4,2):
        c,r = numbers(s); bound=(r+c)/2
        truth = [numbers(v)==[bound,bound] and '≥' in v and 'penuh' in v and 'kanan' in v for v in t]
        assert numbers(exp)[0] == bound and 'lingkaran penuh, panah kanan' in exp
    elif key == (8,4,3):
        c,a,b,d,r = map(float,re.search(r'\$(\d+)-(\d+)\(x\+(\d+)\)≥(\d+)x\+(\d+)\$',s).groups())
        bound=(c-a*b-r)/(a+d)
        truth = [numbers(v)==[bound] and '≤' in v for v in t]
        assert numbers(exp)[0] == bound and 'membalik ≥ menjadi ≤' in exp
    elif key == (8,5,1):
        budget,fixed,price,claim = numbers(s); maximum=int((budget-fixed)//price)
        v=numbers(t[1]); w=numbers(t[3])
        truth = [numbers(t[0])[0]==maximum,claim==maximum and v==[price,claim,fixed,price*claim+fixed,budget],numbers(t[2])[0]==maximum,w[0]/w[1]==w[2] and int(w[2])==w[3]==maximum]
        assert numbers(exp)[:2] == [maximum,price*maximum+fixed]
    elif key == (8,5,7):
        c,a,r=map(float,re.search(r'\$(\d+)-(\d+)x≥(\d+)\$',s).groups()); bound=(c-r)/a
        truth=[numbers(t[0])==[bound] and '≤' in t[0],numbers(t[1])==[bound] and '≤' in t[1],False,c-a*numbers(t[3])[0]>=r]
        assert numbers(exp)[:2] == [bound,numbers(t[3])[0]] and 'lingkaran penuh' in exp
    elif key == (9,4,5):
        b,c=map(float,re.search(r'x=2y-(\d+)\$\n\$3x\+4y=(\d+)',s).groups()); y=(c+3*b)/10; x=2*y-b
        truth=[False,False,numbers(t[2])==[2,-b] and 'terisolasi' in t[2],False]
        assert numbers(exp)[:2] == [x,y] and 'x terisolasi' in exp
    elif key in {(9,4,6),(9,5,9)}:
        vals=numbers(s)
        a,b,c,d,e,f=vals[:6]; det=a*e-b*d; x=(c*e-b*f)/det; y=(a*f-c*d)/det
        model=numbers(t[0]); expected=[a,b,c,d,e,f] if key==(9,4,6) else [a,b,c,e,f]
        truth=[model==expected,numbers(t[1])[-1]==x,numbers(t[2])[-1]==y]
        if key == (9,4,6): truth.append(x<y)
        assert numbers(exp)[:2] == [x,y] and 'Model' in exp
    elif key == (9,4,7):
        c,d=map(float,re.search(r'2x-y=(\d+)\$\n\$x\+2y=(\d+)',s).groups()); x=(2*c+d)/5; y=(2*d-c)/5
        pair=list(map(float,re.search(r'=\((\d+),(\d+)\)',t[3]).groups()))
        truth=[numbers(t[0])[-1]==x,numbers(t[1])[-1]==y,numbers(t[2])[-1]==y,pair==[x,y]]
        assert numbers(exp)[:2] == [x,y] and 'Determinan 5 tidak nol' in exp
    else:
        raise ValueError(qid)
    assert [bool(o['correct']) for o in candidate['options']] == truth, (qid,s,t,truth)
    return truth


if __name__ == '__main__':
    import json
    from pathlib import Path
    from engine import assemble, build_values
    from filters import validate_candidate
    path=Path(__file__).resolve().parents[2]/'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count=0
    for e in json.loads(path.read_text(encoding='utf8'))['entries']:
        if tuple(e[z] for z in ('indicator','level','source_number')) not in SELECTION: continue
        a=author(e)
        orig={'hash':'self-check','format':a.s['format'],'stem':a.s['stem'],'options':[{'id':str(j+1) if a.s['format']=='KATEGORI' else chr(65+j),'text':v,'correct':a.correct[j]} for j,v in enumerate(a.s['options'])]}
        cfg=a.config(orig); accepted=[]
        for k in range(31):
            candidate=assemble(cfg,build_values(cfg,lambda name,spec:k))
            check_math(a.qid,candidate)
            if k==0:
                assert candidate['stem']==a.s['stem']
                assert [o['text'] for o in candidate['options']]==a.s['options']
                assert [o['correct'] for o in candidate['options']]==a.correct
            elif not validate_candidate(candidate,orig,accepted): accepted.append(candidate)
            count+=1
        assert len(accepted)>=20,(a.qid,len(accepted))
    assert count==248
    print('248 variants: mathematics, explanations, exact originals; >=20 accepted per family')
