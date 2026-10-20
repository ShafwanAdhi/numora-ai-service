"""Reproduce the independent, source-only academic review of indicators 8 and 9.

Manual mathematical judgments below precede comparison with the declared key.
No generated bank or earlier review is read. Run from any working directory.
"""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from audit_original_questions import ROOT, source_entries

OUT = ROOT / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/part-08-09.json'
REVIEWS = {}


def add(i, l, q, solution, truths, reasons):
    assert (i, l, q) not in REVIEWS
    reasons = reasons.split(' | ')
    assert len(truths) == len(reasons), (i, l, q)
    REVIEWS[i, l, q] = dict(solution=solution, truths=truths, reasons=reasons)


# Indicator 8: independent reductions, endpoint checks, integer maxima.
add(8,1,1,'12000n+50000≤200000; n≤25/2. Bilangan bulat maksimum12; biaya12=194000,13=206000.', 'FTFF',
    '11 bukan maksimum karena12 masih194000≤200000 | 12 maksimum;13 memerlukan206000>200000 | 13 memerlukan206000>200000 | 14 memerlukan218000>200000')
add(8,1,2,'7−3x≤−5; −3x≤−12; x≥4, x∈Z. x=4 memberi−5; x=3 memberi−2>−5.', 'FTFF',
    'x≤4 memasukkan3 yang gagal dan membuang5 yang lolos | x≥4 tepat setelah pembagian−3 membalik arah | x≤−4 memasukkan−4 dengan19>−5 | x≥−4 memasukkan0 dengan7>−5')
add(8,1,3,'K=2[(3x−2)+(x+4)]=8x+4≤36; x≤4. Dimensi positif mengharuskan x>2/3; p maksimum3(4)−2=10, l=8,K=36.', 'FTFF',
    '8 bukan maksimum; p10,l8 memenuhiK36 | p10 dicapai x4; p lebih besar melanggar x≤4 | p12 membutuhkan x14/3>4 | p14 membutuhkan x16/3>4')
add(8,1,4,'4x−6>5x+1; −x>7; x<−7. Batas−7 tidak termasuk, daerah ke kiri.', 'TFFF',
    'Kiri−7 terbuka menyatakan x<−7 | Kanan−7 menyatakan x>−7;0 gagal | Batas7 salah;0 dalam gambar tetapi0 gagal | Kanan7 seluruhnya gagal x<−7')
add(8,1,5,'20n+60≤500; n≤22, n∈Z≥0. n22 memberi500; n23 memberi520.', 'FTFF',
    'Persamaan hanya mengizinkan22, menghilangkan muatan aman21 | Model≤ dan maksimum22 benar | Model≥ memasukkan23 dengan520>500 | Model< melarang22 padahal500 diperbolehkan')
add(8,1,6,'A:2x>6 sehingga x>3. B:−x<−3 sehingga x>3. C:x²>9 sehingga x<−3 atau x>3, berderajat2. D memuat x,y.', 'TTFF',
    'Linear satu variabel; solusi x>3 | Linear satu variabel; pembagian−1 memberi x>3 | Kuadrat; juga memasukkan−4, bukan tepat x>3 | Dua variabel x dan y, bukan satu')
add(8,1,7,'Jumlah76+82+84=242. (242+x)/4≥82 setara242+x≥328, x≥86; x85 memberi327/4=81,75.', 'TTTF',
    'Rata-rata empat nilai≥82 tepat | 4×82=328 minimum total | 328−242=86 minimum tes4 | 327/4<82 sehingga85 belum cukup')
add(8,1,8,'Distribusi benar2−3(x−1)=5−3x. Maka−3x≤6, x≥−2. Rangkaian siswa salah di1 dan4; dari−3x−1≤11 ke−3x≤12 benar secara lokal.', 'TTTT',
    '−3×(−1)=+3, bukan−3 | Menambah1 pada−3x−1≤11 menghasilkan−3x≤12 | −3x≤12 harus menjadi x≥−4 | Bentuk asli5−3x≤11 memberi x≥−2')
add(8,1,9,'25000y+150000≤450000; y≤12. Saat y=10,biaya400000,sisa50000; saat y=13,biaya475000 melampaui anggaran.', 'TTT',
    'Biaya tetap150000 ditambah25000y dibatasi450000 | Batas integer12;13 berbiaya475000 | 450000−(250000+150000)=50000')
add(8,1,10,'Stimulus native berbunyi32x−1\u200b≥2x+2\u200b, tanpa garis pecahan. Jika dibaca literal:30x≥3 sehingga x≥1/10. Jika diperbaiki menjadi(2x−1)/3≥(x+2)/2:4x−2≥3x+6 sehingga x≥8. Kedua versi berbeda; tidak dipilih diam-diam.', 'UUU',
    'Bergantung pecahan yang tidak terbaca; versi(2x−1)/3≥(x+2)/2 memberi2(2x−1)≥3(x+2) | Versi pecahan memberi x≥8; literal memberi x≥1/10 | Penuh8 ke kanan sesuai versi pecahan, bukan literal')

add(8,2,1,'15000x+80000≤350000; x≤18. Biaya18=350000,19=365000.', 'FTFF',
    '17 bukan maksimum;18 terjangkau | 18 tepat memenuhi350000 | 19 berbiaya365000 | 20 berbiaya380000')
add(8,2,2,'5−4(x−2)=13−4x≥21; −4x≥8; x≤−2. x−2 memberi21, x−1 memberi17.', 'FTFF',
    'x≥−2 memasukkan0 dengan13<21 | x≤−2 tepat; arah dibalik ketika dibagi−4 | x≥2 memasukkan2 dengan5<21 | x≤2 memasukkan0 yang gagal')
add(8,2,3,'B−A=(80000+20000x)−(120000+15000x)=5000x−40000. B>A iff x>8; x8 kedua biaya240000.', 'FFTF',
    'x<8 memberi B<A | x8 memberi A=B=240000 | x>8 tepat setara5000x>40000 | x≥8 memasukkan8 yang tidak lebih mahal')
add(8,2,4,'15−3(2t−1)=18−6t<3; −6t<−15; t>5/2. Batas5/2 terbuka, arah kanan.', 'TFFF',
    'Kanan5/2 terbuka tepat | Kiri5/2 memberi t<5/2 yang gagal | Bulatan penuh memasukkan5/2 dengan3<3 salah | Kiri penuh salah arah sekaligus memasukkan batas')
add(8,2,5,'K=2[(2x+5)+(x−1)]=6x+8≤68 memberi x≤10. Lebar x−1>5 memberi x>6. Irisan6<x≤10.', 'FFTF',
    'x≤10 saja memasukkan6 dengan lebar5 gagal | x>6 saja memasukkan11 denganK74 gagal | Irisan6<x≤10 tepat;10 memberiK68 | Memasukkan x6 yang lebarnya5, bukan>5')
add(8,2,6,'A:3x≥15,x≥5. B:−2y<6,y>−3. C:x²−4≤0 berderajat2. D:2a+3b>12 memiliki dua variabel.', 'TTFF',
    'Satu variabel derajat1 dan x≥5 benar | Satu variabel derajat1 dan y>−3 benar | Satu jenis variabel belum cukup; derajat2 | Derajat1 tetapi dua variabel a,b')
add(8,2,7,'Jumlah78+85+80+82=325. (325+x)/5≥83 memberi325+x≥415,x≥90. x88 memberi413/5=82,6.', 'TTTF',
    'Lima nilai dibagi5 dan≥83 tepat | 5×83=415 | 415−325=90 | 413/5<83 sehingga88 gagal')
add(8,2,8,'(1−2x)/3<(x+5)/2; kali6 positif:2−4x<3x+15; −7x<13; x>−13/7. Langkah1–3 benar,4 salah arah.', 'TTTT',
    'Kali6 dan distribusi2−4x,3x+15 tepat | −4x−3x=−7x,15−2=13 | Membagi−7 harus membalik< menjadi> | Penyelesaian tepat x>−13/7')
add(8,2,9,'25n+70≤650 memberi n≤116/5=23,2. Integer maksimum23; n23 beban645,n24 beban670. n20 beban570,sisa80.', 'TTT',
    '25n+70≤650 menjumlahkan kardus dan petugas | 23 maksimum;24 melebihi650 | 650−[25(20)+70]=80')
add(8,2,10,'A:3x−6≤5x+4 sehingga−2x≤10,x≥−5. B:2−2x>8 sehingga−2x>6,x<−3. Irisan[−5,−3) berisi integer−5,−4.', 'TTF',
    'Pembagian−2 memberi x≥−5 | Pembagian−2 memberi x<−3 | Ada dua integer−5,−4; klaim tidak ada salah')

add(8,3,1,'X:15000x≤285000 sehingga maksimum19. Y:12000y≤240000 sehingga maksimum20. Selisih20−19=1 siswa.', 'TFFF',
    '20−19=1 | 2 bukan selisih maksimum masing-masing20 dan19 | 3 bukan20−19 | 4 bukan20−19')
add(8,3,2,'−3(2x−4)=−6x+12; −6x+12>18−2x memberi−4x>6,x<−3/2. x0 memberi12>18 salah. Langkah1,2 benar;3 salah arah.', 'FFTF',
    'x0 gagal12>18; langkah3 salah | −3(−4)=+12 benar | Pembagian−4 memberi x<−3/2;0 bukan solusi | Menambah2x dan mengurangi12 pada langkah2 benar')
add(8,3,3,'I:2x≥8,x≥4. II:3x−6<x+10 memberi2x<16,x<8. Irisan[4,8):4 termasuk,8 tidak.', 'TFFF',
    'Penuh4,terbuka8 tepat untuk[4,8) | Terbuka4,penuh8 membalik kedua batas | Dua panah luar menyatakan gabungan luar interval | Penuh8 memasukkan8; syaratII memberi18<18 salah')
add(8,3,4,'Untuk solusi x>−4, koefisien k−2<0 dan batas12/(k−2)=−4; 12=−4k+8,k=−1. Verifikasi−3x<12 iff x>−4.', 'TFFF',
    'k−1 memberi−3x<12,x>−4 | k1 memberi−x<12,x>−12 | k3 memberi x<12 | k5 memberi3x<12,x<4')
add(8,3,5,'(155+x)/3≥80 memberi x≥85. Syarat lain x≥80,x≤100; irisan[85,100]. Pada85 rata-rata80.', 'FTFF',
    'Memasukkan80 dengan rata-rata235/3<80 | [85,100] tepat memenuhi seluruh batas | Memasukkan75 yang gagal rata-rata | Memasukkan80 dan membuang90 yang valid')
add(8,3,6,'(1)2x−1≤2x+1 mereduksi−1≤1,identitas benar; koefisien bersih0 sehingga bukan PtLSV ax+b≤0,a≠0. (2)−2x>8 iff x<−4. (3)native2x−4=2x−8 literal mustahil; versi x/2−4=(x−8)/2 identitas tetapi bukan PLSV nondegenerat. (4)x²+2x≥x²−6 mereduksi2x≥−6,x≥−3.', 'UTUT',
    'Kebenaran semua real benar; sebutan PtLSV identitas bergantung definisi apakah a=0 diperbolehkan | 3−2x>11 memberi x<−4 | Formula(3) rusak; literal−4=−8 salah, versi pecahan identitas; klasifikasi PLSV identitas juga degenerat | Setelah pembatalan x²,2x≥−6 sehingga x≥−3')
add(8,3,7,'Langkah tertulis1→2→3 sah:−(3−2x)=−3+2x,2(x−6)=2x−12, sehingga0≥−9 benar. Namun stimulus native43−2x≤−2x−6 kehilangan pecahan; literal43≤−6 mustahil. Versi(3−2x)/4≤(x−6)/(−2) menghasilkan semua real.', 'TTTU',
    'Perubahan tanda≤ menjadi≥ benar untuk perkalian−4<0; kebenaran rumus hasil bukan dapat dipastikan dari stimulus rusak | Distribusi dari langkah1 ke2 tepat | 0≥−9 benar terlepas nilai x | Semua real benar untuk versi pecahan; literal stimulus justru himpunan kosong')
add(8,3,8,'Beban tetap150+20(15)=450. 50x+450≤1200 memberi x≤15. x12 memberi1050,sisa150. Sisa S=750−50x; linear menurun, bukan S=kx maupun S=k/x.', 'TTTF',
    '150+300=450,beban50x+450≤1200 | Maksimum15;16 memberi1250>1200 | 1200−[600+450]=150 | S=750−50x bukan perbandingan lurus kx')
add(8,3,9,'−2x+5<13 memberi−2x<8,x>−4. Fani salah arah. Gina:5<13+2x;−8<2x;−4<x sah. x−3 memberi11<13.', 'TTT',
    'Pembagian−2 semestinya x>−4 | Rangkaian Gina memberi x>−4 tanpa pembagian negatif | −2(−3)+5=11<13')
add(8,3,10,'15000n+100000≤2500000 memberi n≤160. Kapasitas minimum n≥80;80≤n≤160,integer. n170 biaya2650000>2500000 namun170≥80.', 'TTT',
    '2400000/15000=160 | Irisan n≥80 dan n≤160 | n170 memenuhi minimum80 namun biaya2650000 melanggar anggaran')

add(8,4,1,'18000n+100000≤550000; n≤25. n25 biaya550000,n26 biaya568000;integer maksimum25.', 'FTFF',
    'Tanda< melarang25 yang sah | ≤ dan25 tepat | Biaya tetap harus ditambah; n36 nyata748000 | ≥ membolehkan26 sehingga tidak membatasi anggaran maksimum')
add(8,4,2,'2h−40≥220;2h≥260;h≥130. h130 diterima; lingkaran penuh130 ke kanan.', 'FFTF',
    'h≤130 memasukkan100 dengan160<220 | Batas90 salah dan lingkaran kosong tidak mewakili≥ | h≥130 penuh ke kanan tepat | h>130 menghilangkan130 yang diperbolehkan')
add(8,4,3,'5−2(x+3)=−2x−1≥3x+14;−5x≥15; x≤−3, x∈Z. x=−3 memberi ruas kiri5−2(0)=5,kanan3(−3)+14=5,sehingga batas termasuk.', 'TFFF',
    'x≤−3 tepat setelah pembagian−5 | x≥−3 memasukkan0 dengan−1≥14 salah | x≤3 memasukkan0 yang gagal | x≥3 seluruhnya gagal x≤−3')
add(8,4,4,'3x−7>5x+3 memberi−2x>10; bagi−2 menghasilkan x<−5. Langkah1,2 benar,3,4 salah arah.', 'FFFT',
    'Memindahkan5x memberi3x−5x,bukan3x+5x | 3+7=10,bukan−4 | Langkah3 tetap> sesudah bagi−2 salah | x<−5 karena pembagian−2 membalik>')
add(8,4,5,'25k+60≤800; k≤148/5=29,6. Maksimum integer29. Beban29=785,30=810,32=860;28 bukan maksimum.', 'FFTF',
    '810>800 tidak diperbolehkan | 32 menghasilkan860 setelah berat sopir ditambah | 29 aman785;30 tidak aman810 | 28 aman tetapi29 juga aman sehingga bukan maksimum')
add(8,4,6,'A:2x−5<9 iff x<7. B:(x+3)/4≥2 iff x≥5. C:x²−3x≤10 kuadrat. D:4y−4≤2y+8 iff y≤6.', 'TTFT',
    'Satu variabel x,derajat1 | Penyebut4 konstan; setara x≥5 linear | Koefisien x²=1 tidak hilang,derajat2 | Satu variabel y,2y≤12 linear')
add(8,4,7,'4−3x≥13;−3x≥9;x≤−3. x−4 memberi16≥13. Batas−3 termasuk karena4+9=13.', 'FTTF',
    'x≥−3 salah arah;0 gagal | x≤−3 tepat | x−4 memberi16≥13 | Terbuka−3 menghilangkan batas yang memenuhi13≥13')
add(8,4,8,'2(2x−3)−5x=−x−6. −x−6<1 memberi−x<7,x>−7. Penyederhanaan tidak membalik tanda; pembagian−1 membalik. x0 memberi−6<1.', 'TFTT',
    '4x−6−5x=−x−6 | Distribusi dan penggabungan tidak mengubah< | −x<7 setara x>−7 | x0 memberi−6<1')
add(8,4,9,'Total3 ujian3×72=216. (216+y)/4≥75 iff y≥84. y80 memberi74; y85 memberi301/4=75,25.', 'TFT',
    'Model(216+y)/4≥75 tepat | Minimum84,bukan80;80 memberi74 | 301/4≥75 sehingga85 memenuhi')
add(8,4,10,'Persamaan2x+6=12 iff x3. Pertidaksamaan2x+6≤12 iff x≤3. Kali−1:−2x−6=−12 tetap=;−2x−6≥−12 membalik≤.', 'TTF',
    '2x=6 sehingga solusi tunggal3 | x≤3 memiliki tak hingga anggota real | = tidak berubah arah;hanya≤ berubah menjadi≥')

add(8,5,1,'16000n+120000≤600000; n≤30. n30 berbiaya600000,n31 berbiaya616000. Pembagian600000/16000=75/2=37,5; lantainya37,bukan30.', 'FTFF',
    '37 berbiaya712000>600000 | Maksimum30; biaya30 tepat600000 dan31 melampaui | 28 bukan maksimum;30 masih terjangkau | 37,5 dibulatkan ke bawah37,bukan30;alasan salah')
add(8,5,2,'7−3x≤19;−3x≤12;x≥−4. x=−4 menghasilkan19≤19. Penuh−4 ke kanan; Fajar salah arah dan batas.', 'FFFT',
    '≤ memuat batas,tidak diwakili lingkaran kosong | Pembagian−3 memberi≥,arah kanan | Batas12/(−3)=−4,bukan4 | Gina penuh−4 ke kanan tepat')
add(8,5,3,'4−2(x+5)=−2x−6>8;−2x>14;x<−7. Langkah1–3 benar;4 salah arah.', 'FFTF',
    '−2×5=−10,bukan+10 | Menambah6 menghasilkan14,bukan2 | Pembagian−2 memberi x<−7 | Langkah4 x>−7 salah')
add(8,5,4,'15k+130≤350; k≤220/15=44/3. Integer maksimum14;14 memberi340,15 memberi355. 44/3=14,666… bukan14,67 tepat.', 'TFFF',
    '14 aman340 dan15 gagal355 | 355>350,toleransi tidak diberikan | 23 memberi475 setelah petugas dihitung | 13 bukan maksimum;14 aman340')
add(8,5,5,'30x+50≤500; x≤15. x16 memberi480+50=530>500; sopir benar menyatakan melebihi batas.', 'FTFF',
    'Beban16=530,bukan500 | 530>500 membuktikan klaim sopir | Maksimum15,bukan18 | Kesimpulan benar tetapi alasan maksimum12 salah;15 aman500')
add(8,5,6,'(i)2x−7<9 iff x<8,linear satu variabel. (ii)3x+2y≤12 dua variabel. (iii)x−2≥12 iff x≥14. (iv)−4x>12 iff x<−3.', 'TFTT',
    'Satu variabel x derajat1 dan< | Ada dua variabel x,y | Kali3 positif memberi x≥14 | Bagi−4 memberi x<−3')
add(8,5,7,'5−2x≥11;−2x≥6;x≤−3. Batas−3 terisi; x−5 memberi15≥11.', 'FTFT',
    'x≥−3 salah arah;0 gagal | x≤−3 tepat | −3 memberi11≥11 sehingga harus penuh | x−5 memberi15≥11')
add(8,5,8,'Jumlah70+75+80=225. (225+x)/4≥78 iff x≥312−225=87. x90 memberi315/4=78,75;85 memberi310/4=77,5.', 'TTTF',
    'Empat nilai dibagi4 dan≥78 | Minimum312−225=87 | 315/4≥78 | 310/4<78,85 tidak cukup')
add(8,5,9,'3x+65≤140;3x≤75;x≤25. Beban25=140,beban26=143.', 'TFT',
    'Menjumlahkan beban kotak3x dan pengemudi65 | Maksimum25;26 menghasilkan143>140 | 25 menghasilkan140≤140 sehingga aman')
add(8,5,10,'I:−2x=8 memberi x=−4 tunggal. II:−2x≤8 memberi x≥−4 karena pembagian negatif. SolusiI satu anggota,II tak hingga real.', 'TTF',
    '8/(−2)=−4 | Membagi−2 mengubah≤ menjadi≥ | Satu solusi dibanding tak hingga,bukan sama banyak')

# Indicator 9: solve from simultaneous constraints, without declared keys.
add(9,1,1,'(2x+3y)+(3x+2y)=70000 memberi x+y14000. Selisih persamaan memberi x−y2000; x8000,y6000. Pesanan2x+2y28000.', 'FFTF',
    '24000≠2(8000+6000)=28000 | 26000≠28000 | 2x+2y=28000 | 30000≠28000')
add(9,1,2,'Stimulus memberi2x+3y=85000,x+4y=80000. Matriks yang diperlukan[[2,3],[1,4]] [x;y]=[85000;80000]. Native opsi meratakan elemen tanpa baris/kolom: A(21​34​),B(23​14​). Urutan kolom memilihA;urutan baris memilihB;tidak ada struktur native yang menentukan.', 'UUFF',
    'A benar hanya jika21 dan34 dibaca sebagai kolom [2,1] dan[3,4] | B benar jika23 dan14 dibaca sebagai baris[2,3] dan[1,4] | C versi kolom[[3,2],[4,1]] dan versi baris[[3,4],[2,1]] keduanya tidak cocok[[2,3],[1,4]] | D versi kolom[[2,3],[4,1]],versi baris[[2,4],[3,1]];denganRHS terbalik keduanya tidak cocok model yang dibalik[[1,4],[2,3]]')
add(9,1,3,'Mengalikan garis1 dengan2 memberi4x−2y=8. Garis2 paralel berbeda iff k≠8,termasuk k0,k4. Maka nilai konkret k4 dan syarat umum k≠8 sama-sama memenuhi;opsi PG tumpang tindih.', 'FTTF',
    'k8 menghasilkan garis berimpit,bukan paralel berbeda | k4≠8 merupakan nilai konkret yang memenuhi | Syarat lengkap k≠8 tepat | k≠4 masih mengizinkan8 yang berimpit;tidak cukup')
add(9,1,4,'p+l26,p−l6;2p32,p16,l10;luas160m².', 'FFTF',
    '140≠16×10 | 150≠160 | 16×10=160 | 170≠160')
add(9,1,5,'Substitusi x=2y−3 langsung memberi3(2y−3)+4y31;10y40,y4,x5. Eliminasi juga dapat dilakukan tanpa bentuk baku:3×persamaan1 memberi3x6y−9;kurangkan dari persamaan2 untuk10y40.', 'TUFF',
    'Substitusi langsung menghasilkan y4 | Eliminasi juga menghasilkan y4 tanpa bentuk baku;keunggulan paling langsung tidak memiliki ukuran langkah baku | y5 memberi x7 dan3x+4y41≠31 | y5 salah;nilai benar4')
add(9,1,6,'4x+3y71000,2x+5y81000. Dua kali persamaan2 dikurangi1:7y91000,y13000;2x16000,x8000. Selisih5000;3x+2y50000.', 'TTTF',
    'x=8000;4x+3y=32000+39000=71000 | y=13000;2x+5y=16000+65000=81000 | 13000−8000=5000 | 3(8000)+2(13000)=50000,bukan55000')
add(9,1,7,'Garis2=2×garis1,sehingga berimpit. Garis3 sama ruas kiri dengan konstanta6≠12,sehingga sejajar berbeda. Garis1 saat x0 memberi y4. Garis2 dibanding3: ruas kiri dua kali,konstanta24≠12.', 'TTTF',
    'Garis2=2×garis1,solusi tak hingga | Menuntut2x+3y sekaligus12 dan6 mustahil | x0 memberi3y12,y4 | Garis2/2 berkonstanta12,garis3 berkonstanta6;tidak ada titik potong')
add(9,1,8,'x+y100000,x−y20000;2x120000,x60000,y40000;rasio60000:40000=3:2.', 'TTTT',
    'Jumlah100000 dan selisih20000 sesuai narasi | x60000 | y40000 | 60000/40000=3/2')
add(9,1,9,'3x+2y210000,2x+4y260000. Dua kali1 dikurangi2 memberi4x160000,x40000. 4y180000,y45000. x+y85000.', 'TTT',
    'x=40000;120000+90000=210000 | y=45000;80000+180000=260000 | 40000+45000=85000')
add(9,1,10,'I:persamaan2=2×persamaan1,garis berimpit. II:x−y harus sekaligus3 dan7,mustahil;gradien1 dengan intersep−3,−7. (4,1) hanya memenuhi yang pertama.', 'TTF',
    'I berimpit dan solusi tak hingga | II paralel berbeda,solusi kosong | 4−1=3≠7 sehingga bukan solusiII')

add(9,2,1,'2×(3x+5y65000)−3×(2x+3y41000) memberi y7000;2x20000,x10000. Pesanan2x+2y34000;kembali50000−34000=16000.', 'FTFF',
    '14000≠50000−34000 | 16000 kembalian tepat | 18000≠16000 | 20000≠16000')
add(9,2,2,'Model4x+2y=140000,3x+5y=210000. Matriks perlu[[4,2],[3,5]] [x;y]=[140000;210000]. Native A(43​25​),B(42​35​) tanpa struktur. Membaca kolom memilihA;membaca baris memilihB.', 'UUFF',
    'A benar bersyarat43 dan25 adalah kolom | B benar bersyarat42 dan35 adalah baris | C versi kolom[[2,4],[5,3]],versi baris[[2,5],[4,3]];denganRHS ditukar keduanya tidak cocok model terbalik[[3,5],[4,2]] | D versi kolom[[4,5],[3,2]],versi baris[[4,3],[5,2]];keduanya tidak cocok[[4,2],[3,5]]')
add(9,2,3,'p+l26,p2l+2;3l24,l8,p18;luas18×8=144m².', 'FTFF',
    '128≠18×8 | 144=18×8 | 160≠144 | 180≠144')
add(9,2,4,'Dua kali garisA:4x−6y=−24. GarisB kx−6y10 paralel berbeda iff k4,karena konstanta10≠−24. Rasio benar2/4=(−3)/(−6)=1/2≠−12/10=−6/5.', 'FFTF',
    'k2 gradienB1/3≠A2/3 | k3 gradienB1/2≠2/3 | k4 memberi ruas kiri sama,konstanta10≠−24 | k6 gradienB1≠2/3')
add(9,2,5,'Samakan35000x+100000=45000x+20000;10000x80000,x8,y380000. Substitusi langsung bisa;eliminasi juga langsung mengurangkan dua persamaan y=f(x) menghasilkan0=−10000x+80000 tanpa bentuk umum.', 'UTFF',
    'Eliminasi y bisa langsung tanpa menata ulang; x8 benar;frasa paling langsung tidak membedakanA/B secara matematis | Substitusi menyamakan y dan x8 benar | x10 memberi450000 dan470000,bukan impas | x10 salah;impas8')
add(9,2,6,'2×(5x+2y44000)−(3x+4y46000) memberi7x42000,x6000. 4y28000,y7000. Selisih1000,total2x+2y26000.', 'TTTF',
    'x6000 | y7000 | 7000−6000=1000 | 12000+14000=26000,bukan30000')
add(9,2,7,'Garis2=2×garis1,berimpit. Garis3 sama ruas kiri3x−2y dengan konstanta12≠6,paralel berbeda. Saat y0 pada1,x2. (0,0) tidak memenuhi garis2 ataupun3.', 'TTTF',
    '2 adalah kelipatan2 dari1 | 3x−2y tidak dapat sekaligus6 dan12 | 3(2)−2(0)=6 | Garis2/2 konstanta6 berbeda12,solusi kosong;origin juga gagal')
add(9,2,8,'m+c50;2500m+2000c110000. Kurangi2000(m+c)=100000 memberi500m10000,m20,c30. Pendapatan3500(20)+3000(30)=160000;untung50000.', 'TTTF',
    'm20 | c30 | 70000+90000=160000 | 160000−110000=50000,bukan60000')
add(9,2,9,'x+2y80000 dari persamaan1;3x+2y180000. Kurangkan memberi2x100000,x50000,y15000. x+2y80000.', 'TTT',
    'x50000 | y15000 | 50000+2(15000)=80000')
add(9,2,10,'x−y15000,x+y75000;2x90000,x45000(Dika),y30000(Eka). Langkah3 menukar identitas keduanya.', 'TTT',
    'Dika lebih15000 dan jumlah75000 dimodelkan tepat | x untuk Dika sehingga45000 milik Dika | Eka30000,bukan45000;penukaran pada langkah3 nyata')

add(9,3,1,'PaketB/2:x+2y13000. Kurangkan dari3x+2y23000 memberi2x10000,x5000,y4000. Satuan5x+5y45000;2PaketA46000;selisih1000 lebih murah. 2PaketA berisi6 gantungan dan4 stiker,bukan5 masing-masing.', 'TFFF',
    '45000 dibanding46000 lebih murah1000 | Arah selisih terbalik;45000<46000 | Selisih1000,bukan2000 | Arah dan besar salah;selisih−1000')
add(9,3,2,'A=[[2,3],[5,2]],det4−15=−11. adjA=[[2,−3],[−5,2]];inverse=adjA/(−11). X=(260000/11,230000/11). A·adjA=−11I.', 'TFFF',
    'adjA/(−11) benar;mengalikan memberi260000/11,230000/11 | [[2,3],[5,2]]/11 bukaninverse;produkA dengannya memiliki elemen luar diagonal12/11,20/11 | Matriks dalamC=−adjA;pembagi−11 menghasilkan−inverse | Pembagi+11 memberi−inverse;pasangan negatif tidak memenuhi RHSpositif')
add(9,3,3,'Dua kali rute1 memberi6x−2ay=24. Untuk identik rute2,−2a=8 dan b=24 sehingga a=−4,a+b=20.', 'TFFF',
    '−4+24=20 | 28≠20 | −20≠20 | 16≠20')
add(9,3,4,'Substitusi y3x−5 ke2x+5y43 memberi17x−25=43,x4,y7. Eliminasi juga bisa:kalikan persamaan1 dengan5 lalu kurangkan dari persamaan2 menghasilkan17x68 tanpa menata ke bentuk baku.', 'TUFF',
    'Substitusi langsung menghasilkan(4,7) | 5y15x−25,kurangkan dari2x+5y43 memberi17x68; metode valid tanpa bentuk baku,maka klaim paling langsung ambigu | (5,10) memberi2x+5y60≠43 | (5,10) tidak memenuhi persamaan2 dan mengubah bentuk menambah langkah')
add(9,3,5,'n4t+6 dan n5(t−2)=5t−10. Samakan4t+6=5t−10,t16,n70. Verifikasi4×16+6=70;5×14=70.', 'TFFF',
    '70 siswa16tenda memenuhi kedua kondisi | 64−4(14)=8,bukan6;5(14−2)=60≠64 | 70−4(14)=14,bukan6 | 60−4(16)=−4,bukan6')
add(9,3,6,'Q=2P. R memiliki ruas kiri sama denganP,konstanta−4≠6. Gradien semua2/3. P intersepX=3,Y=−2. Q danR sejajar,tidak tegak lurus.', 'TTTF',
    'Q/2=P sehingga berimpit,tak hingga | P danR memerlukan6=−4,mustahil | 2(3)=6 dan−3(−2)=6 | Kedua gradien2/3,produk4/9≠−1')
add(9,3,7,'30x+20y130000;20x+40y140000. Bagi10 dan20:3x+2y13000,x+2y7000;2x6000,x3000,y2000. Selisih1000;15x+15y75000;10x30000>12y24000.', 'TTTT',
    'x3000,y2000 memenuhi130000 dan140000 | 3000−2000=1000 | 15(3000+2000)=75000 | 10(3000)=30000>12(2000)=24000')
add(9,3,8,'Jumlah persamaan memberi4x16,x4;2y4,y2. Selisih persamaan1−2 adalah−2x+4y0,bukan−2x0. Pasangan(0,4) memberi8 pada1 tetapi−8 pada2.', 'TTTT',
    'Untuk menghapus+2y dan−2y perlu penjumlahan;pengurangan siswa kehilangan4y | 4x16 memberi x4 | 4+2y8 memberi y2 | 0+8=8 tetapi0−8=−8≠8')
add(9,3,9,'A:persamaan2=2×1 sehingga berimpit. B:2×1 memberi2x−4y8,berbeda10,sehingga kosong. C:jumlah memberi2x8,x4,y2;det−2≠0.', 'TTT',
    'Rasio2/4=3/6=10/20=1/2 | Rasio1/2=(−2)/(−4)=1/2≠4/10=2/5 | (4,2) memberi6 dan2;det−2 menjamin tunggal')
add(9,3,10,'v=r+15000. 100r+50(r+15000)=3750000;150r3000000,r20000,v35000. Cek2000000+1750000=3750000.', 'TTT',
    'Selisihv−r15000 dan penerimaan100r+50v3750000 | r20000 | v20000+15000=35000')

add(9,4,1,'2x+3y31000,4x+y37000. 2×persamaan1−2 memberi5y25000,y5000;x8000. Pesananx+2y18000. A danC sama-sama18000;formatPG tidak unik.', 'TFTF',
    '18000=8000+2(5000) | 20000≠18000 | 18000 beserta revisi8000+10000 benar;duplikatA | 22000≠18000')
add(9,4,2,'2d+3a190000,4d+a220000. 2×1−2 memberi5a160000,a32000. 4d188000,d47000. Selisih15000.', 'FTFF',
    '10000≠47000−32000 | Selisih47000−32000=15000 | 20000≠15000 | 25000≠15000')
add(9,4,3,'4x+6y24 adalah dua kali2x+3y12. Satu garis sama,solusi semua titik pada2x+3y12,tak hingga.', 'TFFF',
    'Berimpit,solusi tak hingga | Bukan tunggal;misal(0,4) dan(6,0) keduanya solusi | Bukan paralel berbeda,konstanta juga berkelipatan | Bukan hanya dua;seluruh garis memenuhi')
add(9,4,4,'I:3×(x−2y5) memberi3x−6y15≠10,sehingga kosong. II:jumlah(x+y6)+(2x−y3) memberi3x9,x3,y3,det−3≠0.', 'FFFT',
    'I kosong,bukan tunggal;II tunggal,bukan kosong | I kosong,II tunggal,bukan tak hingga | II memiliki(3,3) | I paralel berbeda,II titik tunggal(3,3)')
add(9,4,5,'x2y−1 langsung disubstitusikan:3(2y−1)+4y27;10y30,y3,x5. Tidak perlu syarat tanda y.', 'FFTF',
    'Eliminasi tidak selalu lebih cepat;di sini substitusi langsung | Grafik tetap memerlukan penentuan garis dan pembacaan,tanpa hitungan bukan alasan valid | Variabelx terisolasi memungkinkan substitusi langsung | Efisiensi substitusi tidak bergantung y positif;struktur aljabarnya menentukan')
add(9,4,6,'3x+2y19000,2x+4y18000. Kedua/2:x+2y9000. Selisih memberi2x10000,x5000,y2000. x>y.', 'TTTF',
    'Koefisien jumlah pembelian tepat | x5000 | y2000 | 5000>2000,buku lebih mahal')
add(9,4,7,'2×(2x−y4)+(x+2y12) memberi5x20,x4. Persamaan2:2y8,y4. Cek8−4=4 dan4+8=12;det5≠0.', 'TFTT',
    'x4 | y2 memberi persamaan1=6≠4 | y4 | (4,4) memenuhi kedua dan det5≠0,titik potong unik')
add(9,4,8,'I:2×(2x+y=5) memberi4x+2y=10,berimpit. II:ruas kiri3x−y harus4 dan8,mustahil. III:2x−y=2 memberi y=2x−2; x+2(2x−2)=6,5x=10,x=2,y=2,tunggal.', 'FTFT',
    'I berimpit,tidak kosong | I punya tak hingga solusi | II kosong,bukan tunggal | II sejajar berbeda karena4≠8')
add(9,4,9,'p+l21,p−l5;2p26,p13,l8. Luas13×8=104m².', 'TFT',
    'Keliling42 memberi jumlah21;selisih5 | p13,bukan15 | 13×8=104')
add(9,4,10,'Jumlah persamaan2x14,x7. Dari x+y10,y3. Det−2≠0,solusi tunggal(7,3).', 'TTF',
    'Menjumlahkan menghapus+y dan−y,2x14 | (7,3) memenuhi7+3=10,7−3=4 | Garis berpotongan pada(7,3),bukan tidak pernah')

add(9,5,1,'PaketB/2:x+2y45000. Kurangkan dari3x+2y85000 memberi2x40000,x20000;2y25000,y12500. x>y,pernyataan pengunjung salah. OpsiA danB menyatakan evaluasi sama.', 'TTFF',
    'Salah sebab20000>12500;matematis benar | Harga20000 dan12500 benar;pengunjung salah,duplikatA | Harga15000 dan20000 memenuhi paketA85000 tetapi gagal paketB30000+80000=110000≠90000 | Diskon khusus tidak diberikan;data tidak mendukung kesimpulan tiket sepeda air lebih murah')
add(9,5,2,'4l+3k22000,2l+5k25000. 2×2−1 memberi7k28000,k4000;l2500. Pesanan2l+3k=5000+12000=17000. Uang18000 cukup,kembalian1000.', 'FFFT',
    'Uang18000 melebihi17000,tidak kurang2000 | Harga17000≠18000,ada kembali1000 | Kembalian1000,bukan3000;5000+12000=17000 | 18000−17000=1000')
add(9,5,3,'I:persamaan2=2×1,berimpit,tak hingga. II:x+2y sekaligus8 dan12,mustahil,paralel berbeda.', 'FFFT',
    'Klasifikasi kedua sistem tertukar | I tak hingga,bukan tunggal | II kosong,bukan tak hingga | I berimpit tak hingga,II paralel tanpa solusi')
add(9,5,4,'Substitusi y3x−2 ke2x+5y24:17x−10=24,x2,y4. Substitusi langsung wajar paling praktis; klaim jumlah langkah eliminasi mutlak perlu bentuk baku terlalu kuat.', 'TFFF',
    'y terisolasi sehingga2x+5(3x−2)=24 langsung | Tidak ada aturan eliminasi selalu lebih cepat | Substitusi tetap berlaku untuk koefisienx positif2 | Jumlah langkah bergantung cara menulis,bukan selalu persis sama')
add(9,5,5,'Data berulang tetap memuat p+l18,p−l4;2p22,p11,l7,luas77m², sehingga klaim80 salah. A menyebut72,B menyebut10 dan8,C diawaliBenar lalu revisiSALAH,D menyebut12 dan6. Tak ada opsi konsisten yang menyatakanSalah karena77;narasi akhir mengubah kunci keA tetapiA belum direvisi.', 'FFUF',
    'Penolakan80 benar tetapi alasanluas72 salah;luas77 | p10,l8 berselisih2,bukan4 | Berkontradiksi:Benar terhadap80 lalu revisi mengatakanSALAH dan77;tidak dipilih salah satu versi | p12,l6 berselisih6,bukan4;luas72 juga bukan80')
add(9,5,6,'2×(3x−y5)+(x+2y11) memberi7x21,x3. 3+2y11,y4. Det7≠0;solusi(3,4).', 'TFTT',
    'x3 | y2 memberi3x−y7≠5 | y4 | (3,4) memberi9−4=5 dan3+8=11,det7≠0')
add(9,5,7,'Maju:2k_M+3s_M=70000;Jaya:4k_J+s_J=65000. Dua persamaan empat harga tidak menentukan harga bersama. ContohMaju k20000,s10000 danJaya k15000,s5000 memenuhi data,berbeda dari sumber. Jika tambahan harga kedua toko sama DAN unit data adalahpasang,k12500,s15000 sehinggaBD. Kedua tambahan tidak disebutkan.', 'UUUU',
    'Tidak ada harga bersama;15000 bisa benar diJaya atau salah. Bersyarat sama harga:12500,bukan15000 | 12500 hanya teridentifikasi bila harga antar toko sama dan unitpasang | Urutan harga tidak ditentukan;contohMaju20000>10000,versibersama12500<15000 | 15000 hanya muncul pada asumsi harga bersama dan unitpasang')
add(9,5,8,'I:persamaan2 adalah dua kali(x−y=2),yakni2x−2y=4,berimpit. II:x+y sekaligus5 dan9,mustahil. III:3×(2x+y=7) ditambah(x−3y=−7) memberi7x=14,x=2,y=3;det−7≠0.', 'TFTT',
    'I berimpit,solusi tak hingga | (5,9) berjumlah14,bukan5 ataupun9;II kosong | II paralel berbeda sebab5≠9 | (2,3) memberi7 dan−7,det−7 menjamin tunggal')
add(9,5,9,'2x+3y27000,x+2y16000. 2×2−1 memberi y5000. x16000−10000=6000.', 'TFT',
    'Koefisien pembelian2,3 dan1,2 tepat | x6000,bukan7000 | y5000')
add(9,5,10,'x=4;2x+y=11 memberi y=11−2(4)=3,solusi tunggal(4,3). Substitusi langsung satu evaluasi;eliminasi juga dapat mengurangkan dua kali persamaan x=4 dari persamaan2,tanpa perlu menambahkan0y secara eksplisit.', 'TTF',
    'Evaluasi langsung y11−8=3 | (4,3) memenuhi kedua; x sudah tetap | Eliminasi tidak lebih cepat secara niscaya;perlu menghilangkan2x sementarax sudah tersedia')


def issue(component, evidence, impact, proposal):
    return dict(component=component, evidence=evidence, impact=impact, proposal=proposal)


# Status overrides address the source record, including every explanation error.
OVERRIDES = {
 (8,1,10): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='UNCERTAIN',conditional_correct_ids=[dict(condition='Stimulus diperjelas menjadi(2x−1)/3≥(x+2)/2',ids=['1','2','3'])], issues=[issue('stem','p2557 native w:t berisi32x−1\u200b≥2x+2\u200b;tidak ada pecahan OMML/garis pembagi.','Literal x≥1/10;versi yang dipakai pembahasan x≥8;tidak ekuivalen.','Tuliskan pecahan eksplisit(2x−1)/3≥(x+2)/2 sebelum menentukan kunci.')]),
 (8,3,2): dict(explanation_status='INCORRECT',issues=[issue('explanation','p2869 menulis x<−46\u200b⟹x<−1,5 dalam native w:t.','Rangkaian pecahan rusak;literal−46 bukan−3/2. Kesimpulan dan kunciC tetap benar.','Ganti tahap pembagian menjadi x<6/(−4)=−3/2=−1,5.')]),
 (8,3,6): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='UNCERTAIN',conditional_correct_ids=[dict(condition='(3)dimaksud x/2−4=(x−8)/2 DAN istilah PtLSV/PLSV mengizinkan identitas dengan koefisien bersih0',ids=['A','B','C','D']),dict(condition='Definisi linear nondegenerat a≠0 setelah penyederhanaan;rumus(3) tidak dipulihkan',ids=['B','D'])],issues=[issue('stem','p2949 native2x\u200b−4=2x−8\u200b;literal−4=−8,tidak ada solusi.','PernyataanC tidak dapat dipastikan tanpa merekonstruksi pecahan.','Nyatakan formula(3)dengan pembilang dan penyebut eksplisit.'),issue('classification','PernyataanA menyebut identitas−1≤1 sebagai PtLSV;C menyebut identitas0=0 sebagaiPLSV.','Setelah penyederhanaan koefisien variabel0;bukan bentuk linear nondegenerat ax+b⋚0,a≠0.','Nyatakan konvensi definisi atau ubahA/C menjadi pernyataan identitas tanpa klasifikasi linear.'),issue('projection','Parser menganggap empat stimulus bernomor1–4 sebagai opsiA–D,opsi eksplisit A–D menjadiE–H.','KeyA–D akan menunjuk stimulus,bukan pernyataan jawaban.','Gunakan opsi eksplisit p2952–2955;semua stimulus tetap dipertahankan dalam source_projection.stem.')]),
 (8,3,7): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='UNCERTAIN',conditional_correct_ids=[dict(condition='Stimulus diperbaiki(3−2x)/4≤(x−6)/(−2)',ids=['A','B','C','D'])],issues=[issue('stem','p2967 native43−2x\u200b≤−2x−6\u200b tanpa pecahan.','Literal menghasilkan43≤−6(himpunan kosong),sedangkan langkah1–3 menghasilkan semua real.','Tampilkan pecahan eksplisit;langkah1–3 saja tidak membuktikan kesetaraan dengan stimulus rusak.')]),
 (8,3,8): dict(explanation_status='INCORRECT',issues=[issue('explanation','OpsiD ditolak dengan alasan hubungan sisa kapasitas berbanding terbalik.','S=750−50x linear menurun;bukan perbandingan terbalik S=k/x.Misalx5,S500 memberi xS2500; x10,S250 memberi2500 kebetulan,namun x1,S700 memberi700.','Tulis hubungan linear menurun denganS=750−50x;hindari istilah berbanding terbalik.')]),
 (8,5,4): dict(explanation_status='CORRECT',issues=[issue('precision','Sumber menulis k≤220/15 \\implies k≤14,67;tidak menulis persamaan220/15=14,67.','Implikasi sah karena44/3<14,67;untuk domain integer kedua batas memberi maksimum14 yang sama.Tidak ada kesalahan matematis;nilai pecahan tepat44/3 lebih jelas.','Opsional:pertahankan k≤44/3;catat44/3≈14,67 lalu ambil lantai14.')]),
 (9,1,2): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='UNCERTAIN',conditional_correct_ids=[dict(condition='Run angka native dibaca urutan perkolom',ids=['A']),dict(condition='Run angka native dibaca urutan perbaris',ids=['B'])],issues=[issue('options','p3555–3558 berisi matriks runtuh plain w:t seperti(21\u200b34\u200b)(xy\u200b).','Baris,kolom,dan dimensi tidak terkode;A/B dapat bertukar menurut rekonstruksi.','Gunakan matriks OMML/LaTeX eksplisit[[2,3],[1,4]] dengan vektor kolom;bangun ulang semua opsi.')]),
 (9,1,3): dict(validity='INVALID',answer_status='INCORRECT',explanation_status='INCORRECT',issues=[issue('options','B menyatakan k4;C menyatakan k≠8;k4 memenuhi kedua garis paralel berbeda.','PG memiliki dua respons benar di bawah permintaan nilai k yang tepat.','Tanyakan syarat perlu dan cukup untukk,lalu gantiB dengan kondisi yang salah;atau gunakan empat nilai konkret.'),issue('explanation','Rasio4/k digunakan tanpa menangani k0.','k0 adalah kasus valid paralel namun4/0 tidak terdefinisi sehingga argumen tidak mencakup semua k≠8.','Bandingkan langsung4x−2y8 dengan4x−2yk;paralel berbeda iff k≠8.')]),
 (9,1,5): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='INCORRECT',conditional_correct_ids=[dict(condition='Metode dipilih berdasarkan pola penggantian variabel eksplisit menurut konvensi pedagogis',ids=['A']),dict(condition='Eliminasi tanpa bentuk baku juga diizinkan;tidak ada ukuran efisiensi tambahan',ids=['A','B'])],issues=[issue('explanation','Pembahasan mengklaim eliminasi memerlukan pengubahan x−2y−3 dan penyamaan koefisien.','3×persamaan1 memberi3x6y−9,lalu persamaan2 dikurangi langsung menghasilkan10y40;pengubahan bentuk baku tidak wajib.','Tanyakan metode penggantian variabel secara eksplisit atau ubah nilai dalamB agar salah;hindari klaim eliminasi wajib bentuk baku.')]),
 (9,1,7): dict(explanation_status='INCORRECT',issues=[issue('explanation','PembahasanB menyebut konstanta berbeda lalu mencetak(12=6);D mencetak rasio runtuh24\u200b=36\u200b=624\u200b.','12=6 salah;relasi rasio untuk garis paralel harus membedakan konstanta.Klasifikasi/keyABC tetap benar.','Tulis12≠6;untuk(2),(3):4/2=6/3=2≠24/6=4.')]),
 (9,2,2): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='UNCERTAIN',conditional_correct_ids=[dict(condition='Run angka native dibaca urutan perkolom',ids=['A']),dict(condition='Run angka native dibaca urutan perbaris',ids=['B'])],issues=[issue('options','p3773–3776 matriks plain w:t seperti(43\u200b25\u200b),tanpa struktur baris/kolom.','Matriks koefisien yang benar[[4,2],[3,5]] dapat dipetakan keA/perkolom atauB/perbaris.','Tulis matriks serta vektor eksplisit;periksa kembali semua distraktor.')]),
 (9,2,4): dict(explanation_status='INCORRECT',issues=[issue('explanation','Pembahasan menulis syarat sejajar a1/a2=b1/b2=c1/c2 dan cek konstanta−12/10=−6/5=1/2.','Syarat yang dicetak justru berhimpit;−6/5≠1/2.KunciC tetap benar dari koefisien.','Tulis2/4=(−3)/(−6)=1/2≠−12/10=−6/5;atau gunakan dua kali garisA berkonstanta−24≠10.')]),
 (9,2,5): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='INCORRECT',conditional_correct_ids=[dict(condition='Menyamakan dua ekspresiy disebut substitusi secara konvensi sekolah',ids=['B']),dict(condition='Eliminasi y dengan mengurangkan kedua persamaan apa adanya diizinkan',ids=['A','B'])],issues=[issue('explanation','Pembahasan mengklaim eliminasi harus menata ke bentuk35000x−y−100000 dan45000x−y−20000.','Pengurangan langsung y−y=−10000x+80000 mengeliminasi y tanpa bentuk baku;A danB sama hasilx8.','Tanyakan nama proses substitusiy pada persamaan kedua;atau ubahA sehingga salah tanpa membatasi eliminasi secara keliru.')]),
 (9,2,7): dict(explanation_status='INCORRECT',issues=[issue('explanation','B menyebut konstanta berbeda kemudian mencetak(6=12).','6=12 salah secara eksplisit;kesimpulan sejajar dankeyABC benar.','Ganti dengan6≠12 dan tulis transformasi persamaan2/2 lengkap.')]),
 (9,3,1): dict(issues=[issue('context','DuaPaketA menghasilkan6 gantungan dan4 stiker,sedangkan kebutuhan5 dan5.','Selisih biaya45000 vs46000 dapat dihitung,tetapi duaPaketA tidak memenuhi kebutuhan stiker;tidak menjadi alternatif pengadaan yang layak.','Nyatakan perbandingan hanya nominal harga,atau pilih kombinasi paket yang memenuhi kebutuhan dan hitung ulang.')]),
 (9,3,4): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='INCORRECT',conditional_correct_ids=[dict(condition='Penggantian variabel eksplisit dijadikan metode yang diminta',ids=['A']),dict(condition='Eliminasi langsung tanpa bentuk baku juga dinilai memenuhi kriteria',ids=['A','B'])],issues=[issue('explanation','Eliminasi dinyatakan memerlukan pengubahan menjadi3x−y5.','B dapat mengalikan persamaan1 dengan5,lalu mengurangkannya dari2x+5y43 untuk17x68 tanpa bentuk baku.','Tanyakan langkah substitusi langsung;atau gantiB dengan langkah eliminasi yang salah,bukan mengklaim perubahan bentuk wajib.')]),
 (9,3,7): dict(explanation_status='INCORRECT',issues=[issue('explanation','30x+20y130000 dikatakan dibagi10000 menjadi3x+2y13;20x+40y140000 dikatakan dibagi20 menjadix+2y7.','Pembagian benar berturut-turut(3/1000)x+(1/500)y13 danx+2y7000.Variabel didefinisikan rupiah,tiba-tiba diubah ribuan tanpa definisi.','Bagi persamaan1 dengan10,persamaan2 dengan20 untuk3x+2y13000,x+2y7000;atau definisikan ulang harga dalam ribuan secara eksplisit.')]),
 (9,4,1): dict(validity='INVALID',answer_status='INCORRECT',issues=[issue('options','A=Rp18000,C=Rp18000 ditambah revisi8000+2(5000)=18000.','PG memiliki dua jawaban benarA,C;kunci tunggalC tidak lengkap.','Pertahankan satu18000;ganti opsi duplikat dengan nilai salah dan hapus catatan revisi.')]),
 (9,5,1): dict(validity='INVALID',answer_status='INCORRECT',issues=[issue('options','A danB sama-sama menyatakan pengunjung salah,harga sepeda air20000 dan komidi12500.','PG memiliki dua jawaban benarA,B;kunciB tidak unik.','Ganti salah satu duplikat dengan harga atau evaluasi yang salah.')]),
 (9,5,2): dict(answer_status='INCORRECT',explanation_status='INCORRECT',issues=[issue('key','KunciC menuntut kembali3000;solusi l2500,k4000 memberi pesanan17000 dan kembali1000.','Jawaban benarD;C salah.','Ganti kunciD.'),issue('explanation','5000+12000 ditulis15000,lalu18000−15000=3000.','Kesalahan penjumlahan mengubah total belanja dan kembalian.','Tulis5000+12000=17000;18000−17000=1000.')]),
 (9,5,4): dict(explanation_status='INCORRECT',issues=[issue('explanation','Eliminasi dinyatakan harus mengubahy3x−2 menjadi−3x+y−2 terlebih dahulu.','Tidak wajib:kalikan persamaan1 dengan5,lalu kurangkan langsung dari persamaan2 menghasilkan17x34.Hasil substitusi/keyA benar.','Tulis substitusi merupakan pilihan langsung karena y terisolasi;hapus keharusan bentuk baku dan klaim tepat2 langkah tanpa konvensi hitungan.')]),
 (9,5,5): dict(validity='INVALID',answer_status='INCORRECT',explanation_status='INCORRECT',conditional_correct_ids=[dict(condition='RevisiC diterapkan menyeluruh:awalBenar diubahSalah;opsi lainnya tetap',ids=['C']),dict(condition='Narasi akhir mengubahA menjadiSalah karena77 secara nyata',ids=['A'])],issues=[issue('options','C dimulaiBenar denganluas77 lalu catatan revisi mengatakan klaim80SALAH;A masih menyatakan luas72.','Tidak ada opsi lengkap konsisten yang sesuai hasil77;memilih versiC atauA diam-diam mengubah naskah.','Tetapkan satu versi final;buat satu opsiSalah,karena luas77m².'),issue('key','MetadataC;akhir pembahasan menyebutKunci Jawaban disesuaikan keA.','Dua kunci berbeda dalam satu sumber;A yang ada salah danC kontradiktif.','Sesuaikan satu kunci hanya setelah satu opsi final valid dipasang.'),issue('explanation','Perhitunganp11,l7,luas77 benar,tetapi instruksi penyesuaian kunciA menunjuk opsi72 yang salah.','Kesimpulan akademik benar tidak menyelesaikan konflik versi/kunci.','Hapus catatan revisi,ulang pembahasan final77 dengan opsi/key yang konsisten.'),issue('formatting','Paragraf4552–4564 mengulang bentuk teks+LaTeX+teks,termasuk36 meter36\\text{ meter}36 meter.','Besaran dan persamaan sulit dibaca;jejak edit bocor ke soal.','Sisakan satu representasi setiap besaran/persamaan.')]),
 (9,5,7): dict(validity='UNCERTAIN',answer_status='UNCERTAIN',explanation_status='UNCERTAIN',conditional_correct_ids=[dict(condition='Harga satuan kedua toko sama DAN tiap unit data berarti satu pasang',ids=['B','D'])],issues=[issue('stem','Data berasal dariTokoMaju danTokoJaya tanpa pernyataan harga satuan sama;data hanya menyebutkaus kaki/sarung tangan,opsi menyebut1pasang.','Ada empat harga toko yang independen,dua persamaan saja;harga12500/15000 tidak teridentifikasi tanpa asumsi tambahan,unitpasang juga tidak pasti.','Nyatakan harga satuan sama di kedua toko dan semua jumlah dihitung perpasang;atau gunakan satu toko yang sama.')]),
 (9,5,10): dict(explanation_status='INCORRECT',issues=[issue('explanation','Eliminasi dinyatakan membutuhkan pengubahan menjadi x+0y4.','Eliminasi dapat langsung(2x+y)−2x=11−8,y3;menulis0y tidak wajib.Kunci1,2 tetap wajar.','Pertahankan substitusi langsung sebagai pilihan sederhana;hapus klaim pengubahan bentuk0y wajib dan definisikan cara menghitung langkah bila diuji.')]),
}


def source_projection(e):
    """Keep parser evidence separately; recover only explicit source boundaries."""
    stem, options, explanation = e['stem'], list(e['options']), e['explanation']
    fixes = []
    ps = e['paragraphs']
    if explanation is None:
        start = next((j for j,p in enumerate(ps) if p['text'].strip().upper().startswith('PEMBAHASAN')), None)
        if start is not None:
            end = next((j for j in range(start+1,len(ps)) if ps[j]['text'].strip().lower().startswith('kesalahan umum')), len(ps))
            explanation = '\n'.join(p['text'].strip() for p in ps[start:end] if p['text'].strip())
            stem = stem.split('PEMBAHASAN',1)[0].strip()
            options = [v.split('PEMBAHASAN',1)[0].strip() for v in options]
            fixes.append(dict(kind='explicit_explanation_boundary',paragraph_index=ps[start]['paragraph_index'],evidence=ps[start]['text']))
    if (e['indicator'],e['level'],e['source_number']) == (8,3,6):
        options = [re.sub(r'^\[\s*\]\s*[A-D]\.\s*','',p['text'].strip()) for p in ps if re.match(r'^\[\s*\]\s*[A-D]\.\s*',p['text'].strip())]
        head = [p for p in ps if 2946<=p['paragraph_index']<=2951]
        stem = '\n'.join(((p['native_label']+' ') if p['native_label'] else '')+p['text'] for p in head)
        fixes.append(dict(kind='explicit_answer_labels_not_numbered_stimuli',paragraphs=[2952,2953,2954,2955]))
    # Category key rows are retained in raw paragraphs, separated from stimulus.
    stem = re.sub(r'^(?:\([abc]\)\s+(?:BENAR|SALAH)\s*)+','',stem).strip()
    return dict(stem=stem,options=options,key=e['key'],declared_key_texts=e['declared_key_texts'],explanation=explanation,notes=e['additional_notes'],format=e['format'],category_labels=e['category_labels'],projection_adjustments=fixes,
                paragraphs=ps,tables=e['tables'])


def math_notation(text):
    # Expand only the manual review's compact assignments, never source text.
    text=re.sub(r'(?<![A-Za-z_])([xyplmnthkvrscSabd])(?=\d)',r'\1=',text)
    return re.sub(r'(?<![A-Za-z0-9_])([xyk])−(\d+)(?=\s+(?:memberi|dengan))',r'\1=−\2',text)


def build():
    es = [e for e in source_entries(ROOT/'docs/sources/incoming/2026-10-19-indikator-6-10') if e['indicator'] in (8,9)]
    assert len(es)==100 and len(REVIEWS)==100
    entries=[]
    for e in es:
        k=e['indicator'],e['level'],e['source_number']; r=REVIEWS[k]; projection=source_projection(e)
        ids=[str(j+1) if e['format']=='KATEGORI' else chr(65+j) for j in range(len(projection['options']))]
        assert len(ids)==len(r['truths']),k
        evaluation=[dict(id=oid,text=option,truth={'T':'TRUE','F':'FALSE','U':'UNCERTAIN'}[truth],reason=math_notation(reason)) for oid,option,truth,reason in zip(ids,projection['options'],r['truths'],r['reasons'])]
        correct=None if 'U' in r['truths'] else [o['id'] for o in evaluation if o['truth']=='TRUE']
        override=OVERRIDES.get(k,{})
        issues=override.get('issues',[])
        answer_status=override.get('answer_status','MISSING' if e['key'] is None else 'CORRECT' if correct is not None and set(correct)==set(e['key']) else 'UNCERTAIN' if correct is None else 'INCORRECT')
        explanation_status=override.get('explanation_status','CORRECT' if projection['explanation'] else 'MISSING')
        # Item solvability, declared-key correctness, and explanation correctness
        # are independent axes; a wrong key/explanation does not invalidate a
        # uniquely answerable stimulus with complete, unambiguous options.
        validity=override.get('validity','VALID')
        if k==(9,5,5): correct=None
        entries.append(dict(audit_id=e['audit_id'],indicator=e['indicator'],level=e['level'],source_number=e['source_number'],source_location=e['source'],source_projection=projection,
            parsed_source_key=e['key'],resolved_declared_key=e['key'] if k!=(9,5,5) else None,
            declared_key_candidates=[e['key']] if k!=(9,5,5) else [['C'],['A']],
            independent_solution=math_notation(r['solution']),option_evaluation=evaluation,independently_correct_ids=correct,conditional_correct_ids=override.get('conditional_correct_ids',[]),
            validity=validity,answer_status=answer_status,explanation_status=explanation_status,
            explanation_audit=dict(source_text=projection['explanation'],independently_checked_steps=math_notation(r['solution']).split('. '),option_claim_checks=[dict(id=o['id'],reason=o['reason']) for o in evaluation],
                discrepancies=[i for i in issues if i['component'] in ('explanation','classification','key')]),
            issues=issues,recommendation='Pertahankan soal,opsi,kunci,pembahasan.' if not issues else ' '.join(i['proposal'] for i in issues)))
    summary=dict(total=len(entries),by_indicator={str(i):sum(e['indicator']==i for e in entries) for i in (8,9)},validity=dict(Counter(e['validity'] for e in entries)),answer_status=dict(Counter(e['answer_status'] for e in entries)),explanation_status=dict(Counter(e['explanation_status'] for e in entries)),with_issues=sum(bool(e['issues']) for e in entries))
    return dict(schema_version=1,scope='100 original source questions;indicators8–9,levels1–5,10 questions per level',method='Independent derivations from stimulus;every option and source explanation compared afterward.No bank,generated variant,old review,or source key used as solving oracle.Native DOCX paragraphs and all category tables retained;corrupt equations/matrices and incompatible revisions remain conditional.',linear_definition='Linear nondegenerate:after simplification ax+b⋚0 or ax+b=0 witha≠0.Identity naming flagged conditional.',summary=summary,entries=entries)


def verify(data):
    entries=data['entries']
    assert len(entries)==100 and len({e['audit_id'] for e in entries})==100
    assert Counter((e['indicator'],e['level']) for e in entries)=={(i,l):10 for i in (8,9) for l in range(1,6)}
    for e in entries:
        assert len(e['source_projection']['options'])==len(e['option_evaluation'])>=3
        assert e['source_projection']['paragraphs'] and e['independent_solution'] and e['source_projection']['explanation']
        assert all(o['text'] and o['reason'] and o['truth'] in ('TRUE','FALSE','UNCERTAIN') for o in e['option_evaluation'])
        assert e['validity'] in ('VALID','INVALID','UNCERTAIN')
        if e['independently_correct_ids'] is not None:
            assert e['independently_correct_ids']==[o['id'] for o in e['option_evaluation'] if o['truth']=='TRUE']
        if any(o['truth']=='UNCERTAIN' for o in e['option_evaluation']): assert e['independently_correct_ids'] is None
    # Arithmetic checks exercise the corrected results and actual constraints.
    assert F(200000-50000,12000)==F(25,2)
    assert F(650-70,25)==F(116,5) and 25*23+70<=650<25*24+70
    assert F(350-130,15)==F(44,3) and 15*14+130<=350<15*15+130
    assert 2*2500+3*4000==17000 and 18000-17000==1000
    assert 4*2500+3*4000==22000 and 2*2500+5*4000==25000
    x,y=F(260000,11),F(230000,11)
    assert 2*x+3*y==110000 and 5*x+2*y==160000
    assert 11+7==18 and 11-7==4 and 11*7==77
    assert 2*20000+3*10000==70000 and 4*15000+5000==65000
    assert {e['source_number'] for e in entries if e['indicator']==8 and e['level']==3}==set(range(1,11))


if __name__=='__main__':
    data=build();verify(data)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data['summary'],ensure_ascii=False))
