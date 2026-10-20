"""Academic audit ledger for 50 authorized indicator-3 entries only.

Manual independent solutions are supported by exact positive rounding and
integer midpoint tests for radicals. No generator or active-bank comparison.
"""
import csv
import json
from collections import Counter
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
from audit_original_questions import ROOT, OUT, digest, read, write
from audit_indicator_01_academic import issue

DEST=OUT/'stage-04-academic-indicator-03'


def nearest(value,step):
    """Nonnegative rational, half-up as illustrated in this curriculum source."""
    value,step=F(value),F(step)
    assert value>=0 and step>0
    return ((value/step+F(1,2))//1)*step


def radical_round(n,places):
    """Round sqrt(n) using the square of the rounding midpoint, no floats."""
    assert type(n) is int and n>=0 and type(places) is int and places>=0
    scale=10**places; scaled=n*scale*scale; floor=isqrt(scaled)
    return F(floor+(4*scaled>=(2*floor+1)**2),scale)


PROOFS={
(1,1):('FTFF','37685 berada315 di bawah38000 dan685 di atas37000; ribuan terdekat38000, B. 37700 bukan kelipatan1000;40000 bukan yang terdekat.'),
(1,2):('FFTF','6,65²=44,2225 <45<45,5625=6,75²; sqrt(45) berada dalam sel pembulatan6,7. Hanya C, bukan6,5/6,6/6,8.'),
(1,3):('FFTF','Harga24800 dibulatkan ke1000 menjadi25000; berat13/4 tetap; hasil81250 dibulatkan ke1000 menjadi81000. Hanya C; A75000 menghilangkan1/4kg, B80000 dan D82500 bukan hasil prosedur.'),
(1,4):('FTFF','4,75²=22,5625<23<23,5225=4,85², jadi sqrt(23) kepersepuluhan4,8. B;4,7/4,9/5,0 di luar hasil pembulatan. Data142m tidak diperlukan untuk menghitung akar.'),
(1,5):('FTFF','19 ke10terdekat→20 dan6850 ke1000terdekat→7000. Estimasi140000, B. A120000/C133000/D130000 tidak mengikuti kedua pembulatan yang diminta.'),
(1,6):('TFTT','14,836→14,84 karena digitperseribuan6; sqrt(10)→3,2 bukan3,5 (3,15²<10<3,25²);8,9²=79,21<80<81=9²;402→400,298→300 memberi120000. A,C,D benar.'),
(1,7):('TTFT','sqrt(15)→3,9, sqrt(26)→5,1 kepersepuluhan; sqrt(35) berada di antara5,5dan6,5 sehingga satuan6, bukan5. A,B,D benar.'),
(1,8):('FTTF','Pembulatan semua ke satuan memberi48*20/10, bukan48*19/9. Pembulatan lebih kasar50*20/10=100 sah sebagaiestimasi; nilai eksak47477/490≈96,8918 dekat100 dan jauh1000. B,C benar.'),
(1,9):('TFT','2,48→2,5;1,73 ke satuan→2 bukan1. Kepersepuluhan masing-masing2,5+1,7+0,9=5,1 dengan aturan5naik yang dicontohkan sumber. a,c benar.'),
(1,10):('TTF','sqrt(18) kepersepuluhan4,2; sqrt(50) kesatuan7. Pembulatan masing-masingkesatuan4+7=11, bukan12. Jika jumlah akar dulu lalu bulatkesatuan,8sqrt(2) juga membulat11; c salah pada kedua bacaan.'),
(2,1):('FTFF','47580 ke1000terdekat48000: jarak420 versus580 ke47000. Hanya B;47600 adalah ratusan,50000 bukan ribuan terdekat.'),
(2,2):('FFTF','7,15²=51,1225<52<52,5625=7,25²; akar membulat7,2. C;7,0/7,1/7,3 bukan hasil yang diminta.'),
(2,3):('FFTF','24600 ke1000terdekat25000; berat7/2 tidakdibulatkan. Estimasi(7/2)*25000=87500, C. A84000 memakai24000; B86100 ialahriil; D90000 tidak sesuai prosedur.'),
(2,4):('FTFF','Riil=(297/5)*(99/5)/(97/10)=58806/485≈121,24948. ModelA50 berjarak34556/485; modelB120 berjarak606/485, jauh lebihkecil. B benar; A/C memilihmodellebihjauh, D memberiaturan tanpa melihatdigit yangsalah.'),
(2,5):('TFFF','sqrt(15) beradaantara3,85dan3,95 sehingga3,9; sqrt(16)=4 tepat ditulis4,0. HanyaA cocok; B/D salahakar15, C salahakar16.'),
(2,6):('TFTT','25,648→25,65; sqrt(18)→4,2 bukan4,5;19→20 dan408→400 menghasilkan8000;5,4²=29,16<30<30,25=5,5². A,C,D benar.'),
(2,7):('TTFT','Kepersepuluhan:sqrt(20)→4,5 dan sqrt(32)→5,7. Sqrt(48)>6,5 dan<7,5 sehingga satuan7 bukan6. A,B,D benar.'),
(2,8):('FTTF','Riil48*19500+8*4800=974400. EstimasiB50*20000+10*5000=1050000 berjarak75600; A440000 berjarak534400. Semua faktorpadaB positif dan lebihbesar dari asli sehingga upperbound, Cbenar; Dterbalik.'),
(2,9):('TFT','3,64→3,6 kepersepuluhan;2,45 langsungkesatuan2 bukan3 (hindari doublerounding). Kepersepuluhan3,6+2,5+0,8=6,9. a,c benar.'),
(2,10):('TTF','sqrt(27) kepersepuluhan5,2; sqrt(75) kesatuan9. Bulatmasing-masingkesatuan5dan9, selisih4 bukan5. Jika selisihakar dulu lalu bulat,2sqrt(3) juga→3 bukan5; jawaban c tetap salah.'),
(3,1):('FTFF','38462 ke1000terdekat38000 (462<500), ke100terdekat38500 (62≥50). HanyaAnalisisII/B; I/IV salahribuan, III salah ratusan.'),
(3,2):('FTFF','6,25²<40<6,35² memberi6,3;6,35²<41<6,45² memberi6,4. HanyaB; A/C/D salahsatuatau kedua komponen salah.'),
(3,3):('FFTF','Ceiling28ke10→30 dan14850ke1000→15000. ModelC450000;riil415800. A/B membulatkebawah;D420000 memang lebihbesarriil tetapi harganya14000 melanggar kewajiban kedua faktor dibulatkeatas.'),
(3,4):('FTFF','Riil=(1994/5)*(102/5)/(49/10)=406776/245≈1660,3102. Selisih ke1600=14776/245, ke1200=112776/245, sehinggaIIjauhlebihdekat. Bbenar;A/C memilihI;D salahkarena20,4→20 justruturun.'),
(3,5):('FFTF','Sqrt(38) kesatuan6 dan sqrt(83) kesatuan9 dengan ujiambang6,5²dan9,5². Selisihkomponenyangdibulatkan9-6=3, C;1/2/4 tidakcocok.'),
(3,6):('TFTT','18,749 langsungkepersepuluhan18,7 (digitpersatusan4); sqrt(22)→4,7 bukan4,9;7,4²=54,76<55<56,25=7,5²;503→500,197→200 menghasilkan100000. A,C,D benar.'),
(3,7):('TTFT','Sqrt(12)→3,5, sqrt(29)→5,4 kepersepuluhan. Sqrt(50) kesatuan7 bukan8. A,B,D benar.'),
(3,8):('FTTF','Riil39*14500+19*4800=656700;I700000 galat43300;II340000 galat316700. I upperbound karenaempatfaktor positifnaik. A salah;B/C benar;D salahkarena656700>340000.'),
(3,9):('TFT','4,36→4,4;2,65 kesatuan3 bukan2. Kepersepuluhan4,4+2,7+1,2=8,3 memakai5naik. a,c benar.'),
(3,10):('TTF','sqrt(19) kepersepuluhan4,4; sqrt(60) kesatuan8. Pembulatanmasing-masingkesatuan4+8=12, bukan11. a,b benar.'),
(4,1):('FTFF','28647 ke1000terdekat29000, ke100terdekat28600. AnalisisII/B;I/IV salahribuan,III/IV salah ratusan.'),
(4,2):('FFTF','7,55²<58<7,65² memberi7,6;7,65²<59<7,75² memberi7,7. HanyaC cocok;A/B/D tidak cocok salahsatuatau keduanya.'),
(4,3):('FTFF','Riil=(2493/5)*(297/10)/(51/10)=246807/85≈2903,61176. GalatII3000=8193/85 lebihkecil daripadaI2400=42807/85. B benar;A/C mendukunglebihjauh;D salahkarena5,1→5turun.'),
(4,4):('FTFF','Riil49*19800=970200. X400000 kurang570200;Y1000000 lebih29800 danupperbound sebabdua faktorpositifnaik. EvaluasiB benar;A/D tidakmenjamin kecukupan, C salahkarenaB benar.'),
(4,5):('TFTF','sqrt(98) kesatuan10, sqrt(45) kesatuan7: selisih3. EvaluasiI danIII sama-samabenar;IIImerinciaproksimasidesimal. II memakaioperasiakar yangtidaksah;D menggabungkanIIsalah. Kriteria palingtepat tidakmenjelaskan apakah rincian wajib, sehingga pilihan tunggalperluklarifikasi.'),
(4,6):('TFTT','34,853→34,9; sqrt(27)→5,2 bukan5,4;7,7²=59,29<60<60,84=7,8²;396→400 dan204→200 menghasilkan80000. A,C,D benar.'),
(4,7):('TTFT','sqrt(15)→3,9 dan sqrt(35)→5,9 kepersepuluhan; sqrt(80) kesatuan9 bukan8. A,B,D benar.'),
(4,8):('FTTF','Riil29*14500+19*9800=606700. I650000 berjarak43300;II290000 berjarak316700. I upperbound empatfaktorpositifnaik. A/D salah;B/C benar.'),
(4,9):('TFT','5,46→5,5;3,75 kesatuan4 bukan3. Kepersepuluhan5,5+3,8+1,2=10,5. a,c benar.'),
(4,10):('TTF','sqrt(22) kepersepuluhan4,7; sqrt(68) kesatuan8. Untukjumlah bulatmasing-masingkesatuan5+8=13, bukan12. a,b benar.'),
(5,1):('FTFF','19482 langsungke1000→19000 karena482<500; langsungke100→19500. HanyaEvaluasiII/B; I/IV salahribuan danIII/IV salah ratusan.'),
(5,2):('FFTF','7,25²=52,5625 <53<54<54,0225=7,35²: keduaakar masuk selpembulatan7,3. Ybenar, C;A/B memberi7,2untuk53,Dsalah7,4untukkeduanya. Ujiambangmembuktikan hasil tanpa menggeneralisasi aturan selisihkuadratterkecil.'),
(5,3):('FTFF','Riil=(2991/5)*(152/5)/(61/10)=909264/305≈2981,19344. GalatB3000=5736/305;galatA2500=146764/305. Blebihakurat;A/C mendukunglebihjauh;D salahkarenaB memberiestimasidekat.'),
(5,4):('FTFF','Riil39*24800=967200;I600000 kurang367200;II1000000 lebih32800 danupperbound dua faktorpositifnaik. HanyaEvaluasiII/B menjamin danacukup.'),
(5,5):('TFTF','Sqrt(82) kesatuan9 dan sqrt(35) kesatuan6: selisih3. Ibenar danIIIbenar, hanya beda rincian. II menggunakanakar(82-35) yangtidakekuivalen;D menggabungkanII salah. PG tidakunik karena pertanyaan meminta evaluasi pasti benar.'),
(5,6):('TFTT','45,748 langsungkepersepuluhan45,7; sqrt(30)→5,5 bukan5,8;7²=49<50<50,41=7,1²;497→500,302→300 menghasilkan150000. A,C,D benar.'),
(5,7):('TTTTTTTF','Dua rangkaian A–D berbeda. Pada awal,A4,2benar,B6,2benar,C8benar,D pernyataan bahwa klaim9cmSALAH juga benar. Pada rangkaianakhir,A4,2benar,B6,2benar,C8benar,Dklaim9salah. Ambangakar18kepersepuluhan4,2;akar38kepersepuluhan6,2;akar70kesatuan8. AwalABCD,akhirABC. HeaderABD tidaklengkapuntukawal dan tidakcocokakhir; kuncitambahanABC sah hanya untukakhir.'),
(5,8):('FTTF','Riil39*19500+19*4800=851700. I900000 galat48300;II340000 galat511700. Semua faktorI positifnaik, jadiB/C benar,A/D salah.'),
(5,9):('TFT','6,46→6,5;4,75 kesatuan5 bukan4. Kepersepuluhan6,5+4,8+1,2=12,5. a,c benar.'),
(5,10):('TTF','sqrt(27) kepersepuluhan5,2 dan sqrt(75) kesatuan9. Bulatmasing-masingkesatuan5+9=14, bukan13. a,b benar.'),
}


def run():
    stage1=OUT/'stage-01-extraction-01-05/validation.json'
    entries=[q for q in read(stage1)['entries'] if q['indicator']==3]
    assert len(entries)==50 and set(PROOFS)=={(l,n) for l in range(1,6) for n in range(1,11)}
    rounding_cases=[(45,1,F(67,10)),(23,1,F(48,10)),(10,1,F(32,10)),(15,1,F(39,10)),(26,1,F(51,10)),
        (35,0,F(6)),(18,1,F(42,10)),(50,0,F(7)),(52,1,F(72,10)),(16,1,F(4)),(20,1,F(45,10)),
        (32,1,F(57,10)),(48,0,F(7)),(27,1,F(52,10)),(75,0,F(9)),(40,1,F(63,10)),(41,1,F(64,10)),
        (38,0,F(6)),(83,0,F(9)),(22,1,F(47,10)),(12,1,F(35,10)),(29,1,F(54,10)),(19,1,F(44,10)),
        (60,0,F(8)),(58,1,F(76,10)),(59,1,F(77,10)),(98,0,F(10)),(45,0,F(7)),(35,1,F(59,10)),
        (80,0,F(9)),(22,0,F(5)),(68,0,F(8)),(53,1,F(73,10)),(54,1,F(73,10)),(82,0,F(9)),
        (30,1,F(55,10)),(38,1,F(62,10)),(70,0,F(8)),(27,0,F(5)),(18,0,F(4)),(19,0,F(4))]
    radical_checks=[]
    for n,p,expected in rounding_cases:
        actual=radical_round(n,p);assert actual==expected,(n,p,actual,expected)
        half=F(1,2*10**p);lo=actual-half;hi=actual+half
        assert lo*lo<=n<hi*hi
        radical_checks.append(dict(radicand=n,decimal_places=p,rounded_exact=str(actual),
            lower_midpoint=str(lo),upper_midpoint=str(hi),lower_squared=str(lo*lo),upper_squared=str(hi*hi),status='PASS'))
    range_cases=[(80,F(89,10),F(9)),(30,F(54,10),F(55,10)),(55,F(74,10),F(75,10)),
                 (60,F(77,10),F(78,10)),(50,F(7),F(71,10))]
    for n,lo,hi in range_cases:assert lo*lo<n<hi*hi
    estimates={
        'L1Q8':(F('48.2')*F('19.7')/F('9.8'),F(100),F(1000)),
        'L2Q4':(F('59.4')*F('19.8')/F('9.7'),F(120),F(50)),
        'L3Q4':(F('398.8')*F('20.4')/F('4.9'),F(1600),F(1200)),
        'L4Q3':(F('498.6')*F('29.7')/F('5.1'),F(3000),F(2400)),
        'L5Q3':(F('598.2')*F('30.4')/F('6.1'),F(3000),F(2500)),
    }
    estimate_checks=[]
    for name,(actual,better,worse) in estimates.items():
        assert abs(actual-better)<abs(actual-worse)
        estimate_checks.append(dict(question=name,actual_exact=str(actual),better_estimate=str(better),
            better_absolute_error=str(abs(actual-better)),worse_estimate=str(worse),worse_absolute_error=str(abs(actual-worse)),status='PASS'))
    checks={
        'integer_rounding':nearest(37685,1000)==38000 and nearest(47580,1000)==48000 and nearest(38462,1000)==38000 and nearest(38462,100)==38500 and nearest(28647,1000)==29000 and nearest(28647,100)==28600 and nearest(19482,1000)==19000 and nearest(19482,100)==19500,
        'two_stage_price':nearest(F(13,4)*nearest(24800,1000),1000)==81000,
        'one_stage_price':F(7,2)*nearest(24600,1000)==87500,
        'unit_estimate':nearest(19,10)*nearest(6850,1000)==140000,
        'decimal_rounding':nearest(F('14.836'),F('0.01'))==F('14.84') and nearest(F('25.648'),F('0.01'))==F('25.65') and nearest(F('18.749'),F('0.1'))==F('18.7') and nearest(F('34.853'),F('0.1'))==F('34.9') and nearest(F('45.748'),F('0.1'))==F('45.7'),
        'component_weight_sums':all(sum(nearest(F(x),F('0.1')) for x in inputs)==F(expected) for inputs,expected in [(['2.48','1.73','0.85'],'5.1'),(['3.64','2.45','0.78'],'6.9'),(['4.36','2.65','1.24'],'8.3'),(['5.46','3.75','1.24'],'10.5'),(['6.46','4.75','1.24'],'12.5')]),
        'avoid_double_rounding':nearest(F('2.45'),1)==2 and nearest(nearest(F('2.45'),F('0.1')),1)==3,
        'upper_bound_1':48*19500+8*4800==974400<1050000,
        'upper_bound_2':39*14500+19*4800==656700<700000,
        'upper_bound_3':29*14500+19*9800==606700<650000,
        'upper_bound_4':39*19500+19*4800==851700<900000,
        'budget_ceilings':28*14850==415800<450000 and 49*19800==970200<1000000 and 39*24800==967200<1000000,
        'radical_root_count':len(radical_checks)==41,
    }
    assert all(checks.values()),checks
    findings={
    (1,3):[issue('explanation/distractors','MINOR','AlasanB mengubah3,25×24000=78000 menjadi80000, tidak mengikuti pembulatanribuan (tetap78000). AlasanD menyebut3,5×24800, hasil86800 bukan82500.','Pertahankan kunciC81000; koreksi skenario kesalahan yang diatribusikan ke opsiB/D atau hapus atribusinya.')],
    (1,5):[issue('explanation/distractor A','MINOR','Pembahasan menyebut keduaoperand dibulatkebawah untuk20×6000. Dari19ke20 justru naik, sedangkan6850ke6000 turun.','Tulis hanya harga dibulatkan ke bawah; jumlahpaket tetap dibulatkankeatas20. Kunci140000 tetap.')],
    (2,3):[issue('explanation/distractor D','MINOR','AlasanD90000 menyebut berat4kg danharga25000, padahal4×25000=100000, bukan90000.','Ganti alasanD dengan hitungan yang benar-benar menghasilkan90000 atau hapus atribusi. Kunci87500 tetap.')],
    (2,4):[issue('stem/explanation/rounding direction','MINOR','ModelA disebut membulatkan semuaangka kebawah, tetapi9,7→10 justrunaik. ModelA memang buruk; jangan mewariskan labelarah yang tidaktepat ke rumusumum pembagian.','Sebut pembilangdibulatkankebawah dan penyebutkeatas. Jangan menyatakan pembulatanpenyebutkebawah selalu menurunkan nilaipecahan.')],
    (4,3):[issue('explanation/editorial artifact','MINOR','Pembahasan menyisakan literal[cite:12] setelah3000. Tidak mengubah hitungan, tetapi bukan rujukan akademik yang dapat ditelusuri.','Hapus penanda editorial atau ganti rujukan nyata bila diperlukan; kunciB tetap.')],
    (4,5):[issue('options/selection','IMPORTANT','EvaluasiI danIII sama-sama membulatkan10dan7 lalu mengurangkan3. III lebih rinci, tetapi I tidak salah. Kata palingtepat tidak menetapkan bahwa rincianaproksimasidesimal wajib.','Perjelas kriteria rincian yangdiminta atau ubah salahsatuopsi agar tidak sama-sama sah. Jangan menilaiI salah hanya karena ringkas.'),
             issue('explanation/terminology','MINOR','Pembahasan memakai kata radian untuk bilangan dalamakar; istilah yang dimaksud radikan.','Ganti radian menjadi radikan (bilangan di dalamtandaakar).')],
    (5,5):[issue('options/key/explanation','CRITICAL','EvaluasiI danIII sama-sama memberi9−6=3 dengan pembulatan yang benar. Pertanyaan meminta evaluasi pasti benar; opsiA danC memenuhi. Pembahasan memilihIII karena rinci, kriteria yang tidak diminta.','Ubah salahsatuevaluasi menjadi salah atau tambahkan kriteria eksplisit. KunciC saatini tidakunik.'),
             issue('explanation/terminology','MINOR','Pembahasan memakai radian dalam konteks bilangan di dalamakar.','Ganti dengan radikan.')],
    (5,7):[issue('stem/options/key/explanation','CRITICAL','Dua rangkaian A–D tercampur. Dawal menyatakan klaim9cmadalahSALAH: pernyataanini benar. Dakhir langsungmengklaim9cm: salah. HeaderABD tidakcocok keduanya; tambahan KunciJawabanTepatABC cocok hanya versiakhir. Pembahasan menilaiDakhir tanpa menyelesaikan duplikasiversi.','Kurikulum menetapkan satuversi dan menghapus rancangan/catatanwait setelah disetujui. Jika versiakhir yang dipilih, jawabanABC; jika opsi meta awal dipertahankan, ABCD. Jangan memilih otomatis atau menganggap delapanopsi sebagai satu rangkaian.')],
    }
    rows=[]
    for q in entries:
        pos=(q['level'],q['source_number']);vector,proof=PROOFS[pos]
        assert len(vector)==len(q['options']),pos
        validity='VALID';answer='CORRECT';explanation='CORRECT';issues=findings.get(pos,[])
        if pos in ((1,3),(1,5),(2,3)):explanation='INCORRECT'
        if pos==(4,5):validity='UNCERTAIN';answer='UNCERTAIN';explanation='UNCERTAIN'
        if pos==(5,5):validity='INVALID';answer='INCORRECT';explanation='INCORRECT'
        if pos==(5,7):validity='INVALID';answer='INCORRECT';explanation='UNCERTAIN'
        special=pos==(5,7)
        evaluations=[]
        for i,(text,t) in enumerate(zip(q['options'],vector)):
            label=chr(97+i) if q['format']=='KATEGORI' else chr(65+i%4)
            evaluations.append(dict(label=label,source_part=('initial' if i<4 else 'rewrite') if special else 'single',
                source_text=text,evaluated_claim=text.splitlines()[0] if special else text,
                result='TRUE' if t=='T' else 'FALSE'))
        ids=[str(i+1) if q['format']=='KATEGORI' else chr(65+i) for i,t in enumerate(vector) if t=='T']
        if answer=='CORRECT':assert ids==q['parsed_key'],(pos,ids,q['parsed_key'])
        if validity=='VALID' and q['format']=='PG':assert vector.count('T')==1,pos
        recommendation=('HOLD_FOR_SOURCE_REVISION' if validity=='INVALID' else 'HOLD_FOR_CLARIFICATION' if validity=='UNCERTAIN' else
            'REVISE_EXPLANATION' if explanation=='INCORRECT' else 'NO_BLOCKING_ACADEMIC_FINDING')
        row=dict(audit_id=q['audit_id'],indicator=3,level=pos[0],source_number=pos[1],source=q['source'],format=q['format'],
            validity=validity,answer_status=answer,explanation_status=explanation,independent_solution=proof,option_evaluations=evaluations,
            independently_correct_ids=None if special else ids,declared_key_texts=q['declared_key_texts'],parsed_source_key=q['parsed_key'],
            explanation_review='Seluruh langkah pembahasan serta catatan dibaca dan dibandingkan dengan solusi independen; temuan per komponen disimpan terpisah. Tidak menyamakan kunci benar dengan seluruh pembahasan benar.',
            issues=issues,recommendation=recommendation,approval_status='NOT_CURRICULUM_APPROVED',generator_matching_status='NOT_EVALUATED_IN_THIS_STAGE')
        if special:
            row['source_parts']=[dict(part='initial',labels=['A','B','C','D'],independently_correct_ids=['A','B','C','D']),
                dict(part='rewrite',labels=['A','B','C','D'],independently_correct_ids=['A','B','C'])]
            row['additional_declared_key']='Kunci Jawaban Tepat: A, B, dan C.'
        rows.append(row)
    baseline=read(OUT/'protected-inputs.json')['sha256'];assert all(digest(ROOT/p)==h for p,h in baseline.items())
    summary=dict(scope='Indikator 3 saja, 50 entri sumber (satu entri memiliki dua rangkaian opsi)',review_date='2026-10-20',entries=50,
        validity=dict(Counter(r['validity'] for r in rows)),answer_status=dict(Counter(r['answer_status'] for r in rows)),
        explanation_status=dict(Counter(r['explanation_status'] for r in rows)),recommendations=dict(Counter(r['recommendation'] for r in rows)),
        source_sha256=read(stage1)['summary']['source_sha256'],stage1_evidence_sha256=digest(stage1),script_sha256=digest(Path(__file__)),
        protected_files_checked=len(baseline),protected_hashes_unchanged=True)
    DEST.mkdir(parents=True,exist_ok=True)
    write(DEST/'audit.json',dict(summary=summary,exact_checks=checks,radical_rounding_evidence=radical_checks,
        interval_checks=[dict(radicand=n,lower=str(lo),upper=str(hi),lower_squared=str(lo*lo),upper_squared=str(hi*hi),status='PASS') for n,lo,hi in range_cases],
        estimate_comparisons=estimate_checks,
        methodology=dict(independence='Stimulus/semua opsi diselesaikan sebelum membaca kunci/pembahasan. Review sementara lama bukan bukti; tidak memakai generator.',
            rounding='Half-up positif sesuai contoh5naik dalam pembahasan sumber. Tempat pembulatan mengikuti soal, tanpa menambah pembulatan antara.',
            radicals='Uji kuadrat titik tengah sel pembulatan dengan Fraction/isqrt, bukan menganggap selisih kuadrat terdekat sebagai teorema umum.',
            categories='Benar/Salah per pernyataan; tidak membuat rubrik skor.',
            versions='L5Q7 dipertahankan satu kemunculan sumber dengan dua subbagian opsi; tidak memilih atau mempromosikan versi.'),entries=rows))
    fields=['audit_id','level','source_number','format','validity','answer_status','explanation_status','recommendation','independent_solution','issues']
    with (DEST/'entries.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in rows:writer.writerow({k:json.dumps(r[k],ensure_ascii=False) if k=='issues' else r[k] for k in fields})
    c=summary['recommendations']
    report=f'''# Tahap 4 — Audit akademik indikator 3

**Cakupan disetujui:** indikator 3 saja, 50 entri sumber (5 level × 10 soal). Seluruh stimulus, opsi/pernyataan, kunci, pembahasan, dan catatan diperiksa. L5Q7 mempunyai dua rangkaian opsi yang dicatat sebagai subbagian terpisah; tidak digabung menjadi satu MCMA delapan opsi dan tidak dipilih versi resmi.

| Komponen | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | {summary['validity'].get('VALID',0)} | {summary['validity'].get('INVALID',0)} | {summary['validity'].get('UNCERTAIN',0)} |
| Kunci | {summary['answer_status'].get('CORRECT',0)} | {summary['answer_status'].get('INCORRECT',0)} | {summary['answer_status'].get('UNCERTAIN',0)} |
| Pembahasan | {summary['explanation_status'].get('CORRECT',0)} | {summary['explanation_status'].get('INCORRECT',0)} | {summary['explanation_status'].get('UNCERTAIN',0)} |

Hitungan per komponen berdiri sendiri. **{c.get('NO_BLOCKING_ACADEMIC_FINDING',0)} soal tanpa temuan yang menghalangi**; {50-c.get('NO_BLOCKING_ACADEMIC_FINDING',0)} soal perlu tindak lanjut.

Temuan dan usulan **PROPOSED, belum diterapkan/disetujui Kurikulum**:

| Soal | Bukti dan dampak | Usulan |
|---|---|---|
| L5Q7 | Rangkaian awal: A/B/C benar dan D menyatakan klaim “9 cm” salah, sehingga D juga benar. Rangkaian akhir: A/B/C benar, D langsung menyatakan “9 cm” sehingga salah. Header ABD tidak cocok; tambahan ABC hanya cocok versi akhir. | Tetapkan satu versi. Jawaban kondisional: **ABCD untuk opsi meta awal; ABC untuk opsi langsung akhir**. Jangan memilih otomatis. |
| L5Q5 | Evaluasi I dan III sama-sama benar: √82→9, √35→6, selisih 3. Pertanyaan meminta evaluasi pasti benar, bukan yang paling rinci. | Bedakan opsi atau tetapkan kriteria eksplisit; kunci C tidak unik. |
| L4Q5 | Evaluasi I dan III sama-sama sah: √98→10, √45→7, selisih 3. Kata “paling tepat” tidak menjelaskan kewajiban menampilkan desimal antara. | Klarifikasi kriteria/rubrik; jangan menganggap I salah karena ringkas. |
| L1Q3 | Alasan B mengubah 78.000→80.000, tidak mengikuti ribuan terdekat; alasan D memakai 3,5×24.800=86.800, bukan 82.500. | Koreksi alasan opsi pengecoh; **kunci C, Rp81.000, tetap**. |
| L1Q5 | Alasan A menyebut kedua faktor dibulatkan ke bawah untuk 20×6.000; 19→20 justru naik. | Koreksi arah pembulatan; **kunci B, Rp140.000, tetap**. |
| L2Q3 | Alasan opsi D (Rp90.000) menyebut 4×25.000 yang sebenarnya 100.000. | Koreksi alasan opsi pengecoh; **kunci C, Rp87.500, tetap**. |

Catatan minor tanpa perubahan jawaban: pada L2Q4, model A disebut membulatkan semua angka ke bawah meskipun 9,7→10 naik; L4Q3 menyisakan penanda editorial `[cite:12]`; L4Q5/L5Q5 memakai “radian” padahal istilah yang dimaksud **radikan**.

Perhitungan pembulatan memakai pecahan eksak dan **{len(radical_checks)} uji sel pembulatan akar**, ditambah 5 uji interval dan 5 perbandingan galat estimasi. Uji akar membandingkan kuadrat titik tengah, sehingga tidak bergantung pada pembulatan desimal antara atau asumsi bahwa kuadrat terdekat selalu membuktikan pembulatan akar. Aturan angka 5 dibulatkan naik mengikuti contoh sumber; tempat pembulatan tetap sesuai instruksi tiap soal. Tidak ada rubrik skor kategori baru.

Keluaran: [JSON lengkap 50 entri dan subbagian versi](audit.json), [CSV](entries.csv). Semua opsi memiliki penilaian independen; untuk PG valid dipastikan tepat satu opsi benar. Kunci yang dinyatakan benar cocok dengan hasil independen. Seluruh {len(baseline)} hash sumber/bank/config/stok/layanan tetap sama.

Reproduksi: `python variant_gen/tests/audit_indicator_03_academic.py`. Tidak ada perubahan sumber, bank aktif, generator, atau pemetaan runtime. Audit ini bukan persetujuan publikasi/kesetaraan kesulitan. **Indikator 4 dan pencocokan generator menunggu instruksi berikutnya.**
'''
    (DEST/'README.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':run()
