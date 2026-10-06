"""Checks revised sources and answers from rendered questions, without generator formulas."""
import hashlib
import sys
import unittest
import re
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import generate, build_values, assemble
from expr import RejectDraw
from lint import reproduce_original
from drill_math import nums, stats
from fractions import Fraction

REVISED = (
    'pg-20-3-3', 'pg-21-2-2', 'pg-21-3-1', 'pg-21-3-4', 'pg-21-3-5',
    'mcma-21-3-8', 'kategori-21-3-9', 'pg-22-1-1', 'mcma-22-1-6',
    'mcma-22-1-7', 'mcma-22-3-8', 'pg-23-3-2', 'pg-23-3-5',
    'mcma-23-3-7', 'mcma-23-3-8', 'kategori-23-3-9',
)


def check_revised_math(test, original, candidate):
    q = original['id']
    stem, options = candidate['stem'], candidate['options']
    numbers = nums(stem)
    if q in ('pg-21-3-5', 'pg-22-1-1', 'mcma-22-1-6', 'mcma-22-1-7', 'mcma-22-3-8'):
        a = nums(re.search(r'(?:Kelompok|kelompok) A: ([\d, .]+)',stem)[1])
        b = nums(re.search(r'(?:Kelompok|kelompok) B: ([\d, .]+)',stem)[1])
        test.assertEqual((len(a), len(b)), (5, 5))
        aa, bb = stats(a), stats(b)
        am, bm = aa['mean'], bb['mean']
        ad, bd = aa['median'], bb['median']
        ar, br = aa['range'], bb['range']
        if q == 'pg-21-3-5':
            claims = [am < bm, ad < bd, br > ar, aa['modes'] != bb['modes']]
            true_claims = {i + 1 for i, correct in enumerate(claims) if correct}
            flags = [set(nums(o['text'])) == true_claims for o in options]
        elif q == 'pg-22-1-1':
            flags = [am > bm, bm > am, am == bm, False]
        elif q == 'mcma-22-1-6':
            flags = [am > bm, ad == bd, ar < br, ar > br]
        elif q == 'mcma-22-1-7':
            test.assertEqual((len(aa['modes']), len(bb['modes'])), (1, 1))
            flags = [am == bm, ad > bd, ar == br, next(iter(aa['modes'])) > next(iter(bb['modes']))]
        else:
            flags = [am > bm, ad < bd, ar > br, br < ar]
    elif q == 'pg-20-3-3':
        answer = 6 * numbers[-1] - sum(numbers[:5])
        flags = [nums(o['text'])[0] == answer for o in options]
    elif q == 'pg-21-2-2':
        answer = 5 * numbers[0] - sum(numbers[1:])
        flags = [nums(o['text'])[0] == answer for o in options]
    elif q == 'pg-21-3-1':
        answer = numbers[2] * numbers[3] - numbers[0] * numbers[1]
        flags = [nums(o['text'])[0] == answer for o in options]
    elif q == 'pg-21-3-4':
        answer = (sum(numbers[1:5]) + numbers[-1]) / 5
        flags = [nums(o['text'])[0] == answer for o in options]
    elif q == 'mcma-21-3-8':
        before = list(numbers[:5])
        after = list(before)
        after[after.index(numbers[-2])] = numbers[-1]
        aa, bb = stats(before), stats(after)
        n0, n1, n2, n3 = [nums(o['text']) for o in options]
        flags = [aa['modes'] == bb['modes'] and n0[0] in bb['modes'],
                 aa['median'] != bb['median'] and bb['median'] == n1[0],
                 aa['max'] == n2[0] and bb['max'] == n2[1] and bb['max'] > aa['max'],
                 len(before) == n3[0] and len(after) == n3[1]]
    elif q == 'kategori-21-3-9':
        aa = stats(numbers)
        claims = [nums(o['text'])[0] for o in options]
        flags = [claims[0] in aa['modes'], claims[1] == aa['median'],
                 claims[2] == aa['range'], claims[3] == sum(numbers)]
    else:
        trials, observed = (numbers[0], numbers[-1])
        test.assertTrue(0 <= observed <= trials)
        frequency = observed / trials
        if q == 'pg-23-3-2':
            flags = [nums(o['text'])[0] == frequency for o in options]
        elif q == 'pg-23-3-5':
            flags = [nums(options[0]['text'])[-1] == frequency,
                     nums(options[1]['text'])[-1] == frequency,
                     frequency < Fraction(1, 6),
                     nums(options[3]['text'])[-1] == Fraction(1, 6)]
        elif q in ('mcma-23-3-7', 'mcma-23-3-8'):
            flags = [nums(options[0]['text'])[0] == frequency,
                     nums(options[1]['text'])[0] == frequency,
                     nums(options[2]['text'])[0] == Fraction(1, 2),
                     True if q.endswith('-8') else nums(options[3]['text'])[0] == Fraction(1, 2)]
        elif q == 'kategori-23-3-9':
            flags = [nums(options[0]['text'])[0] == frequency,
                     frequency < Fraction(1, 2),
                     nums(options[2]['text'])[0] == Fraction(1, 2), True]
        else:
            raise AssertionError('Missing independent check: ' + q)
    test.assertEqual([o['correct'] for o in options], flags, q)
    test.assertEqual(sum(flags), sum(o['correct'] for o in original['options']), q)


class RevisedDrillTests(unittest.TestCase):
    def test_parameter_boundaries_preserve_every_option(self):
        bank = OriginalBank(ROOT / 'data/drill-1-indicators-20-23/q0_bank.csv')
        configs = ConfigStore(ROOT / 'configs')
        for q in REVISED:
            o=bank.get(q);cfg,_=configs.load(q);domains={}
            for name,spec in cfg['variables'].items():
                if spec['gen']=='derived':continue
                values=spec['values'] if spec['gen']=='choice' else [*spec['range'],cfg['original_values'][name]]
                if name=='trials' and 1000 in range(spec['range'][0],spec['range'][1]+1,spec['step']):values+= [1000]
                if name=='p' and spec['gen']=='range':
                    values += [v for v in (49,50,51,499,500,501) if spec['range'][0]<=v<=spec['range'][1]]
                domains[name]=sorted(set(values))
            accepted=0
            for combination in product(*domains.values()):
                free=dict(zip(domains,combination))
                try:values=build_values(cfg,lambda name,spec:free[name])
                except RejectDraw:continue
                with self.subTest(question=q,parameters=free):
                    check_revised_math(self,o,assemble(cfg,values))
                accepted+=1
            self.assertGreater(accepted,0,q)

    def test_repeatability_and_additional_seeds(self):
        bank = OriginalBank(ROOT / 'data/drill-1-indicators-20-23/q0_bank.csv')
        configs = ConfigStore(ROOT / 'configs')
        for q in REVISED:
            o=bank.get(q);cfg,_=configs.load(q)
            for seed in range(101,201):
                with self.subTest(question=q,seed=seed):
                    result=generate(o,cfg,seed,[])
                    check_revised_math(self,o,result.cand)
            first=generate(o,cfg,37,[]);again=generate(o,cfg,37,[])
            self.assertEqual(first,again,q)

    def test_revised_sources_generate_twenty_distinct_correct_variants(self):
        bank = OriginalBank(ROOT / 'data/drill-1-indicators-20-23/q0_bank.csv')
        configs = ConfigStore(ROOT / 'configs')
        for q in REVISED:
            with self.subTest(question=q):
                original = bank.get(q)
                self.assertEqual(original['version'], 2)
                self.assertEqual(original['metadata']['generation_status'], 'ACTIVE')
                cfg, _ = configs.load(q)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                check_revised_math(self, original, original)
                candidates = []
                for seed in range(1, 101):
                    result = generate(original, cfg, seed, candidates)
                    check_revised_math(self, original, result.cand)
                    self.assertTrue(result.cand['explanation'].strip())
                    candidates.append(result.cand)
                    if len(candidates) == 20:
                        break
                self.assertEqual(len(candidates), 20, q)

    def test_source_archives_preserve_both_documents(self):
        folder = ROOT / 'data/drill-1-indicators-20-23'
        self.assertEqual(hashlib.sha256((folder / 'source.docx').read_bytes()).hexdigest(),
                         '2129f33e8ecc524e4c489b668798e8db0393f4b01348bf964cf1a8d420160575')
        revised = folder / 'source-revision-2026-10-07.docx'
        self.assertTrue(revised.exists())
        self.assertEqual(hashlib.sha256(revised.read_bytes()).hexdigest(),
                         '1edd91abfc4e9a2ad1143cc578d0df8da54becd711b8e0cdb1dc8dc1543608e9')


if __name__ == '__main__':
    unittest.main()
