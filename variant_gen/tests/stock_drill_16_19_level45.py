"""Thirty curated editorial items, two distinct situations per conceptual original."""
import json
from complete_drill_16_19_level45 import ROOT,DATA,CONCEPTS,dump

ITEMS={}


def add(q,stem,options,key,explanation,note):
    assert len(options)==4
    ITEMS.setdefault(q,[]).append(dict(stem=stem,options=options,key=key,
                                      explanation=explanation,variation_note=note))


add('pg-16-4-2','Empat rancangan memiliki sambungan yang sesuai. Rancangan manakah yang kekurangan bidang sehingga tidak membentuk bangun tertutup?',
 ['Kubus: enam persegi kongruen.','Prisma segitiga: dua segitiga kongruen dan tiga persegi panjang sesuai sisi alas.','Limas segi empat: satu persegi dan tiga segitiga sisi tegak.','Kerucut: satu lingkaran dan satu juring dengan busur sepanjang keliling alas.'],'C',
 'Limas segi empat memerlukan empat segitiga sisi tegak; C hanya tiga, sehingga satu sisi terbuka. Komponen A,B,D lengkap dengan sambungan yang disyaratkan.',
 'Menilai bidang yang hilang, bukan segitiga berlebih seperti sumber.')
add('pg-16-4-2','Setiap rancangan mempunyai sambungan yang sesuai. Rancangan manakah yang gagal menutup karena ukuran sambungannya?',
 ['Tabung: dua lingkaran kongruen dan selimut persegi panjang sepanjang keliling alas.','Limas segi empat: satu persegi dan empat segitiga yang sesuai.','Prisma segitiga: dua segitiga kongruen dan tiga persegi panjang sesuai sisi alas.','Kerucut: lingkaran alas dan juring yang panjang busurnya lebih pendek daripada keliling alas.'],'D',
 'D tidak cukup panjang untuk mengelilingi alas; selimut menyisakan celah. A,B,C sudah memenuhi jumlah bidang dan kecocokan sambungan.',
 'Membedakan kecocokan ukuran dari kelengkapan jumlah bidang.')

add('pg-16-4-5','Sebuah prisma tegak mempunyai alas segitiga sama sisi. Jika dibuka sepanjang rusuk yang sesuai, komponen jaring-jaring yang benar adalah...',
 ['Dua segitiga kongruen dan tiga persegi panjang yang kongruen.','Dua segitiga kongruen dan dua persegi panjang.','Satu segitiga dan tiga persegi panjang.','Tiga segitiga dan tiga persegi panjang.'],'A',
 'Terdapat dua alas segitiga. Tiga sisi alas sama panjang dan tinggi prisma sama, sehingga ketiga persegi panjang kongruen. B kekurangan sisi tegak; C kekurangan alas; D menambah alas.',
 'Alas sama sisi mengubah relasi ukuran tiga selimut dari berbeda menjadi kongruen.')
add('pg-16-4-5','Prisma tegak mempunyai alas segitiga sama kaki yang bukan sama sisi. Hubungan ukuran bidang pada jaring-jaringnya adalah...',
 ['Ketiga persegi panjang selimut pasti berbeda ukuran.','Dua segitiga alas tidak kongruen.','Dua segitiga alas kongruen; tepat dua dari tiga persegi panjang selimut kongruen.','Jaring-jaring hanya memerlukan satu segitiga alas.'],'C',
 'Dua sisi alas sama dan sisi ketiga berbeda. Pada tinggi prisma yang sama, tepat dua selimut kongruen. Alas dan tutup tetap kongruen; A,B,D salah.',
 'Menguji dua ukuran selimut yang sama, bukan sekadar mengganti ukuran segitiga siku-siku.')

add('mcma-16-4-6','Sebuah tetrahedron dibuka menjadi jaring-jaring, kemudian dilipat kembali. Pilih semua pernyataan benar tentang bangun yang sudah dilipat!',
 ['Memiliki empat sisi berbentuk segitiga.','Memiliki enam rusuk.','Memiliki empat titik sudut.','Memiliki lima titik sudut.'],'A,B,C',
 'Tetrahedron: F=4,E=6,V=4 dan V-E+F=2. A,B,C benar; D salah. Titik sudut dihitung setelah dilipat, bukan pada gambar datar.',
 'Memisahkan hitungan titik sudut bangun terlipat dari titik pada net.')
add('mcma-16-4-6','Sebuah limas segitiga memiliki satu alas dan tiga sisi tegak. Pilih semua hasil pemeriksaan yang benar!',
 ['Jumlah seluruh bidangnya empat.','Tiga rusuk alas dan tiga rusuk tegak menghasilkan enam rusuk.','Tiga titik sudut alas ditambah satu puncak menghasilkan empat titik sudut.','Jumlah bidang dikurangi jumlah rusuk ditambah jumlah titik sudut adalah satu.'],'A,B,C',
 'A=1+3=4 bidang; B=3+3=6 rusuk; C=3+1=4 titik. Untuk D,4-6+4=2, bukan1.',
 'Menyusun hitungan dari alas dan puncak serta menguji konsistensi Euler.')

add('mcma-16-4-7','Tabung tanpa tutup dengan jari-jari r dan tinggi h dibuka menjadi jaring-jaring. Pilih semua pernyataan benar!',
 ['Terdapat satu lingkaran dan satu persegi panjang.','Lebar selimut mewakili tinggi h.','Jaring-jaring harus memiliki dua lingkaran.','Panjang selimut sama dengan 2*pi*r.'],'A,B,D',
 'Satu tutup dihilangkan, sehingga alas tinggal satu lingkaran. Selimut tetap berukuran2*pi*r kali h. A,B,D benar; C salah.',
 'Mengubah kelengkapan tutup, tetap menilai struktur net dan sambungan.')
add('mcma-16-4-7','Tabung tertutup dipotong sepanjang satu garis tegak dan kedua tepi lingkarannya. Pilih semua pernyataan benar tentang bidang yang dilebarkan!',
 ['Kedua lingkaran alas dan tutup kongruen.','Selimut dapat dilebarkan menjadi persegi panjang.','Luas seluruh bidang adalah pi*r*r+2*pi*r*h.','Luas kedua lingkaran bersama-sama adalah 2*pi*r*r.'],'A,B,D',
 'A,B,D benar. Rumus C hanya memasukkan satu lingkaran, padahal tabung tertutup memerlukan dua; luas total2*pi*r*r+2*pi*r*h.',
 'Memeriksa komponen rumus luas, bukan hanya jumlah bidang.')

add('mcma-16-4-8','Sebuah net terdiri dari satu segi lima dan lima segitiga sisi tegak yang sesuai. Pilih semua pernyataan benar mengenai bangun ruangnya!',
 ['Bangun tersebut adalah limas segi lima.','Jumlah rusuknya sepuluh.','Jumlah titik sudutnya enam.','Jumlah sisi tegaknya enam.'],'A,B,C',
 'Limas segi lima memiliki5 rusuk alas+5 rusuk tegak=10, serta5 titik alas+1 puncak=6. Sisi tegak hanya5, sehingga D salah.',
 'Menggeneralisasi hubungan alas, rusuk dan puncak ke segi lima.')
add('mcma-16-4-8','Net sebuah limas mempunyai alas segitiga dan tiga segitiga sisi tegak. Pilih semua pernyataan benar!',
 ['Bangun memiliki empat bidang.','Bangun memiliki enam rusuk.','Bangun memiliki lima titik sudut.','Bangun memiliki satu puncak di luar tiga titik sudut alas.'],'A,B,D',
 'F=1+3=4; E=3+3=6; V=3+1=4. A,B,D benar; C salah karena bukan5.',
 'Mengubah jenis alas sehingga tidak menghafal angka delapan rusuk dari sumber.')

add('kategori-16-4-9','Nilai Benar atau Salah untuk sifat prisma tegak dan limas berikut!',
 ['Prisma memiliki dua alas yang kongruen.','Limas memiliki satu puncak yang bukan titik sudut alas.','Semua sisi tegak prisma berbentuk segitiga.','Limas segi-n mempunyai n+1 bidang seluruhnya.'],'1,2,4',
 '1,2,4 benar: dua alas prisma; satu puncak limas; satu alas+n sisi tegak. 3 salah karena sisi tegak prisma tegak berbentuk persegi panjang.',
 'Membedakan jumlah seluruh bidang dari jumlah sisi tegak.')
add('kategori-16-4-9','Bandingkan prisma segitiga dan limas segitiga tertutup. Nilai setiap pernyataan!',
 ['Prisma segitiga mempunyai lima bidang.','Prisma segitiga mempunyai sembilan rusuk.','Prisma segitiga mempunyai enam titik sudut.','Limas segitiga mempunyai lima bidang.'],'1,2,3',
 'Prisma segitiga:F=2+3=5,E=3+3+3=9,V=3+3=6. Limas segitiga:F=1+3=4 sehingga4 salah.',
 'Menangani kasus n=3 ketika alas limas juga segitiga.')

add('kategori-16-4-10','Kategorikan karakteristik net sebagai Tabung atau Kerucut. Kategori pertama adalah Tabung.',
 ['Luas dua bidang alas dan tutup bersama-sama adalah 2*pi*r*r.','Selimut berupa juring yang jari-jarinya sama dengan garis pelukis.','Luas satu alas dan selimut adalah pi*r*r+pi*r*s.','Selimut persegi panjang mempunyai dua tepi sejajar untuk menyambung dua alas kongruen.'],'1,4',
 '1,4 Tabung: dua lingkaran dan selimut persegi panjang. 2,3 Kerucut: satu lingkaran dan selimut juring dengan luas pi*r*s.',
 'Klasifikasi dari relasi luas dan tepi sambungan, bukan daftar bentuk sumber.')
add('kategori-16-4-10','Kategorikan proses melipat berikut sebagai Tabung atau Kerucut; setiap rancangan sesuai ukuran sambungannya.',
 ['Sebuah juring disatukan pada dua sisi lurusnya hingga mempunyai satu puncak.','Dua tepi sejajar sebuah persegi panjang disatukan dan kedua ujungnya ditutup lingkaran kongruen.','Satu alas lingkaran disambungkan dengan tepi busur sebuah juring.','Tidak ada titik puncak; kedua bidang ujung berupa lingkaran kongruen.'],'2,4',
 '1,3 Kerucut karena juring menghasilkan puncak dan satu alas. 2,4 Tabung karena selimut persegi panjang dan dua ujung lingkaran tanpa puncak.',
 'Menggunakan proses pelipatan sebagai representasi baru.')

add('pg-16-5-1','Seluruh bidang penyusun suatu net sudah lengkap. Rancangan manakah tetap gagal menjadi bangun tertutup?',
 ['Prisma dengan bidang dan tepi sambungan yang kongruen sesuai pasangannya.','Tabung dengan panjang selimut tepat sama keliling alas.','Kerucut dengan busur selimut lebih pendek daripada keliling alas.','Limas dengan setiap tepi segitiga tegak cocok dengan alas dan sisi tetangganya.'],'C',
 'C menyisakan celah sepanjang sambungan alas-selimut. A,B,D sudah memenuhi kecocokan tepi yang dinyatakan.',
 'Kelengkapan bidang tidak menjamin kecocokan panjang sambungan.')
add('pg-16-5-1','Sebuah tabung tertutup akan dirakit. Dua lingkaran kongruen sudah tersedia. Kondisi selimut manakah yang menjamin sambungan alas dapat menutup tepat tanpa tumpang tindih?',
 ['Panjang persegi panjang sama dengan diameter alas.','Panjang persegi panjang sama dengan jari-jari alas.','Panjang persegi panjang sama dengan keliling alas, lebarnya sama dengan tinggi tabung.','Panjang persegi panjang sama dengan setengah keliling alas.'],'C',
 'Selimut harus mengelilingi seluruh tepi alas satu kali, sehingga panjangnya2*pi*r dan lebarnya h. A,B,D terlalu pendek untuk r>0.',
 'Mengevaluasi kondisi cukup, bukan memilih gambar berdasarkan proporsi.')

add('pg-16-5-2','Jari-jari tabung digandakan, sedangkan tingginya dijadikan setengah. Siswa menyatakan luas permukaan tabung tertutup tetap. Evaluasi yang tepat adalah...',
 ['Benar karena luas kedua alas tetap.','Salah: luas selimut tetap tetapi luas kedua alas menjadi empat kali.','Benar karena semua panjang saling meniadakan.','Salah: luas selimut menjadi empat kali.'],'B',
 'Selimut2*pi*(2r)*(h/2)=2*pi*r*h tetap. Kedua alas2*pi*(2r)^2=8*pi*r*r, empat kali semula. Luas total bertambah; A,C,D salah.',
 'Menilai perubahan komponen luas ketika alas membesar, kebalikan kasus sumber.')
add('pg-16-5-2','Pada tabung tertutup, jari-jari tetap dan tinggi digandakan. Siswa menyatakan seluruh luas permukaan menjadi dua kali. Evaluasi yang tepat adalah...',
 ['Benar karena kedua alas ikut menjadi dua kali.','Salah karena luas seluruh permukaan tetap.','Salah: hanya luas selimut yang menjadi dua kali; luas kedua alas tetap.','Benar karena luas selimut tetap.'],'C',
 'Lbaru=2*pi*r*r+4*pi*r*h, sedangkan2*Llama=4*pi*r*r+4*pi*r*h. Untuk r>0 keduanya tidak sama. C benar; A,B,D salah.',
 'Memisahkan perubahan luas selimut dari luas total dengan alas tetap.')

add('mcma-16-5-7','Tabung tanpa tutup mempunyai jari-jari r>0 dan tinggi h>0. Pilih semua pernyataan benar!',
 ['Selimut menjadi persegi bila h=2*pi*r.','Luas alas yang diperlukan adalah pi*r*r.','Menggandakan h selalu menggandakan seluruh luas net.','Panjang selimut sebelum dilipat adalah 2*pi*r.'],'A,B,D',
 'A karena kedua ukuran selimut sama; B satu alas; D keliling alas. C salah: alas tetap, hanya selimut yang dua kali.',
 'Menguji syarat persegi yang tepat dan membedakan luas komponen.')
add('mcma-16-5-7','Tabung terbuka di kedua ujung dibuat hanya dari selimut, dengan tebal bahan diabaikan. Pilih semua pernyataan benar!',
 ['Net cukup berupa satu persegi panjang.','Luas bahannya 2*pi*r*h.','Jika r dijadikan setengah dan h digandakan, luas bahan tetap.','Net tetap membutuhkan dua lingkaran alas.'],'A,B,C',
 'Tanpa kedua penutup, bahan hanya selimut. L=2*pi*r*h dan Lbaru=2*pi*(r/2)*(2h)=L. D salah karena kedua ujung sengaja terbuka.',
 'Mengubah kondisi penutup untuk menguji batas berlakunya rumus.')

add('mcma-16-5-8','Evaluasi hubungan net dan jenis alas pada prisma tegak serta limas. Pilih semua pernyataan benar!',
 ['Prisma segi empat mempunyai dua bidang alas dan empat bidang selimut.','Limas segi lima mempunyai lima segitiga sisi tegak.','Prisma dengan alas semua sisinya berbeda dapat mempunyai selimut persegi panjang berbeda ukuran.','Setiap limas harus mempunyai alas persegi.'],'A,B,C',
 'Prisma segi-n memiliki2 alas+n selimut. Limas segi-n memiliki n sisi tegak. Ukuran selimut mengikuti sisi alas pada tinggi tetap. Alas limas dapat berupa poligon selain persegi, sehingga D salah.',
 'Menguji generalisasi dan satu klaim universal yang berlebihan.')
add('mcma-16-5-8','Sebuah limas beralas persegi memiliki semua rusuk alas dan rusuk tegak sama panjang. Pilih semua pernyataan benar!',
 ['Setiap sisi tegaknya berbentuk segitiga sama sisi.','Net mempunyai satu persegi dan empat segitiga.','Bangun tersebut mempunyai empat bidang seluruhnya.','Jumlah seluruh bidangnya lima.'],'A,B,D',
 'Masing-masing segitiga memiliki tiga sisi sama panjang. Terdapat1 alas+4 segitiga=5 bidang. A,B,D benar; C salah.',
 'Menggunakan konstruksi penyangkal klaim bahwa sisi tegak sama sisi mustahil.')

add('pg-17-5-3','Refleksi terhadap garis y=x diterapkan pada seluruh segitiga. Sifat bayangannya adalah...',
 ['Luas dan panjang sisi tetap, tetapi orientasi matematis terbalik.','Luas menjadi dua kali dan orientasi tetap.','Panjang sisi berubah namun luas tetap.','Luas tetap dan orientasi matematis selalu tetap.'],'A',
 'Refleksi adalah isometri dengan determinan-1: panjang dan luas tetap, orientasi matematis terbalik. B,C mengubah ukuran; D salah tentang orientasi.',
 'Jenis transformasi ditetapkan pada seluruh bangun, bukan disimpulkan dari satu pasangan titik.')
add('pg-17-5-3','Sebuah segitiga dirotasi 90 derajat terhadap suatu pusat, lalu ditranslasi. Pernyataan yang benar mengenai hasil akhirnya adalah...',
 ['Luas berubah karena ada dua transformasi.','Panjang sisi tetap tetapi orientasi matematis terbalik.','Bangun kongruen dan orientasi matematis tetap.','Bangun hanya sebangun dengan faktor ukuran yang berbeda.'],'C',
 'Rotasi dan translasi sama-sama isometri yang mempertahankan orientasi. Komposisinya menjaga panjang, luas dan orientasi; C benar. Banyaknya transformasi tidak menggandakan luas.',
 'Membandingkan komposisi isometri dengan refleksi sumber.')

add('mcma-17-5-7','Pilih semua evaluasi yang benar tentang komposisi transformasi pada bangun datar!',
 ['Rotasi diikuti translasi mempertahankan luas.','Dua refleksi berturut-turut mempertahankan orientasi matematis.','Refleksi tunggal mempertahankan keliling.','Rotasi diikuti translasi selalu menggandakan keliling.'],'A,B,C',
 'Rotasi, translasi dan refleksi adalah isometri. Dua refleksi membalik orientasi dua kali sehingga tetap. D salah: keliling tetap, bukan dua kali.',
 'Memeriksa komposisi serta orientasi, bukan hanya transformasi tunggal.')
add('mcma-17-5-7','Bangun tak degenerat didilatasi dengan faktor k<0 terhadap satu pusat. Pilih semua pernyataan benar!',
 ['Perbandingan luas adalah k*k.','Perbandingan keliling adalah nilai mutlak k.','Untuk k=-1, bangun kongruen dengan bangun awal.','Luas bayangan bernilai negatif karena k negatif.'],'A,B,C',
 'Panjang dikali|k|, luas dikali k^2>0. k=-1 sama dengan rotasi180 sehingga kongruen. Luas tidak negatif; D salah.',
 'Menguji nilai mutlak faktor panjang dan kuadrat faktor luas.')

add('mcma-19-5-6','Prisma dan limas memiliki luas alas sama serta tinggi sama yang positif. Pilih semua evaluasi benar!',
 ['Prisma menampung tiga kali volume limas.','Limas menampung sepertiga volume prisma.','Volume keduanya sama jika tinggi prisma diubah menjadi sepertiga tinggi limas.','Volume keduanya sama jika tinggi limas diubah menjadi sepertiga tinggi prisma.'],'A,B,C',
 'Vp=A*hp, Vl=A*hl/3. Pada tinggi sama Vp=3Vl. Syarat sama volume hp=hl/3. D membalik hubungan itu dan salah.',
 'Menentukan syarat kesamaan volume, bukan sekadar memperbesar tinggi keduanya.')
add('mcma-19-5-6','Sebuah prisma dan limas mempunyai volume sama dan luas alas sama yang positif. Pilih semua hubungan benar!',
 ['Tinggi limas tiga kali tinggi prisma.','Tinggi prisma sepertiga tinggi limas.','Jika kedua tinggi digandakan, volume keduanya tetap sama satu sama lain.','Tinggi kedua bangun harus sama.'],'A,B,C',
 'A*hp=A*hl/3 memberi hl=3hp. Menggandakan kedua tinggi menggandakan kedua volume sehingga tetap sama. D salah untuk tinggi positif.',
 'Memulai dari volume sama untuk membalik hubungan tinggi.')

add('mcma-19-5-7','Bola berjari-jari r>0 dibandingkan dengan limas yang luas alasnya pi*r*r dan tingginya r. Pilih semua pernyataan benar!',
 ['Volume limas adalah pi*r*r*r/3.','Volume bola empat kali volume limas.','Perbandingan volume bola:limas adalah 4:1.','Jika r bola digandakan dengan limas tetap, volume bola menjadi dua kali volume limas.'],'A,B,C',
 'Vl=pi*r^3/3 dan Vb=4*pi*r^3/3 sehingga rasio4:1. r bola digandakan memberi8*Vb=32*Vl, bukan2*Vl. A,B,C benar.',
 'Mengganti hubungan luas alas sehingga rasio pi pada sumber menjadi rasio4.')
add('mcma-19-5-7','Bola berjari-jari r>0 dibandingkan dengan limas beralas persegi bersisi r dan tinggi r. Pilih semua evaluasi benar!',
 ['Volume limas adalah r*r*r/3.','Volume bola lebih besar daripada volume limas.','Perbandingan volume bola:limas adalah 4*pi:1.','Menggandakan jari-jari bola membuat volumenya hanya dua kali volume semula.'],'A,B,C',
 'Vl=r^3/3, Vb=4*pi*r^3/3; r>0 memberi Vb>Vl dan rasio4*pi:1. Volume bola berskala kubik: r dua kali memberi8 kali, bukan2. A,B,C benar.',
 'Menguji pengaruh sisi alas r, bukan2r, terhadap perbandingan simbolik.')


def build_stock():
    from bank import load_workspace_bank
    from conceptual_stock import load_stock
    from filters import validate_candidate
    bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
    path=ROOT/'data/conceptual_stock.json';payload=json.loads(path.read_text(encoding='utf8'))
    assert set(ITEMS)==CONCEPTS and all(len(items)==2 for items in ITEMS.values())
    existing={i['variant_id']:i for i in payload['variants']}
    additions=[]
    for q,items in ITEMS.items():
        o=bank.get(q);prior=[]
        for index,source in enumerate(items,1):
            key=source['key'].split(',');options=[dict(id=p['id'],text=t) for p,t in zip(o['options'],source['options'])]
            item=dict(source,variant_id=f'{q}:stock-{index:02d}',question_id=q,stock_index=index,
                stock_version=1,original_hash=o['hash'],original_version=o['version'],options=options,
                review_status='VERIFIED',review_note='Review engineering isi, tiap opsi, kunci, variasi tugas dan pembahasan; bukan approval kurikulum atau kesetaraan IRT.')
            candidate=dict(stem=item['stem'],options=[dict(p,correct=p['id'] in key) for p in options],explanation=item['explanation'])
            assert not validate_candidate(candidate,o,prior,allow_same_answer=True),(q,index,validate_candidate(candidate,o,prior,allow_same_answer=True))
            prior.append(candidate)
            if item['variant_id'] in existing:assert existing[item['variant_id']]==item,'Refusing changed stock overwrite'
            else:additions.append(item)
    # Validate the complete proposed inventory before replacing the live asset.
    payload['variants'].extend(additions)
    tmp=path.with_name('conceptual_stock.review.json');dump(tmp,payload)
    try:load_stock(tmp,bank)
    finally:tmp.unlink(missing_ok=True)
    dump(path,payload)
    metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
    for q in CONCEPTS:
        metadata[q].update(generation_status='DEFERRED_CONCEPTUAL',generator_status='FINITE_STOCK',
            reason='Soal konseptual memakai dua stok editorial VERIFIED yang dapat dipilih dan dipakai ulang; tidak memakai generator numerik.')
    dump(DATA/'question_metadata.json',metadata)
    print(f'Editorial stock: {len(CONCEPTS)} originals, {sum(map(len,ITEMS.values()))} verified items; added {len(additions)}.')
