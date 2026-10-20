"""Independent rendered-data arithmetic and survey-inference checks."""
import re
from fractions import Fraction


def numbers(text):
    return [Fraction(x.replace('.','').replace(',','.')) for x in re.findall(r'\d+(?:\.\d{3})*(?:,\d+)?',text)]


def require(text,*parts):
    for part in parts:assert part.casefold() in text.casefold(),(part,text)


def table(stem):
    rows=re.findall(r'^\|\s*([^|]+)\|\s*(\d+(?:\.\d{3})*)\s*\|',stem,re.M)
    assert len(rows)==4
    return [(label.strip(),numbers(value)[0]) for label,value in rows]


def check_math(qid,candidate):
    stem=candidate['stem'];opts=[o['text'] for o in candidate['options']];exp=candidate['explanation']
    truth=[]
    if qid=='pg-20-4-5':
        data=table(stem);total=sum(v for _,v in data);highest=max(v for _,v in data)
        assert data[0][0]=='Futsal' and data[0][1]==highest
        require(stem,'sebuah sekolah','seluruh siswa di kabupaten')
        assert numbers(opts[1])==[total]
        for option in opts:
            if 'data hanya mewakili responden' in option:
                require(option,'sekolah','belum tentu','kabupaten');truth.append(True)
            else:
                assert option.startswith(('Benar,','Tidak tepat, karena kegiatan'));truth.append(False)
        assert numbers(exp)==[total,highest]
        require(exp,'tidak membuktikan keterwakilan','Tabel sah')
    elif qid=='mcma-20-4-8':
        n=numbers(stem)[0];assert n>0
        require(stem,'sedang makan di kantin','istirahat pertama')
        for option in opts:
            if 'berpotensi kurang mewakili' in option:truth.append(True)
            elif 'pengalaman berbeda' in option:truth.append(True)
            elif 'kelas dan waktu istirahat yang berbeda' in option:truth.append(True)
            else:
                require(option,'pasti');truth.append(False)
                if 'hanya' in option:assert numbers(option)==[n]
        assert numbers(exp)==[n]
        require(exp,'nonpengguna','tidak menetapkan','tidak selalu sama')
    elif qid=='pg-20-5-2':
        data=table(stem);total=sum(v for _,v in data);assert numbers(stem)[0]==total
        require(stem,'diagram garis','kategori ekstrakurikuler')
        for option in opts:
            if 'diagram batang lebih sesuai' in option:
                require(option,'kategori yang berbeda');truth.append(True)
            else:
                assert any(x in option for x in ('selalu','kontinu','hanya dapat'));truth.append(False)
        assert numbers(exp)==[total,4]
        require(exp,'nominal','bukan urutan waktu','bukan satu-satunya')
    elif qid=='pg-20-5-3':
        n,high,cutoff=numbers(stem);assert cutoff==80 and n>=high>n/2
        require(stem,'menyurvei','mengikuti bimbingan belajar','pasti menyebabkan')
        for option in opts:
            if 'tidak ada data pembanding' in option:
                require(option,'faktor lain');truth.append(True)
            else:
                assert option.startswith(('Tepat,','Salah, karena siswa'));truth.append(False)
        assert numbers(exp)==[n,high]
        require(exp,'lebih dari setengah','Tidak ada data pembanding','tidak membuktikan sebab-akibat')
    elif qid=='pg-20-5-4':
        n=numbers(stem)[0];require(stem,'hanya bertanya','aktif menggunakan','semua siswa')
        assert numbers(opts[0])==[n]
        for option in opts:
            if 'sampel yang lebih beragam' in option:
                require(option,'pertanyaan netral','manfaat serta risiko');truth.append(True)
            else:
                assert any(t in option for t in ('Menggunakan jawaban','mengarahkan','Mengganti semua'));truth.append(False)
        assert numbers(exp)==[n]
        require(exp,'mengabaikan pendapat','beragam','netral','tidak memperbaiki bias')
    elif qid=='mcma-20-5-8':
        data=re.findall(r'(sepeda motor|sepeda|berjalan kaki|angkutan umum)\s+(\d+(?:\.\d{3})*)\s+siswa',stem)
        assert len(data)==4
        counts=[numbers(x)[0] for _,x in data];assert all(v>0 for v in counts)
        total=sum(counts)
        for option in opts:
            if 'diagram batang' in option:truth.append(True)
            elif 'diagram lingkaran' in option:
                require(option,'proporsi','keseluruhan');truth.append(True)
                if 'proporsi sepeda motor:' in option:
                    part=re.search(r'proporsi sepeda motor:\s*([\d.]+)/([\d.]+)',option);assert part
                    assert numbers(part[1])[0]==counts[0] and numbers(part[2])[0]==total
            elif 'judul dan label' in option:truth.append(True)
            else:
                assert any(t in option for t in ('urutan waktu','Menghilangkan kategori'));truth.append(False)
        assert numbers(exp)==[total,counts[0]]
        require(exp,'bukan urutan waktu','Menghapus kategori','proporsi')
    else:raise AssertionError(qid)
    # Numeric annexes are actual sample counts, not arbitrary serial labels.
    expected={'pg-20-4-5':locals().get('total'),'mcma-20-4-8':locals().get('n'),
              'pg-20-5-2':locals().get('total'),'pg-20-5-3':locals().get('high'),
              'pg-20-5-4':locals().get('n')}.get(qid)
    for option in opts:
        if '(hasil:' in option:
            annex=option.split('(hasil:',1)[1];assert numbers(annex)[0]==expected
    actual=[o['correct'] for o in candidate['options']]
    assert actual==truth,(qid,actual,truth)
    return truth
