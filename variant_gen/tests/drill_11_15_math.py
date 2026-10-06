"""Independent Fraction-based checks of rendered questions (no engine expressions).

The oracle reads the stimulus/options, never the config's derived values or keys.
Deliberately fail closed for an unimplemented question model.
"""
import ast
import operator
import re
import math
from fractions import Fraction as F
from math import isqrt


NUMBER = r'-?\d+ \d+/\d+|-?\d+/\d+|-?\d+(?:\.\d{3})*(?:,\d+)?(?:\.\d+)?'


def nums(text):
    # Ignore exponents and subscripts, but keep coefficients in 3x / 4n.
    text = re.sub(r'\^\([^)]*\)|_\d+|ke-\d+|(?<=[AB])\d', '', text)
    return [number(m) for m in re.findall(NUMBER, text)]


def number(s):
    if ' ' in s.strip():
        a,b=s.split(); return F(a)+F(b)
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif re.fullmatch(r'-?\d{1,3}(?:\.\d{3})+', s):
        s = s.replace('.', '')
    return F(s)


def calc(text, **env):
    text = text.strip().replace('−', '-').replace('×', '*').replace('·','*').replace('^', '**')
    text = re.sub(r'(?<=\d)\.(?=\d{3}(?:\D|$))','',text)
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)
    text = re.sub(r'(\d|\))\s*(?=[xn(])', r'\1*', text)
    text = re.sub(r'([xn])\s*(?=\()', r'\1*', text)
    text = re.sub(r'\)(?=\d)', r')*',text)
    ops = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul,
           ast.Div:operator.truediv, ast.Pow:operator.pow}
    def visit(node):
        if isinstance(node, ast.Constant): return F(str(node.value))
        if isinstance(node, ast.Name): return F(env[node.id])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -visit(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](visit(node.left), visit(node.right))
        raise AssertionError(('unsupported test expression', text))
    return visit(ast.parse(text, mode='eval').body)


def root(value):
    value = F(value)
    a, b = isqrt(value.numerator), isqrt(value.denominator)
    assert a*a == value.numerator and b*b == value.denominator, value
    return F(a, b)


def equal_options(options, answer):
    return [nums(o['text'])[0] == answer for o in options]


def flags(options, expected):
    actual = [o['correct'] for o in options]
    assert actual == list(expected), (actual, expected, options)


def angle_model(qid, c):
    s, options = c['stem'], c['options']
    suffix = '-'.join(qid.split('-')[2:])
    # Build all eight angles from position, not from their written answers.
    body = s.split('∠B1). ', 1)[-1] if s.startswith('Garis p ∥ q (p di atas q)') else s
    n = nums(body)
    on = [nums(o['text']) for o in options]
    if s.startswith('Garis p ∥ q (p di atas q)'):
        assignments = re.findall(r'∠([AB][1-4])\s*=\s*(\([^°]+\)|[-\d,./ ]+)°', body)[:2]
        if suffix == '5-6':
            theta=180-n[0]/2; x=None
        elif len(assignments) == 2:
            (u, a), (v, b) = assignments
            a0,a1,b0,b1 = calc(a,x=0),calc(a,x=1),calc(b,x=0),calc(b,x=1)
            same = (u[-1] in '14') == (v[-1] in '14')
            x = (b0-a0)/(a1-a0-b1+b0) if same else (180-a0-b0)/(a1-a0+b1-b0)
            av = calc(a,x=x)
            theta = av if u[-1] in '14' else 180-av
        elif assignments:
            u,a = assignments[0]; av = calc(a); x = None
            theta = av if u[-1] in '14' else 180-av
        elif suffix == '3-3':
            a,b = n; theta=180*a/(a+b); x=None
        elif suffix == '3-9':
            theta=180*n[0]/(n[0]+1); x=None
        elif suffix == '5-6':
            theta=180-n[0]/2; x=None
        else: raise AssertionError(('parallel model missing', qid, body))
        assert 0 < theta < 180, (qid, theta)
        angles = {p+str(i):theta if i in (1,4) else 180-theta for p in 'AB' for i in range(1,5)}
        if qid.startswith('pg'):
            if suffix == '5-2':
                return [False, on[1][-1]==angles['A2'], False, False]
            if suffix == '5-3':
                claims = re.findall(r'(Rina|Doni) menyatakan ∠B4 = ([\d, /]+)°', body)
                wins = [number(v)==angles['B4'] for _,v in claims]
                return [wins[0],wins[1],not any(wins) and on[2][0]==angles['B4'],
                        not any(wins) and on[3][0]==angles['B4']]
            target=re.search(r'(?:besar|Besar) ∠([AB][1-4])',body).group(1)
            return equal_options(options,angles[target])
        out=[]
        for o in options:
            t=o['text']
            if t.startswith('x ='): out.append(nums(t)[0]==x); continue
            if 'adalah sudut sehadap' in t:
                a,b=re.findall(r'∠([AB][1-4])',t); out.append(a[-1]==b[-1]); continue
            if 'besarnya sama' in t:
                a,b=re.findall(r'∠([AB][1-4])',t); out.append(angles[a]==angles[b]); continue
            lhs,rhs=t.split('=',1)
            if 'sehingga' in lhs: lhs=lhs.split('sehingga',1)[1]
            labels=re.findall(r'∠([AB][1-4])',lhs)
            value=sum(angles[a] for a in labels)
            correct = value==number(re.search(NUMBER,rhs).group().strip())
            if 'karena sehadap' in rhs:
                ref=re.search(r'∠([AB][1-4])',rhs).group(1)
                correct &= labels[0][-1]==ref[-1]
            out.append(correct)
        return out
    expressions = re.findall(r'\(([^°]+x[^°]*|x[^°]*)\)°',body)
    if expressions:
        if len(expressions)==3:
            x=(180-sum(calc(e,x=0) for e in expressions))/sum(calc(e,x=1)-calc(e,x=0) for e in expressions)
            a,b,d=[calc(e,x=x) for e in expressions]
        elif suffix=='2-10':
            ext=nums(body)[-1]
            x=(ext-sum(calc(e,x=0) for e in expressions))/sum(calc(e,x=1)-calc(e,x=0) for e in expressions)
            a,b=[calc(e,x=x) for e in expressions]; d=180-ext
        else: raise AssertionError(qid)
    else:
        x=None
        if suffix in ('1-3','1-5','2-8','3-5','4-5','4-8','5-9'):
            a,b=n[:2];d=180-a-b
        elif suffix=='2-4': a=n[0];b=d=(180-a)/2
        elif suffix=='2-5': a=n[0]*n[1]/(n[1]+n[2]);b=n[0]-a;d=180-n[0]
        elif suffix=='3-4': a=180-n[0];b=d=n[0]/2
        elif suffix=='3-7': a,b,d=[180*v/sum(n) for v in n]
        elif suffix=='3-8': a,b=180-n[0],180-n[1];d=180-a-b
        elif suffix=='3-10': a=n[0];b=90;d=90-a
        elif suffix=='4-7':
            ratio=2 if 'dua kali' in body else n[0];a=180/(1+2*ratio);b=d=ratio*a
        elif suffix=='5-5': a=(n[0]+n[1])/2;b=n[0]-a;d=180-n[0]
        elif suffix=='5-8': a=180-n[0];d=n[0]/(n[1]+1);b=n[1]*d
        elif suffix=='1-8': return [sum(v)==180 and min(v)>0 for v in on]
        else: raise AssertionError(('triangle model missing',qid,n))
    assert min(a,b,d)>0 and a+b+d==180,(qid,a,b,d)
    if qid.startswith('pg'):
        answers={'1-3':d,'1-4':max(a,b,d),'1-5':a+b,'2-4':b,'2-5':a,
                 '3-4':b,'3-5':90-b,'4-4':max(a,b,d)-min(a,b,d)}
        if suffix in answers: return equal_options(options,answers[suffix])
        if suffix=='4-5': return [False,False,False,on[3][0]==a+b]
        if suffix=='5-4': return [False,len({a,b,d})==3 and max(a,b,d)<90,max(a,b,d)==90,max(a,b,d)>90]
        if suffix=='5-5':
            winners=[name for name,v in re.findall(r'(Dina|Eko) memperoleh ∠A = ([\d,]+)°',body) if number(v)==a]
            return [o['text'].split()[0] in winners for o in options]
        raise AssertionError(qid)
    if suffix=='2-7': return [on[0][0]==x,on[1][0]==a,on[2][0]==b,max(a,b,d)==90]
    if suffix=='2-8': return [on[0][0]==d,on[1][0]==d,on[2][0]==180-d,on[3][0]==180-d]
    if suffix=='2-10': return [on[0][0]==x,on[1][0]==d,max(a,b,d)==90]
    if suffix=='3-7': return [on[0][0]==a,on[1][0]==b,max(a,b,d)<90,on[3][0]==180-a]
    if suffix=='3-8': return [on[0][0]==b,on[1][0]==a,on[2][0]==d,on[3][0]==180-d]
    if suffix=='3-10': return [on[0][0]==d,on[1][0]==180-d,on[2][0]==a+d]
    if suffix=='4-7': return [on[0][0]==a,on[1][0]==b,on[2][0]==b+d,max(a,b,d)>90]
    if suffix=='4-8': return [on[0][0]==180-a,on[1][0]==180-b,on[2][0]==180-d,on[3][0]==360]
    if suffix=='5-7': return [on[0][0]==x,max(a,b,d)==90,on[2][0]==min(a,b,d),on[3][0]==max(a,b,d)]
    if suffix=='5-8': return [on[0][0]==b,on[1][0]==d,max(a,b,d)<90,on[3][0]==180-d]
    if suffix=='5-9': return [on[0][0]==a,on[1][0]==d,max(a,b,d)<90]
    raise AssertionError(qid)


def geometry_model(qid,c):
    s,options=c['stem'],c['options']; n=nums(s); v=[nums(o['text']) for o in options]
    suffix='-'.join(qid.split('-')[2:]); pg=qid.startswith('pg')
    if qid == 'pg-15-4-2':
        short, long, angle = map(float, n[:3])
        assert 0 < short < long and 0 < angle < 90, (qid, n)
        other = math.degrees(math.asin(short * math.sin(math.radians(angle)) / long))
        possibilities = sum(angle + b < 180 for b in (other, 180 - other))
        vertices = re.search(r'segitiga ([A-Z]{3})', s)[1]
        given_angle = re.search(r'∠([A-Z]) =', s)[1]
        included = given_angle == vertices[1]
        assert len(options) == 4
        return [included, False, False, not included and possibilities == 1]
    def right(sides):
        a,b,d=sorted(sides); assert a+b>d and a>0,sides
        return a*a+b*b==d*d
    if pg:
        answers={}
        if suffix=='1-1': return [right(t) for t in v]
        elif suffix=='1-2': answer=root(n[1]**2-n[0]**2)
        elif suffix=='1-4': answer=n[2]*n[1]/n[0]
        elif suffix=='1-5': answer=n[1]*n[3]/n[2]
        elif suffix=='2-1': answer=root(n[0]**2-n[1]**2)+n[2]
        elif suffix=='2-2':
            # Rendered affine side lengths, solve x from the Pythagorean equation.
            sides=['x']+re.findall(r'\(([^)]+)\) cm',s)
            xs=[i for i in range(1,501) if (z:=sorted(calc(e,x=i) for e in sides))[0]>0 and z[0]**2+z[1]**2==z[2]**2]
            assert len(xs)==1,(s,xs);answer=sum(calc(e,x=xs[0]) for e in sides)
        elif suffix=='2-3': return ['∠Q' in o['text'] and nums(o['text'])[0]==n[2] for o in options]
        elif suffix=='2-4': answer=sum(n[:3])*n[3]/n[0]
        elif suffix=='2-5': answer=n[0]*(n[2]/n[1])**2
        elif suffix=='3-1': answer=4*root((n[0]/2)**2+(n[1]/2)**2)
        elif suffix=='3-2': return [not right(t) for t in v]
        elif suffix=='3-4': answer=n[0]**2/root(n[0]**2+n[1]**2)
        elif suffix=='3-5': answer=n[2]*n[3]*(n[1]/100000)**2
        elif suffix=='4-1': answer=n[1]*root(n[0]**2-(n[1]/2)**2)/2
        elif suffix=='4-3': answer=n[2]*(n[0]+n[1])/n[0]
        elif suffix=='4-4': answer=n[0]*(n[1]+n[2])/n[2]
        elif suffix=='4-5': return [False,v[1][0]==(n[2]/n[0])**2 and v[1][1]==n[1]*n[2]**2/n[0] and v[1][2]==n[0]*n[1],False,False]
        elif suffix=='5-1':
            z=v[1];return [False,right(z[:3]) and not right(z[3:6]) and z[8]==z[3]**2+z[4]**2 and z[9]==z[5]**2,False,False]
        elif suffix=='5-2':
            answer=root(n[0]**2-n[1]**2)
            reports=re.findall(r'(Ani|Budi|Cici|Doni): ([^.]+?)(?=\. | Siswa)',s)
            # The subtraction-of-squares method with an actual square root is correct.
            winners=[name for name,text in reports if '√(' in text and ' - ' in text and nums(text)[-1]==answer]
            return [o['text'] in winners for o in options]
        elif suffix=='5-4': return [v[0][0]==n[1]*n[3]/n[0],False,False,False]
        elif suffix=='5-5': answer=n[1]*n[2]/100000;return [False,False,v[2][-1]==answer,False]
        else: raise AssertionError(qid)
        return equal_options(options,answer)
    if suffix=='1-6':
        r=n[0]/n[1];return [v[0][0]/v[0][1]==r*r,v[1][0]/v[1][1]==r*r,v[2][0]/v[2][1]==r,v[3][0]/v[3][1]==r]
    if suffix=='1-7':
        a,b=n;d=root(a*a+b*b);return [v[0][0]==d,v[1][0]==a+b+d,v[2][0]==a*b/2,False]
    if suffix=='1-8':
        return [v[0][:3]==v[0][3:],False,0<v[2][1]<180,v[3][0]==v[3][1]]
    if suffix=='1-9':
        scale=n[1]/n[0]/100000;return [v[0][1]==v[0][0]*scale,v[1][1]==v[1][0]/scale,v[2][1]==v[2][0]*scale]
    if suffix=='1-10':
        a,b=n;return [v[0][0]==root(a*a+b*b),v[1][0]==a*b/2,False]
    if suffix=='2-6':
        return [v[0][0]==max(n),right(v[1]),right(v[2]),v[3][0]==n[0]*n[1]/2]
    if suffix=='2-9': return [v[0][0]==n[0]*n[2]/n[1],v[1][0]/v[1][1]==n[0]/n[1],v[2][1]/v[2][0]==n[0]/n[1]]
    if suffix=='2-10':
        r=n[1]/n[0];big=n[2]*r*r;return [v[0][1]/v[0][0]==r*r,v[1][0]==big,v[2][0]==big-n[2]]
    if suffix=='3-6':
        r=n[2]/n[0];return [v[0][1]/v[0][0]==r*r,v[1][1]/v[1][0]==r,v[2][0]==r,v[3][0]==n[2]*n[3]-n[0]*n[1]]
    if suffix=='3-7':
        r=n[0]/(n[0]+n[1]);return [True,v[1][0]==n[2]/r,v[2][0]/v[2][1]==r,v[3][0]/v[3][1]==r*r]
    if suffix=='3-8': return [v[0][0]==n[0]*n[2]/n[1],v[1][0]==n[3]*n[1]/n[0],v[2][0]==abs(n[0]*n[2]/n[1]-n[3]),v[3][0]/v[3][1]==n[0]/n[1]]
    if suffix=='3-9': return [right(v[0]),right(v[1]),right(v[2][:3]) and v[2][3]==max(v[2][:3])]
    if suffix=='3-10':
        diag=root(n[0]**2+n[1]**2);path=sum(n);return [v[0][0]==diag,v[1][0]==path-diag,v[2][0]==path/diag]
    if suffix=='4-6': return [right(n),False,right(v[2][:3]) and all(t==v[2][3]*b for t,b in zip(v[2][:3],v[2][4:])),v[3][0]==max(n)]
    if suffix=='4-7':
        r=n[1]/n[0];return [True,v[1][0]==n[2]*r,v[2][1]/v[2][0]==r,v[3][1]/v[3][0]==r*r]
    if suffix=='4-8': return [v[0][0]==n[0]*n[2]/n[1],v[1][0]==n[0]*n[2]/n[1],True,False]
    if suffix=='4-9':
        r=n[0];return [v[0][0]==r*r,v[1][0]==v[1][1],v[2][0]*v[2][1]**2==v[2][2]]
    if suffix=='4-10': return [v[0][0]==root(n[0]**2-n[1]**2),False,v[2][1]==root(n[0]**2-v[2][0]**2)]
    if suffix=='5-6':
        r=n[1]/n[0];return [v[0][0]==n[2]*r*r,v[1][0]==n[2]*r*r,v[2][1]/v[2][0]==r*r,v[3][1]/v[3][0]==r]
    if suffix=='5-7':
        ratios=[b/a for a,b in zip(n[:3],n[3:])];return [len(set(ratios))==1 and v[0][1]/v[0][0]==ratios[0],ratios==[1]*3,False,len(set(ratios))==1]
    if suffix=='5-8':
        r=n[0]/n[1];return [v[0][0]==n[2]/r,v[1][0]==n[2]/r,v[2][0]/v[2][1]==r,v[3][0]/v[3][1]==r*r/(1-r*r)]
    if suffix=='5-9': return [v[0][0]==n[2]*100/n[1] and v[0][1]==n[3]*100/n[1],v[1][-1]==n[2]*n[3]*10000,v[2][1]/v[2][0]==n[1]**2]
    if suffix=='5-10': return [all(right(v[0][i:i+3]) for i in (0,3,6)),False,right(v[2]) and v[2]==[3,4,5]]
    raise AssertionError(qid)


def formula(text, variable='n'):
    return text.split('=',1)[1].strip().rstrip('.')


def sequence_model(qid,c):
    """Solve sequence/series stimuli; finite sums use enumeration as an oracle."""
    s,opts=c['stem'],c['options']; z=nums(s); v=[nums(o['text']) for o in opts]
    ind=int(qid.split('-')[1]); suf='-'.join(qid.split('-')[2:])
    def arithmetic(a,d):
        return lambda j:a+(j-1)*d
    def geometric(a,r):
        return lambda j:a*r**(j-1)
    def terms(a): return sum(a(j) for j in range(1,13))
    def match(a): return equal_options(opts,a)
    def formulas(U,S,kind='U'):
        f=U if kind=='U' else S
        return [all(calc(formula(o['text']),n=j)==f(j) for j in range(1,7)) for o in opts]
    def claims(U,S):
        out=[]
        for o in opts:
            t=o['text'].replace(' adalah ','=')
            start=re.search(r'[US]_(?:n|\d+)',t)
            assert start,(qid,t)
            eq=t[start.start():].rstrip(' .').split(' dan ')
            valid=True
            for part in eq:
                for j in range(1,7):
                    parts=part.split('=')
                    values=[]
                    for p in parts:
                        p=re.sub(r'([US])_(n|\d+)',lambda m:str((U if m[1]=='U' else S)(j if m[2]=='n' else int(m[2]))),p)
                        values.append(calc(p,n=j))
                    valid &= len(set(values))==1
            out.append(valid)
        return out
    if ind==12:
        if suf=='1-1':
            a=arithmetic(z[0],z[1]-z[0]);return [False,v[1][-2:]==[a(5),a(6)],v[2][-2:]==[a(5),a(6)],False]
        if suf=='1-2': return formulas(geometric(z[0],z[1]/z[0]),None)
        if suf=='1-3': return match(arithmetic(z[0],z[1]-z[0])(8))
        if suf=='1-4': return [False,v[1][0]/v[1][1]==z[1]/z[2],False,False]
        if suf=='1-5': return match(arithmetic(z[0],z[1])(12))
        if suf=='1-6':
            d=z[1]-z[0];return [len(set(z[i+1]-z[i] for i in range(len(z)-1)))==1,v[1][0]==d,-v[2][0]==d,v[3][0]==z[-1]+d]
        if suf=='1-7':
            U=arithmetic(z[0],z[1]-z[0]);return [v[0][0]==z[1]-z[0]]+[all(calc(formula(o['text']).rstrip('.'),n=j)==U(j) for j in range(1,7)) for o in opts[1:]]
        if suf=='1-8':
            # P,Q arithmetic; R,S geometric. Direction matters as well as type.
            seqs=re.findall(r'[PQRS]: ([^\n]+)',s)
            p,q,r,t=[nums(a) for a in seqs];return [p[1]<p[0],q[1]-q[0]==v[1][0],r[1]/r[0]==v[2][0],t[1]/t[0]==v[3][0]/v[3][1]]
        if suf in ('1-9','1-10','2-9'):
            U=geometric(z[0],z[1]/z[0]) if suf=='1-9' else arithmetic(z[0],z[1]-z[0]) if suf=='1-10' else arithmetic(z[0],z[1])
            if suf=='1-10':return [z[1]-z[0]>0,z[1]<z[0],v[2][0]==U(5)]
            if suf=='1-9': return [a[0]==U(j) for a,j in zip(v,[5,7,8])]
            return [a[0]==U(j) for a,j in zip(v,[4,10,8])]
        if suf=='2-1':
            r=z[1]/z[0];u=geometric(z[0],r)(6);return [False,calc(formula(opts[1]['text']).split(';')[0])==r and calc(opts[1]['text'].split('U_6=')[1])==u,False,False]
        if suf=='2-2':
            U=arithmetic(z[0]-2*(z[1]-z[0])/4,(z[1]-z[0])/4);return formulas(U,None)
        if suf=='2-3':return match(geometric(z[0],z[1]/z[0])(5))
        if suf=='2-5':
            U=arithmetic(z[0],z[1]);return [U(int(a[0])-1)<=z[2]<U(int(a[0])) for a in v]
        if suf=='2-6':
            r=z[1]/z[0];return [len(set(z[i+1]/z[i] for i in range(len(z)-1)))==1,v[1][0]/v[1][1]==r,len(set(z[i+1]-z[i] for i in range(len(z)-1)))==1,v[3][0]==z[-1]*r]
        if suf=='2-7':
            U=arithmetic(z[0],z[1]-z[0]);n=(z[-1]-z[0])/(z[1]-z[0])+1;return [v[0][0]==n,v[1][0]==U(10),v[2][0]==U(15),F(re.search(r'ke-(\d+)',opts[3]['text'])[1])==n]
        if suf=='2-8':return [v[0][0]>1,False,True,v[3][0]==1 and v[3][1]==z[0]]
        if suf=='2-10':
            fs=[s.split('U_n=')[1].split(' dan ')[0],s.split('U_n=')[2].split('. Tentukan')[0]];r=[calc(a,n=2)/calc(a,n=1) for a in fs];return [r[0]==2,r[1]==2,calc(fs[0],n=1)==calc(fs[1],n=1) and calc(fs[0],n=2)!=calc(fs[1],n=2)]
        if suf=='3-1':
            rows=re.findall(r'(\([iv]+\)) ([\d, .-]+)',s);geo=[];down=[]
            for label,t in rows:
                a=nums(t.strip(' .'));diff=[a[i+1]-a[i] for i in range(len(a)-1)];rat=[a[i+1]/a[i] for i in range(len(a)-1)]
                if len(set(rat))==1 and 0<rat[0]<1:geo.append(label)
                if len(set(diff))==1 and diff[0]<0:down.append(label)
            return [re.findall(r'\([iv]+\)',o['text'])==geo+down for o in opts]
        if suf=='3-2':
            b=z[-1]/6;return formulas(arithmetic(2*b,b),None)
        if suf=='3-3':
            U=arithmetic(z[0],z[1]-z[0]);V=arithmetic(z[3],z[4]-z[3]);j=next(i for i in range(1,11) if U(i)==V(i));return match(U(j))
        if suf=='3-4':return [v[0][0]==-z[1] and v[0][1]==z[0]*(1-z[2]/z[3]),False,False,False]
        if suf=='3-5':
            U=geometric(z[0],3);return [U(int(a[0])-1)<=z[1]<U(int(a[0])) for a in v]
        if suf=='3-6':
            groups=re.findall(r'[PQR]: ([^\n]+)',s);p,q,r=[nums(t) for t in groups]
            return [q[1]/q[0]==v[0][0],r[1]-r[0]==v[1][0],len(set(p[i+1]-p[i] for i in range(len(p)-1)))>1 and len(set(p[i+1]/p[i] for i in range(len(p)-1)))>1,len(set(p[i+1]-p[i] for i in range(len(p)-1)))==1]
        if suf=='3-7':
            r=next(F(i) for i in range(1,11) if i**3==z[1]/z[0]);a=z[0]/r**2;return [v[0][0]==r,v[1][0]==a,False,r==3]
        if suf=='3-8':
            U=arithmetic(z[0],z[3]);V=arithmetic(z[4],z[-1]);return [v[0][0]==(U(2)-V(2))-(U(1)-V(1)),v[1][0]==U(5)-V(5),U(2)-V(2)>U(1)-V(1),v[3]==[U(4),V(4)]]
        if suf=='3-9':
            U=arithmetic(z[0],z[1]-z[0]);count=(z[-1]-z[0])/(z[1]-z[0])+1;return [v[0][0]==count,v[1][0]==U(20),U(2)+U(int(count)-1)==z[0]+z[-1]]
        if suf=='4-1':return [False,v[1][0]==z[1]/z[0],False,False]
        if suf=='4-2':
            U=arithmetic(z[0],z[1]-z[0]);report=s.split('U_n = ')[1].split(', sedangkan')[0];good=all(calc(report,n=j)==U(j) for j in range(1,7));return [good,not good,False,False]
        if suf=='4-3':
            r=root(z[1]/z[0]);return match(z[0]*r**4)
        if suf=='4-4':
            U=arithmetic(z[0],(z[1]-z[0])/4);negative=next(j for j in range(1,100) if U(j)<0);return [False,False,False,int(re.findall(r'U_(\d+)',opts[3]['text'])[-1])==negative]
        if suf=='4-5':
            U=geometric(z[0],z[1]/z[0]);reports=re.findall(r'(Ayu|Bimo|Citra): U_n = ([^;]+?)(?=;|\. Siswa)',s);good=[name for name,f in reports if all(calc(f,n=j)==U(j) for j in range(1,7))]
            return [all(name in good for name in re.findall(r'Ayu|Bimo|Citra',o['text'])) and len(re.findall(r'Ayu|Bimo|Citra',o['text']))==len(good) for o in opts]
        if suf=='4-6':
            d=[z[i+1]-z[i] for i in range(len(z)-1)];return [len(set(d))>1,len(set(z[i+1]/z[i] for i in range(len(z)-1)))==1,len(set(d[i+1]-d[i] for i in range(len(d)-1)))==1,v[3][0]==z[-1]+d[-1]+(d[-1]-d[-2])]
        if suf=='4-7':
            d=(z[1]-z[0])/4;U=arithmetic(z[0]-2*d,d);return [v[0][0]==d,v[1][0]==U(1),all(calc(formula(opts[2]['text']),n=j)==U(j) for j in range(1,7)),v[3][0]==U(10)]
        if suf=='4-8':
            U=geometric(z[0],z[1]);return [U(2)>U(1) and U(3)>U(2),z[1]<0,v[2][0]==U(6),False]
        if suf=='4-9':
            groups=[nums(t) for t in re.findall(r'[PQR]: ([^;]+)',s)];p,q,r=groups;return [p[1]-p[0]==v[0][0],len(set(r[i+1]-r[i] for i in range(3)))==1,len(set(q[i+1]-q[i] for i in range(3)))==1]
        if suf=='4-10':
            U=geometric(z[0],z[1]/z[0]);return [U(10)<0,z[2]-z[1]!=z[1]-z[0],v[2][-1]==U(6)]
        if suf=='5-1':return [False,False,v[2][-1]==z[3]+z[1]-z[0],False]
        if suf=='5-2':
            U=arithmetic(z[0],z[1]);V=arithmetic(z[2],z[3]);return [V(int(j)-1)<=U(int(j)-1) and V(int(j))>U(int(j)) for j in [re.search(r'ke-(\d+)',o['text'])[1] for o in opts]]
        if suf=='5-3':
            # Symbols n and r are general identities; isolate the numeric a,r assignments.
            a=z[0];r=z[1]/z[0];answer=a*r**7
            return [v[0][-1]==answer,False,v[2][-1]==answer,False]
        if suf=='5-4':return [a[1]>a[0] and 0<a[1]/a[0]<1 for a in v]
        if suf=='5-5':
            a=z[0];r=1-z[1]/100;answer=a*r*r;return [v[i][0]==answer and 'Beta' in opts[i]['text'] for i in range(4)]
        if suf=='5-6':return [min(a)>0 and len(set(a[i+1]/a[i] for i in range(3)))==1 and 0<a[1]/a[0]<1 for a in v]
        if suf=='5-7':
            r=next(F(i) for i in range(1,11) if i**3==z[1]/z[0]);U=geometric(z[0]/r**2,r)
            ratio_reason=v[0][1]/v[0][2]==v[0][3]==r**3
            return [v[0][0]==r and ratio_reason,v[1][0]==U(1),all(calc(formula(opts[2]['text']).split('.')[0],n=j)==U(j) for j in range(1,7)),v[3][0]==U(8)]
        if suf=='5-8':
            a=z[0];d=z[1];r=1+z[2]/100;return [a+2*d==a*r*r,a+d==a*r,a*r*r>a+2*d,r==1]
        if suf=='5-9':
            U=arithmetic(z[0],z[1]-z[0]);return [v[0][0]==U(15),v[1][0]==U(21),all(U(j)%v[2][1]==v[2][0] for j in range(1,7))]
        if suf=='5-10':return [False,z[5]/z[4]==v[1][0],False]
        raise AssertionError(qid)
    # Indicator 13: reconstruct either S_n directly or a first term and difference/ratio.
    poly={'2-1','2-9','3-1','3-9','4-1','4-9','5-1','5-9'}
    if suf in poly:
        expr=re.search(r'S_n=([\d.,n()^*/+\- ]+)',s)[1].strip(' .,').replace(',)',')')
        S=lambda j:calc(expr,n=j)
        U=lambda j:S(j)-S(j-1)
    else:
        if suf in ('1-1','1-2','1-3','1-6','1-9','2-7','5-2','5-3','5-6','5-7','4-6','4-7'):
            # Skip a leading term count before the displayed sequence.
            seq=re.search(r'(?:\d+(?:\.\d{3})*(?:,\d+)?[,+]\s*){2,}\d+(?:\.\d{3})*',s)
            zz=nums(seq[0]);a=zz[0];d=zz[1]-a;r=zz[1]/a
        elif suf in ('1-7','2-2','2-3','2-6'):
            seq=re.search(r'(?:\d+[+]\s*){2,}\d+',s);zz=nums(seq[0]);a=zz[0];r=zz[1]/a;d=zz[1]-a
        elif suf=='1-4': a,d=z[0],z[1]
        elif suf=='1-5': a,d=z[1],z[2]
        elif suf=='1-8': a,d=z[1],-z[2]
        elif suf in ('1-10','2-8','2-10','3-7','3-10','4-10'):a,d=z[0],z[1]
        elif suf=='3-8':a,d=z[1],z[2]
        elif suf=='2-4':
            assert z[0]==5,(qid,'number of ribbon parts must stay five',z)
            a=z[1];r=root(root(z[2]/z[1]))
        elif suf=='2-5': a,d=z[0],z[1]
        elif suf=='3-2': d=(z[1]-z[0])/3;a=z[0]-2*d
        elif suf=='3-4': a=z[0];r=2
        elif suf=='3-5': a,d=z[0],z[1]
        elif suf=='3-6': r=next(F(i) for i in range(1,11) if i**3==z[1]/z[0]);a=z[0]/r
        elif suf=='4-2': a=2*z[1]/5-z[0];d=(z[0]-a)/4
        elif suf=='4-3': a=z[0];r=next(F(i) for i in range(1,11) if a*(1+i+i*i)==z[1])
        elif suf=='4-4': a,d=z[1],z[2]
        elif suf=='4-5':a,d=z[0],z[1]
        elif suf=='4-8':a,d=z[1],z[2]
        elif suf=='5-4': a=z[1];r=2
        elif suf=='5-5':a,d=z[0],z[1]
        elif suf=='5-8':a,d=z[2],z[3]
        elif suf=='5-10':a=z[0];r=2
        elif suf=='3-3':
            answer=sum(i for i in range(int(z[0])+1,int(z[1])) if i%z[2]==0);return match(answer)
        else: raise AssertionError(qid)
        geo=suf in ('1-7','2-2','2-3','2-4','2-6','3-4','3-6','4-3','4-6','5-2','5-4','5-7','5-10')
        if suf=='2-6': a=z[0];r=z[1]/z[0]
        U=geometric(a,r) if geo else arithmetic(a,-d if suf=='3-10' else d)
        S=lambda j:sum(U(i) for i in range(1,j+1))
    if qid.startswith('pg'):
        if suf=='1-1':return [a==[U(4),S(4)] for a in v]
        if suf in ('1-2','2-2','3-2','4-2'):return formulas(U,S,'S')
        if suf in ('1-3','1-4','2-3','2-4','4-3'):return match(S({'1-3':10,'1-4':8,'2-3':6,'2-4':5,'4-3':5}[suf]))
        if suf=='1-5':return match(S(10)-z[-1])
        if suf=='2-1':return match(U(5))
        if suf in ('2-5','3-5'):return [S(int(a[0])-1)<z[2]<=S(int(a[0])) for a in v]
        if suf=='3-1':return [a==[U(6),S(6)] for a in v]
        if suf=='3-4':return match(sum(U(j) for j in range(5,8)))
        if suf=='4-1':return formulas(U,S)
        if suf=='4-4':return [False,False,False,v[3]==[S(10),S(10)-10*z[3],10*z[3]]]
        if suf=='4-5':
            j=int(re.search(r'hari ke-(\d+)',s)[1]);return [v[0][0]==S(j) and v[0][1]==S(j+1) and S(j)<z[2]<=S(j+1),False,False,False]
        if suf=='5-1':
            reports=re.findall(r'(Ani|Budi|Cici) menjawab ('+NUMBER+')',s);winner=next(name for name,val in reports if number(val)==U(5));return [o['text'].startswith('Hanya '+winner+' yang benar;') for o in opts]
        if suf=='5-2':return [False,False,v[2][-2]==U(1)/2 and v[2][-1]==U(1),False]
        if suf=='5-3':return [a==[U(15),S(15)] for a in v]
        if suf=='5-4':return [False,v[1][0]==S(10),False,v[3]==[S(10),S(10)-10*z[2],10*z[2]]]
        if suf=='5-5':return [False,v[1][-2]==S(10) and S(10)<=z[3]<S(11),False,False]
        raise AssertionError(qid)
    if suf in ('1-6','1-7','1-9','2-6','2-9','3-9','4-9'):return claims(U,S)
    if suf=='1-8':return [v[0][0]==U(5),v[1][0]==S(5),v[2][0]==S(3),v[3][0]==U(4)+U(5)]
    if suf=='1-10':return [v[0][1]==S(7),S(7)>=v[1][0],S(7)>v[2][-1]]
    if suf=='2-7':
        count=(z[-1]-z[0])/(z[1]-z[0])+1;return [v[0][0]==count,v[1][0]==count,v[2][0]==S(int(count)),v[3][-1]==S(10)]
    if suf=='2-8':return [v[0][0]==U(12),v[1][0]==S(12),v[2][0]==S(12),v[3][-1]==S(5)]
    if suf=='2-10':return [v[0][0]==U(8),v[1][-1]==S(8),v[2][-1]==v[2][0]-S(8)]
    if suf=='3-6':return [v[0][0]==r,v[1][0]==U(1),all(calc(formula(opts[2]['text']),n=j)==S(j) for j in range(1,7)),v[3][0]==S(4)]
    if suf=='3-7':return claims(U,S)
    if suf=='3-8':return [v[0][0]==U(10),v[1][0]==S(10),v[2][-1]==S(5),v[3][-1]==S(10)-S(5)]
    if suf=='3-10':return [v[0][-1]==S(10),S(10)>=v[1][0],10*v[2][-1]-45*d>=v[2][0] and 10*(v[2][-1]-1)-45*d<v[2][0]]
    if suf=='4-6':return [all(calc(formula(opts[i]['text']),n=j)==S(j) for j in range(1,7)) for i in (0,1)]+[v[2][0]==S(4),v[3][0]==2*U(1)]
    if suf=='4-7':return [v[0]==[12,11],v[1][0]==S(12),z[-1]<S(12),v[3][0]==z[-1]-S(12)]
    if suf=='4-8':
        V=arithmetic(z[3],z[4]);T=sum(V(j) for j in range(1,13));return [v[0][-1]==S(12),v[1][-1]==T,v[2][0]==S(12)-T,v[3]==[U(12),V(12)]]
    if suf=='4-10':return [v[0][-1]==S(14),S(14)>=z[-1],v[2][-1]==z[-1]-S(14)]
    if suf=='5-6':
        reports=re.findall(r'S_n=([^dA-Za-z;,.]+(?:n[^dA-Za-z;,.]*)?)',s)
        # Independently check the two displayed formulas extracted between prose boundaries.
        aexpr=s.split('Andi menulis S_n=')[1].split(' dan Beni')[0];bexpr=s.split('Beni menulis S_n=')[1].split('. Pilih')[0]
        ag=all(calc(aexpr,n=j)==S(j) for j in range(1,7));bg=all(calc(bexpr,n=j)==S(j) for j in range(1,7));return [ag,bg,not bg,v[3][0]==U(1) and ag]
    if suf=='5-7':
        steps=s.split('S_6=')[1].split('. Pilih')[0].split('=')
        values=[calc(e) for e in steps]
        return [len(set(values+[S(6)]))==1,v[1][0]==S(5),v[2][0]==U(6),v[3][0]==S(6)]
    if suf=='5-8':return [v[0][-1]==S(12),z[0]<S(12),v[2][0]==S(12)-z[0],v[3][0]==S(12)]
    if suf=='5-9':return [False,all(calc(formula(opts[1]['text']),n=j)==U(j) for j in range(1,7)),False]
    if suf=='5-10':return [v[0][-1]==S(10),S(10)<z[-1],v[2][0]==S(10)-z[-1]]
    raise AssertionError(qid)


def function_model(qid,c):
    s,opts=c['stem'],c['options'];suf='-'.join(qid.split('-')[2:]);v=[nums(o['text']) for o in opts]
    def pairs(text):
        return [(a.strip(),b.strip()) for a,b in re.findall(r'\(([-\d ]+),\s*([-\dab c]+)\)',text)]
    def members(text):
        return {a.strip() for a in re.search(r'\{([^{}]+)\}',text)[1].split(',')}
    def named(name):return members(re.search(name+r'\s*=\s*\{[^}]+\}',s)[0])
    def is_function(ps,domain,codomain=None):
        return {a for a,b in ps}==domain and len(ps)==len(domain) and (codomain is None or all(b in codomain for a,b in ps))
    def defs():
        exprs=re.findall(r'[fgT]\(x\)\s*=\s*([\d.,x()^*/+\- ]+)',s)
        return [lambda x,e=e.split(', x')[0].strip(' .,'):calc(e,x=x) for e in exprs[:2]]
    if qid == 'mcma-11-1-7':
        constant = int(re.search(r'x² - (\d+)', s)[1])
        claims = [tuple(map(int, re.search(r'f\((-?\d+)\)=(-?\d+)', o['text']).groups())) for o in opts]
        assert claims[0][0] > 0 and claims[2][0] < 0
        assert all(x*x-constant > 0 for x, _ in claims)
        return [x*x-constant == answer for x, answer in claims]
    if qid == 'pg-11-2-4':
        coefficient, constant = map(int, re.search(r'f\(x\)=(\d+)x\+(\d+)', s).groups())
        subtract = int(re.search(r'g\(x\)=x-(\d+)', s)[1])
        arg = int(re.search(r'\(f∘g\)\((\d+)\)', s)[1])
        assert arg-subtract > 0
        return equal_options(opts, coefficient*(arg-subtract)+constant)
    if qid == 'kategori-11-3-9':
        names = re.findall(r'([A-Z])=\{', s)
        A, B = ({number(a) for a in named(name)} for name in names)
        assert len(A) == 3 and len(B) == 6
        assert all(x > 0 for x in A) and {y*y for y in B} == A
        functions = {(names[0], names[1]): all(sum(y*y == x for y in B) == 1 for x in A),
                     (names[1], names[0]): all(sum(y*y == x for x in A) == 1 for y in B)}
        x1, x2, image = map(int, re.search(r'karena (-?\d+) dan (-?\d+) dipasangkan dengan (\d+)', opts[2]['text']).groups())
        assert x1 in B and x2 in B and x1 != x2 and x1*x1 == x2*x2 == image
        out = []
        for option in opts:
            source, target = re.search(r'Relasi dari ([A-Z]) ke ([A-Z])', option['text']).groups()
            valid = functions[source, target]
            out.append(not valid if 'bukan fungsi' in option['text'] else valid)
        return out
    if suf=='1-2':return [members(o['text'])=={a for a,b in pairs(s)} for o in opts]
    if suf in ('1-3','3-3','2-3'):
        data=[(number(a),number(b)) for a,b in re.findall(r'f\(([-\d]+)\)\s*=\s*([-\d]+)',s)] if suf!='2-3' else [(number(a),number(b)) for a,b in pairs(s)]
        return [all(calc(formula(o['text']),x=a)==b for a,b in data) for o in opts]
    if suf=='1-4':
        f=defs()[0];arg=number(re.findall(r'f\(([-\d]+)\)',s)[0]);return equal_options(opts,f(arg))
    if suf=='1-5':
        f=defs()[0];slope=f(1)-f(0);return [False,slope>0,slope<0,slope==0]
    if suf=='1-6':
        ps=pairs(s);return [members(o['text'])=={p[i] for p in ps} for o,i in zip(opts,[0,0,1,1])]
    if suf=='1-10':
        f=defs()[0];return [f(number(re.search(r'f\(([-\d]+)\)',o['text'])[1]))==nums(o['text'])[-1] for o in opts[:2]]+[f(v[2][-1])==v[2][0]]
    if suf=='2-1':return [is_function(pairs(o['text']),named('A'),named('B')) for o in opts]
    if suf=='2-2':
        f=defs()[0];ends=nums(s.split('D =')[1])[:2];answer=sorted([f(0)]+[f(a) for a in ends]);return [nums(o['text'])==[answer[0],answer[-1]] for o in opts]
    if suf=='2-5':
        a,b=nums(s)[:2];return [all(calc(formula(o['text']),x=x)==a+b*x for x in (0,1,5)) for o in opts]
    if suf=='2-7':
        f,g=defs();out=[]
        for o in opts:
            order,x,y=re.search(r'\(([fg])∘[fg]\)\(([-\d]+)\)=([-\d]+)',o['text']).groups();x=number(x)
            out.append((f(g(x)) if order=='f' else g(f(x)))==number(y))
        return out
    if suf=='2-8':
        f=defs()[0];pole=number(re.search(r'x-('+NUMBER+')',s)[1]);return [v[0][0]==pole,False,v[2][0]==pole,False]
    if suf=='2-10':
        f=defs()[0];return [v[0][0]==f(0),f(v[1][0])==v[1][1],f(v[2][1])==v[2][0]]
    if suf=='3-1':
        domain=named('A');lines=s.splitlines()[1:4];ps0=[(a,b) for a,b in re.findall(r'([-\d]+) → ([-\d]+)',lines[0])]
        good={re.search(r'R_(\d+)',line)[1] for line,ps in zip(lines,[ps0,pairs(lines[1]),pairs(lines[2])]) if is_function(ps,domain,named('B'))}
        return [set(re.findall(r'R_(\d+)',o['text']))==good for o in opts]
    if suf=='3-2':
        f=defs()[0];domain=[number(a) for a in named('A')];return equal_options(opts,len({f(a) for a in domain}))
    if suf in ('3-4','4-3'):
        f,g=defs();args=[number(x) for x in re.findall(r'\)\(([-\d]+)\)',s)];return equal_options(opts,g(f(args[0]))-f(g(args[1])))
    if suf=='3-5':
        fixed,a,b=nums(s);first=int(fixed/(b-a))+1;return [int(re.search(r'ke-(\d+)',o['text'])[1])==first for o in opts]
    if suf=='3-6':
        f,g=defs();return [all(calc(formula(opts[0]['text']),x=x)==g(f(x)) for x in (0,1,2)),all(calc(formula(opts[1]['text']),x=x)==f(g(x)) for x in (0,1,2)),all(f(g(x))==g(f(x)) for x in (0,1,2)),v[3][-1]==g(f(2))-f(g(2))]
    if suf=='3-7':
        f,g=defs();x=(g(0)-f(0))/(f(1)-f(0)-g(1)+g(0));return [f(1)>f(0),g(1)>g(0),[number(a) for a in pairs(opts[2]['text'])[0]]==[x,f(x)],v[3][0]==x and f(x+1)>g(x+1)]
    if suf=='3-8':
        ps=[(number(a),number(b)) for a,b in re.findall(r'([-\d]+) → ([-\d]+)',s)];m=(ps[1][1]-ps[0][1])/(ps[1][0]-ps[0][0]);b=ps[0][1]-m*ps[0][0]
        return [all(calc(formula(opts[0]['text']),x=a)==b for a,b in ps),set(pairs(opts[1]['text']))=={(str(a),str(b)) for a,b in ps},members(opts[2]['text'])=={str(b) for a,b in ps},not all(m*x+b==y for x,y in ps)]
    if suf in ('3-10','4-8'):
        f=defs()[0];A=named('A');B=named('B');R={str(f(number(a))) for a in A}
        if suf=='3-10':return [R==B,str(v[1][0]) in B-R,len(R)==len(A)]
        return [members(opts[0]['text'])==R,R==B,False,len(R)==len(A)]
    if suf=='4-1':
        A=named('A');bad=[name for name,text in re.findall(r'([PQRS]) = (\{[^}]+\})',s) if not is_function(pairs(text),A,named('B'))];return [o['text'].startswith(', '.join(bad)+', karena') for o in opts]
    if suf=='4-2':
        f=defs()[0];lo,hi=nums(s.split('D =')[1]);return equal_options(opts,len({f(x) for x in range(int(lo),int(hi)+1) if f(x)>0}))
    if suf=='4-4':
        data=s.split('berturut-turut memiliki f(x) = ')[1].split('. Rani')[0];xs=nums(s.split('x = ')[1].split('berturut')[0]);ys=nums(data);expr=s.split('Doni menyatakan f(x) = ')[1].split('. Penilaian')[0];doni=lambda x:calc(expr,x=x)
        return [False,False,False,all(doni(x)==y for x,y in zip(xs,ys))]
    if suf=='4-5':
        a,b=nums(s)[:2];return [False,False,v[2][1:3]==[a+b,a] and v[2][-2:]==[b,a-b],False]
    if suf=='4-6':return [o['text'].strip().startswith('y =') for o in opts]
    if suf=='4-7':
        pts=[(number(a),number(b)) for a,b in re.findall(r'f\(([-\d]+)\) = ([-\d]+)',s)];a=(pts[1][1]-pts[0][1])/(pts[1][0]-pts[0][0]);b=pts[0][1]-a*pts[0][0]
        return [v[0]==[a,b],a*v[1][0]+b==v[1][1],a*v[2][0]+b==v[2][1],a<0]
    if suf=='4-9':
        f=defs()[0];return [f(1)<f(0),v[1]==[0,f(0)],f(v[2][0])==v[2][1]]
    if suf=='4-10':
        f=defs()[0];return [True,False,f(v[2][0])==v[2][1]]
    if suf=='5-1':return [False,False,len({a for a,b in pairs(s)})==len(pairs(s)),False]
    if suf=='5-2':
        f=defs()[0];D={number(a) for a in named('D')};R={str(f(a)) for a in D};return [False,members(opts[1]['text'])==R,members(opts[2]['text'])==R,members(opts[3]['text'])==R]
    if suf=='5-3':
        f,g=defs();arg=number(re.search(r'\(f ∘ g\)\(([-\d]+)\)',s)[1]);return [False,False,v[2][-1]==f(g(arg)),v[3][-1]==f(g(arg))]
    if suf=='5-4':
        a=nums(s.split('diagram panah:')[1].split('. Dua')[0]);ps=list(zip(a[::2],a[1::2]));nia=defs()[0]
        reason_value=number(opts[0]['text'].split('bukan ')[1])
        return [all(nia(x)==y for x,y in ps) and reason_value==nia(0),False,False,False]
    if suf=='5-5':
        a,b=nums(s)[:2];return [b>0 and nums(opts[0]['text'])==[0,a],False,b<0,a==0]
    if suf=='5-7':
        x,y=[number(a) for a in re.search(r'f\(([-\d]+)\) = ([-\d]+)',s).groups()];p=(y-x*x)/x;f=lambda x:x*x+p*x
        return [v[0][0]==p,f(v[1][0])==v[1][1],f(v[2][0])==v[2][1],f(v[3][0])==v[3][1]]
    if suf=='5-8':
        a,b=nums(s)[:2];return [False,b>0,a+b*v[2][0]==v[2][1],True]
    if suf=='5-9':
        ps=re.findall(r'f\((\d+)\) = ([ab])',s);valid=is_function(ps,named('A'),named('B'));return [valid,False,v[2][0]==len(named('B'))**len(named('A'))]
    if suf=='5-10':
        f,g=defs();return [f(v[0][0])==g(v[0][0]),g(v[1][0])<f(v[1][0]),g(1)-g(0)>f(1)-f(0)]
    raise AssertionError(qid)


def check_math(qid,c):
    indicator=int(qid.split('-')[1])
    if indicator==11: expected=function_model(qid,c)
    elif indicator in (12,13): expected=sequence_model(qid,c)
    elif indicator==14: expected=angle_model(qid,c)
    elif indicator==15: expected=geometry_model(qid,c)
    else: raise AssertionError(('oracle missing',qid))
    flags(c['options'],expected)
