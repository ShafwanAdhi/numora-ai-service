"""Independent rendered-text oracle for indicator 4-5 completion families."""
import math
import re
from datetime import datetime, timedelta
from fractions import Fraction


def _numbers(text):
    # Indonesian thousands separators and decimal commas are normalized exactly.
    found = re.findall(r'(?:(?<![\w])|(?<=Rp))\d+(?:\.\d{3})*(?:,\d+)?', text)
    return [Fraction(x.replace('.', '').replace(',', '.')) for x in found]


def _assert_explanation(exp, words, values):
    low = exp.lower()
    assert any(w.lower() in low for w in words), (words, exp)
    normalized = exp.replace('.', '').replace(',', '.')
    for value in values:
        assert str(value) in normalized, (value, exp)

def _intnums(text):
    return [int(x) for x in _numbers(text) if x.denominator == 1]

def _assert_inline_equalities(text):
    """Reject a corrupted displayed arithmetic step, including intermediate work."""
    n=r'\d+(?:\.\d{3})*(?:,\d+)?'
    for left,op,right,shown in re.findall(rf'({n})\s*([×÷+\-])\s*({n})\s*=\s*({n})',text):
        x,y,z=(_numbers(v)[0] for v in (left,right,shown))
        actual={'+':x+y,'-':x-y,'×':x*y,'÷':x/y}[op]
        assert actual==z,(left,op,right,shown,text)

def _selected_report(option):
    """Return the report/evaluation labels asserted by a qualitative PG option."""
    labels=[]
    for x in re.findall(r'(?:Evaluasi|Proposal|Alternatif|Laporan Regu)\s+([ABCXYZI]+)',option):
        if x not in labels: labels.append(x)
    return set(labels)


def check_math(qid, candidate):
    """Recompute the governing quantity from displayed data, then verify all key flags."""
    _, indicator, level, number = qid.split('-')
    indicator, level, number = map(int, (indicator, level, number))
    stem = candidate['stem']
    opts = [o['text'] for o in candidate['options']]
    exp = candidate['explanation']
    for text in opts:
        for match in re.finditer(r'(FPB|KPK)\((\d+(?:,\d+)+)\)(?:=(\d+(?:\.\d{3})*))?',text):
            operands=list(map(int,match[2].split(',')))
            assert set(operands)<=set(_numbers(stem)),(qid,'stale function operands',operands)
            value=(math.gcd(*operands) if match[1]=='FPB' else math.lcm(*operands))
            if match[3]: assert value==_numbers(match[3])[0],(qid,match[0])
    _assert_inline_equalities(stem+'\n'+exp)
    expected_exp = None
    answer = None

    if indicator == 4:
        if number == 2:
            # Evaluate every displayed factorization option against the exact gcd.
            lines = re.findall(r'\$[MNPQ]=([^$]+)\$', stem)
            assert len(lines) >= 2
            def factor_value(t):
                pairs = re.findall(r'(\d+)\}\^\{(\d+)', t)
                if not pairs:
                    pairs = re.findall(r'(\d+)\^\{?(\d+)', t)
                value = 1
                for p, e in pairs:
                    value *= int(p) ** int(e)
                for p in re.findall(r'×(\d+)(?![}\^])', t):
                    value *= int(p)
                return value
            a, b = map(factor_value, lines[:2]); target = math.gcd(a, b)
            truths = ([factor_value(t) == target for t in opts] if level == 4
                      else [True, False, False, False])
            assert sum(truths) == 1
            _assert_explanation(exp, ['FPB'], [target])
            answer=target
            if number==2:
                value=target; powers=[]
                for prime in (2,3):
                    exponent=0
                    while value%prime==0:
                        value//=prime; exponent+=1
                    powers.append(exponent)
                assert value==1
                expected_exp=[2,3,*powers,2,powers[0],3,powers[1],target]
            else: expected_exp=[target]
        elif number in (3, 4, 8, 9, 10):
            ns = [int(x) for x in _numbers(stem)[:2]]
            a, b = ns[:2]; target = math.gcd(a, b)
            assert a % target == b % target == 0
            if number == 3:
                assert target in [int(x) for x in _numbers(' '.join(opts))]
                # A is the only proposal whose group count is the gcd and whose
                # two displayed per-bag counts equal the two exact quotients.
                truths=[]
                for o in opts:
                        ns=_intnums(o)
                        truths.append(target in ns and 'FPB' in o and ('bulat' in o or 'valid' in o))
            elif number == 4:
                assert target in [int(x) for x in _numbers(stem)[2:]], stem
                reports={}
                for label,body in re.findall(r'(?:Klaim Regu|Regu)\s+(\w+):\s*"([^"]+)"',stem):
                    ns=_intnums(body); reports[label]=target in ns and a//target in ns and b//target in ns
                truths=[]
                for o in opts:
                    named=next((x for x in reports if x in o),None); ons=_intnums(o)
                    direct=target in ons and a//target in ons and b//target in ons
                    truths.append(named is not None and (direct or reports[named]) and ('sama-sama' not in o))
            elif number == 8:
                assert target in [int(x) for x in _numbers(' '.join(opts))]
                groups={x:int(y) for x,y in re.findall(r'Opsi (I+):[^$]*\$(\d+)\$',stem)}
                truths=[]
                for o in opts:
                    ns=_intnums(o)
                    if 'terbanyak' in o: truths.append(target in ns)
                    elif 'masing-masing' in o or 'berisi' in o:
                        label=re.search(r'Opsi (I+)',o); g=groups[label[1]] if label else ns[0]
                        truths.append(g==target and ns[-2:]==[a//g,b//g])
                    else: truths.append(False)
            elif number == 9:
                assert (a + b) // target in [int(x) for x in _numbers(' '.join(opts))]
                truths=[]
                for o in opts:
                    ns=_intnums(o)
                    if 'terbanyak' in o: truths.append(target in ns)
                    elif 'Total' in o: truths.append((a+b)//target in ns)
                    elif 'biskuit' in o: truths.append(b//target in ns)
                    else: truths.append((a+b)//target in ns)
            else:
                assert target in [int(x) for x in _numbers(' '.join(opts))]
                truths=[]
                for o in opts:
                    ns=_intnums(o)
                    if 'terpanjang' in o: truths.append(target in ns)
                    elif 'seluruh' in o: truths.append((a+b)//target in ns)
                    else: truths.append(b//target==2*(a//target))
            _assert_explanation(exp, ['FPB'], [target])
            answer=target
            if number==2:
                value=target; powers=[]
                for prime in (2,3):
                    exponent=0
                    while value%prime==0:
                        value//=prime; exponent+=1
                    powers.append(exponent)
                assert value==1
                expected_exp=[2,3,*powers,2,powers[0],3,powers[1],target]
            else: expected_exp=[target]
        elif number == 5:
            dims = [int(x) for x in _numbers(stem)[:3]]
            if level == 4:
                period = math.lcm(*dims)
                truths = [period in [int(x) for x in _numbers(t)] for t in opts]
            else:
                baseline = math.lcm(dims[0], dims[1])
                values=[int(x) for x in _numbers(stem)]
                proposal1, proposal2 = math.lcm(values[2],values[3]), math.lcm(values[4],values[5])
                period = baseline
                truths=[]
                for o in opts:
                    ns=_intnums(o)
                    if 'Kebijakan I ' in o: truths.append(proposal1>baseline and proposal1 in ns)
                    elif 'Kebijakan II ' in o: truths.append(proposal2>baseline and proposal2 in ns)
                    elif 'Kedua' in o: truths.append(proposal1>baseline and proposal2>baseline)
                    else: truths.append(proposal1<baseline and proposal2<baseline and all(x in ns for x in (proposal1,proposal2,baseline)))
            _assert_explanation(exp, ['KPK'], [period])
            answer=period
            expected_exp=([period,60,12,60,15,60,20,60] if level==4 else [baseline,proposal1,proposal2])
        elif number == 7:
            for hour,minute in re.findall(r'(\d+) jam \((\d+) menit\)',stem+' '.join(opts)):
                assert int(hour)*60==int(minute)
            for minute,second in re.findall(r'(\d+)\$?\s*menit\s*\(\$?(\d+)\$?\s*detik',stem):
                assert int(minute)*60==int(second)
            periods = [int(x) for x in re.findall(r'setiap \$(\d+)\$', stem)]
            if len(periods) < 2:
                periods = [int(x) for x in _numbers(stem)[:2]]
            period = math.lcm(*periods[:2])
            spans=[int(v) for chunk in re.findall(r'\(([^)]*(?:menit|detik)[^)]*)\)',stem+' '.join(opts)) for v in _numbers(chunk)]
            if not spans:
                spans=[int(_numbers(x)[0]) for x in re.findall(r'selang waktu (\d+(?:\.\d{3})*) menit',' '.join(opts))]
            assert spans,qid
            duration=max(spans)
            assert duration // period in [int(x) for x in _numbers(' '.join(opts))]
            _assert_explanation(exp, ['KPK', 'frekuensi'], [period])
            count=duration//period; gcd=math.gcd(*periods[:2]); truths=[]
            expected_exp=[period,duration,period,count]
            for o in opts:
                ns=_intnums(o)
                if 'setiap' in o: truths.append(period in ns)
                elif 'FPB' in o:
                    match=re.search(r'FPB\((\d+),(\d+)\)=(\d+)',o); assert match
                    left,right,shown=map(int,match.groups())
                    assert (left,right)==tuple(periods[:2])
                    truths.append(math.gcd(left,right)==shown)
                elif 'sebanyak' in o:
                    claimed=int(re.search(r'sebanyak\s+(\d+)',o)[1]); truths.append(claimed==count)
                else:
                    start=re.search(r'pukul\s+(\d{2})\.(\d{2})',stem)
                    end=re.search(r'pukul\s+(\d{2})\.(\d{2})',o)
                    expected=datetime(2000,1,1,int(start[1]),int(start[2]))+timedelta(minutes=period)
                    truths.append((int(end[1]),int(end[2]))==(expected.hour,expected.minute))
        elif number == 6:
            raise AssertionError('out of assigned scope')
        else:
            raise AssertionError(qid)
    else:
        if number == 2:
            vals = [int(x) for x in _numbers(stem)]
            assert vals[0] == 1
            scale, old, new = vals[1], vals[2], vals[3]
            target = scale * old // new
            shown_options = [int(x) for x in _numbers(' '.join(opts))]
            # Some evaluative PG options name reports only; the computed scale is then in the stem.
            assert target in shown_options or target in [int(x) for x in _numbers(stem)]
            _assert_explanation(exp, ['skala'], [target])
            expected_exp=[scale*old,target]; answer=target
            if level==4: truths=[target in _numbers(o) for o in opts]
            else:
                reports={label:(target in _intnums(body)) for label,body in re.findall(r'Evaluasi (I+):\s*"([^"]+)"',stem)}
                truths=[len(_selected_report(o))==1 and reports.get(next(iter(_selected_report(o))),False) for o in opts]
        elif number == 3:
            vals = [int(x) for x in _numbers(stem)]
            volume1, time1, volume2, time2 = vals[:4]
            q1, q2 = Fraction(volume1, time1), Fraction(volume2, time2)
            target = abs(q2 - q1)
            displayed = [int(x) for x in _numbers(stem + ' '.join(opts))]
            assert target.denominator == 1 and int(target) in displayed
            assert 'mula-mula kosong' in stem and 'tidak bocor' in stem
            _assert_explanation(exp, ['debit'], [int(target)])
            expected_exp=[q1,q2,target]; answer=target
            if level==4: truths=[target in _numbers(o) for o in opts]
            else:
                reports={'A':q1>q2,'B':q2>q1 and all(x in _numbers(stem) for x in (q1,q2,target))}
                truths=[any(label in o and ok for label,ok in reports.items()) and 'sama' not in o for o in opts]
        elif number == 4:
            rows = re.findall(r'berisi \$(\d+)\$.*?Rp([\d.]+)(?:,00)?', stem)
            assert len(rows) == 2
            units = [Fraction(int(p.replace('.', '')), int(n)) for n, p in rows]
            saving = abs(units[0] - units[1])
            assert units[1] < units[0]
            assert int(saving) in [int(x) for x in _numbers(stem + ' '.join(opts))]
            _assert_explanation(exp, ['harga'], [int(units[0]), int(units[1]), int(saving)])
            expected_exp=[*units,saving]; answer=saving
            labels=('A','B') if level==4 else ('X','Y'); correct_label=labels[1]
            truths=[_selected_report(o)=={correct_label} for o in opts]
        elif number in (5, 10):
            vals = [int(x) for x in _numbers(stem)]
            if number == 5:
                pairs = vals[:6]; target_output = vals[7]
                rates = [Fraction(pairs[j + 1], pairs[j]) for j in range(0, 6, 2)]
                assert len(set(rates)) == 1
                target_time = Fraction(target_output, rates[0])
                assert target_time.denominator == 1
                _assert_explanation(exp, ['laju', 'konstanta'], [int(rates[0]), int(target_time)])
                expected_exp=[rates[0],target_time]; answer=target_time
                correct_label='III' if level==4 else 'II'
                truths=[_selected_report(o)=={correct_label} for o in opts]
            else:
                pairs = vals[:6]
                rates = [Fraction(pairs[j + 1], pairs[j]) for j in range(0, 6, 2)]
                assert len(set(rates)) == 1
                _assert_explanation(exp, ['laju'], [int(rates[0])])
                expected_exp=[rates[0]]
                output10=10*rates[0]; requested=_intnums(opts[2])[0]
                needed=Fraction(requested,rates[0])
                truths=[rates[0] in _numbers(opts[0]),output10 in _numbers(opts[1]),needed in _numbers(opts[2])]
        elif number == 7:
            vals = [int(x) for x in _numbers(stem)]
            assert vals[0] == 1
            scale, length, width = vals[1:4]
            real_l = Fraction(length * scale, 100); real_w = Fraction(width * scale, 100)
            area = real_l * real_w
            assert all(x.denominator == 1 for x in (real_l, real_w, area))
            _assert_explanation(exp, ['luas'], [int(real_l), int(real_w), int(area)])
            expected_exp=[real_l,real_w,area,2]
            truths=[]
            for o in opts:
                ns=_numbers(o)
                if 'Panjang' in o: truths.append(real_l in ns)
                elif 'Lebar' in o: truths.append(real_w in ns)
                else: truths.append(area in ns)
        elif number == 8:
            vals = _numbers(stem)
            # Parenthetical hour/minute restatement follows the four governing data.
            d1, t1, d2, t2 = vals[:4]
            v1, v2 = d1 / t1, d2 / t2
            assert v1 == v2
            _assert_explanation(exp, ['kecepatan'], [int(v1), int(v2)])
            expected_exp=[v1,v2]
            truths=[]
            for o in opts:
                ns=_numbers(o)
                if 'lebih cepat' in o: truths.append(v2>v1)
                elif (' K ' in o or ' P ' in o): truths.append(v1 in ns)
                else: truths.append(v2 in ns)
        else:
            raise AssertionError(qid)

    assert expected_exp is not None,qid
    assert _numbers(exp)==expected_exp,(qid,_numbers(exp),expected_exp)
    for option in opts:
        for shown in re.findall(r'(?:dengan hasil|hasil:)\s*(\d+(?:\.\d{3})*(?:,\d+)?)',option):
            assert answer is not None and _numbers(shown)[0]==answer,(qid,shown,answer)
    assert [o['correct'] for o in candidate['options']] == truths,(qid,truths)
    return [o['correct'] for o in candidate['options']]
