"""Seven source-preserving numerical families after determinate key corrections."""
import re
from fractions import Fraction
from build_drill_1_5_level45_batch1 import Author
from author_drill_6_7_level45_batch4 import _nums

def author(e):
    a=Author(e); case=(a.i,a.l,a.n)
    if case==(6,4,1):
        a.stem=a.stem.replace('3jam30menit',a.var('3+k','3')+'jam30menit')
        a.options=[a.nums(t,{str(v):f'{v}+20*k'}) for t,v in zip(a.options,(30,40,50,70))]
        a.exp=a.explanation('Waktu berangkat = [[210+60*k]] menit. Jarak = [[210+60*k]] km. Waktu pulang = [[(210+60*k)*4/3]] menit. Selisih = [[70+20*k]] menit. D benar.')
    elif case==(6,5,1):
        a.stem=a.nums(a.stem,{'14':'14+5*k'})
        a.options=[a.nums(t,{str(v):f'{v}+6*k'}) for t,v in zip(a.options,(16,18,19,21))]
        a.exp=a.explanation('Sisa awal = [[60*(10+5*k)]] jatah keluarga-hari. Setelah tambahan 50% = [[90*(10+5*k)]]. Penerima menjadi 75 keluarga. Sisa waktu = [[12+6*k]] hari; total = [[16+6*k]] hari. A benar.')
    elif case==(6,5,3):
        a.allnums({'6':'6*(k+1)','4':'4*(k+1)','1,5':'1.5*(k+1)',
                   '2,5':'2.5*(k+1)','3':'3*(k+1)','3,5':'3.5*(k+1)'})
        a.exp=a.explanation('Laju gabungan = 1/[[6*(k+1)]] + 1/[[4*(k+1)]]. Pekerjaan bersama selesai 5/8 bagian; tersisa 3/8. Truk B memerlukan [[1.5*(k+1)]] jam lagi; total [[3*(k+1)]] jam. B benar.')
    elif case==(7,4,3):
        a.stem=a.nums(a.stem,{'44':'44+8*k'})
        for j,v in enumerate((96,105,112,117)):
            a.options[j]=a.nums(a.options[j],{str(v):f'{v}+38*k+3*k*k'})
        a.exp=a.explanation('Keliling memberi 4x-2 = [[22+4*k]], sehingga x = [[6+k]]. Panjang [[14+3*k]] cm, lebar [[8+k]] cm. Luas = [[(14+3*k)*(8+k)]] cm kuadrat. C benar.')
    elif case==(7,5,5):
        a.stem=a.nums(a.stem,{'36':'36+8*k'})
        a.options[0]=a.nums(a.options[0],{'10':'10+3*k','8':'8+k'})
        a.options[1]=a.nums(a.options[1],{'96':'96+34*k+3*k*k'})
        a.options[2]=a.nums(a.options[2],{'13':'13+3*k','5':'5+k'})
        a.exp=a.explanation('Keliling memberi 4x+2 = [[18+4*k]], sehingga x = [[4+k]]. Panjang [[10+3*k]] meter, lebar [[8+k]] meter. Luas [[(10+3*k)*(8+k)]] meter kuadrat. A benar; panjang berbeda dari lebar.')
    elif case==(9,5,2):
        a.allnums({v:f'{v.replace(".","")}*(k+1)' for v in ('22.000','25.000','18.000','2.000','3.000','1.000')})
        a.exp=a.explanation('SPLDV memberi harga lemper [[2500*(k+1)]] rupiah dan lapis [[4000*(k+1)]] rupiah. Harga pesanan = [[17000*(k+1)]]. Uang [[18000*(k+1)]] cukup; kembalian [[1000*(k+1)]]. D benar.')
    elif case==(10,4,7):
        a.stem=a.stem.replace('3x',a.var('3+k','3')+'x')
        a.options=[a.nums(t,{'3':'3+2*k'}) for t in a.options]
        a.exp=a.explanation('Distribusi menghasilkan [[6+2*k]]x-4y-3x+12y = [[3+2*k]]x+8y. Suku x adalah [[3+2*k]]x, suku y adalah +8y. A, B, D benar; C salah tanda/koefisien y.')
    else:
        raise ValueError(case)
    if any('{m}' in t for t in a.options):
        a.variables['m']=dict(gen='derived',expr="'{m}' if k == 0 else 'm'")
    return a

def check_math(qid,c):
    case=tuple(map(int,qid.split('-')[1:])); s=c['stem']; texts=[o['text'] for o in c['options']]
    v=_nums(s); o=[_nums(t) for t in texts]
    if case==(6,4,1):
        speed,hours,minutes,back=v
        target=(hours*60+minutes)*(speed/back-1)
        truths=[ns[0]==target for ns in o]
        expected=[target]
    elif case==(6,5,1):
        families,days,elapsed,percent,added=v
        target=elapsed+families*(days-elapsed)*(1+percent/100)/(families+added)
        truths=[ns[0]==target for ns in o]
        expected=[target]
    elif case==(6,5,3):
        ta,tb,joint=v
        target=joint+(1-joint*(1/ta+1/tb))*tb
        truths=[ns[0]==target for ns in o]
        expected=[target]
    elif case in ((7,4,3),(7,5,5)):
        from author_drill_10_level45_batch4 import _poly
        from sympy import Symbol,solve
        math=re.findall(r'\$([^$]+)\$',s)
        p,w,perimeter=(_poly(t.replace('cm','')) for t in math)
        x=Symbol('x'); solution=solve(2*(p+w)-perimeter,x)[0]
        p,w=p.subs(x,solution),w.subs(x,solution)
        if case==(7,4,3): truths=[ns[0]==p*w for ns in o]
        else: truths=[o[0]==[p,w],o[1][0]==p*w,o[2]==[p,w],p==w]
        expected=[p,w,p*w,solution]
    elif case==(9,5,2):
        # Read the two rendered bundles and solve without using author parameters.
        label1,a,b,total1,label2,d,e,total2,budget,f,g=v
        assert (label1,label2)==(1,2)
        determinant=a*e-b*d
        x=(total1*e-b*total2)/determinant; y=(a*total2-total1*d)/determinant
        change=budget-f*x-g*y
        truths=[change==-o[0][0],change==0,change==o[2][0],change==o[3][0]]
        expected=[x,y,budget-change,change]
    elif case==(10,4,7):
        from author_drill_10_level45_batch4 import _poly
        from sympy import Symbol
        x,y=Symbol('x'),Symbol('y')
        target=_poly(re.findall(r'\$([^$]+)\$',s)[0]).expand()
        claims=[_poly(re.findall(r'\$([^$]+)\$',t)[-1]) for t in texts]
        truths=[claims[0]==target.coeff(x)*x,claims[1]==target.coeff(y)*y,claims[2]==target,claims[3]==target]
        expected=[target.coeff(x),target.coeff(y)]
    else: raise AssertionError(case)
    assert list(map(bool,truths))==[bool(t['correct']) for t in c['options']],(qid,v,o,truths)
    explanation_numbers=_nums(c['explanation'].split('\n\n')[0])
    assert all(n in explanation_numbers for n in expected),(qid,expected,explanation_numbers)
