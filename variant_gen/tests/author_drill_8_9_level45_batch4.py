"""Batch four: rendered inequality and system witnesses, independent arithmetic checks."""
import math
import re
from build_drill_1_5_level45_batch1 import Author

SELECTION = {(8,4,4),(8,4,6),(8,4,10),(8,5,4),(8,5,6),(9,4,3),(9,4,4),(9,4,8),(9,5,3),(9,5,4),(9,5,10)}


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    # Preserve original LaTeX grouping at zero; variants use equivalent bare x.
    a.variables['x'] = dict(gen='derived', expr="'{x}' if k == 0 else 'x'")
    key = (a.i,a.l,a.n)
    def replace(old, expr, literal):
        token = a.var(expr,literal)
        a.stem = a.stem.replace(old,token)
        a.options = [t.replace(old,token) for t in a.options]
    if key == (8,4,4):
        a.allnums({'7':'7+2*k','10':'10+2*k','5':'5+k'})
        # The coefficient 5 must stay fixed; only the claimed boundary changes.
        a.stem = a.stem.replace(a.var('5+k','5')+'x','5x')
        a.options = [t.replace(a.var('5+k','5')+'x','5x') for t in a.options]
        exp = 'Batas atas ketat = [[-5-k]]. Langkah 1 dan 2 sah. Pembagian dengan -2 membalik > menjadi <; langkah 3 dan 4 salah. Hanya D benar.'
    elif key == (8,4,6):
        a.options[0] = a.nums(a.options[0], {'9':'9+2*k'})
        a.options[1] = a.nums(a.options[1], {'3':'3+4*k'})
        a.options[3] = a.nums(a.options[3], {'8':'8+2*k'})
        a.answer_value(0,'6+k',', contoh x yang memenuhi')
        exp = 'Batas A = [[7+k]], batas B = [[5-4*k]], batas D = [[6+k]]. A dan B linear satu variabel. C kuadratik. D linear satu variabel. A, B, D benar.'
    elif key == (8,4,10):
        a.allnums({'12':'12+2*k','3':'3+k'})
        exp = 'Solusi persamaan = [[3+k]]. Batas atas pertidaksamaan = [[3+k]]. Persamaan tetap memakai = saat dikalikan -1; pertidaksamaan membalik arah. Pernyataan 1 dan 2 benar; 3 salah.'
    elif key == (8,5,4):
        a.allnums({'350':'350+15*k','14':'14+k','15':'15','340':'340+15*k','355':'355+15*k','13':'13+k','23':'23+k','23,33':'round((350+15*k)/15,2)'})
        # Replace counts of fifteen, leaving the per-box weight fixed.
        a.options[1] = a.s['options'][1].replace('Maksimal 15','Maksimal '+a.var('15+k','15')).replace('(15)','('+a.var('15+k','15')+')')
        a.options[1] = a.nums(a.options[1], {'355':'355+15*k'})
        a.options[2] = a.options[2].replace('='+a.var('round((350+15*k)/15,2)','23,33'),a.var("'=' if k == 0 else 'â‰ˆ'",'=')+a.var('round((350+15*k)/15,2)','23,33'))
        exp = 'Maksimum kardus = [[14+k]]. Beban aman = [[340+15*k]] kg. Satu tambahan = [[355+15*k]] kg melebihi kapasitas [[350+15*k]] kg. Pembagian kapasitas tanpa petugas hanya pendekatan [[round((350+15*k)/15,2)]], bukan kapasitas kardus yang aman. Hanya A benar.'
    elif key == (8,5,6):
        a.stem = a.stem.replace('2x-7','2x-'+a.var('7+2*k','7')).replace('x-2','x-'+a.var('2+3*k','2')).replace('5-4x','5-4x').replace('>17','>'+a.var('17+4*k','17'))
        a.options[2] = a.nums(a.options[2],{'14':'14+3*k'})
        a.options[3] = a.nums(a.options[3],{'3':'3+k'})
        a.answer_value(0,'8+k',', batas atas ketat formulasi (i)')
        exp = 'Batas (i) = [[8+k]]. Batas (iii) = [[14+3*k]]. Batas (iv) = [[-3-k]]. (ii) mempunyai dua variabel. A, C, D benar.'
    elif key == (9,4,3):
        a.allnums({'12':'12+6*k','24':'24+12*k'})
        a.answer_value(0,'6+3*k',', x saat y=0')
        exp = 'Persamaan kedua tepat dua kali persamaan pertama, sehingga garis berimpit. Pada y nol, x = [[6+3*k]]. Tak hingga solusi; hanya A benar.'
    elif key == (9,4,4):
        a.stem = a.stem.replace('=5','= '+a.var('5+k','5')).replace('=10','='+a.var('10+3*k','10')).replace('=6','='+a.var('6+3*k','6')).replace('=3','='+a.var('3','3'))
        # No added whitespace in the original projection.
        a.stem = a.stem.replace('= ','=')
        a.answer_value(3,'3+k',', x sistem II')
        exp = 'Sistem I: konstanta kedua dikurangi tiga kali konstanta pertama = [[-5]], bukan nol; garis sejajar. Sistem II: x = [[3+k]], y = [[3+2*k]], determinan -3 tidak nol. Hanya D benar.'
    elif key == (9,4,8):
        a.stem = a.stem.replace('=5','='+a.var('5+k','5')).replace('=10','='+a.var('10+2*k','10')).replace('=4','='+a.var('4+k','4')).replace('=8','='+a.var('8+k','8'))
        a.answer_value(1,'5+k',', y saat x=0 pada pasangan I')
        a.answer_value(3,'4',', selisih konstanta pasangan II')
        exp = 'Pasangan I berimpit; pada x nol, y = [[5+k]]. Pasangan II sejajar dengan selisih konstanta [[4]]. Pasangan III memiliki determinan -5, sehingga solusi tunggal. B dan D benar.'
    elif key == (9,5,3):
        a.stem = a.stem.replace('=6','='+a.var('6+6*k','6')).replace('=12','='+a.var('12+12*k','12'),1)
        a.stem = a.stem.replace('=8','='+a.var('8+2*k','8')).replace('=12','='+a.var('12+2*k','12'))
        a.answer_value(3,'3+3*k',', x saat y=0 pada sistem I')
        exp = 'Sistem I berimpit karena persamaan kedua dua kali persamaan pertama. Pada y nol, x = [[3+3*k]]. Sistem II sejajar, selisih konstanta [[4]]. Hanya D benar.'
    elif key == (9,5,4):
        a.stem = a.stem.replace('3x-2','3x-'+a.var('2+k','2')).replace('=24','='+a.var('24+12*k','24'))
        a.answer_value(0,'2+k',', x solusi')
        exp = 'Substitusi langsung y yang sudah terisolasi memberi x = [[2+k]], y = [[4+2*k]]. Tidak perlu mengisolasi variabel terlebih dahulu. Hanya A benar.'
    elif key == (9,5,10):
        a.stem = a.stem.replace('x=4','x='+a.var('4+k','4')).replace('=11','='+a.var('11+3*k','11'))
        a.options[0] = a.options[0].replace('y=3','y='+a.var('3+k','3'))
        a.options[1] = a.options[1].replace('(4,3)','('+a.var('4+k','4')+','+a.var('3+k','3')+')')
        exp = 'Substitusi langsung memberi y = [[3+k]] dari konstanta kedua dikurangi dua kali x. Solusi tunggal x = [[4+k]], y = [[3+k]]. Satu langkah berarti satu substitusi beserta perhitungan; eliminasi tidak lebih cepat untuk bentuk ini. Pernyataan 1 dan 2 benar; 3 salah.'
    else:
        raise ValueError(key)
    a.exp = a.explanation(exp)
    return a


def numbers(text):
    return [float(v.replace('.','').replace(',','.')) for v in re.findall(r'-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?',text)]


def check_math(qid,c):
    key = tuple(map(int,qid.split('-')[1:]))
    s=c['stem']; t=[o['text'].split(' (hasil: ')[0] for o in c['options']]; exp=c['explanation']
    original_math = {
        (9,4,3): ['2x+3y=12','4x+6y=24'],
        (9,4,4): ['x-2y=5','3x-6y=10','x+y=6','2x-y=3'],
        (9,4,8): ['2x+y=5','4x+2y=10','3x-y=4','3x-y=8','x+2y=6','2x-y=2'],
        (9,5,3): ['2x-3y=6','4x-6y=12','x+2y=8','x+2y=12'],
        (9,5,4): ['y=3x-2','2x+5y=24'],
        (8,5,6): ['2x-7<9','3x+2y\u226412','\\frac{x-2}{3}\u22654','5-4x>17'],
    }
    original = re.findall(r'\$(.*?)\$',s) == original_math.get(key)
    if key == (8,4,6): original = numbers(t[0]) == [2,-5,9]
    def witness(j,value):
        full=c['options'][j]['text']
        assert (' (hasil: ' in full) != original, (qid, full, 'missing or unexpected witness')
        if ' (hasil: ' in full: assert math.isclose(numbers(full.split(' (hasil: ')[1])[0],value,abs_tol=1e-6),(qid,full,value)
    def first(*values):
        assert numbers(exp)[:len(values)] == list(values),(qid,exp,values)
    if key == (8,4,4):
        p,q,r,u=map(float,re.search(r'\$(\d+)x-(\d+)>(\d+)x\+(\d+)\$',s).groups()); bound=(q+u)/(p-r)
        assert numbers(t[3])[-2:]==[bound,p-r]
        # Validate all displayed student algebra, including fraction numerator.
        formula = re.findall(r'\$(.*?)\$',s)
        assert numbers(formula[1]) == [p,-r,u,q]
        assert numbers(formula[2]) == [p-r,q+u]
        assert numbers(formula[3]) == [q+u,p-r]
        assert numbers(formula[4]) == [bound]
        assert numbers(t[0]) == [1,p,r,u,-q]
        assert numbers(t[1]) == [2,p-r,-4]
        assert '<' in t[3] and 'dibalik' in t[3]
        first(bound); truth=[False,False,False,True]
    elif key == (8,4,6):
        a,b,d=numbers(t[0]); bound=(d-b)/a
        assert '^' in t[2] and '{2}' in t[2] and 'y' in t[3]
        witness(0,bound-1)
        bn=numbers(t[1]); dn=numbers(t[3]); first(bound,bn[1]*bn[2]-bn[0],(dn[-1]-dn[0]*dn[1])/(dn[0]-dn[2]))
        truth=[True,True,False,True]
    elif key == (8,4,10):
        a,b,d=map(float,re.search(r'\$(\d+)x\+(\d+)=(\d+)\$',s).groups()); bound=(d-b)/a
        assert numbers(t[0])[-1]==numbers(t[1])[-1]==bound
        first(bound,bound);truth=[True,True,False]
    elif key == (8,5,4):
        cap,staff,weight=numbers(s); maximum=math.floor((cap-staff)/weight)
        av=numbers(t[0]); bv=numbers(t[1]); cv=numbers(t[2]); dv=numbers(t[3]); truth=[av[0]==maximum and weight*av[0]+staff<=cap,bv[0]==maximum and weight*bv[0]+staff<=cap,cv[0]==maximum,dv[0]==maximum]
        assert av==[maximum,weight,maximum,staff,weight*maximum+staff,cap]
        assert bv==[maximum+1,weight,maximum+1,staff,weight*(maximum+1)+staff], (s,t,bv)
        assert cv[:3]==[math.floor(cap/weight),cap,weight] and abs(cv[3]-cap/weight)<0.0051
        if 'â‰ˆ' in t[2]: assert 'â‰ˆ' in t[2]
        first(maximum,weight*maximum+staff,weight*(maximum+1)+staff,cap)
    elif key == (8,5,6):
        b=float(re.search(r'2x-(\d+)<9',s)[1]); d=float(re.search(r'frac\{x-(\d+)',s)[1]); r=float(re.search(r'4x>(\d+)',s)[1]); bounds=((b+9)/2,d+12,(5-r)/4)
        assert numbers(t[2])[-1]==bounds[1] and numbers(t[3])[-1]==bounds[2]
        assert '2y' in s; witness(0,bounds[0]);first(*bounds);truth=[True,False,True,True]
    elif key == (9,4,3):
        a,b=map(float,re.findall(r'=(\d+)',s)); assert b==2*a
        witness(0,a/2);first(a/2);truth=[True,False,False,False]
    elif key == (9,4,4):
        a,b,d,e=map(float,re.findall(r'=(\d+)',s)); x=(d+e)/3;y=d-x
        assert b!=3*a;witness(3,x);first(b-3*a,x,y);truth=[False,False,False,True]
    elif key == (9,4,8):
        a,b,d,e,f,g=map(float,re.findall(r'=(\d+)',s));assert b==2*a and d!=e
        witness(1,a);witness(3,e-d);first(a,e-d);truth=[False,True,False,True]
    elif key == (9,5,3):
        a,b,d,e=map(float,re.findall(r'=(\d+)',s));assert b==2*a and d!=e
        witness(3,a/2);first(a/2,e-d);truth=[False,False,False,True]
    elif key == (9,5,4):
        b=float(re.search(r'y=3x-(\d+)',s)[1]);r=float(re.search(r'5y=(\d+)',s)[1]);x=(r+5*b)/17;y=3*x-b
        assert 'terisolasi' in t[0];witness(0,x);first(x,y);truth=[True,False,False,False]
    elif key == (9,5,10):
        x,r=map(float,re.findall(r'=(\d+)',s));y=r-2*x
        assert numbers(t[0])[:2]==[y,1]
        pair=re.search(r'\$\((\d+),(\d+)\)',t[1]);assert list(map(float,pair.groups()))==[x,y]
        first(y,x,y);truth=[True,True,False]
    else: raise ValueError(qid)
    assert [bool(o['correct']) for o in c['options']]==truth,(qid,truth)
    return truth


if __name__ == '__main__':
    import json
    from pathlib import Path
    from engine import assemble,build_values
    from filters import validate_candidate
    path=Path(__file__).resolve().parents[2]/'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    count=0
    for e in json.loads(path.read_text(encoding='utf8'))['entries']:
        if tuple(e[z] for z in ('indicator','level','source_number')) not in SELECTION: continue
        a=author(e)
        orig={'hash':'self-check','format':a.s['format'],'stem':a.s['stem'],'options':[{'id':str(j+1) if a.s['format']=='KATEGORI' else chr(65+j),'text':v,'correct':a.correct[j]} for j,v in enumerate(a.s['options'])]}
        cfg=a.config(orig);accepted=[]
        for k in range(31):
            c=assemble(cfg,build_values(cfg,lambda name,spec:k));check_math(a.qid,c)
            if k==0:
                assert c['stem']==a.s['stem'],(a.qid,c['stem'],a.s['stem'])
                assert [o['text'] for o in c['options']]==a.s['options']
                assert [o['correct'] for o in c['options']]==a.correct
            elif not validate_candidate(c,orig,accepted): accepted.append(c)
            count+=1
        assert len(accepted)>=20,(a.qid,len(accepted))
    assert count==341
    print('341 variants checked; exact originals; >=20 accepted per family')

