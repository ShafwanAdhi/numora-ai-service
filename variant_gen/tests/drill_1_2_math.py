"""Exact independent oracle of rendered 1–2 questions; no config/key evaluation."""
import ast
import re
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import isqrt

def number(s): return F(s.replace('.', '').replace(',', '.'))
def numbers(s): return [number(t) for t in re.findall(r'-?\d+(?:\.\d{3})*(?:,\d+)?',s)]

def squarefree(n):
    coefficient=1;radicand=1;p=2
    while p*p<=n:
        count=0
        while n%p==0: n//=p;count+=1
        coefficient*=p**(count//2)
        if count%2:radicand*=p
        p+=1
    return coefficient,radicand*n

class Root(dict):
    def __add__(self, other):
        out=Root(self)
        for d,c in rootvalue(other).items():out[d]=out.get(d,F(0))+c
        return Root({d:c for d,c in out.items() if c})
    __radd__=__add__
    def __neg__(self):return Root({d:-c for d,c in self.items()})
    def __sub__(self,other):return self+-rootvalue(other)
    def __mul__(self,other):
        out=Root()
        for a,c in self.items():
            for b,d in rootvalue(other).items():
                coef,rad=squarefree(a*b);out=out+Root({rad:c*d*coef})
        return out
    __rmul__=__mul__
    def scalar(self):
        assert not set(self)-{1},self
        return self.get(1,F(0))
    def __truediv__(self,other):
        value=rootvalue(other).scalar();assert value
        return Root({d:c/value for d,c in self.items()})
    def __pow__(self,n):
        n=rootvalue(n).scalar();assert n.denominator==1 and abs(n)<=24
        if n<0:return rootvalue(1)/(self**(-n))
        out=rootvalue(1)
        for _ in range(int(n)):out=out*self
        return out

def rootvalue(v):return v if isinstance(v,Root) else Root({1:F(v)}) if v else Root()
def radical(q):
    q=rootvalue(q).scalar();assert q>=0
    if not q:return Root()
    coefficient,rad=squarefree(q.numerator*q.denominator)
    return Root({rad:F(coefficient,q.denominator)})
def rational(q):return not set(q)-{1}
def compare(a,b):
    delta=rootvalue(a)-rootvalue(b)
    if not delta:return 0
    if rational(delta):return 1 if delta.scalar()>0 else -1
    with localcontext() as ctx:
        ctx.prec=50
        value=sum(Decimal(c.numerator)/Decimal(c.denominator)*Decimal(d).sqrt() for d,c in delta.items())
        assert abs(value)>Decimal('1e-35'), 'comparison too close for oracle bound'
        return 1 if value>0 else -1

def calc(text):
    text=text.strip().replace('−','-').replace('×','*').replace('÷','/').replace('^','**')
    text=re.sub(r'\d+(?:\.\d{3})+(?:,\d+)?',lambda m:m[0].replace('.',''),text)
    text=re.sub(r'(?<=\d),(?=\d)', '.',text)
    text=re.sub(r'(\d+)\s+(\d+)/(\d+)',r'(\1+\2/\3)',text)
    text=re.sub(r'(?<=[0-9)])\s*(?=sqrt\(|\()', '*',text)
    def visit(n):
        if isinstance(n,ast.Constant):return rootvalue(F(str(n.value)))
        if isinstance(n,ast.UnaryOp):
            assert isinstance(n.op,(ast.USub,ast.UAdd));return -visit(n.operand) if isinstance(n.op,ast.USub) else visit(n.operand)
        if isinstance(n,ast.Call):
            assert isinstance(n.func,ast.Name) and n.func.id=='sqrt' and len(n.args)==1
            return radical(visit(n.args[0]))
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow):return a**b
        raise AssertionError(('oracle unsupported expression',text))
    return visit(ast.parse(text,mode='eval').body)

def flags(c, expected):
    actual=[o['correct'] for o in c['options']]
    assert actual==list(expected),(actual,expected,c)
def between(x,a,b):return compare(x,a)*compare(x,b)<0
def line_value(s,label,ending):
    return calc(re.search(re.escape(label)+r'\s*(.*?)'+ending,s)[1])

def check_math(original,c):
    from drill_1_5_revised_math import SUPPORTED,check_math as revised_math
    if original['id'] in SUPPORTED:return revised_math(original,c)
    q=original['id'];s=c['stem'];opts=[o['text'] for o in c['options']]
    if q=='pg-1-1-1':
        values=[line_value(s,n+':',r'\s*gram') for n in ['Rian','Siti','Budi','Dewi']]
        flags(c,[not rational(v) for v in values]);assert sum(not rational(v) for v in values)==1
        for name,value in zip(['Rian','Siti'],values):
            match=re.search(name+r'=(.*?), (i?rasional)',c['explanation'])
            assert match and calc(match[1])==value and (match[2]=='rasional')==rational(value)
    elif q=='pg-1-1-2':
        a,b,d,e=[line_value(s,'Kedai '+n+' berada di posisi',r'\s*km') for n in 'ABCD']
        flags(c,[compare(a,b)>0,between(b,a,0),compare(d,e)<0,all(compare(e,v)>0 for v in (a,b,d))])
    elif q=='pg-1-1-3':
        values={}
        for name in ['Merah','Biru','Hijau','Kuning']:
            text=re.search('Toko '+name+r':\s*([^\n]+)',s)[1]
            values[name]=calc(text.replace('%',''))/(100 if '%' in text else 1)
            assert compare(values[name],-1)>=0 and compare(values[name],0)<0
        expected=[]
        for text in opts:
            names=re.findall(r'Toko (\w+)',text);expected.append(all(compare(values[a],values[b])<0 for a,b in zip(names,names[1:])))
        flags(c,expected)
    elif q=='pg-1-1-5':
        values={n:line_value(s,'Suhu wadah '+n+' adalah',r'°C') for n in 'XYZ'}
        flags(c,[all(compare(values[a],values[b])<0 for a,b in zip(re.findall(r'Wadah (\w)',t),re.findall(r'Wadah (\w)',t)[1:])) for t in opts])
    elif q=='mcma-1-1-6':
        fields=re.search(r'\{(.*?)\}',s)[1].split(';');a,b,d=map(calc,fields[:3])
        assert a.scalar().denominator==1 and fields[3]=='π'
        flags(c,[rational(a),not rational(b),rational(d),True])
        assert calc(re.search(r'^(-[^ ]+)',opts[0])[1])==a
        assert calc(re.search(r'(\([^()]*\)/\([^()]*\))',opts[2])[1])==d
    elif q=='mcma-1-1-7':
        a,b,d,e=[line_value(s,'Kelompok '+n+':',r'\s*mL') for n in 'ABCD']
        root=calc(re.search(r'Nilai (.*?) berada',opts[2])[1])
        bounds=re.search(r'antara (.*?) dan (.*?)\.',opts[2]);lower,upper=calc(bounds[1]),calc(bounds[2])
        flags(c,[compare(a,e)<0,all(compare(b,v)>0 for v in (a,e)),between(d,lower,upper) and root==d,
                 compare(e,a)<0 and compare(a,d)<0 and compare(d,b)<0])
    elif q in ['pg-1-2-2','pg-1-3-2']:
        if q=='pg-1-2-2':
            n=number(re.search(r'Sebanyak (\d+)',s)[1]);prices=[number(t) for t in re.findall(r'Rp([\d.,]+)',s)]
        else:
            n=number(re.search(r'Sebanyak (\d+)',s)[1]);prices=[number(t) for t in re.findall(r'Rp([\d.,]+)',s)]
        correct=n*sum(prices)
        results=[calc(t).scalar()==correct for t in opts]
        flags(c,results)
    elif q in ['pg-1-2-4','pg-1-3-3']:
        expression=re.search(r'karena (.*?) \(bilangan rasional\)',opts[0])[1]
        left,right=expression.split('=');assert calc(left)==calc(right)
        r=calc(re.search(r'sqrt\([^)]*\)',expression)[0]);assert not rational(r)
        flags(c,[True,False,False,False])
    elif q in ['pg-1-2-5','pg-1-3-4']:
        name='p' if q=='pg-1-2-5' else 'a'
        first=calc(re.search(name+r'=(.*?)\n',s)[1]);second=True # repeating decimal explicitly stated in stimulus
        assert 'desimal berulang' in s
        truth=[]
        for text in opts:
            if 'keduanya' in text:truth.append((rational(first) and second) if 'irasional' not in text else not rational(first) and not second)
            elif 'p dan q' in text or 'a dan b' in text:
                truth.append((not rational(first)) and not second)
            else:
                a_irr=re.search(name+r' (?:adalah )?irasional',text) is not None
                b_irr=re.search(r'(?:q|b) (?:adalah )?irasional',text) is not None
                truth.append(a_irr==(not rational(first)) and b_irr==(not second))
        flags(c,truth)
        if q=='pg-1-3-4':
            match=re.search(r'a=(.*?), (i?rasional)',c['explanation'])
            assert match and calc(match[1])==first and (match[2]=='rasional')==rational(first)
    elif q in ['mcma-1-2-7','mcma-1-3-7','mcma-2-3-7']:
        chains=re.findall(r'(?:Rumus [12]|Model I{1,2}):\s*([^\n]+)',s)
        assert len(chains)==2
        for chain in chains:
            values=[calc(t) for t in chain.split('=')];assert all(v==values[0] for v in values)
        equal=calc(chains[0].split('=')[0])==calc(chains[1].split('=')[0])
        if q=='mcma-2-3-7':
            assert equal;assert numbers(opts[0])[-1]==calc(chains[0].split('=')[0]).scalar()
            modified=re.search(r'diubah menjadi (.*?), hasilnya',opts[2])
            assert modified,opts[2]
            flags(c,[True,True,calc(modified[1])==calc(chains[1].split('=')[0]),True])
        else:
            assert not equal
            expression=opts[3].split('dengan ')[-1].split(' sesuai')[0] if q=='mcma-1-3-7' else opts[3].split('menjadi ')[-1].rstrip('.')
            if '=' in expression:
                left,right=expression.split('=');assert calc(left)==calc(right)
                assert calc(left)==calc(chains[1].split('=')[0])
            else:
                assert calc(expression)==calc(chains[0].split('=')[0])
            flags(c,[True,True,False,True])
    elif q in ['mcma-1-2-8','mcma-1-3-8']:
        k,l,m,n=[line_value(s,label+'=',r'\n') for label in ['K','L','M','N']]
        assert n==Root()
        targets={0:k*l,3:l*l,(1 if q=='mcma-1-2-8' else 2):k+m}
        for index,target in targets.items():
            match=re.search(r'yaitu (.*)\) (?:tergolong|merupakan|menghasilkan)',opts[index])
            assert match,opts[index]
            assert all(calc(part)==target for part in match[1].split('=')),opts[index]
        if q=='mcma-1-2-8':flags(c,[rational(k*l),rational(k+m),False,rational(l*l) and (l*l).scalar().denominator==1])
        else:flags(c,[not rational(k*l),False,rational(k+m),rational(l*l) and (l*l).scalar().denominator==1])
    elif q in ['kategori-1-1-9','kategori-1-2-9','kategori-1-3-9']:
        if q=='kategori-1-1-9':
            a,b,d=[line_value(s,'Siswa '+str(i)+':',r'\s*m') for i in (1,2,3)]
            bound=calc(re.search(r'daripada (.*?) m',opts[1])[1]);flags(c,[compare(a,b)<0,compare(d,bound)>0,compare(-b,-a)<0])
        elif q=='kategori-1-2-9':
            a,b,d=[line_value(s,'Kedai '+n+':',r'°C') for n in ['Merah','Kuning','Hijau']]
            decimal=calc(re.search(r'desimal adalah (.*?)°C',opts[0])[1]);flags(c,[decimal==b,compare(a,b)>0,compare(a,b)<0 and compare(b,d)<0])
        else:
            a,b,d=[line_value(s,'Tim '+n+':',r'\s*°C') for n in ['Alpha','Beta','Gamma']]
            decimal=re.search(r'\((-?\d+),(\d+)\.\.\.',opts[0]);integer=F(decimal[1]);repeat=F(int(decimal[2]),10**len(decimal[2])-1)
            assert integer-repeat==b.scalar()
            flags(c,[True,compare(a,b)<0,compare(b,a)<0 and compare(a,d)<0])
    elif q in ['pg-2-1-4','pg-2-2-3','pg-2-3-3']:
        if q=='pg-2-1-4':
            initial=calc(re.search(r'terdapat (.*?) mikroorganisme',s)[1]);hours=number(re.search(r'setelah ([\d,]+) jam',s)[1]);periods=hours*2;base=2
        elif q=='pg-2-2-3':
            initial=calc(re.search(r'terdapat (.*?) sel',s)[1]);minutes=number(re.search(r'\((\d+) menit',s)[1]);periods=minutes/20;base=3
            assert number(re.search(r'selama ([\d,]+) jam',s)[1])==F(str(round(Decimal(minutes.numerator)/Decimal(minutes.denominator)/60,2)))
        else:
            initial=calc(re.search(r'Kultur Y mula-mula berjumlah (.*?) sel',s)[1]);hours=number(re.search(r'setelah ([\d,]+) jam',s)[1]);periods=hours*2;base=2
        assert periods.denominator==1 and periods>0
        answer=initial*base**int(periods)
        flags(c,[calc(t.split(' ')[0])==answer for t in opts])
    elif q=='mcma-2-1-6':
        expressions=re.findall(r'\([iv]+\) (.*?)\n',s)
        expected=[]
        for expression in expressions:
            left,right=expression.split('=');expected.append(calc(left)==calc(right))
        flags(c,expected)
    elif q=='mcma-2-1-7':
        total=number(re.search(r'membagikan (\d+)',s)[1]);groups=number(re.search(r'kepada (\d+)',s)[1]);used=calc(re.search(r'menggunakan (.*?) bagian',s)[1]).scalar();people=number(re.search(r'kepada (\d+) anggota',s)[1])
        received=total/groups;remaining=received*(1-used)
        flags(c,[numbers(opts[0])[0]==received,numbers(opts[1])[0]==received*used,numbers(opts[2])[0]==remaining,numbers(opts[3])[0]==remaining/people])
    elif q in ['mcma-2-1-8','mcma-2-2-8','mcma-2-3-8']:
        expression=re.search(r'[HMN]=(.*?)\n',s)[1];total=calc(expression).scalar()
        divide=re.search(r'([\d.,]+)÷(\(-?[\d.,]+\)|[\d.,]+)',expression);div=calc(divide[0]).scalar()
        multiply=re.search(r'([\d.,]+)×(\(\d+\)/\(\d+\)|\(-?[\d.,]+\))',expression);mul=calc(multiply[0]).scalar()
        if q=='mcma-2-1-8':
            a,b=map(number,re.search(r'H=([\d.,]+)-([\d.,]+)',s).groups());den=calc(divide[2]).scalar();factor=number(multiply[1]);last=calc(multiply[2]).scalar()
            left_to_right=((a-b)/den+factor)*last
            flags(c,[numbers(opts[0])[-1]==div,numbers(opts[1])[-1]==mul,numbers(opts[2])[-1]==total,numbers(opts[3])[-1]==left_to_right])
            explanation=c['explanation']
            division=re.search(r'Pembagian (.*?);',explanation)
            multiplication=re.search(r'perkalian(.*?)\.',explanation)
            assert division and multiplication,explanation
            for match,expected in [(division,div),(multiplication,mul)]:
                assert all(calc(part).scalar()==expected for part in match[1].split('='))
            assert number(re.search(r'H=([^ .]+)',explanation)[1])==total
            assert number(re.search(r'Kiri ke kanan memberi ([^,]+),',explanation)[1])==left_to_right
        else:flags(c,[numbers(opts[0])[-1]==div,numbers(opts[1])[-1]==mul,numbers(opts[2])[-1]==total,numbers(opts[3])[-1]==total])
    elif q in ['kategori-2-1-9','kategori-2-2-9','kategori-2-3-9']:
        weights=[calc(t).scalar() for t in re.findall(r'(\d+ \d+/\d+)kg',s)];prices=[number(t) for t in re.findall(r'Rp([\d.,]+)',s)]
        assert len(weights)==len(prices)==2
        a,b=[w*p for w,p in zip(weights,prices)]
        middle=b<a if 'lebih murah' in opts[1] else b>a
        flags(c,[numbers(opts[0])[-1]==a,middle,numbers(opts[2])[-1]==a+b])
    elif q in ['kategori-2-1-10','kategori-2-2-10','kategori-2-3-10']:
        p=calc(re.search(r'P=(.*?)\n',s)[1]);v=calc(re.search(r'Q=(.*?)\n',s)[1])
        if q=='kategori-2-1-10':expected=[calc(str(numbers(opts[0])[-1]).replace('.',','))==p,rootvalue(numbers(opts[1])[-1])==v,rootvalue(numbers(opts[2])[-1])==p-v]
        else:
            claim=re.search(r'adalah (.*?)\.',opts[0])[1]
            expected=[calc(claim)==p,rootvalue(numbers(opts[1])[-1])==v,compare(v,p)<0]
        flags(c,expected)
        for name,val in [('P',p),('Q',v)]:
            match=re.search(name+r'=([^,;]+)',c['explanation'])
            if match:
                # Decimal comma belongs to the expression, so use punctuation boundary rather than comma.
                text=c['explanation'].split(name+'=',1)[1].split(';')[0].split(', Q=')[0]
                assert calc(text)==val,(q,text,val)
    elif q=='pg-2-3-2':
        areas=[number(t) for t in re.findall(r'luas ([\d.,]+)m\^\(2\)',s)];assert len(areas)==2
        answer=radical(areas[0])-radical(areas[1]);flags(c,[calc(t.rstrip('m').strip())==answer for t in opts])
    else:raise AssertionError('No independent oracle for '+q)
