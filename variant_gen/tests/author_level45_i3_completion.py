"""Offline authoring for the thirteen remaining indicator-3 questions."""
from copy import deepcopy
import re

from build_drill_1_5_level45_batch1 import Author


def prepare(entry, academic):
    out = deepcopy(entry)
    q = out['source_projection']
    n, level = out['source_number'], out['level']
    if n == 5:
        # The terse evaluation duplicated the detailed correct evaluation.  Make
        # its stated subtraction false, leaving the detailed evaluation unique.
        q['stem'] = q['stem'].replace('Selisih panjang diagonal adalah $3m$',
                                      'Selisih panjang diagonal adalah $2m$', 1)
        q['stem'] = q['stem'].replace('10 - 7 = 3', '10 - 7 = 2', 1) if level == 4 else \
                    q['stem'].replace('9 - 6 = 3', '9 - 6 = 2', 1)
        q['explanation'] = ('Pembahasan draft koreksi:\nBulatkan setiap radikan secara terpisah. '
                            'Evaluasi I salah karena menuliskan selisih 2 m. Evaluasi II salah karena '
                            'akar selisih radikan tidak sama dengan selisih akar. Evaluasi III benar '
                            'dan memperlihatkan aproksimasi sebelum pembulatan. Jadi kunci jawaban C.')
        q['key_caption'] = 'C. Evaluasi III (draft koreksi)'
        return out, ['Draft: Evaluasi I dibuat salah secara eksplisit (selisih 2 m); Evaluasi III tetap satu-satunya jawaban benar.',
                     'Istilah yang dipakai adalah radikan, bukan radian.']
    if n == 7 and level == 5:
        # Select the coherent final A--D rewrite embedded in the raw source.
        q['options'] = [
            r'Aproksimasi Sampel A ($\sqrt{18}$) ke persepuluhan terdekat adalah $4,2 cm$.',
            r'Aproksimasi Sampel B ($\sqrt{38}$) ke persepuluhan terdekat adalah $6,2 cm$.',
            r'Sampel C ($\sqrt{70}$) jika dibulatkan ke satuan terdekat adalah $8 cm$.',
            r'Sampel C ($\sqrt{70}$) jika dibulatkan ke satuan terdekat adalah $9 cm$.',
        ]
        q['key'] = ['A', 'B', 'C']
        q['explanation'] = ('Pembahasan draft koreksi: akar 18 dibulatkan ke persepuluhan menjadi 4,2; '
                            'akar 38 menjadi 6,2; dan akar 70 dibulatkan ke satuan menjadi 8. '
                            'Jadi A, B, C benar dan D salah.')
        q['key_caption'] = 'A, B, dan C (versi akhir yang dipilih sebagai draft)'
        return out, ['Draft chooses the clearly labelled final rewrite from the duplicated source; the raw initial and rewrite versions remain in audit provenance.',
                     'The final rewrite has A, B, C true and preserves four MCMA options and three keyed answers.']
    return out, []


def _scale(a, mapping):
    a.allnums({literal: f'({expr})*(k+1)' for literal, expr in mapping.items()})


def author(entry):
    a = Author(entry)
    l, n = a.l, a.n
    a.variables['k']['range'] = [0, 24]
    if n == 3:
        vals = ({'498,6':'498.6','14808,42':'14808.42','2.903,61':'round(498.6*(k+1)*29.7/5.1,2)/(k+1)','400':'400','12000':'12000','2.400':'2400','500':'500','15000':'15000','3.000':'3000'}
                if l == 4 else
                {'598,2':'598.2','18185,28':'18185.28','2.981,19':'round(598.2*(k+1)*30.4/6.1,2)/(k+1)','500':'500','15000':'15000','2.500':'2500','600':'600','18000':'18000','3.000':'3000'})
        _scale(a, vals)
        real = ('round(498.6*(k+1)*29.7/5.1,2)' if l == 4 else
                'round(598.2*(k+1)*30.4/6.1,2)')
        a.exp = a.explanation('Hitung nilai riil = [[%s]]. Estimasi bawah = [[%s]], estimasi dekat = [[%s]]. '
                              'Galat mutlak estimasi dekat lebih kecil, sehingga opsi B benar.' %
                              ((real,'2400*(k+1)','3000*(k+1)') if l == 4 else
                               (real,'2500*(k+1)','3000*(k+1)')))
        a.answer_value(1, ('3000*(k+1)' if l == 4 else '3000*(k+1)'), ' (estimasi terdekat)')
    elif n == 4:
        vals = ({'19.800':'19800','10.000':'10000','20.000':'20000','400.000':'400000','1.000.000':'1000000','970.200':'970200'} if l == 4 else
                {'24.800':'24800','20.000':'20000','25.000':'25000','600.000':'600000','1.000.000':'1000000','967.200':'967200'})
        _scale(a, vals)
        a.exp = a.explanation('Total riil = [[%s]]. Usulan bawah = [[%s]] dan batas atas = [[1000000*(k+1)]]. '
                              'Batas atas melebihi total riil dan paling dekat; Evaluasi II (opsi B) benar.' %
                              (('970200*(k+1)','400000*(k+1)') if l == 4 else ('967200*(k+1)','600000*(k+1)')))
        a.answer_value(1, '1000000*(k+1)', ' (batas atas)')
    elif n == 5:
        lo, hi = ((45,98) if l == 4 else (35,82))
        rlo, rhi = ((7,10) if l == 4 else (6,9))
        lo_rad = a.var(f'{lo}*(k+1)**2', str(lo))
        hi_rad = a.var(f'{hi}*(k+1)**2', str(hi))
        diff_rad = a.var(f'({hi}-{lo})*(k+1)**2', str(hi-lo))
        a.stem = re.sub(
            rf'\\sqrt\{{\s*{hi}-{lo}\s*\}}\s*=\s*\\sqrt\{{\s*{hi-lo}\s*\}}',
            rf'\\sqrt{{{hi_rad}-{lo_rad}}}=\\sqrt{{{diff_rad}}}', a.stem)
        a.stem = re.sub(rf'(?<=\\sqrt\{{){lo}(?=\s*\}})', lo_rad, a.stem)
        a.stem = re.sub(rf'(?<=\\sqrt\{{){hi}(?=\s*\}})', hi_rad, a.stem)
        low=f'round(sqrt({lo})*(k+1))'; high=f'round(sqrt({hi})*(k+1))'; delta=f'({high})-({low})'
        a.allnums({str(rlo):low, str(rhi):high, '3':delta, '2':f'({delta})-1'})
        approx = ({'9,899':'sqrt(98)*(k+1)', '6,708':'sqrt(45)*(k+1)'} if l == 4 else
                  {'9,055':'sqrt(82)*(k+1)', '5,916':'sqrt(35)*(k+1)'})
        a.stem = a.nums(a.stem, approx)
        a.exp = a.explanation(f'Bulatkan setiap akar secara terpisah: akar pertama = [[{low}]] m dan akar kedua = [[{high}]] m. '
                              f'Selisih benar = [[{delta}]] m. Evaluasi I menyatakan [[({delta})-1]] m dan salah; Evaluasi III benar. Radikan tidak boleh dikurangkan sebelum diakar.')
        a.answer_value(2, delta, ' m')
    elif n == 7:
        roots = ([(15,3.9),(35,5.9),(80,9)] if l == 4 else [(18,4.2),(38,6.2),(70,8)])
        for rad, shown in roots:
            token = a.var(f'{rad}*(k+1)**2', str(rad))
            a.stem = re.sub(rf'(?<=\\sqrt\{{){rad}(?=\s*\}})', token, a.stem)
            a.options = [re.sub(rf'(?<=\\sqrt\{{){rad}(?=\s*\}})', token, x) for x in a.options]
            lit = str(shown).replace('.', ',')
            places = 1 if rad != roots[2][0] else 0
            a.options = [a.nums(x, {lit:f'round(sqrt({rad})*(k+1),{places})'}) for x in a.options]
        a.exp = a.explanation('Akar pertama dan kedua dibulatkan half-up ke persepuluhan; akar ketiga dibulatkan ke satuan. '
                              f'Hasilnya [[round(sqrt({roots[0][0]})*(k+1),1)]], [[round(sqrt({roots[1][0]})*(k+1),1)]], dan [[round(sqrt({roots[2][0]})*(k+1))]]. '
                              + ('A, B, D benar.' if l == 4 else 'A, B, C benar.'))
    elif n == 8:
        vals = ({'14.500':'14500','9.800':'9800','15.000':'15000','10.000':'10000','9.000':'9000','450.000':'450000','200.000':'200000','650.000':'650000','90.000':'90000','290.000':'290000'} if l == 4 else
                {'19.500':'19500','4.800':'4800','20.000':'20000','5.000':'5000','10.000':'10000','4.000':'4000','800.000':'800000','100.000':'100000','900.000':'900000','300.000':'300000','40.000':'40000','340.000':'340000'})
        _scale(a, vals)
        real = '606700*(k+1)' if l == 4 else '851700*(k+1)'
        upper = '650000*(k+1)' if l == 4 else '900000*(k+1)'
        lower = '290000*(k+1)' if l == 4 else '340000*(k+1)'
        a.exp = a.explanation(f'Total riil = [[{real}]]. Model I = [[{upper}]] adalah batas atas; Model II = [[{lower}]] berada di bawah. B dan C benar; A dan D salah.')
    elif n == 10:
        x,y,rx,ry,bad = ((22,68,4.7,8,12) if l == 4 else (27,75,5.2,9,13))
        for rad in (x,y):
            token=a.var(f'{rad}*(k+1)**2',str(rad))
            a.stem=re.sub(rf'(?<=\\sqrt\{{){rad}(?=\s*\}})',token,a.stem)
            a.options=[re.sub(rf'(?<=\\sqrt\{{){rad}(?=\s*\}})',token,z) for z in a.options]
        ex=f'round(sqrt({x})*(k+1),1)'; ey=f'round(sqrt({y})*(k+1))'; total=f'round(sqrt({x})*(k+1))+round(sqrt({y})*(k+1))'
        a.options=[a.nums(z,{str(rx).replace('.',','):ex,str(ry):ey,str(bad):f'({total})-1'}) for z in a.options]
        a.exp=a.explanation(f'Akar pertama ke persepuluhan = [[{ex}]], akar kedua ke satuan = [[{ey}]]. '
                            f'Jumlah pembulatan satuan = [[{total}]], bukan [[({total})-1]]. Pernyataan 1 dan 2 benar.')
    elif n == 2:
        # For k>0 both integer radicands are chosen nearest to the square of the
        # displayed tenth.  This preserves both the rounding result and the
        # source option's nearest-square justification over the whole domain.
        x='(53 if k==0 else round((10.3+k)**2))'; y='(54 if k==0 else round((10.3+k)**2)+(1 if round((10.3+k)**2)<(10.3+k)**2 else -1))'; ra=f'round(sqrt({x}),1)'; rb=f'round(sqrt({y}),1)'
        mapping={'53':x,'54':y,'7,2':f'{ra}-0.1','7,3':rb,'7,4':f'{rb}+0.1','51,84':f'({ra}-0.1)**2','53,29':f'({rb})**2','54,76':f'({rb}+0.1)**2'}
        a.stem=a.nums(a.stem,mapping)
        special={'7,{2}':a.var(f'{ra}-0.1','7,{2}'),'7,{3}':a.var(rb,'7,{3}'),'7,{4}':a.var(f'{rb}+0.1','7,{4}')}
        a.options=[a.nums(x.replace('7,{2}',special['7,{2}']).replace('7,{3}',special['7,{3}']).replace('7,{4}',special['7,{4}']),mapping) for x in a.options]
        shown_x, shown_y = a.var(x, '53'), a.var(y, '54')
        a.exp=a.explanation(f'Gunakan batas tengah pembulatan, bukan jarak nilai kuadrat: '
                            f'sqrt({shown_x}) = [[{ra}]] dan sqrt({shown_y}) = [[{rb}]] '
                            'ke persepuluhan. Evaluasi Y, opsi C, benar.')
        a.answer_value(2, rb, ' m')
    else:
        raise AssertionError(a.qid)
    return a
