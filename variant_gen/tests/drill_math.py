"""Independent stdlib oracle. Never evaluates generator expressions or reads their keys."""
import re
from collections import Counter
from fractions import Fraction
from statistics import median

NUMBER = r'(?<!\w)-?\d+(?:\.\d{3})*(?:,\d+)?(?:/\d+)?'


def nums(text):
    return [Fraction(s.replace('.','').replace(',','.')) for s in re.findall(NUMBER,text)]


def stats(data):
    counts = Counter(data)
    modes = {x for x,n in counts.items() if n == max(counts.values())}
    return dict(mean=Fraction(sum(data),len(data)), median=median(data),
                range=max(data)-min(data), min=min(data), max=max(data), modes=modes)


def rounded(value):
    value=Fraction(value)
    whole,remainder=divmod(abs(value.numerator)*100,value.denominator)
    return Fraction((whole+(2*remainder>=value.denominator))*(-1 if value<0 else 1),100)


def check_math(test, orig, result):
    q = orig['id']; v = result.values; cand = result.cand; opts = cand['options']
    flags = None
    # Dataset variables are checked against the rendered stimulus before using them.
    if 'x1' in v:
        data = [v['x'+str(i)] for i in range(1,30) if 'x'+str(i) in v]
        actual = stats(data)
        for n in data: test.assertIn(n, nums(cand['stem']), q)
        if q in ['pg-20-2-5','pg-21-2-3']:
            answer = 5*v['targetmean']-sum(data)
            flags = [nums(o['text'])[0] == answer for o in opts]
        elif q == 'pg-21-3-2':
            after = stats([n+v['increment'] for n in data])
            flags = [after['mean']==actual['mean'] and after['median']==actual['median'],
                     after['mean']-actual['mean']==nums(opts[1]['text'])[0] and after['median']-actual['median']==nums(opts[1]['text'])[0],
                     after['range']-actual['range']==nums(opts[2]['text'])[0], False]
        elif orig['format']=='PG':
            kind = ('range' if 'Jangkauan' in cand['stem'] else 'median' if 'Median' in cand['stem'] else
                    'mode' if 'Modus' in cand['stem'] else 'mean')
            flags = [nums(o['text'])[0] in actual['modes'] if kind=='mode' else nums(o['text'])[0]==actual[kind] for o in opts]
        else:
            flags=[]
            for o in opts:
                t=o['text'].lower()
                if 'dua modus' in t: flags.append(len(actual['modes'])==2); continue
                n=nums(t)[0]
                if 'modus' in t: flags.append(n in actual['modes']); continue
                kind=('median' if 'median' in t else 'range' if 'jangkauan' in t or 'range' in t or 'selisih' in t else
                      'max' if 'terbesar' in t else 'min' if 'terkecil' in t else 'mean')
                flags.append(n == rounded(actual[kind]) if kind=='mean' else n == actual[kind])
    elif 'a1' in v:
        a=[v['a'+str(i)] for i in range(1,6)];b=[v['b'+str(i)] for i in range(1,6)]
        for n in a+b:test.assertIn(n,nums(cand['stem']),q)
        aa,bb=stats(a),stats(b)
        am,bm=aa['mean'],bb['mean'];ad,bd=aa['median'],bb['median'];ar,br=aa['range'],bb['range']
        def claim(index): return next(iter(nums(opts[index]['text'])),None)
        flags={
          'mcma-20-3-6':[am==bm,ad==bd,br>ar,max(b)>max(a)],
          'pg-21-3-3':[ar>br,ar==br,ad>bd,br>ar],
          'kategori-21-3-10':[am==claim(0),bm==claim(1),bd==claim(2),ar>br],
          'pg-22-1-2':[ar>br,ar==br,br>ar,False],
          'pg-22-1-3':[ad==bd,ad>bd,bd>ad,am>bm],
          'pg-22-1-5':[am>bm,bm>am,am==bm,ad>bd],
          'kategori-22-1-9':[am==bm,ad==bd,ar>br,br==claim(3)],
          'kategori-22-1-10':[am==bm,ad>bd,br>ar,ar==claim(3)],
          'pg-22-2-1':[am>bm and ar>br,bm>am and br<ar,am==bm and br>ar,am==bm and ar==br],
          'pg-22-2-2':[am==bm and br>ar,am>bm and br<ar,bm>am and ar>br,am==bm and ar==br],
          'pg-22-2-4':[am>bm,am==bm and br>ar,bm<am,ar==br],
          'mcma-22-2-6':[am==bm,ad==bd,ar<br,br<ar],
          'mcma-22-2-7':[ad==bd,am>bm,br>ar,False],
          'kategori-22-2-9':[am==bm,ad==bd,ar>br,br>ar],
          'kategori-22-2-10':[ad==bd,am>bm,br>ar,ar>br],
          'pg-22-3-1':[am>bm and ar>br,bm>am and br<ar,am==bm and br>ar,am==bm and ar==br],
          'pg-22-3-3':[am==bm and ad==bd and br>ar,bm>am,bd>ad,ar>br],
          'pg-22-3-4':[am>bm,ad>bd,ar>br,am==bm and ad==bd and br>ar],
          'mcma-22-3-6':[am==bm,ad>bd,claim(2) in bb['modes'],ar==br],
          'mcma-22-3-7':[am==bm,ad==bd,br>ar,br>ar],
          'kategori-22-3-9':[ad==bd,am==bm,ar>br,br>ar],
          'kategori-22-3-10':[am==bm,ad>bd,br>ar,ar>br],
        }[q]
        if q=='mcma-22-2-7': test.assertEqual(len(bb['modes']),len(b),'B has no unique mode')
    elif q=='pg-22-3-2':
        flags=[v['ma']>v['mb'],v['ma']==v['mb'] and v['rb']>v['ra'],v['mb']<v['ma'],v['ra']==v['rb']]
    elif q.startswith(('pg-20','mcma-20','kategori-20')):
        if q=='pg-20-1-3':
            days=[v[n] for n in ['mon','tue','wed','thu','fri']];flags=[days[i]==max(days) for i in [0,1,2,4]]
        elif q=='pg-20-3-1':
            a,b,c,d=[v[n] for n in 'abcd'];total=a+b+c+d
            flags=[d>total/2,b>max(a,c,d),a==b==0,a==c]
        elif q=='pg-20-3-2':
            a,b,c,d=[v[n] for n in ['jan','feb','mar','apr']];flags=[a<b<c<d,a>b>c>d,a<b<c and c>d,a==b==c==d]
        elif q=='pg-20-2-3':
            answer=Fraction(v['last']-v['first'],v['first'])*100;flags=[nums(o['text'])[0]==answer for o in opts]
        else:
            k=v['k']
            if q=='pg-20-1-2':flags=[nums(o['text'])[0]==sum([4*k,6*k,3*k,7*k,5*k]) for o in opts]
            elif q=='pg-20-2-4':flags=[nums(o['text'])[0]==Fraction(40,100)*200*k for o in opts]
            elif q=='pg-20-3-4':flags=[nums(o['text'])[0]==Fraction(25+20,100)*360*k for o in opts]
            elif q=='mcma-20-1-7':flags=[20*k==max([15*k,20*k,10*k,5*k]),nums(opts[1]['text'])[0]==20*k,10*k==2*5*k,5*k==15*k]
            elif q=='mcma-20-1-8':flags=[50*k==max([30*k,25*k,40*k,35*k,50*k]),40*k>25*k,35*k<30*k,nums(opts[3]['text'])[0]==50*k-25*k]
            elif q=='mcma-20-2-8':flags=[20*k==max([5*k,15*k,20*k,10*k]),nums(opts[1]['text'])[0]==50*k,nums(opts[2]['text'])[-1]==100*Fraction(10*k,50*k),5*k==max([5*k,15*k,20*k,10*k])]
            elif q=='kategori-20-2-9':flags=[55*k==max([30*k,45*k,40*k,55*k,30*k]),45*k>40*k,nums(opts[2]['text'])[0]==55*k-30*k,nums(opts[3]['text'])[0]==sum([30*k,45*k,40*k,55*k,30*k])/5]
            elif q=='mcma-20-3-7':flags=[50*k==100*k/2,20*k==20*k,nums(opts[2]['text'])[0]==100*k-50*k,False]
            elif q=='kategori-20-3-9':flags=[36*k==max([24*k,36*k,20*k,10*k,10*k]),nums(opts[1]['text'])[0]==100*Fraction(24*k,100*k),nums(opts[2]['text'])[0]==24*k-20*k,10*k==10*k,nums(opts[4]['text'])[0]==100*k]
            elif q=='kategori-20-3-10':flags=[nums(opts[0]['text'])[0]==35*200*k/100,nums(opts[1]['text'])[0]==(25+20)*200*k/100,nums(opts[2]['text'])[0]==15*200*k/100,35==7*5,35+25+20==nums(opts[4]['text'])[0]]
    elif q.startswith(('pg-23','mcma-23','kategori-23')):
        if q in ['pg-23-1-3','pg-23-2-1','pg-23-2-2']:
            counts=[v['c'+str(i)] for i in range(3) if 'c'+str(i) in v]
            target={'pg-23-1-3':0,'pg-23-2-1':1,'pg-23-2-2':2}[q];answer=Fraction(counts[target],sum(counts))
            flags=[nums(o['text'])[0]==answer for o in opts]
        elif q in ['pg-23-1-4','pg-23-1-5','pg-23-2-5','pg-23-3-3']:
            test.assertTrue(0<=v['observed']<=v['trials']);answer=Fraction(v['observed'],v['trials']);flags=[nums(o['text'])[0]==answer for o in opts]
        elif q in ['pg-23-2-3','pg-23-2-4','pg-23-3-4']:
            p=Fraction(1,6) if q=='pg-23-2-3' else Fraction(1,2) if q=='pg-23-2-4' else Fraction(v['red'],v['red']+v['blue'])
            answer=v['trials']*p;flags=[nums(o['text'])[0]==answer for o in opts]
        elif q=='pg-23-3-1':
            freq=Fraction(v['observed'],v['trials']);flags=[freq>Fraction(1,6),freq==Fraction(1,6),freq<Fraction(1,6),False]
        elif q in ['mcma-23-1-6','kategori-23-1-9']:
            faces=list(range(1,7));flags=[]
            for o in opts:
                t=o['text'];numbers=nums(t);claim=numbers[-1]
                event=([n for n in faces if n%2==0] if 'genap' in t else
                       [n for n in faces if n<numbers[0]] if 'kurang dari' in t else
                       [n for n in faces if n>numbers[0]] if 'lebih dari' in t else [n for n in faces if n==numbers[0]])
                flags.append(Fraction(len(event),6)==claim)
        elif q in ['mcma-23-1-7','mcma-23-2-7']:
            counts={n:v[n] for n in ['red','white','blue','green'] if n in v};total=sum(counts.values());flags=[]
            for o in opts:
                t=o['text'];n=(total-counts['red'] if 'bukan merah' in t else total-counts['green'] if 'bukan hijau' in t else
                              counts['red'] if 'merah' in t else counts['white'] if 'putih' in t else counts['blue'] if 'biru' in t else counts['green'])
                flags.append(nums(t)[0]==Fraction(n,total))
        elif q in ['mcma-23-1-8','mcma-23-2-6']:
            flags=[]
            for o in opts:
                ns=nums(o['text']);observed=ns[1] if 'genap' not in o['text'] else ns[0]
                test.assertTrue(0<=observed<=v['trials']);flags.append(Fraction(observed,v['trials'])==ns[-1])
        elif q in ['mcma-23-2-8','mcma-23-3-6']:
            flags=[]
            for o in opts:
                t=o['text'];ns=nums(t);faces=[n for n in range(1,7) if n%2==0] if 'genap' in t else [n for n in range(1,7) if n>4] if 'lebih dari' in t else [int(ns[0])]
                flags.append(ns[-1]==v['trials']*Fraction(len(faces),6))
        elif q in ['kategori-23-1-10','kategori-23-2-9']:
            freq=Fraction(v['observed'],v['trials']);flags=[nums(opts[0]['text'])[0]==freq,nums(opts[1]['text'])[0]==freq,True,False]
        elif q=='kategori-23-2-10':
            freq=Fraction(v['observed'],v['trials']);flags=[nums(opts[0]['text'])[0]==freq,nums(opts[1]['text'])[0]==rounded(freq),nums(opts[2]['text'])[0]==Fraction(1,2),True]
        elif q=='kategori-23-3-10':
            theoretical=Fraction(v['red'],v['red']+v['white']);freq=Fraction(v['observed'],v['trials']);flags=[nums(opts[0]['text'])[0]==theoretical,nums(opts[1]['text'])[0]==freq,nums(opts[2]['text'])[0]==freq,False]
    test.assertIsNotNone(flags, 'Missing oracle: '+q)
    test.assertEqual([o['correct'] for o in opts],flags,q)
    test.assertEqual(sum(flags),sum(o['correct'] for o in orig['options']),q)
