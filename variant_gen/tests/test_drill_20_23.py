"""Drill source provenance and generator safety; all writes belong to temporary stores."""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, BankError, load_workspace_bank, original_hash
from config_store import ConfigError, ConfigStore, validate_config
from engine import generate, original_record, make_record
from handoff import export_record
from lint import reproduce_original
from store import StoreError

BANK = ROOT / 'data/drill-1-indicators-20-23/q0_bank.csv'


class DrillTests(unittest.TestCase):
    def test_new_bank_identity_and_catalog(self):
        bank = OriginalBank(BANK)
        self.assertEqual(len(bank.ids()), 120)
        self.assertEqual(Counter(bank.get(q)['format'] for q in bank.ids()), dict(PG=60, MCMA=36, KATEGORI=24))
        self.assertEqual(len(bank.catalog()), 20)
        self.assertEqual(sum(not g['question_ids'] for g in bank.catalog()), 8)
        self.assertEqual({len(g['question_ids']) for g in bank.catalog() if g['source_level'] < 4}, {10})
        for qid in bank.ids():
            o = bank.get(qid)
            self.assertEqual(o['classification']['activity'], 'DRILL')
            self.assertEqual(o['classification']['package_id'], 'drill-1')
            self.assertTrue(o['metadata']['source_text'])
            self.assertTrue(o['metadata']['original_explanation'])
        self.assertEqual(bank.get('pg-20-3-3')['metadata']['source_number'], 23)
        self.assertEqual(bank.get('pg-20-2-1')['cognitive_level'], 'C3 & C4')
        self.assertEqual(hashlib.sha256(BANK.with_name('source.docx').read_bytes()).hexdigest(),
                         '2129f33e8ecc524e4c489b668798e8db0393f4b01348bf964cf1a8d420160575')

    def test_workspace_preserves_existing_banks(self):
        legacy = OriginalBank(ROOT/'data/q0_bank.csv')
        tryout = OriginalBank(ROOT/'data/tryout-1/q0_bank.csv')
        new = OriginalBank(BANK)
        workspace = load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(len(legacy.ids()), 120)
        early = OriginalBank(ROOT/'data/drill-1-indicators-6-10/q0_bank.csv')
        self.assertEqual(set(workspace.ids()), set(legacy.ids()+tryout.ids()+new.ids()+early.ids()+OriginalBank(ROOT/'data/drill-1-indicators-11-15/q0_bank.csv').ids()+OriginalBank(ROOT/'data/drill-1-indicators-1-2/q0_bank.csv').ids()+OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv').ids()))
        self.assertEqual(len(load_workspace_bank(BANK).ids()), 120)
        for qid in legacy.ids()+tryout.ids():
            self.assertEqual(workspace.get(qid), (legacy if qid in legacy.ids() else tryout).get(qid))

    def test_source_conflicts_and_guards(self):
        bank = OriginalBank(BANK)
        for qid in ['pg-20-3-3','pg-21-2-2','pg-21-3-1','pg-21-3-4','pg-21-3-5',
                    'mcma-21-3-8','kategori-21-3-9','pg-22-1-1','mcma-22-1-6',
                    'mcma-22-1-7','mcma-22-3-8']:
            orig = bank.get(qid)
            self.assertEqual(orig['metadata']['generation_status'], 'ACTIVE')
            self.assertEqual(orig['metadata']['source_review_status'], 'REVISED_CURRICULUM')
            self.assertEqual(orig['metadata']['generator_status'], 'IMPLEMENTED')
            self.assertEqual(ConfigStore(ROOT/'configs').versions(qid), [1])
            self.assertTrue(validate_config({}, orig))
            with self.assertRaises(ConfigError): generate(orig, {}, 1, [])
        self.assertNotEqual(bank.get('pg-20-3-3')['options'][2]['text'],
                            bank.get('pg-20-3-3')['options'][3]['text'])
        self.assertEqual(bank.get('pg-23-1-2')['metadata']['generation_status'], 'DEFERRED_CONCEPTUAL')

    def test_custom_category_labels_and_hash(self):
        bank = OriginalBank(BANK)
        orig = bank.get('kategori-20-1-9')
        rec = original_record(orig)
        self.assertEqual(rec['answer_categories'], {'1':'Kuantitatif','2':'Kualitatif','3':'Kuantitatif'})
        other = bank.get('kategori-20-2-10')
        self.assertEqual(original_record(other)['answer_categories'],
                         {'1':'Sesuai','2':'Tidak Sesuai','3':'Sesuai','4':'Tidak Sesuai'})
        old_hash = orig['hash']
        orig['metadata']['category_labels'] = ['Jumlah','Jenis']
        self.assertNotEqual(original_hash(orig), old_hash)
        legacy = OriginalBank(ROOT/'data/q0_bank.csv').get('kategori-16-1-9')
        before = original_hash(legacy)
        legacy['metadata'] = {'category_labels':['Benar','Salah']}
        self.assertEqual(original_hash(legacy), before)
        with self.assertRaisesRegex(StoreError, 'boolean'):
            export_record(rec, {})
        # Exercise custom-label generation with a numeric fixture, without approving
        # a new academic scenario for either deferred source question.
        fixture = bank.get('kategori-21-1-9')
        cfg,h = ConfigStore(ROOT/'configs').load(fixture['id'])
        fixture['metadata']['category_labels'] = ['Kategori A','Kategori B']
        fixture['hash'] = original_hash(fixture)
        self.assertTrue(any('original_hash' in error for error in validate_config(cfg,fixture)))
        cfg['original_hash'] = fixture['hash']
        result = generate(fixture,cfg,5,[])
        record = make_record(fixture,cfg,h,5,1,result)
        self.assertEqual(set(record['answer_categories']), {'1','2','3','4'})
        self.assertEqual(record['answer_categories']['3'], 'Kategori B')
        self.assertIn('3: Kategori B',record['explanation'])
        fixture['metadata']['category_labels'] = ['Baru A','Baru B']
        self.assertEqual(record['answer_categories']['3'],'Kategori B')

    def test_invalid_labels_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'q0_bank.csv'
            shutil.copyfile(BANK,path)
            for qid, labels in [('kategori-20-1-9',['','Kualitatif']),
                                ('kategori-20-1-9',['a','a']), ('pg-20-1-1',['a','b'])]:
                path.with_name('question_metadata.json').write_text(json.dumps({qid:{
                    'generation_status':'ACTIVE','category_labels':labels}}),encoding='utf8')
                with self.assertRaises(BankError): OriginalBank(path)

    def test_active_configs_reproduce(self):
        bank = OriginalBank(BANK)
        for qid in bank.ids():
            orig = bank.get(qid)
            if orig['metadata']['generation_status'] != 'ACTIVE': continue
            with self.subTest(question=qid):
                cfg, _ = ConfigStore(ROOT/'configs').load(qid)
                self.assertEqual(validate_config(cfg,orig), [])
                self.assertEqual(reproduce_original(orig,cfg), ([],[]))

    def test_active_stock_and_independent_math(self):
        from drill_math import check_math
        from test_drill_20_23_revisions import REVISED, check_revised_math
        from unittest.mock import patch
        bank = OriginalBank(BANK)
        configs = ConfigStore(ROOT/'configs')
        with patch('database.connection', side_effect=AssertionError('generator must not connect to DB')):
            for qid in bank.ids():
                orig = bank.get(qid)
                if orig['metadata']['generation_status'] != 'ACTIVE': continue
                with self.subTest(question=qid):
                    cfg,_ = configs.load(qid)
                    candidates = []
                    from engine import GenerationError
                    for seed in range(1,201):
                        try: result = generate(orig,cfg,seed,candidates)
                        except GenerationError: continue
                        if qid in REVISED: check_revised_math(self,orig,result.cand)
                        else: check_math(self,orig,result)
                        candidates.append(result.cand)
                        if len(candidates) == 20: break
                    self.assertEqual(len(candidates),20)

    def test_frequency_rounding_tie(self):
        from drill_math import check_math
        orig=OriginalBank(BANK).get('kategori-23-2-10')
        cfg,_=ConfigStore(ROOT/'configs').load(orig['id'])
        result=generate(orig,cfg,24,[])
        self.assertEqual(result.values['observed'],346)
        self.assertEqual(result.values['trials'],400)
        self.assertIn('0,87',result.cand['options'][1]['text'])
        check_math(self,orig,result)

    def test_cli_hold_original_is_visibly_unapproved(self):
        import contextlib, io, cli
        with tempfile.TemporaryDirectory() as tmp:
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(cli.main(['view','pg-21-3-1','s0','--bank',str(BANK),
                                           '--store',str(Path(tmp)/'variants.jsonl')]),0)
            text=output.getvalue()
            self.assertIn('ACTIVE',text)
            self.assertIn('89',text)
            self.assertNotIn('belum disahkan',text)
            self.assertFalse((Path(tmp)/'variants.jsonl').exists())

    def test_cli_hold_rejects_even_an_existing_seed(self):
        import contextlib, io, cli
        orig=OriginalBank(BANK).get('pg-21-3-1')
        record=original_record(orig)
        record.update(seed=1,variant_ver=1,record_id=orig['id']+':s1:v1',config_ver=1,
                      config_hash='fixture',draws_used=1,replacement_of=None,regen_reason=None,
                      created_at='2026-10-05T00:00:00Z')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'variants.jsonl';path.write_text(json.dumps(record)+'\n',encoding='utf-8')
            before=path.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main(['gen',orig['id'],'s1','--bank',str(BANK),'--store',str(path)]),0)
            self.assertEqual(path.read_bytes(),before)


if __name__ == '__main__': unittest.main()
