"""Tryout stock: reviewed conceptual profiles, exact answers and read-only access."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import load_workspace_bank
from conceptual_stock import load_stock,stock_record
from drill_1_2_math import calc

IDS=('tryout-1-b1-q07','tryout-1-b4-q02','tryout-1-b4-q06')


class TryoutStock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        cls.stock=load_stock(ROOT/'data/conceptual_stock.json',cls.bank)

    def test_three_reviewed_variants_each_and_preserved_original_profiles(self):
        for q in IDS:
            self.assertIn(q,self.stock)
            self.assertEqual(len(self.stock[q]),3)
            original=self.bank.get(q)
            for item in self.stock[q]:
                rec=stock_record(original,item)
                self.assertEqual(rec['classification'],original['classification'])
                self.assertEqual(rec['format'],original['format'])
                self.assertEqual(rec['cognitive_level'],original['cognitive_level'])
                self.assertEqual(len(rec['key'].split(',')),sum(o['correct'] for o in original['options']))
            self.assertFalse((ROOT/'configs'/q).exists())

    def test_parentheses_and_each_claim(self):
        q=IDS[0];self.assertIn(q,self.stock)
        for item,expected in zip(self.stock[q],('A,C','B,D','A,D')):
            import re
            expressions=re.findall(r'Penyelesaian [12]: (.*?)=(−?\d+)\.',item['stem'])
            self.assertEqual(len(expressions),2)
            values=[]
            for expression,result in expressions:
                value=calc(expression).scalar();self.assertEqual(value,int(result.replace('−','-')));values.append(value)
            if item['stock_index']==1:
                self.assertEqual(values[0],values[1])
                self.assertIn('kedua suku',item['options'][2]['text'])
            else:self.assertNotEqual(values[0],values[1])
            self.assertEqual(item['key'],expected)

    def test_probability_counts_match_all_options(self):
        q=IDS[1];self.assertIn(q,self.stock)
        for item,space,favorable in zip(self.stock[q],(4,8,6),(1,1,2)):
            expected=Fraction(favorable,space)
            truth=[]
            for option in item['options']:
                a,b=map(int,option['text'].split(' dari '));truth.append(Fraction(a,b)==expected)
            self.assertEqual([o['id'] for o,ok in zip(item['options'],truth) if ok],item['key'].split(','))
            self.assertIn(f'{favorable}/{space}',item['explanation'])
            self.assertIn('sama',item['stem'].lower())

    def test_survey_claims_do_not_assume_equal_allocation_is_proportional(self):
        q=IDS[2];self.assertIn(q,self.stock)
        items=self.stock[q]
        self.assertEqual([i['key'] for i in items],['1,2','1,3','2,3'])
        self.assertIn('masing-masing 40 siswa',items[0]['stem'])
        self.assertIn('60, 30, dan 30 siswa',items[1]['stem'])
        self.assertNotEqual(Fraction(5,60),Fraction(5,30))
        self.assertIn('tidak proporsional',items[1]['explanation'])
        self.assertIn('pertanyaan netral',items[2]['stem'])
        self.assertIn('menit, termasuk pecahan menit',items[2]['stem'])
        self.assertIn('kontinu',items[2]['explanation'])

    def test_cli_stock_is_reusable_without_database_or_output_storage(self):
        import cli
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            store=Path(tmp)/'variants.jsonl'
            for q in IDS:
                for index in (1,2,3,1):
                    output=io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(cli.main(['stock',q,'--variant',str(index),'--json','--store',str(store)]),0)
                    result=json.loads(output.getvalue())
                    self.assertEqual(result['stock_index'],index)
                    self.assertEqual(result['question_id'],q)
            self.assertFalse(store.exists())

    def test_ui_reads_every_stock_repeatedly_without_writes(self):
        import http.client,threading,webui
        stock_path=ROOT/'data/conceptual_stock.json';before=stock_path.read_bytes()
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            store=Path(tmp)/'variants.jsonl'
            server=webui.make_server(port=0,store=store)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                for q in IDS:
                    for index in (1,2,3,1):
                        connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=5)
                        connection.request('GET',f'/api/question?id={q}&stock_variant={index}')
                        response=connection.getresponse();body=json.loads(response.read());connection.close()
                        self.assertEqual(response.status,200,body)
                        self.assertEqual(body['variant_mode'],'stock')
                        self.assertEqual(body['stock_count'],3)
                        self.assertEqual(body['variant']['stock_index'],index)
                        self.assertEqual(body['variant']['classification']['activity'],'TRYOUT')
                        self.assertIsNone(body['variant']['seed'])
            finally:
                server.shutdown();thread.join();server.server_close()
            self.assertFalse(store.exists())
        self.assertEqual(stock_path.read_bytes(),before)


if __name__=='__main__':unittest.main()
