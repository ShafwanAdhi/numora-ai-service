import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from bank import OriginalBank
from bank import load_workspace_bank

class Drill35(unittest.TestCase):
    def test_cli_stateless_generation_and_hold(self):
        import contextlib,io,tempfile,cli
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            path=Path(tmp)/'variants.jsonl';args=['--store',str(path)]
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                for qid in ['pg-3-1-1', 'mcma-4-1-7', 'kategori-5-1-9']:
                    for command in ['gen','gen','view']:
                        self.assertEqual(cli.main([command,qid,'s11']+args),0)
                self.assertEqual(cli.main(['gen','pg-3-1-3','s1']+args),1)
            self.assertFalse(path.exists())

    def test_workspace_registration_preserves_existing(self):
        default=ROOT/'data/q0_bank.csv'
        prior_paths=[p for p in (ROOT/'data').rglob('q0_bank.csv') if p!=default and 'indicators-3-5' not in str(p)]
        old=load_workspace_bank(default,prior_paths)
        bank=load_workspace_bank(default)
        self.assertEqual(len(bank.ids()),820)
        self.assertEqual(len(bank.catalog()),109)
        for qid in old.ids():self.assertEqual(bank.get(qid),old.get(qid))
        self.assertEqual(len(load_workspace_bank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv').ids()),90)

    def test_source_scope(self):
        import hashlib
        from collections import Counter
        path=ROOT/'data/drill-1-indicators-3-5/q0_bank.csv'
        self.assertTrue(path.exists(),'new source bank missing')
        bank=OriginalBank(path)
        self.assertEqual(len(bank.ids()),90)
        self.assertEqual(len(bank.catalog()),9)
        self.assertEqual({g['indicator'] for g in bank.catalog()},{3,4,5})
        self.assertEqual({g['source_level'] for g in bank.catalog()},{1,2,3})
        self.assertEqual(Counter(bank.get(q)['format'] for q in bank.ids()),{'PG':45,'MCMA':27,'KATEGORI':18})
        self.assertEqual(hashlib.sha256(path.with_name('source.docx').read_bytes()).hexdigest(),
                         'f12c25edf8b1e6a4a10daa19cbbe7459624450f619921186d0c75818e6b499c6')
        for qid in bank.ids():
            o=bank.get(qid)
            self.assertTrue(o['metadata']['source_text'])
            self.assertTrue(o['metadata']['original_explanation'])
            self.assertEqual(o['classification']['package_id'],'drill-1')

    def test_every_source_has_audited_status_and_matching_config(self):
        import json
        from config_store import ConfigStore
        bank=OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv')
        configs=ConfigStore(ROOT/'configs')
        revisions = {r['question_id']:r for r in map(json.loads,
            (ROOT/'data/drill-1-indicators-3-5/original_revisions.jsonl').read_text(encoding='utf8').splitlines())}
        for indicator in [3,4,5]:
            report=ROOT.parent/f'docs/audits/2026-10-06-drill-indicator{indicator}-audit.json'
            self.assertTrue(report.exists(),'indicator audit missing')
            rows=json.loads(report.read_text(encoding='utf8'))['rows']
            self.assertEqual(len(rows),30)
            for row in rows:
                metadata=bank.get(row['question_id'])['metadata']
                if row['question_id'] in revisions:
                    # Compare the historical audit against its original source version.
                    metadata=revisions[row['question_id']]['original_metadata']
                self.assertEqual(metadata['generation_status'],row['status'])
                if row['status']=='ACTIVE':
                    self.assertEqual(configs.versions(row['question_id']),[1])
                    self.assertEqual(row['stock_count'],20)
                else:
                    self.assertTrue(metadata['reason'])
                    self.assertEqual(configs.versions(row['question_id']),[])

if __name__=='__main__':unittest.main()
