"""Authorized batch: academic evidence for indicators 4–5 (100 entries).

Manual solutions are checked with exact arithmetic, enumerated divisors/events,
calendar offsets, and source data tables. No source, bank, or generator writes.
"""
import csv
import json
import re
from collections import Counter
from datetime import date,timedelta
from fractions import Fraction as F
from math import gcd,lcm,prod
from pathlib import Path
from audit_original_questions import ROOT,OUT,digest,read,write,flatten
from audit_indicator_01_academic import issue

DEST=OUT/'stage-05-academic-indicators-04-05'

P4={
(1,1):('FFTF','KPK(12,18)=36; 6 ialah FPB,12 bukan kelipatan18,72 kelipatan bersama tetapi bukan yang paling cepat. Hanya C.'),
(1,2):('FFTF','FPB(60,45,30)=15; isi per kantong4 buku,3 pensil,2 penghapus. A5/B10 bukan maksimum; D30 tidak membagi45; C benar.'),
(1,3):('FFTF','N=360. Opsi A48 tidak membagi120; B360 dan D180 lebih besar dari120; C120 membagi360 dan120. Hanya C faktor persekutuan dalam opsi.'),
(1,4):('FTFF','KPK(6,8,12)=24 menit, bersama kedua 07.24. 07.12 bukan kelipatan8;07.36 bukan kelipatan8;07.48 adalah bersama ketiga, bukan kedua.'),
(1,5):('TFFF','FPB(48,36)=12 piring; isi4 donat dan3 lemper. A benar; B tertukar; C ialah jumlah piring yang disalahgunakan sebagai isi; D tidak memberi jumlah piring sama untuk48 dan36.'),
(1,6):('TFTT','24=2^3*3; FPB(18,24,36)=6 bukan12; KPK=72. A,C,D benar, B salah.'),
(1,7):('TFFT','KPK(15,20)=60; FPB=5 bukan10. Dalam (0,180] pertemuan60,120,180:3 kali, bukan2. A,D benar.'),
(1,8):('TTFT','FPB(84,56,28)=28=2²*7; per kantong3 buku,2 pensil,1 penggaris. A/B/D benar; C3 pensil salah.'),
(1,9):('TFT','FPB(72,90)=18; per piring4 bolu dan5 lapis. a benar,b5 bolu salah,c selisih1 benar.'),
(1,10):('TTF','FPB(45,75)=15 cm; potongan3 dan5, total8 bukan10. a,b benar;c salah.'),
(2,1):('FFTF','KPK(8,10)=40 hari.18 hanya jumlah interval;20 bukan kelipatan8;80 bukan pertemuan paling cepat. C benar.'),
(2,2):('FTFF','FPB(48,36,24)=12 paket dengan isi4,3,2 kg bilangan bulat. A6 bukan maksimum; C24 tidak membagi36; D36 tidak membagi48/24. B benar.'),
(2,3):('TFFF','KPK(12,15,20)=60 menit.07.00+60=08.00, A.08.20/08.30 bukan pertemuan bersama,09.00 bersama ketiga.'),
(2,4):('FTFF','180=2²*3²*5 dengan prima2,3,5; jumlah faktor positif(2+1)(2+1)(1+1)=18 bukan6. Analisis I memakai komposit10 sehingga bukan faktorisasi prima. B benar; D salah karena180 habis dibagi10.'),
(2,5):('FFTF','A=360, B=756; FPB36=2²*3². Opsi A7560 ialah KPK; B72 tidak membagi756; D12 bukan terbesar. Hanya C.'),
(2,6):('TFTT','60=2²*3*5; FPB(24,36,60)=12 bukan24; KPK360. A,C,D benar.'),
(2,7):('TTFT','KPK(18,24)=72, FPB6; pertemuan (0,180] pada72 dan144, dua kali. A,B,D benar; C3 kali salah.'),
(2,8):('FTTF','FPB(72,96)=24; tiap ruangan3 tetikus,4 papan ketik. A12 bukan maksimum; B/C benar; D tertukar.'),
(2,9):('TFT','FPB(54,72)=18; isi3 apel,4 jeruk,total7. a,c benar;b3 jeruk salah.'),
(2,10):('TTF','FPB(60,90)=30 cm; potongan2 dan3,total5. Rasio3:2 bukan2:1. a,b benar;c salah.'),
(3,1):('FFTF','KPK(12,15,20)=60 hari; 1 Maret+60 hari=30 April. I29April dan II1Mei salah tanggal; IV30hari bukan interval bersama. C benar.'),
(3,2):('FTFF','P=360,Q=84,FPB12=2²*3. A72 dan D180 tidak membagi84; C2520 ialah KPK. B benar.'),
(3,3):('TFFF','FPB(90,105)=15; isi6 buku,7 pulpen. A benar; B/D mendukung30 wadah dengan3,5 pulpen yang tidak utuh; C salah karena justru pulpen lebih banyak.'),
(3,4):('FFTF','FPB(120,150)=30; tiap kelompok4 laki-laki,5 perempuan. A15 bukan maksimum; B mengambil jumlah perempuan; D60 tidak membagi150. C benar.'),
(3,5):('FTFF','X72,Y240,KPK720=2^4*3²*5. A24 ialah FPB; C360 bukan kelipatan240; D17280 bukan terkecil. B benar.'),
(3,6):('TFTT','72=2³*3²; FPB(36,48,72)=12 bukan24; KPK144. A,C,D benar.'),
(3,7):('TTFT','KPK(20,30)=60 dan FPB10. Pertemuan (0,240] pada60,120,180,240:4 kali. A,B,D benar; C5 menghitung awal secara keliru.'),
(3,8):('FTTF','FPB(80,112)=16; isi5 pak dan7 botol. A32 tidak membagi80; B/C benar; D tertukar.'),
(3,9):('TFT','FPB(60,84)=12; isi5 mikroskop,7 kaca,total12. a,c benar;b5 kaca salah.'),
(3,10):('TTF','FPB(75,105)=15 cm; potongan5 dan7,total12. Rasio7:5 bukan2:1. a,b benar;c salah.'),
(4,1):('FTFF','KPK(6,8,12)=24 hari. Kejadian pertama pada2Mei; ketiga setelah48 hari=19Juni. I baru kejadian kedua; III salah tanggal; IV memakai3interval untuk kejadian ketiga. B benar.'),
(4,2):('FFTF','M1080,N252;FPB36=2²*3². A216 tidak membagi252; B7560 bukan pembagi; D12 bukan terbesar. C benar.'),
(4,3):('TFFF','FPB(120,144)=24; isi5 modul dan6 pena. Proposal48 memerlukan2,5 modul, tidak utuh. A benar; B/D merestui proposal tak layak; C salah karena pena justru lebih banyak.'),
(4,4):('FTFF','Jika komposisi per kelompok wajib identik: FPB(96,120)=24; isi4 laki-laki,5 perempuan,selisih1. B benar pada syarat itu;12 bukan maksimum dan48 tidak membagi120. Stem belum menyatakan keseragaman komposisi yang diperlukan.'),
(4,5):('FFTF','KPK(12,15,20)=60, sehingga C sesuai hitungan KPK. Namun stem meminta ubin lantai,jumlah terkecil,dan ukuran tiga dimensi sekaligus, lalu membahas rusuk kubus dari balok yang tidak ditetapkan. C hanya kondisional pada model balok searah12×15×20 cm. Header300/900 tidak cocok dan300 bukan kuadrat sempurna.'),
(4,6):('TFTT','90=2*3²*5;FPB(45,60,90)=15 bukan30;KPK180. A,C,D benar.'),
(4,7):('TTFT','KPK(16,24)=48 menit; kedua08.48. Dalam (0,120] bunyi bersama pada48 dan96 menit, dua kali, bukan3. A,B,D benar.'),
(4,8):('FTTF','Dengan komposisi sama: FPB(108,135)=27; opsiII isi4 agenda,5 pulpen. OpsiI9 wadah berisi12 agenda,15 pulpen bukan12. B/C benar secara kondisional; stem belum mewajibkan komposisi identik untuk klaim maksimum.'),
(4,9):('TFT','FPB(84,126)=42; isi2 minuman,3 makanan,total5. a,c benar;b2 makanan salah.'),
(4,10):('TTF','FPB(90,120)=30 cm; potongan3 dan4,total7.4:3 bukan2:1. a,b benar;c salah; spasi9 0 pada opsi merujuk90 dari stimulus.'),
(5,1):('FTFF','KPK(10,15,20)=60 detik.30 bukan kelipatan20, sehingga I salah. B benar; C memakai penjumlahan,bukan hasil kali dan bukan KPK; D memakai3000 bukan alasan interval60.'),
(5,2):('TFFF','P144,Q1080,FPB72=2³*3². EvaluasiA benar. B/D memakai faktor pangkat maksimum untukKPK2160; C penambahan5 tidak mempertahankan FPB.'),
(5,3):('TFFF','FPB(144,180)=36; alternatifI isi4 buku,5 pulpen,utuh. II memerlukan2,5 pulpen sehingga tak layak. A benar; B/D mengabaikan keterbagian180; C tak punya alasan menolak komposisi4:5.'),
(5,4):('FFTF','Pada pembagian sama: FPB(108,135)=27, isi4 laki-laki,5 perempuan. ReguA9 kelompok layak tapi bukan maksimum; C54 tidak utuh. OpsiC menunjuk ReguB yang benar pada syarat ini; stem belum menyatakan pembagian komposisi sama.'),
(5,5):('FTFT','Interval awalKPK(14,21)=42 hari; usulanI KPK(7,14)=14;usulanII KPK(12,18)=36. II lebih panjang dariI (B), tetapi lebih pendek dari awal sehingga lebih buruk terhadap tujuan memperpanjang baseline (D). Acuan perbandingan belum tegas; A salah karenaKPK7,14 bukan28,C salah.'),
(5,6):('TFTT','54=2*3³;FPB(54,72,90)=18 bukan36;KPK1080. A,C,D benar.'),
(5,7):('TTFT','KPK(24,36)=72;FPB12. Dalam (0,300] pertemuan72,144,216,288:4 kali. A,B,D benar; C5 salah.'),
(5,8):('FTTF','Pada pembagian komposisi sama: FPB(96,144)=48, isi2 tabung dan3 pipet. A24 bukan maksimum,B/C benar,D tertukar. Tanpa syarat komposisi sama, klaim maksimum tidak terjamin.'),
(5,9):('TFT','Pada pembagian komposisi sama: FPB(120,150)=30, isi4 susu,5 biskuit,total9. a,c benar dan b4 biskuit salah pada model itu. Stem belum mewajibkan keseragaman yang mendasari nilai maksimum.'),
(5,10):('TTF','FPB(105,135)=15 cm; potongan7 dan9,total16.9:7 bukan2:1. a,b benar;c salah.'),
}

P5={
(1,1):('FTFF','18:13,5=36:27=4:3. Hanya B; rasio3:2,5:4,8:5 tidak ekuivalen.'),
(1,2):('FFTF','45m=4500cm;gambar4500/300=15cm. C;9/12/18 bukan15.'),
(1,3):('FTFF','Durasi18menit. Jika bak awal kosong tanpa aliran keluar, volume masuk450liter dan debit rata-rata450/18=25liter/menit,B. Tanpa volume awal, debit=(450−Vawal)/18 tidak tunggal.'),
(1,4):('FFTF','27000/6=4500 per buku;7buku31500. B juga langsung menyatakan paket31500 di stimulus. Hanya C; soal tetap dapat dijawab meskipun harga yang ditanya sudah diberikan.'),
(1,5):('FTFF','Tabel80/2=120/3=200/5=40km/liter;240/40=6liter. Hanya B;5,5/6,5/7 tidak sesuai model proporsional.'),
(1,6):('TFTT','36:24=3:2 dan45:30=3:2 bukan4:3; keduanya ekuivalen. Cerita/total24/60=2/5. A,C,D benar.'),
(1,7):('TTFT','Skala250: panjang12*250/100=30m,lebar8*250/100=20m. Luas gambar96cm² bukan100;luas asli600m². A,B,D benar.'),
(1,8):('FTTF','A90/(3/2)=60km/jam;B110/2=55km/jam. B/C benar,A50salah,Dlebihcepat salah karena55<60.'),
(1,9):('TFT','P35000/(5/2)=14000 per liter;Q52000/4=13000 bukan13500. Q lebih murah; a,c benar,b salah.'),
(1,10):('TTF','Tabel18/3=30/5=48/8=6unit/jam.10jam→60,72unit→12jam bukan14. a,b benar;c salah pada model laju konstan.'),
(2,1):('FTFF','22,5:13,5=45:27=5:3. B benar; A3:2,C9:5,D15:8 tidak ekuivalen.'),
(2,2):('FFTF','72m=7200cm;gambar7200/400=18cm. Hanya C.'),
(2,3):('FTFF','Durasi08.10–08.30=20menit. Jika bak awal kosong dan tidak bocor, debit rata-rata360/20=18liter/menit,B. Jika sudah ada air, kapasitas360bukan seluruh volume yang masuk.'),
(2,4):('FTFF','X36000/8=4500 per botol;Y51600/12=4300, hemat200 per botol. AnalisisII/B benar untuk harga per unit; A membandingkan paket berbeda isi,C salah karenaIIbenar,Dtidak ekuivalen.'),
(2,5):('FFTF','Tabel120/3=160/4=240/6=40km/liter.7,5liter→300km, C;270/280/320 tidak sesuai.'),
(2,6):('TFTT','48:32=3:2 dan60:40=3:2 bukan4:3;ekuivalen. Fiksi/total48/80=3/5. A,C,D benar.'),
(2,7):('TTFT','Skala200:15cm→30m,10cm→20m;luas600m² bukan300. A,B,D benar.'),
(2,8):('FTTF','P100/2=50km/jam,Q120/(5/2)=48. B/C benar; A45salah,Dlebihcepat salah.'),
(2,9):('TFT','A70000/5=14000/kg;B135000/10=13500/kg bukan14000. B lebih murah500/kg; a,c benar.'),
(2,10):('TTF','Tabel24/2=60/5=96/8=12lembar/jam.6jam→72;120lembar→10jam bukan12. a,b benar;c salah pada model konstan.'),
(3,1):('FTFF','P12,5:37,5=1:3;Q15:45=1:3. Komponen dan konsentrat sama jenisnya menghasilkan konsentrasi ekuivalen. II/B benar;I salah rasioQ,III salah menyatakan tak ekuivalen,IV membandingkan volume absolut.'),
(3,2):('FFTF','Panjang asli6*500=3000cm;denah baru12cm berarti12/3000=1/250. C;1/1000,1/500,1/125 berbeda.'),
(3,3):('FTFF','Jika kedua akuarium diisi dari kosong tanpa aliran lain:P300/15=20,Q480/20=24liter/menit,selisih4,B. Tanpa volume awal yang pasti, kedua laju tidak dapat ditentukan dari kapasitas saja.'),
(3,4):('FFTF','TokoA48000/10=4800 per buku;B67500/15=4500. B lebih murah300; C satu-satunya opsi sesuai. A/B salah selisih500;Dtidak sama.'),
(3,5):('FTFF','Tabel160/4=280/7=400/10=40lembar/menit.6menit→240lembar,B;200/260/300 tidak cocok. Baris640 memerlukan n=16menit.'),
(3,6):('TFTT','42:28=3:2 dan54:36=3:2; B4:3 salah, Cekuivalen benar. Biru/total42/70=3/5. A,C,D benar.'),
(3,7):('TTFT','Skala300:10cm→30m,6cm→18m;luas540m² bukan180. A,B,D benar.'),
(3,8):('FTTF','X150/(5/2)=60km/jam;Y180/3=60. B/C benar;A50salah;Dlebihcepat salah karena rata-rata sama.'),
(3,9):('TFT','M28000/40=700 per lembar;N39000/60=650 bukan700. N lebih murah50; a,c benar,b salah.'),
(3,10):('TTF','Tabel21/3=35/5=56/8=7stel/jam.10jam→70;84stel→12jam bukan14. a,b benar;c salah pada model konstan.'),
(4,1):('FTFF','A15:45=1:3 danB20:60=1:3: proporsi sama untuk sirup sejenis. II/B benar;I salah rasioB,III salah menyatakan tidak ekuivalen,IV hanya melihat jumlah sirup.'),
(4,2):('FFTF','Panjang asli5*600=3000cm;denah baru10cm berarti1/300. C;1/1200,1/600,1/150 salah.'),
(4,3):('FTFF','Jika kedua kolam diisi dari kosong tanpa aliran lain:I360/18=20,II600/24=25liter/menit,selisih5,B. Volume awal tidak disebutkan sehingga hasil ini bersyarat.'),
(4,4):('FTFF','Maju42000/12=3500 per pulpen;Jaya66000/20=3300,hemat200 per unit. B benar;A hanya membandingkan harga paket, CmenolakB yang benar,Dekuivalen salah.'),
(4,5):('FFTF','Tabel16/2=40/5=56/7=8stel/jam.72stel→9jam,III/C. I keliru menambah3jam untuk16stel (seharusnya2);II memberi t8 dengan satuan laju9 yang tidak sesuai tabel;D menggabungkan keduanya salah.'),
(4,6):('TFTT','36:24=3:2 dan54:36=3:2 bukan4:3. Ekuivalen;merah/total36/60=3/5. A,C,D benar.'),
(4,7):('TTFT','Skala250:14cm→35m,8cm→20m;luas700m² bukan280. A,B,D benar.'),
(4,8):('FTTF','K120/2=60km/jam;L135/(9/4)=60km/jam. B/C benar;A50salah,Dlebihcepat salah.'),
(4,9):('TFT','X21000/30=700 per lembar;Y32500/50=650 bukan700. Y lebih murah50; a,c benar.'),
(4,10):('TTF','Tabel27/3=45/5=72/8=9lembar/jam.10jam→90;108lembar→12jam bukan14. a,b benar;c salah pada model konstan.'),
(5,1):('FTFF','X16:48=1:3 danY25:75=1:3, jadi komposisi sama untuk sirup sejenis. B benar;A/D hanya membandingkan volume satu komponen,C salah karenaBbenar.'),
(5,2):('FFTF','Lebar asli6*400=2400cm;denah baru12cm berarti1/200. III/C benar;I1/800 danII1/400 salah,D menggabungkan keduanya salah.'),
(5,3):('FTFF','Jika bak awal kosong tanpa aliran lain:A400/16=25,B720/24=30liter/menit,selisih5,Blebihbesar. OpsiB benar dalam model itu. Kapasitas dan durasi saja tidak menentukan debit bila volume awal tidak diketahui.'),
(5,4):('FTFF','Alfa60000/15=4000 per buku;Beta92500/25=3700,hemat300. EvaluasiY berada pada opsiB. C menyatakan kedua evaluasi salah sehingga tidak benar;A/X membandingkan paket,Dhargaekuivalen salah.'),
(5,5):('FTFF','Tabel24/3=48/6=64/8=8lembar/jam.88lembar→11jam. II/B benar;I10 danIII12 tidak sesuai laju8,D menggabungkan keduanya salah.'),
(5,6):('TFTT','45:30=3:2 dan60:40=3:2 bukan4:3. Ekuivalen;merah/total45/75=3/5. A,C,D benar.'),
(5,7):('TTFT','Skala300:12cm→36m,8cm→24m;luas864m² bukan288. A,B,D benar.'),
(5,8):('FTTF','P140/2=70km/jam;Q175/(5/2)=70. B/C benar;A60salah;Dlebihcepat salah karena rata-rata sama.'),
(5,9):('TFT','A36000/20=1800 per kotak;B59500/35=1700 bukan1800. B lebih murah100; a,c benar.'),
(5,10):('TTF','Tabel18/2=45/5=63/7=9eksemplar/jam.10jam→90;117eksemplar→13jam bukan15. a,b benar;c salah pada model konstan.'),
}


def exact_evidence():
    """Check discrete math independently by enumerating admissible cases."""
    number_sets=[(12,18),(60,45,30),(6,8,12),(48,36),(18,24,36),(15,20),(84,56,28),(72,90),(45,75),
        (8,10),(48,36,24),(12,15,20),(360,756),(24,36,60),(18,24),(72,96),(54,72),(60,90),
        (360,84),(90,105),(120,150),(72,240),(36,48,72),(20,30),(80,112),(60,84),(75,105),
        (1080,252),(120,144),(96,120),(45,60,90),(16,24),(108,135),(84,126),(90,120),
        (10,15,20),(144,1080),(144,180),(14,21),(7,14),(54,72,90),(24,36),(96,144),(105,135)]
    divisors=[]
    for ns in number_sets:
        ds=[d for d in range(1,min(ns)+1) if all(n%d==0 for n in ns)]
        g=max(ds);m=lcm(*ns)
        assert g==gcd(*ns) and all(m%n==0 for n in ns)
        assert next(k for k in range(max(ns),m+1,max(ns)) if all(k%n==0 for n in ns))==m
        divisors.append(dict(numbers=list(ns),common_divisors=ds,gcd=g,lcm=m,status='PASS'))
    events=[]
    for a,b,duration in [(15,20,180),(18,24,180),(20,30,240),(16,24,120),(24,36,300)]:
        hits=[t for t in range(1,duration+1) if t%a==0 and t%b==0]
        assert len(hits)==duration//lcm(a,b)
        events.append(dict(periods=[a,b],duration=duration,interval='(0,duration]',events=hits,status='PASS'))
    dates=[dict(start='2026-03-01',elapsed_days=60,expected='2026-04-30'),
           dict(start='2026-05-02',elapsed_days=48,expected='2026-06-19')]
    for r in dates:
        assert (date.fromisoformat(r['start'])+timedelta(days=r['elapsed_days'])).isoformat()==r['expected']
        r['status']='PASS';r['note']='Tahun2026 hanya saksi kalender; rentang Maret–Juni tidak bergantung tahun kabisat.'
    rate_checks={
        'ratios':F(18)/F('13.5')==F(4,3) and F('22.5')/F('13.5')==F(5,3) and F('12.5')/F('37.5')==F(15,45)==F(16,48)==F(25,75)==F(1,3),
        'map_distances':F(4500,300)==15 and F(7200,400)==18,
        'map_rescaling':F(12,6*500)==F(1,250) and F(10,5*600)==F(1,300) and F(12,6*400)==F(1,200),
        'unit_prices':F(27000,6)==F(31500,7)==4500 and F(36000,8)==4500 and F(51600,12)==4300 and F(48000,10)-F(67500,15)==300 and F(42000,12)-F(66000,20)==200 and F(60000,15)-F(92500,25)==300,
        'unit_price_categories':[(F(a,b),F(c,d)) for a,b,c,d in [(35000,F('2.5'),52000,4),(70000,5,135000,10),(28000,40,39000,60),(21000,30,32500,50),(36000,20,59500,35)]]==[(14000,13000),(14000,13500),(700,650),(700,650),(1800,1700)],
        'scale_areas':all(F(p*s,100)*F(w*s,100)==area for p,w,s,area in [(12,8,250,600),(15,10,200,600),(10,6,300,540),(14,8,250,700),(12,8,300,864)]),
        'speed_pairs':[(F(a)/F(t),F(b)/F(u)) for a,t,b,u in [(90,'1.5',110,2),(100,2,120,'2.5'),(150,'2.5',180,3),(120,2,135,'2.25'),(140,2,175,'2.5')]]==[(60,55),(50,48),(60,60),(60,60),(70,70)],
        'empty_tank_rates':F(450,18)==25 and F(360,20)==18 and F(480,20)-F(300,15)==4 and F(600,24)-F(360,18)==5 and F(720,24)-F(400,16)==5,
        'nonempty_tank_counterexample':F(450-90,18)==20 and F(360-60,20)==15,
        'calendar_clock':7*60+lcm(6,8,12)==7*60+24 and 7*60+lcm(12,15,20)==8*60,
        'cube_conditional':lcm(12,15,20)==60 and 60**3//(12*15*20)==60 and 300%60==0 and 17**2<300<18**2,
    }
    assert all(rate_checks.values())
    return dict(divisors_and_multiples=divisors,event_enumerations=events,calendar_checks=dates,exact_calculation_checks=rate_checks)


def run():
    stage1=OUT/'stage-01-extraction-01-05/validation.json'
    entries=[q for q in read(stage1)['entries'] if q['indicator'] in (4,5)]
    assert len(entries)==100 and set(P4)==set(P5)=={(l,n) for l in range(1,6) for n in range(1,11)}
    evidence=exact_evidence()
    # Each issue is a proposal, never an authorized source correction.
    findings={
    (4,3,1):[issue('stem/editorial','MINOR','Pembuka menyebut empat jadwal tetapi hanya mencantumkan tiga ruangan dan tiga periode.','Ubah empat jadwal menjadi tiga jadwal; perhitungan60hari tetap.')],
    (4,4,1):[issue('stem/editorial','MINOR','Pembuka menyebut tiga siswa tetapi menyajikan empat analisis.','Samakan jumlah siswa/analisis; perhitungan19Juni tetap.')],
    (4,4,5):[issue('stem/key/explanation','CRITICAL','Stem meminta jumlah ubin lantai berukuran12×15×20cm lalu membahas rusuk kubus dari balok. Header kunci menyebut ArgumenII,300 sebagai nilai terkecil dan kuadratsempurna, padahal KPK60 dan300 bukan kuadratsempurna. Pembahasan melompat ke model balok yang tidak ditetapkan.','Kurikulum menetapkan satu konteks/model dan besaran yang ditanya. Jika model balok searah dipilih, tulis asumsi itu; panjang rusuk60cm dan jumlahbalok60 adalah dua besaran berbeda. Hapus header300/900 setelah koreksi disetujui.')],
    (4,4,7):[issue('explanation/unit','MINOR','Frekuensi menyebut pada detik ke48 dan menit ke96; periode48menit, sehingga kejadian pertama setelah awal juga menit48.','Ganti detik ke48 menjadi menit ke48; jumlahdua kejadian dan kunciABD tetap.')],
    (4,4,8):[issue('additional_notes/reasoning','MINOR','Catatan menyimpulkan9bukanmaksimum karena9masihbisadibagi3. Membagi banyakwadah dengan3 justru menguranginya, bukan membuktikan27wadah.','Tulis banyakwadah dapat dinaikkan9×3=27 karena108/27 dan135/27 tetapbulat; jangan memakai keterbagian angka9 saja sebagai bukti FPB.')],
    (4,4,10):[issue('option c/typography','MINOR','Teks opsi menulis panjangtali9 0cm, sementara stimulus90cm.','Satukan menjadi90cm agar tidak menyerupai hasilkali9dan0; jawaban kategoriTTF tetap pada konteks90cm.')],
    (4,5,4):[issue('key/description','MINOR','Huruf kunciC menunjuk LaporanReguB, tetapi caption memakai EvaluasiIII yang tidak didefinisikan di stimulus. Rujukannya bisa disalahartikan sebagai regu ketiga. Tidak disimpulkan sebagai kesalahan huruf.','Perjelas caption menjadi C.LaporanReguB setelah syarat pembagian sama dijelaskan.')],
    (4,5,5):[issue('stem/criterion','IMPORTANT','Awal42hari; usulanI14hari,usulanII36hari. B benar jika hanya dibandingIvsII, sedangkan D benar jika tujuannya memperpanjang rentang dibandingjadwalawal. Keduanya memperpendek jadwalawal.','Tegaskan apakah memilih usulan terbaik diantaraI/II atau wajib lebihlama dari42hari. Pada kriteria kedua,takadausulan yangmemenuhi; jangan memilih acuan otomatis.')],
    (4,5,7):[issue('additional_notes/precision','MINOR','Catatan menulis300÷72=4,16, padahal nilai eksak25/6=4,1666…;4,16 hanya potongan desimal.','Tulis300/72=25/6≈4,1667 lalu ambilfloor4. Tidak perlu pembulatan untuk menghitung kejadian.')],
    (5,1,2):[issue('stem/editorial','MINOR','Kata denah diulang tiga kali berturut-turut.','Hapus pengulangan; jawaban15cm tetap.')],
    (5,1,4):[issue('stem/assessment design','MINOR','Harga paketB31500 sudah diberikan lalu ditanyakan kembali untuk7buku. Soal dapat dijawab tanpa menghitung rasio.','Jika ingin mengukur harga perunit, jangan berikan hargaB langsung; perubahan memerlukan review Kurikulum. JawabanC tetap benar.')],
    (5,3,3):[issue('explanation/missing value','MINOR','Baris selisih tertulis24liter/menit−20liter/menit=liter/menit tanpa angka4; paragraf opsi berikutnya baru memberi4.','Lengkapi angka4 pada persamaan; pisahkan pula volume masuk dari kapasitas bila bak tidakdinyatakan kosong.')],
    (5,4,10):[issue('additional_notes/distractor','MINOR','Catatan mengaitkan jawaban14jam dengan108÷8, tetapi hasilnya13,5jam, bukan14 tanpa aturan pembulatan tambahan.','Hapus atribusi atau jelaskan kesalahan pembulatan yang dimaksud sebagai kesalahan siswa; jangan menambahkan pembulatan ke solusi benar. Waktu benar12jam.')],
    (5,5,4):[issue('key/letter','CRITICAL','EvaluasiY benar berdasarkan4000−3700=300 perbuku dan berada pada opsiB. HeaderC.EvaluasiY bertentangan dengan opsiC.Keduaevaluasisalah.','Usulkan kunciB.EvaluasiY. Pembahasan harga perunit sudahbenar; sumber belum diubah.')],
    }
    uniform={(4,4),(4,8),(5,4),(5,8),(5,9)}
    for l,n in uniform:
        findings.setdefault((4,l,n),[]).append(issue('stem/equal composition','IMPORTANT',
            'Jumlah kelompok maksimum memakai FPB hanya jika setiap kelompok/kotak harus mempunyai komposisi masing-masing jenis yang sama. Stem tidak menyatakan syarat itu. Tanpa syarat sama, pembagian lebih banyak bisa dibuat dengan isi berbeda.',
            'Tambahkan syarat setiap kelompok/kotak berisi jumlah masing-masing jenis yang sama, semua barang/orang utuh dan terbagi habis. Kunci yang dihitung dengan FPB bersifat kondisional sampai klarifikasi.'))
    for l in range(1,6):
        findings.setdefault((5,l,3),[]).append(issue('stem/initial volume','IMPORTANT',
            'Yang diketahui kapasitas wadah dan waktu sampai penuh; volume air awal dan aliran keluar tidak disebutkan. Kapasitas bukan otomatis volume yang masuk. Debit kapasitas/waktu hanya sah jika pengisian dari kosong tanpa kehilangan air.',
            'Nyatakan bak/kolam/akuarium mula-mula kosong,tanpa kebocoran/aliran lain; untuk debit tetap,tulis konstan,atau minta debit rata-rata. Jangan mengasumsikan kondisi itu sebagai fakta sumber.'))
    rows=[]
    for q in entries:
        i,l,n=q['indicator'],q['level'],q['source_number'];pos=(i,l,n)
        vector,proof=(P4 if i==4 else P5)[(l,n)]
        assert len(vector)==len(q['options'])
        validity='VALID';answer='CORRECT';explanation='CORRECT';conditional=False
        if i==4 and (l,n) in uniform or i==5 and n==3:
            validity=answer=explanation='UNCERTAIN';conditional=True
        if pos==(4,4,5):validity='INVALID';answer='INCORRECT';explanation='UNCERTAIN';conditional=True
        if pos==(4,5,5):validity=answer=explanation='UNCERTAIN';conditional=True
        if pos in ((4,4,7),(4,4,8),(4,5,7),(5,3,3),(5,4,10)):explanation='INCORRECT'
        if pos==(5,5,4):answer='INCORRECT'
        ids=[str(j+1) if q['format']=='KATEGORI' else chr(65+j) for j,t in enumerate(vector) if t=='T']
        if answer=='CORRECT':assert ids==q['parsed_key'],(pos,ids,q['parsed_key'])
        if validity=='VALID' and q['format']=='PG':assert vector.count('T')==1,pos
        issues=findings.get(pos,[])
        recommendation=('HOLD_FOR_SOURCE_REVISION' if validity=='INVALID' else 'HOLD_FOR_CLARIFICATION' if validity=='UNCERTAIN' else
            'REVISE_KEY' if answer=='INCORRECT' else 'REVISE_EXPLANATION' if explanation=='INCORRECT' else 'NO_BLOCKING_ACADEMIC_FINDING')
        data_tables=[]
        for t in q['tables']:
            if len(t['rows'][0])==2:
                data_tables.append(dict(table_id=t['id'],rows=[['\n'.join(p['text'] for p in flatten(c['blocks'])) for c in row] for row in t['rows']]))
        if data_tables:
            expected_rate={(1,5):40,(1,10):6,(2,5):40,(2,10):12,(3,5):40,(3,10):7,
                           (4,5):8,(4,10):9,(5,5):8,(5,10):9}[(l,n)]
            for table in data_tables:
                checks=[]
                for row in table['rows'][1:]:
                    values=[cell.replace('$','').strip().replace(',','.') for cell in row]
                    if all(re.fullmatch(r'\d+(?:\.\d+)?',cell) for cell in values):
                        rate=F(values[1])/F(values[0]);assert rate==expected_rate,(pos,values,rate)
                        checks.append(dict(input=values[0],output=values[1],rate_exact=str(rate),status='PASS'))
                assert len(checks)>=3,pos
                table['independent_ratio_checks']=checks
        rows.append(dict(audit_id=q['audit_id'],indicator=i,level=l,source_number=n,source=q['source'],format=q['format'],
            validity=validity,answer_status=answer,explanation_status=explanation,independent_solution=proof,
            option_evaluation_basis='CONDITIONAL_ON_ASSUMPTIONS_OR_CRITERION_IN_SOLUTION' if conditional else 'SOURCE_STIMULUS',
            option_evaluations=[dict(label=chr(97+j) if q['format']=='KATEGORI' else chr(65+j),text=text,
                result='TRUE' if t=='T' else 'FALSE') for j,(text,t) in enumerate(zip(q['options'],vector))],
            independently_correct_ids=None if conditional else ids,conditionally_proven_ids=ids if conditional else [],
            declared_key_texts=q['declared_key_texts'],parsed_source_key=q['parsed_key'],data_tables=data_tables,
            explanation_review='Seluruh faktorisasi,operasi,satuan,tanggal,alasan opsi dan catatan sumber dibandingkan dengan solusi independen. Status terpisah membedakan hitungan benar dari asumsi/label yang belum sah.',
            issues=issues,recommendation=recommendation,approval_status='NOT_CURRICULUM_APPROVED',generator_matching_status='NOT_EVALUATED_IN_THIS_STAGE'))
    # All 10 source data tables have been read, not inferred from category keys.
    assert sum(len(r['data_tables']) for r in rows)==10
    baseline=read(OUT/'protected-inputs.json')['sha256'];assert all(digest(ROOT/p)==h for p,h in baseline.items())
    def counts(rs):return dict(entries=len(rs),validity=dict(Counter(r['validity'] for r in rs)),
        answer_status=dict(Counter(r['answer_status'] for r in rs)),explanation_status=dict(Counter(r['explanation_status'] for r in rs)),
        recommendations=dict(Counter(r['recommendation'] for r in rs)))
    summary=dict(scope='Indikator4–5 saja,100soal',review_date='2026-10-20',**counts(rows),
        by_indicator={str(i):counts([r for r in rows if r['indicator']==i]) for i in (4,5)},
        source_sha256=read(stage1)['summary']['source_sha256'],stage1_evidence_sha256=digest(stage1),script_sha256=digest(Path(__file__)),
        protected_files_checked=len(baseline),protected_hashes_unchanged=True,
        next_batch_policy='Mulai bagian berikutnya lima indikator per audit; bagian setelah ini6–10 menunggu instruksi.')
    DEST.mkdir(parents=True,exist_ok=True)
    write(DEST/'audit.json',dict(summary=summary,exact_evidence=evidence,
        methodology=dict(independence='Seluruh100stimulus dan semua opsi diselesaikan sebelum membaca kunci/pembahasan. Tidak memakai review sementara lama,bank aktif,atau generator sebagai oracle.',
            assumptions='Tidak menyamakan tanpa sisa dengan komposisi identik,atau kapasitas dengan volume masuk. Hasil bersyarat dipisahkan dari jawaban yang terbukti dari teks.',
            units='Meter–centimeter,skala kuadrat untukluas,pecahan jam,debit rata-rata,periode waktu diperiksa.',
            categories='Benar/Salah per pernyataan;tidak membuat rubrik skor.',
            tables='Sepuluh tabel data dipertahankan dan dibaca langsung meskipun proyeksi stem kategori tidak memuat nilai tabel.',
            scope='Tidak mengaudit indikator6–10,memperbaiki sumber,atau mencocokkan generator.'),entries=rows))
    fields=['audit_id','indicator','level','source_number','format','validity','answer_status','explanation_status','recommendation','independent_solution','issues']
    with (DEST/'entries.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(r[k],ensure_ascii=False) if k=='issues' else r[k] for k in fields})
    report=['# Tahap 5 — Audit akademik indikator 4–5','',
        'Cakupan disetujui: **100 soal indikator 4–5 saja**. Bagian selanjutnya akan mencakup lima indikator per audit, sesuai instruksi terbaru; indikator 6–10 menunggu instruksi.',
        '', '| Indikator | Entri | Tanpa temuan yang menghalangi | Perlu tindak lanjut |','|---|---:|---:|---:|']
    for i in (4,5):
        c=summary['by_indicator'][str(i)];clean=c['recommendations'].get('NO_BLOCKING_ACADEMIC_FINDING',0)
        report.append(f'| {i} | 50 | {clean} | {50-clean} |')
    report+=['','Seluruh opsi/pernyataan, kunci, pembahasan, dan catatan diperiksa. Sepuluh tabel data dibaca langsung dan disertakan dalam JSON. Jawaban bersyarat diberi label khusus; kunci yang benar secara hitung tidak otomatis mengesahkan asumsi yang hilang.','',
        '| Komponen (100 soal) | Benar/valid | Bermasalah | Belum dapat dipastikan |','|---|---:|---:|---:|']
    for field,label,good,bad in [('validity','Soal','VALID','INVALID'),('answer_status','Kunci','CORRECT','INCORRECT'),('explanation_status','Pembahasan','CORRECT','INCORRECT')]:
        c=summary[field];report.append(f"| {label} | {c.get(good,0)} | {c.get(bad,0)} | {c.get('UNCERTAIN',0)} |")
    report+=['','Hitungan per komponen berdiri sendiri. Ini pemeriksaan akademik, bukan persetujuan publikasi atau kesetaraan kesulitan. Semua usulan berikut **PROPOSED, belum diterapkan/disetujui Kurikulum**.','',
        '| Lokasi | Temuan utama dan usulan |','|---|---|',
        '| I4 L4Q5 | Konteks ubin/lantai bercampur balok/kubus; header tentang 300/900 rusak. KPK 60 benar tetapi model geometri dan besaran yang ditanya harus ditetapkan ulang. Panjang rusuk dan jumlah balok jangan disamakan. |',
        '| I4 L5Q5 | Jadwal awal 42 hari, usulan I 14 hari, usulan II 36 hari. B benar terhadap I, D benar terhadap jadwal awal 42 hari. Tegaskan acuan: kedua usulan tidak memperpanjang jadwal awal. |',
        '| I4 L4Q4,L4Q8,L5Q4,L5Q8,L5Q9 | Maksimum memakai FPB memerlukan komposisi setiap kelompok/kotak yang sama. Syarat ini belum tertulis; tambahkan sebelum mengesahkan kunci. |',
        '| I4 L5Q4 | Huruf C menunjuk Regu B, tetapi caption memakai Evaluasi III yang tidak didefinisikan. Perjelas menjadi C. Laporan Regu B, setelah syarat pembagian sama diperjelas. Ini bukan kesalahan huruf yang sudah terbukti. |',
        '| I5 L5Q4 | Harga Alfa Rp4.000/buku, Beta Rp3.700/buku, hemat Rp300. Evaluasi Y berada pada **opsi B**, bukan header C. Pembahasan harga benar; usulan kunci B. |',
        '| I5 L1Q3, L2Q3, L3Q3, L4Q3, L5Q3 | Kapasitas/waktu hanya memberi debit bila pengisian dari kosong tanpa aliran lain. Volume awal belum disebutkan. Jawaban kondisional masing-masing 25, 18, selisih 4, selisih 5, dan Keran B 30 > Keran A 25 liter/menit. Tambahkan kondisi pengisian; bukan koreksi angka otomatis. |',
        '| I4 L4Q7 | Pembahasan menyebut detik 48, seharusnya menit 48. Kunci ABD tetap. |',
        '| I4 L4Q8 | Catatan tentang membagi 9 dengan 3 tidak membuktikan jumlah wadah maksimum 27. Jelaskan kenaikan 9×3 dan keterbagian kedua barang. |',
        '| I4 L5Q7 | Catatan 300/72=4,16 seharusnya 25/6≈4,1667; jumlah kejadian mengambil bilangan bulat ke bawah (4), bukan pembulatan terdekat. |',
        '| I5 L3Q3 | Angka 4 hilang pada baris selisih 24−20; tercantum benar pada alasan opsi berikutnya. Lengkapi persamaan. |',
        '| I5 L4Q10 | Catatan 108/8 menghasilkan 13,5 jam, bukan 14 tanpa pembulatan tambahan. Waktu benar 108/9=12 jam. |',
        '', 'Catatan minor lain: jumlah jadwal/siswa tidak konsisten pada I4L3Q1/I4L4Q1; spasi pada 90 cm di I4L4Q10; pengulangan kata denah pada I5L1Q2; I5L1Q4 sudah memberikan harga Rp31.500 yang ditanyakan sehingga tidak mengharuskan perhitungan rasio. Detail bukti dan usulan per soal tersedia pada keluaran.',
        '', 'Asumsi ideal yang belum tertulis dibedakan dari kesalahan hitung. Misalnya, bak 450 liter yang sudah berisi 90 liter hanya menerima 360 liter selama 18 menit: debit 20 liter/menit, bukan 25. Pembagian 96 laki-laki dan 120 perempuan juga bisa menjadi 96 kelompok campuran tidak identik, sehingga 24 bukan maksimum tanpa syarat keseragaman.',
        '', '[JSON lengkap dan bukti eksak](audit.json) · [CSV 100 soal](entries.csv). Verifikasi meliputi 100 posisi unik, penilaian semua opsi, kecocokan kunci yang dinyatakan benar, PG valid satu jawaban, enumerasi pembagi/kelipatan dan kejadian, kalender, rasio, satuan, dan sepuluh tabel data.',
        '', f'Seluruh {len(baseline)} hash sumber/bank/config/stok/layanan tetap sama. Tidak ada perubahan API, database, bank aktif, generator, atau pemetaan runtime. Reproduksi: `python variant_gen/tests/audit_indicators_04_05_academic.py`.',
        '', '**Berhenti di indikator 5. Bagian berikutnya: indikator 6–10, menunggu instruksi.**','']
    (DEST/'README.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':run()
