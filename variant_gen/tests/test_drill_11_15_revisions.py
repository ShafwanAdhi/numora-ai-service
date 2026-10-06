"""Independent answer checks cover all allowed inputs for the four revised generators."""
import sys
import unittest
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate, make_record
from expr import RejectDraw
from lint import reproduce_original
from drill_11_15_math import check_math

REVISED = ('mcma-11-1-7', 'pg-11-2-4', 'kategori-11-3-9', 'pg-15-4-2')


class RevisedGenerators1115(unittest.TestCase):
    def test_revised_sources_generate_correct_distinct_variants(self):
        bank = OriginalBank(ROOT / 'data/drill-1-indicators-11-15/q0_bank.csv')
        configs = ConfigStore(ROOT / 'configs')
        for q in REVISED:
            with self.subTest(question=q):
                original = bank.get(q)
                self.assertEqual(original['metadata']['generation_status'], 'ACTIVE')
                cfg, digest = configs.load(q)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                check_math(q, original)
                candidates = []
                for seed in range(1, 21):
                    result = generate(original, cfg, seed, candidates)
                    check_math(q, result.cand)
                    candidates.append(result.cand)
                    record = make_record(original, cfg, digest, seed, 1, result)
                    self.assertEqual(record['original_version'], 2)
                    self.assertEqual(record['classification'], original['classification'])
                    self.assertTrue(record['explanation'].strip())
                for seed in range(101, 201):
                    check_math(q, generate(original, cfg, seed, []).cand)
                self.assertEqual(generate(original, cfg, 37, []), generate(original, cfg, 37, []))

    def test_every_allowed_input_preserves_answers(self):
        bank = OriginalBank(ROOT / 'data/drill-1-indicators-11-15/q0_bank.csv')
        configs = ConfigStore(ROOT / 'configs')
        for q in REVISED:
            with self.subTest(question=q):
                original = bank.get(q)
                self.assertEqual(original['metadata']['generation_status'], 'ACTIVE')
                cfg, _ = configs.load(q)
                domains = {}
                for name, spec in cfg['variables'].items():
                    if spec['gen'] == 'derived':
                        continue
                    domains[name] = spec['values'] if spec['gen'] == 'choice' else range(
                        spec['range'][0], spec['range'][1] + 1, spec.get('step', 1))
                accepted = 0
                for combination in product(*domains.values()):
                    inputs = dict(zip(domains, combination))
                    try:
                        values = build_values(cfg, lambda name, spec: inputs[name])
                    except RejectDraw:
                        continue
                    with self.subTest(inputs=inputs):
                        check_math(q, assemble(cfg, values))
                    accepted += 1
                self.assertGreater(accepted, 0)


if __name__ == '__main__':
    unittest.main()
