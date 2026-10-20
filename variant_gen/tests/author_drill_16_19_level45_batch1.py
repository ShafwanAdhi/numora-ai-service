"""27 bounded numeric families; oracle recomputes answers from rendered text."""
import json
import re
from fractions import Fraction as F
from pathlib import Path

from build_drill_1_5_level45_batch1 import Author, NUMBER
from drill_11_15_math import number, calc
from test_drill_16_19_level45_batch1 import ROOT, SELECTION

DATA=ROOT/'data/drill-1-indicators-16-19-levels-4-5'


def selected():
    return [e for e in json.loads((DATA/'audit.json').read_text(encoding='utf8'))['entries']
            if e['source_number'] in SELECTION.get(e['indicator'],{}).get(e['level'],[])]


def author(e):
    e=dict(e,format=e['source_projection']['format'])
    a=Author(e); f='(k+1)'; case=(a.i,a.l,a.n)
    # ponytail: 30 positive homothetic variants per family; broaden dimensions only after a new domain audit.
    def scaled(text,mapping):
        # A coordinate comma separates components; it is not an Indonesian decimal comma.
        def coordinate(m):
            def component(token):
                sign='-' if token.startswith('-') else ''; literal=token.lstrip('-')
                return sign+a.var(mapping[literal],literal) if literal in mapping else token
            return '('+component(m[1])+m[2]+component(m[3])+')'
        text=re.sub(r'\((-?\d+(?:\.\d{3})*)(,\s*)(-?\d+(?:\.\d{3})*)\)',coordinate,text)
        # The prescribed pi=22/7 and powers are constants, never physical dimensions.
        pattern=re.compile(r'\\frac\{22\}\{7\}|'+NUMBER.pattern)
        def sub(m):
            token=m[0]
            if token not in mapping or re.search(r'[\^_]\{?$',text[:m.start()]):return token
            return a.var(mapping[token],token)
        return pattern.sub(sub,text)
    def stem(mapping):a.stem=scaled(a.stem,mapping)
    def option(index,mapping):a.options[index]=scaled(a.options[index],mapping)
    def powers(values,power=1):
        return {str(v):f'({number(str(v))})*{f}**{power}' for v in values}
    def opts(power=1):
        for j,text in enumerate(a.options):
            m=NUMBER.search(text)
            if not m:continue
            a.options[j]=text[:m.start()]+a.var(f'{number(m[0])}*{f}**{power}',m[0])+text[m.end():]
    def explain(answer,text):a.exp=a.explanation('Hasil = [['+answer+']]. '+text)

    if case==(16,5,4):
        stem(dict(powers([12,8]),**powers([412],2)));opts()
        explain('5.5*(k+1)','L=2(pl+pt+lt). Tinggi = (L/2-pl)/(p+l) = [[5.5*(k+1)]] cm. Hanya opsi B memenuhi persamaan luas permukaan.')
    elif case==(16,5,10):
        stem(powers([7,14]));option(0,powers([14]));option(2,powers([14]));option(3,powers([147],2))
        explain('147*(k+1)**2','r=[[7*(k+1)]], s=[[14*(k+1)]]. Busur=2*pi*r=[[14*(k+1)]] pi cm; sudut=360*r/s=180 derajat, bukan90. Tinggi=sqrt(s^2-r^2)=[[7*(k+1)]] sqrt(3) cm, bukan garis pelukis. Luas=pi*r*(r+s)=[[147*(k+1)**2]] pi cm2. Pernyataan 1 dan4 benar.')
    elif case==(17,4,1):
        stem(powers([3,4]));a.options=[scaled(t,powers([3,4])) for t in a.options]
        explain('4*(k+1)','Rotasi90 searah jarum jam: (x,y) menjadi(y,-x). Hasil ([[4*(k+1)]],[[3*(k+1)]]), opsi C.')
    elif case==(17,4,2):
        a.stem=a.stem.replace('=6','=6'.replace('6',a.var('6*(k+1)','6')))
        a.stem=a.stem.replace('T(1,-2)','T('+a.var('k+1','1')+',-'+a.var('2*(k+1)','2')+')')
        for j,text in enumerate(a.options):
            left,right=text.split('=');a.options[j]=left+'='+scaled(right,powers([2,10,4]))
        explain('2*(k+1)','Untuk ax+by=c ditranslasi(u,v), bayangan ax+by=c+a*u+b*v. Di sini c+a*u+b*v=[[2*(k+1)]]. Opsi A.')
    elif case==(17,4,3):
        stem(powers([6,4]));opts(2)
        explain('96*(k+1)**2','Luas awal=[[24*(k+1)**2]]. Faktor dilatasi-2 memberi luas4 kali, yaitu [[96*(k+1)**2]] cm2. Opsi C.')
    elif case==(17,4,4):
        stem(powers([4,3]));opts()
        explain('k+1','Refleksi y=x menukar koordinat: a=[[-3*(k+1)]], b=[[4*(k+1)]]. Jumlah=[[k+1]], opsi C.')
    elif case==(17,4,5):
        stem(powers([1,2,3,4,5]));a.options=[scaled(t,powers([1,2,4,6,9,10])) for t in a.options]
        explain('-6*(k+1)','Vektor T=([[-5*(k+1)]],[[6*(k+1)]]). Tambahkan pada Q untuk memperoleh([[-6*(k+1)]],[[10*(k+1)]]). Opsi A.')
    elif case==(17,5,2):
        stem(powers([4,5]));a.options=[scaled(t,powers([4,5])) for t in a.options]
        explain('5*(k+1)','Invers rotasi90 berlawanan jarum jam: (X,Y) memberi titik awal(Y,-X). P=([[5*(k+1)]],[[4*(k+1)]]), opsi A.')
    elif case==(17,5,4):
        stem(powers([3]));a.options=[scaled(t,powers([3])) for t in a.options]
        explain('3*(k+1)','Refleksi y=-x: substitusi x=-Y,y=-X ke2x-y+c=0. Bayangan X-2Y+c=0 dengan c=[[3*(k+1)]], opsi A.')
    elif case==(17,5,5):
        stem(powers([2,6,12]));opts()
        explain('-4*(k+1)','Faktor dilatasi-3 memberi -3*k=[[12*(k+1)]]. Maka k=[[-4*(k+1)]]. Komponen x juga cocok: -3*[[2*(k+1)]]=[[-6*(k+1)]]. Opsi A.')
    elif case==(18,4,1):
        stem(powers([28,14]));opts(2)
        explain('420*(k+1)**2','Luas lingkaran=[[616*(k+1)**2]], kolam persegi=[[196*(k+1)**2]]. Selisih=[[420*(k+1)**2]] m2. Opsi B.')
    elif case==(18,4,2):
        stem(powers([24,14]));opts(2)
        explain('182*(k+1)**2','Diameter lingkaran terbesar sama dengan sisi pendek persegi panjang. Luas persegi panjang=[[336*(k+1)**2]], lingkaran=[[154*(k+1)**2]], selisih=[[182*(k+1)**2]]. Opsi B.')
    elif case==(18,4,4):
        stem(powers([10,7]));opts()
        explain('38*(k+1)','Keliling luar=2p+l+pi*l/2. Sisi sambungan tidak dihitung. Keliling=[[38*(k+1)]] cm. Opsi C.')
    elif case==(18,4,5):
        stem(powers([44]));option(1,powers([33],2));option(3,powers([33],2))
        explain('33*(k+1)**2','Persegi: sisi=K/4, luas=[[121*(k+1)**2]]. Lingkaran: r=K/(2*pi), luas=[[154*(k+1)**2]]. Lingkaran lebih luas [[33*(k+1)**2]] m2; opsi B. A,D salah arah, C salah karena luas tidak sama.')
    elif case==(18,4,6):
        stem(powers([14]));option(0,powers([196],2));option(1,powers([154],2));option(2,powers([42],2));option(3,powers([72]))
        explain('196*(k+1)**2','Persegi=[[196*(k+1)**2]], seperempat lingkaran=[[154*(k+1)**2]], sisa=[[42*(k+1)**2]]. Keliling sisa=2s+pi*s/2=[[50*(k+1)]], bukan [[72*(k+1)]]. A,B,C benar.')
    elif case==(18,5,1):
        stem(powers([88]));opts(2)
        explain('132*(k+1)**2','Persegi berluas[[484*(k+1)**2]]; lingkaran berluas[[616*(k+1)**2]]. Selisih[[132*(k+1)**2]], lingkaran lebih luas. Hanya B; A salah arah, C salah sama besar, D salah selisih.')
    elif case==(18,5,2):
        stem(powers([20,14]));opts(2)
        explain('126*(k+1)**2','Luas awal[[280*(k+1)**2]], dua setengah lingkaran berjumlah satu lingkaran luas[[154*(k+1)**2]]. Sisa[[126*(k+1)**2]], opsi C.')
    elif case==(18,5,4):
        stem(powers([28,'3,5']));opts(2)
        explain('34650000*(k+1)**2','R=[[17.5*(k+1)]], r=[[14*(k+1)]]. Luas jalan=pi*(R^2-r^2)=[[346.5*(k+1)**2]] m2. Tarif tetap100000/m2, biaya[[34650000*(k+1)**2]], opsi D.')
    elif case==(18,5,5):
        stem(powers([14]));opts()
        explain('500000*(k+1)','Keliling juring=2r+pi*r/2=[[50*(k+1)]]. Biaya=[[7500000*(k+1)]], anggaran=[[7000000*(k+1)]], kurang[[500000*(k+1)]]. Opsi B.')
        # Budget scales with the fence, tariff remains fixed.
        a.stem=scaled(a.stem,{'7.000.000,00':'7000000*(k+1)'})
    elif case==(19,4,1):
        stem(powers([36],3));opts(3)
        explain('288*(k+1)**3','Jari-jari digandakan memberi faktor volume8. Volume baru=[[288*(k+1)**3]] pi cm3, opsi C.')
    elif case==(19,4,2):
        stem(dict(powers([6,8]),**powers([240],3)));opts()
        explain('10*(k+1)','Luas alas=a*b/2=[[24*(k+1)**2]]. Tinggi=V/luas alas=[[10*(k+1)]], opsi B.')
    elif case==(19,4,3):
        stem(dict(powers([8,6]),**powers([160],3)));opts()
        explain('10*(k+1)','Luas alas=[[48*(k+1)**2]]. Tinggi limas=3V/luas alas=[[10*(k+1)]], opsi D.')
    elif case==(19,4,4):
        stem(powers([10]));a.options=[scaled(t,powers([1000,500,250],3)) for t in a.options]
        explain('1000*(k+1)**3','r=rusuk/2=[[5*(k+1)]]. Volume kubus=[[1000*(k+1)**3]]; volume bola=[[500*(k+1)**3]] pi/3. Selisih adalah opsi A.')
    elif case==(19,4,6):
        stem(powers([3,4,5,10]));option(0,powers([6],2));option(1,powers([60],3));option(2,dict(powers([20]),**powers([120],3)))
        explain('60*(k+1)**3','Luas alas=[[6*(k+1)**2]], volume=[[60*(k+1)**3]]. Tinggi dua kali memberi[[120*(k+1)**3]]. Menggandakan semua sisi alas pada tinggi tetap memberi faktor volume4, bukan2. A,B,C benar.')
    elif case==(19,5,1):
        stem(dict(powers([10,12,15]),**powers([40],2)));opts(3)
        explain('200*(k+1)**3','Air limas=[[400*(k+1)**3]], kapasitas prisma=[[600*(k+1)**3]]. Muat, sisa[[200*(k+1)**3]], opsi A. B salah sisa, C salah tumpah, D salah penuh.')
    elif case==(19,5,3):
        stem(powers([12,10,8,18]));opts()
        explain('10*(k+1)','Volume limas1=[[480*(k+1)**3]]. Luas alas2=[[144*(k+1)**2]]. Tinggi2=3V/luas alas=[[10*(k+1)]], opsi B.')
    elif case==(19,5,4):
        stem(dict(powers([12,16]),**powers([960],3)));opts()
        explain('10*(k+1)','Luas alas=d1*d2/2=[[96*(k+1)**2]]. Tinggi=V/luas alas=[[10*(k+1)]], opsi D.')
    else:raise AssertionError(case)
    # Source Word typography c{m} is preserved for reproduction, displayed as cm in variants.
    from expr import placeholders
    for text in [a.stem,*a.options,a.exp]:
        for name in placeholders(text)-a.variables.keys():
            assert name=='m',(a.qid,name)
            a.variables[name]=dict(gen='derived',expr="'{m}' if k == 0 else 'm'")
    return a


def nums(text):
    text=re.sub(r'\((-?\d+(?:\.\d{3})*),\s*(-?\d+(?:\.\d{3})*)\)',r'(\1;\2)',text)
    text=re.sub(r'\\frac\{22\}\{7\}','',text)
    text=re.sub(r'(\d)\{(\d+)\}',r'\1\2',text)
    text=re.sub(r'\^\{[^{}]*\}|[²³]','',text)
    return [number(x) for x in re.findall(r'-?\d+(?:\.\d{3})*(?:,\d+)?',text)]


def line_zero(text,x,y):
    text=text.replace('$','').replace(' ','')
    left,right=text.split('=')
    def evaluate(t):return calc(re.sub(r'(\d)([xy])',r'\1*\2',t),x=x,y=y)
    return evaluate(left)==evaluate(right)


def check_math(q,c):
    """Read only rendered stimulus/options, not config values, original key or k."""
    i,l,n=map(int,q.split('-')[1:]);case=(i,l,n);v=nums(c['stem']); options=c['options']
    values=[nums(o['text']) for o in options]
    answer=None; truth=None
    if case==(16,5,4):
        count,area,p,w=v;assert count==6;answer=(area/2-p*w)/(p+w)
    elif case==(16,5,10):
        r,s=v;answer=r*(r+s)
        truth=[values[0][0]==2*r,values[1][0]==360*r/s,
               values[2][0]**2==s*s-r*r,values[3][0]==answer]
    elif case==(17,4,1):
        x,y,angle,ox,oy=v;assert angle==90 and ox==oy==0
        pair=[y,-x];answer=y;truth=[p==pair for p in values]
    elif case==(17,4,2):
        a,b,c0,u,w=v;answer=c0+a*u+b*w
        truth=[all(line_zero(o['text'],x,(answer-a*x)/b) for x in (F(0),F(1))) for o in options]
    elif case==(17,4,3):
        p,w,_,_,scale=v;answer=p*w*scale**2
    elif case==(17,4,4):answer=sum(v)
    elif case==(17,4,5):
        x,y,X,Y,u,w=v;pair=[u+X-x,w+Y-y];answer=pair[0];truth=[p==pair for p in values]
    elif case==(17,5,2):
        angle,_,_,X,Y=v;assert angle==90
        pair=[Y,-X];answer=Y;truth=[p==pair for p in values]
    elif case==(17,5,4):
        _,constant,_=v;answer=constant
        truth=[all(line_zero(o['text'],-(2*x+constant),-x) for x in (F(0),F(1))) for o in options]
    elif case==(17,5,5):
        x,scale,_,_,X,Y=v;assert scale*x==X;answer=Y/scale
    elif case==(18,4,1):
        d,s=v;assert s*s*2<=d*d;answer=F(22,7)*(d/2)**2-s*s
    elif case==(18,4,2):
        p,w=v;answer=p*w-F(22,7)*(min(p,w)/2)**2
    elif case==(18,4,4):
        p,w=v;answer=2*p+w+F(22,7)*w/2
    elif case==(18,4,5) or case==(18,5,1):
        perimeter,=v;answer=F(7,88)*perimeter**2-(perimeter/4)**2
        truth=[False,values[1][0]==answer,False,False]
    elif case==(18,4,6):
        s,r=v;assert s==r;answer=s*s;quarter=F(22,28)*r*r
        truth=[values[0][0]==answer,values[1][0]==quarter,
               values[2][0]==answer-quarter,values[3][0]==2*s+F(11,7)*r]
    elif case==(18,5,2):
        p,w,d=v;assert w==d and p>=d;answer=p*w-F(22,7)*(d/2)**2
    elif case==(18,5,4):
        d,width,rate=v;answer=F(22,7)*((d/2+width)**2-(d/2)**2)*rate
    elif case==(18,5,5):
        angle,r,rate,budget=v;assert angle==90
        answer=(2*r+angle/360*F(44,7)*r)*rate-budget
        truth=[False,values[1][0]==answer,False,False];assert answer>0
    elif case==(19,4,1):
        initial,factor=v;answer=initial*factor**3
    elif case==(19,4,2):
        a,b,volume=v;answer=volume/(a*b/2)
    elif case==(19,4,3):
        p,w,volume=v;answer=3*volume/(p*w)
    elif case==(19,4,4):
        side,=v;answer=side**3;ball=4*(side/2)**3/3
        truth=[p==[answer,ball*3,F(3)] for p in values]
    elif case==(19,4,6):
        a,b,hyp,h=v;assert a*a+b*b==hyp*hyp
        area=a*b/2;answer=area*h
        truth=[values[0][0]==area,values[1][0]==answer,
               values[2][1]==area*values[2][0],values[3][0]==4]
    elif case==(19,5,1):
        side,h,base,H=v;answer=base*H-side*side*h/3;assert answer>0
        truth=[values[0][0]==answer,False,False,False]
    elif case==(19,5,3):
        side,h,p,w=v;answer=side*side*h/(p*w)
    elif case==(19,5,4):
        volume,d1,d2=v;answer=volume/(d1*d2/2)
    else:raise AssertionError(case)
    if truth is None:truth=[p==[answer] for p in values]
    assert [o['correct'] for o in options]==truth,(q,v,values,truth)
    assert sum(truth)==(2 if q.startswith('kategori') else 3 if q.startswith('mcma') else 1),(q,truth)
    assert nums(c['explanation'])[0]==answer,(q,c['explanation'],answer)


def main():
    from bank import OriginalBank
    from config_store import validate_config
    from lint import reproduce_original
    bank=OriginalBank(DATA/'q0_bank.csv'); configs={}
    for e in selected():
        assert not e['issues'],e['question_id']
        a=author(e);o=bank.get(a.qid);cfg=a.config(o)
        assert validate_config(cfg,o)==[],(a.qid,validate_config(cfg,o))
        assert reproduce_original(o,cfg)==([],[]),(a.qid,reproduce_original(o,cfg))
        path=ROOT/'configs'/a.qid/'v1.json';value=json.dumps(cfg,indent=2,ensure_ascii=False)+'\n'
        if path.exists():assert path.read_text(encoding='utf8')==value,f'Refusing overwrite: {path}'
        configs[path]=value
    for path,value in configs.items():
        path.parent.mkdir(exist_ok=True)
        if not path.exists():path.write_text(value,encoding='utf8')
    path=DATA/'question_metadata.json';metadata=json.loads(path.read_text(encoding='utf8'))
    for e in selected():metadata[e['question_id']]['generator_status']='IMPLEMENTED'
    path.write_bytes((json.dumps(metadata,indent=2,ensure_ascii=False)+'\n').encode('utf8'))
    print(f'Authored {len(configs)} configs; generator status updated, original content unchanged.')


if __name__=='__main__':main()
