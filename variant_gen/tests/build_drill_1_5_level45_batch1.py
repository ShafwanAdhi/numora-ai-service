"""Offline, reproducible import/config authoring for the approved first 33 questions.

Uses the existing config language; no runtime evaluator or service changes.
Original prose and numeric typography are retained at original_values.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from expr import placeholders
from test_drill_1_5_level45_batch1 import SELECTION, DATA

AUDIT = REPO / 'docs/audits/2026-10-19-original-question-audit'
def safe_algebra(text):
    # Equivalent display normalization; raw DOCX/projection is kept in metadata.
    return re.sub(r'\\+frac\{a\}\{b\}', '(a)/(b)', text)


NUMBER = re.compile(r'(?:(?<![\w.,])|(?<=Rp))(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?!\d|[.,]\d)')


class Author:
    def __init__(self, entry):
        self.entry = entry
        self.s = entry['source_projection']
        self.i, self.l, self.n = (entry[x] for x in ('indicator', 'level', 'source_number'))
        self.qid = f'{self.s["format"].lower()}-{self.i}-{self.l}-{self.n}'
        self.variables = {'k': {'gen': 'range', 'range': [0, 30], 'fmt': 'raw'}}
        self.cache = {}
        self.constraints = []
        self.stem = safe_algebra(self.s['stem'])
        self.options = [safe_algebra(t) for t in self.s['options']]
        self.correct = [str(j+1) in self.s['key'] if self.s['format'] == 'KATEGORI'
                        else chr(65+j) in self.s['key'] for j in range(len(self.options))]

    def var(self, expr, literal=None, decimals=6):
        key = (expr, literal, decimals)
        if key not in self.cache:
            name = f'v{len(self.cache)}'
            expression = f'{literal!r} if k == 0 else ({expr})' if literal is not None else expr
            assert len(expression) <= 300, (self.qid, expression)
            self.variables[name] = dict(gen='derived', expr=expression, fmt='id', decimals=decimals)
            self.cache[key] = name
        return '{' + self.cache[key] + '}'

    def nums(self, text, mapping):
        def sub(m):
            key = m[0] if m[0] in mapping else m[0][:-3] if m[0].endswith(',00') else m[0]
            return self.var(mapping[key], m[0]) if key in mapping else m[0]
        return NUMBER.sub(sub, text)

    def allnums(self, mapping):
        self.stem = self.nums(self.stem, mapping)
        self.options = [self.nums(t, mapping) for t in self.options]

    def swap_reports(self, word='Evaluasi', first='I', second='II'):
        self.stem = re.sub(rf'\b{word} ({second}|{first})(?![IVX\w])',
                           lambda m: word + ' ' + self.var(
                               repr(second if m[1] == first else first), m[1]), self.stem)
        # The correct claim moves with its numeric content; options are not shuffled.
        self.correct = ['k != 0', 'k == 0', False, False]

    def answer_value(self, option_index, expression, suffix=''):
        # Include the calculated mathematical result in an otherwise qualitative rationale.
        self.options[option_index] += (self.var("' (hasil: '", '') +
                                      self.var(expression, '') +
                                      self.var(repr(suffix + ')'), ''))

    def explanation(self, text):
        return re.sub(r'\[\[([^\]]+)\]\]', lambda m: self.var(m[1]), text)

    def config(self, orig):
        # Literal algebraic LaTeX groups such as \\frac{a}{b} are not parameters.
        for text in [self.stem, *self.options, self.exp]:
            for name in placeholders(text) - self.variables.keys():
                assert name in {'a', 'b', 'Z'}, (self.qid, name)
                self.variables[name] = dict(gen='derived', expr=repr(name))
        return dict(question_id=self.qid, config_version=1, original_hash=orig['hash'],
                    original_values={'k': 0}, variables=self.variables, constraints=self.constraints,
                    stem=self.stem, options=[dict(id=o['id'], text=t, correct=c)
                                           for o, t, c in zip(orig['options'], self.options, self.correct)],
                    explanation=self.exp, shuffle=False, max_draws=1000)


def author(e):
    a = Author(e)
    i, l, n = a.i, a.l, a.n
    if i == 1 and n == 2:
        # Non-original radicands are perfect squares: classification really changes.
        r = '(5 if k == 0 else (k+1)**2)'
        a.allnums({'20': f'4*{r}', '5': r, '0,272727': '(27+k)*10101/1000000'})
        # Repeated block is kept exactly equal in all three visible repetitions.
        a.stem = a.stem.replace(a.var('(27+k)*10101/1000000', '0,272727'),
                                '0,' + a.var('27+k', '27') * 3)
        a.correct = [False, 'k != 0', 'k == 0', False]
        a.exp = a.explanation('Sederhanakan x dengan mengeluarkan faktor kuadrat sempurna. '
                             'Radikan dasar = [[' + r + ']]. '
                             'x = sqrt([[' + r + ']]). Desimal berulang selalu rasional. '
                             'Untuk radikan kuadrat sempurna x rasional; selain itu x irasional. '
                             'Bilangan y rasional karena blok berulang [[27+k]]/99.')
    elif i == 1 and n == 3:
        a.allnums({'18': '18+k', '20.000': '20000+500*k', '2.500': '2500+100*k'})
        a.exp = a.explanation('Sifat distributif: a*b+a*c=a*(b+c). '
                             'Biaya = [[18+k]] * ([[20000+500*k]] + [[2500+100*k]]) '
                             '= [[(18+k)*(22500+600*k)]]. Opsi A benar; B, C, D tidak memodelkan kedua pembelian.')
    elif i == 1 and n == 6:
        if l == 4:
            a.allnums({'16': '(4+k)**2', '15': '15+k', '3,75': '(15+k)/4'})
            # Only the negative integer is changed; denominators 4 remain constant.
            a.stem = a.stem.replace('-4;', '-' + a.var('4+k', '4') + ';')
            a.options[0] = a.options[0].replace('-4$', '-' + a.var('4+k', '4') + '$')
            a.exp = a.explanation('A benar: -[[4+k]] = -[[4+k]]/1, bilangan bulat rasional. '
                                 'B salah: sqrt([[(4+k)**2]]) = [[4+k]], rasional. '
                                 'C benar: [[15+k]]/4 = [[(15+k)/4]], desimal berhenti. '
                                 'D benar: pi irasional.')
        else:
            a.allnums({'6': '6+k', '25': '(5+k)**2', '22': '22+k'})
            a.exp = a.explanation('A benar: -[[6+k]] adalah bilangan bulat rasional. '
                                 'B salah: sqrt([[(5+k)**2]]) = [[5+k]], bukan irasional. '
                                 'C benar: [[22+k]]/7 adalah pecahan rasional. D benar: sqrt(2) irasional.')
    elif i == 1 and n == 9:
        if l == 4:
            a.allnums({'1,75': '1.75*(k+1)', '1,80': '1.8*(k+1)', '9': '9*(k+1)'})
            # sqrt radicand 3 changes, but source statement numbers are untouched.
            for attr in ('stem',):
                a.stem = re.sub(r'(?<=sqrt\{)3(?=\s*\})', lambda m: a.var('3*(k+1)**2', '3'), a.stem)
            a.exp = a.explanation('B = -[[9*(k+1)]]/5 = [[-1.8*(k+1)]]. '
                                 'A = [[-1.75*(k+1)]]. C = -sqrt([[3*(k+1)**2]]). '
                                 'Karena (7/4)^2 > 3, maka B < A < C untuk skala positif. '
                                 'Pernyataan 1 dan 3 benar; 2 salah karena A lebih hangat daripada B.')
        else:
            a.allnums({'2,25': '2.25*(k+1)', '9': '9*(k+1)', '2,236': 'round(sqrt(5)*(k+1),3)'})
            a.stem = re.sub(r'(?<=sqrt\{)5(?=\s*\})', lambda m: a.var('5*(k+1)**2', '5'), a.stem)
            a.options = [re.sub(r'(?<=sqrt\{)5(?=\s*\})', lambda m: a.var('5*(k+1)**2', '5'), t) for t in a.options]
            a.exp = a.explanation('Sampel 1 = Sampel 2 = [[-2.25*(k+1)]]. '
                                 'Sampel 3 = -sqrt([[5*(k+1)**2]]). '
                                 'Karena (9/4)^2 > 5 dan skala positif, Sampel 1 = Sampel 2 < Sampel 3. '
                                 'Pernyataan 1 dan 3 benar; 2 salah, Sampel 3 lebih hangat.')
    elif i == 1 and n == 1:
        a.allnums({'1,95': '1.95*(k+1)', '9': '9*(k+1)'})
        a.stem = re.sub(r'(?<=sqrt\{)3(?=\s*\})', lambda m: a.var('3*(k+1)**2', '3'), a.stem)
        a.swap_reports()
        a.exp = a.explanation('P = [[-1.95*(k+1)]], R = -[[9*(k+1)]]/5, Q = -sqrt([[3*(k+1)**2]]). '
                             'Karena 1,95 > 1,8 > sqrt(3), untuk skala positif urutannya P < R < Q. '
                             'Evaluasi yang memuat urutan P, R, Q adalah yang benar.')
    elif i == 2 and n == 4:
        a.allnums({'4,5': '4.5+0.5*k', '9,5': '9.5+k', '9': '9+k',
                   '2,75': '2.75+0.25*k', '11': '11+k'})
        a.answer_value(0, '9.5+k')
        a.exp = a.explanation('Pembagian dan perkalian mendahului penjumlahan. '
                             '[[4.5+0.5*k]] : 0,5 = [[9+k]], 2 * 0,25 = 0,5. '
                             'Hasil benar = [[9.5+k]]. Hasil cara berurutan yang keliru = [[2.75+0.25*k]]. '
                             'Hanya Evaluasi I beserta alasannya yang benar.')
    elif i == 2 and n == 6:
        if l == 4:
            a.stem = a.stem.replace('2\\sqrt{48}', a.var('2+k', '2') + r'\sqrt{48}')
            a.options[0] = a.nums(a.options[0], {'2': '2+k', '8': '4*(2+k)'})
            a.options[3] = a.nums(a.options[3], {'5': '4*(2+k)-3'})
            a.exp = a.explanation('sqrt(48)=4*sqrt(3), sqrt(75)=5*sqrt(3), sqrt(12)=2*sqrt(3). '
                                 'Koefisien suku pertama = [[4*(2+k)]]. '
                                 'Koefisien akhir = [[4*(2+k)]] - 5 + 2 = [[4*(2+k)-3]]. '
                                 'A, C, D benar; B salah karena sqrt(75) bukan 3*sqrt(5).')
        else:
            a.stem = a.stem.replace('3\\sqrt{32}', a.var('3+k', '3') + r'\sqrt{32}')
            a.options[0] = a.nums(a.options[0], {'3': '3+k', '12': '4*(3+k)'})
            a.options[3] = a.nums(a.options[3], {'10': '4*(3+k)-2'})
            a.exp = a.explanation('sqrt(32)=4*sqrt(2), sqrt(50)=5*sqrt(2), sqrt(18)=3*sqrt(2). '
                                 'Koefisien suku pertama = [[4*(3+k)]]. '
                                 'Koefisien akhir = [[4*(3+k)]] - 5 + 3 = [[4*(3+k)-2]]. '
                                 'A, C, D benar; B salah karena sqrt(50) bukan 2*sqrt(5).')
    elif i == 2 and n == 8:
        if l == 4:
            p, q, d, x, y = '12500+500*k', '3500+100*k', '5000+100*k', 4, 6
            mapping = {'12.500': p, '3.500': q, '5.000': d, '50.000': f'{x}*({p})',
                       '21.000': f'{y}*({q})', '71.000': f'{x}*({p})+{y}*({q})',
                       '66.000': f'{x}*({p})+{y}*({q})-({d})', '12.506': f'({p})+{y}',
                       '175.079.000': f'{x}*(({p})+{y})*({q})-({d})'}
        else:
            p, q, d, x, y = '8000+200*k', '15000+500*k', '10000+100*k', 5, 4
            mapping = {'8.000': p, '15.000': q, '10.000': d, '40.000': f'{x}*({p})',
                       '60.000': f'{y}*({q})', '100.000': f'{x}*({p})+{y}*({q})',
                       '90.000': f'{x}*({p})+{y}*({q})-({d})', '8.004': f'({p})+{y}',
                       '600.290.000': f'{x}*(({p})+{y})*({q})-({d})'}
        a.allnums(mapping)
        a.exp = a.explanation(f'Belanja pertama = [[{x}*({p})]]. Belanja kedua = [[{y}*({q})]]. '
                             f'Sebelum potongan = [[{x}*({p})+{y}*({q})]]. Potongan = [[{d}]]. '
                             f'Pengeluaran akhir = [[{x}*({p})+{y}*({q})-({d})]]. '
                             'Model pertama benar; model kedua salah menggabungkan jumlah dan harga. '
                             'A dan D salah; B dan C benar.')
    elif i == 2 and n == 1:
        u, p, inc, cost = '1500000+10000*k', '22500+500*k', '800000+10000*k', '450000+1000*k'
        a.allnums({'1.500.000': u, '22.500': p, '800.000': inc, '450.000': cost,
                   '33.749.900.000': f'(({u})-20)*({p})+({inc})-({cost})',
                   '1.400.000': f'({u})-20*({p})+({inc})-({cost})',
                   '15.400.000': f'-(({u})-20*(({p})+({inc}))-({cost}))',
                   '700.000': f'({u})+20*({p})-({inc})-({cost})'})
        a.swap_reports()
        a.exp = a.explanation(f'Biaya buku = 20 * [[{p}]] = [[20*({p})]]. '
                             f'Saldo akhir = [[{u}]] - [[20*({p})]] + [[{inc}]] - [[{cost}]] '
                             f'= [[({u})-20*({p})+({inc})-({cost})]]. '
                             'Perkalian biaya buku dilakukan sebelum pengurangan; pengeluaran mengurangi kas.')
    elif i == 2 and n == 2:
        u, v, w = '7+k', '5+k%3', '4+k%2'
        a.constraints.append(f'({v}) != ({w})')
        a.allnums({'98': f'2*({u})**2', '50': f'2*({v})**2', '32': f'2*({w})**2',
                   '116': f'2*(({u})**2+({v})**2-({w})**2)',
                   '7': u, '5': v, '4': w, '8': f'({u})+({v})-({w})',
                   '18': f'({u})+({v})+({w})+2'})
        a.answer_value(2, f'({u})+({v})-({w})', '*sqrt(2) m')
        a.exp = a.explanation(f'Radikan masing-masing = [[2*({u})**2]], [[2*({v})**2]], [[2*({w})**2]]. '
                             f'Koefisien akar sejenis = [[{u}]] + [[{v}]] - [[{w}]] '
                             f'= [[({u})+({v})-({w})]]. Hasil = [[({u})+({v})-({w})]]*sqrt(2) meter. '
                             'Evaluasi Y benar, karena suku sejenis digabung melalui koefisiennya; radikan tidak dijumlahkan langsung.')
    elif i == 3 and n == 1:
        if l == 4:
            a.allnums({'28.647': '28647+1000*k', '28.000': '28000+1000*k',
                       '29.000': '29000+1000*k', '28.600': '28600+1000*k', '28.700': '28700+1000*k'})
            a.swap_reports('Analisis')
            a.exp = a.explanation('Pembulatan langsung pada data [[28647+1000*k]]: '
                                 'ribuan = [[29000+1000*k]] (digit ratusan 6); '
                                 'ratusan = [[28600+1000*k]] (digit puluhan 4). Jangan membulatkan bertahap.')
        else:
            a.allnums({'19.482': '19482+1000*k', '19.000': '19000+1000*k',
                       '20.000': '20000+1000*k', '19.500': '19500+1000*k', '19.400': '19400+1000*k'})
            a.swap_reports()
            a.exp = a.explanation('Pembulatan langsung pada data [[19482+1000*k]]: '
                                 'ribuan = [[19000+1000*k]] (digit ratusan 4); '
                                 'ratusan = [[19500+1000*k]] (digit puluhan 8). Jangan membulatkan bertahap.')
    elif i == 3 and n == 2:
        a.variables['k']['range'] = [0, 100]
        ra, rb = 'round(sqrt(58+k),1)', 'round(sqrt(59+k),1)'
        a.constraints.append(f'{ra} != {rb}')
        a.stem = a.nums(a.stem, {'58': '58+k', '59': '59+k'})
        for j, (x, y) in enumerate([(f'{ra}-0.1', f'{rb}-0.1'), (ra, f'{rb}-0.1'), (ra, rb),
                                     (f'{ra}+0.1', f'{rb}+0.1')]):
            tokens = list(NUMBER.finditer(a.options[j]))
            assert len(tokens) == 2
            pieces, last = [], 0
            for match, expr in zip(tokens, (x, y)):
                pieces.extend([a.options[j][last:match.start()], a.var(expr, match[0])]); last = match.end()
            a.options[j] = ''.join(pieces) + a.options[j][last:]
        a.exp = a.explanation(f'Bulatkan masing-masing akar langsung ke persepuluhan: '
                             f'sqrt([[58+k]]) dibulatkan menjadi [[{ra}]] m; '
                             f'sqrt([[59+k]]) dibulatkan menjadi [[{rb}]] m. '
                             'Gunakan batas tengah dua persepuluhan, bukan membulatkan nilai kuadrat yang paling dekat. Opsi C benar.')
    elif i == 3 and n == 6:
        base, root, bound, x, y = ((34.853, 27, 60, 396, 204) if l == 4 else (45.748, 30, 50, 497, 302))
        # Original: true/false/true/true. Variants: false/true/true/true.
        claimed1 = f'round({base}+k,1)+(0 if k == 0 else 0.1)'
        low = f'floor(sqrt({bound}+k)*10)/10'
        a.constraints.append(f'({low})**2 < {bound}+k')
        mapping = {str(base).replace('.', ','): f'{base}+k', str(root): f'{root}+k', str(bound): f'{bound}+k',
                   str(x): f'{x}+100*k', str(y): f'{y}+100*k',
                   ('34,9' if l == 4 else '45,7'): claimed1,
                   ('5,4' if l == 4 else '5,8'): f'round(sqrt({root}+k),1)',
                   ('7,7' if l == 4 else '7,0'): low,
                   ('7,8' if l == 4 else '7,1'): f'{low}+0.1',
                   ('80.000' if l == 4 else '150.000'): f'round(({x}+100*k)/100)*100*round(({y}+100*k)/100)*100'}
        a.allnums(mapping)
        a.correct = ['k == 0', 'k != 0', True, True]
        a.exp = a.explanation(f'(i) Nilai pembulatan yang benar = [[round({base}+k,1)]]. '
                             f'(ii) Aproksimasi akar yang benar = [[round(sqrt({root}+k),1)]]. '
                             f'(iii) Batas akar = [[{low}]] dan [[{low}+0.1]], kuadrat batas mengapit [[{bound}+k]]. '
                             f'(iv) Hasil estimasi = [[round(({x}+100*k)/100)*100*round(({y}+100*k)/100)*100]]. '
                             'Nilai klaim harus dibandingkan dengan nilai benar tersebut, bukan sekadar mengikuti panjang desimal.')
    elif i == 3 and n == 9:
        bx, by, total = (5.46, 3.75, 10.5) if l == 4 else (6.46, 4.75, 12.5)
        mapping = {str(bx).replace('.', ','): f'{bx}+k', str(by).replace('.', ','): f'{by}+k',
                   str(bx+0.04).replace('.', ','): f'round({bx}+k,1)',
                   str(int(by)): f'{int(by)}+k', str(total).replace('.', ','): f'{total}+2*k'}
        a.allnums(mapping)
        a.exp = a.explanation(f'Massa pertama ke persepuluhan = [[round({bx}+k,1)]]. '
                             f'Massa kedua ke satuan = [[round({by}+k)]], bukan [[floor({by}+k)]]. '
                             f'Massa kedua ke persepuluhan = [[round({by}+k,1)]]. Massa ketiga ke persepuluhan = 1,2. '
                             f'Total estimasi = [[{total}+2*k]]. Pernyataan 1 dan 3 benar; 2 salah.')
    elif i == 4 and n == 1 and l == 4:
        a.variables['k']['range'] = [0, 28]
        a.stem = a.stem.replace('2 Mei', a.var('2+k', '2') + ' Mei')
        # Dates are offsets from 1 May (May=31, June=30, July=31).
        for literal, offset in [('26 Mei', 24), ('19 Juni', 48), ('18 Juni', 47), ('13 Juli', 72)]:
            ordinal = f'2+k+{offset}'
            day = f'{ordinal} if {ordinal}<=31 else {ordinal}-31 if {ordinal}<=61 else {ordinal}-61 if {ordinal}<=92 else {ordinal}-92'
            month = f"'Mei' if {ordinal}<=31 else 'Juni' if {ordinal}<=61 else 'Juli' if {ordinal}<=92 else 'Agustus'"
            d, mo = literal.split()
            a.stem = a.stem.replace(literal, a.var(day, d) + ' ' + a.var(month, mo))
        a.swap_reports('Analisis')
        a.exp = a.explanation('KPK(6,8,12) = 24 hari. Kejadian pertama pada hari ke-0; '
                             'kejadian ketiga setelah (3-1)*24 = 48 hari. '
                             'Tanggal mulai = [[2+k]] Mei. Bulan Mei 31 hari dan Juni 30 hari. '
                             'Gunakan tanggal pada klaim 48 hari yang menghitung kalender tersebut secara benar.')
    elif i == 4 and n == 1:
        a.stem = a.stem.replace('KPK(10,15,20)',
            'KPK(' + ','.join(a.var(expr, literal) for expr, literal in
                             [('2*(5+k)', '10'), ('3*(5+k)', '15'), ('4*(5+k)', '20')]) + ')')
        a.allnums({'10': '2*(5+k)', '15': '3*(5+k)', '20': '4*(5+k)',
                   '30': '6*(5+k)', '60': '12*(5+k)', '3.000': '24*(5+k)**3'})
        a.exp = a.explanation('KPK dari [[2*(5+k)]], [[3*(5+k)]], [[4*(5+k)]] '
                             '= [[12*(5+k)]] detik. Klaim [[6*(5+k)]] salah karena tidak habis dibagi [[4*(5+k)]]. '
                             'Hanya opsi B memberi waktu dan alasan KPK yang benar; hasil kali ketiganya bukan KPK.')
    elif i == 4 and n == 6:
        primes = [5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137]
        if l == 4:
            a.variables['k'] = dict(gen='choice', values=[p-5 for p in primes], fmt='raw')
            a.stem = a.stem.replace('45,60,', a.var('9*(5+k)', '45') + ',' + a.var('12*(5+k)', '60') + ',')
            a.allnums({'45': '9*(5+k)', '60': '12*(5+k)', '90': '18*(5+k)',
                       '30': '6*(5+k)', '15': '3*(5+k)', '180': '36*(5+k)', '5': '5+k'})
            a.exp = a.explanation('Faktorisasi bilangan ketiga = 2*3^2*[[5+k]]. '
                                 'FPB = [[3*(5+k)]], bukan [[6*(5+k)]]. KPK = [[36*(5+k)]]. '
                                 'A, C, D benar; B salah karena tidak membagi bilangan pertama.')
        else:
            b, c = '18*(4+k)', '18*(5+k)'
            a.stem = a.stem.replace('54,72,', '54,' + a.var(b, '72') + ',')
            a.options = [t.replace('(54,72,90)', '(54,' + a.var(b, '72') + ',' + a.var(c, '90') + ')')
                         for t in a.options]
            first_lcm = f'54*({b})/gcd(54,({b}))'
            lcm = f'({first_lcm})*({c})/gcd(({first_lcm}),({c}))'
            a.allnums({'72': b, '90': c, '1.080': lcm})
            a.exp = a.explanation(f'Faktorisasi 54 = 2*3^3. '
                                 f'FPB(54,[[{b}]],[[{c}]]) = 18 karena dua faktor skala berurutan koprima. '
                                 f'KPK = [[{lcm}]]. A, C, D benar; B salah karena 36 tidak membagi 54.')
    elif i == 4 and n == 9:
        a.allnums({'84': '2*(42+k)', '126': '3*(42+k)', '42': '42+k'})
        a.exp = a.explanation('FPB([[2*(42+k)]],[[3*(42+k)]]) = [[42+k]]. '
                             'Minuman per kantong = 2, makanan per kantong = 3; total = 5. '
                             'Pernyataan 1 dan 3 benar; 2 salah karena tertukar komponen.')
    elif i == 4 and n == 10:
        a.allnums({'105': '7*(15+k)', '135': '9*(15+k)', '15': '15+k'})
        a.exp = a.explanation('FPB([[7*(15+k)]],[[9*(15+k)]]) = [[15+k]] cm. '
                             'Jumlah potongan = 7+9 = 16. Rasio banyak potongan 9:7, bukan 2:1. '
                             'Pernyataan 1 dan 2 benar; 3 salah.')
    elif i == 5 and n == 1:
        if l == 4:
            a.allnums({'15': '15+k', '45': '3*(15+k)', '20': '20+k', '60': '3*(20+k)'})
            a.swap_reports('Analisis')
            a.exp = a.explanation('Campuran A = [[15+k]]:[[3*(15+k)]] = 1:3. '
                                 'Campuran B = [[20+k]]:[[3*(20+k)]] = 1:3. '
                                 'Kedua rasio ekuivalen sehingga sama manis. Volume absolut sirup tidak cukup untuk membandingkan kemanisan.')
        else:
            a.allnums({'16': '16+k', '48': '3*(16+k)', '25': '25+k', '75': '3*(25+k)'})
            a.swap_reports('Evaluasi', 'A', 'B')
            a.exp = a.explanation('Racikan X = [[16+k]]:[[3*(16+k)]] = 1:3. '
                                 'Racikan Y = [[25+k]]:[[3*(25+k)]] = 1:3. '
                                 'Keduanya ekuivalen dan sama manis; laporan yang memakai rasio, bukan volume sirup absolut, benar.')
    elif i == 5 and n == 6:
        a.variables['k'] = dict(gen='range', range=[0, 60], step=2, fmt='raw')
        if l == 4:
            a.stem = a.stem.replace('berisi $36$', 'berisi $' + a.var('12*(3+k)', '36') + '$', 1)
            a.allnums({'54': '18*(3+k)', '3': '3+k', '4': '4+k', '5': '5+k'})
            a.options[1] = a.options[1].replace(':'+a.var('3+k', '3'), ':3')
            a.exp = a.explanation('Kotak A = [[12*(3+k)]]:24 = [[3+k]]:2. '
                                 'Kotak B = [[18*(3+k)]]:36 = [[3+k]]:2. '
                                 'Rasio merah ke total = [[3+k]]:[[5+k]]. '
                                 'Pada rasio merah ke total, kedua suku ganjil dan selisihnya 2, sehingga FPB keduanya 1. Rasio sudah sederhana. A, C, D benar; B salah.')
        else:
            a.allnums({'45': '15*(3+k)', '60': '20*(3+k)', '3': '3+k', '4': '4+k', '5': '5+k'})
            a.options[1] = a.options[1].replace(':'+a.var('3+k', '3'), ':3')
            a.exp = a.explanation('Tempat I = [[15*(3+k)]]:30 = [[3+k]]:2. '
                                 'Tempat II = [[20*(3+k)]]:40 = [[3+k]]:2. '
                                 'Rasio merah ke total = [[3+k]]:[[5+k]]. '
                                 'Pada rasio merah ke total, kedua suku ganjil dan selisihnya 2, sehingga FPB keduanya 1. Rasio sudah sederhana. A, C, D benar; B salah.')
    elif i == 5 and n == 9:
        if l == 4:
            a.allnums({'21.000': '30*(700+10*k)', '32.500': '50*(650+5*k)', '700': '700+10*k'})
            a.exp = a.explanation('Harga X per lembar = [[700+10*k]]. Harga Y per lembar = [[650+5*k]]. '
                                 'Selisih = [[50+5*k]], sehingga Y lebih murah. Pernyataan 1 dan 3 benar; 2 salah.')
        else:
            a.allnums({'36.000': '20*(1800+10*k)', '59.500': '35*(1700+5*k)', '1.800': '1800+10*k'})
            a.exp = a.explanation('Harga A per kotak = [[1800+10*k]]. Harga B per kotak = [[1700+5*k]]. '
                                 'Selisih = [[100+5*k]], sehingga B lebih murah. Pernyataan 1 dan 3 benar; 2 salah.')
    else:
        raise AssertionError(a.qid)
    return a


def main():
    matching = json.loads((AUDIT / 'stage-06-matching-indicators-01-05/matching.json').read_text(encoding='utf-8'))
    source_dir = REPO / 'docs/sources/incoming/2026-10-19-indikator-1-5'
    source_index = json.loads((source_dir / 'question-index.json').read_text(encoding='utf-8'))['questions']
    selected = [e for e in matching['entries']
                if e['source_number'] in SELECTION.get(e['indicator'], {}).get(e['level'], [])]
    assert len(selected) == 33
    DATA.mkdir(parents=True, exist_ok=True)
    metadata, groups, rows = {}, {}, []
    for e in selected:
        assert e['recommendation'] == 'UPDATE_ATAU_BANGUN_GENERATOR'
        assert e['academic'] == dict(validity='VALID', answer_status='CORRECT', explanation_status='CORRECT',
                                     recommendation='NO_BLOCKING_ACADEMIC_FINDING')
        s = e['source_projection']
        qid = f"{s['format'].lower()}-{e['indicator']}-{e['level']}-{e['source_number']}"
        raw = next(q['extracted_content'] for q in source_index
                   if (q['source_indicator'], q['source_level'], q['source_question_number']) ==
                   (e['indicator'], e['level'], e['source_number']))
        cog = re.search(r'Level Kognitif:\s*(C\d)', raw)
        rows.append(dict(id=qid, format=s['format'], cognitive_level=cog[1] if cog else '',
                         stem=safe_algebra(s['stem']), options_json=json.dumps([safe_algebra(t) for t in s['options']], ensure_ascii=False),
                         key=','.join(s['key']), version=1))
        group_key = e['indicator'], e['level']
        groups.setdefault(group_key, []).append(qid)
        metadata[qid] = dict(generation_status='ACTIVE', reason='', source_number=e['source_number'],
            source_document='../../..' + '/docs/sources/incoming/2026-10-19-indikator-1-5/source.docx',
            source_document_sha256=e['source']['sha256'], source_location=e['source'], audit_id=e['audit_id'],
            original_explanation=s['explanation'], source_text=raw, source_key_caption=s['key_caption'],
            source_additional_notes=s['additional_notes'], approval_status='NOT_CURRICULUM_APPROVED',
            self_adjustment_enabled=False, batch='2026-10-20-level45-batch1',
            notes=['Generator lokal, bukan persetujuan publikasi atau kesetaraan kesulitan/IRT.',
                   'Nomor sumber dipertahankan; penomoran tidak dipadatkan untuk batch parsial.',
                   'Pecahan simbolik LaTeX a/b dinormalisasi ke (a)/(b) untuk menghindari placeholder template; teks sumber mentah tetap disimpan.'])
        if s['category_labels']:
            metadata[qid]['category_labels'] = s['category_labels']
    with (DATA / 'q0_bank.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    dump = lambda p, obj: p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    dump(DATA / 'question_metadata.json', metadata)
    dump(DATA / 'question_catalog.json', [dict(activity='DRILL', package_id='drill-1', indicator=i,
          source_level=l, question_ids=qs) for (i, l), qs in groups.items()])
    bank = OriginalBank(DATA / 'q0_bank.csv')
    for e in selected:
        a = author(e)
        cfg = a.config(bank.get(a.qid))
        folder = ROOT / 'configs' / a.qid
        folder.mkdir(exist_ok=True)
        dump(folder / 'v1.json', cfg)
    print('Authored', len(selected), 'originals/configs')


if __name__ == '__main__':
    main()
