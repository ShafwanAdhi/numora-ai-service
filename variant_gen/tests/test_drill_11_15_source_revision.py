"""Revised sources stay readable; the unresolved geometry source remains blocked."""
import hashlib
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, load_workspace_bank
from config_store import ConfigError, ConfigStore
from conceptual_stock import load_stock
from engine import generate

IDS = ('mcma-11-1-7', 'pg-11-2-4', 'kategori-11-3-9', 'mcma-15-2-8', 'pg-15-4-2')
FOLDER = ROOT / 'data/drill-1-indicators-11-15'


class SourceRevision1115(unittest.TestCase):
    def test_archive_versions_and_unresolved_source_remains_blocked(self):
        archive = FOLDER / 'source-revision-2026-10-07.docx'
        self.assertTrue(archive.exists())
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         '2ea7ebb8e96b8a210ce0368210cd0539f38e57b96bdfd022dd715438f61ba5c6')
        self.assertEqual(hashlib.sha256((FOLDER / 'source.docx').read_bytes()).hexdigest(),
                         '08b30681b07398eaea08331029f8c6934d576aaa31294a6529fd8ac69dff5383')
        bank, configs = OriginalBank(FOLDER / 'q0_bank.csv'), ConfigStore(ROOT / 'configs')
        self.assertEqual(len(bank.ids()), 250)
        for qid in IDS:
            with self.subTest(question=qid):
                original = bank.get(qid)
                self.assertEqual(original['version'], 2)
                blocked = qid == 'mcma-15-2-8'
                self.assertEqual(configs.versions(qid), [] if blocked else [1])
                self.assertEqual(original['metadata']['generator_status'], 'NOT_IMPLEMENTED' if blocked else 'IMPLEMENTED')
                self.assertTrue(original['metadata']['source_text'])
                self.assertTrue(original['metadata']['original_explanation'])
                self.assertTrue(original['metadata']['reason'])
                if blocked:
                    with self.assertRaises(ConfigError):
                        generate(original, {}, 1, [])
                else:
                    cfg, _ = configs.load(qid)
                    self.assertTrue(generate(original, cfg, 1, []).cand['explanation'])
        workspace = load_workspace_bank(ROOT / 'data/q0_bank.csv')
        stocks = load_stock(ROOT / 'data/conceptual_stock.json', workspace)
        self.assertEqual((len(stocks), sum(map(len, stocks.values()))), (67, 206))
        for qid in IDS:
            self.assertEqual(workspace.get(qid), bank.get(qid))

    def test_function_and_relation_keys(self):
        bank = OriginalBank(FOLDER / 'q0_bank.csv')
        original = bank.get('mcma-11-1-7')
        self.assertIn('f(x) = x² - 3', original['stem'])
        self.assertEqual([o['correct'] for o in original['options']],
                         [2**2 - 3 == 1, 2**2 - 3 == 4, (-3)**2 - 3 == 6, (-3)**2 - 3 == 12])
        original = bank.get('pg-11-2-4')
        answer = 2 * (3 - 1) + 3
        self.assertEqual([o['correct'] for o in original['options']],
                         [int(o['text']) == answer for o in original['options']])
        original = bank.get('kategori-11-3-9')
        a, b = {1, 4, 9}, {-3, -2, -1, 1, 2, 3}
        a_to_b_is_function = all(sum(y*y == x for y in b) == 1 for x in a)
        b_to_a_is_function = all(sum(y*y == x for x in a) == 1 for y in b)
        self.assertEqual([o['correct'] for o in original['options']],
                         [a_to_b_is_function, b_to_a_is_function, not b_to_a_is_function])
        self.assertIn('y² = x', original['options'][0]['text'])

    def test_geometry_issue_is_retained_without_silent_correction(self):
        bank = OriginalBank(FOLDER / 'q0_bank.csv')
        original = bank.get('mcma-15-2-8')
        self.assertIn('∠A = 75°', original['stem'])
        self.assertIn('BC = 9 cm', original['stem'])
        self.assertIn('13,5', original['options'][1]['text'])
        self.assertEqual(original['metadata']['generation_status'], 'HOLD_SOURCE')
        self.assertEqual(original['metadata']['source_review_status'], 'REVISED_NEEDS_REVIEW')
        self.assertIn('9,016', original['metadata']['reason'])
        implied_side = 6 * math.sin(math.radians(75)) / math.sin(math.radians(40))
        self.assertFalse(math.isclose(implied_side, 9, rel_tol=1e-9))
        original = bank.get('pg-15-4-2')
        self.assertIn('terhadap alasan Rani', original['stem'])
        self.assertEqual([o['id'] for o in original['options'] if o['correct']], ['D'])
        acute_b = math.degrees(math.asin(6 * math.sin(math.radians(40)) / 8))
        self.assertGreater(40 + 180 - acute_b, 180)


if __name__ == '__main__':
    unittest.main()
