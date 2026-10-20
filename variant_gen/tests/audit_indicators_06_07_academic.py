"""Offline source-bound academic evidence. Run from repository root with Python 3.

Only reads original DOCX/extraction; never reads old reviews or generated banks.
The authored solutions below are independent calculations, not copied answer keys.
"""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from audit_original_questions import ROOT, source_entries, flatten

FOLDER = ROOT / 'docs/sources/incoming/2026-10-19-indikator-6-10'
OUT = ROOT / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/part-06-07.json'
REVIEWS = {}


def pg(i, l, q, proof, actual, expected, options, unit=''):
    assert actual == expected, (i, l, q, actual, expected)
    vals = [F(v) for v in options]
    REVIEWS[i, l, q] = dict(independent_solution=proof, calculation_witness=str(actual),
        truths=['TRUE' if v == actual else 'FALSE' for v in vals],
        reasons=[f'Nilai opsi {v}{unit}; hasil stimulus {actual}{unit}; ' + ('sama.' if v == actual else 'berbeda.') for v in vals],
        explanation_review=proof)


def mc(i, l, q, proof, pattern, reasons):
    assert len(pattern) == len(reasons)
    REVIEWS[i, l, q] = dict(independent_solution=proof,
        truths=[{'T':'TRUE', 'F':'FALSE', '?':'UNCERTAIN'}[s] for s in pattern],
        reasons=reasons, explanation_review=proof)


def issue(k, component, evidence, impact, proposal, explanation_status=None, validity=None):
    r = REVIEWS[k]
    r.setdefault('issues', []).append(dict(component=component, evidence=evidence,
        impact=impact, proposal=proposal))
    if explanation_status: r['explanation_status'] = explanation_status
    if validity: r['validity'] = validity


# INDICATOR 6 / LEVEL 1. Units and every intermediate quantity stated explicitly.
pg(6,1,1, 'Faktor 60/24=5/2. Tepung=300(5/2)=750 g; gula=150(5/2)=375 g; selisih=375 g. Setara (300-150)60/24.', F(60,24)*(300-150),375,[300,350,375,450],' g')
pg(6,1,2, 'Jarak=15(20/60)=5 km; waktu tersedia=12/60=1/5 jam; kecepatan minimum=5/(1/5)=25 km/jam.', F(15)*F(20,60)/F(12,60),25,[20,F(45,2),25,28],' km/jam')
pg(6,1,3, 'Beban=18(8)=144 orang-hari; selesai=6(8)=48; sisa=96; sisa waktu=18-6-4=8 hari; total pekerja=96/8=12; tambahan=12-8=4.', F(18*8-6*8,18-6-4)-8,4,[2,4,6,12],' orang')
pg(6,1,4, 'Panjang=6(250)/100=15 m; lebar=4(250)/100=10 m; pagar=2(15+10)=50 m.', F(2*(6+4)*250,100),50,[25,50,75,100],' m')
pg(6,1,5, 'Luas naik 360/120=3 kali; laju kerja konstan memberi durasi 6 jam; konsumsi 1.5 liter/2 jam, jadi 6(1.5/2)=4.5 liter.', F(3,2)*F(360,120),F(9,2),[3,4,F(9,2),6],' liter')
mc(6,1,6, 'Uji bentuk y=kx versus xy=k: harga=tarif×pensil; vt=jarak tetap; anggota×hari=stok/(porsi harian); cat=luas/daya tutup.', 'FTTF', ['Dengan tarif pensil tetap, biaya/pensil konstan, bukan hasil kali.', 'vt=s tetap untuk rute yang sama.', 'Dengan konsumsi harian sama dan tetap, anggota×hari tetap.', 'Dengan daya tutup tetap, cat/luas tetap.'])
mc(6,1,7, 'Laju A=180/12=15 lembar/menit; B=200/15=40/3. B selama30 menit=400; waktu300 lembar A=20 menit, B=45/2=22.5 menit; 15>40/3.', 'TTTF', ['180/12=15.', '30(40/3)=400.', '20<45/2 menit.', '40/3<15; B justru lebih lambat.'])
mc(6,1,8, 'Stok=40(6)=240 kue; hadir=40-8=32; jatah=240/32=15/2=7.5 kue; tambahan=7.5-6=1.5 kue. Pembagian merata dimungkinkan dengan membagi kue menjadi bagian.', 'TTTF', ['40×6=240.', 'Siswa×jatah=240 tetap.', '240/32=15/2.', '15/2-6=3/2, bukan2.'])
mc(6,1,9, 'Data asli tabel I (2,10),(4,20),(6,30): y/x=5 untuk ketiganya. Tabel II (2,24),(4,12),(8,6): xy=48 untuk ketiganya; pada x12, y=48/12=4.', 'TTF', ['10/2=20/4=30/6=5.', '2×24=4×12=8×6=48.', '48/12=4, bukan3.'])
mc(6,1,10, 'Jarak=60×3=180 km; kecepatan untuk2.5 jam=180/(5/2)=72 km/jam. Pulang-pergi360 km membutuhkan360/12=30 liter; satu arah15 liter.', 'TTF', ['60×3=180.', '180/(5/2)=72.', '360/12=30, bukan15.'])

# LEVEL 2
pg(6,2,1, '300 g=3/10 kg; faktor28/12=7/3. Jeruk=(3/2)(7/3)=7/2 kg; gula=(3/10)(7/3)=7/10 kg; selisih=14/5=2.8 kg.', F(28,12)*(F(3,2)-F(3,10)),F(14,5),[F(21,10),F(5,2),F(14,5),F(16,5)],' kg')
pg(6,2,2, 'Jarak=12(45/60)=9 km; waktu baru45-15=30 menit=1/2 jam; v=9/(1/2)=18 km/jam. Persamaan12×45=v×30 memakai satuan menit yang sama pada kedua sisi.', F(12*45,45-15),18,[15,16,18,20],' km/jam')
pg(6,2,3, 'Beban=5×6=30 siswa-jam; 2 jam pertama10 siswa-jam; sisa20; tersisa3 siswa; tambahan20/3 jam=6j40m; total2+20/3=26/3 jam=8j40m.', 2+F(30-10,3),F(26,3),[F(22,3),8,F(26,3),F(28,3)],' jam')
pg(6,2,4, 'Laju satu printer=180/(2×15)=6 halaman/menit; tiap printer selama25 menit=150 halaman; 600/150=4 printer. Tiga printer450<600.', F(600,25*6),4,[3,4,5,6],' printer minimum')
pg(6,2,5, 'Produktivitas=60/(4×5)=3 kg/(siswa·hari); kebutuhan=90/(3×3)=10 siswa.', F(90,3*3),10,[8,9,10,12],' siswa')
mc(6,2,6, 'Dengan modul seragam kertas/modul tetap; untuk rute1 km vt=1; untuk pagar tetap siswa×waktu tetap bila produktivitas sama; honor=tarif harian×hari.', 'FTTF', ['Kertas bertambah sebanding jumlah modul seragam.', 'v×t=1 km.', 'Pada model produktivitas sama, pekerja×waktu=pekerjaan tetap.', 'Honor/hari tetap, hubungan senilai.'])
mc(6,2,7, 'Efisiensi Anggrek120/15=8 km/l; Mawar150/20=15/2 km/l. Untuk360 km: Anggrek45 l; Mawar48 l; selisih3 l. Anggrek lebih hemat sebab8>7.5.', 'TFTT', ['360/8=45 liter untuk jarak total360 km.', '7.5<8 km/l; Mawar lebih boros.', '48-45=3 liter.', '120/15=8 dan150/20=7.5.'])
mc(6,2,8, 'Stok awal8×15=120 porsi-hari; terpakai3×8=24; sisa96=8×12. Siswa baru12; sisa hari96/12=8. Total durasi3+8=11, lebih cepat15-11=4 hari; tanpa pendatang tetap15.', 'TTTF', ['15-3=12 hari untuk8 siswa.', '96/12=8 hari sejak bergabung.', '15-(3+8)=4 hari.', 'Stok awal8×15, jadi15 hari bukan18.'])
mc(6,2,9, 'Laju gabungan3 siswa=18/45=2/5 bibit/menit. Untuk30 bibit=30/(2/5)=75 menit. Beban18 bibit=3×45=135 siswa-menit; untuk15 menit135/15=9 siswa. Bibit dan waktu berbanding lurus pada pekerja tetap.', 'TTF', ['30×45/18=75 menit.', '3×45/15=9 siswa.', 't=(45/18)N, bukan t=k/N.'])
mc(6,2,10, 'Biaya per kulkas-hari=180000/(3×20)=3000 rupiah. Untuk4×30 kulkas-hari=120, biaya360000. Pada durasi tetap biaya=3000×hari×kulkas.', 'TTF', ['180000/60=3000.', '4×30×3000=360000.', 'Biaya/kulkas tetap; hubungan senilai.'])

# LEVEL 3
pg(6,3,1, 'Dengan kecepatan B=1.25 kali kecepatan A: A=360/(3×15)=8 lembar/menit/unit; B=10; keluaran2×10×20=400; selisih400-360=40 lembar. Jika frasa "1.25 kali lebih cepat" berarti peningkatan125%, B=18 dan selisih360 lembar; redaksi harus menyebut pengali.', F(2*20)*F(5,4)*8-360,40,[20,40,60,80],' lembar')
pg(6,3,2, 'Bus A240/10=24 liter; B240/8=30 liter; selisih30-24=6 liter. Waktu A4 jam dan B3 jam tidak diperlukan untuk konsumsi per jarak.', F(240,8)-F(240,10),6,[4,6,8,10],' liter')
pg(6,3,3, 'Produktivitas12/(4×3)=1 panel/siswa/hari; kebutuhan20/(1×2)=10 siswa; tambahan10-4=6 siswa.', F(20,2)-4,6,[4,6,8,10],' siswa tambahan')
pg(6,3,4, 'Durasi normal9/18=1/2 jam=30 menit; 3 km awal3/18=1/6 jam=10 menit; berhenti10 menit; sisa waktu10 menit=1/6 jam; sisa jarak6 km; v=6/(1/6)=36 km/jam.', F(9-3)/(F(9,18)-F(3,18)-F(10,60)),36,[24,28,32,36],' km/jam')
pg(6,3,5, 'Beban8×10=80 pekerja-hari; selesai8×4=32; sisa48; waktu10-4-2=4 hari; total12 pekerja; tambahan12-8=4.', F(80-32,10-4-2)-8,4,[2,4,6,8],' orang')
mc(6,3,6, 'K=4s memberi K/s=4. vt=jarak tetap. Baris×kursi/baris=kapasitas tetap. L=s² memberi L/s=s berubah, jadi bukan perbandingan senilai.', 'TTTF', ['K/s=4 konstan.', 'v×t konstan.', 'Hasil kali baris dan kursi/baris tetap.', 'L/s=s; misalnya sisi2 dan4 luas4 dan16, rasio bukan tetap.'])
mc(6,3,7, 'Elang6×10=60 porsi-hari; Sriti4×15=60. Gabungan120/10=12 hari. Jika anggota datang awal hari3: sudah2 hari, sisa60-12=48, untuk8 siswa6 hari. Jika datang setelah 3 hari: sisa42, untuk8 siswa21/4=5.25 hari. Tidak satu pun menghasilkan tepat5 hari. Porsi harian kedua regu dinyatakan sama.', 'TTFF', ['60=60 porsi-hari.', '120/10=12 hari.', 'Awal hari3 memberi6 hari; setelah 3 hari memberi21/4 hari; keduanya bukan5.', 'Porsi harian sama menurut stimulus, bukan dua kali.'])
mc(6,3,8, 'Ukuran sebenarnya28×16 m; rasio7:4; keliling2(28+16)=88 m. Rasio luas1:400²=1:160000. Skala1:200 menggandakan kedua sisi gambar14×8 cm, luas112 dibanding28, faktor4.', 'TTFT', ['28:16=7:4.', '2(28+16)=88.', 'Rasio luas1:160000, bukan1:400.', '(400/200)²=4.'])
mc(6,3,9, 'Vendor Y=90000t, rasio biaya/t tetap; X=200000+50000t, biaya/t=200000/t+50000 berubah. Pada5 jam X450000 danY450000, sama.', 'TFF', ['Y/t=90000 tetap.', 'X mempunyai biaya tetap; X/t berubah.', '200000+5×50000=5×90000=450000.'])
mc(6,3,10, 'Beban2 gazebo=5×6=30 pekerja-hari, satu gazebo15. Empat gazebo60, untuk6 hari10 pekerja. Produktivitas1/15 gazebo/pekerja/hari. Tiga gazebo45 pekerja-hari, dengan6 pekerja45/6=7.5 hari.', 'TTT', ['4×15/6=10.', '1/(30/2)=1/15.', '3×15/6=15/2 hari.'])

# LEVEL 4
pg(6,4,1, 'Berangkat3j30m=7/2 jam; jarak60×7/2=210 km. Pulang210/45=14/3 jam=4j40m. Selisih14/3-7/2=7/6 jam=70 menit, bukan40.', (F(210,45)-F(7,2))*60,70,[30,40,50,70],' menit')
mc(6,4,2, 'Dari120 porsi/6 hari hanya diketahui konsumsi kelompok20 porsi/hari, bukan20 orang. Misalkan porsi/orang/hari=r>0: awalN=20/r; sesudah10 orang datang, kebutuhan20+10r; sponsor20, penyusutan bersih10r. Sisa setelah2 hari80 porsi; durasi total2+80/(10r)=2+8/r hari. r=1 memberi10 hari (tidak ada opsi); Dengan jumlah awal orang bulat6,10,11,15, nilai r=10/3,2,20/11,4/3 memberi durasi4.4,6,6.4,8 hari, sehingga habis pada hari5,6,7,8. Waktu pasokan harian juga perlu dijelaskan untuk saat stok nol.', '????', ['Awal6 orang,r=10/3 memberi durasi4.4 hari: habis hari5; r tidak ditetapkan.', 'Hari6 mungkin bila r=2; r tidak ditetapkan.', 'Awal11 orang,r=20/11 memberi durasi6.4 hari: habis hari7; r tidak ditetapkan.', 'Hari8 mungkin bila r=4/3; r tidak ditetapkan.'])
pg(6,4,3, 'Laju480/(12×8)=5 potong/mesin/jam. Target900/10=90 potong/jam; total mesin90/5=18; tambahan18-12=6.', F(900,10*5)-12,6,[6,8,18,24],' unit tambahan')
pg(6,4,4, 'Dengan pembelian pada awal hari6 dan penjualan setelah hari9: stok600 ayam-hari; hari1–5 habis200, sisa400; hari6–9 habis50×4=200, sisa200; setelahnya30 ayam, waktu200/30=20/3 hari. Total9+20/3=47/3=15⅔ hari=15 hari16 jam. Stok habis selama hari16, bukan bertahan16 hari penuh.', 9+F(200,30),F(47,3),[13,14,16,18],' hari durasi')
mc(6,4,5, 'X tiba=07:00+180/60=10:00; Y tiba=07:15+180/75=09:39. X unggul60×1/4=15 km, laju relatif15 km/jam, tersusul1 jam setelah07:15 yaitu08:15, posisi75 km. Saat09:39, X sudah(53/20)×60=159 km, tersisa21 km.', 'FTFF', ['Posisi susul75 km, bukan45.', '07:15+1 jam=08:15.', 'Y09:39 lebih awal daripadaX10:00.', 'X pada159 km, sisa21 bukan30.'])
mc(6,4,6, 'Skala500 memberi A sisi20 m, keliling80 m, luas400 m²; B30×15 m, luas450 m². Keliling petaA16 cm danB18 cm, rasio8:9; nyata80:90=8:9.', 'TFTT', ['4×20=80 m.', '30×15=450, bukan900.', '16:18=80:90=8:9.', '20²=400 m².'])
mc(6,4,7, 'P per unit=1500/(3×4)=125 brosur/jam; Q=1200/(2×3)=200. SatuP+Q=325/jam. DuaP+duaQ=650/jam, selama4 jam2600 brosur.', 'FTFT', ['125<200; P lebih lambat.', '1200/6=200.', '125+200=325, bukan350.', '4(2×125+2×200)=2600.'])
mc(6,4,8, 'Misalkan dA,dB,dC jumlah hari kerja tiap minggu. HasilA=e×6×8×dA=240, maka e=5/dA unit/jam-orang. X=240dB/dA; jam-pekerjaA48dA danB48dB; 300=e×Y×10×dC sehinggaY=6dA/dC. Hanya bila jumlah hari kerja mingguan sama didapat X240, jam-pekerja sama,Y6,D salah. Efisiensi konstan saja tidak menetapkan dA=dB=dC.', '????', ['X=240dB/dA, bernilai240 bila dB=dA.', '48dA=48dB hanya bila dA=dB.', 'Y=6dA/dC, bernilai6 bila dC=dA.', 'Jumlah pekerja lebih banyak tidak cukup menentukan keluaran; X>240 hanya bila dB>dA, bukan semata karena8>6.'])
mc(6,4,9, 'Alpha total200+800=1000 ml, fraksi sirup1/5=20%; Beta total300+900=1200 ml, fraksi1/4=25%. Untuk2 liter Beta, sirup2000/4=500 ml. Dengan sirup yang sama, Beta lebih pekat.', 'TFT', ['200/1000=1/5.', '20%<25%; air saja tidak menentukan konsentrasi.', '2000×1/4=500 ml.'])
mc(6,4,10, 'Beban360 pekerja-hari; selesai120; sisa240; waktu30-10-5=15 hari. Perlu240/15=16 pekerja, tambahan4; tambahan3 menghasilkan15×15=225<240. Tanpa tambahan, faktor jam20/15=4/3; kenaikan tepat1/3=33⅓%, sedangkan33.3%=333/1000 kurang1/3000 dari kebutuhan, kekurangan kapasitas0.06 pekerja-hari.', 'TFF', ['360-120=240.', '15×15=225<240; perlu tambahan4.', '33.3% bukan tepat33⅓%; 12×15×1.333=239.94<240.'])

# LEVEL 5
pg(6,5,1, 'Stok awal60×14=840 keluarga-hari; 4 hari terpakai240, sisa600. Tambahan50% dari600=300; sisa baru900. Keluarga75, sisa waktu900/75=12 hari; total4+12=16 hari.', 4+F((840-240)*3,2*75),16,[16,18,19,21],' hari')
pg(6,5,2, 'Laju1200/(8×15)=10 bibit/relawan/hari; 3 hari selesai450; sisa750; relawan12 memberi120 bibit/hari; sisa750/120=25/4=6.25 hari; tambahan terhadap5 hari rencana=5/4=1.25 hari. OpsiB danC sama nilainya. Konversi1.25 hari menjadi1 hari6 jam hanya benar untuk hari24 jam, belum ditentukan sebagai hari kerja.', F(750,120)-5,F(5,4),[1,F(5,4),F(5,4),2],' hari')
pg(6,5,3, 'LajuA1/6, B1/4, gabungan5/12 pekerjaan/jam; 1.5 jam selesai(3/2)(5/12)=5/8; sisa3/8; waktuB=(3/8)/(1/4)=3/2 jam; total3 jam. Tidak ada informasi percepatan B.', F(3,2)+(1-F(3,2)*(F(1,6)+F(1,4)))/F(1,4),3,[F(5,2),3,F(7,2),4],' jam')
mc(6,5,4, 'LajuX=120/(4×5)=6; Y=180/(6×4)=15/2 potong/orang/hari. Target300/4=75/hari. A5X=30/hari→120/4hari; B8Y=60→240; C4X+3Y=93/2→186; D2X+4Y=42→168. Semua kurang300. Jika pekerja tambahan tersedia,10Y memenuhi300 dengan10 pekerja; opsiB meminta8Y padahal kelompokY hanya6, juga belum diizinkan merekrut.', 'FFFF', ['5×6×4=120<300.', '8×7.5×4=240<300; kelompokY hanya6 orang.', '(4×6+3×7.5)×4=186<300.', '(2×6+4×7.5)×4=168<300.'])
mc(6,5,5, 'Rute1=24/40=3/5 jam=36 menit; Rute2=30/60=1/2 jam=30 menit; lebih cepat6 menit.', 'FTFF', ['Penghematan6, bukan3 menit.', '36-30=6 menit lebih cepat.', 'Rute2 lebih cepat6, bukan lambat3.', 'Rute2 lebih cepat6, bukan lambat6.'])
mc(6,5,6, 'A12×25000=300000 cm=3 km; B16×25000=400000 cm=4 km; beda1 km; rasio12:16=3:4 tetap; B pada4 km/jam=1 jam.', 'TTFT', ['300000/100000=3 km.', '4-3=1 km.', 'Rasio tetap3:4.', '4/4=1 jam.'])
mc(6,5,7, 'TarifH=150000/10=15000/m², lajuH5m²/jam. TarifC=250000/15=50000/3≈16666.67/m², lajuC15/2m²/jam. H30m²=450000; C45m² membutuhkan45/(15/2)=6 jam.', 'FTTF', ['15000<50000/3, Hemat lebih murah.', '15/2=7.5 m²/jam.', '30×15000=450000.', '45/(15/2)=6, bukan4 jam.'])
mc(6,5,8, 'Dengan laju konsumsi tiap ternak sama dan tetap, stok setara30×20=600 ternak-hari; Q600/40=15 hari; R600/12=50 ekor. Besar P dalam satuan porsi memerlukan porsi/ekor/hari; tanpa definisi1 porsi harian, P=600r porsi. D menyebut kesetaraan600 porsi-hari yang ambigu terhadap satuan.', 'TFT?', ['600/40=15 hari pada konsumsi sama.', 'Ternak×hari tetap: berbalik nilai.', '600/12=50 ekor pada konsumsi sama.', '600 adalah ternak-hari; P=600r porsi bila r porsi/ekor/hari. D benar hanya bila porsi-hari didefinisikan sebagai satu jatah harian ternak.'])
mc(6,5,9, 'Debit per kran60/(3×4)=5m³/jam. Y debit20, waktu90/20=9/2=4.5jam. X dua kran debit10, waktu60/10=6jam.', 'TFT', ['60/12=5.', '4.5>4 jam.', '60/(2×5)=6.'])
mc(6,5,10, 'Beban12×6=72 pekerja-hari; selesai4×6=24, proporsi1/3, pagar60m. Sisa beban48; waktu12-4-2=6 hari; perlu8 pekerja, tambahan minimum2. Tambahan3 cukup selesai dalam48/9=16/3 hari sesudah kembali, tetapi tidak diperlukan sebagai minimum; "dibutuhkan3" ambigu antara cukup dan perlu.', 'T?T', ['180×24/72=60m.', 'Minimum2; tambahan3 juga cukup lebih cepat. Benar bila berarti opsi cukup, salah bila berarti keharusan/minimum.', '12-4-2=6 hari.'])

# Source-specific findings; absence of a flag does not replace the authored proof above.
issue((6,1,2),'explanation','Paragraf60 hanya PEMBAHASAN;61–62 kosong.','Tidak ada langkah penyelesaian.','Isi jarak5 km dan kecepatan25 km/jam.',explanation_status='MISSING')
issue((6,1,7),'explanation','300/13,33=22,5 ditulis dengan tanda sama dengan.','300/(1333/100)=30000/1333, bukan45/2; penggunaan pembulatan sebagai nilai eksak.','Gunakan300/(40/3)=45/2 atau tanda≈.',explanation_status='INCORRECT')
issue((6,3,1),'stem','Kecepatan cetak1,25 kali lebih cepat.','Pengali1,25 versus peningkatan125% dapat ditafsir berbeda; hasil40 versus360.','Tulis kecepatan B=1,25 kali kecepatan A.',validity='UNCERTAIN')
issue((6,3,4),'explanation','Waktu berhenti menambal ban, sedangkan stimulus rantai putus.','Sebab berhenti tidak sesuai stimulus; durasi dan matematika tetap benar.','Ganti menambal ban menjadi memperbaiki rantai.',explanation_status='INCORRECT')
issue((6,3,7),'key','KunciA,B,C; C menyatakan sisa5 hari.','C salah pada awal hari3 maupun setelah 3 hari; himpunan benarA,B.','KunciA,B; jelaskan saat bergabung.',explanation_status='INCORRECT')
issue((6,3,7),'explanation','Sisa48 lalu diganti42;42/8=5 hari.','Beralih waktu2 ke3 hari tanpa dasar;42/8=21/4, bukan5.','Awal hari3: (60-6×2)/8=6 hari; setelah 3 hari:21/4 hari.')
issue((6,4,1),'key','KunciB40 menit; hitungan4j40m-3j30m=40menit.','Pengurangan salah; jawabanD70 menit.','Ubah kunciD; selisih70 menit.',explanation_status='INCORRECT')
issue((6,4,2),'stem','120 porsi untuk6hari;10 relawan baru; tidak ada porsi/orang/hari.','Durasi2+8/r tak tunggal; kunciC tak dapat dipastikan.','Tetapkan konsumsi/orang, saat pasokan; bila1porsi/orang/hari tambahkan opsi hari10.',validity='UNCERTAIN',explanation_status='INCORRECT')
issue((6,4,2),'explanation','120porsi/6hari=20orang; akhir2+8=10 lalu hari8 operasional tambahan; kunciC hari7.','Salah dimensi porsi/hari menjadiorang; mengganti acuan hari; hasil pun tak cocok kunci.','Gunakanr eksplisit; jika r1 total10hari, jangan ganti acuan.')
issue((6,4,4),'options','Opsi13,14,16,18hari; hasil durasi47/3hari.','Tidak ada opsi eksak; membulatkan ke16 tidak diminta.','Sediakan15⅔hari atau tanyakan pada hari keberapa stok habis.',validity='INVALID',explanation_status='INCORRECT')
issue((6,4,4),'explanation','200/30=6,67hari≈6hari16jam; lalu5+4+7=16.','Mengganti durasi20/3 dengan7 tanpa aturan pembulatan.','Total47/3hari; jika yang dimaksud nomor hari, nyatakan hari ke16.')
issue((6,4,8),'stem','Jam kerja/hari dibanding hasil/minggu; jumlah hari kerja tidak diberikan.','A,B,C bergantung kesamaan hari kerja tiap kondisi.','Tetapkan jumlah hari kerja mingguan sama.',validity='UNCERTAIN',explanation_status='INCORRECT')
issue((6,4,8),'explanation','240produk/minggu dibagi48jam-orang/hari=5unit/jam-orang.','Mengabaikan faktor hari/minggu; produktivitas aktual5/dA.','Gunakan240/(48dA); simpulkan rasio hanya setelah dA=dB=dC.')
issue((6,4,10),'key','C BENAR untuk kenaikan33,3%.','Nilai eksak33⅓%;33.3% sedikit kurang untuk tepat waktu.','Tulis33⅓% atau sekitar33,3% dengan toleransi eksplisit.',explanation_status='INCORRECT')
issue((6,5,1),'key','KunciB18hari; pembahasan menghasilkan16hari.','Kunci salah; opsiA sesuai stimulus.','Ubah kunciA.')
issue((6,5,2),'options','B1,25hari danC1,25hari(1hari6jam).','Dua opsi setara dalam PG; konversi jam juga memerlukan definisi hari.','Ganti salah satu distraktor; pertahankan1,25hari sebagai jawaban tunggal.',validity='INVALID')
issue((6,5,3),'key','KunciA2.5jam; sisa3/8÷1/4=1.5jam.','Total3jam, opsiB; percepatanB tidak ada dalam stimulus.','Ubah kunciB; hapus versi kontradiktif2.5jam.',explanation_status='INCORRECT')
issue((6,5,3),'explanation','1.5+1.5=3 lalu1.5+1=2.5 dengan dalihB mempercepat.','Memasukkan laju baru tanpa data; dua total saling bertentangan.','Pertahankan1.5+1.5=3jam.')
issue((6,5,4),'options','Keluaran4hariA120,B240,C186,D168; target300.','Tidak ada opsi memenuhi; D salah.','Tentukan ketersediaan pekerja tambahan; sediakan komposisi yang memenuhi300.',validity='INVALID',explanation_status='INCORRECT')
issue((6,5,4),'explanation','D2X+4Y diganti5Y+5X lalu10Y atau5X+6Y.','Menyebut beberapa versiD yang tidak ada pada opsi;5Y+5X hanya67.5/hari.','Jangan mengganti opsi dalam pembahasan; hitung keempat opsi asli.')
issue((6,5,7),'explanation','250000/15=Rp16.667/m².','50000/3 rupiah bukan16667 eksak, walau urutan tarif benar.','Gunakan≈Rp16.666,67/m².',explanation_status='INCORRECT')
issue((6,5,8),'units','P diberi satuan porsi tetapiD600porsi-hari tanpa konsumsi per ternak.','Nilai numerik P bergantung definisi porsi; kunciD bersyarat.','Definisikan satu porsi sebagai jatah harian satu ternak; pakai600jatah-harian.',validity='UNCERTAIN',explanation_status='UNCERTAIN')
issue((6,5,10),'option B','Dibutuhkan tambahan3 pekerja.','Minimum2;3 cukup tetapi bukan perlu; status bergantung makna dibutuhkan.','Tulis minimum tambahan3 (SALAH), atau tambahan3 cukup (BENAR).',validity='UNCERTAIN',explanation_status='UNCERTAIN')

# INDICATOR 7 / LEVEL 1
mc(7,1,1, 'Harga penggaris12000; total4x+12000=92000; 4x=80000; x=20000. Periksa 4×20000+12000=92000.', 'TFFF', ['Model danx20000 keduanya cocok.', 'Penggaris menambah biaya, bukan mengurangi; x26000 memberi116000 pada transaksi asli.', 'Empat pack harus4x, bukan x; x80000 memberi332000.', '4(x+12000) mengalikan penggaris empat kali; x11000 memberi56000 pada transaksi asli.'])
pg(7,1,2, 'Modelx+45000=3x-25000; tambah25000 dan kurangi x:70000=2x; x35000. Kedua ruas80000.', F(45000+25000,3-1),35000,[30000,35000,40000,45000],' rupiah')
pg(7,1,3, 'Keliling2[(3x-2)+(x+4)]=36;8x+4=36; x4. Panjang10m, lebar8m, luas80m², keliling36m.', (3*4-2)*(4+4),80,[68,72,80,96],' m²')
pg(7,1,4, '3(2x-3)=4(x+2);6x-9=4x+8;2x17; x17/2. Nilai2x+5=22. Substitusi ke pecahan memberi7/2 pada kedua sisi.', 2*F(17,2)+5,22,[17,19,22,24])
pg(7,1,5, 'Halaman n,n+1,n+2;3n+3=147; n48; urutan48,49,50; terbesar50.', F(147-3,3)+2,50,[48,49,50,51])
mc(7,1,6, 'PLSV harus satu variabel berderajat 1 dan tanda=. A3x+7=22→x5; B2p²-5=13→p²9 berderajat 2; C(1/2)y-4=2y+5→(-3/2)y9→y-6; D dua variabel a,b.', 'TFTF', ['Satu variabel x pangkat1; x5.', 'p² berderajat 2, bukan linear.', 'Satu variabel y pangkat1; y-6.', 'Ada dua variabel a danb.'])
mc(7,1,7, 'I2x+6=2x+6 identitas semua real. II3x-3=3x+5→-3=5 kontradiksi tanpa solusi. III4x-2=2x+8→2x10→x5 tunggal.', 'TTTF', ['I identik pada semua real.', 'II menuntut-3=5 yang mustahil.', 'III2x=10, koefisien2≠0, x5 tunggal.', 'II himpunan kosong; III{5}.'])
mc(7,1,8, 'Adikx, kakak3x; empat tahun nanti x+4+3x+4=32→4x24→x6. Kakak18; selisih18-6=12 tahun; jumlah mendatang10+22=32.', 'TTTF', ['Masing-masing umur bertambah4, total4x+8.', '4x=24→6.', '3×6=18.', '18-6=12 bukan10.'])
mc(7,1,9, 'Tiga karung masing-masingx ditambah5kg:3x+5=80;3x75; x25kg. Urutan invers kurangi5 lalu bagi3; substitusi3×25+5=80.', 'TTT', ['3x+5=80 sesuai3karung dan5kg sisa.', '(80-5)/3, operasi invers benar.', '75/3=25kg.'])
mc(7,1,10, 'A5(x-2)=3x+2x-10→5x-10=5x-10, semua real. B4(x+1)=4x+7→4=7, tanpa solusi. Padax0, ruasB4 dan7 berbeda.', 'TTF', ['Kedua ruas5x-10.', 'Selisih konstanta4-7=-3≠0.', 'Substitusix0 memberi4≠7.'])

# LEVEL 2
mc(7,2,1, 'Diskon sekali15000 atas5pack:5x-15000=110000;5x125000; x25000. Uji5×25000-15000=110000.', 'TFFF', ['Model5x-15000 danharga25000 cocok.', 'Diskon dikurangkan; x19000 pada transaksi asli memberi80000.', '5(x-15000) memberi diskon75000; x37000 pada transaksi asli170000.', 'Jumlahpack5 bukan1; x125000 pada transaksi asli610000.'])
mc(7,2,2, 'Sumber menulis2x+1/3=x+5/2 tanpa kurung. Pembacaan standar:2x+1/3=x+5/2→x=13/6→3x-10=-7/2, tanpa opsi. Jika maksud(2x+1)/3=(x+5)/2, baru2(2x+1)=3(x+5)→x13→nilai29. Kedua persamaan berbeda; pembahasan tidak boleh mengganti stimulus tanpa bukti.', 'FF?F', ['23 bukan-7/2 maupun29.', '26 bukan-7/2 maupun29.', '29 hanya benar pada versi pembilang berkurung, bukan teks literal.', '32 bukan-7/2 maupun29.'])
pg(7,2,3, '2[(4x-3)+(2x+1)]=44→12x-4=44→x4; p13m,l9m; luas117m²; keliling2(13+9)=44.', (4*4-3)*(2*4+1),117,[99,108,117,126],' m²')
mc(7,2,4, '3(2x-a)=6x+12→6x-3a=6x+12→-3a=12. a=-4 memberi identitas; setiap a≠-4 memberi kontradiksi. a4 adalah salah satu nilai sah, bukan keseluruhan himpunan.', 'FTTF', ['a=-4 memberi12=12, bukan kontradiksi.', 'a4 memberi-12=12; ini nilai yang memenuhi pertanyaan.', 'Himpunan lengkap semuaa≠-4 benar.', 'Ada banyak nilai, misalnyaa=0.'])
pg(7,2,5, 'Wakilw, ketuaw+2; tiga tahun lalu(w-3)+(w-1)=24→2w-4=24→w14. Ketua kini16, lima tahun nanti21; umur lalu11+13=24.', F(24+4,2)+2+5,21,[19,20,21,22],' tahun')
mc(7,2,6, 'A4x-5=2x+7→2x12→x6; Bx²+3x=10 berderajat 2; C(1/3)y+2=5 dikali3→y+6=15→y9; D3a+2b=12 dua variabel.', 'TFTF', ['x6 membuat19=19; satu variabellinear.', 'Pangkat tertinggi 2.', 'Mengalikan kedua ruas dengan3≠0 mempertahankan himpunan solusi.', 'a danb dua variabel.'])
mc(7,2,7, 'I4(x-2)=4x-8 identitas; II2(3x+1)=6x+5→2=5 kontradiksi; III5x-3=2x+9→3x12→x4.', 'TTTF', ['I4x-8=4x-8 semua real.', 'II6x+2=6x+5 mustahil.', 'III3x12→4.', 'I tak hingga, II kosong; bukan satu solusi positif.'])
mc(7,2,8, 'Nomor ganjiln,n+2,n+4;3n+6=135→3n129→n43; urutan43,45,47; beda4; jumlahujung90.', 'TTFT', ['3n+6=135.', '129/3=43 ganjil.', '47-43=4, bukan6.', '47+43=90.'])
mc(7,2,9, 'Tiga sapu dengan harga satuan x ditambah tempat sampah 22000, total 67000:3x+22000=67000;3x45000;x15000. Operasi invers: kurangi 22000 lalu bagi 3;3×15000+22000=67000.', 'TTT', ['3x+22000=67000.', '(67000-22000)/3.', '45000/3=15000.'])
mc(7,2,10, 'A2(2x+3)=4x+6→4x+6=4x+6, identitas. B3(x-2)=3x-4→3x-6=3x-4→-6=-4, kontradiksi. Padax2, B0=2 salah.', 'TTF', ['A kedua ruas identik.', 'B konstanta-6 dan-4 berbeda.', 'x2 memberi0≠2, bukan solusi.'])

# LEVEL 3
mc(7,3,1, 'DistributorA4x+15000=95000→x20000; B5x-10000=90000→x20000; selisihharga=0.', 'FFTF', ['Selisih0, bukan A lebih mahal 2000.', 'Selisih0, bukan B lebih mahal 2000.', '80000/4=100000/5=20000.', 'Selisih0, bukan B lebih murah 5000.'])
pg(7,3,2, '2(3x-4)=6x-8. Identitas6x-8=ax+b mengharuskana6,b-8. Jumlah6-8=-2.', 6-8,-2,[14,2,-2,-14])
mc(7,3,3, 'Teks3x-2/4=x+4/2 secara standar memberi2x=5/2→x5/4; langkah 1 Budi bukan transformasi persamaan itu. Jika versi(3x-2)/4=(x+4)/2, perkalian silang2(3x-2)=4(x+4) benar, langkah 2benar, langkah 3salah tanda:2x=16+4=20→x10. Pembahasan keliru menyebut langkah 1 sebagai mengalikan kedua ruas denganKPK4: kali4 seharusnya3x-2=2(x+4), sedangkan bentukBudi ekuivalen kali8.', 'FF?F', ['Pada teks literal  salah pertama langkah 1 tetapix5/4 bukan8; pada versi pecahan kesalahan langkah 3.', 'Langkah 2 distributif benar pada versi pecahan; x12 bukanhasil.', 'Langkah 3 danx10 benar hanya bila pembilangberkurung.', 'Langkah 4 mengikuti kesalahan sebelumnya; x5 bukanhasil kedua versi.'])
pg(7,3,4, 'Kelilingtaman2[(3x-5)+(x+1)]=8x-8; persegibasket4(x+3)=4x+12. Sama→4x20→x5; dimensitaman10×6m; luas60m².', (3*5-5)*(5+1),60,[48,54,60,72],' m²')
mc(7,3,5, '4(x+2)-2x=2(x+k)→2x+8=2x+2k→8=2k. k4 identitas; k≠4 kontradiksi. OpsiB k8 adalah contoh nilai memenuhi. D k≠8 memuatk4 yang tidak memenuhi  dan mengeluarkank8 yang memenuhi.', 'FTTF', ['k4 memberi8=8, identitas.', 'k8 memberi8=16, kontradiksi.', 'k≠4 tepat himpunan lengkap.', 'k4 memenuhiD tetapi bukan kontradiksi; k8 kontradiksi tetapi dikecualikan.'])
mc(7,3,6, 'Bentuk1:3x-7=2x+8→x15. Bentuk 2 tertulis 2x2+5=13 tanpa superskrip; tidak boleh memastikan2x² versus2×x×2. Bentuk 3 dua  variabel a,b. Bentuk 4 tertulis 21​(4x+6)=2x+3: jika21literal memberi82x=-123→x-3/2 tunggal; jika maksud1/2 memberiidentitas. Penjelasan memakai² dan½ yang tidak ada dalam stimulus asli.', 'T?F?', ['3x-7=2x+8→x15 tunggal.', 'Bergantung apakah2x2berarti2x²; XML hanya teksbiasa2x2.', '4a-3b=10 memiliki dua variabel.', 'Identitas bila koefisien½; literal 21 memberi x-3/2 tunggal.'])
mc(7,3,7, 'Andix; Budix10000lebihbanyak; Cicidua kali(2x+10000)=4x+20000. Total6x+30000=180000→x25000; Budi35000; Cici120000; jumlah180000.', 'TTTF', ['x+(x+10000)+(4x+20000)=6x+30000.', '150000/6=25000.', '25000+10000=35000.', '2(25000+35000)=120000,bukan100000.'])
mc(7,3,8, 'P:3x-6+4=2x+2+x-4→3x-2=3x-2 identitas. Q:5x+5-3x=2x+6→2x+5=2x+6→5=6 kontradiksi.', 'TTTT', ['Kedua ruasPmenjadi3x-2.', 'Pberlaku semua real.', 'Qmenjadi2x+5=2x+6.', '5=6mustahil, himpunan solusi kosong.'])
mc(7,3,9, 'Fiksi3x; nonfiksi2(x+5)=2x+10; total5x+10=110→x20. Total fiksi 3×20=60; biaya60×15000=900000.', 'TTT', ['3x+2(x+5)=5x+10.', '(110-10)/5=20.', '3×20×15000=900000.'])
mc(7,3,10, 'm(x-1)+2x=5x-3→(m-3)x=m-3. m3 memberi0x0 semua real; m2 memberi-x=-1→x1 tunggal. Bahkan untuk semua m≠3 solusi tunggalx1.', 'TFT', ['m3 kedua ruas5x-3 identik.', 'x0 salah satu dari tak hingga solusi, bukan satu-satunya.', 'm2 memberi-x=-1→1.'])

# LEVEL 4
mc(7,4,1, 'Biaya=120000+3000x=345000→3000x225000→x75buku. Uji120000+3000×75=345000.', 'FFTF', ['Modelmengalikanbiayatetap120000denganx, salahmeskihasil75disebut.', 'Tandabiayatetapmestiplus; x155memberi585000pada transaksi asli.', 'Modelbenar;225000/3000=75.', 'Modelbenartetapix115memberi465000,bukan345000.'])
pg(7,4,2, '80000+15000d=140000+10000d→5000d60000→d12. Keduanya Rp260000 setelah 12 hari.', F(140000-80000,15000-10000),12,[10,12,14,15],' hari')
pg(7,4,3, '2[(3x-4)+(x+2)]=44→8x-4=44→x6. Panjang14cm,lebar8cm;keliling44;luas112cm². KunciheaderD117bertentangandenganperhitungan dan revisi dalam teks C112.', (3*6-4)*(6+2),112,[96,105,112,117],' cm²')
mc(7,4,4, '2(3x-5)+4=6x-10+4=6x-6, identitasuntuk semua real. Budi benar. Andi hanya menyatakan persamaan memiliki penyelesaianx0, tidakmenyatakanhanya x0; klaimtersebutjugabenar. JikaAndi dimaksud mengklaimsolusi tunggal, barupendapatnyasalah; katahanyatidakadadistemulus.', 'T?FF', ['Identitas6x-6=6x-6mendukungBudi.', 'x0memangsolusi;benarsecaraliteral,tetapijikadimaksudsolusi tunggalbarusalah.', 'Semuarealmerupakansolusi, bukan kosong.', 'x1memenuhitapitidak tunggal; kedua pendapattidaksalah.'])
mc(7,4,5, 'A4(x+3)-2x=4x+12-2x=2x+12;B2(x+6)=2x+12. Selisih0untuk semua x, termasuksemua jumlah buku bulat nonnegatif.', 'FFFT', ['SelisihA-B=0jugapada x>5.', 'Konstanta keduanya 12.', 'Samapada semua x,bukan hanya x6.', 'Keduanya persis 2x+12.'])
mc(7,4,6, 'A3x-6+5=2x+9→x10;Bx²+4x-5=x²-3→4x2→x1/2;suku²dapatdikurangkankarenakedua ruasterdefinisiuntuk semua real. C(2x+6)/4=5→2x14→x7.Ddua variabel x,y.', 'TTTF', ['Alinear satu variabel setelah disederhanakan,x10.', 'Setelah mengurangi x²:4x-5=-3.', 'Penyebut konstan 4 tidak mengubah derajat;2x14.', 'Ddua variabel .'])
mc(7,4,7, '3(2x+4)-2x=6x+12-2x=4x+12.Persamaan4x+12=4x+7→12=7mustahil;tidak ada solusi.', 'FTFT', ['x5memberi32≠27;bukan solusi.', 'Distributifmemberi4x+12.', '12≠7,bukan identitas.', 'Kontradiksi 12=7,himpunan kosong.'])
mc(7,4,8, '2x+30000=4x-10000→2x40000→x20000.Rani=70000, Dion=70000, Sinta=3×20000+10000=70000.', 'TFTT', ['40000/2=20000.', 'Rani=Sinta=70000,bukanlebih kecil.', '2×20000+30000=70000.', 'Sinta=Dion=70000.'])
mc(7,4,9, '3b+2000=17000→3b15000→b5000. Enam buku membutuhkan 6×5000=30000,cukup pas.', 'TFT', ['3bukudan1penggaris2000memberi3b+2000.', 'Harga5000,bukan6000.', '6×5000=30000.'])
mc(7,4,10, 'I2(x+3)=2x+6identitas.II3x+5=3x-2→5=-2kontradiksi.III4x-8=0→x2tunggal;substitusix-2memberi-16≠0.', 'TTF', ['Isemua real.', 'II5≠-2tanpa solusi.', 'III hanya x=2; x-2bukan.'])

# LEVEL 5
mc(7,5,1, 'Skema A 3b+2×2000=22000→b6000.Skema B 5b-6000=24000→b6000.Kedua harga  dasarsama,selisih0.', 'FTFF', ['Selisih0,bukan1000.', '18000/3=30000/5=6000.', 'Selisih0,bukan2000.', 'Jumlah bukubukanpenentuharga dasar;hasilkeduanya6000.'])
mc(7,5,2, 'Regulerx,VIP2x+10000;3x+2(2x+10000)=160000→7x140000→x20000;VIP50000;selisih30000.Uji3×20000+2×50000=160000.', 'FFTF', ['Reguler20000,bukan25000.', 'VIP50000,bukan40000.', '2×20000+10000=50000.', '50000-20000=30000,bukan20000.'])
mc(7,5,3, 'Ruas kiri 4(x-1)+2=4x-2;ruas kanan 2(2x-1)=4x-2.Identitasuntuk semua real;mengeliminasi x menghasilkan 0=0,bukan0=4.', 'FFFT', ['Tidak diperoleh 0=4,tetapi0=0.', 'Hilangnya variabel disertai identitas konstanta, bukan kontradiksi.', 'x0salah satu solusi,bukan tunggal.', 'Keduanya menjadi 4x-2,semua real.'])
pg(7,5,4, 'Total M=15000n+20000=18000n-16000;36000=3000n→n12.M=15000×12+20000=200000;cekkondisi2:216000-16000=200000.', 15000*F(20000+16000,18000-15000)+20000,200000,[200000,180000,160000,120000],' rupiah')
mc(7,5,5, '2[(3x-2)+(x+4)]=36→8x+4=36→x4.Panjang10m,lebar8m,luas80m².KunciheaderC13×5hanya memenuhi keliling, tetapi tidak memenuhi  pasangan rumus p3x-2,lx+4bersama x yang sama.', 'TFFF', ['x4memberip10,l8.', '10×8=80,bukan96.', 'p=13 mengharuskan x=5,lebar9;bukan5;pasangan13×5takcocok.', '10≠8,bukanpersegi.'])
mc(7,5,6, 'i3x-5=2x+7→x12,linear; iix²-4=0berderajat 2; iii(x+4)/2=3→x2,linear; iv2x+y=10dua variabel .', 'TFTF', ['i daniii berderajat 1,satu variabel .', 'Pangkat 2 menggagalkan linear.', 'ivdua variabel x,y.', 'Pecahan dengan penyebut konstan 2 tetap linear.'])
mc(7,5,7, '2(3x-1)+5=6x-2+5=6x+3.Persamaan6x+3=6x+8→3=8mustahil;takhimpunan solusi.', 'FTFT', ['x3memberi21≠26.', 'Distributif6x-2+5=6x+3.', '3≠8,bukan identitas.', 'Kontradiksi 3=8.'])
mc(7,5,8, 'Harga inti dua formula 3x+15000dan5x-25000;sama→2x40000→x20000.Keduanya75000;dua kaus 150000.NamunopsiAaslitertulis"Nilai xxx ... 20.00020.00020.000",tidak menentukan numeral/variabel yangsah;semuaformuladiulangtiga kali dalam stimulus dan pembahasan.Opsi A tidak diganti secara diam-diam.', '?TFT', ['Benarhanyajika xxxdinormalisasimenjadixdanangkaulangmenjadi20000;teks aslimengalamikerusakan.', '3×20000+15000=75000.', 'Kedua harga 75000;B tidak lebih mahal.', '2×75000=150000.'])
mc(7,5,9, 'Persamaan 2n+18=50→n16.Jikanadalahsiswayangmasing-masingmeminjam2buku,merekameminjam2n32buku;makna18bukutambahanbelumdijelaskan.Total50hanyasahjika18adalahpinjamanoranglain.Jika4bukubaruuntuk2siswabarudengan18tetap,n18;kalau4bukudipinjamsiswalamajumlahsiswatidakbertambah.Stimulusbelummenetapkanmekanismeitu.', 'T??', ['Solusialjabar(50-18)/2=16pasti.', '32adalah2n;total50jika18merupakanpinjamanlain,namunmakna18tidakdijelaskan.', 'n18hanyajikatotal54dan18tetapsertaaturan2buku/siswaterusberlaku;4bukutidakotomatis2siswabaru.'])
mc(7,5,10, 'I5(x-2)=5x-10identitassemua real.II2x+7=2x-3→7=-3kontradiksi.III3x-12=0→x4tunggal,sehingga"tidakmemilikinilai"salah.', 'TTF', ['Keduanya persis 5x-10.', '7≠-3menolaksemua x.', 'x=4 memenuhi persamaan III.'])

# INDICATOR 7 findings: textual equations are never silently replaced by explanations.
issue((7,1,1),'explanation','4x=80.000⟹x=480.000​=20.000.','Teksmenyatakan480000=20000,bagianpecahanrusakdalamDOCXasli.','Tulisx=80000/4=20000.',explanation_status='INCORRECT')
issue((7,1,6),'explanation','OpsiC(1/2)y,tetapipembahasan menulis 21​y−4=2y+5.','Koefisien21bukan1/2;klasifikasilineartetapbenarnamunpersamaan berubah.','Tulis(1/2)y−4=2y+5secarautuh.',explanation_status='INCORRECT')
issue((7,1,9),'explanation','x=380−5​ danx=375​=25kg.','Pecahanhilang;375tidaksama25.','Gunakanx=(80-5)/3=75/3=25.',explanation_status='INCORRECT')
issue((7,2,2),'stem','Paragraf1415asli2x+1/3​=x+5/2​,XMLteksbiasa.','Literalx13/6memberinilai-7/2tanpaopsi;versi pembahasanx13memberi29.','Minta/nyatakanpersamaanyangdimaksud;gunakan(2x+1)/3=(x+5)/2jika29diinginkan.',validity='UNCERTAIN',explanation_status='UNCERTAIN')
issue((7,2,4),'options','B a=4 danC semuaa≠-4.','Keduanyamemenuhipertanyaan"nilai a yang memenuhi";Bcontohsahdi dalamC.','TanyakanhimpunansemuanilaiasecaralengkapataugantiB.',validity='INVALID')
issue((7,2,6),'explanation','C dijelaskansebagai31​y+2=5,opsi(1/3)y+2=5.','Pembahasan mengganti koefisien 1/3dengan31secara literal.','Tulis(1/3)y+2=5;kalikan3menjadiy+6=15.',explanation_status='INCORRECT')
issue((7,2,8),'notes','Modeln,n+1,n+2dikatakanmenghasilkandesimalyangmembingungkan.','Untuk jumlah 135, model itu justru memberi n=44 bulat; kesalahannya urutan 44,45,46 tidak semua ganjil.','Jelaskanbahwabilanganberurutanjarak1bukanganjilberurutanjarak2.')
issue((7,3,3),'stem','Paragraf1679:3x −2/4=x+4/2tanpakurung.','Literalx5/4berbedadarix10pembahasan;opsiCbersyaratversi pecahan.','Tulis(3x-2)/4=(x+4)/2denganpembilangjelas.',validity='UNCERTAIN',explanation_status='INCORRECT')
issue((7,3,3),'explanation','Langkah 1disebutmengalikan kedua ruas dengan KPK 4.','Bentuk 2(3x-2)=4(x+4)adalahkali dengan 8;kali dengan 4memberi3x-2=2(x+4).','Sebut perkalian  silangataukalikan 4 dengan bentuk yang tepat.')
issue((7,3,5),'options','B k=8 danC k≠4.','k=8 memenuhi kontradiksi;BdanCsamabenarmenurutpertanyaanliteral.','Tanyakanhimpunansemuanilaikatauganticontohk8.',validity='INVALID')
issue((7,3,6),'stem','Paragraf1746asli2x2+5=13dan1748asli21​(4x+6)=2x+3;XMLbukansuperskrip/pecahan.','BdanDbergantungperbaikannotasi;tidakbolehmenyalin²dan½daripembahasansebagaisumber.','Konfirmasikannotasi;gunakan2x²dan½bilaituversiyangdimaksud.',validity='UNCERTAIN',explanation_status='UNCERTAIN')
issue((7,4,3),'key','Header D=117; pembahasan menulis Jawaban benar C dan Kunci disesuaikan ke C.','Versi kunci bertentangan; hasil112 mendukung C.','Satukan kunci menjadi C; hapus teks penyuntingan.',validity='VALID')
issue((7,4,4),'stem','Andi menyatakan "memilikipenyelesaianx=0",tanpakatatunggal/hanya.','AndidanBudi benarsecaraliteral;penjelasanmenambahklaimhanya x0.','UbahAndimenjadi"satu-satunyapenyelesaianx=0"atausediakanopsikeduanya benar.',validity='UNCERTAIN',explanation_status='INCORRECT')
issue((7,5,5),'key','Header C=13m×5m; akhir pembahasan Revisi Kunci ke A=10m×8m.','Dua versi kunci; A yang memenuhi rumus pada x=4.','Satukan kunci ke A; hilangkan catatan revisi.',validity='VALID')
issue((7,5,8),'stem/options/explanation','Paragraf2282–2296memuatformulaulangtigakali,PDF,opsiAxxxdan20.00020.00020.000.','NotasimatematikadanopsiArusak;himpunanABDbaruberlakusetelahnormalisasiyangharusdinyatakan.','Bersihkanduplikat;Aharusx=20000;pertahankansalinanrawuntukjejak.',validity='UNCERTAIN',explanation_status='UNCERTAIN')
issue((7,5,9),'stem','2n+18=50diberitanpamakna18;Cmenambah4bukulangsungn18.','BdanCmemerlukanasumsipinjamanlain18tetapdanbukubaruuntuksiswabaru.','Jelaskan18bukuuntukkelompoklain;4bukubaruuntuk2siswabarumasing-masing2.',validity='UNCERTAIN',explanation_status='UNCERTAIN')

# Conditional cases preserve competing readings rather than selecting the author's key.
REVIEWS[6,3,1]['truths'][1] = 'UNCERTAIN'
REVIEWS[6,3,1]['reasons'][1] = '40 lembar bila pengali laju1.25; bila kenaikan125%, selisih360 lembar.'
CONDITIONS = {
    (6,3,1): [('B=1.25×lajuA', ['B']), ('B=(1+1.25)×lajuA', [])],
    (6,4,2): [('Awal6 orang,r=10/3; model aliran bersih memberi durasi22/5 hari, habis pada hari5', ['A']), ('Awal10 orang,r=2; durasi6 hari', ['B']), ('Awal11 orang,r=20/11; durasi32/5 hari, habis pada hari7', ['C']), ('Awal15 orang,r=4/3; durasi8 hari', ['D']), ('Awal20 orang,r=1; durasi10 hari', [])],
    (6,4,8): [('dA=dB=dC, jumlah hari kerja mingguan sama', ['A','B','C'])],
    (6,5,8): [('Satu porsi-hari didefinisikan sebagai satu jatah harian satu ternak', ['A','C','D']), ('Porsi tidak dinormalisasi menjadi jatah harian; D tidak terdefinisi', ['A','C'])],
    (6,5,10): [('Dibutuhkan berarti tambahan minimum', ['A','C']), ('Dibutuhkan berarti strategi tambahan yang cukup', ['A','B','C'])],
    (7,2,2): [('Persamaan ditulis ulang (2x+1)/3=(x+5)/2', ['C']), ('Persamaan literal 2x+1/3=x+5/2', [])],
    (7,3,3): [('Persamaan ditulis ulang (3x-2)/4=(x+4)/2', ['C']), ('Persamaan literal3x-2/4=x+4/2', [])],
    (7,3,6): [('Bentuk 2=2x²+5=13 dan bentuk 4=(1/2)(4x+6)=2x+3', ['A','B','D']), ('Bentuk 2=2×x×2+5=13 dan bentuk 4=21(4x+6)=2x+3', ['A'])],
    (7,4,4): [('Andi sekadar menyatakan x0 adalah salah satu solusi', ['A','B']), ('Andi dimaksud menyatakan hanya x0, tetapi kata hanya ditambahkan', ['A'])],
    (7,5,8): [('Hapus duplikasi: xxx menjadi x;20.00020.00020.000 menjadi20.000', ['A','B','D'])],
    (7,5,9): [('18 buku untuk kelompok lain tetap;4 buku tambahan untuk2 siswa baru;total54', ['A','C']), ('Kelompok yang dijelaskan hanya n siswa×2 buku;B menghitung kelompok itu', ['A','B'])],
}

# These checks independently pin the most consequential arithmetic/counterexamples.
assert F(300,1)/F(1333,100) != F(45,2)
assert F(210,45)*60-210 == 70
assert F(42,8) == F(21,4) and F(48,8) == 6
assert 9+F(200,30) == F(47,3)
assert F(12*15)*F(1333,1000) == F(11997,50) < 240
assert [4*(5*6), 4*(8*F(15,2)), 4*(4*6+3*F(15,2)), 4*(2*6+4*F(15,2))] == [120,240,186,168]
assert F(3,2)+(1-F(3,2)*(F(1,6)+F(1,4)))/F(1,4) == 3
assert F(13,6)*3-10 == F(-7,2)
assert 3*F(5,4)-F(2,4) == F(5,4)+F(4,2)
assert -3*4 != 12 and 8 != 2*8  # PG distractors that are also valid examples.


def source_projection(e):
    """Recover boundaries from original paragraphs, retaining parser output alongside.

    Special boundaries are anchored to exact original paragraph numbers, never to a
    prior audit. Native numeric stimulus labels are not answer-choice letters.
    """
    k = e['indicator'], e['level'], e['source_number']
    ps = e['paragraphs']
    first_explanation = next((p['paragraph_index'] for p in ps
        if re.match(r'^PEMBAHASAN\b', p['text'].strip(), re.I)), None)
    if k == (7,2,10): first_explanation = 1623
    if k == (7,3,10): first_explanation = 1859
    stop = next((p['paragraph_index'] for p in ps if re.match(r'^Kesalahan Umum',p['text'],re.I)), 10**9)
    ep = [p for p in ps if first_explanation is not None and first_explanation <= p['paragraph_index'] < stop and p['text'].strip()]
    explanation = '\n'.join(p['text'] for p in ep) or None
    stem = e['stem']
    # Remove only exact raw paragraphs that the parser had accidentally absorbed.
    for p in ep:
        for line in p['text'].splitlines():
            stem = stem.replace(line.strip(), '')
    stem = '\n'.join(t.strip() for t in stem.splitlines() if t.strip())
    # A legitimate option may repeat an explanation sentence verbatim. Trim only
    # the appended explanation boundary; never subtract explanation text globally.
    options = [re.split(r'\nPEMBAHASAN\b',o,flags=re.I,maxsplit=1)[0].strip() for o in e['options']]
    if k == (7,3,6):
        actual = [p for p in ps if re.match(r'^\[\s*\]\s*[A-D]\.',p['text'])]
        options = [re.sub(r'^\[\s*\]\s*[A-D]\.\s*','',p['text']) for p in actual]
        stem = '\n'.join(p['text'] for p in ps if 1744 <= p['paragraph_index'] <= 1749)
    if k == (7,5,8):
        paragraph = next(p['text'] for p in ps if p['paragraph_index'] == 2284)
        chunks = re.split(r'\[\s*\]\s*([A-D])\.\s*',paragraph)
        assert chunks[1::2] == list('ABCD')
        options = [x.strip() for x in chunks[2::2]]
        stem = '\n'.join(p['text'] for p in ps if 2281 <= p['paragraph_index'] <= 2283)+'\n'+chunks[0].strip()
    tables = [[[ '\n'.join(p['text'] for p in flatten(c['blocks'])) for c in row]
               for row in table['rows']] for table in e['tables']]
    return dict(stem=stem,options=options,key=e['key'],
        key_evidence=[dict(paragraph_index=p['paragraph_index'],text=p['text']) for p in ps
                      if re.search(r'KUNCI\s+JAWABAN|Revisi Kunci|Kunci Jawaban disesuaikan',p['text'],re.I)],
        explanation=explanation,explanation_paragraphs=ep,
        notes=e['additional_notes'],tables=tables,category_labels=e['category_labels'])


def build():
    entries = [e for e in source_entries(FOLDER) if e['indicator'] in (6,7)]
    assert len(entries) == len(REVIEWS) == 100
    result = []
    for e in entries:
        k = e['indicator'],e['level'],e['source_number']
        r = REVIEWS[k]
        projection = source_projection(e)
        options = projection['options']
        assert len(options) == len(r['truths']) == len(r['reasons']) == (3 if e['format']=='KATEGORI' else 4), k
        assert all(t.strip() and any(t in p['text'] for p in e['paragraphs']) for t in options), ('option source fidelity',k)
        category = e['format']=='KATEGORI'
        canonical = lambda label: str(ord(label)-64) if category and label in 'ABC' else label
        evaluations = [dict(id=str(j+1) if category else chr(65+j),source_label=f'({chr(97+j)})' if category else chr(65+j),text=t,truth=r['truths'][j],reason=r['reasons'][j]) for j,t in enumerate(options)]
        correct = [x['id'] for x in evaluations if x['truth']=='TRUE']
        conditional = any(x['truth']=='UNCERTAIN' for x in evaluations)
        raw_key = e['key']
        parsed_key_ids = raw_key[:] if raw_key is not None else None
        if raw_key is None: answer_status='MISSING'
        elif conditional or k in [(7,4,3),(7,5,5)]: answer_status='UNCERTAIN'
        else: answer_status='CORRECT' if parsed_key_ids == correct else 'INCORRECT'
        explanation_status = r.get('explanation_status','CORRECT' if projection['explanation'] and projection['explanation'].strip().upper()!='PEMBAHASAN' else 'MISSING')
        issues = list(r.get('issues',[]))
        validity = r.get('validity','VALID')
        if conditional and validity == 'VALID': validity='UNCERTAIN'
        if e['format']=='PG' and not conditional and len(correct)!=1: validity='INVALID'
        if answer_status=='INCORRECT' and not any(x['component']=='key' for x in issues):
            issues.append(dict(component='key',evidence=f'Kunci asli{raw_key}; himpunan benar independen{correct}.',impact='Kunci tidak mencakup tepat semua opsi benar.',proposal=f'Sesuaikan opsi/pertanyaan dahulu; himpunan benar pada teks sekarang{correct}.'))
        if validity=='INVALID' and not issues:
            raise AssertionError(('invalid without specific issue',k))
        recommendation = 'Pertahankan stimulus, opsi dan kunci; gunakan bukti hitung independen untuk pemeriksaan.' if not issues else ' '.join(x['proposal'] for x in issues)
        result.append(dict(audit_id=e['audit_id'],indicator=e['indicator'],level=e['level'],source_number=e['source_number'],
            source=e['source'],source_heading=e['source_heading'],format=e['format'],
            source_projection=projection,
            parser_projection={x:e[x] for x in ['stem','options','key','explanation','additional_notes','parse_flags']},
            raw_paragraphs=e['paragraphs'],
            independent_solution=r['independent_solution'],
            calculation_witness=r.get('calculation_witness'),
            option_evaluation=evaluations,
            independently_correct_ids=None if conditional else correct,
            definitely_correct_ids=correct,
            conditional_correct_ids=[dict(condition=c,ids=[canonical(x) for x in ids]) for c,ids in CONDITIONS.get(k,[])],
            parsed_key=raw_key,parsed_key_ids=parsed_key_ids,
            resolved_raw_key_ids=None if k in [(7,4,3),(7,5,5)] else parsed_key_ids,
            answer_status=answer_status,explanation_status=explanation_status,validity=validity,
            explanation_review=r['explanation_review'],
            notes_review=dict(status='INCORRECT' if any(x['component']=='notes' for x in issues) else ('CORRECT' if e['additional_notes'].strip() else 'MISSING'),
                source_text=e['additional_notes'],independent_check=r['independent_solution']),
            issues=issues,recommendation=recommendation))
    return dict(schema_version=1,scope='100 original questions, indicators6–7, 5 levels ×10 each',
        method='Read original source_entries paragraphs/tables and native DOCX for ambiguous notation. Independently solve stimulus, evaluate each actual choice, compare every explanation chain with independent proof. No old reviews, banks or generator output used.',
        option_id_convention='Actual source choices A–D; category rows(a),(b),(c) have canonical IDs1,2,3 and preserved source_label. Original numeric parsed keys preserved.',
        assumptions_policy='School proportional-rate problems are calculated in the usual ideal constant-rate model when context specifies or presupposes it; explicit alternative readings with material effects are retained as conditions, never selected from the explanation. Units and missing numerical inputs are checked separately.',
        summary={f'by_{field}':dict(Counter(e[field] for e in result)) for field in ['validity','answer_status','explanation_status']},
        entries=result)


if __name__=='__main__':
    data=build()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    reread=json.loads(OUT.read_text(encoding='utf-8'))
    assert len(reread['entries'])==100
    assert len({e['audit_id'] for e in reread['entries']})==100
    assert all(e['source_projection']['options']==[o['text'] for o in e['option_evaluation']] for e in reread['entries'])
    print(json.dumps(data['summary'],ensure_ascii=False))

