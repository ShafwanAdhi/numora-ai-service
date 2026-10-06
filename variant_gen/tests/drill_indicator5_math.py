"""Independent exact arithmetic on rendered indicator 5 text, never config values."""
import re
from fractions import Fraction

NUM = r'-?\d+(?:\.\d{3})*(?:,\d+)?'


def numbers(text):
    return [Fraction(x.replace('.', '').replace(',', '.')) for x in re.findall(NUM, text)]


def reduced(a, b):
    assert a > 0 and b > 0
    ratio = a / b
    return [Fraction(ratio.numerator), Fraction(ratio.denominator)]


def simplest(values, a, b):
    return len(values) == 2 and values == reduced(a, b)


def check_math(original, candidate):
    qid = original['id']
    _, _, level, index = qid.split('-')
    level, index = int(level), int(index)
    s = candidate['stem']
    texts = [o['text'] for o in candidate['options']]
    assert len(texts) == len(original['options'])
    opts = [numbers(t) for t in texts]
    n = numbers(s)
    expected_explanation = None
    # These families vary numerical facts only; this also guards changed units/nouns.
    for text, old in zip(texts, original['options']):
        assert re.sub(NUM, '#', text) == re.sub(NUM, '#', old['text']), (qid, text)
    assert re.sub(NUM, '#', s) == re.sub(NUM, '#', original['stem']), qid

    if index == 1 and level < 3:
        a, b = n
        truth = [simplest(o, a, b) for o in opts]
        expected_explanation = reduced(a, b)
        assert max(a, b) <= 100
    elif index == 2 and level < 3:
        distance, one, scale = n
        assert one == 1 and 0 < distance <= 200
        answer = distance * 100 / scale
        truth = [o == [answer] for o in opts]
        expected_explanation = [answer]
    elif index == 3 and level < 3:
        volume = n[0]
        clocks = re.findall(r'pukul (\d{2})\.(\d{2})', s)
        assert len(clocks) == 2
        start, end = [60*int(h)+int(m) for h,m in clocks]
        duration = end-start
        assert 0 < duration < 120 and 0 < volume <= 2000
        answer = volume/duration
        truth = [o == [answer] for o in opts]
        expected_explanation = [duration, answer]
    elif qid == 'pg-5-1-4':
        a, price_a, b, price_b, buy = n
        unit = price_a/a
        assert price_b/b == unit and buy == b and all(x.denominator == 1 for x in [a,b,price_a,price_b])
        truth = [o == [buy*unit] for o in opts]
        expected_explanation = [unit,buy*unit]
    elif qid == 'pg-5-2-4':
        a, price_a, b, price_b, repeated, stated_b, stated_a = n
        ua, ub = price_a/a, price_b/b
        assert repeated == price_a and stated_b == ub and stated_a == ua
        analysis_i = ua < ub and price_a < price_b
        analysis_ii = ub < ua
        truth = [analysis_i,analysis_ii,not analysis_i and not analysis_ii,ua == ub]
        expected_explanation = [ua,ub]
    elif qid == 'pg-5-3-4':
        one,a,price_a,other,b,price_b = n
        assert one == other == 1
        ua, ub = price_a/a, price_b/b
        truth = [ua < ub and opts[0] == [ub-ua],ub < ua and opts[1] == [ua-ub],
                 ub < ua and opts[2] == [ua-ub],ua == ub]
        expected_explanation = [ua,ub,ua-ub]
    elif qid in ['pg-5-2-5','pg-5-3-5']:
        pairs = list(zip(n[:6:2],n[1:6:2]))
        rate = pairs[0][1]/pairs[0][0]
        assert all(y/x == rate for x,y in pairs)
        if level == 2:
            fuel, repeat = n[6:]
            assert fuel == repeat and 10 <= rate <= 100
            answer = fuel*rate
            expected_explanation = [rate,answer]
        else:
            target,time,repeat = n[6:]
            assert time == repeat and 10 <= rate <= 100
            answer = time*rate
            expected_explanation = [rate,answer,target/rate]
        truth = [o == [answer] for o in opts]
    elif index == 6:
        a,b,c,d = [n[i] for i in ([1,2,4,5] if level==1 else [0,1,2,3])]
        assert all(x.denominator == 1 and 0 < x <= 250 for x in [a,b,c,d])
        first = opts[0][-2:];second = opts[1][-2:];part = opts[3][-2:]
        chosen = b if level==1 else a
        truth = [simplest(first,a,b),simplest(second,c,d),a/b == c/d,simplest(part,chosen,a+b)]
        assert a/b == c/d
        expected_explanation = reduced(a,b)+reduced(chosen,a+b)
    elif index == 7:
        one, scale, length, width = n
        assert one == 1 and 0 < width < length <= 25
        actual_l, actual_w = length*scale/100,width*scale/100
        assert actual_l <= 45 and actual_w <= 30
        paper, area = length*width,actual_l*actual_w
        assert all(o[-1] == 2 for o in opts[2:])
        truth = [opts[0] == [actual_l],opts[1] == [actual_w],opts[2][0] == (paper if level==1 else area),opts[3][0] == area]
        expected_explanation = [actual_l,actual_w,paper,area]
    elif index == 8:
        a,ta,b,tb = n
        va,vb = a/ta,b/tb
        assert 20 <= va <= 90 and 20 <= vb <= 90
        truth = [opts[0] == [va],opts[1] == [va],opts[2] == [vb],vb > va]
        expected_explanation = [va,vb,va-vb]
    elif index == 9:
        a,pa,b,pb = n
        ua,ub = pa/a,pb/b
        assert pa.denominator == pb.denominator == 1 and min(ua,ub)>0
        truth = [opts[0] == [ua],opts[1] == [ub],ub < ua]
        expected_explanation = [ua,ub,ua-ub]
    elif index == 10:
        pairs = list(zip(n[::2],n[1::2]))
        rate = pairs[0][1]/pairs[0][0]
        assert len(pairs)==3 and all(y/x==rate for x,y in pairs)
        time,production = opts[1];target,duration = opts[2]
        truth = [opts[0] == [rate],production == time*rate,duration == target/rate]
        expected_explanation = [rate,time*rate,target/rate]
    elif qid == 'pg-5-3-2':
        one,scale,old,new = n
        assert one == 1 and new > old
        actual = scale*old
        assert 2000 <= actual <= 4000
        truth = [len(o)==2 and o[0]/o[1] == new/actual for o in opts]
        expected_explanation = [actual,1,actual/new]
    elif qid == 'pg-5-3-1':
        a,b,c,d = n[:4]
        first,second = a/b,c/d
        i = simplest(n[4:6],a,b) and simplest(n[6:8],c,d) and first>second
        ii = simplest(n[8:10],a,b) and simplest(n[8:10],c,d) and first==second
        iii = n[10]/n[11]==first and n[12]/n[13]==second and first!=second
        assert n[14:] == [c,a]
        iv = second>first and c>a
        truth = [i,ii,iii,iv]
        expected_explanation = reduced(a,b)+reduced(c,d)
        relation = 'sama dengan' if first == second else 'lebih besar daripada'
        assert relation in candidate['explanation']
    else:
        raise AssertionError(('unsupported',qid))
    assert [o['correct'] for o in candidate['options']] == truth, (qid,truth,candidate)
    assert numbers(candidate['explanation']) == expected_explanation, (qid,expected_explanation,candidate['explanation'])
    shape = {
        1:'Rasio sederhana = #:#. Kedua '+('panjang' if level==2 else 'volume')+' dibagi faktor yang sama.',
        2:'Jarak denah = jarak sebenarnya dalam cm dibagi skala = # cm.',
        3:'Durasi = # menit. Debit = volume dibagi durasi = # liter/menit.',
        4:'Harga satuan = Rp#. Harga pembelian = jumlah buku dikali harga satuan = Rp#.',
        6:'Rasio sederhana kedua kelompok = #:#. Rasio bagian terhadap seluruh kelompok pertama = #:#.',
        7:'Panjang sebenarnya = # m; lebar sebenarnya = # m. Luas denah = # cm persegi; luas sebenarnya = # m persegi.',
        8:'Kecepatan kendaraan pertama = # km/jam; kendaraan kedua = # km/jam. Selisih kecepatan pertama terhadap kedua = # km/jam.',
        9:'Harga satuan kemasan pertama = Rp#; kemasan kedua = Rp#. Kemasan kedua lebih murah Rp# per satuan.',
        10:'Laju produksi = # satuan/jam. Produksi untuk waktu yang ditanyakan = # satuan. Waktu untuk target pernyataan terakhir = # jam.',
    }.get(index)
    if qid=='pg-5-2-5':shape='Rasio jarak per liter = # km/liter. Jarak = volume dikali rasio = # km.'
    if qid=='pg-5-3-5':shape='Laju cetak = # lembar/menit. Jumlah brosur = # lembar. Waktu untuk baris terakhir = # menit.'
    if qid=='pg-5-3-4':shape='Harga per buku Toko A = Rp#; Toko B = Rp#. Toko B lebih murah Rp# per buku.'
    if qid=='pg-5-3-2':shape='Panjang sebenarnya = # cm. Skala baru = panjang gambar baru dibagi panjang sebenarnya = #:#.'
    if qid=='pg-5-3-1':shape='Rasio sederhana Campuran P = #:#; Campuran Q = #:#. Perbandingan konsentrat terhadap air Campuran P '+relation+' Campuran Q.'
    assert re.sub(NUM,'#',candidate['explanation'])==shape,(qid,candidate['explanation'])
    assert sum(truth) == sum(o['correct'] for o in original['options']), qid
