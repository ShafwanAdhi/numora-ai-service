"""Audit and source-only import; preserve declared keys, tables and raw provenance."""
import csv
import hashlib
import io
import json
import re
from collections import Counter
from html.parser import HTMLParser

from audit_original_questions import ROOT,source_entries

SOURCE=ROOT/'docs/sources/incoming/2026-10-19-indikator-20-23'
DATA=ROOT/'variant_gen/data/drill-1-indicators-20-23-levels-4-5'
SOURCE_HASH='74a6f81a2c65ed9f11fc824f1f999c13fb79faa2887cf5db9311df9b85a19e57'

# Independent option-by-option review, Q31..Q50 in source order. Do not adopt
# corrected keys from explanations: contradictory source declarations stay held.
REVIEW={
20:[
 ('C','Only C relates both measured variables: study duration and mathematics score. A,D count students; B asks preferences.'),
 ('B','Books 2,4,3,6,5: maximum6 belongs to Dini; minimum2 Andi. Citra3<6; only B.'),
 ('B','Transport categories are nominal; counts45,20,15,20 total100. Bars compare category frequencies; no continuous/time/pair relation for other charts.'),
 ('B','The question leads with praise and combines benefit with making all students smarter; school name/numeric response/length do not fix that bias.'),
 ('C','Futsal40 is largest among this school sample100; neither largest count nor sample size establishes district representativeness. Tables can present categories.'),
 ('ABD','A measures reading duration, B material type, D completed books. C is judgmental, E measures policy agreement rather than actual reading habits.'),
 ('ABCD','Sorted70,75,80,80,85,90,90,90: sum660,n8,mean82.5,median82.5,mode90,range20. Values70,75 refute E.'),
 ('ABD','Current first-break canteen users can exclude nonusers and other schedules. Broader class/time sampling helps; n30 does not itself prove invalidity, and answers need not be identical.'),
 ('124','Mon80,Tue100,Wed70,Thu110: maxThu;100-80=20;Wed not max;80+70=150.'),
 ('124','Health, saving and superiority to canteen are distinct claims; split into neutral specific questions. Omitting answer choices does not make wording neutral.'),
 ('C','C directly measures sports-facility satisfaction on an explicit ordered scale. A,D lead the respondent; B concerns school liking rather than these facilities.'),
 ('B','Categories futsal80,basket50,music40,dance30 total200 have no continuous time order. Bars compare them; categories can also use tables or suitable pie charts.'),
 ('C','18/20 high scores in tutoring participants alone give neither baseline/control nor exclusion of confounders. Counts do not establish causation; participants can be surveyed.'),
 ('C','15 active classroom-phone users form a selected sample. Diverse respondents and neutral benefit/risk questions improve it; leading questions or replacing responses do not.'),
 ('C','Counts20,45,35 total100: >4h is35%, neither a majority nor the largest group. 2-4h is largest at45; it is not itself a majority.'),
 ('ABD','Multiple grades improve coverage; explicit last-month period improves recall/comparability; neutral wording reduces bias. Frequent visitors alone do not support claims about all students.'),
 ('ACE','60% is largest; bars compare categories. Sampling limits generalization; no scores or experiment demonstrate causation and not every student belongs to that group.'),
 ('ABD','Transport50,25,15,10 total100: bars compare counts,pie shows shares,title/labels aid reading. No time order; removing the smallest category distorts the complete data.'),
 ('13','Clear satisfaction scale and category bars support measurement. Selecting only fans biases sampling; altering unwanted responses violates data integrity.'),
 ('134','44+24+12=80;44/80=55%,the largest and a majority of respondents. It does not establish all-school support; report counts/percentages and examine sample coverage.'),
],
21:[
 ('B','Eight sorted values72,75,80,80,83,85,85,92: median=(80+83)/2=81.5. Frequency does not define median.'),
 ('C','3+4+5+5+8=25;mean5,median5. Mean is not greater; only C has both correct verdict and numbers.'),
 ('A','10,12,15,15,18,20,25: mode15,range25-10=15,median15,mean115/7. Only A.'),
 ('B','Initial sum375,n5,mean75. Add100:475/6=79.166...,greater75; median initial75 does not become new mean.'),
 ('C','A and B sums400,mean80,median80. Ranges20 and40 differ; equal center does not imply equal spread.'),
 ('ABD','4,6,6,8,11:sum35,mean7,median6,mode6,range7. C mode8 false; E7<6 false.'),
 ('ABC','65,70,75,80,80,85,95:sum550,mean550/7,median80,mode80,range30. Remove95:median(75+80)/2=77.5,not75.'),
 ('ACD','Both sums400,means80,medians80. A all distinct has no unique mode; B mode80. Ranges20,40; this alone cannot prove every B student is superior.'),
 ('1234','20,25,25,30,40:sum140,mean28,median25,mode25,range20. All four statements true, including B despite its false source label.'),
 ('4','A1,2,2,3,7 and B2,2,3,4,4 both sum15,mean3. Medians2 and3 differ. Ranges6 and2: only D is correct.'),
 ('B','60,70,75,80,85,100:median77.5; mean470/6 is influenced by extremes. No repeated mode; range40 measures spread,not center.'),
 ('B','100,110,120,130,540:median120,mean200,no mode,range440. Median resists the high540; alternative rationales are false.'),
 ('C','P constant10:mean10,range0;Q6,8,10,12,14:mean10,range8. Same mean and count do not imply identical distribution.'),
 ('A','Initial70,75,80,80,95:mean80,median80,range25. Replace70 with80:mean82,median80,range20.'),
 ('A','Ranges A28-20=8,B33-15=18; both medians24 and means24. Defined consistency uses smaller range,not larger maximum/variation.'),
 ('ABCD','65,70,75,80,110:sum400,mean80,median75,range45,no mode.110 shifts mean above75. Source omits true B then acknowledges it in explanation.'),
 ('ABE','A70,70,80,80,100 and B60,80,80,90,90 both sum400,mean80,median80,range30. A modes70,80; A mean not higher; B range not smaller.'),
 ('ABCD','Replace80 with50 in20,30,30,40,80:mean40 becomes34,median30 and mode30 unchanged,range60 becomes30; E false.'),
 ('124','2,3,3,4,8:sum20,mean4,median3,mode3,range6. C mode4 false.'),
 ('134','A1,2,3,4,10 and B2,3,3,4,8 both sum20,mean4,median3. Ranges9 and6;B mode3. A median not higher.'),
],
22:[
 ('C','Both groups sum400,mean80,median80;A range20,B40. Only C states equal centers and unequal ranges.'),
 ('B','P20,22,24,26,28 and Q15,20,24,28,33 both sum120,mean24; ranges8 and18. Only B.'),
 ('D','A2,3,3,4,8:mean4,median3,range6;B3,3,4,4,6:mean4,median4,range3. D is already correct; source key A and explanation saying no option is correct both fail.'),
 ('B','X70,80,80,80,90 and Y60,70,80,90,100:median80 each,ranges20/40. X mode80,Y no unique mode; A wrongly claims higher median.'),
 ('C','Both means/medians80;A range10,B40. Maximum100 versus85 alone does not rank whole groups; maximum remains legitimate data.'),
 ('ABC','Means80,medians80;A range40,B20. D falsely higher mean for B; E reverses range comparison.'),
 ('ABD','P constant5:mean5,median5,range0;Q3,4,5,6,7:mean5,median5,range4,no unique mode. E falsely singles out5 as mode.'),
 ('ABCD','A1..5 mean3,median3,range4;B1,2,3,4,10 mean4,median3,range9. More study time alone does not prove superior learning.'),
 ('13','Both sums100,means20,medians20. Ranges20 and10. A,C true; B greater mean false; D unique modes false.'),
 ('124','P70,75,80,85,90 and Q60,80,80,80,100:means/medians80,ranges20/40. P narrower; Q not narrower.'),
 ('A','A70,75,80,85,90 range20;B60,70,80,90,100 range40. Defined consistency uses range; common median80 does not equalize spread.'),
 ('A','Both sums600,means120,medians120;A100..140 range40,B80..160 range80. Only A.'),
 ('C','X60,70,80,90,100 and Y75,78,80,82,85:means/medians80,ranges40/10. Y tighter; largest value alone does not imply overall superiority or justify removing it.'),
 ('C','P65,70,75,80,85 and Q55,70,75,80,95:means/medians75,ranges20/40. Highest score alone is insufficient; P median not higher.'),
 ('A','A12,14,15,16,18 range6;B8,12,15,18,22 range14. Both median15; the stipulated consistency criterion selects A.'),
 ('ABD','Means/medians80;A range20,B40;B mode80. C,E falsely claim wider A.'),
 ('CD','P50,60,70,80,90 and Q65,70,70,75,70:sum350 each,means70,medians70,ranges40/10. Q mode70,not range25.'),
 ('ABC','Both means/medians30;A range40,B20. B all distinct lacks a unique mode; spreads not equal.'),
 ('123','Both means/medians80;A range40,B20. D wrongly assigns40 to B.'),
 ('234','P1..5 and Q2,2,3,3,5 both sum15,mean3,median3. Ranges4/3;Q bimodal2,3. A greater mean false.'),
],
23:[
 ('B','18/120=3/20=0.15; other numerical options differ.'),
 ('C','Heads108 of200 means other side92;92/200=0.46,not108/200=0.54.'),
 ('C','28/80=0.35 is empirical. Composition unknown,so no exact theoretical probability or guaranteed next100 frequency.'),
 ('C','Even count150-81=69;69/150=0.46.0.54 is odd frequency.'),
 ('C','Empirical26/40=0.65. C gives theoretical0.5 only under a fair-coin assumption not stated in stimulus.'),
 ('ABC','Counts14,18,16,20,17,15 sum100;relative1=.14,4=.20,6=.15,2=.18;total1,not1.5.'),
 ('AC','32/60=0.5333... matches A recurring3;28/60=0.4666... is not exactly0.47 without rounding. C total1 true,D fair probability1/2 not32/60,E reverses comparison.'),
 ('ABD','8/30~.267,19/120~.158;theoretical1/6. Absolute errors1/10 and1/120: B is closer. Counts do not redefine theoretical probability.'),
 ('134','Counts7,9,8,10,6,10 sum50;1=.14,4=.20 not.25,5=.12;9/50>8/50.'),
 ('124','Fair coin:empirical picture57/100=.57,other43/100=.43;theoretical.5;count difference14.'),
 ('B','44/240=11/60~.18333,not.20. Relative frequency needs only event count and total; unknown remaining outcomes do not prevent it.'),
 ('C','72/200=.36 is empirical. Composition unknown; it may equal theoretical probability but the trial does not establish that equality.'),
 ('C','For independent fair tosses,AA,AG,GA,GG equally likely and exactly one picture2/4=.5. Without fairness/independence,2p(1-p) need not equal.5.'),
 ('C','Empirical162/300=.54;theoretical even3/6=.5 only if die is fair,which is not stated in stimulus.'),
 ('B','I8/24=1/3,error1/6 from theoretical1/6;II25/120=5/24,error1/24. II closer; underlying fair-die probability unchanged.'),
 ('ABCD','Counts25+29+31+32+30+33=180.25/180 exact,32/180~.178,33/180~.183;31/180>30/180;total1,not6.'),
 ('ABC','46/80=.575,34/80=.425,total1,other side smaller. Excluding theoretical.575 requires fair-coin assumption; an unspecified biased coin could have p=.575.'),
 ('ABC','Under uniform random draws,p(red)=4/(4+6)=.4. Empiricalred38/100=.38,blue62/100=.62. No guarantee of next-trial frequency; uniform sampling is not explicit in source.'),
 ('124','Fairdie P(1or2)=2/6=1/3;39/120=.325<1/3,not equal.'),
 ('124','Faircoin:96/200=.48,104/200=.52,theoretical.5;absolute difference.02. Empirical and theoretical values differ.'),
]}

ISSUES={
 (21,39):'WRONG_KEY_AND_EXPLANATION: median data adalah25, sehingga B benar. Kunci/tabel memberi B Salah, pembahasan juga menyebut median25 tetapi menyimpulkan B salah. Himpunan benar1234, bukan134.',
 (21,40):'CONFLICTING_KEY: rerata kedua kelompok3; median2 dan3; jangkauan6 dan2. Hanya D tepat. Kunci/tabel124 bertentangan dengan data dan koreksi pada pembahasan yang memilih4.',
 (21,46):'CONFLICTING_KEY: jumlah400/5=80, jadi opsi B benar. Kunci awal A,C,D menghilangkan B; pembahasan kemudian mengoreksi menjadi A,B,C,D.',
 (21,47):'CONFLICTING_KEY: rerata kedua kelompok400/5=80, sehingga C salah. Kunci awal A,B,C,E bertentangan dengan koreksi pembahasan A,B,E.',
 (22,33):'WRONG_KEY_AND_CORRECTION: opsi D benar karena rerata kedua kelompok4. Kunci awal A salah; pembahasan salah menyatakan tidak ada opsi benar, lalu mengusulkan perubahan A yang akan menduplikasi D.',
 (22,37):'CONFLICTING_KEY: kelompok Q berisi3,4,5,6,7 tanpa modus tunggal. E salah. Kunci awal A,B,D,E bertentangan dengan koreksi pembahasan A,B,D.',
 (22,39):'CONFLICTING_KEY: rerata kedua kelompok20, sehingga B salah. Kunci/tabel123 bertentangan dengan koreksi pembahasan13.',
 (23,35):'MISSING_FAIRNESS: stimulus tidak menyebut koin seimbang. Frekuensi relatif0.65 tidak menetapkan peluang teoretis; opsi C memakai peluang0.5 yang mensyaratkan koin seimbang. Tegaskan asumsi pada stimulus.',
 (23,37):'UNSTATED_ROUNDING:28/60=0.4666..., bukan tepat0.47 pada opsi B. Pembahasan memakai sekitar0.47, stimulus/opsi tidak. KunciABC menganggap pembulatan yang belum dinyatakan; kunci eksakAC.',
 (23,43):'MISSING_MODEL: peluang tepat satu gambar adalah1/2 hanya untuk dua lemparan independen koin seimbang. Stimulus tidak menetapkan kedua asumsi; ruang sampel empat hasil saja tidak menjamin peluang setara.',
 (23,44):'MISSING_FAIRNESS: stimulus tidak menyebut dadu seimbang. Peluang genap0.5 pada opsi C memerlukan asumsi tersebut; frekuensi relatif162/300 tidak menetapkannya.',
 (23,47):'MISSING_FAIRNESS: stimulus tidak menyebut koin seimbang. A,B,C benar empiris; D tidak dapat dinilai salah secara pasti karena peluang koin yang tidak diketahui dapat saja0.575. Tegaskan model sebelum memakai kunciABC.',
 (23,48):'MISSING_RANDOM_DRAW: peluang4/10 pada opsi A membutuhkan pengambilan acak seragam. Stimulus hanya menyebut mengambil satu bola dan pengembalian, belum menyatakan acak/seragam. Frekuensi relatifB,C tetap benar; tegaskan mekanisme untuk kunciABC.',
}


class Table(HTMLParser):
    def __init__(self,text):
        super().__init__();self.rows=[];self.cell=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.rows.append([])
        if tag in ('td','th'):self.cell=[]
        if tag=='br' and self.cell is not None:self.cell.append('\n')
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th'):
            self.rows[-1].append(''.join(self.cell).strip());self.cell=None


def parse(raw,n):
    body,explanation=re.split(r'Pembahasan\s*:',raw,maxsplit=1,flags=re.I)
    explanation='Pembahasan: '+re.split(r'\n\s*(?:[IVX]+\.\s*)?Pilihan Ganda',explanation,maxsplit=1,flags=re.I)[0].strip()
    fmt='PG' if (n-1)%10<5 else 'MCMA' if (n-1)%10<8 else 'KATEGORI'
    keylines=re.findall(r'^Kunci\s+jawaban\s*:\s*(.+)$',body,re.M|re.I)
    assert len(keylines)<=1,(n,keylines)
    body=re.sub(r'^Kunci\s+jawaban\s*:.*$','',body,flags=re.M|re.I)
    body=re.sub(r'^Soal\s+\d+[^\n]*','',body,flags=re.I)
    stem=[];options=[];labels=None;table_key=None
    for token in re.findall(r'<table>.*?</table>|[^\n]+',body,re.S):
        token=token.strip()
        if not token or token.startswith('<!--'):continue
        if token.startswith('<table>'):
            rows=Table(token).rows
            is_category=len(rows[0])>=2 and rows[0][1].casefold() in ('kategori','benar','tepat','layak')
            if is_category:
                assert fmt=='KATEGORI' and not options,(n,rows)
                labels=rows[0][1:] if rows[0][1]!='Kategori' else ['Benar','Salah']
                assert len(labels)==2,(n,labels)
                options=[re.sub(r'^[A-E]\.\s*','',r[0]) for r in rows[1:]]
                if rows[0][1]=='Kategori':table_key=[str(j+1) for j,r in enumerate(rows[1:]) if r[1].casefold()==labels[0].casefold()]
                else:
                    assert all(sum(bool(c.strip()) for c in r[1:])==1 for r in rows[1:]),(n,rows)
                    table_key=[str(j+1) for j,r in enumerate(rows[1:]) if r[1].strip()]
            else:
                assert len({len(r) for r in rows})==1,(n,rows)
                def row(r):return '| '+' | '.join(c.replace('|','\\|').replace('\n','<br>') for c in r)+' |'
                stem.append('\n'.join([row(rows[0]),row(['---']*len(rows[0])),*[row(r) for r in rows[1:]]]))
            continue
        if re.match(r'^[A-E]\.\s',token):
            assert fmt!='KATEGORI',(n,token)
            starts=[];expected=65+len(options)
            for m in re.finditer(r'(?<!\S)([A-E])\.\s+',token):
                if ord(m[1])==expected:starts.append(m);expected+=1
            assert starts and starts[0].start()==0,(n,token)
            for j,m in enumerate(starts):
                end=starts[j+1].start() if j+1<len(starts) else len(token)
                options.append(token[m.end():end].strip())
        else:stem.append(token)
    expected_count=5 if fmt=='MCMA' or fmt=='PG' and 'PG (' in raw.splitlines()[0] else 4
    assert len(options)==expected_count,(n,fmt,len(options))
    if fmt=='KATEGORI':
        assert labels and table_key is not None,n
        key=table_key
        if keylines:
            pattern='|'.join(re.escape(t) for t in sorted(labels,key=len,reverse=True))
            pairs=re.findall(r'\b([A-E])\s+('+pattern+r')\b',keylines[0],re.I)
            assert len(pairs)==len(options),(n,pairs)
            key=[str(j+1) for j,(letter,label) in enumerate(pairs) if label.casefold()==labels[0].casefold()]
            assert key==table_key,(n,key,table_key)
    else:
        assert keylines,n
        key=re.findall(r'\b[A-E]\b',keylines[0]);assert key and (fmt!='PG' or len(key)==1),(n,key)
    return dict(format=fmt,stem='\n\n'.join(stem),options=options,key=key,explanation=explanation,
                category_labels=labels,additional_notes='',declared_key_texts=keylines)


def build():
    assert hashlib.sha256((SOURCE/'source.docx').read_bytes()).hexdigest()==SOURCE_HASH
    raw=json.loads((SOURCE/'question-index.json').read_text(encoding='utf8'))['questions']
    assert len(raw)==200
    raw={(q['source_indicator'],q['source_level'],q['source_question_number']):q for q in raw}
    assert len(raw)==200
    entries=[e for e in source_entries(SOURCE) if e['level'] in (4,5)]
    assert len(entries)==80
    assert Counter((e['indicator'],e['level']) for e in entries)==Counter({(i,l):10 for i in range(20,24) for l in (4,5)})
    rows=[];metadata={};groups={};reviews=[]
    for e in entries:
        i,l,n=e['indicator'],e['level'],e['source_number'];assert (l-1)*10<n<=l*10,(i,l,n)
        q=raw[i,l,n];p=parse(q['extracted_content'],n)
        cognitive=re.search(r'\bC[1-6]\b',q['source_heading']);assert cognitive,(i,l,n)
        qid=f"{p['format'].lower()}-{i}-{l}-{n-(l-1)*10}"
        expected,reasoning=REVIEW[i][n-31];issues=[ISSUES[i,n]] if (i,n) in ISSUES else []
        if list(expected)!=p['key'] and not issues:raise AssertionError((qid,expected,p['key']))
        status='HOLD_SOURCE' if issues else 'ACTIVE'
        review=dict(question_id=qid,indicator=i,level=l,source_number=n,audit_id=e['audit_id'],
                    source_projection=p,independent_answer=list(expected),independent_reasoning=reasoning,
                    answer_is_conditional=(i==23 and n in (35,43,44,47,48)),issues=issues,generation_status=status)
        reviews.append(review)
        rows.append(dict(id=qid,format=p['format'],cognitive_level=cognitive[0],stem=p['stem'],
                         options_json=json.dumps(p['options'],ensure_ascii=False),key=','.join(p['key']),version=1))
        metadata[qid]=dict(generation_status=status,reason='; '.join(issues),generator_status='NOT_IMPLEMENTED',
            source_number=n,source_document=e['source']['path'],source_document_sha256=SOURCE_HASH,
            source_location=e['source'],source_text=q['extracted_content'],source_projection=p,
            original_explanation=p['explanation'],source_additional_notes='',approval_status='NOT_CURRICULUM_APPROVED',
            self_adjustment_enabled=False,source_review=dict(date='2026-10-21',audit_id=e['audit_id'],issues=issues,
                independent_reasoning=reasoning,original_unchanged=True),batch='2026-10-21-indicators20-23-level45-source-only')
        if p['category_labels']:metadata[qid]['category_labels']=p['category_labels']
        groups.setdefault((i,l),[]).append(qid)
    counts=dict(originals=80,active=sum(not e['issues'] for e in reviews),hold=sum(bool(e['issues']) for e in reviews),generators_added=0,stocks_added=0)
    assert len({r['id'] for r in rows})==80
    report=dict(date='2026-10-21',source_sha256=SOURCE_HASH,counts=counts,entries=reviews)
    out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    def encoded(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
    return {DATA/'q0_bank.csv':out.getvalue(),DATA/'question_metadata.json':encoded(metadata),DATA/'audit.json':encoded(report),
            DATA/'question_catalog.json':encoded([dict(activity='DRILL',package_id='drill-1',package_name='Paket 1',indicator=i,source_level=l,question_ids=qs) for (i,l),qs in groups.items()])}


def main():
    files=build()
    # ponytail: fixed source intake only; create a new revision ledger for subsequent edits.
    for path,text in files.items():
        if path.exists() and path.read_bytes()!=text.encode('utf8'):raise ValueError(f'Refusing overwrite: {path}')
    DATA.mkdir(exist_ok=True)
    for path,text in files.items():
        if not path.exists():path.write_bytes(text.encode('utf8'))
    print(json.loads(files[DATA/'audit.json'])['counts'])


if __name__=='__main__':main()
