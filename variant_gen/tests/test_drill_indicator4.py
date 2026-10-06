"""Independent rendered mathematics and original-reproduction checks for indicator 4."""
import copy
import itertools
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from lint import reproduce_original

HOLD = {'pg-4-1-1', 'pg-4-2-2', 'pg-4-2-5', 'pg-4-3-1'}
HOLD |= {f'mcma-4-{level}-8' for level in [1,2,3]}
HOLD |= {f'kategori-4-{level}-{item}' for level in [1,2,3] for item in [9,10]}

class Indicator4(unittest.TestCase):
    def test_prime_analysis_rejects_changed_concept(self):
        from drill_indicator4_math import check_math
        original = OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv').get('pg-4-2-4')
        cfg, _ = ConfigStore(ROOT/'configs').load(original['id'])
        candidate = assemble(cfg, build_values(cfg, lambda n, s: cfg['original_values'][n]))
        check_math(original, candidate)
        mutations = [(0, 'merupakan faktor', 'bukan faktor'),
                     (1, 'bilangan prima', 'bilangan komposit'),
                     (2, 'lebih cepat dan singkat', 'menggunakan bilangan prima'),
                     (3, 'tidak habis dibagi', 'habis dibagi')]
        for index, before, after in mutations:
            with self.subTest(option=index):
                bad = copy.deepcopy(candidate)
                bad['options'][index]['text'] = bad['options'][index]['text'].replace(before, after)
                with self.assertRaises(AssertionError): check_math(original, bad)

    def test_math_and_reproduction(self):
        from drill_indicator4_math import check_math
        bank = OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv')
        configs = ConfigStore(ROOT/'configs')
        ids = [q for q in bank.ids() if q.split('-')[1] == '4']
        self.assertEqual(len(ids), 30)
        for qid in ids:
            with self.subTest(qid=qid):
                if bank.get(qid)['metadata']['generation_status'] != 'ACTIVE':
                    self.assertEqual(configs.versions(qid), [])
                    continue
                original = copy.deepcopy(bank.get(qid))
                original['metadata']['generation_status'] = 'ACTIVE'
                cfg, _ = configs.load(qid)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                stale = dict(cfg, original_hash='stale')
                self.assertTrue(validate_config(stale, original))
                check_math(original, assemble(cfg, build_values(cfg, lambda n, s: cfg['original_values'][n])))
                domains = {n: spec.get('values', range(spec.get('range', [0, 0])[0], spec.get('range', [0, 0])[1]+1))
                           for n, spec in cfg['variables'].items() if spec['gen'] != 'derived'}
                for point in itertools.product(*domains.values()):
                    values = dict(zip(domains, point))
                    check_math(original, assemble(cfg, build_values(cfg, lambda n, s: values[n])))
                stock = []
                for seed in range(1, 21):
                    result = generate(original, cfg, seed, stock)
                    check_math(original, result.cand)
                    stock.append(result.cand)
                for index in range(len(stock[0]['options'])):
                    bad = copy.deepcopy(stock[0])
                    bad['options'][index]['correct'] = not bad['options'][index]['correct']
                    with self.assertRaises(AssertionError): check_math(original, bad)
                bad = copy.deepcopy(stock[0])
                bad['explanation'] += ' 1+1=999.'
                with self.assertRaises(AssertionError): check_math(original, bad)

if __name__ == '__main__': unittest.main()
