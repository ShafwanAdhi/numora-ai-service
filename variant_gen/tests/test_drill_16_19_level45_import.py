"""Source-only intake: completeness, provenance, quarantine and runtime visibility."""
import json
import sys
import unittest
import threading
import tempfile
from collections import Counter
from pathlib import Path
from urllib.request import urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, load_workspace_bank
from config_store import ConfigStore

DATA = ROOT/'data/drill-1-indicators-16-19-levels-4-5'


class Import(unittest.TestCase):
    def test_complete_and_visible(self):
        self.assertTrue((DATA/'q0_bank.csv').exists(), '80 originals not imported')
        bank = OriginalBank(DATA/'q0_bank.csv')
        workspace = load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(len(bank.ids()), 80)
        self.assertEqual(Counter((o['classification']['indicator'], o['classification']['source_level'])
                                 for o in (bank.get(q) for q in bank.ids())),
                         Counter({(i,l):10 for i in range(16,20) for l in (4,5)}))
        for q in bank.ids():
            o = bank.get(q)
            self.assertEqual(workspace.get(q), o)
            self.assertEqual(o['classification']['package_id'], 'drill-1')
            self.assertTrue(o['metadata']['source_text'])
            self.assertEqual(o['metadata']['generator_status'],
                             'IMPLEMENTED' if ConfigStore(ROOT/'configs').versions(q) else 'FINITE_STOCK')
            self.assertFalse(o['metadata']['self_adjustment_enabled'])
        for i in range(16,20):
            self.assertEqual(sum(q.split('-')[1:2]==[str(i)] for q in workspace.ids()
                                 if not q.startswith('tryout')), 50)

    def test_source_identity_and_audit(self):
        bank = OriginalBank(DATA/'q0_bank.csv')
        report = json.loads((DATA/'audit.json').read_text(encoding='utf8'))
        self.assertEqual(len(report['entries']), 80)
        revisions = {r['question_id']: r for r in map(json.loads,
            (DATA/'original_revisions.jsonl').read_text(encoding='utf8').splitlines())}
        for entry in report['entries']:
            o = bank.get(entry['question_id']); s = entry['source_projection']
            revision = revisions.get(entry['question_id'])
            if revision:
                raw = revision['original_row']
                self.assertEqual(raw['stem'], s['stem'])
                self.assertEqual(json.loads(raw['options_json']), s['options'])
                self.assertEqual(raw['key'].split(','), s['key'])
                self.assertEqual(revision['original_metadata']['generation_status'], 'HOLD_SOURCE')
                self.assertTrue(entry['issues'])
            else:
                self.assertEqual(o['stem'], s['stem'])
                self.assertEqual([x['text'] for x in o['options']], s['options'])
                self.assertEqual([x['id'] for x in o['options'] if x['correct']], s['key'])
                self.assertFalse(entry['issues'])
            self.assertNotEqual(o['metadata']['generation_status'], 'HOLD_SOURCE')
            self.assertTrue(entry['independent_reasoning'])
        self.assertEqual(bank.get('kategori-16-4-10')['metadata']['category_labels'], ['Tabung','Kerucut'])
        for q in ('mcma-16-4-6','pg-16-4-4','kategori-17-4-9','pg-17-5-3','kategori-17-5-10'):
            self.assertEqual(bank.get(q)['version'], 2)

    def test_http_reads_originals_without_generators_or_database(self):
        import webui
        bank = OriginalBank(DATA/'q0_bank.csv')
        with tempfile.TemporaryDirectory() as tmp, patch('database.connection', side_effect=AssertionError('No database')):
            store = Path(tmp)/'unused.jsonl'
            with webui.make_server(0, store=store) as server:
                worker = threading.Thread(target=server.serve_forever, daemon=True)
                worker.start()
                try:
                    base = f'http://127.0.0.1:{server.server_port}'
                    for q in ('pg-16-4-1','kategori-16-4-10','pg-17-5-3','mcma-18-5-8','kategori-19-5-10'):
                        with urlopen(base+'/api/question?id='+q) as response:
                            result = json.load(response)
                        self.assertEqual(result['original']['question_id'], q)
                        versions=ConfigStore(ROOT/'configs').versions(q)
                        self.assertEqual(result['variant_mode'], 'generator' if versions else 'stock')
                        if versions:
                            self.assertIsNone(result['variant'])
                        else:
                            self.assertIsNotNone(result['variant'])
                        self.assertEqual(result['config_versions'], versions)
                finally:
                    server.shutdown(); worker.join(timeout=3)
            self.assertFalse(store.exists())


if __name__ == '__main__':
    unittest.main()
