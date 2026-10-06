"""Check transformation claims from rendered text, independently of config formulas."""
import itertools
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate, GenerationError, make_record
from expr import RejectDraw, to_num
from filters import correct_set, signature, validate_candidate
from lint import reproduce_original

IDS = ('mcma-17-1-8', 'kategori-17-2-10')
FACTORS = (-4, -3, -2, -0.5, 0.5, 2, 3, 4)


class TransformPropertyGenerators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = OriginalBank(ROOT / 'data/q0_bank.csv')
        cls.configs = ConfigStore(ROOT / 'configs')

    def setup_question(self, qid):
        self.assertEqual(self.configs.versions(qid), [1], 'Missing requested generator')
        return self.bank.get(qid), self.configs.load(qid)[0]

    def check_rendered(self, original, candidate):
        factor = Fraction(re.search(r'faktor skala k=(-?\d+(?:,\d+)?)', candidate['stem'])[1].replace(',', '.'))
        self.assertNotIn(factor, (0, 1, -1))
        expected = []
        for option in candidate['options']:
            text = option['text']
            if text.startswith('Dilatasi'):
                self.assertEqual(Fraction(re.search(r'faktor skala (-?\d+(?:,\d+)?)', text)[1].replace(',', '.')), factor)
                truth = 'mengubah ukuran bangun tetapi' in text
            else:
                self.assertTrue(text.startswith(('Translasi', 'Refleksi', 'Rotasi')))
                truth = 'mempertahankan' in text
            expected.append(truth)
            self.assertEqual(option['correct'], truth, text)
            verdict = 'Benar' if truth else 'Salah'
            self.assertIn(f"Pernyataan {option['id']}: {verdict}.", candidate['explanation'])
        self.assertEqual(sum(expected), 3 if original['format'] == 'MCMA' else 2)
        self.assertEqual(validate_candidate(candidate, original, []), [])
        self.assertNotEqual(correct_set(candidate['options']), correct_set(original['options']))

    def test_activation_and_original_v2_reproduction(self):
        for qid in IDS:
            with self.subTest(question=qid):
                original, cfg = self.setup_question(qid)
                self.assertEqual(original['version'], 2)
                self.assertEqual(original['metadata']['generation_status'], 'ACTIVE')
                self.assertEqual(original['metadata']['generator_status'], 'IMPLEMENTED')
                self.assertEqual(original['metadata']['source_review_status'], 'REVISED_CURRICULUM')
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))

    def test_entire_finite_domain_has_correct_keys_and_explanations(self):
        for qid in IDS:
            original, cfg = self.setup_question(qid)
            candidates, keys = [], set()
            for k, false_slot in itertools.product(FACTORS, range(1, len(original['options']) + 1)):
                inputs = {'variant': 1, 'k': to_num(k), 'false_slot': false_slot}
                values = build_values(cfg, lambda name, spec: inputs[name])
                candidate = assemble(cfg, values)
                self.check_rendered(original, candidate)
                self.assertEqual(validate_candidate(candidate, original, candidates), [])
                candidates.append(candidate)
                keys.add(tuple(o['id'] for o in candidate['options'] if o['correct']))
            self.assertEqual(len({signature(c['stem'], c['options']) for c in candidates}), len(FACTORS) * len(original['options']))
            self.assertEqual(len(keys), len(original['options']))
            # Exhaustion must fail, never emit an already seen candidate.
            with self.assertRaises(GenerationError):
                generate(original, dict(cfg, max_draws=2), 1, candidates)

    def test_invalid_factors_are_rejected(self):
        for qid in IDS:
            _, cfg = self.setup_question(qid)
            for k in (0, 1, -1):
                inputs = {'variant': 1, 'k': k, 'false_slot': 1}
                with self.subTest(question=qid, factor=k), self.assertRaises(RejectDraw):
                    build_values(cfg, lambda name, spec: inputs[name])

    def test_seed_determinism_and_record_provenance(self):
        for qid in IDS:
            original, cfg = self.setup_question(qid)
            cfg_hash = self.configs.load(qid)[1]
            seen = set()
            for seed in range(1, 101):
                result = generate(original, cfg, seed, [])
                self.assertEqual(result.cand, generate(original, cfg, seed, []).cand)
                self.check_rendered(original, result.cand)
                seen.add(signature(result.cand['stem'], result.cand['options']))
            self.assertGreater(len(seen), 10)
            record = make_record(original, cfg, cfg_hash, 100, 1, result)
            self.assertEqual(record['original_version'], 2)
            self.assertEqual(record['original_hash'], original['hash'])
            self.assertEqual(record['config_ver'], 1)
            self.assertEqual(record['config_hash'], cfg_hash)


if __name__ == '__main__':
    unittest.main()
