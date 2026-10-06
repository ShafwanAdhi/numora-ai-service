"""Independent Decimal/Fraction oracle: reads rendered operands, never config values."""
import re
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction as F
from drill_1_2_math import calc, number, numbers

def rounded(value, places=0):
    with localcontext() as context:
        context.prec=50
        if isinstance(value,F): value=Decimal(value.numerator)/Decimal(value.denominator)
        return F(Decimal(value).quantize(Decimal(10)**-places,rounding=ROUND_HALF_UP))

def root(value):
    with localcontext() as context:
        context.prec=50
        return Decimal(int(value)).sqrt()

def roots(text):return [int(x) for x in re.findall(r'sqrt\(\s*(\d+)\s*\)',text)]

def check_math(original,candidate):
    qid=original['id'];kind,_,level,num=qid.split('-');level=int(level);num=int(num)
    stem=candidate['stem'];options=candidate['options'];expected={};truth=[]
    def claims(entries):expected.update(entries)
    if qid in ['pg-3-1-1','pg-3-2-1','pg-3-3-1']:
        value=number(re.search(r'sebanyak ([\d.]+)',stem)[1]);thousand=rounded(value/1000)*1000
        claims([('Bilangan',value),('Pembulatan ribuan',thousand)])
        if level==3:
            hundred=rounded(value/100)*100;expected['Pembulatan ratusan']=hundred
            analyses={label:(number(a),number(b))==(thousand,hundred) for label,a,b in re.findall(
                r'Analisis (I+|IV): Laporan Dinas = ([\d.]+) orang, Laporan Internal = ([\d.]+) orang',stem)}
            truth=[analyses[re.search(r'Analisis (I+|IV)$',op['text'])[1]] for op in options]
        else:truth=[numbers(op['text'])[0]==thousand for op in options]
    elif qid=='pg-3-1-4':
        value=roots(stem)[0];answer=rounded(root(value),1)
        truth=[numbers(op['text'])[0]==answer for op in options]
        claims([('Akar radikan',value),('Pembulatan persepuluhan',answer)])
    elif num==6:
        lines={roman:text for roman,text in re.findall(r'\(([iv]+)\) ([^\n]+)',stem)}
        decimal_values=numbers(lines['i']);places=1 if 'satu tempat' in lines['i'] else 2
        decimal_answer=rounded(decimal_values[0],places)
        square=roots(lines['ii'])[0];square_answer=rounded(root(square),1)
        interval_line=next(text for text in lines.values() if 'berada di antara' in text)
        rad=roots(interval_line)[0];lo,hi=numbers(interval_line)[-2:]
        interval_truth=Decimal(lo.numerator)/Decimal(lo.denominator)<root(rad)<Decimal(hi.numerator)/Decimal(hi.denominator)
        multiplication=next(text for text in lines.values() if '\u00d7' in text)
        a,b,out=map(number,re.search(r'([\d.]+)\u00d7([\d.]+).*?adalah ([\d.]+)',multiplication).groups())
        product=rounded(a/(10 if 'puluhan/ratusan' in multiplication else 100))*(10 if 'puluhan/ratusan' in multiplication else 100)*rounded(b/100)*100
        statement_truth={'i':decimal_values[-1]==decimal_answer,'ii':numbers(lines['ii'])[-1]==square_answer}
        for label,text in lines.items():
            if 'berada di antara' in text:statement_truth[label]=interval_truth
            elif '\u00d7' in text:statement_truth[label]=out==product
        truth=[statement_truth[re.search(r'\(([iv]+)\)',op['text'])[1]] for op in options]
        floor_tenth=F(int(root(rad)*10),10)
        claims([('Pembulatan desimal',decimal_answer),('Pembulatan akar',square_answer),('Batas bawah akar',floor_tenth),
            ('Batas atas akar',floor_tenth+F(1,10)),('Estimasi perkalian',product)])
    elif num==7:
        a,b,c=roots(stem);answers=[rounded(root(a),1),rounded(root(b),1),rounded(root(c))]
        for op in options:
            text=op['text'];index=0 if ('Akuarium P' in text or 'Sampel 1' in text) else 1 if ('Akuarium Q' in text or 'Sampel 2' in text) else 2
            echoed=roots(text)
            if echoed:assert echoed==[[a,b,c][index]],(qid,text,[a,b,c][index])
            truth.append(numbers(text)[-1]==answers[index])
        claims(zip(['Rusuk pertama','Rusuk kedua','Rusuk ketiga'],answers))
    elif kind=='kategori' and num==9:
        a,b,c=numbers(stem);ra,rb,rc=[rounded(x,1) for x in (a,b,c)]
        assert numbers(options[0]['text'])[0]==a
        assert numbers(options[1]['text'])[0]==b
        truth=[numbers(options[0]['text'])[-1]==ra,numbers(options[1]['text'])[-1]==rounded(b),numbers(options[2]['text'])[-1]==ra+rb+rc]
        claims([('Bahan pertama',ra),('Bahan kedua satuan',rounded(b)),('Bahan kedua persepuluhan',rb),('Bahan ketiga',rc),('Total',ra+rb+rc)])
    elif num==10:
        a,b=roots(stem);ra=rounded(root(a),1);ia=rounded(root(a));ib=rounded(root(b));result=ib-ia if level==2 else ia+ib
        assert roots(options[0]['text'])==[a]
        assert roots(options[1]['text'])==[b]
        if level==1:
            with localcontext() as context:
                context.prec=50
                total=root(a)+root(b)
                assert abs(total-(total.to_integral_value(rounding='ROUND_FLOOR')+Decimal('0.5')))>Decimal('1e-40')
                assert rounded(total)==result,(qid,a,b,result,total)
        truth=[numbers(options[0]['text'])[-1]==ra,numbers(options[1]['text'])[-1]==ib,numbers(options[2]['text'])[-1]==result]
        claims([('Akar pertama persepuluhan',ra),('Akar pertama satuan',ia),('Akar kedua satuan',ib),('Estimasi',result)])
    elif qid in ['pg-3-2-5','pg-3-3-2']:
        a,b=roots(stem);answers=[rounded(root(a),1),rounded(root(b),1)]
        truth=[numbers(op['text'])==answers for op in options]
        claims(zip(['Kawat pertama','Kawat kedua'],answers))
    elif qid=='pg-3-3-5':
        a,b=roots(stem);ia,ib=rounded(root(a)),rounded(root(b));answer=ib-ia
        truth=[numbers(op['text'])[0]==answer for op in options]
        claims([('Papan X',ia),('Papan Y',ib),('Selisih',answer)])
    elif qid=='mcma-3-1-8':
        a,b,c=numbers(stem);ra,rb,rc=rounded(a/10)*10,rounded(b),rounded(c);answer=ra*rb/rc
        for index,op in enumerate(options):
            values=numbers(op['text'])
            if index==0:truth.append(values==[rounded(a),rounded(b),rounded(c)])
            elif index==1:truth.append(values==[ra,rb,rc])
            else:truth.append(values[0]==answer)
        claims([('Pembilang pertama',ra),('Pembilang kedua',rb),('Penyebut',rc),('Estimasi',answer),('Hasil riil',rounded(a*b/c,2))])
    elif qid=='pg-3-3-4':
        real_line=re.search(r'Hitungan Riil:([^\n]+)',stem)[1]
        first,intermediate,shown=re.split('=|\u2248',real_line)
        real=calc(first).scalar();assert calc(intermediate).scalar()==real
        assert number(shown)==rounded(real,2)
        analyses={}
        for label,line in re.findall(r'Analisis (I+): Membulatkan menjadi ([^\n]+)',stem):
            chain=line.split('=');value=calc(chain[0]).scalar()
            assert all(calc(piece).scalar()==value for piece in chain[1:])
            analyses[label]=value
        closer=min(analyses,key=lambda label:abs(analyses[label]-real))
        # Options include causal claims: the final "all round up" reason is false.
        for op in options:
            text=op['text'];label=re.search(r'Analisis (I+)',text)[1]
            causal='sangat dekat' in text
            if causal:
                values=numbers(text);a=numbers(first)[0]
                assert values==[rounded(a/100)*100,a,analyses[label],rounded(real,2)]
            truth.append(label==closer and causal)
        claims([('Hasil riil',rounded(real,2)),('Analisis I',analyses['I']),('Analisis II',analyses['II'])])
    elif qid=='mcma-3-3-8':
        a,p,b,q=numbers(stem.split('\n')[0]);real=a*p+b*q;methods={};operands={}
        for label,line in re.findall(r'Metode (I+): ([^\n]+)',stem):
            chain=line.split('=');value=calc(chain[0]).scalar()
            assert all(calc(piece).scalar()==value for piece in chain[1:])
            methods[label]=value;operands[label]=numbers(chain[0])
        all_up=all(x>y for x,y in zip(operands['I'],[a,p,b,q]))
        truth=[abs(methods['II']-real)<abs(methods['I']-real),all_up and numbers(options[1]['text'])[-1]==methods['I'],
            real<methods['I'] and numbers(options[2]['text'])[-1]==methods['I'],real<methods['II'] and numbers(options[3]['text'])[-1]==methods['II']]
        claims([('Total riil',real),('Metode I',methods['I']),('Metode II',methods['II'])])
    else:raise AssertionError('uncovered '+qid)
    assert [op['correct'] for op in options]==truth,(qid,truth,options)
    explanation=candidate['explanation'];assert explanation.endswith('.')
    parts=explanation[:-1].split('; ')
    assert len(parts)==len(expected),(qid,explanation,expected)
    actual={}
    for part in parts:
        assert part.count('=')==1,part
        label,value=part.split('=');assert label not in actual
        assert re.fullmatch(r'-?\d+(?:\.\d{3})*(?:,\d+)?',value),value
        actual[label]=number(value)
    assert actual==expected,(qid,actual,expected)
