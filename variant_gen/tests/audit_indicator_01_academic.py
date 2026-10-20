"""Academic evidence ledger for the explicitly authorized 50 indicator-1 entries.

Solutions below were authored from stimuli/options, before reading source keys.
This script validates the ledger and exact auxiliary calculations; it does not
pretend to be a general automated academic checker or approve source revisions.
"""
import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from audit_original_questions import ROOT, OUT, digest, read, write

DEST=OUT/'stage-02-academic-indicator-01'

# T/F vectors follow option order. Category statements retain source (a)/(b)/(c).
# Each independent derivation supplies evidence for every option, including false ones.
PROOFS={
(1,1):('FTFF','3/4, sqrt(5), -4, 4: hanya sqrt(5) irasional; 5 bukan kuadrat bilangan bulat.'),
(1,2):('FTFF','A=-9/5 < B=-7/4 < 0 < D=8/5 < C=sqrt(3); 3>(8/5)^2=64/25. A tidak di kanan B; C tidak di kiri D; D bukan paling kanan.'),
(1,3):('TFFF','Perubahan proporsional: Kuning=-38/100 < Merah=-3/8 < Hijau=-36/100 < Biru=-35/100. Besar penurunan berurutan 38%,37,5%,36%,35%; hanya urutan A cocok.'),
(1,4):('FFTF','15*18000+15*4000=330000=15*(18000+4000). Menggabungkan faktor yang sama adalah distributif; bukan pertukaran faktor, pengelompokan perkalian, atau sekadar tertutup.'),
(1,5):('TFFF','(13/4)^2=169/16 < 12 < (7/2)^2=49/4, maka -7/2 < -sqrt(12) < -13/4. Urutan X,Y,Z; B membalik X/Y, C membalik Y/Z, D menaruh Z di depan X.'),
(1,6):('TFTT','-5=-5/1 rasional dan bulat; sqrt(9)=3 bukan irasional; 22/7 rasional dengan penyebut bukan nol; pi irasional. Semua empat opsi dievaluasi.'),
(1,7):('FTTT','D=-13/5 < A=-5/2 < C=-sqrt(6) < B=-12/5 sebab (12/5)^2<6<(5/2)^2. A>D, bukan A<D. B pengurangan terkecil; C di antara -2,5/-2,4; besar pengurangan D,A,C,B.'),
(1,8):('TFTT','Untuk p/q+r/s=(ps+rq)/(qs), q,s bukan nol: hasil rasional. 5-3=2 tetapi 3-5=-2 membantah komutatif pengurangan. a(b+c)=ab+ac distributif; (ab)c=a(bc) asosiatif perkalian real.'),
(1,9):('TFT','-3/2=-1,5<-7/5=-1,4; sqrt(2)<3/2 karena 2<9/4; |-7/5|=7/5<3/2. Maka (a) benar,(b) salah,(c) benar.'),
(1,10):('TTF','25*40000+25*10000=1250000=25*50000 merupakan penerapan distributif; 25*50000=50000*25 komutatif. Pengurangan tidak komutatif: 5-3 != 3-5. Contoh numerik mengilustrasikan hukum distributif, bukan pembuktian universal tersendiri.'),
(2,1):('FFFT','Kelompok3=-31/50 < Dimas=-3/5 < Kelompok2=-29/50 < Kelompok1=-11/20. -58%=-29/50=-0,58, bukan 0,58%. Pilihan D paling kecil; A,B,C bukan minimum.'),
(2,2):('FFTF','12*(25000+3000)=336000. A=25012*3012, B=12*75000000, D=303000; ketiganya bukan total dua belas paket. Hanya C mendistribusikan 12 ke kedua komponen.'),
(2,3):('FTFF','C=-4/3 < D=-13/10 < A=-5/4 < 0 < B=sqrt(2). Jadi A salah (C kiri A), B benar, C salah (A kanan D), D salah (minimum C).'),
(2,4):('TFFF','sqrt(5)+(-sqrt(5))=0: dua irasional menghasilkan rasional, membantah klaim universal A. 3*4=12 tetap bulat; 0,5=1/2 mendukung rasional; 2+3=3+2 mendukung komutatif. B,C,D bukan penyangkal klaim asal.'),
(2,5):('FFTF','p=7-6/2=4, q=1/3 dari 10q-q=3. Keduanya rasional: C. A,D masing-masing salah pada salah satu jenis; B salah pada keduanya.'),
(2,6):('TFTF','B=-sqrt(8) < C=-11/4 < D=-27/10 < A=-5/2; 8>(11/4)^2. C=-2,75 benar; paling dingin B bukan C; (27/10)^2<8<(29/10)^2 membuktikan -2,9<B<-2,7; urutan hangat ke dingin A,D,C,B bukan C,D,B,A.'),
(2,7):('TTFT','(500000-120000)-80000=300000; 500000-(120000-80000)=460000. Counterexample menolak asosiatif, pengelompokan memengaruhi hasil. Komutatif tidak bisa menyamakan. Mengubah tanda dalam kurung menjadi + memberi 500000-200000=300000.'),
(2,8):('FTFT','-3*sqrt(2) irasional: andaikan rasional, dibagi -3 akan membuat sqrt(2) rasional. -3+5/2=-1/2 rasional. (5/2)/0 tidak terdefinisi karena 0*x tidak mungkin 5/2. sqrt(2)^2=2 bulat.'),
(2,9):('TFT','Kuning=-7/4=-1,75; Merah=-9/5=-1,8 lebih dingin, bukan lebih hangat. 3<(7/4)^2 membuktikan -sqrt(3)>-7/4. Urutan Merah,Kuning,Hijau.'),
(2,10):('TTF','Jika x rasional bukan nol dan xy rasional, y=(xy)/x rasional: kontradiksi, jadi (a) benar. Irasional didefinisikan R\\Q, maka R=Q union (R\\Q) dan Q intersection (R\\Q)=kosong: (b) benar,(c) salah.'),
(3,1):('FTFF','(13/5)^2=6,76 < 7 < (53/20)^2=7,0225; maka -2,65 < -sqrt(7) < -2,6 < -2,4. Hanya Analisis II cocok; I/III/IV melanggar rantai ini.'),
(3,2):('FFTF','16*35000+16*5000=640000=16*(35000+5000). C sesuai distributif. A menambah pengali pada harga; B mengalikan kedua harga; D hanya menambah satu pita.'),
(3,3):('TFFF','sqrt(3)*sqrt(3)=3 rasional membantah tertutupnya perkalian irasional. 5-8=-3 masih bulat; 1 asli; 4+2=2+4. Contoh B,C,D tidak menyangkal klaim yang ditulis.'),
(3,4):('FTFF','a=3sqrt(2)-sqrt(2)=2sqrt(2) irasional (jika rasional maka dibagi 2 juga rasional); 99b=12 jadi b=4/33 rasional. Hanya B cocok.'),
(3,5):('FFFT','r=-47/20 < p=-9/4 < q=-sqrt(5), karena (9/4)^2=81/16>5. r paling kiri, q kanan r, p kanan r, dan r<p<q. Maka A,B,C salah; D benar.'),
(3,6):('TFTF','W=Y=-16/5; (78/25)^2=9,7344 < 10 < (16/5)^2=10,24, sehingga W=Y<X=-sqrt(10)<Z=-78/25. W/Y paling dalam, Z paling dangkal. A dan C benar; B dan urutan D salah.'),
(3,7):('TTFT','ModelI=650000; ModelII=950000. Perbedaan ini counterexample asosiatif, dan mengubah pengelompokan berpengaruh. Komutatif pengurangan tidak berlaku. -(400000-150000)=-400000+150000 memberi ModelII=950000.'),
(3,8):('TFTT','-4sqrt(5) irasional dengan argumen pembagian -4; (3/2)/0 tidak terdefinisi; -4+3/2=-5/2 rasional; sqrt(5)^2=5 bulat. Semua empat opsi diperiksa.'),
(3,9):('TFT','Beta=-5/3=-1,666... < Alpha=-8/5 < Gamma=-sqrt(2), karena 2<(8/5)^2. (a) benar; Alpha lebih hangat dari Beta sehingga (b) salah; urutan Beta,Alpha,Gamma benar.'),
(3,10):('TTF','Untuk x dalam Q bukan nol, xy dalam Q akan memaksa y=(xy)/x dalam Q, kontradiksi. Setiap n asli juga bulat dan n=n/1 rasional. Pecahan dua bilangan bulat dengan penyebut bukan nol tidak dapat memiliki ekspansi desimal tak berakhir nonperiodik.'),
(4,1):('TTFF','A=-37/20 < C=-7/4 < B=-sqrt(3) < D=-17/10; batas (17/10)^2<3<(7/4)^2. Analisis I dan II identik dan benar; opsi A dan B sama-sama menunjuk Analisis I. C dan D bukan urutan naik. PG tidak memiliki tepat satu pilihan benar.'),
(4,2):('FFTF','x=2sqrt(5)-sqrt(5)=sqrt(5) irasional; 99y=27 sehingga y=3/11 rasional. C benar, A/B/D salah menurut jenis kedua nilai.'),
(4,3):('TFFF','18*20000+18*2500=405000=18*(20000+2500). A satu-satunya bentuk sesuai total. B mencampur pengali dengan harga; C mengalikan harga; D hanya menghitung satu pompa.'),
(4,4):('FTFF','5-3=2 sedangkan 3-5=-2: Evaluasi I salah, II benar. Jadi B; C salah karena II benar. D salah sebab 5 dan 3 sama-sama positif namun hasil pengurangannya berbeda.'),
(4,5):('FFTF','(12/5)^2<6<(5/2)^2 memberi P=-5/2<Q=-sqrt(6)<R=-12/5. Penilaian I salah (R bukan di tengah), II salah (P di kiri Q), III benar. Hanya C; D menggabungkan dua penilaian salah.'),
(4,6):('TFTT','-4=-4/1 bulat rasional; sqrt(16)=4 bukan irasional; 15/4=3,75 rasional; pi irasional. Nilai dan jenis semua opsi sudah diperiksa.'),
(4,7):('TTFT','Model1=(600000-150000)-50000=400000; Model2=600000-100000=500000. Counterexample asosiatif dan pengelompokan berpengaruh. Dua pengeluaran total200000 berarti sisa400000, bukan Model2. Penggantian menjadi 600000-(150000+50000) benar.'),
(4,8):('FTFT','-2sqrt(3) irasional; sqrt(3)^2=3 bulat; (4/3)/0 tidak terdefinisi karena 0*x tak dapat sama4/3; -2+4/3=-2/3 rasional. Kunci konseptual B,D.'),
(4,9):('TFT','B=-9/5=-1,8 < A=-7/4=-1,75 < C=-sqrt(3), sebab 3<49/16. (a) benar,(b) salah karena A lebih hangat,(c) benar.'),
(4,10):('TTF','Rasional bukan nol kali irasional tetap irasional: andaikan hasil rasional, bagi faktor rasional bukan nol untuk kontradiksi. Setiap z bulat=z/1 rasional. Q dan R\\Q saling lepas sehingga (c) salah.'),
(5,1):('FTFF','P=-39/20 < R=-9/5 < Q=-sqrt(3), sebab 3<(9/5)^2=81/25. Hanya Evaluasi II menyusun P,R,Q; I/III/IV salah.'),
(5,2):('????','Definisi awal a=sqrt(32)-2sqrt(2)=2sqrt(2) irasional, b=45/99=5/11 rasional. Definisi akhir a=sqrt(48)-4sqrt(3)=0 rasional, b sama rasional. Keduanya muncul bersama sejumlah rancangan lain dan label Evaluasi I–III dipakai ulang. Pada blok akhir saja vektor F,F,T,F dan C benar; itu hasil kondisional, bukan pemilihan versi resmi.'),
(5,3):('TFFF','UsulanI=25*27000=675000, tepat total25paket. UsulanII=15025*12025=180675625 memang hasil kali numerik yang tertulis, tetapi tidak memodelkan total paket atau distributif. Jadi A benar; B/C salah. Dua usulan masing-masing mempunyai satu operasi kali utama; II bukan lebih hemat perkalian sehingga D tidak benar.'),
(5,4):('FFTF','Contoh a=16,b=4,c=2 memenuhi domain: (16/4)/2=2, sedangkan 16/(4/2)=8; Klaim1 salah. Asosiativitas perkalian real adalah hukum aljabar: Klaim2 benar. Kombinasi salah/benar hanya C.'),
(5,5):('TTFF','B=-4/5=-0,8 dan C=-sqrt(16/25)=-4/5; A=-17/20=-0,85 lebih dalam. Evaluasi A benar tentang kesamaan, Evaluasi B benar tentang kesamaan plus perbandingan A. Evaluasi C/D salah. Pertanyaan meminta evaluasi yang benar, bukan yang paling lengkap; A dan B keduanya sah.'),
(5,6):('TFTT','-6 bulat rasional; sqrt(25)=5 rasional sehingga B salah; 22/7 rasional dan berbeda dari pi; sqrt(2) irasional. A,C,D benar.'),
(5,7):('TTF?','X=270000 dan Y=270000; -(100000+30000)=-100000-30000, jadi A/B benar sebagai penerapan hukum distributif. Bentuk 400000-(100000-30000)=330000 membantah C. D memakai kata mempermudah tanpa ukuran/formal kriteria, sehingga tidak dapat dipastikan sebagai pernyataan matematika benar/salah dari stimulus saja.'),
(5,8):('FTTF','-5sqrt(7) irasional, bukan rasional; sqrt(7)^2=7 bulat; 0/(3/5)=0 rasional karena penyebut bukan nol; (3/5)/0 tidak terdefinisi. Hanya B,C benar.'),
(5,9):('TFT','Sampel1=-9/4=Sampel2; (9/4)^2>5 berarti -9/4<-sqrt(5)=Sampel3. (a) benar,(b) salah karena Sampel3 lebih hangat,(c) benar dengan ikatan Sampel1/2 dipertahankan.'),
(5,10):('TTF','p/q+r/s=(ps+rq)/(qs) dengan q,s bukan nol membuktikan tertutupnya Q terhadap tambah. Setiap n asli ada dalam Z dan R. sqrt(3)+(-sqrt(3))=0 rasional menjadi counterexample (c).'),
}


def issue(component,severity,evidence,proposal):
    return dict(component=component,severity=severity,evidence=evidence,proposed_correction=proposal,
                correction_status='PROPOSED_NOT_APPLIED')


def run():
    source=OUT/'stage-01-extraction-01-05/validation.json'
    entries=[q for q in read(source)['entries'] if q['indicator']==1]
    assert set(PROOFS)=={(l,n) for l in range(1,6) for n in range(1,11)}
    assert len(entries)==50
    checks={
        'distributive_l1q4':15*18000+15*4000==330000,
        'distributive_l2q2':12*(25000+3000)==336000,
        'distributive_l3q2':16*(35000+5000)==640000,
        'distributive_l4q3':18*(20000+2500)==405000,
        'l5q3_both_numeric_products':25*(15000+12000)==675000 and 15025*12025==180675625,
        'l2q7_models':(500000-120000)-80000==300000 and 500000-(120000-80000)==460000,
        'l3q7_models':(1200000-400000)-150000==650000 and 1200000-(400000-150000)==950000,
        'l4q7_models':(600000-150000)-50000==400000 and 600000-(150000-50000)==500000,
        'l5q7_models':(400000-100000)-30000==270000 and 400000-(100000+30000)==270000 and 400000-(100000-30000)==330000,
        'l5q4_counterexample':(F(16)/4)/2==2 and F(16)/(F(4)/2)==8,
        'repeating_decimals':F(45,99)==F(5,11) and F(12,99)==F(4,33) and F(27,99)==F(3,11),
    }
    bounds=[(3,F(8,5),F(7,4)),(12,F(13,4),F(7,2)),(6,F(12,5),F(5,2)),
            (8,F(11,4),F(29,10)),(7,F(13,5),F(53,20)),(5,F(2),F(9,4)),
            (10,F(78,25),F(16,5)),(2,F(7,5),F(3,2)),(3,F(17,10),F(7,4))]
    exact_bounds=[]
    for n,lo,hi in bounds:
        assert lo*lo<n<hi*hi
        exact_bounds.append(dict(radicand=n,positive_lower=str(lo),positive_upper=str(hi),
                                 lower_squared=str(lo*lo),upper_squared=str(hi*hi),status='PASS'))
    assert all(checks.values())
    rows=[]
    for q in entries:
        pos=(q['level'],q['source_number']);vector,proof=PROOFS[pos]
        assert len(vector)==len(q['options']),(pos,vector)
        labels=['a','b','c'] if q['format']=='KATEGORI' else ['A','B','C','D']
        v='VALID';answer='CORRECT';explanation='CORRECT';issues=[]
        if '?' in vector:answer='UNCERTAIN';explanation='UNCERTAIN'
        if pos==(4,1):
            v='INVALID';answer='INCORRECT'
            issues.append(issue('options/key','CRITICAL',
                'Analisis I dan II sama-sama berurutan A,C,B,D; opsi A=Analisis I dan B=Analisis I (dengan urutan). Header kunci B. Analisis II berbeda dari teks opsi B.',
                'Bedakan empat urutan analisis dan empat opsi; samakan rujukan label kunci. Pastikan hanya satu opsi benar, lalu ajukan ulang ke Kurikulum.'))
        elif pos==(5,2):
            v='INVALID'
            issues.append(issue('stem/key/explanation','CRITICAL',
                'Stem mendefinisikan a berulang kali: sqrt(32)-2sqrt(2)=2sqrt(2) irasional, tetapi blok akhir sqrt(48)-4sqrt(3)=0 rasional; Evaluasi I–III juga didefinisikan ulang. Pembahasan memakai blok akhir saja.',
                'Kurikulum menetapkan satu versi. Jika blok akhir yang dipilih, hapus seluruh rancangan awal dan catatan eh wait; C baru sah untuk versi tunggal itu. Jangan pilih otomatis.'))
        elif pos==(5,5):
            v='INVALID';answer='INCORRECT';explanation='INCORRECT'
            issues.append(issue('options/key/explanation','CRITICAL',
                'Evaluasi A dan B sama-sama benar. Pembahasan memilih B karena paling lengkap, sementara pertanyaan hanya meminta evaluasi yang pasti benar.',
                'Ubah salah satu opsi agar salah, atau nyatakan kriteria jawaban paling lengkap secara eksplisit dan review ulang. Jangan menganggap A salah hanya karena lebih singkat.'))
        elif pos==(5,7):
            v='UNCERTAIN'
            issues.append(issue('option D/explanation','IMPORTANT',
                'Mempermudah rekapitulasi / memudahkan audit kas merupakan penilaian proses tanpa kriteria ukur; perhitungan membuktikan A/B benar dan C salah, tetapi tidak menetapkan D secara objektif.',
                'Ganti D dengan klaim terukur, misalnya total alokasi pengeluaran pada Y adalah Rp130.000,00, atau minta Kurikulum menyatakan kriteria penilaian D.'))
        elif pos==(1,5):
            explanation='INCORRECT'
            issues.append(issue('explanation/distractor D','MINOR',
                'Pembahasan menyebut opsi D (Z,X,Y) muncul jika urutan dibalik. Kebalikan urutan yang benar X,Y,Z ialah Z,Y,X, bukan Z,X,Y. Hitung suhu, opsi A, dan kunci tetap benar.',
                'Ganti alasan opsi D: salah karena menempatkan Z sebelum X serta X sebelum Y dalam urutan yang diminta; urutan kebalikan sebenarnya Z,Y,X.'))
        if pos in ((1,10),(2,7),(3,7),(4,7)):
            issues.append(issue('explanation/generalization','MINOR',
                'Notasi ketidaksamaan umum pada pengurangan harus dibaca dalam konteks contoh. a-b=b-a saat a=b; (a-b)-c=a-(b-c) saat c=0. Satu contoh kesamaan distributif adalah ilustrasi, bukan pembuktian universal.',
                'Tulis tidak selalu sama atau gunakan counterexample bernilai eksplisit. Sebut contoh kesamaan sebagai penerapan/ilustrasi hukum distributif. Jawaban pada data soal tetap benar.'))
        if pos in ((2,8),(3,8),(4,8),(5,8)):
            issues.append(issue('additional_notes/domain','MINOR',
                'Catatan umum menulis 0/a=0 tanpa mengulang syarat a bukan nol. Semua penyebut pada opsi 0/a yang dinilai di soal sudah diketahui bukan nol.',
                'Tambahkan syarat a bukan nol pada rumus umum 0/a=0; ini klarifikasi catatan, tidak mengubah jawaban soal.'))
        computed=[str(i+1) if q['format']=='KATEGORI' else chr(65+i) for i,t in enumerate(vector) if t=='T']
        if answer=='CORRECT':assert computed==q['parsed_key'],(pos,computed,q['parsed_key'])
        if q['format']=='PG' and v=='VALID':assert vector.count('T')==1,pos
        rows.append(dict(audit_id=q['audit_id'],indicator=1,level=pos[0],source_number=pos[1],
            source=q['source'],format=q['format'],validity=v,answer_status=answer,explanation_status=explanation,
            independent_solution=proof,option_evaluations=[dict(label=label,text=text,
                result={'T':'TRUE','F':'FALSE','?':'UNCERTAIN'}[t]) for label,text,t in zip(labels,q['options'],vector)],
            independently_correct_ids=computed if '?' not in vector else None,
            conditionally_proven_ids=computed if '?' in vector else [],
            declared_key_texts=q['declared_key_texts'],parsed_source_key=q['parsed_key'],
            explanation_review=('Perhitungan, urutan, jenis bilangan, alasan opsi dan catatan sumber dibaca seluruhnya; '
                +'penilaian dibandingkan dengan solusi independen di atas. '+
                ('Masalah/ketidakpastian dijelaskan pada issues.' if explanation!='CORRECT' else
                 'Langkah penting dan kesimpulan sesuai pada konteks data; klarifikasi redaksional terpisah bila ada.')),
            issues=issues,approval_status='NOT_CURRICULUM_APPROVED',
            recommendation=('HOLD_FOR_SOURCE_REVISION' if v=='INVALID' else 'HOLD_FOR_CLARIFICATION' if v=='UNCERTAIN' else
                            'REVISE_EXPLANATION' if explanation=='INCORRECT' else 'NO_BLOCKING_ACADEMIC_FINDING'),
            generator_matching_status='NOT_EVALUATED_IN_THIS_STAGE'))
    protected=read(OUT/'protected-inputs.json')['sha256']
    assert all(digest(ROOT/path)==h for path,h in protected.items())
    summary=dict(scope='Indikator 1, level 1–5, soal 1–10: 50 entri',review_date='2026-10-20',
        entries=len(rows),validity=dict(Counter(r['validity'] for r in rows)),
        answer_status=dict(Counter(r['answer_status'] for r in rows)),
        explanation_status=dict(Counter(r['explanation_status'] for r in rows)),
        recommendations=dict(Counter(r['recommendation'] for r in rows)),
        protected_files_checked=len(protected),protected_hashes_unchanged=True,
        source_sha256=read(source)['summary']['source_sha256'],
        stage1_evidence_sha256=digest(source),review_script_sha256=digest(Path(__file__)))
    DEST.mkdir(parents=True,exist_ok=True)
    write(DEST/'audit.json',dict(summary=summary,exact_calculation_checks=checks,exact_radical_bounds=exact_bounds,
        methodology=dict(independence='Solusi dan vektor semua opsi diturunkan dari stimulus sebelum membaca kunci/pembahasan; tidak memakai jawaban generator atau review sementara lama.',
            category_scoring='Hanya nilai Benar/Salah per pernyataan; tidak membuat rubrik skor.',
            precision='Perbandingan utama memakai pecahan eksak dan batas kuadrat; perkiraan desimal sumber bukan nilai eksak baru.',
            status='Kunci nonunik PG diberi INCORRECT walaupun huruf terpilih menunjuk salah satu pernyataan benar. Kebenaran soal, kunci, dan pembahasan terpisah.',
            unresolved='Versi bercampur dan pernyataan subjektif tetap tertahan. Proposal belum diterapkan/disetujui.'),entries=rows))
    with (DEST/'entries.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['audit_id','level','source_number','format','validity','answer_status','explanation_status','recommendation','independent_solution','issues']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in rows:writer.writerow({k:(json.dumps(row[k],ensure_ascii=False) if k=='issues' else row[k]) for k in fields})
    report='''# Tahap 2 — Audit akademik indikator 1

**Cakupan disetujui:** 50 soal indikator 1 saja (5 level × 10 soal). Tidak melakukan pencocokan original/generator, perubahan soal, publikasi, atau audit indikator lain dalam tahap ini.

Seluruh stimulus, opsi/pernyataan, kunci, pembahasan, dan catatan dibaca. Solusi independen dan penilaian seluruh opsi tersedia per soal, termasuk yang tidak memiliki satu jawaban final. Perbandingan angka utama memakai pecahan eksak/batas kuadrat; tidak ada aturan pembulatan baru. Kategori dinilai per pernyataan tanpa mengarang rubrik skor.

| Komponen | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | 46 | 3 | 1 |
| Kunci | 46 | 2 | 2 |
| Pembahasan | 46 | 2 | 2 |

Hitungan setiap baris berdiri sendiri, bukan dijumlahkan menjadi jumlah soal bermasalah. Ada **5 soal yang membutuhkan tindak lanjut**, termasuk satu soal yang hanya memerlukan koreksi alasan distractor.

| Lokasi | Bukti dan dampak | Usulan (PROPOSED, belum diterapkan) |
|---|---|---|
| L4 soal 1 | Urutan A,C,B,D benar; Analisis I dan II sama. Opsi A dan B sama-sama merujuk Analisis I; header B menyebut Analisis II. PG tidak unik. Pembahasan urutan benar, tetapi tidak membuat kunci menjadi unik. | Bedakan analisis/opsi, samakan label kunci, pastikan tepat satu opsi benar. |
| L5 soal 2 | Definisi awal a=2√2 irasional; definisi akhir a=0 rasional. Beberapa rancangan dan label evaluasi bercampur. C hanya benar jika blok akhir dipilih. | Kurikulum menetapkan satu versi; hapus rancangan lain setelah keputusan. Tidak memilih otomatis. |
| L5 soal 5 | B=C=−0,8 dan A=−0,85. Evaluasi A serta B sama-sama benar. Pembahasan memilih B karena paling lengkap, sedangkan stem tidak meminta itu. | Perbaiki opsi atau tetapkan kriteria pertanyaan secara eksplisit. |
| L5 soal 7 | A/B benar dan C salah secara hitung; D “mempermudah rekapitulasi” tidak memiliki kriteria objektif. | Ganti D dengan klaim terukur atau minta klarifikasi Kurikulum. |
| L1 soal 5 | Kunci A dan urutan X,Y,Z benar. Alasan distractor D menyebut Z,X,Y sebagai kebalikan, padahal kebalikannya Z,Y,X. | Koreksi alasan distractor; tidak perlu mengganti jawaban A. |

Empat pembahasan tentang sifat operasi (L1Q10, L2Q7, L3Q7, L4Q7) mendapat catatan redaksional: ketidakkomutatifan/ketidakasosiatifan berarti kesamaan **tidak selalu** berlaku, bukan tidak pernah berlaku. Contoh khusus pengurangan dapat sama ketika a=b atau c=0. Jawaban pada data soal tetap benar. Catatan pembagian di L2Q8, L3Q8, L4Q8, L5Q8 sebaiknya menuliskan syarat a≠0 pada 0/a=0; domain opsi sumber sendiri sudah jelas.

Sebanyak **45 soal tidak memiliki temuan akademik yang menghalangi** pada pemeriksaan ini; itu bukan persetujuan Kurikulum atau bukti kesetaraan kesulitan. Status per komponen dan bukti lokasi paragraf tersimpan di [JSON lengkap](audit.json), serta [CSV 50 soal](entries.csv).

Validasi: cakupan 50 posisi unik, panjang vektor penilaian sesuai opsi, seluruh kunci berstatus benar cocok dengan solusi independen, semua PG valid mempunyai tepat satu opsi benar, perhitungan eksak lulus, dan 859 hash berkas sumber/bank/config/stok/layanan tetap sama. Reproduksi: `python variant_gen/tests/audit_indicator_01_academic.py`.

**Indikator 2 dan pencocokan generator menunggu instruksi berikutnya.**
'''
    (DEST/'README.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':run()
