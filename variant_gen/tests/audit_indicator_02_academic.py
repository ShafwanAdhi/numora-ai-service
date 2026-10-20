"""Bounded academic evidence ledger: indicator 2 only, no source/runtime writes."""
import csv
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from audit_original_questions import ROOT, OUT, digest, read, write
from audit_indicator_01_academic import issue

DEST=OUT/'stage-03-academic-indicator-02'
# Independent option vectors and derivations, authored from stimulus/options.
PROOFS={
(1,1):('FTFF','30000-18000+20000-12500-6000+5000=18500. B satu-satunya nominal yang cocok; A/C/D berbeda.'),
(1,2):('FTFF','Salah=25-16-3=6. Skor=16*4-6*2-3=49, jadi B; A43,C52,D58 tidak cocok.'),
(1,3):('FFTF','d²=(4sqrt(6))²+(2sqrt(3))²=96+12=108, d positif=6sqrt(3). Kuadrat opsi A48,B84,C108,D336: hanya C.'),
(1,4):('FTFF','2,5jam=150menit=5periode. Banyak akhir=2^3*2^5=2^8=256. Eksponen7/9/10 pada A/C/D bukan8.'),
(1,5):('TFFF','Belanja=3*18000+4*14000=110000; tagihan108000 setelah diskon; bayar150000; kembali42000. Hanya A.'),
(1,6):('TTFT','(i)5sqrt(2)+3sqrt(2)=8sqrt(2); (ii)3^(4-2)=9; (iii)sqrt(36)=6 bukan36; (iv)2^(3*2)=64. A,B,D benar.'),
(1,7):('TFTT','Setiap kelompok60/4=15; digunakan(2/3)*15=10 bukan5; sisa5; setiap anggota5/5=1. A,C,D benar.'),
(1,8):('TFTF','12/3=4; 2*(-5)=-10 bukan10. H=24-4-10=10. Kiri-ke-kanan tanpa prioritas: (((24-12)/3)+2)*(-5)=-30, bukan10. A,C benar.'),
(1,9):('TFT','Tepung(7/2)*12000=42000; gula(9/4)*16000=36000<42000; total78000. a,c benar; b salah.'),
(1,10):('TTF','P=(4*3)^2=144; Q=12+9=21; selisih123 bukan120. a,b benar; c salah.'),
(2,1):('FTFF','45000-8500+25000-14000-6000+10000=51500. Hanya B; tanpa cashback41500 adalah C, bukan saldo sebenarnya.'),
(2,2):('TFFF','3sqrt(20)-sqrt(45)=6sqrt(5)-3sqrt(5)=3sqrt(5), jadi A. Koefisien B4,C2,D5 berbeda.'),
(2,3):('????','Jika tepat7periode:3²*3^7=3^9 sehingga C. Tetapi2,33jam=139,8menit, bukan140; untuk pembelahan diskret20menit baru6periode lengkap sehingga3^8 (tidak ada opsi). Jawaban C bersyarat pada140menit/7periode yang juga eksplisit dalam stem dan pertanyaan.'),
(2,4):('FTFF','15-12/4+2*(-4)=15-3-8=4. LangkahII benar; I mengubah prioritas dengan kurung15-12; III menambah kurung4+2; IV mengalikan seluruh jumlah dengan-4. A/C/D bukan ekspresi asal.'),
(2,5):('TFFF','3*24000+3*16000-5000=115000=3*(24000+16000)-5000. A cocok beserta alasan. B/D merestui model yang kehilangan dua botol; C salah karena diskon tidak dikurangi sebelum perkalian.'),
(2,6):('TTFT','2^(5-2)=8; sqrt(72)-sqrt(18)=(6-3)sqrt(2)=3sqrt(2); (3²)^3=3^6=729 bukan243; sqrt(8*2)=4. A,B,D benar.'),
(2,7):('TTFF','A=(150000-40000)-25000=85000; B=150000-(40000+25000)=85000, penerapan -(u+v)=-u-v. Ganti tanda dalam kurung menjadi minus memberi135000, bukan85000. Dua metode masing-masing dua operasi biner, jadi D salah.'),
(2,8):('FTFT','16/(-4)=-4, bukan4; 3/2=1,5. M=-4+3/2+2=-1/2=-0,5, bukan-3,5. B,D benar.'),
(2,9):('TFT','Telur(5/2)*28000=70000; daging(5/4)*40000=50000 lebih murah, bukan lebih mahal; total120000. a,c benar.'),
(2,10):('TTF','P=(10-5)sqrt(2)=5sqrt(2); Q=(8*3)^2/36=16. Dengan pendekatan tertulis1,414, P≈7,07<16; c mengklaim Q lebih kecil, salah.'),
(3,1):('FTFF','Saldo=120000-35000+75000-40000+15000-25000=110000. AnalisisI salah menandai cashback dan memberi80000. B benar; A/C mendukung model salah; D menyebut semua pemasukan di akhir padahal AnalisisII tidak demikian.'),
(3,2):('FFTF','SisiA=sqrt(108)=6sqrt(3); sisiB=sqrt(27)=3sqrt(3); selisih3sqrt(3), C. Koefisien9/6/2 pada A/B/D berbeda.'),
(3,3):('FTFF','Yang ditanya kulturY, awal2² dan6pembelahan selama180/30menit. Akhir2^(2+6)=2^8, B. DataX tidak digunakan; A/C/D bukan2^8.'),
(3,4):('FFTF','30-18/3+4*(-2)=30-6-8=16, cara siswaC. A mendahulukan30-18, B menambah kurung3+4, D memperluas faktor-2 ke jumlah; ketiganya mengubah ekspresi.'),
(3,5):('TFFF','4*(8000+3500)-5000=41000. A tepat model dan alasan; B/D menghilangkan kuantitas pulpen, C salah mendahulukan diskon dibanding perkalian dalam model.'),
(3,6):('TTFT','3^(6-3)=27; sqrt(98)-sqrt(50)=(7-5)sqrt(2)=2sqrt(2); (2^4)^2=2^8=256 bukan128; sqrt(18*2)=6. A,B,D benar.'),
(3,7):('TTF?','Rumus1=100000=Rumus2; -(60000+40000)=-60000-40000. Ganti+ menjadi- di dalam kurung memberi180000, bukan100000. A/B benar dan C salah. D mempermudah rekapitulasi tidak memiliki ukuran objektif yang ditetapkan.'),
(3,8):('FTFT','20/(-5)=-4 bukan4; 4*(1/2)=2. N=-4+2-(-3)=1, bukan-1. B,D benar.'),
(3,9):('TFT','Beras(9/2)*14000=63000; telur(9/4)*28000=63000 sama mahal, bukan lebih murah; total126000. a,c benar.'),
(3,10):('TTF','P=(10-5)sqrt(3)=5sqrt(3); Q=(9*2)^2/36=9. Dengan pendekatan tertulis1,732,P≈8,66<9, sehingga klaim Q<P salah. a,b benar.'),
(4,1):('TTFF','AnalisisI danII identik secara prioritas: perkalian15*18000=270000 lebih dulu, saldo1080000. Kurung tambahan pada II tidak wajib. III/IV mengubah model transaksi. Tidak ada kriteria terukur untuk mengutamakan II daripada I yang sama-sama sah.'),
(4,2):('FTFF','sqrt(75)+sqrt(108)-sqrt(27)=(5+6-3)sqrt(3)=8sqrt(3). Hanya B; koefisien A5,C6,D12 salah.'),
(4,3):('FTFF','(2³)^4*2^-2/2²=2^(12-2-2)=2^8=256, B. A6,C10,D12 bukan eksponen akhir.'),
(4,4):('TFFF','(9/2)/(1/2)+2*(1/4)=9+1/2=9,5. EvaluasiI dan alasan A benar. EvaluasiII=2,75 berasal dari perubahan prioritas, jadi B/D salah; C mengklaim10 juga salah.'),
(4,5):('TF?F','9^-1=3^-2 dan27^(2/3)=9=3²; hasil3^(5-2-2)=3. Langkah kedua siswa sah, maka A benar dan B/D salah. C memuji B paling tepat karena lebih rinci; tidak ada kriteria yang membuat langkah A yang ringkas menjadi tidak sah atau kalah sebagai jawaban benar.'),
(4,6):('TFTT','2sqrt(48)=8sqrt(3); sqrt(75)=5sqrt(3) bukan3sqrt(5); sqrt(12)=2sqrt(3); total(8-5+2)sqrt(3)=5sqrt(3). A,C,D benar.'),
(4,7):('TTFT','Pada domain asal a≠0,b≠0: a^(3-(-1))*b^(-2-4)=a^4*b^-6=a^4/b^6. A,B,D identitas benar. C bukan identitas (misal a=2,b=1 memberi16 versus4), walau bisa kebetulan sama pada nilai khusus.'),
(4,8):('FTTF','Biaya=4*12500+6*3500-5000=66000;71000 adalah sebelum diskon. Model2 mencampur harga dan kuantitas, bukan model transaksi. B,C benar; A,D salah.'),
(4,9):('TTT','Perkalian(5/4)*(2/5)=1/2; ekspresi asal3/4+1/2=5/4. Hipotesis penjumlahan dulu:(3/4+5/4)*(2/5)=2*(2/5)=4/5=0,8. Hipotesis numerik b benar, walaupun prosedur itu tidak sah untuk ekspresi asal. a,b,c semuanya benar menurut teks.'),
(4,10):('TTF','sqrt(50)*sqrt(18)=sqrt(900)=30; sqrt(9)=3; hasil30/3=10 bukan10sqrt(2). a,b benar; c salah.'),
(5,1):('FTFF','1500000-20*22500+800000-450000=1400000. HanyaII memodelkan transaksi tepat. I mengurangi kuantitas dari uang sebelum dikali harga; III menyatukan sponsor ke biaya buku; IV membalik tanda penerimaan/pengeluaran.'),
(5,2):('FFTF','sqrt(98)+sqrt(50)-sqrt(32)=(7+5-4)sqrt(2)=8sqrt(2). Y benar, C. A memakai aturan akar yang tidak sah; B salah karena sqrt(116)=2sqrt(29) masih dapat disederhanakan; D18sqrt(2) salah.'),
(5,3):('FTFF','(3²)^3*3^-1/3³=3^(6-1-3)=3²=9. B tepat. A menjumlahkan pangkat bertingkat, C memilih hasil salah berdasarkan efisiensi, D memberi27 bukan9.'),
(5,4):('TFFF','(32/5)/(4/5)+3/2=8+1,5=9,5. A benar; B/D mengubah prioritas; C mengklaim6,4/0,8=0,8 padahal8.'),
(5,5):('FFTF','16^-1=2^-4 dan8^(2/3)=4=2²; hasil2^(6-4-2)=2^0=1. Langkah A dan B keduanya sah. A/B pada opsi menyatakan identitas yang salah, D hasil0 salah; C mendukung derivasiB yang sah, satu-satunya pilihan yang dapat diterima. Penjabaran8=2³ sebaiknya ditulis eksplisit agar alasan C sesuai langkah tampak.'),
(5,6):('TFTT','3sqrt(32)=12sqrt(2); sqrt(50)=5sqrt(2) bukan2sqrt(5); sqrt(18)=3sqrt(2); total(12-5+3)sqrt(2)=10sqrt(2). A,C,D benar.'),
(5,7):('TTFT','Pada domain asal x≠0,y≠0: x^(4-(-2))*y^(-3-2)=x^6/y^5. A,B,D benar sebagai identitas. C bukan identitas (x=2,y=1: hasil64, bukan4); nilai khusus tidak menjadikannya penyederhanaan umum.'),
(5,8):('FTTF','5*8000+4*15000=100000; setelahcashback10000 bersih90000. ModelI sah, II salah menggabung harga dan jumlah. B,C benar; A,D salah.'),
(5,9):('TTT','Perkalian(3/2)*(1/5)=3/10; ekspresi asal4/5+3/10=11/10. Hipotesis penjumlahan dulu:(4/5+3/2)*(1/5)=23/50=0,46 benar secara hitung. Ketidaksahan prosedur untuk ekspresi asal tidak membuat klaim kondisional b salah. a,b,c benar.'),
(5,10):('TTF','sqrt(72)*sqrt(2)=sqrt(144)=12; sqrt(16)=4;12/4=3, bukan3sqrt(2). a,b benar; c salah.'),
}


def run():
    stage1=OUT/'stage-01-extraction-01-05/validation.json'
    entries=[q for q in read(stage1)['entries'] if q['indicator']==2]
    assert len(entries)==50 and set(PROOFS)=={(l,n) for l in range(1,6) for n in range(1,11)}
    findings={
    (1,1):[issue('explanation/distractors','MINOR','Lupa es krim memberi24500, bukan opsiC20500. Mengganti cashback+5000 menjadi-5000 memberi8500, bukan opsiD22500.','Pertahankan saldo18500 dan kunciB; ganti alasan distractor dengan skenario yang benar-benar menghasilkan nominal opsi, atau hapus atribusi keliru.')],
    (1,2):[issue('explanation/distractor A','MINOR','Tambahan penalti-9 memberi43, tetapi alternatif-6 yang juga disebut dalam alasan A memberi46, bukan43.','Hapus alternatif-6 dari penjelasan opsi43 atau jelaskan hasil46 secara terpisah; kunci49 tetap.')],
    (1,5):[issue('explanation/distractors','MINOR','Tanpa diskon kembalian40000, bukanB38000. Diskon dianggap biaya tambahan memberi38000, bukanD28000. Mengganti harga minuman16000 saja dan tetapdiskon memberi34000, bukanC32000.','Koreksi alasanB/C/D; nyatakan semua kesalahan asumsi yang diperlukan. Jawaban42000 tetap.')],
    (2,1):[issue('explanation/distractor A','MINOR','Mengabaikan saldoawal45000 memberi25000+10000-28500=6500, bukan19500. Pembahasan menyisipkan+13000 tanpa transaksi sumber.','Hapus+13000 dan klaim alasanA; gunakan alasan distractor yang dapat ditelusuri. Saldo51500 tetap.')],
    (2,3):[issue('stem/time','IMPORTANT','2,33jam=139,8menit, bukan140. Sumber juga menyatakan7periode dan menanyakan setelah7pembelahan. Pembelahan diskret20menit baru6periode pada139,8menit.','Gunakan140menit atau2jam20menit tepat; bila2,33jam dimaksudkan pendekatan, tulis pendekatan dan jangan jadikan batas pembelahan ambigu. C hanya sah untuk7periode.')],
    (3,1):[issue('explanation/sign','IMPORTANT','Baris85.000+75.000-40.000+15.000-25.000 diubah menjadi160.000+40.000+15.000-25.000; tanda-40.000 menjadi+40.000. Baris berikutnya kembali120.000 sehingga rantai kesamaan tidak sah.','Ganti baris menjadi160.000-40.000+15.000-25.000; lanjut120.000+15.000-25.000=110.000. KunciB tetap.')],
    (3,7):[issue('option D/explanation','IMPORTANT','Mempermudah rekapitulasi / lebih praktis secara administrasi tidak memiliki ukuran objektif dalam stimulus.','GantiD dengan klaim terukur, misalnya totalpengeluaran100000, atau tetapkan kriteria Kurikulum; A/B benar,C salah.')],
    (4,1):[issue('options/selection','IMPORTANT','AnalisisI danII sama-sama sah menurut prioritasoperasi dan sama-sama memberi1080000. Kurung pada15×18000 opsional; soal tidak mendefinisikan lebih logis sebagai lebih eksplisit.','Kurikulum memperjelas kriteria, misalnya meminta penulisan yang menandai perkalian dengan kurung, atau ubah opsi sehingga hanya satu model sah. Jangan anggapI salah hanya karena tanpa kurung.')],
    (4,2):[issue('key/explanation','CRITICAL','Pembahasan menulis(5+6-3)sqrt(3)=6sqrt(3). Koefisien yang benar8; opsiB8sqrt(3), bukan kunciC6sqrt(3).','Ubah usulan kunci keB dan hasil pembahasan8sqrt(3); soal dan opsi sumber sudah menyediakan jawaban benar.')],
    (4,3):[issue('explanation/exponent rule','IMPORTANT','Baris sifat pangkat dari pangkat ditulis (a^m)^n × a^(m-n), bukan identitas (a^m)^n=a^(mn). Langkah numerik2^12 dan hasil2^8 benar.','Ganti rumus umum dengan(a^m)^n=a^(m*n) pada domain yang sesuai; tetap2^(3*4)=2^12 dan hasil2^8.')],
    (4,5):[issue('options/selection','IMPORTANT','A menyatakan langkah siswaA benar karena27^(2/3)=9, dan pernyataan itu benar. C memuji langkahB lebih rinci. Rincian tambahan tidak membuat langkahA tidak sah; kriteria memilih satu evaluasi belum jelas.','Bedakan kebenaran matematis dan kelengkapan penjabaran; tetapkan pertanyaan/rubrik eksplisit atau ubah opsiA agar tidak menjadi jawaban benar tambahan.')],
    (4,9):[issue('key/explanation/conditional','CRITICAL','Pernyataanb berbunyi jika penjumlahan dilakukan terlebih dahulu, hasil0,8; (3/4+1,25)*0,4=0,8 benar. Pembahasan mengakui hitungan benar lalu menilaiSALAH karena prosedur tidak sah.','Untuk teks sekarang, usulkanbBENAR (a,b,cBENAR). Jika inginbSALAH, ubah menjadi klaim bahwa mendahulukan penjumlahan adalah prosedur sah, lalu review ulang. Catatan sumber disepakatiSALAH bukan persetujuan audit atas perubahan makna.')],
    (4,10):[issue('additional_notes/distractor derivation','MINOR','Kesalahan antara15sqrt(2) lalu dibagi3 menghasilkan5sqrt(2), bukan10sqrt(2) seperti simpulan catatan.','Koreksi contoh jalur kesalahan atau hapus atribusi10sqrt(2). Jawaban10 dan kategoriTTF tetap.')],
    (5,9):[issue('key/explanation/conditional','CRITICAL','Pernyataanb secara kondisional menyatakan hasil0,46 bila tambah lebih dulu; (4/5+1,5)*0,2=0,46 benar. Pembahasan menolak karena langkah melanggarprioritas, mengubah pertanyaan tentang hasil menjadi keabsahan langkah.','Untuk tekssekarang usulkanbBENAR, atau ubah pernyataanb agar menanyakan keabsahanprosedur; butuhpersetujuan Kurikulum.')],
    (5,10):[issue('additional_notes/distractor derivation','MINOR','Catatan mengabaikan faktor sqrt(2) dan langsung membagi6sqrt(2) dengan4; hasilnya(3/2)sqrt(2), bukan3sqrt(2) yang disebut.','Perbaiki contoh jalur kesalahan; hasil benar tetap3 dan kategoriTTF.')],
    }
    checks={
        'balances':30000-18000+20000-12500-6000+5000==18500 and 45000-8500+25000-14000-6000+10000==51500,
        'score':16*4-(25-16-3)*2-3==49,
        'change':150000-(3*18000+4*14000-2000)==42000,
        'growth_period_boundary':F(233,100)*60==F(699,5) and F(699,5)//20==6 and 140//20==7,
        'fraction_operations':F(16,-4)+3*F(1,2)-(-2)==F(-1,2) and F(20,-5)+4*F(1,2)-(-3)==1,
        'category_hypotheses':(F(3,4)+F(5,4))*F(2,5)==F(4,5) and (F(4,5)+F(3,2))*F(1,5)==F(23,50),
        'correct_category_expressions':F(3,4)+F(5,4)*F(2,5)==F(5,4) and F(4,5)+F(3,2)*F(1,5)==F(11,10),
        'cashflow_l3q1':120000-35000+75000-40000+15000-25000==110000,
        'cashflow_l4q1':1200000-15*18000+500000-350000==1080000,
        'cashflow_l5q1':1500000-20*22500+800000-450000==1400000,
        'radical_coefficients':5+6-3==8 and 8-5+2==5 and 12-5+3==10 and 7+5-4==8,
        'exponents':F(2**12,2**2*2**2)==2**8 and F(3**6,3*3**3)==9 and F(2**6,16*4)==1 and F(3**5,9*9)==3,
        'category_roots':30/3==10 and 12/4==3,
    }
    assert all(checks.values())
    rows=[]
    for q in entries:
        pos=(q['level'],q['source_number']);vector,proof=PROOFS[pos]
        assert len(vector)==len(q['options'])
        validity='VALID';answer='CORRECT';explanation='CORRECT';issues=findings.get(pos,[])
        if pos in ((2,3),(3,7),(4,1),(4,5)):
            validity='INVALID' if pos==(2,3) else 'UNCERTAIN';answer='UNCERTAIN';explanation='UNCERTAIN'
        if pos in ((1,1),(1,2),(1,5),(2,1),(3,1),(4,2),(4,3),(4,9),(4,10),(5,9),(5,10)):
            explanation='INCORRECT'
        if pos in ((4,2),(4,9),(5,9)):answer='INCORRECT'
        if pos in ((4,7),(5,7)):
            issues=issues+[issue('stem/domain','MINOR','Pangkatnegatif mensyaratkan variabel bukan nol, tetapi domain tidak ditulis eksplisit. Domain asal ekspresi sudah mengecualikan nol.','Tuliskan a,b≠0 atau x,y≠0. Penyederhanaan berlaku pada domain asal, tidak memperluasnya ke nol.')]
        if pos==(5,5):
            issues=issues+[issue('explanation/completeness','MINOR','Alasan opsiC menyebut konversi8=2³ secara eksplisit, tetapi lembarB sudah langsung menuliskan penyebut2²; pembahasan akhir baru menjabarkan8^(2/3).','Tampilkan konversi8=(2³) pada langkah siswaB agar klaimrinci sesuai teks. Kedua siswa tetap menghasilkan1; opsiA/B/D mengandung klaim salah.')]
        ids=[str(i+1) if q['format']=='KATEGORI' else chr(65+i) for i,t in enumerate(vector) if t=='T']
        if answer=='CORRECT':assert ids==q['parsed_key'],(pos,ids,q['parsed_key'])
        if validity=='VALID' and q['format']=='PG':assert vector.count('T')==1
        recommendation=('HOLD_FOR_SOURCE_REVISION' if validity=='INVALID' else 'HOLD_FOR_CLARIFICATION' if validity=='UNCERTAIN' else
            'REVISE_KEY_AND_EXPLANATION' if answer=='INCORRECT' else 'REVISE_EXPLANATION' if explanation=='INCORRECT' else 'NO_BLOCKING_ACADEMIC_FINDING')
        rows.append(dict(audit_id=q['audit_id'],indicator=2,level=pos[0],source_number=pos[1],source=q['source'],format=q['format'],
            validity=validity,answer_status=answer,explanation_status=explanation,independent_solution=proof,
            option_evaluations=[dict(label=(chr(97+i) if q['format']=='KATEGORI' else chr(65+i)),text=text,
                result={'T':'TRUE','F':'FALSE','?':'UNCERTAIN'}[t]) for i,(text,t) in enumerate(zip(q['options'],vector))],
            independently_correct_ids=ids if '?' not in vector else None,conditionally_proven_ids=ids if '?' in vector else [],
            declared_key_texts=q['declared_key_texts'],parsed_source_key=q['parsed_key'],
            explanation_review=('Seluruh pembahasan dan catatan dibandingkan dengan derivasi independen. '+
                ('Langkah penting sesuai pada domain/data soal; catatan redaksional terpisah bila ada.' if explanation=='CORRECT' else 'Masalah atau ketidakpastian terurai pada issues.')),
            issues=issues,recommendation=recommendation,approval_status='NOT_CURRICULUM_APPROVED',generator_matching_status='NOT_EVALUATED_IN_THIS_STAGE'))
    baseline=read(OUT/'protected-inputs.json')['sha256'];assert all(digest(ROOT/p)==h for p,h in baseline.items())
    summary=dict(scope='Indikator 2 saja, 50 soal',review_date='2026-10-20',entries=50,
        validity=dict(Counter(r['validity'] for r in rows)),answer_status=dict(Counter(r['answer_status'] for r in rows)),
        explanation_status=dict(Counter(r['explanation_status'] for r in rows)),recommendations=dict(Counter(r['recommendation'] for r in rows)),
        source_sha256=read(stage1)['summary']['source_sha256'],stage1_evidence_sha256=digest(stage1),script_sha256=digest(Path(__file__)),
        protected_files_checked=len(baseline),protected_hashes_unchanged=True)
    DEST.mkdir(parents=True,exist_ok=True)
    write(DEST/'audit.json',dict(summary=summary,exact_calculation_checks=checks,
        methodology=dict(scope='Tidak mengaudit indikator lain atau mencocokkan generator.',
            independence='Derivasi stimulus dan semua opsi disusun sebelum pembacaan kunci/pembahasan; review sementara lama tidak dipakai sebagai bukti.',
            semantics='Klaim hasil hitung hipotesis dibedakan dari klaim prosedur sah; domain pangkat negatif tetap domain asal.',
            precision='Pecahan eksak; tidak membulatkan waktu ke batas periode tanpa instruksi.',
            scoring='Benar/Salah per pernyataan kategori, tanpa menetapkan rubrik skor.'),entries=rows))
    fields=['audit_id','level','source_number','format','validity','answer_status','explanation_status','recommendation','independent_solution','issues']
    with (DEST/'entries.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in rows:writer.writerow({k:json.dumps(r[k],ensure_ascii=False) if k=='issues' else r[k] for k in fields})
    counts=summary['recommendations']
    report=f'''# Tahap 3 — Audit akademik indikator 2

Cakupan: **50 soal indikator 2 saja**, lima level × sepuluh soal. Semua opsi/pernyataan, kunci, langkah pembahasan, serta catatan diperiksa. Tidak mencocokkan generator dan tidak mengubah sumber atau bank.

| Komponen | Benar/valid | Bermasalah | Belum dapat dipastikan |
|---|---:|---:|---:|
| Soal | {summary['validity'].get('VALID',0)} | {summary['validity'].get('INVALID',0)} | {summary['validity'].get('UNCERTAIN',0)} |
| Kunci | {summary['answer_status'].get('CORRECT',0)} | {summary['answer_status'].get('INCORRECT',0)} | {summary['answer_status'].get('UNCERTAIN',0)} |
| Pembahasan | {summary['explanation_status'].get('CORRECT',0)} | {summary['explanation_status'].get('INCORRECT',0)} | {summary['explanation_status'].get('UNCERTAIN',0)} |

Hitungan per komponen terpisah. **{counts.get('NO_BLOCKING_ACADEMIC_FINDING',0)} soal tanpa temuan yang menghalangi**, termasuk catatan minor domain/redaksi. Sebanyak {50-counts.get('NO_BLOCKING_ACADEMIC_FINDING',0)} soal memerlukan tindak lanjut; kesalahan alasan distractor dihitung karena pembahasan diperiksa seluruhnya, walaupun kunci akhirnya benar.

Temuan utama dan usulan **PROPOSED, belum diterapkan/disetujui Kurikulum**:

| Soal | Temuan | Tindak lanjut |
|---|---|---|
| L4Q2 | (5+6−3)√3=8√3, bukan6√3. | Usulan kunci **B**, bukanC; koreksi pembahasan. |
| L4Q9 | (3/4+1,25)×0,4=0,8; pernyataan kondisional b benar. | Usulan kategori **Benar, Benar, Benar** untuk teks sekarang; atau ubah b agar menilai keabsahan prosedur. |
| L5Q9 | (4/5+1,5)×0,2=0,46; masalah semantik sama. | Usulan **Benar, Benar, Benar** untuk teks sekarang; jangan mengganti pertanyaan tentang hasil menjadi penilaian prosedur. |
| L2Q3 | 2,33jam=139,8menit, bukan140; belum7periode20menit lengkap. C sah jika memakai7periode yang juga tertulis. | Tetapkan140menit/2jam20menit; tidak membulatkan otomatis. |
| L4Q1 | AnalisisI/II sama-sama sah; kurung tambahan tidak wajib. | Perjelas kriteria pemilihan tunggal atau ubah opsi. |
| L4Q5 | LangkahA sah (hasil3); B juga sah dan lebih rinci. OpsiA benar, sementaraC mengutamakan rincian tanpa kriteria jelas. | Klarifikasi kriteria/rubrik atau bedakan opsi. |
| L3Q7 | D menyatakan mempermudah rekapitulasi tanpa ukuran objektif. | Ganti dengan pernyataan terukur atau minta kriteria Kurikulum. |
| L3Q1 | Baris tengah pembahasan mengganti−40.000 menjadi+40.000 sebelum kembali ke hasil110.000. | Koreksi tanda; kunciB tetap. |
| L4Q3 | Rumus umum pangkat dari pangkat salah tulis; perhitungan numeriknya benar. | Tulis (a^m)^n=a^(mn); hasil2^8 tetap. |

Enam soal lain memerlukan koreksi alasan distractor/catatan: **L1Q1, L1Q2, L1Q5, L2Q1, L4Q10, L5Q10**. Contoh: lupa es krim padaL1Q1 memberi24.500, bukan20.500; padaL4Q10,15√2÷3=5√2, bukan10√2. Detail semua kesalahan, dampak, dan usulan ada per soal di JSON/CSV.

Domain a,b≠0 padaL4Q7 serta x,y≠0 padaL5Q7 perlu ditulis eksplisit; penyederhanaannya benar pada domain asal. L5Q5 perlu memperjelas penulisan konversi basis yang disebut dalam alasan opsiC; kunciC tetap satu-satunya opsi yang dapat diterima di antara opsi yang tersedia.

Bukti: [JSON lengkap 50 soal](audit.json), [CSV](entries.csv). Validasi mencakup cakupan unik, seluruh opsi, kecocokan kunci yang dinyatakan benar, PG valid tepat satu jawaban, serta {len(checks)} pemeriksaan hitung eksak. Semua {len(baseline)} hash sumber/bank/config/stok/layanan tetap sama.

Reproduksi: `python variant_gen/tests/audit_indicator_02_academic.py`. Hasil ini audit akademik, bukan persetujuan publikasi atau kesetaraan kesulitan. **Indikator 3 menunggu instruksi berikutnya.**
'''
    (DEST/'README.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':run()
