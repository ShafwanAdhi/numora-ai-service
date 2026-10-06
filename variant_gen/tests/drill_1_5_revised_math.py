"""Independent checks derived only from rendered question text, options and explanation."""
import math
import re
from datetime import date,timedelta
from fractions import Fraction as F
from drill_1_2_math import calc,compare,number,numbers
from drill_indicator3_math import rounded,root

SUPPORTED = {
    'pg-1-1-5','pg-1-2-3','mcma-1-2-6','pg-1-3-1','pg-1-3-5','mcma-1-3-6',
    'pg-2-1-1','pg-2-1-2','pg-2-1-3','pg-2-1-5','pg-2-2-1','pg-2-2-2',
    'pg-2-2-4','mcma-2-2-6','mcma-2-2-7','mcma-2-3-6',
    'pg-3-1-2','pg-3-1-3','pg-3-1-5','pg-3-2-2','pg-3-2-3','pg-3-2-4',
    'mcma-3-2-7','mcma-3-2-8','kategori-3-2-9','pg-3-3-3',
    'pg-4-1-1','mcma-4-1-8','kategori-4-1-9','kategori-4-1-10',
    'pg-4-2-2','pg-4-2-5','mcma-4-2-8','kategori-4-2-9','kategori-4-2-10',
    'pg-4-3-1','mcma-4-3-8','kategori-4-3-9','kategori-4-3-10','pg-5-1-5',
}


def plain(text):
    text=re.sub(r'\\+',lambda m:'\\',text)
    text=re.sub(r'\\text\{[^}]*\}', '',text).replace(r'^\circ','').replace('$','')
    text=re.sub(r'(-?\d+)\\frac\{(\d+)\}\{(\d+)\}',r'\1 \2/\3',text)
    text=re.sub(r'\\frac\{(\d+)\}\{(\d+)\}',r'(\1)/(\2)',text)
    text=re.sub(r'\\sqrt\{(\d+)\}',r'sqrt(\1)',text)
    text=re.sub(r'(\d+)\((\d+)\)/\((\d+)\)',r'\1 \2/\3',text)
    return text


def expression(text):
    return calc(plain(text).strip().removesuffix('m'))


def checkpoint(c,expected):
    marker='Hasil pemeriksaan: '
    assert marker in c['explanation'],c['explanation']
    tail=c['explanation'].rsplit(marker,1)[1].removesuffix('.')
    if isinstance(expected,str):assert tail==expected,(tail,expected)
    else:assert numbers(tail)==list(map(F,expected)),(tail,expected)


def equal_options(options,value):
    return [expression(o['text'].removeprefix('Rp').replace(',00','').removesuffix(' liter').removesuffix(' hari lagi').removesuffix(' paket'))==value for o in options]


def check_math(original,c):
    q=original['id'];assert q in SUPPORTED,q
    assert 'Hasil pemeriksaan: ' in c['explanation'],c['explanation']
    s=plain(c['stem']);options=c['options'];opts=[plain(o['text']) for o in options]
    expected=[];proof=[]
    if q=='pg-1-1-5':
        measurements={m[1]:expression(m[2]) for m in re.finditer(r'Wadah ([XYZ]): ([^\n]+)',s)}
        assert len(measurements)==3
        from functools import cmp_to_key
        order=sorted(measurements,key=cmp_to_key(lambda a,b:compare(measurements[a],measurements[b])))
        expected=[re.findall(r'Wadah ([XYZ])',o)==order for o in opts];proof=''.join(order)
    elif q=='pg-1-2-3':
        values={m[1]:expression(m[2]) for m in re.finditer(r'Patok ([ABCD]): (.*?)m(?:\s|\n|$)',s)}
        assert len(values)==4,values
        expected=[compare(values['C'],values['A'])>0,compare(values['B'],calc('0'))>0,
            compare(values['A'],values['D'])<0,all(compare(values['A'],v)<0 for n,v in values.items() if n!='A')]
        proof='ABCD'[expected.index(True)]
    elif q=='mcma-1-2-6':
        values={m[1]:expression(m[2].split(' (ditulis')[0]) for m in re.finditer(r'Ruang ([ABCD]): ([^\n]+)',s)}
        assert len(values)==4
        decimal=expression(re.search(r'adalah (.*)$',opts[0])[1])
        match=re.search(r'Nilai (.*?) berada di antara (.*?) dan (.*)$',opts[2])
        x,a,b=map(expression,match.groups())
        expected=[values['C']==decimal,all(compare(values['C'],v)<0 for n,v in values.items() if n!='C'),compare(x,a)*compare(x,b)<0,
            all(compare(values[a],values[b])>0 for a,b in zip(['C','D','B'],['D','B','A']))]
        proof=[decimal.scalar(),min(a.scalar(),b.scalar()),max(a.scalar(),b.scalar())]
    elif q=='pg-1-3-1':
        analyses=re.findall(r'Analisis (I+V?|IV) \([^)]*\): ([^\n]+)',s)
        assert len(analyses)==4,analyses
        truth={label:all(compare(expression(a),expression(b))<0 for a,b in zip(chain.split('<'),chain.split('<')[1:])) for label,chain in analyses}
        expected=[truth[o.split()[-1]] for o in opts];proof=next(label for label,value in truth.items() if value)
    elif q=='pg-1-3-5':
        values={m[1]:expression(m[2]) for m in re.finditer(r'Pos ([pqr])=(.*?)m(?:\s|\n|$)',s)}
        p,z,r=(values[n] for n in 'pqr')
        expected=[compare(r,p)>0 and compare(r,z)>0,compare(z,r)<0,compare(p,r)<0,compare(p,r)*compare(p,z)<0]
        proof='ABCD'[expected.index(True)]
    elif q=='mcma-1-3-6':
        values={m[1]:expression(m[2]) for m in re.finditer(r'([WXYZ])=(.*?)m(?:\s|\n|$)',s)}
        w,x,y,z=(values[n] for n in 'WXYZ')
        expected=[w==y,all(compare(x,v)<0 for v in (w,y,z)),compare(z,w)>0,compare(x,w)>0 and compare(w,y)>=0 and compare(y,z)>0]
        proof=[w.scalar(),z.scalar()]
    elif q in ('pg-2-1-1','pg-2-2-1'):
        values=[number(n) for n in re.findall(r'Rp([\d.,]+)',s)]
        assert len(values)==6,values
        initial,expense,topup,second,third,cashback=values
        result=initial-expense+topup-second-third+cashback
        expected=equal_options(options,calc(str(result)));proof=[result]
    elif q=='pg-2-1-5':
        quantities=[int(n) for n in re.findall(r'(\d+) (?:kotak kue dan|dus minuman kemasan|lembar uang)',s)]
        values=[number(n) for n in re.findall(r'Rp([\d.,]+)',s)]
        assert len(quantities)==3 and len(values)==4,(quantities,values)
        a,b,notes=quantities;cost1,cost2,note,discount=values
        result=notes*note-(a*cost1+b*cost2-discount)
        expected=equal_options(options,calc(str(result)));proof=[result]
    elif q=='pg-2-1-2':
        scores=[number(n) for n in re.findall(r'nilai ([+-]\d+)',s)]
        total,right,blank=[int(n) for n in re.search(r'total (\d+) soal.*?benar (\d+) soal, tidak menjawab (\d+) soal',s).groups()]
        result=right*scores[0]+(total-right-blank)*scores[1]+blank*scores[2]
        expected=[calc(o)==calc(str(result)) for o in opts];proof=[result]
    elif q=='pg-2-1-3':
        p=expression(re.search(r'p=(.*?)meter',s)[1]);width=expression(re.search(r'l=(.*?)meter',s)[1])
        square=p*p+width*width
        expected=[expression(o)**2==square for o in opts];proof=[square.scalar()]
    elif q=='pg-2-2-2':
        p,z=map(expression,re.search(r'ukuran panjang (.*?)meter dan lebar (.*?)meter',s).groups())
        expected=[expression(o)==p-z for o in opts]
        coefficient=(p-z).get(5);assert coefficient is not None;proof=[coefficient]
    elif q=='pg-2-2-4':
        expr=re.search(r'Soal:([^\n]+)',s)[1];result=expression(expr).scalar()
        steps=re.findall(r'Langkah (I+V?|IV): Mengoperasikan ([^\n]+)',s)
        assert len(steps)==4,steps
        truth={}
        for label,chain in steps:
            parts=chain.split('=');values=[expression(part).scalar() for part in parts]
            assert len(set(values))==1,(label,chain,values)
            truth[label]=values[0]==result
        expected=[truth[o.split()[-1]] for o in opts];proof=[result]
    elif q in ('mcma-2-2-6','mcma-2-3-6'):
        statements=dict(re.findall(r'\((i{1,3}|iv)\) ([^\n]+)',s))
        assert len(statements)==4,statements
        truth={};values={}
        for label,statement in statements.items():
            left,right=statement.split('=');a,z=expression(left),expression(right)
            truth[label]=a==z;values[label]=a
        expected=[truth[re.search(r'\(([^)]+)\)',o)[1]] for o in opts]
        proof=[values['i'].scalar(),values['ii'].get(2),values['iii'].scalar(),values['iv'].scalar()]
    elif q=='mcma-2-2-7':
        a,b,z=[number(n) for n in re.search(r'Metode A: \(([\d.]+)-([\d.]+)\)-([\d.]+)',s).groups()]
        methoda=a-b-z;methodb=a-(b+z)
        for chain in re.findall(r'Metode [AB]: ([^\n]+)',s):
            assert all(expression(part).scalar()==methoda for part in chain.split('=')),chain
        claimed=number(re.search(r'Rp([\d.,]+)',opts[0])[1])
        wrong=expression(re.search(r'menjadi ([^,]+),',opts[2])[1]).scalar()
        expected=[methoda==methodb==claimed,True,wrong==methoda,False];proof=[methoda,wrong]
    elif q in ('pg-3-1-2','pg-3-2-2'):
        area=number(re.search(r'adalah ([\d.,]+)m\^2',s)[1]);result=rounded(root(area),1)
        expected=[numbers(o)[0]==result for o in opts];proof=[result]
    elif q in ('pg-3-1-3','pg-3-2-3'):
        weight=expression(re.search(r'seberat (.*?)kg',s)[1]).scalar()
        price=number(re.search(r'Rp([\d.,]+)',s)[1]);unit=rounded(price/1000)*1000
        result=weight*unit
        if q=='pg-3-1-3':result=rounded(result/1000)*1000
        expected=[numbers(o)[0]==result for o in opts];proof=[unit,result]
    elif q=='pg-3-1-5':
        qty=number(re.search(r'membeli (\d+) paket',s)[1]);cost=number(re.search(r'Rp([\d.,]+)',s)[1])
        result=rounded(qty/10)*10*rounded(cost/1000)*1000
        expected=[numbers(o)[0]==result for o in opts];proof=[result]
    elif q=='pg-3-2-4':
        expr=re.search(r'Operasi Hitung:([^\n]+)',s)[1];real=expression(expr).scalar()
        a,b,z=[number(n) for n in re.search(r'\(([\d.,]+)×([\d.,]+)\)/\(([\d.,]+)\)',expr).groups()]
        close=rounded(a/10)*10*rounded(b/10)*10/rounded(z)
        analyses={}
        for label,chain in re.findall(r'Analisis ([AB]): Mengubah operasi menjadi (.*?) dengan',s):
            left,right=chain.split('=');v=expression(left).scalar();assert v==number(right)
            analyses[label]=v
        assert analyses['B']==close
        assert abs(close-real)<abs(analyses['A']-real)
        displayed=number(re.search(r'hasil sebenarnya \(([\d.,]+)\)',s)[1])
        assert displayed==rounded(real,2)
        assert numbers(opts[1])==[close,displayed]
        expected=[False,True,False,False];proof=[rounded(real,2),close]
    elif q=='mcma-3-2-7':
        areas=[int(n) for n in re.findall(r'Luas (\d+)cm\^2',s)];assert len(areas)==3
        expected=[]
        for o in opts:
            match=re.search(r'sqrt\((\d+)\).*?adalah ([\d.,]+)cm',o)
            n,result=int(match[1]),number(match[2]);assert n in areas
            expected.append(result==rounded(root(n),1 if 'persepuluhan' in o else 0))
        proof=[rounded(root(areas[0]),1),rounded(root(areas[1]),1),rounded(root(areas[2]))]
    elif q=='mcma-3-2-8':
        qtya,costa,qtyb,costb=re.search(r'Membeli (\d+) pak buku seharga Rp([\d.,]+) per pak dan (\d+) botol minuman seharga Rp([\d.,]+)',s).groups()
        a,b=int(qtya),int(qtyb);p,z=number(costa),number(costb)
        qa,qb=rounded(F(a,10))*10,rounded(F(b,10))*10;pa,pb=rounded(p/1000)*1000,rounded(z/1000)*1000
        estimate=qa*pa+qb*pb;actual=a*p+b*z
        expected=[]
        for i,o in enumerate(opts):
            if i<2:
                left,right=re.search(r'dengan (.*?)=Rp([\d.,]+)',o).groups()
                assert expression(left).scalar()==number(right)
                expected.append(number(right)==estimate)
            else:
                displayed=number(re.search(r'Rp([\d.,]+)',o)[1]);assert displayed==estimate
                expected.append(actual<estimate if i==2 else estimate<actual)
        assert all(x<y for x,y in [(a,qa),(b,qb),(p,pa),(z,pb)])
        proof=[estimate,actual]
    elif q=='kategori-3-2-9':
        d,z,b=[number(n) for n in re.findall(r': ([\d.,]+) kg',s)]
        rd,rz,rb=rounded(d,1),rounded(z,1),rounded(b,1)
        expected=[numbers(opts[0])[-1]==rd,numbers(opts[1])[-1]==rounded(z),numbers(opts[2])[-1]==rd+rz+rb]
        proof=[rd,rounded(z),rd+rz+rb]
    elif q=='pg-3-3-3':
        qty=int(re.search(r'untuk (\d+) paket',s)[1]);cost=number(re.search(r'Rp([\d.,]+)',s)[1])
        topqty=math.ceil(F(qty,10))*10;topcost=math.ceil(cost/1000)*1000
        expected=[]
        for o in opts:
            a,b,z=numbers(o);assert a*b==z,o
            expected.append(a==topqty and b==topcost)
        proof=[topqty*topcost]
    elif q=='pg-4-1-1':
        a,b=[int(n) for n in re.findall(r'setiap (\d+) hari',s)];result=math.lcm(a,b)
        expected=[numbers(o)[0]==result for o in opts];proof=[result]
    elif q=='mcma-4-1-8':
        a,b,z=[int(n) for n in re.search(r'berupa (\d+) buku, (\d+) pensil, dan (\d+) penggaris',s).groups()]
        g=math.gcd(a,b,z)
        factor=expression(re.search(r'sebagai (.*)$',opts[3])[1]).scalar()
        expected=[numbers(opts[0])[0]==g,numbers(opts[1])[0]==F(a,g),numbers(opts[2])[0]==F(b,g),factor==g]
        listed=numbers(opts[3].split('dapat dinyatakan')[0]);assert listed==[a,b,z]
        proof=[g,F(a,g),F(b,g),F(z,g)]
    elif q.startswith('kategori-4-') and q.endswith('-9'):
        if q=='kategori-4-1-9':a,b=map(int,re.search(r'(\d+) kue bolu dan (\d+) kue lapis',s).groups())
        elif q=='kategori-4-2-9':a,b=map(int,re.search(r'(\d+) botol jus apel dan (\d+) botol jus jeruk',s).groups())
        else:a,b=map(int,re.search(r'(\d+) unit mikroskop dan (\d+) unit kaca',s).groups())
        g=math.gcd(a,b);u,z=F(a,g),F(b,g)
        third=abs(u-z) if 'Selisih' in opts[2] else u+z
        second=u if 'bolu' in opts[1] else z
        expected=[numbers(opts[0])[0]==g,numbers(opts[1])[0]==second,numbers(opts[2])[0]==third];proof=[g,u,z]
    elif q.startswith('kategori-4-') and q.endswith('-10'):
        lengths=[int(n) for n in re.findall(r'(\d+)\s?cm',s)];assert len(lengths)==2
        a,b=lengths;g=math.gcd(a,b);u,z=F(a,g),F(b,g)
        if q=='kategori-4-1-10':
            assert numbers(opts[1])[0]==a
            expected=[numbers(opts[0])[0]==g,numbers(opts[1])[-1]==u,numbers(opts[2])[0]==u+z]
        else:expected=[numbers(opts[0])[0]==g,numbers(opts[1])[0]==u+z,z==2*u]
        proof=[g,u,z,u+z]
    elif q=='pg-4-2-2':
        quantities=[int(n) for n in re.findall(r'(\d+) kg',s)];assert len(quantities)==3
        g=math.gcd(*quantities);expected=[numbers(o)[0]==g for o in opts];proof=[g]
    elif q=='pg-4-2-5':
        a,b=map(expression,re.search(r'faktorisasi prima ([\d^×]+),.*?faktorisasi prima ([\d^×]+)\.',s).groups())
        g=math.gcd(int(a.scalar()),int(b.scalar()))
        expected=[expression(o).scalar()==g for o in opts];proof=[g]
    elif q in ('mcma-4-2-8','mcma-4-3-8'):
        if q=='mcma-4-2-8':a,b=map(int,re.search(r'(\d+) unit tetikus.*?dan (\d+) unit papan',s).groups())
        else:a,b=map(int,re.search(r'(\d+) pak kertas.*?dan (\d+) botol',s).groups())
        g=math.gcd(a,b);u,z=F(a,g),F(b,g)
        expected=[numbers(opts[0])[0]==g,numbers(opts[1])[0]==g,numbers(opts[2])==[u,z],numbers(opts[3])==[u,z]]
        proof=[g,u,z]
    elif q=='pg-4-3-1':
        intervals=[int(n) for n in re.findall(r'setiap (\d+) hari',s)];assert len(intervals)==3
        g=math.lcm(*intervals);start=date(2026,3,int(re.search(r'tanggal (\d+) Maret',s)[1]));end=start+timedelta(days=g)
        months={'Maret':3,'April':4,'Mei':5};truth={}
        for label,days,day,month in re.findall(r'Analisis (I+V?|IV):.*?setelah (\d+) hari, yaitu pada tanggal (\d+) (Maret|April|Mei)',s):
            d=date(2026,months[month],int(day));truth[label]=int(days)==g and d==end
        assert len(truth)==4,truth
        expected=[truth[o.split()[-1]] for o in opts]
        month=next(name for name,n in months.items() if n==end.month)
        proof=f'{g}, {end.day} {month}'
    elif q=='pg-5-1-5':
        rows=re.findall(r'^([\dk]+) \| ([\d.,]+)$',s,re.M);assert len(rows)==4,rows
        ratios=[number(distance)/int(volume) for volume,distance in rows[:3]];assert len(set(ratios))==1
        target=number(rows[3][1])/ratios[0]
        assert 30<=ratios[0]<=50
        expected=[numbers(o)[0]==target for o in opts];proof=[ratios[0],target]
    else:raise AssertionError(q)
    assert [o['correct'] for o in options]==expected,(q,expected,options)
    checkpoint(c,proof)
