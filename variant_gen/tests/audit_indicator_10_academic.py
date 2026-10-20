"""Independent academic review, indicator 10. Only writes its own part-10.json.

Run: python variant_gen/tests/audit_indicator_10_academic.py
Manual derivations below precede comparison with source keys/explanations.
No generator, bank, prior review, database or runtime imports.
"""
import itertools
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

from audit_original_questions import ROOT, source_entries

REVIEWS = {}


def review(level, number, truth, steps, reasons, domain='Identitas polinomial atas bilangan real; evaluasi opsi sebagai identitas, bukan kebetulan pada satu nilai.'):
    REVIEWS[level, number] = dict(truth=truth, steps=steps, reasons=reasons, domain=domain)


review(1, 1, 'TFFF', [
    'Biaya bruto = 3(2x+5000)+2(x-1000) = 6x+15000+2x-2000 = 8x+13000 rupiah.',
    'Biaya bersih = (8x+13000)-(x-3000) = (8-1)x+13000+3000 = 7x+16000 rupiah.'
], [
    'Sama persis dengan 7x+16000.', 'Konstanta 10000 berbeda dari 16000; selisih -6000.',
    '8x+13000 adalah biaya sebelum diskon, belum mengurangkan x-3000.',
    'Koefisien 8 salah; pengurangan diskon menurunkannya menjadi 7.'
], 'Untuk harga dan potongan nonnegatif, x>=3000. Identitas biaya berlaku pada seluruh domain itu; tidak perlu menentukan x.')

review(1, 2, 'FFTF', [
    '(x+7)(x-2)=x^2+(-2+7)x-14=x^2+5x-14.',
    'Lebar = (x^2+5x-14)/(x+7)=x-2; keliling = 2((x+7)+(x-2)) = 4x+10 m.'
], ['2x+5 adalah panjang+lebar, bukan dua kalinya.', '4x+5 salah pada konstanta; 2(5)=10.',
    'Sesuai 2(2x+5)=4x+10.', 'Konstanta 18 tidak sama dengan 10.'
], 'Ukuran panjang dan lebar harus positif: x>2. Notasi opsi 4x+10m dibaca (4x+10) m, sesuai konteks ukuran.')

review(1, 3, 'TFFF', [
    'Formasi baru = 2(3a-2b)+3(2a+5b) = 6a-4b+6a+15b.',
    'Gabung koefisien: (6+6)a+(-4+15)b=12a+11b.'
], ['Koefisien a=12 dan b=11 benar.', 'Koefisien b seharusnya -4+15=11, bukan19.',
    'Koefisien a seharusnya 6+6=12, bukan10.', 'Kedua koefisien 10 dan19 berbeda dari12 dan11.'
], 'Jumlah orang harus bilangan bulat nonnegatif; identitas berlaku untuk semua a,b yang menghasilkan jumlah demikian. Model mengikuti instruksi 2 kali ditambah3 kali, tanpa asumsi anggota tumpang tindih.')

review(1, 4, 'FFTF', [
    '5x^2-3xy+4y-2x^2+7xy-9 = (5-2)x^2+(-3+7)xy+4y-9.',
    'Bentuk sederhana = 3x^2+4xy+4y-9; koefisien xy=4.'
], ['-3 hanya salah satu koefisien sebelum penggabungan.', '3 adalah koefisien x^2, bukan xy.',
    '-3+7=4 benar.', '7 belum digabungkan dengan -3.'])

review(1, 5, 'TFFF', [
    '4(2x-3)-2(x-5)=8x-12-2x+10=(8-2)x+(-12+10)=6x-2.'
], ['Rian benar: hasilnya 6x-2.', 'Sinta salah: konstanta -22 berbeda dari-2.',
    'Rian tidak salah dan konstanta +2 juga salah.', 'Koefisien 10 dan konstanta -22 keduanya salah.'])

review(1, 6, 'TTTF', [
    '(2x-3)^2 = 4x^2-12x+9.', 'x^2-16=(x-4)(x+4).',
    '(x-3)(x-4)=x^2-7x+12.', '(3x+2)(x-5)=3x^2-15x+2x-10=3x^2-13x-10.'
], ['Suku silang 2(2x)(-3)=-12x.', 'Selisih kuadrat x^2-4^2.',
    'Jumlah akar faktor -3-4=-7; hasil kali12.', 'Koefisien x=-15+2=-13, bukan-17.'])

review(1, 7, 'TTTF', [
    'Senin=3(2p+4q)=6p+12q; tambahan Selasa=2(p-3q)=2p-6q.',
    'Perubahan kumulatif sampai Selasa=(6p+12q)+(2p-6q)=8p+6q.',
    'Setelah penjualan Rabu=(8p+6q)-(4p-2q)=4p+8q; koefisien q=8.'
], ['Distributif memberi 6p+12q.', 'Jumlah kedua kiriman=8p+6q.',
    'Kurang 4p-2q memberi -4p+2q, hasil4p+8q.', 'Koefisien q=8, bukan4.'
], 'Perhitungan adalah perubahan persediaan yang dicatat, bukan stok awal tak diketahui. Jika benar-benar total stok, perlu stok awal0. Jika p,q melambangkan jenis buku/pensil, koefisien negatif -6q dan -2q tidak cocok dengan kata menerima/terjual untuk kedua jenis secara terpisah; model formal berbeda dari narasi stok.')

review(1, 8, 'TTTT', [
    '3(x^2-2x+4)-2(2x^2-3x-1)=3x^2-6x+12-4x^2+6x+2.',
    'Gabung suku: (3-4)x^2+(-6+6)x+(12+2)=-x^2+14=14-x^2.'
], ['Hasilnya -x^2+14.', 'Koefisien linear -6+6=0.', 'Konstanta12+2=14.', 'Komutatif penjumlahan memberi14-x^2.'])

review(1, 9, 'TTT', [
    'Luas kebun=(2x+3)^2=4x^2+12x+9 m^2.',
    'Luas kolam=(x-1)^2=x^2-2x+1 m^2.',
    'Luas rumput=(4x^2+12x+9)-(x^2-2x+1)=3x^2+14x+8 m^2.'
], ['Kuadrat sisi kebun benar.', 'Kuadrat sisi kolam benar.', 'Pengurangan memberi koefisien3,14,8.'
], 'Kebun dan kolam bersisi positif serta kolam termuat: x>1, dan2x+3>x-1 pada domain ini.')

review(1, 10, 'TTT', [
    '3xy(2x-3y)=6x^2y-9xy^2.',
    '(6x^2y-9xy^2)/(3xy)=2x-3y karena3xy tidak nol.',
    'Pada x=3,y=1: 2(3)-3(1)=3; langsung pembilang=54-27=27, penyebut9, hasil3.'
], ['Ekspansi faktor3xy benar.', 'Pembatalan faktor dibenarkan oleh x,y!=0.', '27/9=3 tepat.'
], 'x!=0 dan y!=0 dinyatakan eksplisit; pembatalan hanya pada domain itu.')

review(2, 1, 'TFFF', [
    'Pembelian=4(3x+10000)+3(2x-5000)=12x+40000+6x-15000=18x+25000.',
    'Bayar=(18x+25000)-(2x-4000)=16x+29000 rupiah.'
], ['16x+29000 cocok.', 'Konstanta21000 salah: mengurangkan -4000 harus menambah4000.',
    'Koefisien18 belum dikurangi diskon2x.', 'Koefisien18 dan konstanta21000 salah.'
], 'Harga spidol nonnegatif mensyaratkan x>=2500; diskon nonnegatif x>=2000. Domain gabungan x>=2500.')

review(2, 2, 'FFTF', [
    '(2x-3)(x+5)=2x^2+10x-3x-15=2x^2+7x-15.',
    'Lebar=x+5; keliling=2((2x-3)+(x+5))=2(3x+2)=6x+4 m.'
], ['3x+2 adalah setengah keliling.', 'Konstanta2 belum dikali2.', '2(3x+2)=6x+4.', 'Konstanta8 bukan4.'
], 'Panjang2x-3>0 dan lebarx+5>0 memberi x>3/2. Opsi6x+4m dibaca(6x+4) m.')

review(2, 3, 'TFFF', [
    'Luas tambahan=2(2x^2+3xy-5)=4x^2+6xy-10; utama=3(x^2-2xy+4)=3x^2-6xy+12.',
    'Tambahan dikurangi utama=(4-3)x^2+(6+6)xy-10-12=x^2+12xy-22 m^2.'
], ['Cocok dengan pengurangan terarah tambahan-utama.', 'Menghilangkan12xy secara keliru.',
    'Menjumlahkan koefisien kuadrat menjadi7 dan menghilangkan12xy.', 'Koefisien kuadrat seharusnya4-3=1, bukan7.'
], 'Istilah tambahan terhadap utama dibaca pengurangan terarah tambahan-utama. Jika dimaksud besar selisih, hasilnya |x^2+12xy-22| dan perlu urutan luas. Nilai variabel harus memberi kedua luas positif.')

review(2, 4, 'TFFF', [
    '5(2a-b)-3(a-2b)=10a-5b-3a+6b=(10-3)a+(-5+6)b=7a+b.'
], ['Andi benar karena7a+b.', 'Budi memberi-11b, padahal-5b+6b=b.',
    'Andi benar; tanda-b juga salah.', '13a-11b salah pada kedua koefisien.'])

review(2, 5, 'TFFF', [
    '(2x+a)(x-3)=2x^2+(a-6)x-3a.',
    'Tambah3x^2-5x+4 memberi5x^2+(a-11)x+(4-3a).',
    'Kesetaraan koefisien: a-11=-7 memberi a=4; konstanta4-3a=-8 juga memberi a=4.'
], ['a=4 memenuhi kedua persamaan koefisien.', 'a=3 memberi koefisien-8 dan konstanta-5.',
    'a=2 memberi koefisien-9 dan konstanta-2.', 'a=-4 memberi koefisien-15 dan konstanta16.'])

review(2, 6, 'TTTF', [
    '(3x-4)^2=9x^2-24x+16.', '(2x-5)(2x+5)=4x^2-25.',
    '(x+8)(x-3)=x^2+5x-24.', '(2x+1)(x-4)=2x^2-8x+x-4=2x^2-7x-4.'
], ['Suku silang-24x benar.', 'Selisih kuadrat(2x)^2-5^2.', '8-3=5 dan8(-3)=-24.', 'Koefisien linear-7, bukan-9.'])

review(2, 7, 'TTTF', [
    'A=2(3x^2-4x+5)=6x^2-8x+10; B=3(x^2+2x-1)=3x^2+6x-3.',
    'A+B=9x^2-2x+7.', 'A-B=3x^2-14x+13.'
], ['Penjumlahan memberi9x^2-2x+7.', 'Pengurangan memberi3x^2-14x+13.',
    'Koefisien x pada jumlah=-8+6=-2.', 'Konstanta selisih=10-(-3)=13, bukan7.'])

review(2, 8, 'TTTF', [
    '8x^2y+12xy^2=4xy(2x+3y).',
    'Bagi4xy yang tidak nol: hasil2x+3y; pada(2,3), 4+9=13.'
], ['4xy(2x+3y) mengembang ke pembilang.', 'Faktor4xy boleh dibagi karena x,y!=0.',
    '2(2)+3(3)=13.', 'Koefisien x=2, sedangkan3 koefisien y.'
], 'x!=0,y!=0 eksplisit. Substitusi2,3 berada dalam domain.')

review(2, 9, 'TTT', [
    '(3x-2)(x+4)=3x^2+12x-2x-8=3x^2+10x-8.',
    'Panjang=3x-2; keliling=2((3x-2)+(x+4))=8x+4 m.',
    'Pada x=5, panjang13 m, lebar9 m, keliling2(13+9)=44 m.'
], ['Pembagian luas oleh lebar memberi3x-2.', 'Rumus keliling memberi8x+4.', 'Nilai44 m benar.'
], 'Dimensi positif: x>2/3, sehingga x+4!=0; x=5 sah.')

review(2, 10, 'TTT', [
    'Bentuk1=2(x-3)(x+4)=2(x^2+x-12)=2x^2+2x-24=Bentuk2.',
    '2(x-3)=2x-6; Bentuk1=(2x-6)(x+4)=Bentuk3.',
    'Ketiga bentuk mempunyai polinom2x^2+2x-24, sehingga ekuivalen untuk semua real x.'
], ['Bentuk1 dan2 sama sebagai polinom.', 'Bentuk1 dan3 sama oleh distributif.', 'Kesamaan1=2 dan1=3 memberi ketiganya sama.'])

review(3, 1, 'TFFF', [
    'P=4x^2-8x+12; Q=4x^2-10x-2.',
    'P-Q=(4-4)x^2+(-8+10)x+(12+2)=2x+14, berderajat1.'
], ['Suku kuadrat habis;2x+14 benar.', '8x^2-18x+10 merupakan P+Q, bukanP-Q.',
    'Konstanta Q=-2;12-(-2)=14, bukan10.', 'Koefisien kuadrat setelah pengurangan0, bukan4.'])

review(3, 2, 'TFFF', [
    '(2x+5)(3x-2)=6x^2+11x-10, sesuai luas.',
    'K(x)=2((2x+5)+(3x-2))=10x+6 m.',
    'K(x+2)=10x+26 m; K(x+2)-K(x)=20 m, bebas x.'
], ['Kenaikan20 m sama dengan10 kali kenaikan parameter2.', '10 m adalah perubahan jika parameter naik1.',
    'Koefisien keliling10, sehingga perubahan bukan12.', 'Selisih konstan20, tanpa suku x^2.'
], 'Dimensi positif x>2/3. Karena panjang ditulis(2x+5)m dan(3x-2)m, x adalah parameter numerik; frase x bertambah2 meter tidak konsisten satuan. Perhitungan opsi membutuhkan x bertambah2 unit.')

review(3, 3, 'TFFF', [
    '(3x-m)(2x+4)=6x^2+(12-2m)x-4m.',
    '-4m=-20 memberi m=5; n=12-2m=2.',
    'm^2-n^2=25-4=21.'
], ['25-4=21.', '16 tidak sama dengan21.', '9 tidak sama dengan21.', '5 adalah m, bukan m^2-n^2.'])

review(3, 4, 'TFFF', [
    '(12x^2-18xy)/(-6x)=-2x+3y, sebab(-18xy)/(-6x)=+3y.',
    '2(x-3y)=2x-6y; jumlah=(-2x+3y)+(2x-6y)=-3y.',
    'Langkah1 Eko salah tanda; langkah2 benar; langkah3 menjumlahkan hasil salah secara konsisten tetapi bukan hasil ekspresi asal.'
], ['Lokasi kesalahan dan hasil-3y benar.', '2(x-3y)=2x-6y, bukan2x-3y.',
    'Langkah1 tidak tepat; hasil Eko-9y salah.', '-2x+2x=0, bukan4x.'
], 'Domain alami pecahan x!=0; y bebas real. Tidak menganggap hasil-3y memperluas domain asal ke x=0.')

review(3, 5, 'TFFF', [
    'Keliling persegi=4(3x-1)=12x-4 m.',
    'Keliling persegi panjang=2((4x+1)+(2x-3))=2(6x-2)=12x-4 m.',
    'Selisih kedua keliling0 untuk setiap x>3/2.'
], ['Keduanya identik12x-4 pada domain soal.', 'Selisih0, bukan kebun lebih panjang.',
    'Selisih0, bukan lapangan lebih panjang4 m.', 'Selalu sama pada x>3/2; x=0 bahkan di luar domain.'
], 'x>1,5 eksplisit dan menjamin semua sisi positif. Kata setiap x pada opsiA diwarisi batas domain soal.')

review(3, 6, 'TTTT', [
    'P=(2x-3)(x+4)=2x^2+8x-3x-12=2x^2+5x-12=Q.',
    'Koefisien Q: kuadrat2, linear5, konstanta-12.',
    'P(2)=(4-3)(2+4)=6; P-Q identik0 untuk seluruh real x.'
], ['EkspansiP sama denganQ.', 'Koefisien2,5 dan konstanta-12 sesuai.', 'P(2)=1 kali6=6.', 'Polinom P-Q semua koefisiennya0.'])

review(3, 7, 'TTTF', [
    '3x^2-10x-8=3x^2-12x+2x-8=3x(x-4)+2(x-4)=(3x+2)(x-4).',
    'Pada x=4: 48-40-8=0.', '(3x-2)(x+4)=3x^2+10x-8, berbeda tanda koefisien linear.'
], ['Ekspansi faktor memberi3x^2-10x-8.', 'x-4 adalah faktor eksplisit.', '48-40-8=0.', 'Faktor yang ditawarkan memberi+10x, bukan-10x.'])

review(3, 8, 'TTTF', [
    'A=4(x-2y)+3(2x+y)=4x-8y+6x+3y=10x-5y.',
    'B=2(5x-(5/2)y)=10x-5y; jadi A-B=0.'
], ['KoefisienA: x=10,y=-5.', 'B juga10x-5y.', 'A-B=(10-10)x+(-5+5)y=0.', 'Koefisien y=-5, bukan+5.'
], 'Desimal Indonesia2,5 dibaca5/2 tepat; x,y real. Untuk stok nyata perlu hasil nonnegatif, tetapi identitas tidak bergantung pada stok tertentu.')

review(3, 9, 'TTT', [
    '(x-2)^2=x^2-4x+4.',
    '2x(x-3)-(x-2)^2=2x^2-6x-(x^2-4x+4)=x^2-2x-4.',
    'Pada x=3: 9-6-4=-1; langsung2(3)(0)-(1)^2=-1.'
], ['Kuadrat binomial benar.', 'Tanda minus pada kurung memberi+4x-4.', 'Substitusi menghasilkan-1.'])

review(3, 10, 'TTT', [
    'LuasA=(3x+2)(x-1)=3x^2-x-2 m^2.',
    'LuasB=(1/2)(2x+4)(3x-3)=(x+2)(3x-3)=3x^2+3x-6 m^2.',
    'LuasB-LuasA=(3x^2+3x-6)-(3x^2-x-2)=4x-4 m^2.'
], ['Produk sisiA memberi3x^2-x-2.', 'Setengah alas kali tinggi memberi3x^2+3x-6.', 'Pengurangan memberi4x-4.'
], 'Semua panjang positif mengharuskan x>1; pada domain ituB-A=4x-4>0 sehingga selisih juga merupakan besar selisih.')

review(4, 1, 'FTFF', [
    'p=3x+5,l=2x-1; p+l=5x+4.',
    'K=2(p+l)=2(5x+4)=10x+8 m.'
], ['5x+4 hanya setengah keliling.', '10x+8 m benar.',
    '6x^2-5 bukan keliling; hasil p*l pun6x^2+7x-5.', 'Konstanta2(5-1)=8, bukan4.'
], 'Panjang dan lebar positif: x>1/2. Pembahasan asli ada di paragraf5303-5313 meskipun parser memasukkannya ke opsiD.')

review(4, 2, 'TFTF', [
    'A=4(2a-b+3)=8a-4b+12; B=3(a+2b-1)=3a+6b-3.',
    'A-B=(8-3)a+(-4-6)b+(12+3)=5a-10b+15.',
    'OpsiA danC memiliki polinom yang identik5a-10b+15; keterangan revisi padaC tidak mengubah nilai.'
], ['Benar untuk pengurangan A-B; identik denganC.', '11a+2b+9 adalah A+B, bukanA-B.',
    'Benar untuk pengurangan A-B; duplikat matematisA.', 'Koefisienb pada A-B=-4-6=-10, bukan+2.'
], 'Frase selisih antara tidak menyebut arah atau A>=B. PenguranganA-B menghasilkan opsiA,C; besar selisih adalah|5a-10b+15|. Contoh a=1,b=3: A=8,B=18, A-B=-10 tetapi besar selisih10. Tidak ada satu kunci PG unik bahkan pada pembacaanA-B.')

review(4, 3, 'TFFF', [
    '6(-10)=-60; pasangan-15,4 berjumlah-11.',
    '6x^2-11x-10=6x^2-15x+4x-10=3x(2x-5)+2(2x-5)=(2x-5)(3x+2).',
    'AlternatifB=6x^2-4x-10; C=6x^2+11x-10; D=6x^2+7x-10.'
], ['ProdukA=6x^2-11x-10.', 'ProdukB berkoefisien linear-4, bukan-11.',
    'ProdukC berkoefisien linear+11, bukan-11.', 'ProdukD berkoefisien linear+7, bukan-11.'])

review(4, 4, 'FFFT', [
    '4x^2-9=(2x-3)(2x+3); 2x^2+x-6=(2x-3)(x+2).',
    'Pada domain x!=3/2,-2, bagi faktor2x-3; tersisa(2x+3)/(x+2).',
    'Langkah1-3 sah pada domain asal; Langkah4 salah menyalin sisa pembilang menjadi2x-3.'
], ['Langkah1 sudah benar; (4x-3)(x+3)=4x^2+9x-9 salah.',
    'Langkah2 sudah benar; (2x+3)(x-2)=2x^2-x-6 salah.',
    'Faktor2x-3 boleh dibagi karena tidak nol dalam domain asal.',
    'Sisa pembilang2x+3 dan penyebutx+2; kesalahan ada padaLangkah4.'
], 'Domain asli x!=-2 dan x!=3/2. Bentuk sederhana tetap harus mempertahankan kedua pengecualian; x=3/2 adalah lubang yang tidak boleh diisi diam-diam.')

review(4, 5, 'FTFF', [
    'I=3(2x-4)+4(x+1)=6x-12+4x+4=10x-8.',
    'II=2(5x-4)=10x-8, sehingga ekuivalen untuk semua real x.'
], ['I bukan10x-16; penjumlahan konstanta-12+4=-8.', 'Andi benar karena keduanya10x-8.',
    'KonstantaI=-8, bukan+8.', 'Andi benar; kesamaan berlaku seluruh real x, bukan hanya0.'])

review(4, 6, 'TTTF', [
    'Suku-suku3x^2,-5xy,4y,-8 berjumlah4.',
    'Koefisien monomialxy=-5; suku konstan=-8.',
    'x^2 memiliki vektor pangkat(2,0); xy memiliki(1,1), sehingga tidak sejenis.'
], ['Ada4 suku tak nol.', 'Koefisienxy adalah-5.', 'Suku tanpa variabel=-8.', 'Kesamaan satu hurufx tidak cukup; vektor pangkat berbeda.'])

review(4, 7, 'TTFT', [
    '2(3x-2y)-3(x-4y)=6x-4y-3x+12y.',
    'Suku x=(6-3)x=3x; suku y=(-4+12)y=8y; hasil3x+8y.',
    'A,B,D benar; C salah karena-16y bukan+8y. Kunci awalB,D berbeda dari himpunan lengkapA,B,D.'
], ['Suku x=3x, jadiA benar meskipun kunci awal menghilangkannya.', 'Suku y=+8y.',
    '3x-16y salah: -3(-4y)=+12y.', 'Hasil akhir3x+8y tepat.'])

review(4, 8, 'TFTT', [
    '(i) (a-4)(a+4)=a^2-16.', '(ii) (x+3)^2=x^2+6x+9.',
    '(iii) (2x-1)(x+3)=2x^2+6x-x-3=2x^2+5x-3.',
    '(iv) (x-2)(x+3)=x^2+x-6, bukanx^2-5x+6; yang benar(x-2)(x-3).'
], ['(i) identitas selisih kuadrat.', '(iv) salah; konstanta-6 dan koefisien+1 berbeda dari+6 dan-5.',
    '(ii) kuadrat sempurna.', '(iii) koefisien linear6-1=5 dan konstanta-3.'])

review(4, 9, 'TFT', [
    'Rani=3x+2y, Dika=2x+4y; total=5x+6y.',
    'Rani-Dika=x-2y, bukanx+2y. Besar selisih|x-2y| juga bukan identitasx+2y.',
    'Pada x=5000,y=2000: Rani=15000+4000=19000 rupiah.'
], ['Jumlah koefisien buku5 dan pensil6.', 'Pengurangan koefisien pensil2-4=-2, bukan+2.',
    '3(5000)+2(2000)=19000.'
], 'Harga x,y nonnegatif. Hasil FALSE opsi2 tetap sama baik selisih terarah maupun besar selisih; contoh5000,2000 memberi selisih1000, bukan9000.')

review(4, 10, 'TTF', [
    'Penjumlahan real komutatif:3a+5b=5b+3a.',
    '4(2x-3y)=8x-12y; pengelompokan(2x*3y)*4z=2x*(3y*4z)=24xyz sah.',
    'Pengurangan tidak komutatif:5-3=2 tetapi3-5=-2; tidak asosiatif:(5-3)-1=1 tetapi5-(3-1)=3.'
], ['Komutatif berlaku pada penjumlahan.', 'Distributif4 kali masing-masing suku memberi8x-12y.',
    'Contoh5,3 menyangkal komutatif; contoh5,3,1 menyangkal asosiatif.'])

review(5, 1, 'FTFF', [
    '3(2x-5y)-2(x-4y)=6x-15y-2x+8y=4x-7y.',
    'SiswaX benar danY salah; koefisien y=-15+8=-7, koefisienx=6-2=4.'
], ['Mengganti+8y dengan-8y adalah kesalahan tanda.', 'AlasanB memberi-15y+8y=-7y tepat.',
    'Tanda negatif di luar kurung harus mendistribusi ke setiap suku.', 'Suku x=4x, bukan8x;X sudah benar.'])

review(5, 2, 'FFTF', [
    'F1=2(3a+4b)+3(a-2b)=6a+8b+3a-6b=9a+2b=F2.',
    'F3=3(3a+b)-b=9a+3b-b=9a+2b.',
    'F1=F2=F3 sebagai polinom dua variabel.'
], ['Kata saja salah karenaF3 juga ekuivalen.', 'Kata saja salah karenaF1 juga ekuivalen.',
    'Ketiganya memiliki koefisiena=9,b=2.', 'Ada kesetaraan ketiganya, bukan tidak ada.'])

review(5, 3, 'TFFF', [
    '(2x-3)^2=(2x)^2-2(2x)(3)+3^2=4x^2-12x+9.',
    '(2x-3)(2x+3)=4x^2-9; (4x-3)(x-3)=4x^2-15x+9.'
], ['Kuadrat sempurna tepat.', 'Selisih kuadrat tidak memiliki suku-12x dan konstantanya-9.',
    'ProdukC berkoefisien linear-15, bukan-12.', 'Konstanta positif tidak melarang pemfaktoran; faktor(2x-3)^2 eksplisit.'])

review(5, 4, 'FFFT', [
    'x^2-5x+6=(x-2)(x-3); x^2-9=(x-3)(x+3).',
    'Pada domain x!=3,-3, pembagian faktorx-3 memberi(x-2)/(x+3).',
    'Tidak boleh membatalkan suku x dari penjumlahan; contoh x=1 memberi(-1)/4=-1/4, berbeda dari-2/3.'
], ['Langkah1 benar; (x-1)(x-6)=x^2-7x+6 salah.',
    'Langkah2 benar; (x-3)^2=x^2-6x+9 salah.',
    'Langkah3 sah pada x!=3,-3 karena faktorx-3 tidak nol.',
    'Langkah4 salah: x merupakan suku, bukan faktor seluruh pembilang/penyebut.'
], 'Domain asal x!=3 dan x!=-3 wajib dipertahankan setelah pembatalan; bentuk sederhana tidak otomatis sah di x=3.')

review(5, 5, 'TFFF', [
    'U1=2x+3 dan beda=x-1; U2=3x+2.',
    'U3=U1+2(x-1)=2x+3+2x-2=4x+1.'
], ['Rumus dan penjabaranA benar.', '3x+2 adalahU2, bukanU3.', 'Konstanta3-2=1, bukan5.',
    'Kesimpulan benar tetapi alasan salah:3U1=6x+9, bukanU3=4x+1.'
], 'Banyak kursi bilangan bulat positif dan bertambah memerlukan beda x-1>0; misalnya x bilangan bulat>=2. Identitas U3 berlaku pada setiap x yang memenuhi hitungan kursi.')

review(5, 6, 'TTTF', [
    '5a-2b+3(a-4b)-(2a-5b)=5a-2b+3a-12b-2a+5b.',
    'Suku a=(5+3-2)a=6a; suku b=(-2-12+5)b=-9b; hasil6a-9b.'
], ['Kelompok a=5a+3a-2a tepat.', 'Koefisien b=-9.', 'Hasil6a-9b benar.', 'Koefisien a=6, bukan8.'])

review(5, 7, 'FTFT', [
    '(2x-3)(x+5)=2x^2+10x-3x-15=2x^2+7x-15.',
    '(2x-3)(x-5)=2x^2-10x-3x+15=2x^2-13x+15, bukan bentuk soal.',
    'Dalam urutan faktor(2x-3)(x+5), suku luar=2x*5=10x, suku dalam=(-3)*x=-3x; C menukarkan keduanya.',
    'B,D benar. Klaim pembahasan awal C & D Benar salah untukC; revisi akhirB,D benar.'
], ['ProdukA memberi-13x dan+15, bukan+7x dan-15.', 'ProdukB memberi2x^2+7x-15.',
    'Posisi dalam dan luar tertukar; dalam=-3x, luar=+10x.', 'EkspansiD sama dengan polinom soal.'])

review(5, 8, 'TFTT', [
    '(2x+3)^2=4x^2+12x+9; (2x-3)^2=4x^2-12x+9.',
    'P=(4x^2+12x+9)-(4x^2-12x+9)=24x=Q.',
    'Cek alternatif selisih kuadrat:((2x+3)-(2x-3))*((2x+3)+(2x-3))=6*4x=24x.'
], ['EkspansiA benar.', 'Konstanta kuadrat(-3)^2=+9, bukan-9.', 'Selisih=12x-(-12x)=24x.', 'P identikQ=24x.'])

review(5, 9, 'TFU', [
    'Stand1=2x^2+6x-8 rupiah; Stand2=3x^2-6x+6 rupiah.',
    'Total=5x^2+(6-6)x+(-8+6)=5x^2-2 rupiah; koefisienx=0.',
    'Pada x=3: Stand1=28 rupiah, Stand2=15 rupiah, total43 rupiah. Dalam ribuan rupiah, nilai ini43/1000 ribu rupiah, bukan43 ribu rupiah.'
], ['Jumlah kedua stand=5x^2-2.', 'Koefisienx=0, bukan+6.',
    'Angka43 benar dalam rupiah sesuai stimulus; frasa dalam ribuan menyiratkan43000 rupiah. Tidak ada dasar memilih salah satu satuan yang bertentangan.'
], 'Satuan stimulus eksplisit rupiah. Tidak diasumsikan ribuan rupiah. Opsi3 menggabungkan43 rupiah dan dalam ribuan; keputusan benar/salah memerlukan perbaikan satuan.')

review(5, 10, 'TTF', [
    '(x+y)^2=x^2+xy+yx+y^2=x^2+2xy+y^2; (x-y)^2=x^2-xy-yx+y^2=x^2-2xy+y^2.',
    '(x+y)(x-y)=x^2-xy+xy-y^2=x^2-y^2, identitas selisih kuadrat.',
    '(x-y)^2 tidak identikx^2-y^2; contohx=2,y=1 memberi1 sedangkan4-1=3. Selisih kedua ekspresi=2y(y-x).'
], ['Kedua rumus kuadrat benar sebagai identitas seluruh real.', 'IdentitasIII adalah selisih dua kuadrat.',
    'Kontracontoh(2,1) memberi1!=3; ekuivalensi universal salah meskipun bisa sama saat y=0 ataux=y.'])


# Exact finite-grid identity checks: every polynomial here has degree <=2 in
# each variable, so equality on a 3-point Cartesian grid proves its identity.
IDENTITIES = [
    ('3*(2*x+5000)+2*(x-1000)-(x-3000)', '7*x+16000'),
    ('(x+7)*(x-2)', 'x*x+5*x-14'),
    ('2*(3*a-2*b)+3*(2*a+5*b)', '12*a+11*b'),
    ('5*x*x-3*x*y+4*y-2*x*x+7*x*y-9', '3*x*x+4*x*y+4*y-9'),
    ('4*(2*x-3)-2*(x-5)', '6*x-2'),
    ('(2*x-3)**2', '4*x*x-12*x+9'), ('(x-4)*(x+4)', 'x*x-16'),
    ('(x-3)*(x-4)', 'x*x-7*x+12'), ('(3*x+2)*(x-5)', '3*x*x-13*x-10'),
    ('3*(2*p+4*q)+2*(p-3*q)-(4*p-2*q)', '4*p+8*q'),
    ('3*(x*x-2*x+4)-2*(2*x*x-3*x-1)', '-x*x+14'),
    ('(2*x+3)**2-(x-1)**2', '3*x*x+14*x+8'),
    ('3*x*y*(2*x-3*y)', '6*x*x*y-9*x*y*y'),
    ('4*(3*x+10000)+3*(2*x-5000)-(2*x-4000)', '16*x+29000'),
    ('(2*x-3)*(x+5)', '2*x*x+7*x-15'),
    ('2*(2*x*x+3*x*y-5)-3*(x*x-2*x*y+4)', 'x*x+12*x*y-22'),
    ('5*(2*a-b)-3*(a-2*b)', '7*a+b'),
    ('(2*x+a)*(x-3)+(3*x*x-5*x+4)', '5*x*x+(a-11)*x+4-3*a'),
    ('(3*x-4)**2', '9*x*x-24*x+16'), ('(2*x-5)*(2*x+5)', '4*x*x-25'),
    ('(x+8)*(x-3)', 'x*x+5*x-24'), ('(2*x+1)*(x-4)', '2*x*x-7*x-4'),
    ('2*(3*x*x-4*x+5)+3*(x*x+2*x-1)', '9*x*x-2*x+7'),
    ('2*(3*x*x-4*x+5)-3*(x*x+2*x-1)', '3*x*x-14*x+13'),
    ('4*x*y*(2*x+3*y)', '8*x*x*y+12*x*y*y'),
    ('(3*x-2)*(x+4)', '3*x*x+10*x-8'),
    ('2*(x-3)*(x+4)', '2*x*x+2*x-24'),
    ('(2*x-6)*(x+4)', '2*x*x+2*x-24'),
    ('4*(x*x-2*x+3)-2*(2*x*x-5*x-1)', '2*x+14'),
    ('(2*x+5)*(3*x-2)', '6*x*x+11*x-10'),
    ('(3*x-m)*(2*x+4)', '6*x*x+(12-2*m)*x-4*m'),
    ('(-6*x)*(-2*x+3*y)', '12*x*x-18*x*y'),
    ('(-2*x+3*y)+2*(x-3*y)', '-3*y'),
    ('4*(3*x-1)', '2*((4*x+1)+(2*x-3))'),
    ('(2*x-3)*(x+4)', '2*x*x+5*x-12'),
    ('(3*x+2)*(x-4)', '3*x*x-10*x-8'),
    ('(3*x-2)*(x+4)', '3*x*x+10*x-8'),
    ('4*(x-2*y)+3*(2*x+y)', '10*x-5*y'),
    ('2*(5*x-Fraction(5,2)*y)', '10*x-5*y'),
    ('2*x*(x-3)-(x-2)**2', 'x*x-2*x-4'),
    ('(3*x+2)*(x-1)', '3*x*x-x-2'),
    ('Fraction(1,2)*(2*x+4)*(3*x-3)', '3*x*x+3*x-6'),
    ('(3*x*x+3*x-6)-(3*x*x-x-2)', '4*x-4'),
    ('2*((3*x+5)+(2*x-1))', '10*x+8'),
    ('4*(2*a-b+3)-3*(a+2*b-1)', '5*a-10*b+15'),
    ('4*(2*a-b+3)+3*(a+2*b-1)', '11*a+2*b+9'),
    ('(2*x-5)*(3*x+2)', '6*x*x-11*x-10'),
    ('(3*x-5)*(2*x+2)', '6*x*x-4*x-10'),
    ('(2*x+5)*(3*x-2)', '6*x*x+11*x-10'),
    ('(6*x-5)*(x+2)', '6*x*x+7*x-10'),
    ('(2*x-3)*(2*x+3)', '4*x*x-9'),
    ('(2*x-3)*(x+2)', '2*x*x+x-6'),
    ('(4*x-3)*(x+3)', '4*x*x+9*x-9'),
    ('(2*x+3)*(x-2)', '2*x*x-x-6'),
    ('3*(2*x-4)+4*(x+1)', '2*(5*x-4)'),
    ('2*(3*x-2*y)-3*(x-4*y)', '3*x+8*y'),
    ('(a-4)*(a+4)', 'a*a-16'), ('(x+3)**2', 'x*x+6*x+9'),
    ('(2*x-1)*(x+3)', '2*x*x+5*x-3'),
    ('(x-2)*(x+3)', 'x*x+x-6'), ('(x-2)*(x-3)', 'x*x-5*x+6'),
    ('(3*x+2*y)+(2*x+4*y)', '5*x+6*y'),
    ('(3*x+2*y)-(2*x+4*y)', 'x-2*y'),
    ('4*(2*x-3*y)', '8*x-12*y'),
    ('3*(2*x-5*y)-2*(x-4*y)', '4*x-7*y'),
    ('2*(3*a+4*b)+3*(a-2*b)', '9*a+2*b'), ('3*(3*a+b)-b', '9*a+2*b'),
    ('(4*x-3)*(x-3)', '4*x*x-15*x+9'),
    ('(x-3)*(x+3)', 'x*x-9'), ('(x-1)*(x-6)', 'x*x-7*x+6'),
    ('(x-3)**2', 'x*x-6*x+9'), ('(2*x+3)+2*(x-1)', '4*x+1'),
    ('5*a-2*b+3*(a-4*b)-(2*a-5*b)', '6*a-9*b'),
    ('(2*x-3)*(x-5)', '2*x*x-13*x+15'),
    ('(2*x+3)**2-(2*x-3)**2', '24*x'),
    ('2*(x*x+3*x-4)+3*(x*x-2*x+2)', '5*x*x-2'),
    ('(x+y)**2', 'x*x+2*x*y+y*y'), ('(x-y)**2', 'x*x-2*x*y+y*y'),
    ('(x+y)*(x-y)', 'x*x-y*y'), ('(x-y)**2-(x*x-y*y)', '2*y*(y-x)'),
]


def check_math():
    evaluations = 0
    for left, right in IDENTITIES:
        variables = sorted(set(re.findall(r'\b[a-z]\b', left+' '+right)))
        assert len(variables) <= 2
        for values in itertools.product(map(Fraction, (-2, 0, 3)), repeat=len(variables)):
            env = dict(zip(variables, values), Fraction=Fraction)
            assert eval(left, {'__builtins__': {}}, env) == eval(right, {'__builtins__': {}}, env), (left, right, env)
            evaluations += 1
    assert Fraction(-1, 4) != Fraction(-2, 3)
    assert 5**2-2**2 == 21
    assert 3*5000+2*2000 == 19000
    assert 2*(3**2+3*3-4)+3*(3**2-2*3+2) == 43
    assert Fraction(43, 1000) != 43
    return evaluations


def issue(component, evidence, impact, proposal):
    return dict(component=component, evidence=evidence, impact=impact, proposal=proposal)


def build():
    evaluations = check_math()
    entries = [e for e in source_entries(ROOT/'docs/sources/incoming/2026-10-19-indikator-6-10') if e['indicator'] == 10]
    assert len(entries) == len(REVIEWS) == 50
    rows = []
    for e in entries:
        k = e['level'], e['source_number']
        manual = REVIEWS[k]
        assert len(manual['truth']) == len(e['options']) == len(manual['reasons'])
        ids = [str(i+1) if e['format']=='KATEGORI' else chr(65+i) for i in range(len(e['options']))]
        true_ids = [i for i, t in zip(ids, manual['truth']) if t=='T']
        projection = {name:e[name] for name in ('format','stem','options','key','declared_key_texts','explanation','additional_notes','category_labels','parse_flags')}
        row = dict(audit_id=e['audit_id'], indicator=10, level=k[0], source_number=k[1],
            source_projection=projection, source_location=e['source'],
            parsed_source_key=e['key'], source_key_resolution=dict(primary_declared_ids=e['key'],later_amendment_ids=None,conflict=False),
            source_paragraphs=e['paragraphs'], source_tables=e['tables'],
            independent_solution=dict(domain_and_interpretation=manual['domain'], exact_steps=manual['steps']),
            option_evaluation=[dict(id=i,text=text,truth={'T':'TRUE','F':'FALSE','U':'UNCERTAIN'}[t],reason=reason)
                for i,text,t,reason in zip(ids,e['options'],manual['truth'],manual['reasons'])],
            independently_correct_ids=true_ids, conditional_correct_ids=[],
            validity='VALID',answer_status='CORRECT' if e['key']==true_ids else 'INCORRECT',
            explanation_status='CORRECT',
            explanation_step_evaluation=[dict(status='CORRECT',verification=s) for s in manual['steps']],
            notes_status='CORRECT' if e['additional_notes'] else 'MISSING', issues=[],
            recommendation='Pertahankan hasil matematika dan kunci; tidak ada perubahan akademik wajib.')
        if k == (1, 7):
            row['validity']='UNCERTAIN'
            row['independently_correct_ids']=None
            row['answer_status']='UNCERTAIN'
            row['explanation_status']='UNCERTAIN'
            row['conditional_correct_ids']=[dict(condition='Persediaan awal0; catatan diperlakukan sebagai perubahan kuantitas simbolik, bukan koefisien masing-masing jenis barang.',ids=['A','B','C'])]
            for opt in row['option_evaluation'][1:3]:
                opt['truth']='UNCERTAIN'
                opt['reason'] += ' Ini perubahan kumulatif; total stok sama hanya jika persediaan awal0. Dengan stok awalS, totalSelasa=S+8p+6q dan akhirRabu=S+4p+8q.'
            row['issues'].append(issue('stem','B danC menyebut total/sisa persediaan, tetapi stimulus tidak menyatakan persediaan awal. Jika stok awalS, akhir=S+4p+8q, bukan selalu4p+8q.','KunciA,B,C memerlukan stok awal0 yang tidak dinyatakan.','Nyatakan persediaan awal0 atau ganti total/sisa menjadi perubahan persediaan bersih.'))
            row['issues'].append(issue('context','Kiriman Selasa2p-6q dan penjualan Rabu4p-2q memiliki koefisien pensil negatif jika p,q adalah jenis barang.','Narasi menerima/terjual tidak mewakili aliran positif tiap jenis; bentuk formal masih benar.','Gunakan perubahan stok bertanda atau nyatakan p,q sebagai parameter kuantitas, bukan unit jenis barang.'))
            row['recommendation']='Perjelas stok awal dan makna p,q sebelum menerima kunciA,B,C.'
        if k == (2, 3):
            row['issues'].append(issue('stem','Untuk x=2,y=0: luas tambahan6 m^2 dan utama24 m^2; tambahan-utama=-18 m^2 sedangkan besar selisih18 m^2.','JawabanA memakai pengurangan terarah; istilah selisih bisa dibaca besar selisih.','Tulis luas tambahan dikurangi luas utama secara eksplisit.'))
        if k == (3, 2):
            row['issues'].append(issue('stem','p=(2x+5)m,l=(3x-2)m menempatkanx sebagai parameter numerik; stimulus menyebut x bertambah2 meter.','Kenaikan20 m benar untukΔx=2 unit; satuan parameter tidak konsisten secara dimensional.','Ganti x bertambah sebesar2 meter menjadi nilai x bertambah2.'))
            row['recommendation']='Perbaiki satuan pertambahan parameter; kunciA tetap benar untukΔx=2.'
        if k in ((3, 4),(4, 4),(5, 4)):
            exclusions = {(3,4):'x!=0',(4,4):'x!=-2 dan x!=3/2',(5,4):'x!=-3 dan x!=3'}[k]
            row['issues'].append(issue('explanation',f'Pembatalan faktor menggunakan domain asal {exclusions}; pembahasan tidak menuliskan pembatasan itu.',
                'Hasil aljabar benar pada domain asal; tanpa catatan domain, pembaca dapat mengisi titik yang semula tidak terdefinisi.',f'Tambahkan syarat {exclusions} pada hasil akhir.'))
            row['recommendation']='Pertahankan kunci; tuliskan pembatasan domain asal pada hasil akhir.'
        if k == (4, 1):
            source_exp='\n'.join(p['text'] for p in e['paragraphs'] if 5303<=p['paragraph_index']<=5313 and p['text'])
            row['source_projection_resolved']=dict(projection,options=e['options'][:3]+[e['options'][3].split('\nPEMBAHASAN',1)[0]],explanation=source_exp)
            row['issues'].append(issue('source_projection','Paragraf5303 dimulai PEMBAHASAN Ukuran panjang, tanpa titik dua. Parser menggabungkan5303-5313 ke opsiD dan menandai explanation=null.',
                'Pembahasan sebenarnya tersedia dan benar; opsiD proyeksi terkontaminasi. Bukan pembahasan sumber yang hilang.',
                'Pisahkan pembahasan berdasarkan paragraf5303, pertahankan opsiD hanya(10x+4)meter.'))
            row['option_evaluation'][3]['text']=row['source_projection_resolved']['options'][3]
            row['recommendation']='Perbaiki pemisahan proyeksi; matematika dan kunciB benar.'
        if k == (4, 2):
            row['validity']='INVALID'
            row['answer_status']='INCORRECT'
            row['explanation_status']='UNCERTAIN'
            row['independently_correct_ids']=None
            row['conditional_correct_ids']=[dict(condition='Selisih didefinisikan A-B, atau besar selisih dengan A>=B.',ids=['A','C']),dict(condition='Besar selisih ketikaA<B.',ids=[])]
            row['issues'].append(issue('options','OpsiA=5a-10b+15 dan opsiC=5a-10b+15 (Revisi hitung:5a-10b+15) identik sebagai polinom.',
                'PG mempunyai dua opsi benar pada pembacaanA-B; kunci tunggalC tidak cukup.',
                'Ganti salah satu opsi duplikat dengan distraktor berbeda; buang catatan editorialRevisi hitung.'))
            row['issues'].append(issue('stem','A-B=5a-10b+15; pada a=1,b=3 banyak bukuA=8,B=18, besar selisih10 sedangkan bentuk opsiA,C=-10.',
                'Selisih antara dapat berarti nilai mutlak; tidak ada syarat A>=B.',
                'Ganti dengan KelompokA dikurangi KelompokB, atau minta|5a-10b+15| untuk besar selisih.'))
            row['recommendation']='Revisi wajib: satu opsi benar saja, arah pengurangan eksplisit, hapus catatan revisi diC.'
        if k == (4, 7):
            row['answer_status']='INCORRECT'
            row['source_key_resolution'].update(later_amendment_ids=['A','B','D'],conflict=True)
            row['issues'].append(issue('key','Kunci awalB,D, tetapi 2(3x-2y)-3(x-4y)=3x+8y membuatA juga benar; pembahasan akhir sendiri menyatakanA,B,D.',
                'Respons lengkapA,B,D akan berbeda dari kunci awal; kontradiksi deklarasi kunci.',
                'Tetapkan deklarasi kunciA,B,D; hapus riwayat revisi dari pembahasan final.'))
            row['recommendation']='Perbaiki kunci menjadiA,B,D; pertahankan derivasi3x+8y.'
        if k in ((4,9),(4,10),(5,9),(5,10)):
            row['source_projection_resolved']=dict(projection,stem=re.sub(r'^\(a\) BENAR\n\(b\) (?:BENAR|SALAH)\n\(c\) (?:BENAR|SALAH)\n','',projection['stem']))
            row['issues'].append(issue('source_projection','Tiga paragraf(a)/(b)/(c) setelahKUNCI JAWABAN masuk ke awalstem parser, padahal paragraf sumber jelas berada di bagian kunci.',
                'Jika proyeksi ini ditampilkan, jawaban sudah terbaca sebelum stimulus. Ini artefak pemisahan komponen, bukan bagian soal yang dimaksud penulis.',
                'Buang baris deklarasi kunci dari proyeksistem; tetap simpan dalamdeclared_key_texts.'))
            if k != (5,9):
                row['recommendation']='Matematika dan kunci benar; pisahkan deklarasi kunci dari proyeksistem.'
        if k == (5, 7):
            row['explanation_status']='INCORRECT'
            row['explanation_step_evaluation'][-1]['status']='INCORRECT'
            row['explanation_step_evaluation'][-1]['verification']='Klaim sumber(C & D Benar) salah untukC: faktor luar2x*5=10x, dalam(-3)*x=-3x. Revisi akhirB,D benar, tetapi klaim awalC benar masih tertulis.'
            row['issues'].append(issue('explanation','Pembahasan mula-mula menulis(C & D Benar), kemudian membatalkanC karena luar=10x,dalam=-3x. OpsiC justru menyebut dalam+10x,luar-3x.',
                'Pembahasan memuat evaluasiC yang saling bertentangan; kesimpulan akhirB,D benar.',
                'Hapus(C & D Benar), tulisC Salah,D Benar sejak evaluasi pertama; hapus riwayat revisi.'))
            row['recommendation']='KunciB,D benar; bersihkan klaim awalC benar dari pembahasan.'
        if k == (5, 9):
            row['validity']='UNCERTAIN'
            row['answer_status']='UNCERTAIN'
            row['explanation_status']='UNCERTAIN'
            row['independently_correct_ids']=None
            row['conditional_correct_ids']=[dict(condition='Hapus frasa dalam ribuan; satuan semua jumlah tetap rupiah.',ids=['1','3']),dict(condition='Frasa dalam ribuan dipertahankan bermakna43 ribu rupiah; stimulus tetap rupiah.',ids=['1'])]
            row['issues'].append(issue('units','Stimulus2(x^2+3x-4) rupiah dan3(x^2-2x+2) rupiah memberi padax=3 jumlah28+15=43 rupiah=43/1000 ribu rupiah. Opsi3 menulis43 rupiah(dalam ribuan).',
                'Angka43 benar tetapi skala ribuan tidak didukung; status opsi3 dan kunci bergantung interpretasi satuan.',
                'Pilih satu: hapus(dalam ribuan), atau ubah satuan stimulus menjadi ribu rupiah secara konsisten.'))
            row['explanation_step_evaluation'].append(dict(status='UNCERTAIN',verification='Aritmetika43 benar dalam rupiah, tetapi evaluasi3 BENAR tidak membenarkan tambahan skala ribuan.'))
            row['recommendation']='Samakan satuan stimulus dan opsi3; tentukan kunci setelah itu; pisahkan deklarasi kunci dari proyeksistem.'
        if e['additional_notes']:
            row['notes_evaluation']=dict(status='CORRECT',verification={
                (4,1):'Lupa faktor2 memberi p+l=5x+4, tepat menjelaskan distraktorA.',
                (4,2):'-(6b-3)=-6b+3; salah tanda konstanta menghasilkan selisih berbeda.',
                (4,3):'(2x+5)(3x-2)=6x^2+11x-10, tepat menggambarkan pertukaran tanda koefisien tengah.',
                (4,4):'Faktor yang tersisa adalah2x+3, bukan2x-3; peringatan salah salin sesuai.',
                (4,5):'-12+4=-8, bukan-16; salah penjumlahan konstanta memang dapat menolak ekuivalensi secara keliru.',
                (4,6):'x^2 danxy memiliki vektor pangkat berbeda(2,0) dan(1,1), sehingga satu huruf sama tidak cukup.',
                (4,7):'-3(-4y)=+12y; kesalahan tanda memberi-4y-12y=-16y, sesuai distraktorC.',
                (4,8):'(x-2)(x+3)=x^2+x-6, tidak sama denganx^2-5x+6.',
                (4,9):'2y-4y=-2y, bukan+2y, menjelaskan kesalahan opsi2.',
                (4,10):'5-3=2 sedangkan3-5=-2; komutatif penjumlahan tidak dapat diterapkan pada pengurangan.',
                (5,1):'-2(x-4y)=-2x+8y; salah tanda memberi-15y-8y=-23y, sesuai siswaY.',
                (5,2):'3(3a+b)=9a+3b, bukan9a+b; pengali wajib mengenai kedua suku.',
                (5,3):'(2x-3)^2=4x^2-12x+9, sedangkan(2x-3)(2x+3)=4x^2-9.',
                (5,4):'Padax=1, (x-2)/(x+3)=-1/4, bukan-2/3; mencoret suku gagal.',
                (5,5):'Satu kali beda memberiU2=3x+2; dua kali beda diperlukan untukU3=4x+1.',
                (5,6):'-(2a-5b)=-2a+5b; mengabaikan perubahan tanda memberi koefisienb yang keliru.',
                (5,7):'(2x+3)(x-5)=2x^2-7x-15, berbeda dari+7x pada polinom soal.',
                (5,8):'(2x-3)^2=4x^2-12x+9; bentuk4x^2-9 kehilangan suku silang dan salah konstanta.',
                (5,9):'6x+(-6x)=0x, bukan12x; catatan tanda benar, terpisah dari masalah satuan opsi3.',
                (5,10):'Pada(2,1), (x-y)^2=1 sedangkanx^2-y^2=3; kuadrat selisih berbeda dari selisih kuadrat.'
            }[k])
        rows.append(row)
    assert len({r['audit_id'] for r in rows}) == 50
    assert Counter(r['level'] for r in rows) == {1:10,2:10,3:10,4:10,5:10}
    assert sum(len(r['option_evaluation']) for r in rows) == 190
    for row in rows:
        assert row['independent_solution']['exact_steps']
        assert all(o['reason'] and o['truth'] in ('TRUE','FALSE','UNCERTAIN') for o in row['option_evaluation'])
        if row['independently_correct_ids'] is not None:
            assert row['independently_correct_ids'] == [o['id'] for o in row['option_evaluation'] if o['truth']=='TRUE']
        else:
            assert row['conditional_correct_ids']
    output = dict(indicator=10, source_group='2026-10-19-indikator-6-10',
        method='Pembacaan50 sumber asli lengkap: stimulus,190 opsi, deklarasi kunci, pembahasan, catatan, paragraf dan10 tabel kategori. Penyelesaian manual dari stimulus; tidak memakai generator atau review lama sebagai oracle.',
        conventions=dict(category_ids='1,2,3 sesuai urutanbaris; id tercantum berartiTRUE',
            algebra='Identitas atasR; bukan kesamaan kebetulan. Tanda titik dalam harga merupakan pemisah ribuan;2,5=5/2.',
            validity='VALID=hasil akademik dapat ditentukan; INVALID=kontradiksi/PG tidak unik; UNCERTAIN=interpretasi stimulus/satuan mengubah jawaban. Artefak proyeksi dicatat terpisah.'),
        coverage=dict(entries=50,options=190,tables=sum(len(e['tables']) for e in entries),
            paragraphs=sum(len(e['paragraphs']) for e in entries),image_count=sum(len(p['images']) for e in entries for p in e['paragraphs'])),
        verification=dict(exact_polynomial_identities=len(IDENTITIES),fraction_grid_evaluations=evaluations,
            degree_bound='Semua identitas tersandi berderajat<=2 pada setiap variabel; kisi3 titik per variabel memberi bukti identitas eksak.',
            direct_checks='Counterexample pecahan-1/4!=-2/3;25-4=21;belanja19000;total43;43/1000!=43.'),
        summary={name:dict(Counter(r[name] for r in rows)) for name in ('validity','answer_status','explanation_status')}, entries=rows)
    path=ROOT/'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/part-10.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(path=str(path),coverage=output['coverage'],summary=output['summary'],verification=output['verification']),ensure_ascii=True))
    return output


if __name__ == '__main__':
    build()
