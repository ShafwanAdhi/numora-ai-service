"""27 bounded numeric families; no originals, editorial stocks or database writes."""
import json
import re
from pathlib import Path

from build_drill_1_5_level45_batch1 import Author
from drill_11_15_math import number

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/drill-1-indicators-20-23-levels-4-5'
SELECTION={20:{4:[7,9],5:[5]},21:{4:[1,2,3,5,6,7],5:[4,9]},
           22:{4:[1,2,4,6,8],5:[10]},23:{4:[1,2,3,4,6,9,10],5:[1,6,10]}}


def selected():
    entries=json.loads((DATA/'audit.json').read_text(encoding='utf8'))['entries']
    return [e for e in entries if int(e['question_id'].split('-')[-1]) in SELECTION.get(e['indicator'],{}).get(e['level'],[])]


def author(e):
    # ponytail: 30 audited parameter cases; widen dimensions only after another domain audit.
    e=dict(e,source_number=int(e['question_id'].split('-')[-1]))
    a=Author(e);case=(a.i,a.l,a.n)
    def shift(values,direction=1):return {str(v):f'({number(str(v))})+({direction})*k' for v in values}
    def stem(mapping):a.stem=a.nums(a.stem,mapping)
    def opt(j,mapping):a.options[j]=a.nums(a.options[j],mapping)
    def summary(answer,text):a.exp=a.explanation('Hasil = [['+answer+']]. '+text)
    def frac(num,den,literal=None):
        if literal is None:return a.var(num)+'/'+a.var(den)
        return a.var(num,literal)+a.var("'/'",'')+a.var(den,'')
    def probability(num,den,text):a.exp='Hasil = '+frac(num,den)+'. '+a.explanation(text)
    def counts(total,expressions):
        a.stem=re.sub(r'(dilempar(?: sebanyak)? )(\d+)( kali)',lambda m:m[1]+a.var(total,m[2])+m[3],a.stem,count=1,flags=re.I)
        a.stem=re.sub(r'(angka ([1-6]) muncul )(\d+)( kali)',lambda m:m[1]+a.var(expressions[int(m[2])-1],m[3])+m[4],a.stem,flags=re.I)

    if case==(20,4,7):
        a.allnums(shift([70,75,80,85,90,'82,5'],-1))
        summary('82.5-k','Jumlah=[[660-8*k]], banyak data8. Rerata dan median=[[82.5-k]], modus=[[90-k]], jangkauan20. A,B,C,D benar; E salah karena terdapat nilai di bawah atau sama dengan batas[[75-k]].')
    elif case==(20,4,9):
        stem(shift([80,100,70,110]));opt(3,{'150':'150+2*k'})
        summary('110+k','Pengunjung tertinggi Kamis=[[110+k]]. Selasa-Senin=20, Rabu bukan tertinggi, Senin+Rabu=[[150+2*k]]. Pernyataan1,2,4 benar.')
    elif case==(20,5,5):
        a.allnums({'45':'45+k','35':'35-k'})
        summary('45+k','Total100. Kelompok2-4jam=[[45+k]], kelompok>4jam=[[35-k]]%, kurang dari50%. Kelompok terbesar2-4jam; C benar. Tidak menyamakan kelompok terbesar dengan mayoritas.')
    elif case==(21,4,1):
        a.allnums(shift([72,75,80,83,85,92,'81,5',82],-1))
        summary('81.5-k','Delapan data terurut. Median=([[80-k]]+[[83-k]])/2=[[81.5-k]], bukan klaim[[80-k]]. Opsi B benar; frekuensi kemunculan tidak menentukan median.')
    elif case==(21,4,2):
        a.allnums(shift([3,4,5,6,8]))
        summary('5+k','Jumlah=[[25+5*k]], rerata=[[5+k]], median=[[5+k]]. Rerata tidak lebih besar; hanya C mempunyai penilaian dan angka yang benar.')
    elif case==(21,4,3):
        stem(shift([10,12,15,18,20,25]))
        a.options[0]=a.options[0].replace('15',a.var('15+k','15'),1)
        a.options[1]=a.options[1].replace('18',a.var('18+k','18'),1)
        a.options[2]=a.options[2].replace('15',a.var('15+k','15'),1)
        opt(3,shift([15,20]))
        summary('15+k','Modus=[[15+k]], median=[[15+k]], jangkauan15. Rerata=('+a.var('115+7*k')+')/7, bukan klaim opsi D. Hanya A benar.')
    elif case in ((21,4,5),(22,4,1),(22,4,6)):
        a.allnums(shift([60,70,75,80,85,90,100],-1))
        index=0 if case==(22,4,6) else 2
        a.answer_value(index,'80-k',' poin, rerata kedua kelompok')
        ranges=(40,20) if case==(22,4,6) else (20,40)
        summary('80-k',f'Rerata dan median kedua kelompok=[[80-k]]. Jangkauan kelompok A={ranges[0]}, B={ranges[1]}; pusat sama tidak menyamakan penyebaran.')
    elif case==(21,4,6):
        stem(shift([4,6,8,11]));opt(0,shift([7]));opt(1,shift([6]));opt(2,shift([8]))
        summary('7+k','Rerata=[[7+k]], median dan modus=[[6+k]], jangkauan7. A,B,D benar; modus bukan[[8+k]], dan rerata tidak lebih kecil daripada median.')
    elif case==(21,4,7):
        a.allnums(shift([65,70,75,80,85,95],-1))
        summary('80-k','Median dan modus=[[80-k]], jangkauan30. Rerata=('+a.var('550-7*k')+')/7, bukan[[80-k]]. Hapus nilai terbesar: median=[[77.5-k]], bukan[[75-k]]. A,B,C benar.')
    elif case==(21,5,4):
        a.allnums(shift([70,75,80,95],-1));a.answer_value(0,'82-k',' poin, rerata baru')
        summary('82-k','Rerata awal=[[80-k]], baru=[[82-k]]; median tetap[[80-k]]. Jangkauan25 menjadi20 karena minimum baru[[75-k]]. Hanya A benar.')
    elif case==(21,5,9):
        stem(shift([2,3,4,8]));opt(0,shift([4]));opt(1,shift([3]));opt(2,shift([4]))
        summary('4+k','Rerata=[[4+k]], median dan modus=[[3+k]], jangkauan6. Pernyataan1,2,4 benar; modus bukan[[4+k]].')
    elif case==(22,4,2):
        stem(shift([15,20,22,24,26,28,33]));a.answer_value(1,'24+k',' menit, rerata kedua kelompok')
        summary('24+k','Kedua rerata dan median=[[24+k]]. Jangkauan P=8 dan Q=18, sehingga Q lebih menyebar menurut jangkauan. Hanya B benar.')
    elif case==(22,4,4):
        a.allnums(shift([60,70,80,90,100],-1));a.answer_value(1,'80-k',' poin, median kedua kelas')
        summary('80-k','Median kedua kelas=[[80-k]]. Jangkauan X=20,Y=40. Modus X=[[80-k]], kelas Y tidak mempunyai modus tunggal. Hanya B benar.')
    elif case==(22,4,8):
        a.allnums(shift([1,2,3,4,5,10]))
        summary('4+k','Rerata A=[[3+k]], B=[[4+k]]. Median keduanya[[3+k]], jangkauan A4 dan B9. A,B,C,D benar; durasi lebih lama tidak membuktikan hasil belajar lebih baik.')
    elif case==(22,5,10):
        a.allnums(shift([1,2,3,4,5]))
        summary('3+k','Rerata dan median kedua kelompok=[[3+k]]. Jangkauan P4,Q3; modus Q=[[2+k]] dan[[3+k]]. Pernyataan2,3,4 benar; rerata P tidak lebih besar.')
    elif case==(23,4,1):
        stem({'18':'18+3*k'})
        for j in range(5):opt(j,{str(v):f'({number(str(v))})+k/40' for v in ['0,12','0,15','0,18','0,20','0,25']})
        probability('18+3*k','120','Frekuensi relatif=jumlah kejadian/banyak percobaan. Opsi B sesuai; seluruh frekuensi dan opsi berada pada0 sampai1.')
    elif case==(23,4,2):
        stem({'108':'108+2*k'})
        for j in range(5):opt(j,{v:f'({number(v)})-k/100' for v in ['0,36','0,42','0,46','0,54','0,60']})
        probability('92-2*k','200','Sisi angka muncul200-[[108+2*k]]=[[92-2*k]]kali. Opsi C; jangan memakai frekuensi sisi gambar.')
    elif case==(23,4,3):
        stem({'28':'28+k'});opt(0,{'0,35':'(28+k)/80'});opt(1,{'0,28':'(28+k)/100'});opt(2,{'0,35':'(28+k)/80'});opt(4,{'35':'35+k'})
        probability('28+k','80','Ini frekuensi relatif empiris, bukan kepastian peluang teoretis atau jumlah kejadian percobaan berikutnya. Hanya C benar.')
    elif case==(23,4,4):
        stem({'81':'81-k'})
        for j,(literal,num) in enumerate(zip(['0,36','0,40','0,46','0,54','0,60'],[54,60,69,81,90])):
            a.options[j]=a.options[j].replace(literal,frac(f'{num}+k','150',literal))
        probability('69+k','150','Angka genap muncul150-[[81-k]]=[[69+k]]kali; opsi C. Pecahan eksak menghindari pembulatan implisit.')
    elif case in ((23,4,6),(23,4,9),(23,5,6)):
        if case==(23,4,6):
            total='100+10*k';v=['14+k','18+2*k','16+2*k','20+2*k','17+2*k','15+k'];counts(total,v)
            for j,num,lit in [(0,v[0],'0,14'),(1,v[3],'0,20'),(2,v[5],'0,15')]:a.options[j]=a.options[j].replace(lit,frac(num,total,lit))
            probability(v[0],total,'Semua hitungan berjumlah[[100+10*k]]. A,B,C benar. Frekuensi angka2 berbeda dari0.20; jumlah frekuensi relatif1,bukan1.5.')
        elif case==(23,4,9):
            total='50+10*k';v=['7+k','9+2*k','8+2*k','10+2*k','6+2*k','10+k'];counts(total,v)
            a.options[0]=a.options[0].replace('0,14',frac(v[0],total,'0,14'));a.options[2]=a.options[2].replace('0,12',frac(v[4],total,'0,12'))
            probability(v[0],total,'Jumlah[[50+10*k]]. Frekuensi angka4=1/5,bukan0.25; angka2 lebih sering daripada3. Pernyataan1,3,4 benar.')
        else:
            total='180+8*k';v=['25+k','29+k','31+k','32+2*k','30+k','33+2*k'];counts(total,v)
            a.options[0]=a.options[0].replace('25/180',frac(v[0],total,'25/180'))
            a.options[1]=a.options[1].replace('0,178',frac(v[3],total,'0,178'));a.options[2]=a.options[2].replace('0,183',frac(v[5],total,'0,183'))
            probability(v[0],total,'Jumlah[[180+8*k]]. A,B,C,D benar: angka3 lebih sering daripada5. Jumlah frekuensi relatif1,bukan6. Pecahan varian eksak; desimal sumber dibulatkan tiga tempat.')
    elif case==(23,4,10):
        stem({'57':'57+k'});opt(0,{'0,57':'(57+k)/100'});opt(1,{'0,43':'(43-k)/100'});opt(2,{'0,57':'(57+k)/100'});opt(3,{'14':'14+2*k'})
        probability('57+k','100','Sisi angka=[[43-k]], selisih kemunculan=[[14+2*k]]. Peluang teoretis koin seimbang tetap1/2. Pernyataan1,2,4 benar.')
    elif case==(23,5,1):
        stem({'44':'44-k'});opt(0,{'44':'44-k'});a.options[1]=a.options[1].replace('0,183',frac('44-k','240','0,183'))
        probability('44-k','240','Frekuensi relatif kurang dari0.20; opsi B sesuai. Banyak kemunculan tetap positif. Pecahan varian eksak, angka sumber sekitar0.183.')
    elif case==(23,5,10):
        stem({'96':'96-k'});opt(0,{'0,48':'(96-k)/200'});opt(1,{'0,52':'(104+k)/200'});opt(2,{'0,48':'(96-k)/200'});opt(3,{'0,02':'(4+k)/200'})
        probability('96-k','200','Sisi gambar=[[104+k]], peluang teoretis koin seimbang1/2. Selisih absolut frekuensi relatif dan1/2=[[0.02+k/200]]. Pernyataan1,2,4 benar.')
    else:raise AssertionError(case)
    return a


def main():
    from bank import OriginalBank
    from config_store import validate_config
    from engine import assemble,build_values
    from lint import reproduce_original
    from filters import signature,validate_candidate
    from oracle_drill_20_23_level45_batch1 import check_math
    bank=OriginalBank(DATA/'q0_bank.csv');outputs={}
    for e in selected():
        q=e['question_id'];o=bank.get(q);assert not e['issues'] and o['metadata']['generation_status']=='ACTIVE',q
        a=author(e);assert a.qid==q
        cfg=a.config(o);assert validate_config(cfg,o)==[],(q,validate_config(cfg,o))
        assert reproduce_original(o,cfg)==([],[]),(q,reproduce_original(o,cfg))
        unique=set()
        for k in range(31):
            cand=assemble(cfg,build_values(cfg,lambda name,spec:k));check_math(q,cand)
            if k:
                assert not validate_candidate(cand,o,[]),(q,k,validate_candidate(cand,o,[]))
                unique.add(signature(cand['stem'],cand['options']))
        assert len(unique)==30,(q,len(unique))
        path=ROOT/'configs'/q/'v1.json';text=json.dumps(cfg,ensure_ascii=False,indent=2)+'\n'
        if path.exists():assert json.loads(path.read_text(encoding='utf8'))==cfg,f'Refusing overwrite: {path}'
        outputs[path]=text
    assert len(outputs)==27
    for path,text in outputs.items():
        path.parent.mkdir(exist_ok=True)
        if not path.exists():path.write_bytes(text.encode('utf8'))
    path=DATA/'question_metadata.json';metadata=json.loads(path.read_text(encoding='utf8'))
    for e in selected():metadata[e['question_id']]['generator_status']='IMPLEMENTED'
    tmp=path.with_suffix('.json.tmp');tmp.write_bytes((json.dumps(metadata,ensure_ascii=False,indent=2)+'\n').encode('utf8'));tmp.replace(path)
    print('27 configs;837 parameter cases;810 unique valid variants. Originals/stocks unchanged.')


if __name__=='__main__':main()
