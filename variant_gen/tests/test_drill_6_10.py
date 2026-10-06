"""Drill 6–10 source fidelity and generator checks; writes use temporary stores."""
import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import BankError, OriginalBank, load_workspace_bank
from config_store import ConfigError, ConfigStore, validate_config
from engine import GenerationError, assemble, build_values, generate, original_record
from lint import reproduce_original

BANK = ROOT / 'data/drill-1-indicators-6-10/q0_bank.csv'
HOLD = ['pg-6-1-5', 'pg-7-1-2', 'pg-7-1-3', 'pg-7-2-4', 'pg-7-3-5',
        'pg-9-1-3', 'mcma-8-2-8', 'mcma-6-3-7', 'pg-9-3-2']


class DrillSource(unittest.TestCase):
    def test_workspace_registration(self):
        paths = [ROOT / 'data/q0_bank.csv', ROOT / 'data/tryout-1/q0_bank.csv',
                 ROOT / 'data/drill-1-indicators-1-2/q0_bank.csv',
                 ROOT / 'data/drill-1-indicators-3-5/q0_bank.csv',
                 ROOT / 'data/drill-1-indicators-20-23/q0_bank.csv',
                 ROOT / 'data/drill-1-indicators-11-15/q0_bank.csv', BANK]
        workspace = load_workspace_bank(paths[0])
        expected = {}
        for path in paths:
            bank = OriginalBank(path)
            for qid in bank.ids():
                self.assertNotIn(qid, expected)
                expected[qid] = bank.get(qid)
        self.assertEqual(set(workspace.ids()), set(expected))
        for qid, original in expected.items():
            self.assertEqual(workspace.get(qid), original)
        self.assertEqual(len(load_workspace_bank(BANK).ids()), 150)
        with self.assertRaises(BankError):
            load_workspace_bank(BANK, [BANK])

    def test_revised_key_display(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from cli import show
        output = StringIO()
        with redirect_stdout(output):
            show(original_record(OriginalBank(BANK).get('pg-6-1-5')), False)
        self.assertEqual(original_record(OriginalBank(BANK).get('pg-6-1-5'))['key'], 'C')
        self.assertIn("record.key || 'Belum tersedia'", (ROOT / 'webui.html').read_text(encoding='utf8'))

    def test_source_identity_and_catalog(self):
        self.assertTrue(BANK.exists(), 'new source bank is missing')
        bank = OriginalBank(BANK)
        self.assertEqual(len(bank.ids()), 150)
        self.assertEqual(Counter(bank.get(q)['format'] for q in bank.ids()),
                         dict(PG=75, MCMA=45, KATEGORI=30))
        self.assertEqual(Counter(bank.get(q)['cognitive_level'] for q in bank.ids()),
                         {'C3': 77, 'C4': 73})
        self.assertEqual(len(bank.catalog()), 25)
        self.assertEqual(sum(not g['question_ids'] for g in bank.catalog()), 10)
        self.assertEqual(hashlib.sha256(BANK.with_name('source.docx').read_bytes()).hexdigest(),
                         'f736431733803c68f7de09d53285cd80ec6be6d63b56459664489f4d49d954c2')
        for qid in bank.ids():
            o = bank.get(qid)
            self.assertEqual(o['classification']['package_id'], 'drill-1')
            self.assertTrue(o['metadata']['source_text'])
            self.assertTrue(o['metadata']['original_explanation'])
        self.assertEqual(bank.get('pg-9-3-2')['metadata']['source_number'], 2)
        self.assertEqual(bank.get('pg-6-2-1')['metadata']['source_number'], 1)

    def test_missing_key_is_hold_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'q0_bank.csv'
            path.write_text('id,format,cognitive_level,stem,options_json,key,version\n'
                            'test,PG,C3,Question,"[""A"",""B""]",,1\n', encoding='utf8')
            for item in [None, {'generation_status': 'ACTIVE'},
                         {'generation_status': 'HOLD_SOURCE'},
                         {'generation_status': 'DEFERRED_CONCEPTUAL', 'reason': 'fixed'}]:
                metadata = path.with_name('question_metadata.json')
                if item is not None:
                    metadata.write_text(json.dumps({'test': item}), encoding='utf8')
                with self.assertRaises(BankError):
                    OriginalBank(path)
            metadata.write_text(json.dumps({'test': {'generation_status': 'HOLD_SOURCE',
                                                    'reason': 'key missing'}}), encoding='utf8')
            held = OriginalBank(path).get('test')
            self.assertFalse(any(o['correct'] for o in held['options']))
            self.assertEqual(original_record(held)['key'], '')
            self.assertTrue(validate_config({}, held))
            with self.assertRaises(ConfigError):
                generate(held, {}, 1, [])

    def test_source_conflicts(self):
        self.assertTrue(BANK.exists(), 'new source bank is missing')
        bank = OriginalBank(BANK)
        for qid in HOLD:
            original = bank.get(qid)
            expected = 'HOLD_SOURCE' if qid == 'mcma-6-3-7' else 'ACTIVE'
            self.assertEqual(original['metadata']['generation_status'], expected, qid)
            if expected == 'HOLD_SOURCE': self.assertTrue(original['metadata']['reason'])
            self.assertEqual(ConfigStore(ROOT / 'configs').versions(qid), [] if expected == 'HOLD_SOURCE' else [1])
        for qid, key in [('pg-6-1-5', 'C'), ('pg-7-1-2', 'B')]:
            self.assertEqual(original_record(bank.get(qid))['key'], key)
        for qid in ['pg-7-3-5', 'pg-9-1-3']:
            o = bank.get(qid)['options']
            self.assertEqual(len({option['text'] for option in o}), 4)
        self.assertIn('(x-2)^2', bank.get('kategori-10-3-9')['stem'])


class DrillGenerators(unittest.TestCase):
    def test_explanations_render_internal_parameter(self):
        import re
        bank = OriginalBank(BANK)
        configs = ConfigStore(ROOT/'configs')
        for qid in ['kategori-7-3-10', 'mcma-7-3-8', 'mcma-8-3-6', 'mcma-8-3-7']:
            cfg, _ = configs.load(qid)
            result = generate(bank.get(qid), cfg, 201, [])
            self.assertIsNone(re.search(r'\bk\b', result.cand['explanation']), qid)

    def test_cli_stateless_generation_and_hold(self):
        import contextlib,io,tempfile,cli
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            path=Path(tmp)/'variants.jsonl';args=['--store',str(path)]
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                for qid in ['pg-6-1-1', 'mcma-8-1-6', 'kategori-10-1-9']:
                    for command in ['gen','gen','view']:
                        self.assertEqual(cli.main([command,qid,'s11']+args),0)
                self.assertEqual(cli.main(['gen','mcma-6-3-7','s1']+args),1)
            self.assertFalse(path.exists())

    def test_oracle_edges(self):
        from drill_6_10_math import poly, substitute, system, inequality, contains
        self.assertEqual(substitute(poly('x^2'), x=1), substitute(poly('x'), x=1))
        self.assertNotEqual(poly('x^2'), poly('x'))
        self.assertEqual(system((0, 0, 0), (0, 0, 0)), 'ALL')
        self.assertEqual(system((0, 0, 1), (0, 0, 0)), 'EMPTY')
        self.assertEqual(system((0, 2, 6), (3, 0, 12)), (4, 3))
        self.assertEqual(inequality('0x<0'), ('EMPTY', None))
        self.assertEqual(inequality('0x≤0'), ('ALL', None))
        self.assertEqual(inequality('7-3x≤-5'), ('≥', 4))
        self.assertTrue(contains(inequality('x≤4'), 4))
        self.assertFalse(contains(inequality('x<4'), 4))

    def check_indicator(self, indicator):
        bank = OriginalBank(BANK)
        active = [bank.get(q) for q in bank.ids() if bank.get(q)['classification']['indicator'] == indicator
                  and bank.get(q)['metadata']['generation_status'] == 'ACTIVE']
        self.assertTrue(active)
        configs = ConfigStore(ROOT / 'configs')
        for original in active:
            qid = original['id']
            with self.subTest(qid=qid):
                self.assertTrue(configs.versions(qid), 'ACTIVE question needs a recipe: ' + qid)
                cfg, _ = configs.load(qid)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                from drill_6_10_math import check_math
                original_values = build_values(cfg, lambda n, s: cfg['original_values'][n])
                from engine import Result
                check_math(self, original, Result(original_values, assemble(cfg, original_values), 0, Counter()))
                made = []
                for seed in range(1, 201):
                    try:
                        result = generate(original, cfg, seed, made)
                    except GenerationError:
                        continue
                    check_math(self, original, result)
                    made.append(result.cand)
                    if len(made) == 20:
                        break
                self.assertEqual(len(made), 20, qid)

    def test_indicator_6_math(self):
        self.check_indicator(6)

    def test_indicator_7_math(self):
        self.check_indicator(7)

    def test_indicator_8_math(self):
        self.check_indicator(8)

    def test_indicator_9_math(self):
        self.check_indicator(9)

    def test_indicator_10_math(self):
        self.check_indicator(10)


if __name__ == '__main__':
    unittest.main()
