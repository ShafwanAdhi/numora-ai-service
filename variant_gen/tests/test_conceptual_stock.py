"""Finite, reviewed conceptual stock is read-only; numerical generation stays strict."""
import contextlib
import ast
import operator
import re
import http.client
import io
import json
import sys
import tempfile
import threading
import unittest
import statistics
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import load_workspace_bank
from conceptual_stock import CONCEPTUAL_IDS, load_stock, stock_record
from filters import validate_candidate
from store import StoreError


class ConceptualStock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = load_workspace_bank(ROOT / 'data/q0_bank.csv')

    def item(self, qid='pg-1-1-4', index=1):
        original = self.bank.get(qid)
        return dict(variant_id=f'{qid}:stock-{index:02d}', question_id=qid,
                    stock_index=index, stock_version=1, original_hash=original['hash'],
                    original_version=original['version'],
                    stem='Kelompokkan biaya: 8×12000+8×3000 = 8×(12000+3000). Sifat apa yang digunakan?',
                    options=[{'id': o['id'], 'text': o['text']} for o in original['options']],
                    key=','.join(o['id'] for o in original['options'] if o['correct']),
                    explanation='Pemfaktoran 8 memakai distributif; komutatif menukar urutan, asosiatif mengelompokkan, tertutup membahas himpunan hasil.',
                    variation_note='Bentuk terurai menjadi faktor bersama, bukan sekadar mengganti nama.',
                    review_status='VERIFIED', review_note='Identitas distributif dan setiap distractor diperiksa.')

    def load(self, items):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'stock.json'
            path.write_text(json.dumps({'schema_version': 1, 'variants': items}), encoding='utf-8')
            return load_stock(path, self.bank)

    def test_same_answer_only_allowed_in_stock(self):
        original = self.bank.get('pg-1-1-4')
        item = self.item()
        loaded = self.load([item])
        record = stock_record(original, loaded[original['id']][0])
        self.assertEqual(record['key'], 'C')
        self.assertEqual(record['source_kind'], 'conceptual_stock')
        self.assertIsNone(record['seed'])
        cand = dict(stem=item['stem'], explanation=item['explanation'],
                    options=[dict(o, correct=o['id'] == 'C') for o in item['options']])
        self.assertIn('same_answer_as_original', validate_candidate(cand, original, []))
        self.assertEqual(validate_candidate(cand, original, [], allow_same_answer=True), [])

    def test_bad_content_is_not_silently_ignored(self):
        mutations = [dict(original_hash='wrong'), dict(original_version=2), dict(question_id='pg-999-1-1'),
                     dict(stock_index=5), dict(stock_index=True), dict(stock_version=0), dict(review_status='READY'),
                     dict(explanation=''), dict(variation_note=''), dict(review_note=''), dict(key='A,C'),
                     dict(key='C,C'), dict(stem='${unresolved}'), dict(options=[]), dict(original_version=True)]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(StoreError):
                self.load([dict(self.item(), **mutation)])
        original = self.bank.get('pg-1-1-4')
        with self.assertRaises(StoreError):
            self.load([dict(self.item(), stem=original['stem'])])
        with self.assertRaises(StoreError):
            self.load([self.item(), self.item()])
        with self.assertRaises(StoreError):
            self.load([self.item(index=2)])
        with self.assertRaises(StoreError):
            self.load([self.item('pg-1-1-5')])
        with self.assertRaises(StoreError):
            self.load([self.item('pg-23-3-2')])

    def test_draft_and_duplicate_without_option_order(self):
        self.assertEqual(self.load([dict(self.item(), review_status='DRAFT')]), {})
        other = self.item(index=2)
        other['options'].reverse()
        for option, oid in zip(other['options'], 'ABCD'):
            option['id'] = oid
        other['key'] = 'B'
        with self.assertRaises(StoreError):
            self.load([self.item(), other])

    def test_custom_categories_and_all_true_survive(self):
        for qid in ['kategori-20-1-9', 'kategori-20-2-10', 'kategori-10-2-10']:
            original = self.bank.get(qid)
            item = self.item(qid)
            item['stem'] = original['stem'] + '\nNilai setiap butir secara terpisah.'
            rec = stock_record(original, self.load([item])[qid][0])
            labels = original.get('metadata', {}).get('category_labels', ['Benar', 'Salah'])
            self.assertEqual(set(rec['answer_categories'].values()), set(labels) if qid != 'kategori-10-2-10' else {'Benar'})
            self.assertEqual(rec['cognitive_level'], original['cognitive_level'])

    def test_missing_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'missing.json'
            self.assertEqual(load_stock(path, self.bank), {})
            for payload in ['{', '[]', '{"schema_version":true,"variants":[]}', '{"schema_version":1,"variants":null}']:
                path.write_text(payload, encoding='utf-8')
                with self.subTest(payload=payload), self.assertRaises(StoreError):
                    load_stock(path, self.bank)

    def test_complete_inventory_and_preserved_profiles(self):
        stock = load_stock(ROOT / 'data/conceptual_stock.json', self.bank)
        self.assertEqual(set(stock), CONCEPTUAL_IDS)
        self.assertTrue(all(2 <= len(items) <= 4 for items in stock.values()))
        raw = json.loads((ROOT / 'data/conceptual_stock.json').read_text(encoding='utf-8'))['variants']
        self.assertTrue(all(i['review_status'] == 'VERIFIED' for i in raw))
        for qid, items in stock.items():
            original = self.bank.get(qid)
            self.assertFalse((ROOT / 'configs' / qid).exists(), qid)
            for item in items:
                record = stock_record(original, item)
                self.assertEqual(record['format'], original['format'])
                self.assertEqual(record['cognitive_level'], original['cognitive_level'])
                self.assertEqual(len(record['options']), len(original['options']))
                self.assertEqual(len(record['key'].split(',')) if record['key'] else 0,
                                 sum(o['correct'] for o in original['options']))

    def test_reviewed_difficulty_regressions(self):
        items = json.loads((ROOT / 'data/conceptual_stock.json').read_text(encoding='utf-8'))['variants']
        for item in items:
            qid, stem = item['question_id'], item['stem']
            with self.subTest(variant_id=item['variant_id']):
                if qid == 'pg-2-3-1':
                    # Opening balance plus five transactions, as in the source.
                    expressions = re.findall(r'(?:I|II): ([0-9.×÷+−()]+)=', stem)
                    self.assertEqual(len(expressions), 2)
                    self.assertTrue(all(len(re.findall(r'\d[\d.]*', e)) == 6 for e in expressions))
                if qid == 'pg-14-3-1':
                    self.assertNotRegex(stem, r'berikut (?:adalah|memiliki hubungan) (?:sudut )?(?:dalam|berseberangan|sehadap)')
                if qid == 'pg-22-2-5':
                    self.assertNotIn('jangkauan', stem.lower())
                if qid in ('pg-22-2-5', 'pg-22-3-5'):
                    self.assertTrue(all(not re.search(r'\d', o['text']) for o in item['options']))
                if qid == 'kategori-11-2-9':
                    self.assertTrue(all(not re.search(r'\b(?:adalah|pada|sebesar) −?\d', o['text']) for o in item['options']))
                if qid == 'pg-7-3-1':
                    self.assertIn('kupon', stem.lower())

    def test_manual_arithmetic_and_algebra_from_rendered_text(self):
        items = json.loads((ROOT / 'data/conceptual_stock.json').read_text(encoding='utf-8'))['variants']
        operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                      ast.Div: operator.truediv, ast.Pow: operator.pow}
        def evaluate(text, x=0):
            text = re.sub(r'\d{1,3}(?:\.\d{3})+', lambda m: m[0].replace('.', ''), text)
            text = text.replace('−', '-').replace('×', '*').replace('÷', '/').replace('^', '**')
            text = re.sub(r'(?<=[0-9x)])(?=[x(])', '*', text)
            def walk(node):
                if isinstance(node, ast.Constant): return Fraction(str(node.value))
                if isinstance(node, ast.Name) and node.id == 'x': return Fraction(x)
                if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -walk(node.operand)
                if isinstance(node, ast.BinOp): return operations[type(node.op)](walk(node.left), walk(node.right))
                raise AssertionError(ast.dump(node))
            return walk(ast.parse(text, mode='eval').body)
        checked = 0
        for item in items:
            qid, stem = item['question_id'], item['stem']
            if qid in ('pg-2-2-5', 'pg-2-3-1', 'pg-2-3-5'):
                for lhs, rhs in re.findall(r'(?:I|II): ([0-9.×÷+−()]+)=([0-9.]+)', stem):
                    self.assertEqual(evaluate(lhs), evaluate(rhs), item['variant_id'])
                    checked += 1
            if qid == 'kategori-10-2-10':
                expressions = re.findall(r'\b[ABC]: ([^.\n]+)', stem)
                self.assertEqual(len(expressions), 3)
                for x in (-7, -2, 0, 1, 3, 8):
                    self.assertEqual(len({evaluate(e, x) for e in expressions}), 1, item['variant_id'])
        self.assertEqual(checked, 16)

    def test_cli_and_http_read_stock_without_writes(self):
        import cli
        import webui
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'stock.json'
            authored = [self.item(index=i) for i in range(1, 4)]
            for i, item in enumerate(authored, 1):
                item['stem'] += f' Kasus uji {i}.'
            path.write_text(json.dumps({'schema_version': 1, 'variants': authored}), encoding='utf-8')
            before = path.read_bytes()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(cli.main(['stock', 'pg-1-1-4', '--stock', str(path), '--variant', '3', '--json']), 0)
            self.assertEqual(json.loads(output.getvalue())['stock_index'], 3)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(cli.main(['stock', 'pg-1-1-4', '--stock', str(path), '--json']), 0)
            self.assertEqual(json.loads(output.getvalue())['stock_count'], 3)
            server = webui.make_server(0, stock=path)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                def get(route):
                    connection = http.client.HTTPConnection(*server.server_address, timeout=15)
                    connection.request('GET', route)
                    response = connection.getresponse()
                    status, body = response.status, json.loads(response.read())
                    connection.close()
                    return status, body
                for _ in range(2):
                    status, body = get('/api/question?id=pg-1-1-4&stock_variant=3')
                    self.assertEqual(status, 200, body)
                    self.assertEqual(body['stock_count'], 3)
                    self.assertEqual(body['variant']['stock_index'], 3)
                    self.assertEqual(body['original']['original_hash'], self.bank.get('pg-1-1-4')['hash'])
                for bad in ('0', '4', 'no', ''):
                    self.assertEqual(get('/api/question?id=pg-1-1-4&stock_variant=' + bad)[0], 400)
                self.assertEqual(get('/api/question?id=pg-18-1-5&stock_variant=1')[0], 400)
                self.assertEqual(get('/api/question?id=unknown&stock_variant=1')[0], 400)
                self.assertEqual(get('/api/question?id=pg-1-1-4&stock_variant=1&stock_variant=2')[0], 400)
                status, questions = get('/api/questions')
                self.assertEqual(status, 200)
                row = next(q for q in questions if q['id'] == 'pg-1-1-4')
                self.assertEqual(row['variant_mode'], 'stock')
                self.assertFalse(row['has_config'])
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_printed_statistics_and_reflection_compositions(self):
        items = json.loads((ROOT / 'data/conceptual_stock.json').read_text(encoding='utf-8'))['variants']
        checked = 0
        for item in items:
            if item['question_id'] in ('mcma-22-1-8', 'mcma-22-2-8'):
                a, b = [list(map(int, line.split(','))) for line in
                        re.findall(r'[AB]: ([0-9, ]+)\.', item['stem'])]
                self.assertEqual(len(a), 5)
                self.assertEqual(len(b), 5)
                values = {'mean': (statistics.mean(a), statistics.mean(b)),
                          'median': (statistics.median(a), statistics.median(b)),
                          'jangkauan': (max(a)-min(a), max(b)-min(b))}
                for option in item['options']:
                    text = option['text'].lower()
                    if 'modus' in text:
                        modes = statistics.multimode(a)
                        if len(modes) == len(set(a)): modes = []
                        if 'tidak' in text: truth = not modes
                        elif 'dua modus' in text:
                            truth = sorted(modes) == sorted(map(int, re.findall(r'\d+', text)))
                        else: truth = modes == list(map(int, re.findall(r'\d+', text)))
                    else:
                        measure = re.search(r'mean|median|jangkauan', text)[0]
                        av, bv = values[measure]
                        if 'sama' in text: truth = av == bv
                        else:
                            first, second = (bv,av) if re.search(measure+r' b\b', text) else (av,bv)
                            truth = first > second if 'lebih besar' in text else first < second
                    self.assertEqual(bool(truth), option['id'] in item['key'].split(','), item['variant_id']+' '+text)
                    checked += 1
            if item['question_id'] == 'pg-17-3-2':
                first, second = re.search(r'direfleksikan terhadap (.+?), (?:lalu|kemudian) (?:direfleksikan )?terhadap (.+?)\.', item['stem']).groups()
                def reflect(axis, x, y):
                    if axis == 'sumbu X': return x, -y
                    if axis == 'sumbu Y': return -x, y
                    if axis == 'garis y=x': return y, x
                    if axis == 'garis y=−x': return -y, -x
                    self.fail(axis)
                answer = next(o['text'] for o in item['options'] if o['id'] == item['key'])
                for x,y in [(2,5),(-3,7),(0,1)]:
                    if '180°' in answer: expected = -x,-y
                    elif 'berlawanan' in answer: expected = -y,x
                    else: expected = y,-x
                    self.assertEqual(reflect(second,*reflect(first,x,y)),expected,item['variant_id'])
                checked += 1
        self.assertGreaterEqual(checked, 19)


if __name__ == '__main__':
    unittest.main()
