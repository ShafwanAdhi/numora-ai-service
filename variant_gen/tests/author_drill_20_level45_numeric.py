"""Six bounded survey families with coherent sample/table data, no source edits."""
import json
from author_drill_20_23_level45_batch1 import ROOT,DATA
from build_drill_1_5_level45_batch1 import Author

IDS={'pg-20-4-5','mcma-20-4-8','pg-20-5-2','pg-20-5-3','pg-20-5-4','mcma-20-5-8'}


def selected():
    return [e for e in json.loads((DATA/'audit.json').read_text(encoding='utf-8'))['entries'] if e['question_id'] in IDS]


def author(entry):
    a=Author(dict(entry,source_number=int(entry['question_id'].split('-')[-1])))
    a.variables['k']['range']=[0,24]
    q=entry['question_id']
    if q=='pg-20-4-5':
        a.allnums({'40':'40+3*k','25':'25+2*k','20':'20+k','15':'15+k','100':'100+7*k'})
        a.answer_value(2,'100+7*k',' responden pada sekolah ini')
        a.exp=a.explanation('Total = [[100+7*k]]. Terbanyak = [[40+3*k]]. Futsal paling banyak dalam sampel sekolah ini; jumlah responden maupun kategori terbesar tidak membuktikan keterwakilan seluruh kabupaten. Tabel sah untuk data kategori.')
    elif q=='mcma-20-4-8':
        a.allnums({'30':'30+k'})
        a.answer_value(0,'30+k',' responden kantin pada istirahat pertama')
        a.exp=a.explanation('Jumlah sampel = [[30+k]]. Responden hanya pengguna kantin pada istirahat pertama, sehingga pengalaman nonpengguna dan waktu lain dapat tidak terwakili. Sampel lintas kelas dan waktu memperluas cakupan. Jumlah responden saja tidak menetapkan hasil pasti tidak valid; jawaban siswa tidak selalu sama.')
    elif q=='pg-20-5-2':
        a.allnums({'200':'200+5*k','80':'80+2*k','50':'50+k','40':'40+k','30':'30+k'})
        a.answer_value(1,'200+5*k',' responden pada empat kategori')
        a.exp=a.explanation('Total = [[200+5*k]]. Kategori = 4. Ekstrakurikuler merupakan kategori nominal, bukan urutan waktu atau data kontinu. Diagram batang membandingkan jumlah antarkategori; diagram garis penghubung dapat menyiratkan kesinambungan yang tidak diberikan. Tabel bukan satu-satunya penyajian yang sah.')
    elif q=='pg-20-5-3':
        a.allnums({'20':'20+2*k','18':'18+k'})
        a.answer_value(2,'18+k',' siswa bernilai tinggi dalam kelompok yang diamati')
        a.exp=a.explanation('Sampel = [[20+2*k]]. Nilai tinggi = [[18+k]]. Kelompok bernilai tinggi memang lebih dari setengah sampel, tetapi penelitian hanya mengamati peserta bimbingan. Tidak ada data pembanding, nilai sebelum perlakuan, atau pengendalian faktor lain. Mayoritas tidak membuktikan sebab-akibat; peserta tetap boleh menjadi responden.')
    elif q=='pg-20-5-4':
        a.allnums({'15':'15+k'})
        a.answer_value(2,'15+k',' pengguna aktif pada sampel awal')
        a.exp=a.explanation('Sampel awal = [[15+k]]. Pemilihan hanya pengguna aktif dapat mengabaikan pendapat kelompok lain. Sampel beragam dan pertanyaan netral memperbaiki pengumpulan data. Memperbanyak pertanyaan menggiring atau mengganti jawaban siswa dengan pendapat guru tidak memperbaiki bias.')
    elif q=='mcma-20-5-8':
        a.allnums({'50':'50+3*k','25':'25+2*k','15':'15+k','10':'10+k'})
        a.options[1]+=(a.var("' (proporsi sepeda motor: '",'')+a.var('50+3*k','')+
                       a.var("'/'",'')+a.var('100+7*k','')+a.var("')'",''))
        a.exp=a.explanation('Total = [[100+7*k]]. Sepeda motor = [[50+3*k]]. Semua frekuensi positif dan tiap siswa tercatat pada satu kategori. Diagram batang membandingkan jumlah, lingkaran menunjukkan proporsi dari keseluruhan, dan judul serta label memperjelas data. Jenis transportasi bukan urutan waktu. Menghapus kategori terkecil mengubah representasi keseluruhan.')
    else:raise AssertionError(q)
    return a
