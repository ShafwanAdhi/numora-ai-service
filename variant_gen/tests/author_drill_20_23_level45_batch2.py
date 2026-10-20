"""Second27 numeric families; source and runtime persistence stay unchanged."""
import json

from author_drill_20_23_level45_batch1 import ROOT, DATA
from build_drill_1_5_level45_batch1 import Author
from drill_11_15_math import number

SELECTION={20:{4:[2,3],5:[7,10]},21:{4:[4,8],5:[1,2,3,5,8,10]},
           22:{4:[5,10],5:[1,2,3,4,5,6,7,8,9]},23:{4:[8],5:[2,5,9]}}


def selected():
    entries=json.loads((DATA/'audit.json').read_text(encoding='utf8'))['entries']
    return [e for e in entries if int(e['question_id'].split('-')[-1]) in SELECTION.get(e['indicator'],{}).get(e['level'],[])]


def author(e):
    # ponytail: 30 audited cases per family; widen dimensions after another domain audit.
    a=Author(dict(e,source_number=int(e['question_id'].split('-')[-1])))
    case=(a.i,a.l,a.n)
    def shift(values,delta='k'):
        return {str(v):f'({number(str(v))})+({delta})' for v in values}
    def scale(values):
        return {str(v):f'({number(str(v))})*(1+k/10)' for v in values}
    def summary(answer,text):a.exp=a.explanation('Hasil = [['+answer+']]. '+text)
    def fraction(num,den,literal=None):
        if literal is None:return a.var(num)+'/'+a.var(den)
        return a.var(num,literal)+a.var("'/'",'')+a.var(den,'')
    def probability(num,den,text):a.exp='Hasil = '+fraction(num,den)+'. '+a.explanation(text)
    def annex_fraction(j,num,den):
        a.options[j]+=a.var("' (frekuensi relatif: '",'')+fraction(num,den,'')+a.var("')'",'')

    if case==(20,4,2):
        a.allnums(shift([2,4,3,6,5]));a.answer_value(1,'6+k',' buku')
        summary('6+k','Dini membaca paling banyak: [[6+k]] buku. Minimum Andi=[[2+k]]; Citra=[[3+k]] lebih sedikit daripada Dini.')
    elif case==(20,4,3):
        a.allnums(dict(shift([45,20,15]),**{'100':'100+4*k'}))
        a.answer_value(1,'100+4*k',' siswa, total responden')
        summary('100+4*k','Total keempat kategori=[[100+4*k]]. Diagram batang membandingkan jumlah antarjenis transportasi; kategori bukan urutan waktu atau pasangan dua variabel numerik.')
    elif case==(20,5,7):
        a.stem=a.nums(a.stem,{'60':'60+k/2','25':'25-k/5','15':'15-3*k/10'})
        a.answer_value(0,'60+k/2','%, kelompok durasi tersebut')
        summary('60+k/2','Persentase berjumlah100. Kategori1-2jam=[[60+k/2]]%, kurang dari1jam=[[25-k/5]]%, lebih dari2jam=[[15-3*k/10]]%. Kelompok1-2jam terbesar. A,C,E benar; tidak membuktikan sebab-akibat atau berlaku bagi semua siswa.')
    elif case==(20,5,10):
        a.stem=a.nums(a.stem,{'80':'80+4*k','44':'44+2*k','24':'24+k','12':'12+k'})
        a.answer_value(0,'44+2*k',' siswa setuju')
        summary('44+2*k','Setuju=[[44+2*k]], tidak setuju=[[24+k]], ragu-ragu=[[12+k]], total=[[80+4*k]]. Setuju kelompok terbesar; kesimpulan seluruh sekolah perlu keterwakilan sampel. Pernyataan1,3,4 tepat.')
    elif case==(21,4,4):
        a.allnums(shift([60,70,75,80,90,100],'-k'));a.answer_value(1,'75-k',' poin, rerata awal')
        summary('75-k','Rerata awal=[[75-k]]. Jumlah baru=[[475-6*k]] untuk6data, nilai baru=[[100-k]] lebih besar daripada rerata awal; rerata meningkat. Hanya B benar.')
    elif case==(21,4,8):
        a.allnums(shift([60,70,75,80,85,90,100],'-k'))
        a.answer_value(0,'80-k',' poin, median kedua kelas')
        summary('80-k','Rerata dan median kedua kelas=[[80-k]]. Jangkauan A20,B40. A tidak mempunyai modus tunggal, modus B=[[80-k]]. A,C,D benar; modus tidak membuktikan seluruh kemampuan lebih baik.')
    elif case==(21,5,1):
        a.allnums(shift([60,70,75,80,85,100],'-k'));a.answer_value(1,'77.5-k',' poin')
        summary('77.5-k','Median=([[75-k]]+[[80-k]])/2=[[77.5-k]], lebih tahan terhadap nilai ekstrem. Jangkauan bukan ukuran pusat; tidak ada modus tunggal. B benar.')
    elif case==(21,5,2):
        a.allnums(shift([100,110,120,130,540],'10*k'));a.answer_value(1,'120+10*k',' ribu rupiah')
        summary('120+10*k','Median=[[120+10*k]], rerata=[[200+10*k]]. Nilai terbesar=[[540+10*k]] menarik rerata ke atas. B benar; median tahan terhadap pencilan.')
    elif case==(21,5,3):
        a.allnums(shift([6,8,10,12,14]));a.answer_value(2,'10+k',' rerata kedua data')
        summary('10+k','Kedua rerata=[[10+k]]. Jangkauan P0,Q8. P konstan sedangkan Q menyebar; rerata sama tidak berarti karakteristik identik. C benar.')
    elif case==(21,5,5):
        a.allnums(scale([15,20,22,24,26,28,33]));a.answer_value(0,'8*(1+k/10)',' menit, jangkauan A')
        summary('8*(1+k/10)','Jangkauan A=[[8*(1+k/10)]], B=[[18*(1+k/10)]]. Median keduanya=[[24*(1+k/10)]]. A lebih konsisten menurut jangkauan; hanya A benar.')
    elif case==(21,5,8):
        a.allnums(shift([20,30,40,50,80]));a.answer_value(0,'34+k',' menit, rerata baru')
        summary('34+k','Rerata awal=[[40+k]], baru=[[34+k]]. Median dan modus tetap[[30+k]], jangkauan60menjadi30. A,B,C,D benar; median tidak meningkat.')
    elif case==(21,5,10):
        a.allnums(shift([1,2,3,4,8,10],'k/10'))
        summary('4+k/10','Rerata kedua kelompok=[[4+k/10]], median[[3+k/10]]. Jangkauan A9,B6; modus B=[[3+k/10]]. Seluruh waktu harian positif dan di bawah24jam. Pernyataan1,3,4 benar.')
    elif case in ((22,4,5),(22,5,3)):
        a.allnums(shift([60,70,75,78,80,82,85,100,90],'-k'));a.answer_value(2,'80-k',' poin, median kedua kelompok')
        summary('80-k','Rerata dan median keduanya=[[80-k]]. Jangkauan kelompok dengan rentang lebar40, lainnya10. Nilai tertinggi saja tidak menilai seluruh kelompok. C benar.')
    elif case==(22,4,10):
        a.allnums(shift([60,70,75,80,85,90,100],'-k'));a.answer_value(0,'80-k',' poin, rerata kedua kelompok')
        summary('80-k','Rerata dan median kedua kelompok=[[80-k]]. Jangkauan P20,Q40. Penyebaran P lebih kecil berdasarkan jangkauan; pernyataan1,2,4 benar.')
    elif case==(22,5,1):
        a.allnums(shift([60,70,75,80,85,90,100],'-k'));a.answer_value(0,'80-k',' poin, median kedua kelompok')
        summary('80-k','Rerata dan median kedua kelompok=[[80-k]]. Jangkauan A20,B40; A lebih konsisten menurut jangkauan. Median sama tidak menyamakan penyebaran. Hanya A benar.')
    elif case==(22,5,2):
        a.allnums(shift([80,100,110,120,130,140,160],'10*k'));a.answer_value(0,'120+10*k',' ribu rupiah, rerata kedua kelompok')
        summary('120+10*k','Rerata dan median kedua kelompok=[[120+10*k]]. Jangkauan A40,B80. Hanya A benar.')
    elif case==(22,5,4):
        a.allnums(shift([55,65,70,75,80,85,95],'-k'));a.answer_value(2,'75-k',' poin, median kedua kelompok')
        summary('75-k','Rerata dan median kedua kelompok=[[75-k]]. Jangkauan P20,Q40. Nilai tertinggi Q=[[95-k]] tidak cukup untuk menyatakan Q lebih baik. Hanya C benar.')
    elif case==(22,5,5):
        a.allnums(scale([8,12,14,15,16,18,22,6]))
        summary('6*(1+k/10)','Jangkauan A=[[6*(1+k/10)]], B=[[14*(1+k/10)]]. Median keduanya=[[15*(1+k/10)]]. Konsistensi menurut jangkauan memilih A; hanya A benar.')
    elif case==(22,5,6):
        a.allnums(shift([60,70,75,80,85,90,100],'-k'))
        summary('80-k','Rerata dan median kedua kelompok=[[80-k]]. Jangkauan A20,B40; modus B=[[80-k]]. A,B,D benar.')
    elif case==(22,5,7):
        a.allnums(shift([50,60,65,70,75,80,90],'-k'))
        summary('70-k','Rerata dan median kedua kelompok=[[70-k]]. Jangkauan P40,Q10, bukan25. Modus Q=[[70-k]]; C,D benar.')
    elif case==(22,5,8):
        a.allnums(shift([10,20,25,30,35,40,50]));a.answer_value(0,'30+k',' rerata kedua kelompok')
        summary('30+k','Rerata dan median kedua kelompok=[[30+k]]. Jangkauan A40,B20. Semua nilai B berbeda, tidak ada modus tunggal. A,B,C benar.')
    elif case==(22,5,9):
        a.allnums(shift([60,70,75,80,85,90,100],'-k'));a.answer_value(0,'80-k',' poin, rerata kedua kelompok')
        summary('80-k','Rerata dan median keduanya=[[80-k]]. Jangkauan A40,B20; jangkauan B bukan40. Pernyataan1,2,3 benar.')
    elif case==(23,4,8):
        a.stem=a.nums(a.stem,{'30':'30+6*k','8':'8+k','120':'120+6*k','19':'19+k'})
        a.options[0]=a.options[0].replace('0,267',fraction('8+k','30+6*k','0,267'))
        a.options[1]=a.options[1].replace('0,158',fraction('19+k','120+6*k','0,158'))
        a.options[4]=a.options[4].replace('8/30',fraction('8+k','30+6*k','8/30'))
        probability('8+k','30+6*k','Peluang teoretis1/6. Jarak frekuensi A dari1/6=3/([[30+6*k]]), B=1/([[120+6*k]]); B lebih dekat. A,B,D benar; frekuensi empiris bukan bukti peluang teoretis.')
    elif case==(23,5,2):
        a.allnums({'72':'72+2*k','0,36':'(72+2*k)/200'})
        probability('72+2*k','200','Nilai hasil percobaan adalah frekuensi relatif. Peluang teoretis memerlukan komposisi kantong, tidak otomatis sama dengan frekuensi relatif. Hanya C benar.')
    elif case==(23,5,5):
        a.stem=a.nums(a.stem,{'24':'24+6*k','8':'8+k','120':'120+6*k','25':'25+k'})
        annex_fraction(1,'25+k','120+6*k')
        probability('25+k','120+6*k','Peluang teoretis1/6. Jarak percobaan I=4/([[24+6*k]]), II=5/([[120+6*k]]). Pada domain ini II lebih dekat. Jumlah percobaan tidak mengubah peluang teoretis; hanya B benar.')
    elif case==(23,5,9):
        a.stem=a.nums(a.stem,{'120':'120+6*k','39':'39+k'})
        a.options[1]=a.options[1].replace('0,325',fraction('39+k','120+6*k','0,325'))
        probability('39+k','120+6*k','Peluang teoretis2/6=1/3. Frekuensi relatif hasil percobaan lebih kecil daripada1/3 dan tidak persis sama. Pernyataan1,2,4 benar.')
    else:raise AssertionError(case)
    return a


def main():
    from bank import OriginalBank
    from config_store import validate_config
    from engine import assemble,build_values
    from lint import reproduce_original
    from filters import signature,validate_candidate
    from oracle_drill_20_23_level45_batch2 import check_math
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
