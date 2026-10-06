"""Rendered-text oracle. No production formulas, templates, or keys are consulted."""
import math
import re
from fractions import Fraction


def ints(text):
    return [int(n) for n in re.findall(r'\d+', text)]


def product(text):
    value = 1
    for factor in text.strip().split('\u00d7'):
        match = re.fullmatch(r'(\d+)(?:\^\((\d+)\))?', factor)
        assert match, text
        prime, exponent = int(match[1]), int(match[2] or 1)
        assert prime >= 2 and all(prime % d for d in range(2, math.isqrt(prime)+1)), text
        value *= prime**exponent
    return value


def time_value(text):
    h, m = map(int, re.search(r'(\d+)\.(\d+)', text).groups())
    assert 0 <= h < 24 and 0 <= m < 60
    return 60*h+m


def clock(n):
    return f'{n//60:02d}.{n%60:02d}'


def check_math(original, candidate):
    qid = original['id']; level = int(qid.split('-')[2]); item = int(qid.split('-')[3])
    s = candidate['stem']; options = candidate['options']; texts = [o['text'] for o in options]
    assert len(options) == len(original['options'])
    assert [o['id'] for o in options] == [o['id'] for o in original['options']]
    if qid == 'pg-4-1-3':
        n = product(re.search(r'prima (.*?)\. Manakah', s)[1]); m = int(re.search(r'bilangan (\d+)\?', s)[1])
        truth = [n % product(t) == m % product(t) == 0 for t in texts]
        explanation = f'N={n}; M={m}; FPB={math.gcd(n,m)}. Faktor persekutuan membagi kedua bilangan.'
    elif qid in ['pg-4-3-2', 'pg-4-3-5']:
        if item == 2:
            a = product(re.search(r'P=(.*?)\n',s)[1]); b = product(re.search(r'Q=(.*?)\n',s)[1]); answer = math.gcd(a,b)
            explanation = f'P={a}; Q={b}; FPB={answer}. Ambil faktor prima sekutu dengan pangkat terkecil.'
        else:
            a = product(re.search(r'X=(.*?) dan',s)[1]); b = product(re.search(r'Y=(.*?)\.',s)[1]); answer = math.lcm(a,b)
            explanation = f'X={a}; Y={b}; KPK={answer}. Ambil seluruh faktor prima dengan pangkat terbesar.'
        truth = [product(t) == answer for t in texts]
    elif qid == 'pg-4-2-4':
        n = int(re.search(r'bilangan (\d+)',s)[1])
        invalid_label = re.search(r'Analisis (II|I): \d+=.*?, sehingga memiliki faktor',s)[1]
        valid_label = re.search(r'Analisis (II|I): \d+=.*?, sehingga seluruh faktor',s)[1]
        assert invalid_label != valid_label
        first = re.search(r'Analisis '+invalid_label+r': (\d+)=(.*?), sehingga memiliki faktor sebanyak (\d+)',s)
        second = re.search(r'Analisis '+valid_label+r': (\d+)=(.*?), sehingga seluruh faktor primanya adalah (.*)\.',s)
        assert int(first[1]) == int(second[1]) == n
        factors = first[2].split('\u00d7'); composite = int(factors[-1])
        first_value = math.prod(int(re.fullmatch(r'(\d+)(?:\^\((\d+)\))?',f)[1])**int(re.fullmatch(r'(\d+)(?:\^\((\d+)\))?',f)[2] or 1) for f in factors)
        assert first_value == n and product(second[2]) == n
        primes = ints(second[3]); assert math.prod(primes)**2 >= n
        actual_primes = [p for p in range(2, math.isqrt(n)+1) if n % p == 0 and all(p % d for d in range(2,math.isqrt(p)+1))]
        assert sorted(primes) == actual_primes
        factor_count = math.prod(int(re.fullmatch(r'(\d+)(?:\^\((\d+)\))?',f)[2] or 1)+1 for f in second[2].split('\u00d7'))
        valid_first = first_value == n and all(all(int(re.match(r'\d+',f)[0]) % d for d in range(2,math.isqrt(int(re.match(r'\d+',f)[0]))+1)) for f in factors) and int(first[3]) == factor_count
        assert ints(texts[0]) == [composite,n] and ints(texts[3]) == [n,composite]
        assert texts == [
            f'Analisis {invalid_label}, karena {composite} merupakan faktor dari {n}',
            f'Analisis {valid_label}, karena faktorisasi prima hanya boleh memuat bilangan prima',
            f'Analisis {invalid_label}, karena penguraiannya lebih cepat dan singkat',
            f'Analisis {valid_label}, karena angka {n} tidak habis dibagi {composite}',
        ]
        truth = [valid_first and n % composite == 0, True, valid_first, n % composite != 0]
        assert [re.search(r'Analisis (II|I)',t)[1] for t in texts] == [invalid_label,valid_label,invalid_label,valid_label]
        explanation = f'N={n}; faktor komposit={composite}; jumlah faktor positif={factor_count}. Analisis {valid_label} menggunakan faktor prima; Analisis {invalid_label} memuat faktor komposit dan salah menghitung jumlah faktor.'
    elif qid in ['pg-4-1-4','pg-4-2-3']:
        intervals = [int(n) for n in re.findall(r'(\d+) menit',s)]; start = time_value(s)
        period = math.lcm(*intervals); answer = start+period
        truth = [time_value(t) == answer for t in texts]
        explanation = f'KPK={period} menit; waktu bersama berikutnya={clock(answer)} WIB.'
    elif qid == 'pg-4-2-1':
        a,b = [int(n) for n in re.findall(r'(\d+) hari sekali',s)]; period=math.lcm(a,b)
        truth = [ints(t) == [period] for t in texts]
        explanation = f'KPK={period} hari. Waktu bersama berikutnya adalah kelipatan bersama positif terkecil.'
    elif item == 6:
        values = ints(s); g = math.gcd(*values); l = math.lcm(*values)
        m = re.fullmatch(r'Faktorisasi prima dari (\d+) adalah (.*?)\.',texts[0]); assert m
        n = int(m[1]); assert n in values
        truth = [product(m[2]) == n, ints(texts[1]) == [g], ints(texts[2]) == [g], ints(texts[3]) == [l]]
        explanation = f'FPB={g}; KPK={l}. Faktorisasi prima pada pernyataan A memiliki hasil kali {n}.'
    elif item == 7:
        a,b = [int(n) for n in re.findall(r'(\d+) detik',s)[:2]]; g = math.gcd(a,b); l=math.lcm(a,b)
        period = ints(texts[0])[0]; fpb=ints(texts[1]); assert fpb[:2] == [a,b]
        truths = []
        durations = []
        for t in texts[2:]:
            d = int(re.search(r'(\d+) detik',t)[1]); count = int(re.search(r'sebanyak (\d+) kali',t)[1]); durations.append(d)
            minutes = re.search(r'(\d+) menit',t)
            if minutes: assert int(minutes[1])*60 == d
            assert 'tidak menghitung detik ke-0' in t
            truths.append(count == d//l)
        assert durations[0] == durations[1]
        duration=durations[0]
        if level==3:
            assert int(re.search(r'(\d+) menit',s)[1])*60 == duration
            assert int(re.findall(r'(\d+) detik',s)[-1]) == duration
        truth = [period==l, fpb[2]==g]+truths
        explanation=f'FPB={g}; KPK={l} detik; durasi={duration} detik; banyak kejadian={duration//l}. Titik awal tidak dihitung.'
    elif qid == 'mcma-4-1-8':
        values=ints(s); g=math.gcd(*values); a,b,c=[v//g for v in values]
        match=re.search(r'FPB dari (\d+), (\d+), dan (\d+) dapat dinyatakan sebagai (.*?)\.',texts[3]); assert match
        assert list(map(int,match.group(1,2,3)))==values
        truth=[ints(texts[0])==[g],ints(texts[1])==[a],ints(texts[2])==[b],product(match[4])==g]
        explanation=f'FPB={g}; isi per kantong: {a} buku, {b} pensil, {c} penggaris.'
    else:
        values=ints(s)[:3 if qid=='pg-4-1-2' else 2];g=math.gcd(*values);ratios=[v//g for v in values];a,b=ratios[:2]
        nums=[ints(t) for t in texts]
        explanation=f'FPB={g}; hasil bagi berurutan: '+', '.join(map(str,ratios))+'. '
        if qid=='pg-4-1-2':truth=[ns==[g] for ns in nums]
        elif qid=='pg-4-1-5':truth=[ns==[a,b] for ns in nums]
        elif qid=='pg-4-3-4':truth=[ns==[g,a] for ns in nums]
        elif qid=='pg-4-3-3':
            analyses = re.findall(r'Analisis [AB]: Dibuat (\d+) wadah, masing-masing berisi ([\d,]+) buku tulis dan ([\d,]+) pulpen',s)
            assert len(analyses)==2
            good=[]
            for count,x,y in analyses:
                x,y=Fraction(x.replace(',','.')),Fraction(y.replace(',','.'));count=int(count)
                assert count*x==values[0] and count*y==values[1]
                good.append(count==g and x.denominator==y.denominator==1)
            assert nums[0]==values+[g]
            truth=[good[0],good[1],good[0] and a>b,good[1] and nums[3][0]%nums[3][1]==0]
            explanation+='Analisis B menghasilkan pecahan barang; Analisis A memakai jumlah wadah maksimum.'
        elif item==8:truth=[nums[0]==[g],nums[1]==[g],nums[2]==[a,b],nums[3]==[a,b]]
        elif item==9:
            truth=[nums[0]==[g],nums[1]==[a if level==1 else b],nums[2]==[abs(a-b) if level==1 else a+b]]
            explanation+=f'Total isi={a+b}; selisih isi={abs(a-b)}.'
        elif item==10:
            if level==1:
                assert nums[1][0]==values[0]
                truth=[nums[0]==[g],nums[1][1]==a,nums[2]==[a+b]]
            else:
                assert nums[2]==[values[1],values[0]]
                truth=[nums[0]==[g],nums[1]==[a+b],b==2*a]
            explanation+=f'Total potongan={a+b}.'
        else:raise AssertionError(qid)
        if item not in [9,10] and qid!='pg-4-3-3':explanation+='Jumlah kelompok maksimum adalah FPB.'
    assert [o['correct'] for o in options] == truth, (qid,texts,truth)
    if original['format']=='PG': assert sum(truth)==1
    assert candidate['explanation'] == explanation, (qid,candidate['explanation'],explanation)
