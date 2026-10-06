"""Drill 1–2, levels 1–3; no DB or user-store writes."""
import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore, ConfigError, validate_config
from engine import assemble, build_values, generate, GenerationError
from lint import reproduce_original

BANK = ROOT/'data/drill-1-indicators-1-2/q0_bank.csv'

class Drill12(unittest.TestCase):
    def test_oracle_rejects_false_equivalence_and_explanation(self):
        from drill_1_2_math import check_math,calc
        bank=OriginalBank(BANK)
        for qid in ['mcma-1-3-7','mcma-2-3-7','mcma-2-1-8']:
            cfg,_=ConfigStore(ROOT/'configs').load(qid)
            c=generate(bank.get(qid),cfg,7,[]).cand
            check_math(bank.get(qid),c)
            if qid=='mcma-1-3-7':
                c['options'][3]['text']='Model II ekuivalen dengan 1-1+1=1'
            elif qid=='mcma-2-3-7':
                import re
                answer=calc(re.search(r'Rumus 2: (.*?)\n',c['stem'])[1].split('=')[0]).scalar()
                c['options'][2]['text']=f'Jika Rumus 2 diubah menjadi {answer}-(0-0), hasilnya akan tetap bernilai sama.'
            else:c['explanation']='Pembagian 1/0=99. H=999999.'
            with self.assertRaises(AssertionError):check_math(bank.get(qid),c)

    def test_conditional_explanations_match_stimulus(self):
        import re
        from drill_1_2_math import calc
        bank=OriginalBank(BANK)
        for qid in ['pg-1-1-1','pg-1-3-4']:
            cfg,_=ConfigStore(ROOT/'configs').load(qid)
            for k in [1,2,30]:
                c=assemble(cfg,build_values(cfg,lambda n,s:k))
                if qid=='pg-1-1-1':
                    for name in ['Rian','Siti']:
                        expected=calc(re.search(name+r': (.*?) gram',c['stem'])[1])
                        match=re.search(name+r'=(.*?), (?:i?rasional)',c['explanation'])
                        self.assertIsNotNone(match,c['explanation'])
                        self.assertEqual(calc(match[1]),expected)
                else:
                    self.assertNotIn('variant',c['explanation'])
                    expected=calc(re.search(r'a=(.*?)\n',c['stem'])[1])
                    match=re.search(r'a=(.*?), (?:i?rasional)',c['explanation'])
                    self.assertIsNotNone(match,c['explanation'])
                    self.assertEqual(calc(match[1]),expected)

    def test_oracle_rejects_incorrect_rendered_operation(self):
        from copy import deepcopy
        from drill_1_2_math import check_math
        bank=OriginalBank(BANK)
        for qid in ['mcma-1-2-8','mcma-1-3-8']:
            cfg,_=ConfigStore(ROOT/'configs').load(qid)
            c=generate(bank.get(qid),cfg,7,[]).cand
            check_math(bank.get(qid),c)
            for index in [0,2 if qid=='mcma-1-3-8' else 1,3]:
                bad=deepcopy(c)
                text=bad['options'][index]['text']
                start=text.index('yaitu ')+6
                end=text.rindex(') ')
                bad['options'][index]['text']=text[:start]+'999999'+text[end:]
                with self.assertRaises(AssertionError):check_math(bank.get(qid),bad)

    def test_cli_lifecycle_and_cached_hold(self):
        import contextlib,io,tempfile,cli
        from unittest.mock import patch
        from store import VariantStore
        from engine import original_record
        with tempfile.TemporaryDirectory() as tmp, patch('database.connection',side_effect=AssertionError('No DB')):
            path=Path(tmp)/'variants.jsonl';args=['--store',str(path)]
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                for qid in ['pg-1-1-1','mcma-2-1-6','kategori-1-3-9']:
                    self.assertEqual(cli.main(['gen',qid,'s11']+args),0)
                    before=path.read_bytes();self.assertEqual(cli.main(['gen',qid,'s11']+args),0)
                    self.assertEqual(path.read_bytes(),before)
                    self.assertEqual(cli.main(['regen',qid,'s11','--reason','test']+args),0)
                    self.assertEqual(cli.main(['view',qid,'s11','v1']+args),0)
                held=original_record(OriginalBank(BANK).get('pg-1-2-1'))
                held.update(seed=1,variant_ver=1,record_id='pg-1-2-1:s1:v1',config_ver=1,config_hash='fixture',
                    created_at='2026-10-05T00:00:00Z',draws_used=1,replacement_of=None,regen_reason=None)
                VariantStore(path).append(held);before=path.read_bytes()
                self.assertEqual(cli.main(['gen','pg-1-2-1','s1']+args),1)
                self.assertEqual(path.read_bytes(),before)

    def test_oracle_edges_and_simplest_radical(self):
        from drill_1_2_math import calc,rational,compare
        self.assertEqual(calc('sqrt(48)-4sqrt(3)'),{})
        self.assertFalse(rational(calc('sqrt(2)')))
        self.assertTrue(rational(calc('sqrt(16)')))
        self.assertEqual(calc('sqrt(2)*sqrt(2)'),calc('2'))
        self.assertLess(compare(calc('-2,65'),calc('-sqrt(7)')),0)
        self.assertEqual(calc('3 1/2*12.000'),calc('42.000'))
        with self.assertRaises(AssertionError):calc('1/0')
        bank=OriginalBank(BANK);cfg,_=ConfigStore(ROOT/'configs').load('pg-2-3-2')
        cfg['variables']['k']['range']=[3,3]
        result=generate(bank.get('pg-2-3-2'),cfg,1,[])
        self.assertIn('9sqrt(3)',next(o['text'] for o in result.cand['options'] if o['correct']))

    def test_workspace_registration(self):
        from bank import load_workspace_bank,BankError
        default=ROOT/'data/q0_bank.csv'
        old=load_workspace_bank(default,additional_paths=[ROOT/'data/tryout-1/q0_bank.csv',
            ROOT/'data/drill-1-indicators-6-10/q0_bank.csv', ROOT/'data/drill-1-indicators-11-15/q0_bank.csv',
            ROOT/'data/drill-1-indicators-20-23/q0_bank.csv'])
        new=load_workspace_bank(default)
        self.assertEqual(len(new.ids()),820)
        self.assertEqual(len(new.catalog()),109)
        for q in old.ids():self.assertEqual(new.get(q),old.get(q))
        self.assertEqual(len(load_workspace_bank(BANK).ids()),60)
        with self.assertRaises(BankError):load_workspace_bank(BANK,[BANK])

    def test_source_scope(self):
        self.assertTrue(BANK.exists(), 'phase1 source bank missing')
        bank = OriginalBank(BANK)
        self.assertEqual(len(bank.ids()), 60)
        self.assertEqual(Counter(bank.get(q)['format'] for q in bank.ids()), {'PG':30,'MCMA':18,'KATEGORI':12})
        self.assertEqual(len(bank.catalog()), 6)
        self.assertEqual({g['source_level'] for g in bank.catalog()}, {1,2,3})
        self.assertEqual({g['indicator'] for g in bank.catalog()}, {1,2})
        self.assertEqual(hashlib.sha256(BANK.with_name('source.docx').read_bytes()).hexdigest(),
                         'f12c25edf8b1e6a4a10daa19cbbe7459624450f619921186d0c75818e6b499c6')
        for q in bank.ids():
            o = bank.get(q)
            self.assertTrue(o['metadata']['source_text'])
            self.assertTrue(o['metadata']['original_explanation'])
            self.assertEqual(o['classification']['package_id'], 'drill-1')
        for q in ['pg-1-1-5','pg-1-2-1','pg-1-2-3','pg-1-3-1','pg-1-3-5','pg-2-1-1','pg-2-1-2','mcma-2-2-6','pg-2-2-4']:
            self.assertEqual(bank.get(q)['metadata']['generation_status'], 'HOLD_SOURCE', q)

    def check_indicator(self, indicator):
        self.assertTrue(BANK.exists(), 'phase1 source bank missing')
        from drill_1_2_math import check_math
        bank = OriginalBank(BANK); configs = ConfigStore(ROOT/'configs')
        active = [bank.get(q) for q in bank.ids() if bank.get(q)['classification']['indicator']==indicator
                  and bank.get(q)['metadata']['generation_status']=='ACTIVE']
        self.assertTrue(active)
        for o in active:
            with self.subTest(qid=o['id']):
                cfg,_ = configs.load(o['id'])
                self.assertEqual(validate_config(cfg,o), [])
                self.assertEqual(reproduce_original(o,cfg), ([],[]))
                values = build_values(cfg,lambda n,s:cfg['original_values'][n])
                check_math(o,assemble(cfg,values))
                stock=[]
                for seed in range(1,201):
                    result=generate(o,cfg,seed,stock)
                    check_math(o,result.cand);stock.append(result.cand)
                    if len(stock)==20:break
                self.assertEqual(len(stock),20)

    def test_indicator_1_math(self): self.check_indicator(1)
    def test_indicator_2_math(self): self.check_indicator(2)

    def test_status_guards(self):
        self.assertTrue(BANK.exists())
        bank=OriginalBank(BANK); configs=ConfigStore(ROOT/'configs')
        for q in bank.ids():
            o=bank.get(q)
            if o['metadata']['generation_status']=='ACTIVE':continue
            self.assertTrue(o['metadata']['reason'])
            self.assertEqual(configs.versions(q),[])
            with self.assertRaises(ConfigError):generate(o,{},1,[])

if __name__=='__main__':unittest.main()
