"""Curriculum originals imported locally; existing recipes/stocks preserved."""
import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, _parse_row, original_hash
from config_store import ConfigStore, ConfigError
from engine import generate

SHA = 'c2f41c6800e990d6cbc96a07cb83d3abe1bd25e0ebe874f2be5f666beda2a3b1'
FOLDERS = (ROOT/'data/drill-1-indicators-1-2', ROOT/'data/drill-1-indicators-3-5')


class SourceRevisions(unittest.TestCase):
    def test_archives_ledgers_and_unmodified_originals(self):
        configs = ConfigStore(ROOT/'configs')
        for folder, count, expected in zip(FOLDERS, (17,24),
            ({'ACTIVE':50,'DEFERRED_CONCEPTUAL':9,'HOLD_SOURCE':1},
             {'ACTIVE':88,'DEFERRED_CONCEPTUAL':1,'HOLD_SOURCE':1})):
            with self.subTest(bank=folder.name):
                self.assertEqual(hashlib.sha256((folder/'source-revision-2026-10-07.docx').read_bytes()).hexdigest(), SHA)
                ledger = [json.loads(t) for t in (folder/'original_revisions.jsonl').read_text(encoding='utf-8').splitlines()]
                self.assertEqual(len(ledger), count)
                bank = OriginalBank(folder/'q0_bank.csv')
                self.assertEqual(Counter(bank.get(q)['metadata']['generation_status'] for q in bank.ids()), expected)
                self.assertEqual({g['source_level'] for g in bank.catalog()}, {1,2,3})
                revised = {r['question_id'] for r in ledger}
                for entry in ledger:
                    q = entry['question_id']; original = bank.get(q)
                    self.assertEqual(original['version'], 2)
                    self.assertEqual(entry['source_document_sha256'], SHA)
                    self.assertEqual(entry['original_metadata']['generation_status'], 'HOLD_SOURCE')
                    self.assertEqual(original['hash'], _parse_row(entry['replacement_row'], 0)['hash'])
                    held = q == 'pg-1-2-1'
                    self.assertEqual(original['metadata']['generator_status'], 'NOT_IMPLEMENTED' if held else 'IMPLEMENTED')
                    self.assertEqual(configs.versions(q), [] if held else [1])
                    if held:
                        with self.assertRaises(ConfigError): generate(original, {}, 11, [])
                baseline = OriginalBank(folder/'q0_bank.csv')
                # Read the unchanged CSV directly; revised rows exist only in the ledger.
                import csv
                with (folder/'q0_bank.csv').open(encoding='utf-8-sig', newline='') as file:
                    for row in csv.DictReader(file):
                        if row['id'] not in revised:
                            old = _parse_row(row, 0)
                            self.assertEqual(baseline.get(row['id'])['hash'], original_hash(old))

    def test_source_corrections_and_remaining_conflicts(self):
        originals = {q:b.get(q) for b in (OriginalBank(f/'q0_bank.csv') for f in FOLDERS) for q in b.ids()}
        keys = {'pg-1-2-1':'D','pg-1-3-5':'D','mcma-1-2-6':'A,C','mcma-1-3-6':'A,C',
                'pg-2-1-2':'B','pg-2-1-5':'A','pg-2-2-2':'A','pg-2-2-4':'B',
                'mcma-2-2-6':'A,B,D','mcma-2-2-7':'A,B','mcma-2-3-6':'A,B,D',
                'pg-3-1-5':'B','mcma-3-2-8':'B,C','pg-4-1-1':'C','pg-5-1-5':'B'}
        for q, key in keys.items():
            self.assertEqual(','.join(o['id'] for o in originals[q]['options'] if o['correct']), key, q)
        for q in ('pg-1-2-1','pg-5-3-3'):
            self.assertEqual(originals[q]['metadata']['generation_status'], 'HOLD_SOURCE')
            self.assertEqual(originals[q]['metadata']['source_review_status'], 'REVISED_CURRICULUM_PENDING_REVIEW')
        self.assertEqual(originals['pg-5-3-3']['version'], 1)
        self.assertIn('0,58%', originals['pg-1-2-1']['metadata']['original_explanation'])
        self.assertEqual(originals['mcma-3-2-8']['metadata']['cognitive_label_provenance'], 'INHERITED_PREVIOUS_SOURCE')
        self.assertEqual(originals['mcma-1-2-6']['cognitive_level'], 'C4')
        self.assertIn('sisi', originals['pg-3-2-2']['stem'])
        self.assertNotIn('diagonal', originals['pg-3-2-2']['stem'])
        self.assertIn('bilangan bulat', originals['pg-4-2-2']['stem'])


if __name__ == '__main__': unittest.main()
