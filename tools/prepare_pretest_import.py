"""Faithful Pretest intake + per-item academic audit; no DB/network writes."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/audits/2026-10-28-pretest'
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))

# Each entry records a separately solved answer and checks all distractors/statements.
# For MCMA use statement numbers; for CATEGORY use a truth string in row order.
EVIDENCE = {
1: [
('B', '-4/5 < -3/4 < 3/5 < 5/8; only B preserves all adjacent inequalities.'),
('13', 'sqrt(16)=4 rational; sqrt(7) irrational since 7 is not a square; -5 integer/non-natural; repeating 12/99=4/33 rational. Truth 1010.'),
('010', '5-3 != 3-5 disproves commutativity. Z+Z is contained in Z. 6/4=3/2 not in Z disproves division closure.'),
('D', '3(4+5)=27; 3*4+5=17. Distribution requires both terms. A/B assert invalid equality, C incorrectly restricts distribution.'),
('A', '36/4*2=18 (left to right); 24-18+5=11, distinct from -1,16,29.'),
('12', '2^5*4^2/8^2=8; (3^2)^3*3^-2=81=3^4; sqrt(64)=8 !=16; 5^0+5^-1=6/5 !=1/5. Truth 1100.'),
('C', '6/sqrt(3)=2sqrt(3), sqrt(48)=4sqrt(3), sqrt(27)=3sqrt(3); coefficient 3, not 7,9,1.'),
('A', 'A=150000*(4/5)-10000=110000; B=(150000-10000)*(4/5)=112000. A cheaper by 2000; remaining descriptions false.'),
('123', '144<150<169; 12.2^2=148.84<150<150.0625=12.25^2, rounds to12.2. sqrt(150)<12.5 means closer to12; statement4 false.'),
('101', '49.8*2.03=101.094 reasonably about100; 64<80<81 means sqrt80 between8 and9; 19.6+30.7=50.3 about50.'),
('D', '180=2^2*3^2*5. Distractor products are120,300,450; D=180.'),
('12', 'gcd(48,180)=12; lcm=48*180/12=720. Divisors of12 are1,2,3,4,6,12 (6, not8).8640 is product, not lcm.'),
('B', 'gcd(54,90)=18; lcm=270; quotient15, unlike5,18,270.'),
('C', 'lcm(12,18,30)=2^2*3^2*5=180 sec=3min;360 is a later common multiple. 60 and540 are not the least.'),
('12', '1cm maps25km;6cm=150km;80km/25=3.2cm;1cm !=2.5km;10cm=250km !=2500km.'),
('011', 'All distance/time ratios45; J=45t passes origin;45*6.5=292.5. Thus variable-speed claim false, other two true.'),
('A', 'A=36000/2=18000/L; B=15000/(3/4)=20000/L; C=28500/(3/2)=19000/L. Only A,C,B orders ascending.'),
('12', 'Under equal constant productivity: workers*time fixed; price=unitPrice*count; speed*time=distance; machines*time fixed. Truth1100.'),
('B', 'Work240 worker-days; after8 days96 used,144 remain;9 workers need16 extra days; total24, not22,26,28.'),
('110', '240/60=4h; saving1h requires240/3=80km/h;70km/h takes24/7h, saving4/7h=34.2857min, not1h.'),
],
2: [
('C', '6x-15=4x+7 =>2x=22 =>x=11. Substituting6,1,16 fails original equation.'),
('A', '-3x>12 =>x<-4; dividing by negative reverses inequality. Other proposed half-lines include counterexamples.'),
('D', 'Current age sum62-2*5=52; child52/4=13; father39. Other options13,44,52 fail constraints.'),
('124', 'Second row is twice first, rank1 with2unknowns, infinitely many real solutions and coincident lines. (3,2) and(6,0) both work; no uniqueness.'),
('110', '2-3x>=14 iff x<=-4. Step1 valid, Step2 must reverse sign; x=0 gives2<14.'),
('B', 'Coefficients: a:4-2=2,b:7+3=10,constant:-5+8=3. Other three coefficient tuples differ.'),
('13', '(x+3)(x-2)=x^2+x-6; x^2-9=(x-3)(x+3), not(x-3)^2;2x(x+3) exact; (x-4)^2=x^2-8x+16. Truth1010.'),
('C', '3(2x-4)-2(x-5)=6x-12-2x+10=4x-2. Remaining coefficient/constant pairs differ.'),
('12', 'P=2(3x+2+x+4)=8x+12; area=3x^2+14x+8; atx2 area8*6=48 not56; constant8 not6.'),
('011', '(x+2)^2=x^2+4x+4 (x1 gives9 not5);2(x+3)+x=3x+6;(x-2)^2=x^2-4x+4.'),
('A', 'f(-2)=2*4+6+1=15; distinct from3,-1,7.'),
('D', 'Evaluate domain in order: f(-1),f0,f1,f2,f3=3,0,-1,0,3. Deduplicate gives{-1,0,3}; no8, no1/2.'),
('124', 'Input2 maps toboth b,c so notfunction. Domain1,2,3; rangea,b,c. Deleting(2,c) leaves one output for everyinput. Truth1101.'),
('B', 'A-B=3000-500x; negative iff x>6. Equal at6 withboth29000. A,C not exact solution sets; D is a sufficient subset, not the full condition.'),
('011', 'Physical constraints t>=0 and60-4t>=0 imply0<=t<=15. Slope-4 downward; zero at15. Not all real t.'),
('A', 'Arithmetic a5,d4 =>U15=5+14*4=61; alternatives65,60,57 differ.'),
('14', 'Ratio1/3;U5=81/81=1 not1/3; positive starting terms with0<r<1 decrease;81*(1/3)^(n-1)=3^(5-n).'),
('C', 'n=1+(51-3)/4=13;sum13*(3+51)/2=351; alternatives702,324,378 differ.'),
('12', 'Monthly deposits:U10=20000+9*5000=65000;S10=10*(20000+65000)/2=425000;U12=75000,S12=570000 not540000;U10!=S10.'),
('101', 'U10=12+9*3=39; S10=10*(12+39)/2=255 not250;255>=250 with5spare. Truth101.'),
],
3: [
('C', 'Co-interior angles betweenparallel lines sum180;Q=180-72=108, not72,118,98. Diagram putsP,Q on same side inside.'),
('124', 'C=180-50-60=70; exteriorC=180-70=110;B+C=130 not110;interior+exterior=180. Truth1101.'),
('A', 'Cylinder net rectangle: circumference2*(22/7)*7=44 and height10. Other dimensions fail one condition.'),
('D', 'Same sun angle/upright objects:height/shadow=1.5/0.9=5/3;tree6*(5/3)=10m; remaining options mismatch.'),
('123', 'SAS gives congruence andAC=PR. For statement3 withAB=PQ=6,BC=QR=8,angleA=angleP: letAC=z>0. Cosine law gives z^2-12*cos(A)*z-28=0. Product of roots=-28<0, exactlyonepositiveroot; SSA here DOES guarantee congruence. A != C since opposite sides8 !=6, so statement4 false. Sourcekey12 omits3.'),
('011', 'Scale ratio2/3 =>area ratio4/9;largearea20*9/4=45. Rina useslinear ratio30 incorrectly.'),
('B', 'Slant sqrt(6^2+8^2)=10; fullsurface=pi*6*(6+10)=96pi. 84pi usesheight,60pi omitsbase,132pi wrong.'),
('C', '(3,-2)+(-5,4)=(-2,2); others fail one component.'),
('B', 'Clockwise90 maps(x,y)to(y,-x), so(-2,5)to(5,2). Othertriples notthismap.'),
('13', 'Reflections of(4,-1):X=(4,1),Y=(-4,-1),y=x=(-1,4),y=-x=(1,-4). Truth1010.'),
('A', 'Determinant areaabs((3-1)*(4-1))/2=3; dilatedareak^2*3=27. Not9,18,36.'),
('14', 'Translations/rotations/reflections areisometries;dilation2 rescalesnondegenerate lengths by2 andisnotcongruent;reflection reversesorientation. Truth1001.'),
('110', 'Origin dilation3 gives(9,12); center(1,2) plus3*((3,4)-(1,2))=(7,8), so studentusedwrongcenter.'),
('D', 'r28/2=14; area(22/7)*196=616cm2.88 circumference,308halfarea,2464usingdiameterasradius.'),
('101', 'Arc=(60/360)*2*(22/7)*21=22;area=(1/6)*(22/7)*441=231not462;perimeter22+42=64.'),
('123', 'Twodiameters=28 =>r7; square784;fourdisks4*(22/7)*49=616;gap784-616=168not336. Truth1110.'),
('12', 'Cylinder(22/7)*49*10=1540;cone(1/3)*(22/7)*49*12=616;pyramid6^2*10/3=120not360;sphere(4/3)*pi*27=36pinot12pi.'),
('B', 'Cylinder1540 +cone(1/3)*(22/7)*49*6=308 =>1848. Not1540,2464,2156.'),
('C', 'Vnew/Vold=(3/2)^2*(4/5)=9/5=1.8 =>increase80%. Additive30%,120%,25% allfalse.'),
('110', '120*50*60/1000=360L;360/12=30min;2/3remainingneeds20minnot15. Truth110.'),
],
4: [
('A', '(12+15+18+15+20)/5=80/5=16; otheroptions15,18,17false.'),
('C', 'Sorted3,4,7,8,9,12;median(7+8)/2=7.5;others7,8,6.5false.'),
('110', 'Total12+8+6+4=30;footballangle12/30*360=144;basket8/30*100=26.6667%not20%. Truth110.'),
('14', 'Minutesquestionmeasurestargetvariable, enjoymentdoesnot;singleclassnotnecessarilyrepresentative;randomsamplingineveryclassimprovesclasscoverage. Truth1001;unequalclasssizesrequireproportionalallocation/weightsforunbiasedmean.'),
('B', 'Observed40,45,50,55,60 trendpredicts65 butdoesnotlogicallyforceSaturdayattendance. A/Cconfusepredictionwithcertainty;70notincrement5.'),
('124', 'Sum63,n7,mean9;sortedmiddle7;9>7 notsmaller;max20-min4=16. Truth1101.'),
('D', 'Weightedtotal5*2+6*3+7*8+8*5+9*2=142;frequency20;mean7.1,not7,7.2,7.5.'),
('', 'RangeA20 < rangeB35 onlycomparesmax-min,notgeneralconcentration. CounterexampleA=[70,70,90,90] mean80 range20 var100;B=[62.5,97.5]+[80]*98 mean80 range35 var6.125. Bcanbemoreconcentrateddespitelargerrange. Nooptionisuniversallyjustifiedwithoutdefiningconsistencyasrange.'),
('124', 'Xsum37mean7.4,median7,mode7,range3;Ysum36mean7.2,median8,mode8,range3. Truth1101.'),
('101', 'Beforemean50/5=10;after90/6=15;bothmedians10. Medianresistanttooutlier,sointhisdatasetbettertypicalcenter. Truth101.'),
('D', 'Understandardfairdie1..6,primes2,3,5 are3of6 =>1/2;alternatives1/3,2/3,1/6wrong.'),
('B', 'Relativefrequency21/50=.42;29/50countsotherface,1/2theoreticalnotobserved,21/29wrongdenominator.'),
('124', 'Tenphysicalcardsdistinctoutcomes;MATEMATIKAfreqM2,A3,T2,E1,I1,K1;P(A)=3/10;vowels5/10=1/2not2/5;P(T)=2/10=1/5.'),
('124', 'Total10;blue3/10;notgreen8/10=4/5;adding2redgivestotal12with5nonred =>5/12not1/2;red5/10=1/2.'),
('C', 'FairdieP6=1/6;observed90/600=3/20;absolutedifference1/6-3/20=1/60. Otherfractionsdiffer.'),
('13', '210/1200=7/40;fairP4=1/6not1/4;LLNconvergenceofrelativefrequencytoPforindependentrepeatedtrials;finitefrequencyneednotequalP. Truth1010,notamonotonicguarantee.'),
('100', '1..20contains10evens,8primes(2,3,5,7,11,13,17,19),4multiplesof5;probabilities1/2,2/5,4/5. Lasttwoassert7/20and3/4false.'),
('A', 'WithfairdieP(>4)=2/6=1/3;uniformballred4/10=2/5;2/5-1/3=1/15>0. Prefergame2bywinprobability;B/C/Dwrong.'),
('B', 'Sample6/80=3/40=7.5% >6%;estimatedpopulationdefects2000*3/40=150vsallowed120. Evidenceisestimatefromsample,notcertaintyaboutall2000.'),
('101', 'Observed7/10notproofp=.7orbiasedcoin;faircoiniidfrequencyconvergesto1/2notguaranteedexactlyatspecificn. Truth101.'),
]}

NOTES = {
 (1,18): ('ASSUMPTION', 'Perbandingan pekerja/mesin mengasumsikan produktivitas sama dan tetap.', 'Tambahkan asumsi produktivitas seragam dan tetap agar eksplisit.'),
 (2,9): ('CLARITY', 'Panjang 3x+2 dan x+4 harus positif; domain fisik x>-2/3 belum tertulis.', 'Tambahkan x>-2/3; kunci tidak berubah.'),
 (2,14): ('CLARITY', 'x>12 pada opsi D juga kondisi cukup, tetapi bukan himpunan penyelesaian lengkap.', 'Tanyakan himpunan seluruh jarak yang memenuhi A(x)<B(x), agar hanya B yang tepat.'),
 (2,19): ('CLARITY', 'Tabungan tiap bulan dapat dibaca sebagai saldo atau setoran; solusi memakai setoran bulanan.', 'Ganti tabungannya dengan besar setoran bulanannya, tanpa mengubah angka/kunci.'),
 (3,5): ('ERROR', 'SSA tidak selalu ambigu. Sisi di depan A=8 lebih besar daripada sisi AB=6; tepat satu segitiga memenuhi data, sehingga pernyataan3 benar.', 'Draf: kunci Pernyataan1,2,3 dan perbaiki pembahasan3. Alternatif: jadikan pernyataan3 klaim SSA umum tanpa ukuran6,8. Memerlukan review; belum diterapkan.'),
 (3,8): ('CLARITY', 'Vektor translasi dalam OMML sumber ditulis (-5 4) sebagai teks satu baris tanpa koma/pemisah koordinat.', 'Draf: tampilkan sebagai vektor kolom (-5;4) atau pasangan (-5,4). Belum mengubah notasi sumber; spasi tampilan saja dipertahankan eksplisit.'),
 (4,4): ('CLARITY', 'Sampel tiap kelas lebih mencakup kelompok, tetapi peluang adil/mean tak bias perlu alokasi proporsional atau pembobotan jika ukuran kelas berbeda.', 'Batasi alasan pada cakupan semua kelas; sebut alokasi proporsional atau bobot bila menyatakan peluang setara.'),
 (4,8): ('ERROR', 'Jangkauan lebih kecil tidak cukup menyimpulkan semua data lebih terkumpul di pusat; contoh tandingan tersedia.', 'Draf: definisikan konsistensi pada soal secara khusus menurut jangkauan dan ubah alasan menjadi rentang min–maks lebih sempit; atau sediakan data/simpangan baku. Belum diterapkan.'),
 (4,11): ('ASSUMPTION', 'Peluang1/6 per muka memerlukan dadu adil dengan mata1–6.', 'Tambahkan dadu seimbang/bersisi1–6.'),
 (4,13): ('CLARITY', '10 titik sampel benar bila hasil elementer adalah identitas kartu, bukan hanya enam huruf berbeda.', 'Nomori kartu atau jelaskan tiap kartu sebagai hasil elementer yang berbeda.'),
 (4,15): ('ASSUMPTION', 'Peluang teoretis1/6 memerlukan dadu adil.', 'Tambahkan dadu seimbang.'),
 (4,16): ('CLARITY', 'Dadu adil dan percobaan independen diperlukan; ungkapan makin banyak makin dekat jangan dimaknai monoton.', 'Nyatakan dadu seimbang dan pengulangan independen; gunakan cenderung mendekati tanpa menjamin setiap tambahan lemparan lebih dekat.'),
 (4,18): ('ASSUMPTION', 'Perbandingan peluang memakai dadu adil dan pengambilan bola seragam; hadiah/biaya diasumsikan sama atau tujuannya memaksimalkan peluang menang.', 'Nyatakan dadu seimbang dan tujuan memilih peluang menang terbesar.'),
 (4,19): ('CLARITY', 'Sampel menunjukkan estimasi melampaui toleransi, bukan bukti pasti proporsi seluruh produksi.', 'Gunakan diperkirakan belum memenuhi toleransi berdasarkan sampel pada opsi dan kesimpulan.'),
}

def cell_text(cell):
    return '\n'.join(b['text'] if b['type']=='paragraph' else table_text(b) for b in cell['blocks']).strip()

def table_text(block):
    # Plain rich-text renderer has no HTML table support; preserve explicit row/column labels.
    rows = [[cell_text(c) for c in r] for r in block['rows']]
    return '\n'.join(' | '.join(r) for r in rows)

def display_math(text):
    # Literal Word set braces must be visible rather than LaTeX grouping tokens.
    text = re.sub(r'\$\{([^${}]+,[^${}]+)\}\$', lambda m: '$\\{'+m[1]+'\\}$', text)
    text = re.sub(r'\$([A-Za-z]?)=\{([^${}]+,[^${}]+)\}\$', lambda m: '$'+m[1]+'=\\{'+m[2]+'\\}$', text)
    text = re.sub(r'\$([^$]+)\$', lambda m: '$'+re.sub(r'(?<!\\)%',r'\\%',m[1])+'$', text)
    text = re.sub(r'\$([^$]+)\$', lambda m: '$'+m[1].replace('\u2005',r'\;').replace('\u200b','')+'$', text)
    return text.replace(r'T=\left(−5 4 \right)', r'T=\left(−5\;4\right)')

def prepare(write=True):
    packages=[]; media=[]; audits=[]; protected={}
    scope=read(OUT/'taxonomy-snapshot.json')
    for chapter in range(1,5):
        base=ROOT/f'docs/sources/incoming/2026-10-28-pretest-bab-{chapter}'
        manifest=read(base/'manifest.json'); extraction=read(base/'extracted.json')
        assert sha((base/'source.docx').read_bytes())==manifest['source_sha256']
        for name,digest in manifest['files_sha256'].items():
            assert sha((base/name).read_bytes())==digest
            protected[(base/name).relative_to(ROOT).as_posix()]=digest
        assert not extraction['unhandled_math_constructs'] and not extraction['unresolved_numbering_paragraphs']
        source_questions=read(base/'question-index.json'); questions=[]
        appendix=next(b for b in extraction['blocks'] if b['type']=='table' and cell_text(b['rows'][0][0])=='No')
        recap={int(cell_text(row[0])):cell_text(row[-1]) for row in appendix['rows'][1:]}
        chapter_code={1:'CH-BIL',2:'CH-ALG',3:'CH-GP',4:'CH-DP'}[chapter]
        chapter_db=next(ch for ch in scope['chapters'] if ch['code']==chapter_code)
        assert chapter_db['status']!='ARCHIVED'
        for source in source_questions:
            number=source['source_question_number']; qid=f'pretest-b{chapter}-q{number:02d}'
            selected=[]
            for b in source['blocks']:
                if b['type']=='paragraph' and re.match(r'^\s*(LAMPIRAN\b|SUB\s+BAB\b|BAB\s+\d)',b['text'],re.I):break
                selected.append(b)
            # Earlier intake includes a metadata header and the next subchapter/appendix at the tail.
            header=selected[0]['text']; fmt='CATEGORY' if 'Kategori' in header else 'MULTIPLE_CHOICE_MULTIPLE_ANSWER' if 'MCMA' in header else 'SINGLE_CHOICE'
            indicator_line=next(b['text'] for b in selected if b['type']=='paragraph' and b['text'].startswith('Indikator'))
            indicator,cognitive=re.search(r'Indikator\s+(\d+\.\d+)\s*\|\s*Level Kognitif:\s*(C[345])',indicator_line).groups()
            ind=int(indicator.split('.')[0]); subcode=f'SC-DRILL-IND-{ind:03d}'; compcode=f'IND-{ind:03d}'
            sub=next(s for s in scope['subchapters'] if s['code']==subcode and s['chapter_id']==chapter_db['id'])
            comp=next(c for c in scope['competencies'] if c['code']==compcode and c['subchapter_id']==sub['id'])
            assert sub['status']!='ARCHIVED' and comp['status']!='ARCHIVED'
            ki=next(i for i,b in enumerate(selected) if b['type']=='paragraph' and b['text'].startswith('KUNCI JAWABAN'))
            raw_key=selected[ki]['text'].split(':',1)[1].strip()
            assert raw_key==recap[number],(qid,raw_key,recap[number])
            ei=next(i for i,b in enumerate(selected) if b['type']=='paragraph' and re.match(r'^Pembahasan\s*:',b['text'],re.I))
            content=selected[ki+1:ei]; options=[]; stem=[]; assets=[]
            def rich(block,placement='STEM',item_id=None):
                value=block['text'] if block['type']=='paragraph' else table_text(block)
                def image_replace(match):
                    file=base/match[1]; data=file.read_bytes(); assetid=f'diagram-{len(assets)+1}'
                    asset=dict(externalId=qid,assetId=assetid,textMarker=f'[[asset:{assetid}]]',placement=placement,itemId=item_id,
                        assetOrder=len(assets)+1,altText=f'Gambar sumber Pretest Bab {chapter}, soal {number}.',objectKey=None,
                        sha256=sha(data),contentType='image/png',byteLength=len(data),bucket='numora-bucket')
                    assert data[:8]==b'\x89PNG\r\n\x1a\n'
                    assets.append(asset);media.append(dict(**asset,contentVersion=1,filePath=file.relative_to(ROOT).as_posix()))
                    return asset['textMarker']
                return display_math(re.sub(r'!\[Source image [^\]]+\]\((media/[^)]+)\)',image_replace,value)).strip()
            for block in content:
                if fmt=='CATEGORY' and block['type']=='table' and len(block['rows'][0])==3 and [cell_text(c) for c in block['rows'][0]][1:]==['Benar','Salah']:
                    for row in block['rows'][1:]:
                        value=cell_text(row[0]);match=re.match(r'^([A-Z])\.\s*(.*)$',value,re.S);assert match
                        options.append({'id':match[1],'content':{'text':display_math(match[2])}})
                elif block['type']=='paragraph' and fmt=='SINGLE_CHOICE' and re.match(r'^[A-D]\.\s',block['text']):
                    match=re.match(r'^([A-D])\.\s*(.*)',rich(block,'OPTION',block['text'][0]),re.S)
                    options.append({'id':match[1],'content':{'text':match[2]}})
                elif block['type']=='paragraph' and fmt=='MULTIPLE_CHOICE_MULTIPLE_ANSWER' and re.match(r'^\[\s*\]\s*Pernyataan\s+\d+:',block['text']):
                    match=re.match(r'^\[\s*\]\s*Pernyataan\s+(\d+):\s*(.*)',block['text'],re.S)
                    options.append({'id':match[1],'content':{'text':rich(dict(block,text=match[2]),'OPTION',match[1])}})
                else:
                    assert not options, (qid,'Unexpected block after options',block)
                    value=rich(block)
                    if value:stem.append(value)
            explanation='\n\n'.join(v for b in selected[ei+1:] if (v:=rich(b,'EXPLANATION')))
            assert len(options)==(3 if fmt=='CATEGORY' else 4),(qid,len(options))
            if fmt=='SINGLE_CHOICE':answer={'optionId':raw_key}
            elif fmt=='MULTIPLE_CHOICE_MULTIPLE_ANSWER':answer={'optionIds':re.findall(r'Pernyataan\s+(\d+)',raw_key)}
            else:answer={'categoryByStatementId':{a:'TRUE' if b=='Benar' else 'FALSE' for a,b in re.findall(r'([A-Z])\.\s*(Benar|Salah)',raw_key)}}
            independent,proof=EVIDENCE[chapter][number-1]
            if fmt=='SINGLE_CHOICE':independent_answer=independent or None;matches=independent==raw_key
            elif fmt=='MULTIPLE_CHOICE_MULTIPLE_ANSWER':independent_answer=list(independent);matches=independent_answer==answer['optionIds']
            else:independent_answer={chr(65+i):'TRUE' if v=='1' else 'FALSE' for i,v in enumerate(independent)};matches=independent_answer==answer['categoryByStatementId']
            note=NOTES.get((chapter,number));error=note is not None and note[0]=='ERROR'
            audit=dict(id=qid,chapter=chapter,number=number,type=fmt,source_indicator_code=indicator,cognitive_level=cognitive,
                source_docx_sha256=manifest['source_sha256'],source_paragraph_start=source['paragraph_start_index'],
                source_key=raw_key,appendix_key_matches=True,independent_answer=independent_answer,
                validity_status='BERMASALAH' if error and (chapter,number)==(4,8) else 'BENAR',
                key_status='BERMASALAH' if error else 'BENAR',explanation_status='BERMASALAH' if error else 'PERLU_KLARIFIKASI' if note and (chapter,number) in ((4,4),(4,16),(4,19)) else 'BENAR',
                independent_proof=proof,source_key_matches_solution=matches,
                option_truth={o['id']:o['id']==independent if fmt=='SINGLE_CHOICE' else o['id'] in independent if fmt=='MULTIPLE_CHOICE_MULTIPLE_ANSWER' else independent_answer[o['id']]=='TRUE' for o in options},
                finding=note[1] if note else None,proposed_correction=note[2] if note else None,
                note_class=note[0] if note else None,image_count=len(assets),
                image_review='VISUALLY_INSPECTED_SOURCE_LABELS_AND_GEOMETRY' if assets else 'NOT_APPLICABLE',
                disposition='HOLD_FOR_ACADEMIC_REVIEW' if error else 'DRAFT_WITH_CLARIFICATION' if note else 'DRAFT_AUDITED',
                curriculum_approval=False,generator_required=False)
            assert matches or error,(qid,'Unexplained key mismatch')
            audit['source_content_sha256']=sha(json.dumps(selected,ensure_ascii=False,sort_keys=True).encode())
            audits.append(audit)
            metadata=dict(sourceLevelNumber=None,sourceOrder=number,source='Owner-supplied pretest DOCX',
                sourceIndicatorCode=indicator,cognitiveLevel=cognitive,sourceDocxSha256=manifest['source_sha256'],
                sourceArchive=base.relative_to(ROOT).as_posix(),sourceParagraphStart=source['paragraph_start_index'],
                sourceQuestionNumber=number,sourceChapter=chapter,assetManifest=assets,
                academicAudit=audit,sourceSubchapterHeading='Preserved in source archive; runtime indicator taxonomy verified',
                transportNormalization=['Exclude next subchapter heading and appendix from item','Source tables represented with explicit row/column separators','Escape literal set braces and percent signs in LaTeX','Preserve mathematical spacing with explicit TeX spacing; remove zero-width Word superscript bases'])
            if fmt=='CATEGORY':metadata['categories']=[{'id':'TRUE','label':'Benar'},{'id':'FALSE','label':'Salah'}]
            questions.append(dict(externalId=qid,type=fmt,chapterCode=chapter_code,subchapterCode=subcode,competencyCode=compcode,
                difficulty={'C3':'EASY','C4':'MEDIUM','C5':'HARD'}[cognitive],stem={'text':'\n\n'.join(stem)},options=options,
                answer=answer,explanation={'text':explanation},metadata=metadata))
        assert len(questions)==20 and Counter(q['metadata']['cognitiveLevel'] for q in questions)=={'C3':5,'C4':10,'C5':5}
        packages.append(dict(sourceNamespace=f'NUMORA_PRETEST_BAB_{chapter}_20261028',
            package=dict(familyCode=f'NUMORA-PRETEST-BAB-{chapter}',packageVersion=1,name=f'Pretest Bab {chapter} - {chapter_db["name"]}',
                assessmentType='PRETEST',isDemo=False,chapterId=chapter_db['id'],source=dict(sourceNamespace=f'NUMORA_PRETEST_BAB_{chapter}_20261028',
                    sourceName=f'Pretest Bab {chapter} - DOCX pemilik 28 Oktober 2026',sourceReference=base.relative_to(ROOT).as_posix())),questions=questions))
    assert len(media)==35 and len(audits)==80
    result=dict(date='2026-10-28',targetStatus='DRAFT',published=False,generatorsCreated=0,packages=packages,media=media,audit=audits,protectedSourceSha256=protected)
    if write:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'import-input.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (OUT/'audit.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        cols=['id','chapter','number','type','source_indicator_code','cognitive_level','validity_status','key_status','explanation_status','source_key','independent_answer','disposition','finding','proposed_correction','independent_proof']
        with (OUT/'audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,cols);writer.writeheader();writer.writerows({k:a[k] for k in cols} for a in audits)
        for c in range(1,5):
            lines=[f'# Audit Pretest Bab {c}', '', 'Pemeriksaan seluruh soal/opsi, kunci, pembahasan, dan gambar sumber. Tidak ada koreksi yang diterapkan.','']
            for a in (a for a in audits if a['chapter']==c):
                lines.extend([f"## Soal {a['number']} — {a['disposition']}",'',f"Validitas: {a['validity_status']}; kunci: {a['key_status']}; pembahasan: {a['explanation_status']}.",f"Kunci sumber: {a['source_key']}. Jawaban independen: {a['independent_answer']}.",'',a['independent_proof'],''])
                if a['finding']:lines.extend(['Temuan: '+a['finding'],'Usulan (belum diterapkan): '+a['proposed_correction'],''])
            (OUT/f'bab-{c}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        counts=dict(Counter(a['disposition'] for a in audits))
        (OUT/'README.md').write_text('# Audit dan impor Pretest Bab 1–4\n\nTanggal: 2026-10-28. **80 original, 4 paket, 35 gambar sumber; tanpa generator.**\n\n'
            'ENGINEERING DECISION — instruksi pemilik: audit seluruh pretest lalu masukkan database. Impor DRAFT tidak berarti publikasi/persetujuan Curriculum. Sumber dan kunci dipertahankan; usulan koreksi terpisah.\n\n'
            f'Hasil: {counts}. Dua temuan utama: Bab 3 soal 5 (kunci SSA), Bab 4 soal 8 (inferensi penyebaran dari jangkauan). Lihat laporan per bab, audit.csv dan audit.json untuk bukti seluruh opsi/pernyataan.\n\n'
            'Keempat rekap kunci lampiran cocok dengan kunci pada soal. Komposisi tiap bab: 10 PG, 6 MCMA, 4 Kategori; C3=5, C4=10, C5=5. Semua 35 gambar ditinjau langsung: label dan konteks cocok, tidak ada temuan angka/diagram yang mengubah jawaban. Proporsi ilustrasi tidak dipakai sebagai data ukur.\n\n'
            'Pemetaan menggunakan master indikator existing; kode sumber seperti 15.3 disimpan utuh sebagai provenance. Akhiran bukan otomatis level Drill. sourceLevelNumber dan levelId kosong. Difficulty EASY/MEDIUM/HARD hanya mengikuti label Mudah/Sedang/Sulit dalam DOCX, bukan kalibrasi IRT.\n\n'
            'Batas audit: pemeriksaan akademik oleh agen beserta bukti per entri, bukan pengesahan tim Curriculum atau validasi psikometrik. Asumsi dadu adil, produktivitas seragam, bahasa estimasi dan rubrik tidak dilengkapi diam-diam. Status DB/R2 dicatat pada hasil operator setelah operasi; keberadaan input ini belum membuktikan impor.\n',encoding='utf-8')
    return result

if __name__=='__main__':
    d=prepare();print(json.dumps({'questions':len(d['audit']),'media':len(d['media']),'dispositions':dict(Counter(a['disposition'] for a in d['audit']))}))
