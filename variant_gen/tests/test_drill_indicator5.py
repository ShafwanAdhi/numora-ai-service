"""Indicator 5 source guards, independent arithmetic, and mutation checks."""
import copy
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from lint import reproduce_original

BANK = ROOT / 'data/drill-1-indicators-3-5/q0_bank.csv'
HELD = {'pg-5-1-5', 'pg-5-3-3', 'pg-5-2-4'}


class Indicator5(unittest.TestCase):
    def test_explanation_units_are_verified(self):
        from drill_indicator5_math import check_math
        bank=OriginalBank(BANK)
        for qid,old,new in [('pg-5-1-3','liter/menit','liter/jam'),
                            ('mcma-5-1-7','m persegi','cm persegi')]:
            o=bank.get(qid);cfg,_=ConfigStore(ROOT/'configs').load(qid)
            c=generate(o,cfg,77,[]).cand
            check_math(o,c)
            c['explanation']=c['explanation'].replace(old,new)
            with self.assertRaises(AssertionError):check_math(o,c)

    def test_all_originals_and_twenty_unique(self):
        from drill_indicator5_math import check_math
        bank = OriginalBank(BANK)
        ids = [q for q in bank.ids() if q.split('-')[1] == '5']
        self.assertEqual(len(ids), 30)
        configs = ConfigStore(ROOT / 'configs')
        for q in ids:
            with self.subTest(question=q):
                o = bank.get(q)
                self.assertTrue(o['metadata']['original_explanation'])
                if q in HELD:
                    self.assertEqual(o['metadata']['generation_status'], 'HOLD_SOURCE' if q=='pg-5-3-3' else 'DEFERRED_CONCEPTUAL')
                    self.assertTrue(o['metadata']['reason'])
                    self.assertEqual(configs.versions(q), [])
                    continue
                cfg, _ = configs.load(q)
                self.assertEqual(validate_config(cfg, o), [])
                self.assertEqual(reproduce_original(o, cfg), ([], []))
                check_math(o, assemble(cfg, build_values(cfg, lambda n, s: Fraction(str(cfg['original_values'][n])))))
                stock = []
                for seed in range(1, 21):
                    c = generate(o, cfg, seed, stock).cand
                    check_math(o, c)
                    stock.append(c)
                self.assertEqual(len(stock), 20)
                if q in ['pg-5-1-1','pg-5-2-1']:
                    ratios = {next(x['text'] for x in c['options'] if x['correct']) for c in stock}
                    self.assertGreater(len(ratios), 3)

    def test_oracle_rejects_wrong_key_option_and_explanation(self):
        from drill_indicator5_math import check_math
        bank = OriginalBank(BANK)
        for q in ['pg-5-1-1', 'pg-5-1-3', 'mcma-5-1-6', 'mcma-5-2-7', 'kategori-5-1-10']:
            o = bank.get(q)
            cfg, _ = ConfigStore(ROOT / 'configs').load(q)
            c = generate(o, cfg, 77, []).cand
            check_math(o, c)
            bad = copy.deepcopy(c)
            bad['options'][0]['correct'] = not bad['options'][0]['correct']
            with self.assertRaises(AssertionError): check_math(o, bad)
            bad = copy.deepcopy(c)
            bad['explanation'] = 'Hasil = 999999.'
            with self.assertRaises(AssertionError): check_math(o, bad)
            bad = copy.deepcopy(c)
            import re
            bad['explanation'] = re.sub(r'(?<!\d)\d', lambda m: '-'+m[0], bad['explanation'], count=1)
            with self.assertRaises(AssertionError): check_math(o, bad)
            bad = copy.deepcopy(c)
            correct = next(x for x in bad['options'] if x['correct'])
            correct['text'] = re.sub(r'\d+(?:[.,]\d+)*', '999999', correct['text'])
            with self.assertRaises(AssertionError): check_math(o, bad)

    def test_ratio_options_must_be_simplest(self):
        from drill_indicator5_math import check_math
        bank = OriginalBank(BANK)
        o = bank.get('pg-5-1-1')
        cfg, _ = ConfigStore(ROOT / 'configs').load(o['id'])
        c = generate(o, cfg, 7, []).cand
        option = next(x for x in c['options'] if x['correct'])
        a, b = map(int, option['text'].split(':'))
        option['text'] = f'{2*a}:{2*b}'
        with self.assertRaises(AssertionError): check_math(o, c)


if __name__ == '__main__': unittest.main()
