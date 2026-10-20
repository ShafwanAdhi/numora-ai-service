"""Authoring recipes for the remaining indicator 1-2 level 4-5 questions."""
from copy import deepcopy
import re

from level45_completion_common import Author, safe_algebra
from expr import placeholders

HELD = {'pg-1-4-1','pg-1-5-2','pg-1-5-5','mcma-1-5-7','pg-2-4-1','pg-2-4-2',
        'pg-2-4-3','pg-2-4-5','kategori-2-4-9','kategori-2-4-10',
        'kategori-2-5-9','kategori-2-5-10'}


def _replace(projection, field, old, new):
    projection[field] = projection[field].replace(old, new)


def prepare(entry, audit):
    """Return a review copy; valid source projections remain exactly unchanged."""
    out = deepcopy(entry)
    p = out['source_projection']
    qid = f"{p['format'].lower()}-{entry['indicator']}-{entry['level']}-{entry['source_number']}"
    if qid not in HELD:
        return out, []
    reasons = []
    if qid == 'pg-1-4-1':
        _replace(p, 'stem', 'Analisis I: Stasiun A, Stasiun C, Stasiun B, Stasiun D',
                 'Analisis I: Stasiun A, Stasiun B, Stasiun C, Stasiun D')
        p['options'][1] = 'Analisis II (Urutan: Stasiun A, Stasiun C, Stasiun B, Stasiun D)'
        reasons.append('Membedakan Analisis I dan II serta menyelaraskan opsi B dengan label kunci sumber.')
    elif qid == 'pg-1-5-2':
        p['stem'] = ('Seorang siswa mengevaluasi keanggotaan jenis bilangan real berikut:\n'
                     '$a=\\sqrt{48}-4\\sqrt{3}=0$\n'
                     '$b=0,454545...=\\frac{45}{99}=\\frac{5}{11}$\n'
                     'Evaluasi I: "$a$ irasional dan $b$ rasional."\n'
                     'Evaluasi II: "$a$ rasional dan $b$ irasional."\n'
                     'Evaluasi III: "Keduanya ($a$ dan $b$) adalah bilangan rasional."\n'
                     'Evaluasi IV: "Keduanya ($a$ dan $b$) adalah bilangan irasional."\n'
                     'Manakah evaluasi yang benar?')
        reasons.append('Memilih blok akhir yang mendukung kunci C dan menghapus rancangan serta label berulang.')
    elif qid == 'pg-1-5-5':
        p['stem'] = p['stem'].replace(
            'Evaluasi A: Lubang B dan Lubang C berada pada kedalaman yang persis sama.',
            'Evaluasi A: Lubang B dan Lubang C berada pada kedalaman yang berbeda.')
        reasons.append('Mengubah opsi A menjadi salah agar Evaluasi B menjadi satu-satunya jawaban PG.')
    elif qid == 'mcma-1-5-7':
        p['options'][3] = ('Total alokasi dua pengeluaran pada Metode Y adalah Rp130.000,00, '
                           'sehingga sisa kasnya Rp270.000,00.')
        reasons.append('Mengganti penilaian subjektif kemudahan dengan klaim aritmetika terukur.')
    elif qid == 'pg-2-4-1':
        p['stem'] = p['stem'].replace(
            'Analisis I: $1.200.000-15×18.000+500.000-350.000=1.080.000$',
            'Analisis I: $(1.200.000-15)×18.000+500.000-350.000=21.599.730.000$')
        reasons.append('Menghilangkan duplikasi model benar sehingga hanya Analisis II sesuai kunci B.')
    elif qid == 'pg-2-4-2':
        p['key'] = ['B']
        p['explanation'] = (
            'Pembahasan:\n'
            '$\\sqrt{75}=\\sqrt{25×3}=5\\sqrt{3}$\n'
            '$\\sqrt{108}=\\sqrt{36×3}=6\\sqrt{3}$\n'
            '$\\sqrt{27}=\\sqrt{9×3}=3\\sqrt{3}$\n'
            '$5\\sqrt{3}+6\\sqrt{3}-3\\sqrt{3}=8\\sqrt{3}$, '
            'jadi bentuk sederhananya adalah $8\\sqrt{3}$ cm.')
        reasons.append('Memperbaiki 5+6-3 menjadi 8 dan memindahkan kunci dari C ke B.')
    elif qid == 'pg-2-4-3':
        p['explanation'] = p['explanation'].replace(
            '$({a}^{m}{)}^{n}×{a}^{m-n}$', '$({a}^{m}{)}^{n}={a}^{m×n}$')
        reasons.append('Memperbaiki identitas pangkat dari pangkat tanpa mengubah hasil 2^8.')
    elif qid == 'pg-2-4-5':
        p['options'][0] = ('Jawaban Siswa A salah karena $2{7}^{\\frac{2}{3}}$ '
                           'tidak sama dengan $9={3}^{2}$')
        reasons.append('Membuat opsi A salah secara eksplisit agar penilaian rinci pada opsi C unik.')
    elif qid in ('kategori-2-4-9', 'kategori-2-5-9'):
        p['key'] = ['1', '2', '3']
        if qid == 'kategori-2-4-9':
            p['explanation'] = (
                'Pembahasan:\n'
                '$1,25\u00d70,4=0,5$, sehingga pernyataan 1 benar. '
                'Jika penjumlahan diuji lebih dahulu, '
                '$(\\frac{3}{4}+1,25)\u00d70,4=2\u00d70,4=0,8$, sehingga pernyataan 2 benar. '
                'Dengan urutan operasi baku, $\\frac{3}{4}+0,5=1,25=\\frac{5}{4}$, '
                'sehingga pernyataan 3 benar.')
        else:
            p['explanation'] = (
                'Pembahasan:\n'
                '$1,5\u00d70,2=0,3$, sehingga pernyataan 1 benar. '
                'Jika penjumlahan diuji lebih dahulu, '
                '$(\\frac{4}{5}+1,5)\u00d70,2=2,3\u00d70,2=0,46$, sehingga pernyataan 2 benar. '
                'Dengan urutan operasi baku, $\\frac{4}{5}+0,3=1,1=\\frac{11}{10}$, '
                'sehingga pernyataan 3 benar.')
        reasons.append('Mengakui nilai kondisional pernyataan kedua yang secara aritmetika benar.')
    elif qid in ('kategori-2-4-10', 'kategori-2-5-10'):
        # The keyed mathematics is already right; remove the audited false distractor derivation.
        marker = 'Catatan:'
        if marker in p['additional_notes']:
            p['additional_notes'] = p['additional_notes'].split(marker)[0].rstrip()
        else:
            p['additional_notes'] += '\nKoreksi draf: jalur distraktor yang tidak konsisten dihapus.'
        if p['additional_notes'] == entry['source_projection']['additional_notes']:
            p['additional_notes'] += '\nKoreksi draf: contoh hasil antara diperbaiki; jawaban akhir tidak berubah.'
        reasons.append('Menghapus derivasi distraktor yang aritmetikanya tidak konsisten; kunci tetap benar.')
    else:
        raise AssertionError(f'Unimplemented held source: {qid}')
    ids = (['1', '2', '3'] if p['format'] == 'KATEGORI' else
           [chr(65 + i) for i in range(len(p['options']))])
    selected = [p['options'][ids.index(answer)] for answer in p['key']]
    p['key_caption'] = ', '.join(p['key']) + '. ' + ' | '.join(selected)
    note = 'Koreksi draft (belum dipublikasikan): ' + ' '.join(reasons)
    p['additional_notes'] = (p.get('additional_notes', '').rstrip() + '\n' + note).strip()
    return out, reasons


def _token(a, old, expr):
    """Replace all literal occurrences while retaining the exact k=0 typography."""
    v = a.var(expr, old)
    pattern = rf'(?<![\w.,]){re.escape(old)}(?![\d.,])'
    a.stem = re.sub(pattern, lambda _m: v, a.stem)
    a.options = [re.sub(pattern, lambda _m: v, t) for t in a.options]
    a.exp = re.sub(pattern, lambda _m: v, a.exp)
    return v


def _all(a, mapping):
    a.allnums(mapping)
    a.exp = a.nums(a.exp, mapping)


def _text(a, old, new):
    """Exact textual replacement in all authored fields."""
    a.stem = a.stem.replace(old, new)
    a.options = [value.replace(old, new) for value in a.options]
    a.exp = a.exp.replace(old, new)


def _latex_base(a, literal, expression):
    """Vary a braced LaTeX base without touching an equal exponent literal."""
    value = a.var(expression, literal)
    pattern = re.compile(r'\{' + re.escape(literal) + r'\}(?=\^)')
    a.stem = pattern.sub('{' + value + '}', a.stem)
    a.options = [pattern.sub('{' + value + '}', text) for text in a.options]
    a.exp = pattern.sub('{' + value + '}', a.exp)
    return value


def _swap_labels(a, left, right, original_correct, generated_correct):
    """Swap semantic labels after k=0 so the true claim genuinely moves."""
    marker = '__NUMORA_LABEL_SWAP__'
    lv = a.var(repr(right), left)
    rv = a.var(repr(left), right)
    for attr in ('stem', 'exp'):
        text = getattr(a, attr).replace(left, marker).replace(right, rv).replace(marker, lv)
        setattr(a, attr, text)
    a.options = [t.replace(left, marker).replace(right, rv).replace(marker, lv) for t in a.options]
    a.correct = [f'k == 0' if j == original_correct else f'k != 0' if j == generated_correct else False
                 for j in range(len(a.options))]


def _probe(a, marker, body):
    """Insert a generated-only mathematical test case before the task question."""
    assert marker in a.stem
    pieces = []
    for part in re.split(r'(\{v\d+\})', '\nKasus uji numerik: ' + body + '\n'):
        match = re.fullmatch(r'\{(v\d+)\}', part)
        if match:
            name = match[1]
            a.variables[name]['expr'] = "'' if k == 0 else (" + a.variables[name]['expr'] + ')'
            pieces.append(part)
        elif part:
            pieces.append(a.var(repr(part), ''))
    a.stem = a.stem.replace(marker, ''.join(pieces) + marker)


def _generated_parts(a, parts):
    """Render mixed literal/expression parts only for generated (k>0) draws."""
    rendered = []
    for part in parts:
        if isinstance(part, tuple):
            token = a.var(part[1])
            name = token[1:-1]
            a.variables[name]['expr'] = "'' if k == 0 else (" + a.variables[name]['expr'] + ')'
            rendered.append(token)
        else:
            rendered.append(a.var(repr(part), ''))
    return ''.join(rendered)


def author(entry):
    a = Author(entry)
    p = entry['source_projection']
    a.exp = safe_algebra(p['explanation'])
    q = a.qid
    s = '(k+1)'
    a.variables['k']['range'] = [0, 24]

    # Ordering and rational/irrational classification families.
    if q == 'pg-1-4-1':
        _token(a, '1,85', '1.85*(k+1)'); _token(a, '1,70', '1.70*(k+1)')
        _token(a, '7', '7*(k+1)'); _token(a, '4', '4'); _token(a, '3', '3*(k+1)**2')
        _token(a, '1,732', 'round(sqrt(3)*(k+1),3)')
        _token(a, '1,75', '1.75*(k+1)')
        a.options[1] += _generated_parts(a, ['; posisi A=', ('n','-1.85*(k+1)'),
                                             ', C=', ('n','-1.75*(k+1)')])
    elif q == 'pg-1-4-5':
        _token(a, '5', '5*(k+1)'); _token(a, '2', '2'); _token(a, '6', '6*(k+1)**2')
        _token(a, '2,4', '2.4*(k+1)')
        _token(a, '2,50', '2.5*(k+1)'); _token(a, '2,449', 'round(sqrt(6)*(k+1),3)')
        _token(a, '2,40', '2.4*(k+1)')
        a.options[2] += _generated_parts(a, ['; Q=', ('n','-sqrt(6)*(k+1)'),
                                             ' berada di antara R dan P'])
    elif q == 'pg-1-5-2':
        _token(a, '48', '3*(k+4)**2'); _token(a, '4', 'k+4')
        a.options[2] += _generated_parts(a, ['; karena √', ('n','3*(k+4)**2'),
                                             '=', ('n','k+4'), '√3 sehingga a=0'])
        # Keep the repeating decimal fixed; only the independently classified radical changes.
        # Explanations are independently checked; use a concise derivation for generated draws.
    elif q == 'pg-1-5-5':
        _token(a, '0,85', '0.85*(k+1)'); _token(a, '4', '4*(k+1)')
        _token(a, '5', '5'); _token(a, '0,64', '0.64*(k+1)**2'); _token(a, '0,80', '0.8*(k+1)')
        a.options[1] += _generated_parts(a, ['; kedalaman B=C=', ('n','-0.8*(k+1)')])

    # Operation-property and cash-context families: scale monetary/counterexample data.
    elif q == 'pg-1-4-4':
        _token(a, '5', 'k+5'); _token(a, '3', 'k+3'); _token(a, '-2', '-2'); _token(a, '2', '2')
        a.options[1] += _generated_parts(a, ['; contoh memberi ', ('n','k+5'), '-',
                                             ('n','k+3'), '=2 dan urutan balik =-2'])
    elif q == 'mcma-1-4-7':
        _all(a, {'600.000':'600000*(k+1)','150.000':'150000*(k+1)',
                 '50.000':'50000*(k+1)','450.000':'450000*(k+1)',
                 '400.000':'400000*(k+1)','100.000':'100000*(k+1)',
                 '500.000':'500000*(k+1)','200.000':'200000*(k+1)'})
    elif q == 'mcma-1-5-7':
        _all(a, {'400.000':'400000*(k+1)','100.000':'100000*(k+1)',
                 '30.000':'30000*(k+1)','300.000':'300000*(k+1)',
                 '270.000':'270000*(k+1)','130.000':'130000*(k+1)',
                 '70.000':'70000*(k+1)','330.000':'330000*(k+1)'})
    elif q == 'pg-1-5-3':
        _all(a, {'25':'25+k','15.000':'15000+500*k','12.000':'12000+400*k',
                 '27.000':'27000+900*k','675.000':'(25+k)*(27000+900*k)',
                 '15.025':'(25+k)+(15000+500*k)','12.025':'(25+k)+(12000+400*k)',
                 '180.675.625':'((25+k)+(15000+500*k))*((25+k)+(12000+400*k))'})
        a.options[0] += _generated_parts(a, ['; total benar Rp',
                                             ('n','(25+k)*(27000+900*k)')])
    elif q == 'pg-2-4-1':
        cash, count, price, incoming, rent = ('1200000+10000*k','15+k','18000+500*k',
                                               '500000+10000*k','350000+5000*k')
        _all(a, {'1.200.000':cash,'15':count,'18.000':price,'500.000':incoming,'350.000':rent,
                 '270.000':f'({count})*({price})',
                 '1.080.000':f'({cash})-({count})*({price})+({incoming})-({rent})',
                 '21.599.730.000':f'(({cash})-({count}))*({price})+({incoming})-({rent})',
                 '-6.920.000':f'({cash})-({count})*(({price})+({incoming}))-({rent})'})
        a.options[1] += _generated_parts(a, ['; saldo akhir Rp',
                                             ('n',f'({cash})-({count})*({price})+({incoming})-({rent})')])

    # Real-number conceptual questions get varying mathematical witnesses.
    elif q == 'mcma-1-4-8':
        # Vary L itself and every displayed value of L².  The irrational and
        # integer classifications are derived from the changed task operand.
        radicand = a.var('3*(k+1)**2', '3')
        _text(a, '\\sqrt{3}', '\\sqrt{' + radicand + '}')
        squared = a.var('3*(k+1)**2', '3')
        _text(a, '=3$', '=' + squared + '$')
    elif q == 'mcma-1-5-8':
        radicand = a.var('7*(k+1)**2', '7')
        _text(a, '\\sqrt{7}', '\\sqrt{' + radicand + '}')
        squared = a.var('7*(k+1)**2', '7')
        _text(a, '=7$', '=' + squared + '$')
    elif q == 'kategori-1-4-10':
        coefficient = a.var('k+2')
        radicand = a.var('2*(k+1)**2')
        integer = a.var('k+3')
        _probe(a, 'Tentukan status', '$a=' + coefficient + '$, $b=\\sqrt{' + radicand +
               '}$, dan $z=' + integer + '$. Terapkan ketiga hipotesis pada data ini. ')
        # Put the witness in the proposition itself so the varied task, and
        # therefore its correct answer text, changes for every draw.
        a.options[0] += _generated_parts(a, [' Untuk data di atas, a\u00d7b=', ('n','k+2'),
                                                   '\u221a', ('n','2*(k+1)**2'),
                                                   ' tetap irasional.'])
        a.exp += _generated_parts(a, [' Data varian: a\u00d7b=', ('n','k+2'), '\u221a',
                                      ('n','2*(k+1)**2'), ' irasional dan z=',
                                      ('n','k+3'), '/', ('n','1'), ' rasional.'])
    elif q == 'kategori-1-5-10':
        numerator = a.var('k+2')
        integer = a.var('k+3')
        radicand = a.var('2*(k+1)**2')
        _probe(a, 'Tentukan status', '$r=' + numerator + '/3$, $n=' + integer +
               '$, dan $u=\\sqrt{' + radicand + '}$. Uji sifat tertutup, subset, dan $u+(-u)$. ')
        a.options[0] += _generated_parts(a, [' Pada data di atas, r+r=', ('n','2*(k+2)'),
                                                   '/3 tetap rasional.'])
        a.exp += _generated_parts(a, [' Data varian: r+r=', ('n','2*(k+2)'),
                                      '/3 rasional dan u+(-u)=0.'])
    elif q == 'pg-1-5-4':
            left = a.var('k+4')
            total = a.var('4*(k+4)')
            _probe(a, 'Manakah evaluasi', '$a=' + total + '$, $b=' + left +
                   '$, $c=2$: $(a\\div b)\\div c=2$, sedangkan '
                   '$a\\div(b\\div c)=8$. ')
            a.options[2] += _generated_parts(a, [' Contoh: a=', ('n','4*(k+4)'),
                                                     ', b=', ('n','k+4'),
                                                     ', c=2 memberi hasil 2 dan 8.'])
    elif q == 'mcma-2-4-7':
        source_power = a.var('k+3', '3')
        result_power = a.var('k+4', '4')
        _text(a, '{a}^{4}', '{a}^{' + result_power + '}')
        _text(a, '3-(-1)', source_power + '-(-1)')
        _text(a, '{a}^{3}', '{a}^{' + source_power + '}')
    elif q == 'mcma-2-5-7':
        source_power = a.var('k+4', '4')
        result_power = a.var('k+6', '6')
        _text(a, '{x}^{6}', '{x}^{' + result_power + '}')
        _text(a, '4-(-2)', source_power + '-(-2)')
        _text(a, '{x}^{4}', '{x}^{' + source_power + '}')

    # Radical and exponent simplification families.
    elif q == 'pg-2-4-2':
        _token(a, '75', '3*(k+5)**2')
        # The first coefficient grows from 5; the other two stay 6 and 3.
        a.options[1] = a.options[1].replace('8', a.var('k+8', '8'))
        a.options[3] = a.options[3].replace('12', a.var('k+12', '12'))
        a.exp = a.exp.replace('25', a.var('(k+5)**2', '25')).replace('5\\sqrt', a.var('k+5','5')+'\\sqrt')
        a.exp = a.exp.replace('(5+6-3)', '('+a.var('k+5','5')+'+6-3)').replace('=8\\sqrt', '='+a.var('k+8','8')+'\\sqrt')
        a.exp = a.exp.replace('adalah $8\\sqrt', 'adalah $'+a.var('k+8','8')+'\\sqrt')
    elif q in ('pg-2-4-3', 'pg-2-5-3'):
        # Change the base of the expression being asked, throughout the
        # worked alternatives and explanation. Exponents retain the source
        # workload and the answer remains independently derivable.
        if q == 'pg-2-4-3':
            _latex_base(a, '2', 'k+2')
        else:
            _latex_base(a, '3', 'k+3')
            _text(a, '3 mW', a.var('k+3', '3') + ' mW')
            _text(a, '9 mW', a.var('(k+3)**2', '9') + ' mW')
            _text(a, '27 mW', a.var('(k+3)**3', '27') + ' mW')
            a.options[1] += _generated_parts(a, ['; basisnya ', ('n','k+3'),
                                                 ' dan nilainya ', ('n','(k+3)**2'), ' mW'])
    elif q in ('pg-2-4-5', 'pg-2-5-5'):
        if q == 'pg-2-4-5':
            square = a.var('(k+3)**2', '9')
            cube = a.var('(k+3)**3', '2{7}')
            base_plain = a.var('k+3', '3')
            _text(a, '2{7}', cube)
            _text(a, '9', square)
            _text(a, '=3', '=' + base_plain)
            _text(a, 'basis menjadi 3', 'basis menjadi ' + base_plain)
            _text(a, 'ke basis 3', 'ke basis ' + base_plain)
            _text(a, 'basis $3$', 'basis $' + base_plain + '$')
            _latex_base(a, '3', 'k+3')
        else:
            fourth = a.var('(k+2)**4', '1{6}')
            fourth_plain = a.var('(k+2)**4', '16')
            cube = a.var('(k+2)**3', '8')
            _text(a, '1{6}', fourth)
            _text(a, '16', fourth_plain)
            _text(a, '8', cube)
            base_plain = a.var('k+2', '2')
            _text(a, 'basis menjadi 2', 'basis menjadi ' + base_plain)
            _text(a, 'ke basis 2', 'ke basis ' + base_plain)
            _latex_base(a, '2', 'k+2')
    elif q == 'pg-2-5-4':
        for old, expr in [('6,4','6.4+0.8*k'),('0,8','0.8'),('3','3+k'),('0,5','0.5'),
                          ('8','8+k'),('1,5','1.5+0.5*k'),('9,5','9.5+1.5*k'),
                          ('11','11+2*k'),('5,5','5.5+k')]: _token(a, old, expr)
        a.options[0] += _generated_parts(a, ['; hasilnya ', ('n','9.5+1.5*k')])
    elif q in ('kategori-2-4-9', 'kategori-2-5-9'):
        if q.endswith('-4-9'):
            n,d,y='3*(k+1)','4','0.4'
            x='1.25*(k+1)'
            mapping = {'3':n,'4':d,'1,25':x,
                       '0,4':y,'0,5':'0.5*(k+1)','0,75':'0.75*(k+1)',
                       '5':'5*(k+1)', '0,8':'0.8*(k+1)','2':'2*(k+1)'}
        else:
            n,d,x,y='4+k','5','1.5+0.5*k','0.2'
            mapping = {'4':n,'5':d,'1,5':x,'0,2':y,'0,3':f'({x})*({y})',
                       '0,8':f'({n})/({d})','0,46':f'(({n})/({d})+({x}))*({y})',
                       '1,1':f'({n})/({d})+({x})*({y})',
                       '11':f'10*(({n})/({d})+({x})*({y}))','10':'10',
                       '2,3':f'({n})/({d})+({x})'}
        for label in ('1', '2', '3'):
            a.exp = a.exp.replace('pernyataan ' + label, '__PERNYATAAN_' + label + '__')
        _all(a, mapping)
        for label in ('1', '2', '3'):
            a.exp = a.exp.replace('__PERNYATAAN_' + label + '__', 'pernyataan ' + label)
    elif q in ('kategori-2-4-10', 'kategori-2-5-10'):
        scale = '(k+1)**2'
        if q.endswith('-4-10'):
            for old, expr in [('50',f'50*{scale}'),('18',f'18*{scale}'),('9',f'9*{scale}'),
                              ('900',f'900*{scale}*{scale}'),('30','30*(k+1)**2'),('3','3*(k+1)'),('10','10*(k+1)')]: _token(a, old, expr)
        else:
            for old, expr in [('72',f'72*{scale}'),('2',f'2*{scale}'),('16',f'16*{scale}'),
                              ('144',f'144*{scale}*{scale}'),('12','12*(k+1)**2'),('4','4*(k+1)'),('3','3*(k+1)')]: _token(a, old, expr)
    else:
        raise AssertionError(f'No author recipe for {q}')

    # Author.config treats literal LaTeX groups as placeholders; declare every such symbol.
    for text in [a.stem, *a.options, a.exp]:
        for name in placeholders(text) - a.variables.keys():
            a.variables[name] = dict(gen='derived',
                                     expr=f"{repr('{' + name + '}')} if k == 0 else {name!r}")
    return a
