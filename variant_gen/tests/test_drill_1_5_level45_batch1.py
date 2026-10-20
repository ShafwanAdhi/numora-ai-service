"""Approved 33-original batch; source reproduction and independent mathematics."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bank import load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from filters import signature, validate_candidate
from lint import reproduce_original

SELECTION = {1: {4: [2, 3, 6, 9], 5: [1, 6, 9]},
             2: {4: [4, 6, 8], 5: [1, 2, 6, 8]},
             3: {4: [1, 2, 6, 9], 5: [1, 6, 9]},
             4: {4: [1, 6, 9], 5: [1, 6, 10]},
             5: {4: [1, 6, 9], 5: [1, 6, 9]}}
IDS = [f'{"pg" if n < 6 else "mcma" if n < 9 else "kategori"}-{i}-{l}-{n}'
       for i, levels in SELECTION.items() for l, numbers in levels.items() for n in numbers]
DATA = ROOT / 'data/drill-1-indicators-1-5-levels-4-5-batch1'


class Batch1(unittest.TestCase):
    def bank(self):
        self.assertTrue((DATA / 'q0_bank.csv').exists(), '33-original batch has not been implemented')
        return load_workspace_bank(ROOT / 'data/q0_bank.csv')

    def test_exact_scope_and_package(self):
        bank = self.bank()
        metadata = json.loads((DATA / 'question_metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(set(IDS), set(metadata))
        self.assertEqual(len(IDS), 33)
        for qid in IDS:
            with self.subTest(qid=qid):
                o = bank.get(qid)
                _, i, l, n = qid.split('-')
                self.assertEqual(o['classification'], dict(activity='DRILL', package_id='drill-1',
                                                           indicator=int(i), source_level=int(l)))
                self.assertEqual(o['metadata']['source_number'], int(n))
                self.assertEqual(o['metadata']['approval_status'], 'NOT_CURRICULUM_APPROVED')

    def test_original_content_and_provenance_are_preserved(self):
        import hashlib
        import re
        bank = self.bank()
        matching = ROOT.parent / 'docs/audits/2026-10-19-original-question-audit/stage-06-matching-indicators-01-05/matching.json'
        sources = {e['audit_id']: e for e in json.loads(matching.read_text(encoding='utf-8'))['entries']}
        for qid in IDS:
            with self.subTest(qid=qid):
                o = bank.get(qid)
                source = sources[o['metadata']['audit_id']]['source_projection']
                display = lambda s: re.sub(r'\\+frac\{a\}\{b\}', '(a)/(b)', s)
                self.assertEqual(o['stem'], display(source['stem']))
                self.assertEqual([p['text'] for p in o['options']], [display(t) for t in source['options']])
                self.assertEqual([p['id'] for p in o['options'] if p['correct']], source['key'])
                self.assertEqual(o['metadata']['original_explanation'], source['explanation'])
                self.assertEqual(o['metadata']['source_additional_notes'], source['additional_notes'])
                self.assertEqual(o['metadata']['source_key_caption'], source['key_caption'])
                docx = (DATA / o['metadata']['source_document']).resolve()
                self.assertTrue(docx.is_file())
                self.assertEqual(hashlib.sha256(docx.read_bytes()).hexdigest(),
                                 o['metadata']['source_document_sha256'])

    def test_oracle_rejects_stale_operands_and_wrong_ratio_reason(self):
        from copy import deepcopy
        from drill_1_5_level45_math import check_math
        bank = self.bank()
        for qid in ['pg-4-5-1', 'mcma-4-5-6', 'mcma-5-4-6', 'mcma-5-5-6']:
            with self.subTest(qid=qid):
                cfg, _ = ConfigStore(ROOT/'configs').load(qid)
                c = assemble(cfg, build_values(cfg, lambda name, spec: 2))
                check_math(qid, c)
                bad = deepcopy(c)
                if qid == 'pg-4-5-1':
                    import re
                    bad['stem'] = re.sub(r'KPK\([^)]+\)', 'KPK(10,15,20)', bad['stem'])
                elif qid == 'mcma-4-5-6':
                    import re
                    bad['options'][3]['text'] = re.sub(r'KPK\([^)]+\)', 'KPK(54,72,90)', bad['options'][3]['text'])
                else:
                    bad['explanation'] = bad['explanation'].replace(
                        'kedua suku ganjil dan selisihnya 2, sehingga FPB keduanya 1',
                        'pembilang ganjil sehingga pasti sudah sederhana')
                self.assertNotEqual(bad, c)
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)

    def test_reproduction_and_twenty_independently_valid_unique_variants(self):
        bank = self.bank()
        from drill_1_5_level45_math import check_math
        for qid in IDS:
            with self.subTest(qid=qid):
                o = bank.get(qid)
                cfg, _ = ConfigStore(ROOT / 'configs').load(qid)
                self.assertEqual(validate_config(cfg, o), [])
                self.assertEqual(reproduce_original(o, cfg), ([], []))
                check_math(qid, assemble(cfg, build_values(cfg, lambda name, spec: cfg['original_values'][name])))
                made = []
                for seed in range(1, 21):
                    r = generate(o, cfg, seed, made)
                    check_math(qid, r.cand)
                    self.assertEqual(validate_candidate(r.cand, o, made), [])
                    made.append(r.cand)
                self.assertEqual(len({signature(c['stem'], c['options']) for c in made}), 20)
                self.assertEqual(generate(o, cfg, 201, []).cand, generate(o, cfg, 201, []).cand)
                for seed in range(202, 212):
                    check_math(qid, generate(o, cfg, seed, []).cand)

    def test_oracle_rejects_corrupt_key_and_explanation(self):
        from copy import deepcopy
        bank = self.bank()
        from drill_1_5_level45_math import check_math
        for qid in IDS:
            o = bank.get(qid)
            cfg, _ = ConfigStore(ROOT / 'configs').load(qid)
            c = generate(o, cfg, 222, []).cand
            with self.subTest(qid=qid):
                bad = deepcopy(c)
                bad['options'][0]['correct'] = not bad['options'][0]['correct']
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)
                bad = deepcopy(c)
                bad['explanation'] = 'Pembahasan: 1 + 1 = 999.'
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)

    def test_oracle_rejects_incorrect_numeric_claims(self):
        from copy import deepcopy
        import re
        from drill_1_5_level45_math import check_math
        bank = self.bank()
        mutations = {
            'pg-1-4-3': (0, lambda t: re.sub(r'\d+', '999', t, count=1)),
            'mcma-2-4-6': (0, lambda t: re.sub(r'\\sqrt\{48\}', r'\\sqrt{49}', t)),
            'mcma-2-4-8': (2, lambda t: re.sub(r'Rp[\d.,]+', 'Rp999', t)),
            'pg-3-4-2': (2, lambda t: re.sub(r'\d+(?:,\d+)?', '999', t, count=1)),
            'kategori-3-4-9': (2, lambda t: re.sub(r'\d+(?:,\d+)?', '999', t)),
            'mcma-4-4-6': (3, lambda t: re.sub(r'\d[\d.]*', '999', t)),
            'mcma-5-4-6': (0, lambda t: re.sub(r'\d+:\d+', '997:2', t)),
            'kategori-5-5-9': (0, lambda t: re.sub(r'Rp[\d.,]+', 'Rp999', t)),
        }
        for qid, (index, mutate) in mutations.items():
            with self.subTest(qid=qid):
                cfg, _ = ConfigStore(ROOT / 'configs').load(qid)
                c = generate(bank.get(qid), cfg, 333, []).cand
                check_math(qid, c)
                bad = deepcopy(c)
                bad['options'][index]['text'] = mutate(bad['options'][index]['text'])
                self.assertNotEqual(bad, c)
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)

    def test_entire_finite_domain_is_mathematically_valid(self):
        from drill_1_5_level45_math import check_math
        from expr import RejectDraw
        bank = self.bank()
        for qid in IDS:
            with self.subTest(qid=qid):
                o = bank.get(qid)
                cfg, _ = ConfigStore(ROOT / 'configs').load(qid)
                spec = cfg['variables']['k']
                inputs = (spec['values'] if spec['gen'] == 'choice' else
                          range(spec['range'][0], spec['range'][1]+1, spec.get('step', 1)))
                unique = set()
                for k in inputs:
                    try:
                        values = build_values(cfg, lambda name, spec: k)
                    except RejectDraw:
                        continue
                    c = assemble(cfg, values)
                    check_math(qid, c)
                    if not validate_candidate(c, o, []):
                        unique.add(signature(c['stem'], c['options']))
                self.assertGreaterEqual(len(unique), 20)

    def test_workbench_catalog_originals_and_generation_without_writes(self):
        import http.client
        import tempfile
        import threading
        from unittest.mock import patch
        import webui
        from drill_1_5_level45_math import check_math
        with tempfile.TemporaryDirectory() as tmp, patch('database.connection', side_effect=AssertionError('No DB')):
            store = Path(tmp) / 'unused.jsonl'
            server = webui.make_server(0, store=store)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            def request(method, path, payload=None):
                conn = http.client.HTTPConnection(*server.server_address, timeout=10)
                conn.request(method, path, json.dumps(payload) if payload else None,
                             {'Content-Type': 'application/json'})
                r = conn.getresponse()
                data = json.loads(r.read())
                conn.close()
                self.assertEqual(r.status, 200, data)
                return data
            try:
                groups = request('GET', '/api/catalog')
                members = [qid for g in groups if g.get('package_id') == 'drill-1' and
                           g.get('indicator') in SELECTION and g.get('source_level') in (4,5)
                           for qid in g['question_ids']]
                self.assertTrue(set(IDS) <= set(members))
                for qid in IDS:
                    with self.subTest(qid=qid):
                        envelope = request('GET', f'/api/question?id={qid}&seed=1')
                        original = envelope['original']
                        result = request('POST', '/api/generate', {'question_id': qid, 'seed': 777})
                        self.assertEqual(original['question_id'], qid)
                        self.assertEqual(result['classification']['package_id'], 'drill-1')
                        self.assertEqual(result['metadata']['approval_status'], 'NOT_CURRICULUM_APPROVED')
                        correct = result['key'].split(',')
                        c = dict(stem=result['stem'], explanation=result['explanation'],
                                 options=[dict(o, correct=o['id'] in correct) for o in result['options']])
                        check_math(qid, c)
            finally:
                server.shutdown(); thread.join(); server.server_close()
            self.assertFalse(store.exists())


if __name__ == '__main__':
    unittest.main()
