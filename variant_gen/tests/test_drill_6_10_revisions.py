"""Curriculum provenance survives subsequent generator activation."""
import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, BankError
from config_store import ConfigStore

FOLDER = ROOT / 'data/drill-1-indicators-6-10'
REVISED = ('pg-6-1-5', 'mcma-6-3-7', 'pg-7-1-2', 'pg-7-1-3', 'pg-7-2-4',
           'pg-7-3-5', 'mcma-8-2-8', 'pg-9-1-3', 'pg-9-1-5', 'pg-9-2-5',
           'pg-9-3-2', 'pg-9-3-4')


class CurriculumRevision(unittest.TestCase):
    def test_ledger_can_correct_a_historical_missing_pg_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            row = dict(id='q', format='PG', cognitive_level='C3', stem='Question',
                       options_json='["A", "B"]', key='', version=1)
            with (folder/'q0_bank.csv').open('w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=row)
                writer.writeheader(); writer.writerow(row)
            replacement = dict(row, key='B', version=2)
            revision = dict(question_id='q', original_version=1, original_row=row,
                            replacement_version=2, replacement_row=replacement,
                            reason='Curriculum supplied the missing key')
            (folder/'original_revisions.jsonl').write_text(json.dumps(revision)+'\n', encoding='utf-8')
            self.assertEqual(OriginalBank(folder/'q0_bank.csv').get('q')['version'], 2)
            revision['original_row'] = dict(row, stem='tampered')
            (folder/'original_revisions.jsonl').write_text(json.dumps(revision)+'\n', encoding='utf-8')
            with self.assertRaises(BankError): OriginalBank(folder/'q0_bank.csv')

    def test_archive_and_revised_originals(self):
        archive = FOLDER/'source-revision-2026-10-07.docx'
        self.assertTrue(archive.exists())
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         'db7bfd87fb1649b4ad63090a32ae225af14ac888fa26b384bb192a4d9cfa3c69')
        bank = OriginalBank(FOLDER/'q0_bank.csv')
        configs = ConfigStore(ROOT/'configs')
        self.assertEqual(len(bank.ids()), 150)
        for qid in REVISED:
            with self.subTest(question=qid):
                original = bank.get(qid)
                self.assertEqual(original['version'], 2)
                held = qid == 'mcma-6-3-7'
                self.assertEqual(original['metadata']['generator_status'], 'NOT_IMPLEMENTED' if held else 'IMPLEMENTED')
                self.assertEqual(configs.versions(qid), [] if held else [1])
                self.assertEqual(original['metadata']['generation_status'], 'HOLD_SOURCE' if held else 'ACTIVE')
        keys = {'pg-6-1-5':'C', 'pg-7-1-2':'B', 'pg-7-1-3':'C', 'pg-7-2-4':'C',
                'pg-7-3-5':'C', 'mcma-8-2-8':'A,B,C,D', 'pg-9-1-3':'C',
                'pg-9-1-5':'A', 'pg-9-2-5':'B', 'pg-9-3-2':'A', 'pg-9-3-4':'A'}
        for qid, key in keys.items():
            self.assertEqual(','.join(o['id'] for o in bank.get(qid)['options'] if o['correct']), key)
        self.assertEqual(bank.get('pg-9-3-2')['cognitive_level'], 'C3')
        self.assertEqual(bank.get('pg-9-3-2')['metadata']['source_number'], 2)
        self.assertEqual(bank.get('mcma-6-3-7')['metadata']['generation_status'], 'HOLD_SOURCE')


if __name__ == '__main__': unittest.main()
