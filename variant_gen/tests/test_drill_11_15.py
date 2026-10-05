"""Drill 11–15 source and generation checks; never write the user store."""
import hashlib
import json
import sys
import unittest
from itertools import product
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, load_workspace_bank
from expr import render, PLACEHOLDER
from config_store import ConfigError, ConfigStore, validate_config
from engine import generate, assemble, build_values, make_record
from expr import RejectDraw
from handoff import export_record
from store import StoreError
from lint import reproduce_original
from drill_11_15_math import check_math

BANK = ROOT / 'data/drill-1-indicators-11-15/q0_bank.csv'


class Drill1115Tests(unittest.TestCase):
    def test_bank_identity_and_source(self):
        self.assertTrue(BANK.exists(), 'Drill 11–15 original bank is missing')
        bank = OriginalBank(BANK)
        self.assertEqual(len(bank.ids()), 250)
        self.assertEqual(Counter(bank.get(q)['format'] for q in bank.ids()),
                         {'PG': 125, 'MCMA': 75, 'KATEGORI': 50})
        self.assertEqual(hashlib.sha256(BANK.with_name('source.docx').read_bytes()).hexdigest(),
                         '08b30681b07398eaea08331029f8c6934d576aaa31294a6529fd8ac69dff5383')
        for q in bank.ids():
            o = bank.get(q)
            self.assertTrue(o['metadata']['source_text'])
            self.assertTrue(o['metadata']['original_explanation'])

    def test_catalog_complete(self):
        self.assertTrue(BANK.exists(), 'Drill 11–15 original bank is missing')
        bank = OriginalBank(BANK)
        self.assertEqual(len(bank.catalog()), 25)
        self.assertEqual({len(g['question_ids']) for g in bank.catalog()}, {10})
        for q in bank.ids():
            _, indicator, level, number = q.split('-')
            o = bank.get(q)
            self.assertEqual(o['classification'], {'activity': 'DRILL', 'package_id': 'drill-1',
                'indicator': int(indicator), 'source_level': int(level)})
            self.assertEqual(o['metadata']['source_number'], int(number))
            self.assertEqual(o['cognitive_level'],
                             {1:'C3',2:'C3 & C4',3:'C4',4:'C4 & C5',5:'C5'}[int(level)])

    def test_workspace_merge_and_isolation(self):
        self.assertTrue(BANK.exists(), 'Drill 11–15 original bank is missing')
        old = load_workspace_bank(ROOT/'data/q0_bank.csv', additional_paths=[
            ROOT/'data/tryout-1/q0_bank.csv', ROOT/'data/drill-1-indicators-20-23/q0_bank.csv',
            ROOT/'data/drill-1-indicators-6-10/q0_bank.csv'])
        merged = load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(set(merged.ids()), set(old.ids()) | set(OriginalBank(BANK).ids()))
        self.assertEqual(len(load_workspace_bank(BANK).ids()), 250)
        for q in old.ids(): self.assertEqual(merged.get(q), old.get(q))

    def test_status_guards(self):
        self.assertTrue(BANK.exists(), 'Drill 11–15 original bank is missing')
        for q in OriginalBank(BANK).ids():
            o = OriginalBank(BANK).get(q)
            if o['metadata']['generation_status'] == 'ACTIVE': continue
            self.assertTrue(o['metadata']['reason'].strip())
            self.assertTrue(validate_config({}, o))
            with self.assertRaises(ConfigError): generate(o, {}, 1, [])

    def test_literal_set_and_omml_formatting(self):
        self.assertEqual(render('{ {member} }', {'member':1}), '{ 1 }')
        self.assertFalse(PLACEHOLDER.search('{ 1 }'))
        self.assertFalse(PLACEHOLDER.search('{ a }'))
        self.assertTrue(PLACEHOLDER.search('{missing}'))
        o = OriginalBank(BANK).get('pg-12-5-3')
        self.assertIn('3^(8)', o['stem'])
        self.assertIn('U_8', o['stem'])

    def check_indicator(self, indicator):
        bank = OriginalBank(BANK)
        configs = ConfigStore(ROOT/'configs')
        for q in bank.ids():
            o = bank.get(q)
            if o['classification']['indicator'] != indicator: continue
            if o['metadata']['generation_status'] != 'ACTIVE': continue
            with self.subTest(question=q):
                self.assertTrue(configs.versions(q), 'Missing generator config')
                cfg, _ = configs.load(q)
                self.assertEqual(validate_config(cfg, o), [])
                self.assertEqual(reproduce_original(o, cfg), ([], []))
                result = generate(o, cfg, 1, [])
                self.assertTrue(result.cand['explanation'])

    def test_indicator_11_reproduction(self): self.check_indicator(11)
    def test_indicator_12_reproduction(self): self.check_indicator(12)
    def test_indicator_13_reproduction(self): self.check_indicator(13)
    def test_indicator_14_reproduction(self): self.check_indicator(14)
    def test_indicator_15_reproduction(self): self.check_indicator(15)

    def test_rendered_math_all_indicators(self):
        bank, configs = OriginalBank(BANK), ConfigStore(ROOT/'configs')
        for q in bank.ids():
            o=bank.get(q)
            if o['metadata']['generation_status']!='ACTIVE': continue
            cfg,_=configs.load(q)
            for seed in (0,1,2):
                with self.subTest(question=q,seed=seed):
                    check_math(q,o if seed==0 else generate(o,cfg,seed,[]).cand)

    def test_math_formula_punctuation(self):
        bank, configs = OriginalBank(BANK), ConfigStore(ROOT/'configs')
        for q in bank.ids():
            o=bank.get(q)
            if o['metadata']['generation_status']!='ACTIVE': continue
            cfg,_=configs.load(q)
            c=generate(o,cfg,1,[]).cand
            with self.subTest(question=q):
                for text in [c['stem'],c['explanation']]+[a['text'] for a in c['options']]:
                    self.assertNotIn(',)',text,'prose comma was swallowed into a mathematical formula')

    def test_parameter_boundaries_and_angle_equalities(self):
        bank, configs = OriginalBank(BANK), ConfigStore(ROOT/'configs')
        for q in bank.ids():
            o=bank.get(q)
            if o['metadata']['generation_status']!='ACTIVE': continue
            cfg,_=configs.load(q)
            domains={}
            for name,spec in cfg['variables'].items():
                if spec['gen']=='derived': continue
                if spec['gen']=='choice': domain=spec['values']
                else:
                    lo,hi=spec['range'];domain=[lo,hi,cfg['original_values'][name]]
                    if name=='t': domain+= [x for x in (-10,-5,4,5,7,10,15,20,30) if lo<=x<=hi]
                domains[name]=sorted(set(domain))
            for combination in product(*domains.values()):
                values=dict(zip(domains,combination))
                try: built=build_values(cfg,lambda name,spec:values[name])
                except RejectDraw: continue
                with self.subTest(question=q,values=values): check_math(q,assemble(cfg,built))

    def test_export_requires_single_canonical_cognitive_label(self):
        bank=OriginalBank(BANK);o=bank.get('pg-11-1-4');cfg,h=ConfigStore(ROOT/'configs').load(o['id'])
        record=make_record(o,cfg,h,1,1,generate(o,cfg,1,[]))
        mapping=dict(questionExternalId=o['id'],originalHash=o['hash'],originalVersion=o['version'],
            familyId='00000000-0000-0000-0000-000000000001',
            parentQuestionVersionId='00000000-0000-0000-0000-000000000002',
            scoringRubricVersionId='00000000-0000-0000-0000-000000000003')
        for label in ('C1','C2','C3','C4','C5','C6'):
            record['cognitive_level']=label
            self.assertEqual(export_record(record,mapping)['payload']['cognitiveLevel'],label)
        for label in ('C3 & C4','C4 & C5','C0','C7','C3 ','',None):
            record['cognitive_level']=label
            with self.subTest(label=label),self.assertRaisesRegex(StoreError,'cognitive'):
                export_record(record,mapping)

    def test_saved_audit_matches_configs_and_replays_math(self):
        bank, configs = OriginalBank(BANK), ConfigStore(ROOT/'configs')
        report=json.loads(BANK.with_name('audit.json').read_text(encoding='utf8'))
        self.assertEqual({r['question_id'] for r in report['rows']},set(bank.ids()))
        self.assertEqual(report['summary'],dict(Counter(r['sampling_status'] for r in report['rows'])))
        for row in report['rows']:
            q=row['question_id'];o=bank.get(q)
            with self.subTest(question=q):
                self.assertEqual(row['original_hash'],o['hash'])
                self.assertEqual(row['generation_status'],o['metadata']['generation_status'])
                if row['generation_status']!='ACTIVE':
                    self.assertEqual(row['sampling_status'],'SKIP')
                    self.assertFalse(configs.versions(q))
                    continue
                cfg,h=configs.load(q)
                self.assertEqual(row['config_hash'],h)
                self.assertEqual(row['config_version'],cfg['config_version'])
                self.assertFalse(row['math_errors'])
                others=[]
                for seed in row['successful_seeds']:
                    c=generate(o,cfg,seed,others).cand
                    check_math(q,c)
                    others.append(c)
                self.assertEqual(len(others),row['distinct_count'])

    def test_congruence_reasons_and_human_dimensions(self):
        bank, configs = OriginalBank(BANK), ConfigStore(ROOT/'configs')
        for q in ('pg-15-2-3','mcma-15-1-8'):
            o=bank.get(q);cfg,_=configs.load(q);c=generate(o,cfg,2,[]).cand
            self.assertIn('SAS',c['explanation'])
            if q.startswith('mcma'):self.assertIn('SSS',c['explanation']);self.assertIn('AAA',c['explanation'])
        for q in ('pg-15-1-5','pg-15-4-4'):
            o=bank.get(q);cfg,_=configs.load(q)
            for seed in (1,2,3,19,41):
                c=generate(o,cfg,seed,[]).cand
                with self.subTest(question=q,seed=seed):
                    import re
                    from drill_11_15_math import number
                    height=number(re.search(r'siswa setinggi ([\d,]+)',c['stem'])[1])
                    self.assertTrue(100<=height<=220 if 'cm' in c['stem'] else 1<=height<=2.2)
                    check_math(q,c)


if __name__ == '__main__': unittest.main()
