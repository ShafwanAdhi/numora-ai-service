"""Numeric families and rendered-text mathematical oracle for indicators 8–9."""
import ast
import re
from build_drill_1_5_level45_batch1 import Author


def author(e):
    e = dict(e)
    e['source_projection'] = dict(e.get('source_projection_resolved') or e['source_projection'])
    e['source_projection'].setdefault('format', e['format'])
    a = Author(e)
    # Literal LaTeX unit group must survive placeholder rendering.
    a.variables['m'] = dict(gen='derived', expr="'{m}' if k == 0 else 'm'")
    i, l, n = a.i, a.l, a.n
    def replace(old, expression):
        def fragment(node):
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.BinOp):
                return fragment(node.left) + fragment(node.right)
            expr = ast.unparse(node.args[0])
            return a.var(expr, str(eval(expr, {}, {'k': 0})))
        token = fragment(ast.parse(expression, mode='eval').body)
        a.stem = a.stem.replace(old, token)
        a.options = [t.replace(old, token) for t in a.options]
    if (i,l,n) == (8,4,1):
        a.allnums({'550.000':'100000+18000*(25+k)', '100.000':'100000', '18.000':'18000',
                   '24':'24+k', '25':'25+k', '36':'floor((200000+18000*(25+k))/18000)'})
        exp = 'Biaya tetap ditambah biaya paket tidak boleh melebihi anggaran: 18000n+100000 ≤ [[100000+18000*(25+k)]]. Maksimum [[25+k]] paket; paket berikutnya melampaui anggaran. A memakai batas ketat, C mengurangi biaya tetap, D membalik batas; hanya B benar.'
    elif (i,l,n) == (8,4,9):
        a.allnums({'72':'72+k/2','75':'75+k/2','216':'216+3*k/2','80':'80+k/2','85':'85+k/2'})
        exp = 'Total tiga ujian [[216+3*k/2]], sehingga (total+y)/4 ≥ [[75+k/2]]. Batas minimum [[84+k/2]], bukan [[80+k/2]]. Nilai [[85+k/2]] memenuhi batas. Pernyataan 1 dan 3 benar, 2 salah.'
    elif (i,l,n) == (8,5,2):
        a.allnums({'7':'7+k','19':'19+4*k','4':'4+k'})
        exp = 'Kurangi kedua ruas dengan [[7+k]], lalu bagi -3: x ≥ -[[4+k]]. Lingkaran penuh dan panah kanan milik Gina benar. Fajar salah pada lingkaran dan arah; batas positif juga salah. Hanya D benar.'
    elif (i,l,n) == (8,5,8):
        a.allnums({'70':'70+k/4','75':'75+k/4','80':'80+k/4','78':'78+k/4','225':'225+3*k/4',
                   '87':'87+k/4','90':'90+k/4','85':'85+k/4'})
        exp = 'Total tiga nilai [[225+3*k/4]]. Syarat (total+x)/4 ≥ [[78+k/4]] memberi x ≥ [[87+k/4]]. Nilai [[90+k/4]] memenuhi batas; [[85+k/4]] tidak. A, B, C benar; D salah.'
    elif (i,l,n) == (9,4,2):
        a.allnums({'190.000':'190000+7000*k','220.000':'220000+9000*k',
                   '10.000':'10000+1000*k','15.000':'15000+1000*k','20.000':'20000+1000*k','25.000':'25000+1000*k'})
        exp = 'Dengan d harga dewasa dan a harga anak: 2d+3a=[[190000+7000*k]], 4d+a=[[220000+9000*k]]. Eliminasi memberi d=[[47000+2000*k]], a=[[32000+1000*k]]. Selisih [[15000+1000*k]], hanya B benar.'
    elif (i,l,n) == (9,4,9):
        a.allnums({'42':'42+4*k','21':'21+2*k','15':'15+k','104':'(13+k)*(8+k)'})
        exp = 'Setengah keliling [[21+2*k]], selisih 5. Panjang [[13+k]], lebar [[8+k]], luas [[(13+k)*(8+k)]]. Model dan luas benar; klaim panjang [[15+k]] salah. Pernyataan 1 dan 3 benar.'
    elif (i,l,n) == (9,5,6):
        replace('3x-y=5', "'3x-y='+str(5+2*k)")
        replace('x+2y=11', "'x+2y='+str(11+3*k)")
        replace('(3,4)', "'('+str(3+k)+','+str(4+k)+')'")
        for j, value in enumerate((3,2,4)):
            a.options[j] = a.options[j].replace('$'+str(value)+'$', '$'+a.var(str(value)+'+k', str(value))+'$')
        exp = 'Eliminasi y menghasilkan 7x=[[21+7*k]], jadi x=[[3+k]]. Substitusi memberi y=[[4+k]], bukan [[2+k]]. Determinan 7 tidak nol, pasangan ([[3+k]],[[4+k]]) titik potong tunggal. A, C, D benar.'
    elif (i,l,n) == (9,5,8):
        for old, expr in [('x-y=2',"'x-y='+str(2+k)"),('2x-2y=4',"'2x-2y='+str(4+2*k)"),
                          ('x+y=5',"'x+y='+str(5+k)"),('x+y=9',"'x+y='+str(9+k)"),
                          ('2x+y=7',"'2x+y='+str(7+3*k)"),('x-3y=-7',"'x-3y='+str(-7-2*k)"),
                          ('$(5,9)$',"'$('+str(5+k)+','+str(9+k)+')$'"),('$(2,3)$',"'$('+str(2+k)+','+str(3+k)+')$'")]:
            replace(old,expr)
        exp = 'I: persamaan kedua dua kali persamaan pertama, sehingga berimpit dan solusi tak hingga. II: ruas kiri sama tetapi konstanta [[5+k]] dan [[9+k]] berbeda, maka sejajar tanpa solusi. III: determinan -7 tidak nol, solusi ([[2+k]],[[3+k]]) memenuhi kedua persamaan. A, C, D benar; B salah.'
    else:
        raise ValueError((i,l,n))
    a.exp = a.explanation(exp)
    return a


_NUM = r'-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?'
def numbers(text):
    return [float(t.replace('.', '').replace(',', '.')) for t in re.findall(_NUM, text)]


def check_math(qid, candidate):
    """Assert option truth using only the displayed stem/options."""
    _, i, l, n = qid.split('-')
    key = tuple(map(int,(i,l,n)))
    s = candidate['stem']; opts = candidate['options']; t = [o['text'] for o in opts]
    if key == (8,4,1):
        budget,fixed,price = numbers(s)[:3]
        maximum = int((budget-fixed)//price)
        truth=[]
        for text in t:
            vals=numbers(text)
            truth.append(vals == [price,fixed,budget,maximum] and '+' in text and '≤' in text)
    elif key == (8,4,9):
        count,avg,total,target,_ = numbers(s)
        minimum=total*target-count*avg
        v=numbers(t[0]); claim=numbers(t[1])[-1]; score=numbers(t[2])[0]
        truth=[v == [count*avg,total,target] and '≥' in t[0], abs(claim-minimum)<1e-5, (count*avg+score)/total >= target-1e-5]
        assert all(0 <= z <= 100 for z in [avg,target,minimum,claim,score])
    elif key == (8,5,2):
        const,coef,rhs,left,right=numbers(s)
        bound=(rhs-const)/coef
        assert abs(left-bound)<1e-5 and abs(right-bound)<1e-5
        truth=[False,False,numbers(t[2])[-1] == bound, 'Gina benar' in t[3] and abs(numbers(t[3])[0]-bound)<1e-5 and '≥' in t[3]]
    elif key == (8,5,8):
        total,count,a,b,c,again,target,_=numbers(s)
        minimum=total*target-a-b-c
        v=numbers(t[0]); claim=numbers(t[1])[-1]; score=numbers(t[2])[0]; bad=numbers(t[3])[-1]
        truth=[all(abs(x-y)<1e-5 for x,y in zip(v,[a+b+c,total,target])) and '≥' in t[0],abs(claim-minimum)<1e-5,score>=minimum-1e-5,bad>=minimum-1e-5]
        assert all(0 <= z <= 100 for z in [a,b,c,target,minimum,score,bad])
    elif key == (9,4,2):
        a,b,c,d,e,f,_,_=numbers(s)
        adult=(c*e-b*f)/(a*e-b*d); child=(a*f-c*d)/(a*e-b*d)
        truth=[abs(numbers(x)[0]-(adult-child))<1e-5 for x in t]
    elif key == (9,4,9):
        perimeter,diff=numbers(s); length=(perimeter/2+diff)/2; width=length-diff
        model=numbers(t[0]); truth=[model==[perimeter/2,diff],numbers(t[1])[0]==length,numbers(t[2])[0]==length*width]
    elif key == (9,5,6):
        c=float(re.search(r'3x-y=(-?\d+)',s)[1]); d=float(re.search(r'x\+2y=(-?\d+)',s)[1]); x=(2*c+d)/7; y=3*x-c
        truth=[numbers(t[0])[-1]==x,numbers(t[1])[-1]==y,numbers(t[2])[-1]==y,[float(v) for v in re.search(r'\((-?\d+),(-?\d+)\)', t[3]).groups()]==[x,y]]
    elif key == (9,5,8):
        c,d=map(float,re.search(r'x-y=(-?\d+)\$ dan \$2x-2y=(-?\d+)',s).groups())
        e,f=map(float,re.search(r'x\+y=(-?\d+)\$ dan \$x\+y=(-?\d+)',s).groups())
        g,h=map(float,re.search(r'2x\+y=(-?\d+)\$ dan \$x-3y=(-?\d+)',s).groups())
        x=(3*g+h)/7; y=g-2*x
        truth=[d==2*c,False,e!=f,[float(v) for v in re.search(r'\((-?\d+),(-?\d+)\)', t[3]).groups()]==[x,y]]
    else:
        raise ValueError(qid)
    assert [bool(o['correct']) for o in opts] == truth, (qid,s,t,truth)
    return truth


if __name__ == '__main__':
    import json
    from pathlib import Path
    from engine import assemble, build_values
    path = Path(__file__).resolve().parents[2] / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'
    selection = {(8,4,1),(8,4,9),(8,5,2),(8,5,8),(9,4,2),(9,4,9),(9,5,6),(9,5,8)}
    count = 0
    for entry in json.loads(path.read_text(encoding='utf8'))['entries']:
        if tuple(entry[z] for z in ('indicator','level','source_number')) not in selection:
            continue
        a = author(entry)
        original = {'hash':'self-check', 'options':[{'id':str(j+1) if a.s['format']=='KATEGORI' else chr(65+j)} for j in range(len(a.options))]}
        cfg = a.config(original)
        for k in range(31):
            candidate = assemble(cfg, build_values(cfg, lambda name,spec:k))
            check_math(a.qid, candidate)
            if k == 0:
                assert candidate['stem'] == a.s['stem']
                assert [o['text'] for o in candidate['options']] == a.s['options']
            count += 1
    assert count == 248
    print('248 variants: rendered math and exact originals passed')


