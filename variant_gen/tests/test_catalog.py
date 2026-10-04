import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import BankError, OriginalBank, original_hash
from engine import original_record


class CatalogTests(unittest.TestCase):
    def test_all_originals_have_drill_membership_without_changing_content(self):
        bank = OriginalBank(ROOT / 'data/q0_bank.csv')
        groups = Counter()
        for qid in bank.ids():
            original = bank.get(qid)
            meta = original['classification']
            self.assertEqual(meta['activity'], 'DRILL')
            self.assertEqual(meta['indicator'], int(qid.split('-')[1]))
            self.assertEqual(meta['source_level'], int(qid.split('-')[2]))
            self.assertEqual(meta['package_id'], 'drill-1')
            groups[(meta['indicator'], meta['source_level'])] += 1
            self.assertEqual(original['hash'], original_hash(original))
            self.assertEqual(original_record(original)['classification'], meta)
        self.assertEqual(len(groups), 12)
        self.assertEqual(set(groups.values()), {10})
        self.assertEqual(bank.get('pg-16-3-5')['version'], 2)
        catalog = bank.catalog()
        self.assertEqual(len(catalog), 20)
        self.assertEqual(sum(not g['question_ids'] for g in catalog), 8)
        for indicator in range(16, 20):
            self.assertEqual({g['source_level'] for g in catalog if g['indicator'] == indicator}, {1,2,3,4,5})

    def test_custom_bank_unclassified_and_invalid_membership_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bank.csv'
            path.write_bytes((ROOT / 'data/q0_bank.csv').read_bytes())
            self.assertNotIn('classification', OriginalBank(path).get('pg-16-1-1'))
            catalog = Path(tmp) / 'question_catalog.json'
            for ids in (['missing'], ['pg-16-1-1', 'pg-16-1-1']):
                catalog.write_text(json.dumps([dict(activity='DRILL', indicator=16,
                    source_level=1, package_id='drill-16-1', question_ids=ids)]))
                with self.assertRaises(BankError):
                    OriginalBank(path)


if __name__ == '__main__':
    unittest.main()
