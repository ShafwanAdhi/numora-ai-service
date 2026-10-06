"""Source-faithful indicator 3 generators, independent rendered arithmetic."""
import sys
import re
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigError, ConfigStore, validate_config
from engine import generate, assemble, build_values
from lint import reproduce_original
from expr import RejectDraw

HOLD = {'pg-3-1-2', 'pg-3-1-3', 'pg-3-1-5', 'pg-3-2-2', 'pg-3-2-3',
        'pg-3-2-4', 'mcma-3-2-7', 'mcma-3-2-8', 'kategori-3-2-9', 'pg-3-3-3'}
BANK = ROOT/'data/drill-1-indicators-3-5/q0_bank.csv'

class Indicator3(unittest.TestCase):
    def test_oracle_rejects_wrong_echoed_operands(self):
        from drill_indicator3_math import check_math
        bank=OriginalBank(BANK)
        for qid in ['kategori-3-1-9','kategori-3-3-9','mcma-3-3-7',
                    'kategori-3-1-10','kategori-3-2-10','kategori-3-3-10']:
            original=deepcopy(bank.get(qid));original['metadata']['generation_status']='ACTIVE'
            cfg,_=ConfigStore(ROOT/'configs').load(qid)
            candidate=generate(original,cfg,1,[]).cand
            for i,option in enumerate(candidate['options']):
                if not re.search(r'\((?:sqrt\(|\d)',option['text']):continue
                bad=deepcopy(candidate)
                bad['options'][i]['text']=re.sub(r'(?<=sqrt\()\d+|(?<=\()\d+(?:,\d+)?','999',option['text'],count=1)
                with self.subTest(qid=qid,option=i):
                    with self.assertRaises(AssertionError):check_math(original,bad)

    def test_sum_rounding_interpretations_cannot_disagree(self):
        from drill_indicator3_math import check_math
        cfg,_=ConfigStore(ROOT/'configs').load('kategori-3-1-10')
        # sqrt(20)+sqrt(50) rounds to12, but separately rounded operands total11.
        with self.assertRaises(RejectDraw):build_values(cfg,lambda n,s:2)
        candidate=assemble(cfg,build_values(cfg,lambda n,s:2,check=False))
        with self.assertRaises(AssertionError):check_math(OriginalBank(BANK).get('kategori-3-1-10'),candidate)

    def test_hash_and_source_status_guards(self):
        bank=OriginalBank(BANK)
        for qid in HOLD:
            original=deepcopy(bank.get(qid));original['metadata']['generation_status']='HOLD_SOURCE'
            with self.assertRaises(ConfigError):generate(original,{},1,[])
        original=deepcopy(bank.get('pg-3-1-1'));original['metadata']['generation_status']='ACTIVE'
        cfg,_=ConfigStore(ROOT/'configs').load(original['id']);cfg['original_hash']='stale'
        with self.assertRaises(ConfigError):generate(original,cfg,1,[])

    def test_all_valid_sources_have_reproducing_math_checked_stock(self):
        bank = OriginalBank(BANK)
        for qid in bank.ids():
            if qid.split('-')[1] != '3': continue
            with self.subTest(qid=qid):
                path = ROOT/'configs'/qid/'v1.json'
                if bank.get(qid)['metadata']['generation_status'] != 'ACTIVE':
                    self.assertFalse(path.exists())
                    continue
                self.assertTrue(path.exists(), 'missing substantive generator')
                from drill_indicator3_math import check_math
                orig = deepcopy(bank.get(qid))
                orig['metadata']['generation_status'] = 'ACTIVE'
                cfg, _ = ConfigStore(ROOT/'configs').load(qid)
                self.assertEqual(validate_config(cfg, orig), [])
                self.assertEqual(reproduce_original(orig, cfg), ([], []))
                check_math(orig, assemble(cfg, build_values(cfg, lambda n,s: cfg['original_values'][n])))
                stock = []
                for seed in range(1,21):
                    candidate = generate(orig,cfg,seed,stock).cand
                    check_math(orig,candidate)
                    stock.append(candidate)
                for seed in range(201,251): check_math(orig,generate(orig,cfg,seed,[]).cand)
                bad = deepcopy(stock[0]);bad['options'][0]['correct'] = not bad['options'][0]['correct']
                with self.assertRaises(AssertionError): check_math(orig,bad)
                bad = deepcopy(stock[0]);bad['explanation'] += ' Hasil=999999.'
                with self.assertRaises(AssertionError): check_math(orig,bad)

if __name__ == '__main__': unittest.main()
