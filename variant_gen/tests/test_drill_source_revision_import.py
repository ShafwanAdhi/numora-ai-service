"""Revised source provenance remains valid after generator activation."""
import hashlib
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, ConfigError
from engine import generate
from drill_math import nums, stats

IDS=('pg-20-3-3','pg-21-2-2','pg-21-3-1','pg-21-3-4','pg-21-3-5',
     'mcma-21-3-8','kategori-21-3-9','pg-22-1-1','mcma-22-1-6',
     'mcma-22-1-7','mcma-22-3-8','pg-23-3-2','pg-23-3-5',
     'mcma-23-3-7','mcma-23-3-8','kategori-23-3-9')

class SourceRevisionImport(unittest.TestCase):
    def test_revision_archive_and_generator_activation(self):
        folder=ROOT/'data/drill-1-indicators-20-23'
        self.assertEqual(hashlib.sha256((folder/'source-revision-2026-10-07.docx').read_bytes()).hexdigest(),
                         '1edd91abfc4e9a2ad1143cc578d0df8da54becd711b8e0cdb1dc8dc1543608e9')
        bank=OriginalBank(folder/'q0_bank.csv');configs=ConfigStore(ROOT/'configs')
        for q in IDS:
            with self.subTest(question=q):
                o=bank.get(q)
                self.assertEqual(o['version'],2)
                self.assertEqual(o['metadata']['source_review_status'],'REVISED_CURRICULUM')
                self.assertEqual(o['metadata']['generation_status'],'ACTIVE')
                self.assertEqual(o['metadata']['generator_status'],'IMPLEMENTED')
                self.assertEqual(configs.versions(q),[1])
                self.assertEqual(configs.load(q)[0]['original_hash'],o['hash'])

    def test_source_keys_and_explicit_final_corrections(self):
        bank=OriginalBank(ROOT/'data/drill-1-indicators-20-23/q0_bank.csv')
        keys={'pg-20-3-3':'C','pg-21-2-2':'C','pg-21-3-1':'C','pg-21-3-4':'A',
              'pg-21-3-5':'C','mcma-21-3-8':'A,C','kategori-21-3-9':'1,2,4',
              'pg-22-1-1':'C','mcma-22-1-6':'A,B,D','mcma-22-1-7':'A,C',
              'mcma-22-3-8':'A,C,D','pg-23-3-2':'B','pg-23-3-5':'C',
              'mcma-23-3-7':'A,D','mcma-23-3-8':'A,C,D','kategori-23-3-9':'1,2,4'}
        for q,key in keys.items():
            o=bank.get(q)
            self.assertEqual(','.join(a['id'] for a in o['options'] if a['correct']),key,q)
        self.assertEqual([a['text'] for a in bank.get('pg-20-3-3')['options']],['100','105','110','115'])
        self.assertEqual([a['text'] for a in bank.get('pg-21-2-2')['options']],['65','68','70','75'])
        self.assertIn('70',bank.get('mcma-21-3-8')['options'][1]['text'])
        self.assertIn('Pernyataan 1',bank.get('pg-21-3-5')['stem'])
        self.assertEqual(nums(bank.get('pg-23-3-2')['options'][1]['text']),[Fraction(53,100)])

if __name__=='__main__':unittest.main()
