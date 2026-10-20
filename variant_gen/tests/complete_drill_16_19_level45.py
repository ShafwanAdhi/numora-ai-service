"""Finish the remaining 53: explicit source revisions, 38 configs and 15 finite stocks."""
import json
import re
from copy import deepcopy
from fractions import Fraction as F

from author_drill_16_19_level45_batch1 import ROOT,DATA,nums as base_nums,line_zero
from build_drill_1_5_level45_batch1 import Author,NUMBER
from drill_11_15_math import number
from test_drill_16_19_level45_batch1 import SELECTION

CONCEPTS=set('''pg-16-4-2 pg-16-4-5 mcma-16-4-6 mcma-16-4-7 mcma-16-4-8
kategori-16-4-9 kategori-16-4-10 pg-16-5-1 pg-16-5-2 mcma-16-5-7 mcma-16-5-8
pg-17-5-3 mcma-17-5-7 mcma-19-5-6 mcma-19-5-7'''.split())


def dump(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_bytes((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode('utf8'));tmp.replace(path)


def entries():return json.loads((DATA/'audit.json').read_text(encoding='utf8'))['entries']


def remaining():
    return [e for e in entries() if e['source_number'] not in SELECTION.get(e['indicator'],{}).get(e['level'],[])]


def numeric_entries():return [e for e in remaining() if e['question_id'] not in CONCEPTS]


def revise_sources():
    from bank import OriginalBank
    bank=OriginalBank(DATA/'q0_bank.csv');metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
    records=[]
    def row(o):return dict(id=o['id'],format=o['format'],cognitive_level=o['cognitive_level'],stem=o['stem'],
        options_json=json.dumps([p['text'] for p in o['options']],ensure_ascii=False),
        key=','.join(p['id'] for p in o['options'] if p['correct']),version=str(o['version']))
    for e in remaining():
        if not e['issues']:continue
        q=e['question_id'];o=bank.get(q)
        if o['version']==2:continue
        assert o['version']==1 and o['metadata']['generation_status']=='HOLD_SOURCE',q
        n=deepcopy(o);n['version']=2;m=deepcopy(o['metadata'])
        if q=='pg-16-4-1':
            n['stem']=re.sub(r'^.*?\n!\[[^\]]*\]\([^)]*\)\n','Sebuah jaring-jaring tabung terdiri dari dua lingkaran dan satu persegi panjang.\n',o['stem'],count=1)
        elif q=='pg-16-4-3':n['stem']=re.sub(r'!\[[^\]]*\]\([^)]*\)\n?','',o['stem'])
        elif q=='pg-16-4-4':n['stem']='Sebuah jaring-jaring limas segi empat beraturan memiliki alas persegi bersisi 12 cm dan empat sisi tegak segitiga yang masing-masing memiliki tinggi 10 cm. Luas permukaan bangun ruang yang terbentuk adalah...'
        elif q=='mcma-16-4-6':
            n['stem']='Sebuah limas segitiga dibuka menjadi jaring-jaring. Pilihlah semua pernyataan yang benar mengenai jaring-jaring dan bangun ruang tersebut!'
            n['options'][0]['text']='Jaring-jaring bangun tersebut terdiri dari 4 buah segitiga.'
            n['options'][2]['text']='Bangun ruang tersebut memiliki 4 buah titik sudut.'
            for idx,p in enumerate(n['options']):p['correct']=idx in (0,1,2)
        elif q=='mcma-16-4-7':n['stem']='Sebuah tabung tertutup dibuka menjadi jaring-jaring yang terdiri dari dua lingkaran dan satu persegi panjang. Manakah pernyataan yang benar? Pilih tiga jawaban.'
        elif q=='kategori-16-4-9':n['options'][1]['text']='Jaring-jaring limas segi-n selalu memiliki tepat n sisi tegak berbentuk segitiga.'
        elif q=='pg-16-5-1':
            n['stem']='Empat rancangan jaring-jaring berikut memiliki sambungan yang sesuai. A: tabung berjari-jari 7 cm dengan panjang selimut 44 cm. B: prisma segitiga dengan dua alas kongruen dan tiga persegi panjang sesuai sisi alas. C: tabung berjari-jari 7 cm dengan panjang selimut 20 cm. D: kerucut berjari-jari alas 7 cm dengan panjang busur juring 44 cm. Gunakan pi=22/7. Rancangan manakah yang tidak dapat menutup bangun dengan sempurna?'
        elif q=='mcma-17-4-6':pass
        elif q=='kategori-17-4-9':n['options'][0]['text']=o['options'][0]['text'].replace('T(-, 25)','T(-2, 5)')
        elif q=='pg-17-5-1':n['stem']=o['stem'].replace('Faktor skala yang mungkin','Seluruh kemungkinan faktor skala')
        elif q=='pg-17-5-3':n['stem']=o['stem'].replace('Suatu transformasi memetakan','Refleksi terhadap sumbu Y memetakan')
        elif q=='kategori-17-5-9':
            n['options'][0]['text']=o['options'][0]['text'].replace('(-, 2 - 2)','(-2, -2)')
            n['options'][3]['text']=o['options'][3]['text'].replace('(-, 102)','(-10, 2)')
        elif q=='kategori-17-5-10':n['options'][2]['text']='Rotasi 180° mempertahankan luas bangun tetap 20 cm².'
        elif q=='kategori-19-5-10':n['stem']=o['stem']+' Tinggi awal prisma lebih dari 5 cm.'
        else:raise AssertionError(q)
        explanations={
          'mcma-16-4-6':'Limas segitiga memiliki empat bidang segitiga, enam rusuk, dan empat titik sudut. Pernyataan A,B,C benar; D salah karena titik sudut bukan lima.',
          'mcma-17-4-6':'A(-2,5): refleksi sumbu X=(-2,-5); refleksi y=x=(5,-2); rotasi90 berlawanan jarum jam=(-5,-2); dilatasi-2=(4,-10), bukan(-4,10). A,B,C benar.',
          'kategori-17-4-9':'C(4,-3): translasi(-2,5)=(2,2); refleksi X=(4,3); refleksi y=-x=(3,-4); rotasi90 berlawanan jarum jam=(3,4), bukan(3,-4). 1,2,3 benar.',
          'kategori-17-5-9':'D(-5,2): translasi(3,-4)=(-2,-2); refleksi Y=(5,2); rotasi180=(5,-2); dilatasi2=(-10,4), bukan(-10,2). 1,2,3 benar.',
          'kategori-17-5-10':'Refleksi, translasi, rotasi mempertahankan luas20 cm2. Dilatasi3 menghasilkan luas9*20=180, bukan60. 1,2,3 benar.',
          'kategori-16-4-9':'Prisma memiliki dua alas kongruen. Limas segi-n memiliki n sisi tegak segitiga; alasnya dapat juga segitiga bila n=3. Balok tidak mempunyai enam persegi berbeda ukuran. Puncak di atas sudut persegi memungkinkan empat sisi tegak siku-siku. 1,2,4 benar.',
          'pg-16-5-1':'Tabung r7 memerlukan panjang selimut2*(22/7)*7=44cm. Rancangan C hanya20cm sehingga tidak menutup. A sesuai44cm; B sesuai komponen prisma; D busur44cm sesuai keliling alas.'}
        reason='Revisi lokal engineering untuk menuntaskan sisa soal atas instruksi pengguna: '+ '; '.join(e['issues'])
        m.update(generation_status='DEFERRED_CONCEPTUAL' if q in CONCEPTS else 'ACTIVE',
            generator_status='FINITE_STOCK' if q in CONCEPTS else 'NOT_IMPLEMENTED',reason=reason,
            original_explanation=explanations.get(q,m['original_explanation']),
            raw_source_explanation=o['metadata']['original_explanation'],
            raw_source_projection=o['metadata']['source_projection'],
            approval_status='NOT_CURRICULUM_APPROVED',self_adjustment_enabled=False,
            source_review=dict(date='2026-10-21',original_version=1,replacement_version=2,
                reason=reason,source_document_unchanged=True,original_text_preserved=True))
        m['source_projection']=dict(format=n['format'],stem=n['stem'],options=[p['text'] for p in n['options']],
            key=[p['id'] for p in n['options'] if p['correct']],explanation=m['original_explanation'],
            additional_notes=o['metadata'].get('source_additional_notes',''),category_labels=m.get('category_labels'))
        if '![' not in n['stem']:
            m['raw_source_media']=m.get('source_media',[]);m['source_media']=[]
        records.append(dict(question_id=q,original_version=1,replacement_version=2,original_row=row(o),replacement_row=row(n),
            original_metadata=o['metadata'],replacement_metadata=m,source_document_sha256=m['source_document_sha256'],reason=reason))
        metadata[q]=m
    if records:
        ledger=DATA/'original_revisions.jsonl'
        existing=ledger.read_text(encoding='utf8') if ledger.exists() else ''
        tmp=ledger.with_suffix('.jsonl.tmp');tmp.write_text(existing+''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records),encoding='utf8');tmp.replace(ledger)
        dump(DATA/'question_metadata.json',metadata)
    print(f'Source revisions added: {len(records)}; DOCX and source CSV unchanged.')


def author(e):
    # ponytail: 30 variants per family; widen independent dimensions after another domain audit.
    from bank import OriginalBank
    o=OriginalBank(DATA/'q0_bank.csv').get(e['question_id'])
    projection=dict(format=o['format'],stem=o['stem'],options=[p['text'] for p in o['options']],
                    key=[p['id'] for p in o['options'] if p['correct']])
    a=Author(dict(e,format=o['format'],source_projection=projection));case=(a.i,a.l,a.n)
    def scaled(text,mapping):
        def coordinate(m):
            def part(t):
                sign='-' if t.startswith('-') else '';v=t.lstrip('-')
                return sign+a.var(mapping[v],v) if v in mapping else t
            return '('+part(m[1])+m[2]+part(m[3])+')'
        text=re.sub(r'\((-?\d+(?:\.\d{3})*)(,\s*)(-?\d+(?:\.\d{3})*)\)',coordinate,text)
        def sub(m):
            v=m[0]
            if v not in mapping or re.search(r'[\^_]\{?$',text[:m.start()]):return v
            return a.var(mapping[v],v)
        return re.sub(r'\\frac\{22\}\{7\}|'+NUMBER.pattern,sub,text)
    def power(values,p=1):return {str(v):f'({number(str(v))})*(k+1)**{p}' for v in values}
    def stem(mapping):a.stem=scaled(a.stem,mapping)
    def opt(j,mapping):a.options[j]=scaled(a.options[j],mapping)
    def allopts(mapping):a.options=[scaled(t,mapping) for t in a.options]
    def summary(answer,text):a.exp=a.explanation('Hasil = [['+answer+']]. '+text)
    if case==(16,4,1):
        stem(power([7,10]));allopts(power([440,594,616,748],2))
        summary('748*(k+1)**2','Luas dua alas=[[308*(k+1)**2]], selimut=[[440*(k+1)**2]]. Total[[748*(k+1)**2]]cm2; opsi D.')
    elif case==(16,4,3):
        stem(power([14,20]));allopts(power([44,88,154,176]))
        summary('88*(k+1)','Busur juring=keliling alas=2*pi*r=[[88*(k+1)]]cm; opsi B. Garis pelukis tetap lebih besar daripada r.')
    elif case==(16,4,4):
        stem(power([12,10]));allopts(power([144,240,384,480],2))
        summary('384*(k+1)**2','Alas=[[144*(k+1)**2]], empat segitiga=[[240*(k+1)**2]]. Total[[384*(k+1)**2]], opsi C.')
    elif case==(16,5,3):
        image=re.search(r'!\[[^\]]*\]\([^)]*\)',a.stem)[0]
        replacement='Jari-jari juring '+a.var('12*(k+1)','12')+' cm, sudut pusat 150 derajat.'
        a.stem=a.stem.replace(image,a.var(repr(image)+" if k == 0 else ''",image)+a.var("'' if k == 0 else 'Jari-jari juring '",'')+a.var("'' if k == 0 else 12*(k+1)",'')+a.var("'' if k == 0 else ' cm, sudut pusat 150 derajat.'",''))
        a.stem=a.stem.replace('Perhatikan gambar jaring-jaring kerucut di bawah ini!',a.var("'Perhatikan gambar jaring-jaring kerucut di bawah ini!' if k == 0 else 'Perhatikan data jaring-jaring kerucut berikut.'",'Perhatikan gambar jaring-jaring kerucut di bawah ini!'))
        stem(power([5]));opt(0,{'10':'10*(k+1)'});opt(1,power([10]))
        summary('5*(k+1)','Busur=150/360*2*pi*s=[[10*(k+1)]]pi. Maka r=busur/(2*pi)=[[5*(k+1)]]. Opsi A; r bukan setengah s karena sudutnya150, bukan180.')
    elif case==(16,5,5):
        image=re.search(r'!\[[^\]]*\]\([^)]*\)',a.stem)[0]
        a.stem=a.stem.replace(image,a.var(repr(image)+" if k == 0 else ''",image)+a.var("'' if k == 0 else 'Sisi alas persegi '",'')+a.var("'' if k == 0 else 10*(k+1)",'')+a.var("'' if k == 0 else ' cm; tinggi setiap segitiga sisi tegak '",'')+a.var("'' if k == 0 else 13*(k+1)",'')+a.var("'' if k == 0 else ' cm.'",''))
        a.stem=a.stem.replace('Perhatikan gambar jaring-jaring limas segi empat beraturan di bawah ini!',a.var("'Perhatikan gambar jaring-jaring limas segi empat beraturan di bawah ini!' if k == 0 else 'Perhatikan data jaring-jaring limas segi empat beraturan berikut.'",'Perhatikan gambar jaring-jaring limas segi empat beraturan di bawah ini!'))
        stem(dict(power([100,65],2),**{'13':'13 if k == 0 else 12*(k+1)','360':'360 if k == 0 else 400*(k+1)**2'}))
        a.correct=[False,False,'k != 0','k == 0']
        summary('360*(k+1)**2','Alas=[[100*(k+1)**2]], tiap sisi tegak=[[65*(k+1)**2]], tinggi limas=[[12*(k+1)]], total[[360*(k+1)**2]]. Pada original(1),(2),(4) benar; pada varian(1),(2),(3) benar.')
    elif case==(16,5,6):
        a.stem=a.stem.replace('3 kali',a.var('3+k','3')+' kali');opt(0,{'9':'(3+k)**2'});opt(1,{'9':'(3+k)**2'});opt(2,{'18':'6*(3+k)'});opt(3,{'27':'(3+k)**3'})
        summary('(3+k)**2','Faktor panjang[[3+k]] memberi luas[[(3+k)**2]], volume[[(3+k)**3]]. Jumlah persegi tetap6; A,B,D benar.')
    elif case==(16,5,9):
        opt(1,dict(power([150],2),**power([155],3)));opt(3,power([64,40,224],2))
        summary('224*(k+1)**2','Luas net sama dengan permukaan. Kubus: s=[[5*(k+1)]], volume[[125*(k+1)**3]], bukan[[155*(k+1)**3]]. Vtabung=pi*r^2*t. Limas=[[64*(k+1)**2]]+4*[[40*(k+1)**2]]=[[224*(k+1)**2]]. 1,3,4 benar.')
    elif case in ((17,4,6),(17,5,6)):
        first=case==(17,4,6);xy=[2,5] if first else [3,4];stem(power(xy))
        if first:
            for j in (0,1,2):opt(j,power([2,5]))
            opt(3,power([4,10]));summary('5*(k+1)','A=(-[[2*(k+1)]],[[5*(k+1)]]). RefleksiX=(-[[2*(k+1)]],-[[5*(k+1)]]); tukar=([[5*(k+1)]],-[[2*(k+1)]]); CCW90=(-[[5*(k+1)]],-[[2*(k+1)]]); dilatasi-2=([[4*(k+1)]],-[[10*(k+1)]]). A,B,C benar.')
        else:
            opt(0,power([3,4]));opt(1,power([3,4]));opt(2,power([1,2,4]));opt(3,power([6,8]))
            summary('4*(k+1)','P=(-[[3*(k+1)]],[[4*(k+1)]]). RefleksiX=(-[[3*(k+1)]],-[[4*(k+1)]]); rotasi180=([[3*(k+1)]],-[[4*(k+1)]]); translasi=([[k+1]],[[2*(k+1)]]); dilatasi2=(-[[6*(k+1)]],[[8*(k+1)]]). A,B,C benar.')
    elif case==(17,4,7):
        a.stem=a.stem.replace('2x - 1','2x - '+a.var('k+1','1'))
        a.options[0]=scaled(a.options[0],power([3,1,6]));opt(1,power([1]));opt(2,power([1]));opt(3,power([4]))
        summary('6*(k+1)','Translasi memberi y=2x-[[6*(k+1)]]. RefleksiX: y=-2x+[[k+1]]; refleksiY: y=-2x-[[k+1]]. Dilatasi2 memberi y=2x-[[2*(k+1)]], bukan-[[4*(k+1)]]. A,B,C benar.')
    elif case==(17,4,8):
        stem(power([6,8]));opt(0,power([1]));opt(2,power([3,4]));opt(3,power([3,4]))
        summary('-1*(k+1)','Titik awal B=([[3*(k+1)]],-[[4*(k+1)]]), kuadranIV; x+y=[[-1*(k+1)]]. RefleksiY=(-[[3*(k+1)]],-[[4*(k+1)]]); rotasi180=(-[[3*(k+1)]],[[4*(k+1)]]). A,B,C benar.')
    elif case==(17,4,9):
        stem(power([4,3]));opt(0,power([2,5]));opt(1,power([4,3]));opt(2,power([3,4]));opt(3,power([3,4]))
        summary('2*(k+1)','C=([[4*(k+1)]],-[[3*(k+1)]]). Translasi menjadi([[2*(k+1)]],[[2*(k+1)]]); refleksiX=([[4*(k+1)]],[[3*(k+1)]]); refleksi y=-x=([[3*(k+1)]],-[[4*(k+1)]]); CCW90=([[3*(k+1)]],[[4*(k+1)]]). 1,2,3 benar.')
    elif case in ((17,4,10),(17,5,10)):
        area=12 if a.l==4 else 20;stem(power([area],2))
        for j in (0,1,2):opt(j,power([area,108] if a.l==4 else [area],2))
        opt(3,power([24 if a.l==4 else 60],2))
        summary(f'{area}*(k+1)**2',f'Isometri menjaga luas[[{area}*(k+1)**2]]. Luas dilatasi=faktor^2*luas; pernyataan4 salah, 1,2,3 benar.')
    elif case==(17,5,1):
        stem(power([90],2));allopts(dict(power([3]),**power([9],2)))
        summary('3*(k+1)','k^2=Lbayangan/Lasal=[[9*(k+1)**2]]. Seluruh kemungkinannya k=+/-[[3*(k+1)]], opsi C; A hanya salah satu kemungkinan.')
    elif case==(17,5,8):
        stem(power([4,2]))
        for j in (0,1,2):opt(j,power([2,4]))
        opt(3,power([12,6]))
        summary('4*(k+1)','B=([[4*(k+1)]],-[[2*(k+1)]]). Tukar=(-[[2*(k+1)]],[[4*(k+1)]]); refleksi y=-x=([[2*(k+1)]],-[[4*(k+1)]]); CW90=(-[[2*(k+1)]],-[[4*(k+1)]]); dilatasi-3=(-[[12*(k+1)]],[[6*(k+1)]]). A,B,D benar.')
    elif case==(17,5,9):
        stem(power([5,2]));opt(0,power([3,4,2]));opt(1,power([5,2]));opt(2,power([5,2]))
        before,after=a.options[3].split('adalah');a.options[3]=before+'adalah'+scaled(after,power([10,2]))
        summary('2*(k+1)','D=(-[[5*(k+1)]],[[2*(k+1)]]). Translasi=(-[[2*(k+1)]],-[[2*(k+1)]]); refleksiY=([[5*(k+1)]],[[2*(k+1)]]); rotasi180=([[5*(k+1)]],-[[2*(k+1)]]); dilatasi2=(-[[10*(k+1)]],[[4*(k+1)]]). 1,2,3 benar.')
    elif case==(18,4,3):
        stem({'3':'3+k'});allopts({'3':'3+k','9':'(3+k)**2'})
        summary('(3+k)**2','Keliling linear terhadap r, faktor[[3+k]]; luas kuadrat, faktor[[(3+k)**2]]. Opsi C.')
    elif case==(18,4,7):
        stem(power([28]));opt(0,power([616],2));opt(1,power([14]));opt(2,power([392],2));opt(3,power([224],2))
        summary('616*(k+1)**2','Diagonal persegi=diameter[[28*(k+1)]]. Luas lingkaran[[616*(k+1)**2]], persegi[[392*(k+1)**2]], sisa[[224*(k+1)**2]]. A,C,D benar.')
    elif case==(18,4,8):
        stem(power([20,10,2]));opt(0,power([200],2));opt(1,power([336],2));opt(2,power([136],2));opt(3,dict(power([1]),**power([68],2)))
        summary('136*(k+1)**2','Awal[[200*(k+1)**2]], luar[[336*(k+1)**2]], jalan[[136*(k+1)**2]]. Lebar alternatif[[k+1]] memberi jalan[[64*(k+1)**2]], bukan[[68*(k+1)**2]]. A,B,C benar.')
    elif case==(18,4,9):
        stem(power([14,7]));opt(0,power([98],2));opt(1,power(['136,5'],2));opt(2,power([50]));opt(3,power([7]))
        summary('136.5*(k+1)**2','Persegi panjang[[98*(k+1)**2]], dua setengah lingkaran[[38.5*(k+1)**2]], total[[136.5*(k+1)**2]]. Keliling[[50*(k+1)]], r=[[3.5*(k+1)]]. 1,2,3 benar.')
    elif case==(18,4,10):
        stem(power([28,'3,5']));opt(0,power([14]));opt(1,power([616],2));opt(2,power(['17,5']));opt(3,power([462],2))
        summary('346.5*(k+1)**2','r=[[14*(k+1)]], R=[[17.5*(k+1)]]. Luas jalan=pi*(R^2-r^2)=[[346.5*(k+1)**2]], bukan[[462*(k+1)**2]]. 1,2,3 benar.')
    elif case==(18,5,3):
        stem(dict(power([14]),**{'64':'64 if k == 0 else 78*(k+1)'},**power([273],2)))
        opt(1,{'78':'78 if k == 0 else 64*(k+1)'});opt(2,power([308],2));opt(3,dict(power([50]),**power([196],2)))
        a.correct=['k == 0','k != 0',False,False]
        summary('64*(k+1)','Luas=persegi+setengah lingkaran=[[273*(k+1)**2]]. Keliling=3s+busur=[[64*(k+1)]]. Original klaim benar; varian klaim keliling salah sehingga B benar.')
    elif case==(18,5,6):
        stem(power([14]));opt(0,power([196],2));opt(1,power([77],2));opt(2,power([64]));opt(3,power([300],2))
        summary('273*(k+1)**2','Luas persegi[[196*(k+1)**2]], setengah lingkaran[[77*(k+1)**2]], total[[273*(k+1)**2]]; keliling[[64*(k+1)]]. A,B,C benar.')
    elif case==(18,5,7):
        stem(power([28,'3,5']));opt(0,power([616],2));opt(1,power(['17,5']));opt(2,power([462],2));opt(3,power([88]))
        summary('346.5*(k+1)**2','Luas taman[[616*(k+1)**2]], R=[[17.5*(k+1)]], jalan[[346.5*(k+1)**2]], keliling taman[[88*(k+1)]]. A,B,D benar.')
    elif case==(18,5,8):
        stem(power([16,12]));opt(0,power([96],2));opt(1,power([14]));opt(2,power([40]));opt(3,power([4]))
        summary('96*(k+1)**2','Luas=d1*d2/2=[[96*(k+1)**2]]. Sisi=sqrt((d1/2)^2+(d2/2)^2)=[[10*(k+1)]], keliling[[40*(k+1)]]. Sisi persegi sama luas=[[4*(k+1)]]sqrt(6). A,C,D benar.')
    elif case==(18,5,9):
        stem(power([15,10]));opt(0,power([150],2));opt(2,power([600],2));opt(3,power([200],2))
        summary('600*(k+1)**2','Keramik tetap0.5m*0.5m=0.25m2. Lantai[[150*(k+1)**2]], perlu[[600*(k+1)**2]] keramik, [[150*(k+1)**2]] dus berisi4. 1,2,3 benar.')
    elif case==(18,5,10):
        stem(power([20,14]));opt(0,power([280],2));opt(1,power([77],2));opt(2,power([203],2));opt(3,power([88]))
        summary('203*(k+1)**2','Awal[[280*(k+1)**2]], potongan[[77*(k+1)**2]], sisa[[203*(k+1)**2]]. Keliling[[76*(k+1)]], bukan[[88*(k+1)]]. 1,2,3 benar.')
    elif case==(19,4,5):
        stem(power([12,16]));allopts(power([2,8,4,16],3))
        summary('8*(k+1)**3','Volume A=96; volume B=[[768*(k+1)**3]]. Rasio B/A=[[8*(k+1)**3]], opsi B.')
    elif case==(19,4,7):
        stem(power([6,12,8]));opt(0,power([288],3));opt(1,power([384],3))
        summary('384*(k+1)**3','Bola=[[288*(k+1)**3]]pi, limas=[[384*(k+1)**3]]. Rasio limas:bola=4:3pi. Menggandakan r membuat bola8 kali, tetap lebih besar. A,B,C benar.')
    elif case==(19,4,8):
        a.options[1]=a.options[1].replace('1 : 3','1 : '+a.var('3+k','3')).replace('1 : 27','1 : '+a.var('(3+k)**3','27'))
        summary('(3+k)**3','Rasio jari-jari1:[[3+k]] memberi volume1:[[(3+k)**3]]. Prisma3 kali limas pada alas/tinggi sama. Bola diameterd=pi*d^3/6, tidak sama dengan limas d^3/3. A,B,D benar.')
    elif case==(19,4,9):
        stem(power([8,6,15]));opt(0,power([24],2));opt(1,power([360],3));opt(2,dict(power([30]),**power([720],3)));opt(3,dict(power([12],2),**power([200],3)))
        summary('360*(k+1)**3','Alas[[24*(k+1)**2]], volume[[360*(k+1)**3]]. Tinggi dua kali memberi[[720*(k+1)**3]]. Luas alas alternatif[[12*(k+1)**2]] memberi[[180*(k+1)**3]], bukan[[200*(k+1)**3]]. 1,2,3 benar.')
    elif case==(19,4,10):
        stem(power([10]));opt(0,power([4000],3));opt(1,power([20]));opt(2,dict(power([5]),**power([500],3)));opt(3,power([20]))
        summary('4000*(k+1)**3','Volume awal[[4000*(k+1)**3]]pi/3. r dua kali memberi faktor8; r setengah memberi[[500*(k+1)**3]]pi/3. Diameter terakhir sama dengan awal, volume tetap. 1,2,3 benar.')
    elif case==(19,5,2):
        stem(power([6,12]));allopts(power([2,4,3,5]))
        summary('3*(k+1)','Bola=[[288*(k+1)**3]]pi; satu limas=[[96*(k+1)**2]]pi. Banyak limas=[[3*(k+1)]], bilangan bulat, opsi C.')
    elif case==(19,5,5):
        stem(power([10,12,20,7]));opt(0,{'837,33':'round(2512*(k+1)**3/3,2)'});opt(1,power([600],3));opt(3,{'1437,33':'round(4312*(k+1)**3/3,2)'})
        summary('round(2512*(k+1)**3/3,2)','Air dipindah=[[600*(k+1)**3]]. Kapasitas bola=4312/3 kali faktor volume. Sisa kapasitas dibulatkan dua desimal=[[round(2512*(k+1)**3/3,2)]]. Air tidak tumpah; opsi A.')
    elif case==(19,5,8):
        stem(power([10]));opt(0,power([1000],3));opt(1,power([2000],3))
        summary('1000*(k+1)**3','Kubus[[1000*(k+1)**3]]; limas sepertiga, ruang kosong dua pertiga. Rasio limas:kosong1:2, bukan1:3. A,B,C benar.')
    elif case==(19,5,9):
        a.options[0]=scaled(a.options[0],{'3':'3+k','27':'(3+k)**3'})
        summary('(3+k)**3','Rusuk dikali[[3+k]] memberi volume[[(3+k)**3]]. r setengah memberi1/8; tinggi limas dua kali memberi2. Bola:limas pada opsiD=pi:1, bukan4:1. 1,2,3 benar.')
    elif case==(19,5,10):
        stem(dict(power([600],3),**power([5])));opt(0,power([1200],3));opt(1,power([1800],3));opt(2,power([5]))
        summary('600*(k+1)**3','V berbanding lurus dengan luas alas dan tinggi. Tinggi2 kali memberi[[1200*(k+1)**3]], alas3 kali memberi[[1800*(k+1)**3]]. Tinggi awal lebih besar daripada pengurang sehingga volume berkurang. Semua rusuk2 kali memberi8 kali volume, bukan2. 1,2,3 benar.')
    else:raise AssertionError(case)
    from expr import placeholders
    for text in [a.stem,*a.options,a.exp]:
        for name in placeholders(text)-a.variables.keys():
            assert name in ('m','d','r'),(a.qid,name)
            a.variables[name]=dict(gen='derived',expr=repr('{'+name+'}')+' if k == 0 else '+repr(name))
    return a


def nums(text):
    text=re.sub(r'!\[[^\]]*\]\([^)]*\)','',text)
    text=re.sub(r'\(Gunakan.*','',text,flags=re.S|re.I)
    text=re.sub(r'-\s+(?=\d)','-',text)
    return base_nums(text)


def check_math(q,c):
    from math import isqrt
    case=tuple(map(int,q.split('-')[1:]));v=nums(re.sub(r'(?m)^\(\d\)\s*','',c['stem']));opts=c['options'];p=[nums(o['text']) for o in opts]
    truth=None;result=None
    if case==(16,4,1):
        r,h=v;result=2*F(22,7)*r*(r+h)
    elif case==(16,4,3):
        r,s=v;assert s>r;result=F(44,7)*r
    elif case==(16,4,4):
        side,h=v;assert h>side/2;result=side*side+2*side*h
    elif case==(16,5,3):
        if len(v)==1:
            assert 'media/image7.png' in c['stem'];s,angle,claim=F(12),F(150),v[0]
        else:s,angle,claim=v
        result=s*angle/360
        truth=[claim==result and p[0]==[2,2*result],p[1][0]==result and claim!=result,False,angle==180 and claim==result]
    elif case==(16,5,5):
        if len(v)==4:
            assert 'media/image3.jpg' in c['stem'];side,h=F(10),F(13);claims=v
        else:side,h,*claims=v
        height2=h*h-(side/2)**2;result=side*side+2*side*h
        claims_truth=[claims[0]==side*side,claims[1]==side*h/2,claims[2]**2==height2,claims[3]==result]
        expected={j+1 for j,t in enumerate(claims_truth) if t};truth=[set(x)==expected for x in p]
    elif case==(16,5,6):
        count,scale=v;assert count==6;result=scale**2
        truth=[p[0]==[scale**2],p[1]==[scale**2],p[2]==[count],p[3]==[scale**3]]
    elif case==(16,5,9):
        area,volume=p[1];base,count,face,total=p[3];assert count==4
        side2=area/6;side=isqrt(int(side2));assert side*side==side2
        result=base+count*face;truth=[True,volume==side**3,True,total==result]
    elif case in ((17,4,6),(17,5,6)):
        x,y=v;result=y
        if case[1]==4:expected=[[x,-y],[y,x],[-y,x],[-2*x,-2*y]]
        else:
            u,w=p[2][:2];expected=[[x,-y],[-x,-y],[x+u,y+w],[2*x,2*y]]
        truth=[values[-2:]==pair for values,pair in zip(p,expected)]
    elif case==(17,4,7):
        slope,b=v;u,w=p[0][:2];shift=b+w-slope*u;result=-shift
        targets=[lambda x:slope*x+shift,lambda x:-slope*x-b,
                 lambda x:-slope*x+b,lambda x:slope*x+2*b]
        truth=[all(line_zero(o['text'].split('adalah')[-1].rstrip('.'),x,fn(x)) for x in (F(0),F(1))) for o,fn in zip(opts,targets)]
    elif case==(17,4,8):
        ox,oy,scale,X,Y=v;assert ox==oy==0;x,y=X/scale,Y/scale;result=x+y
        truth=[p[0]==[result],x>0 and y<0,p[2]==[-x,y],p[3][-2:]==[-x,-y]]
    elif case==(17,4,9):
        x,y=v;u,w=p[0][:2];result=x+u
        truth=[p[0][-2:]==[x+u,y+w],p[1]==[x,-y],p[2]==[-y,-x],p[3][-2:]==[-y,x]]
    elif case in ((17,4,10),(17,5,10)):
        area,=v;result=area
        if case[1]==4:truth=[True,p[1]==[area],p[2][1]==p[2][0]**2*area,p[3][1]==p[3][0]**2*area]
        else:truth=[p[0]==[area],p[1]==[area],p[2][-1]==area,p[3][1]==p[3][0]**2*area]
    elif case==(17,5,1):
        area,ox,oy,image_area=v;assert ox==oy==0;ratio=image_area/area
        result=F(isqrt(ratio.numerator),isqrt(ratio.denominator));assert result**2==ratio
        truth=[set(values)=={result,-result} for values in p]
    elif case==(17,5,8):
        x,y=v;result=x
        expected=[[y,x],[-y,-x],[y,-x],[-3*x,-3*y]]
        truth=[values[-2:]==pair for values,pair in zip(p,expected)]
    elif case==(17,5,9):
        x,y=v;u,w=p[0][:2];result=y
        truth=[p[0][-2:]==[x+u,y+w],p[1]==[-x,y],p[2][-2:]==[-x,-y],p[3][-2:]==[2*x,2*y]]
    elif case==(18,4,3):
        scale,=v;result=scale**2
        truth=[values==[scale,result] for values in p]
    elif case==(18,4,7):
        d,=v;area=F(22,7)*(d/2)**2;square=d*d/2;result=area
        truth=[p[0]==[area],p[1]==[d],p[2]==[square],p[3]==[area-square]]
    elif case==(18,4,8):
        length,width,t=v;initial=length*width;outer=(length+2*t)*(width+2*t);result=outer-initial
        alt=p[3][0];truth=[p[0]==[initial],p[1]==[outer],p[2]==[result],p[3][1]==(length+2*alt)*(width+2*alt)-initial]
    elif case==(18,4,9):
        length,width=v;rect=length*width;circle=F(22,7)*(width/2)**2;result=rect+circle
        truth=[p[0]==[rect],p[1]==[result],p[2]==[2*length+F(22,7)*width],p[3]==[width/2]]
    elif case in ((18,4,10),(18,5,7)):
        d,t=v;r=d/2;R=r+t;area=F(22,7)*r*r;result=F(22,7)*(R*R-r*r)
        if case[1]==4:truth=[p[0]==[r],p[1]==[area],p[2]==[R],p[3]==[result]]
        else:truth=[p[0]==[area],p[1]==[R],p[2]==[result],p[3]==[F(22,7)*d]]
    elif case==(18,5,3):
        side,claim_k,claim_area=v;result=3*side+F(22,7)*side/2;area=side*side+F(22,7)*(side/2)**2/2
        truth=[claim_k==result and claim_area==area,p[1]==[result] and claim_k!=result,
               p[2]==[area] and claim_area!=area,p[3]==[result,area] and (claim_k!=result or claim_area!=area)]
    elif case==(18,5,6):
        side,=v;square=side*side;half=F(22,7)*(side/2)**2/2;result=square+half
        truth=[p[0]==[square],p[1]==[half],p[2]==[3*side+F(22,7)*side/2],p[3]==[result]]
    elif case==(18,5,8):
        d1,d2=v;area=d1*d2/2;side2=(d1/2)**2+(d2/2)**2;side=F(isqrt(side2.numerator),isqrt(side2.denominator));assert side*side==side2
        result=area;truth=[p[0]==[area],p[1]==[side],p[2]==[4*side],p[3][0]**2*p[3][1]==area]
    elif case==(18,5,9):
        length,width,tx,ty=v;area=length*width;tile=tx*ty/10000;result=area/tile
        one,package,claimed=p[3];assert one==1;truth=[p[0]==[area],p[1]==[tile],p[2]==[result],claimed==result/package]
    elif case==(18,5,10):
        length,width,d=v;assert width==d;area=length*width;cut=F(22,7)*(d/2)**2/2;result=area-cut
        truth=[p[0]==[area],p[1]==[cut],p[2]==[result],p[3]==[2*length+width+F(22,7)*d/2]]
    elif case==(19,4,5):
        s,h,S,H=v;result=S*S*H/(s*s*h)
    elif case==(19,4,7):
        r,side,h=v;ball=F(4,3)*r**3;result=side*side*h/3
        truth=[p[0]==[ball],p[1]==[result],p[2][0]*ball==p[2][1]*result,False]
        assert ball*F(314,100)*8>result
    elif case==(19,4,8):
        first,second,out1,out2=p[1];assert first==out1==1;result=second**3
        truth=[p[0]==[3],out2==result,False,p[3]==[1,6]]
    elif case==(19,4,9):
        base,height,H=v;area=base*height/2;result=area*H
        truth=[p[0]==[area],p[1]==[result],p[2][1]==area*p[2][0],p[3][1]==p[3][0]*H]
    elif case==(19,4,10):
        r,=v;result=4*r**3
        truth=[p[0]==[result,F(3)],p[1][1]==(p[1][0]/r)**3,
               p[2][1]/p[2][2]==F(4,3)*p[2][0]**3,p[3][1]==(p[3][0]/(2*r))**3]
    elif case==(19,5,2):
        r,side,h=v;result=(F(4,3)*r**3)/(side*side*h/3);assert result.denominator==1
    elif case==(19,5,5):
        base,alt,H,r=v;water=base*alt*H/4;ball=F(4,3)*F(22,7)*r**3;assert ball>water
        exact=ball-water;result=F(round(exact*100),100)
        truth=[p[0]==[result],False,water==ball,p[3]==[result]]
    elif case==(19,5,8):
        side,=v;result=side**3;truth=[p[0]==[result,3],p[1]==[2*result,3],True,p[3]==[1,2]]
    elif case==(19,5,9):
        scale,claimed=p[0];result=scale**3
        truth=[claimed==result,True,True,False]
    elif case==(19,5,10):
        volume,minimum=v;result=volume
        decrement=p[2][0];assert minimum==decrement and minimum>0
        truth=[p[0]==[2*volume],p[1]==[3*volume],True,p[3][-1]==8]
    else:raise AssertionError(case)
    if truth is None:truth=[values==[result] for values in p]
    assert [o['correct'] for o in opts]==truth,(q,v,p,truth)
    assert sum(truth)==(1 if q.startswith('pg-') else 3),(q,truth)
    assert nums(c['explanation'])[0]==result,(q,c['explanation'],result)


def build_numeric():
    from bank import OriginalBank
    from config_store import validate_config
    from lint import reproduce_original
    from engine import assemble,build_values
    from filters import validate_candidate,signature
    bank=OriginalBank(DATA/'q0_bank.csv');outputs={}
    for e in numeric_entries():
        a=author(e);o=bank.get(a.qid);cfg=a.config(o)
        assert validate_config(cfg,o)==[],(a.qid,validate_config(cfg,o))
        assert reproduce_original(o,cfg)==([],[]),(a.qid,reproduce_original(o,cfg))
        unique=set()
        for k in range(31):
            c=assemble(cfg,build_values(cfg,lambda name,spec:k));check_math(a.qid,c)
            if k:
                assert not validate_candidate(c,o,[]),(a.qid,k,validate_candidate(c,o,[]))
                unique.add(signature(c['stem'],c['options']))
        assert len(unique)==30,(a.qid,len(unique))
        path=ROOT/'configs'/a.qid/'v1.json'
        if path.exists():assert json.loads(path.read_text(encoding='utf8'))==cfg,f'Refusing overwrite: {path}'
        outputs[path]=cfg
    for path,cfg in outputs.items():
        path.parent.mkdir(exist_ok=True)
        if not path.exists():dump(path,cfg)
    metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
    for e in numeric_entries():metadata[e['question_id']]['generator_status']='IMPLEMENTED'
    dump(DATA/'question_metadata.json',metadata)
    print(f'Numeric configs: {len(outputs)}; all 1178 input cases verified.')


def main():
    revise_sources();build_numeric()
    from stock_drill_16_19_level45 import build_stock
    build_stock()


if __name__=='__main__':main()
