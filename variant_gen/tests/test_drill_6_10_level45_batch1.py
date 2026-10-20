"""First 20 of 100 level 4–5 originals: reproduction, mathematics, ephemeral API."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank, load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from filters import signature, validate_candidate
from lint import reproduce_original

SELECTION = {6: {4: [3, 6], 5: [5, 6]}, 7: {4: [2, 9], 5: [2, 7]},
             8: {4: [1, 9], 5: [2, 8]}, 9: {4: [2, 9], 5: [6, 8]},
             10: {4: [3, 6], 5: [1, 6]}}
IDS = [f'{"pg" if n < 6 else "mcma" if n < 9 else "kategori"}-{i}-{l}-{n}'
       for i, levels in SELECTION.items() for l, ns in levels.items() for n in ns]
DATA = ROOT / 'data/drill-1-indicators-6-10-levels-4-5-batch1'
AUDIT = ROOT.parent / 'docs/audits/2026-10-19-original-question-audit/stage-08-academic-indicators-06-10/audit.json'

def check_math(qid, candidate):
    i = int(qid.split('-')[1])
    if i <= 7:
        from author_drill_6_7_level45_batch1 import check_math as check
    elif i <= 9:
        from author_drill_8_9_level45_batch1 import check_math as check
    else:
        from author_drill_10_level45_batch1 import check_math as check
    check(qid, candidate)

class Batch(unittest.TestCase):
    expected_count = 20
    def test_scope_provenance_and_originals(self):
        self.assertTrue((DATA / 'q0_bank.csv').exists(), '20-question batch missing')
        bank = OriginalBank(DATA / 'q0_bank.csv')
        workspace = load_workspace_bank(ROOT / 'data/q0_bank.csv')
        self.assertEqual(set(bank.ids()), set(IDS))
        self.assertEqual(len(IDS), self.expected_count)
        import hashlib
        sources = {e['audit_id']: e for e in json.loads(AUDIT.read_text(encoding='utf-8'))['entries']}
        from build_drill_1_5_level45_batch1 import safe_algebra
        for qid in IDS:
            with self.subTest(qid=qid):
                o = bank.get(qid)
                self.assertEqual(o, workspace.get(qid))
                m = o['metadata']; e = sources[m['audit_id']]
                s = e.get('source_projection_resolved') or e['source_projection']
                self.assertEqual(o['stem'], safe_algebra(s['stem']))
                self.assertEqual([p['text'] for p in o['options']], [safe_algebra(t) for t in s['options']])
                self.assertEqual([p['id'] for p in o['options'] if p['correct']], s['key'])
                self.assertEqual(m['original_explanation'], s['explanation'])
                self.assertEqual(hashlib.sha256((DATA / m['source_document']).read_bytes()).hexdigest(), m['source_document_sha256'])
                self.assertFalse(m['self_adjustment_enabled'])
                self.assertEqual(m['approval_status'], 'NOT_CURRICULUM_APPROVED')
                self.assertEqual(o['classification'], dict(activity='DRILL', package_id='drill-1', indicator=e['indicator'], source_level=e['level']))

    def test_entire_domain_and_seeded_generation(self):
        from copy import deepcopy
        bank = load_workspace_bank(ROOT / 'data/q0_bank.csv')
        for qid in IDS:
            with self.subTest(qid=qid):
                o = bank.get(qid); cfg, _ = ConfigStore(ROOT / 'configs').load(qid)
                self.assertEqual(validate_config(cfg, o), [])
                self.assertEqual(reproduce_original(o, cfg), ([], []))
                accepted = set()
                spec = cfg['variables']['k']
                for k in range(spec['range'][0], spec['range'][1]+1, spec.get('step', 1)):
                    c = assemble(cfg, build_values(cfg, lambda name, spec: k))
                    check_math(qid, c)
                    if not validate_candidate(c, o, []):
                        accepted.add(signature(c['stem'], c['options']))
                self.assertGreaterEqual(len(accepted), 20)
                prior = []
                for seed in range(20):
                    result = generate(o, cfg, seed, prior)
                    check_math(qid, result.cand)
                    self.assertEqual(validate_candidate(result.cand, o, prior), [])
                    prior.append(result.cand)
                self.assertEqual(generate(o,cfg,77,[]).cand, generate(o,cfg,77,[]).cand)
                bad = deepcopy(prior[0]); bad['options'][0]['correct'] = not bad['options'][0]['correct']
                with self.assertRaises(AssertionError): check_math(qid, bad)

    def test_workbench_without_persistence(self):
        # Reuse the existing HTTP contract check with this batch's scope and oracle.
        from unittest.mock import patch
        import test_drill_1_5_level45_batch1 as previous
        import drill_1_5_level45_math as maths
        with patch.object(previous, 'IDS', IDS), patch.object(previous, 'SELECTION', SELECTION), patch.object(maths, 'check_math', check_math):
            previous.Batch1().test_workbench_catalog_originals_and_generation_without_writes()

    def test_oracle_rejects_wrong_numeric_answers(self):
        from copy import deepcopy
        import re
        bank = load_workspace_bank(ROOT/'data/q0_bank.csv')
        for qid, index in [('pg-6-4-3',0), ('pg-7-4-2',1), ('pg-9-4-2',1),
                           ('mcma-9-5-6',0), ('pg-10-4-3',0), ('mcma-10-4-6',1)]:
            with self.subTest(qid=qid):
                cfg,_=ConfigStore(ROOT/'configs').load(qid)
                c=generate(bank.get(qid),cfg,77,[]).cand
                bad=deepcopy(c)
                bad['options'][index]['text']=re.sub(r'\d[\d.,]*','999',bad['options'][index]['text'],count=1)
                self.assertNotEqual(c,bad)
                with self.assertRaises(AssertionError): check_math(qid,bad)

    def test_service_catalog_and_custom_bank(self):
        from numora_service.bridge import catalog
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        items={r['questionExternalId']:r for r in catalog(bank,ConfigStore(ROOT/'configs'))}
        for qid in IDS:
            self.assertEqual(items[qid]['mode'],'generator')
            self.assertEqual(items[qid]['classification']['package_id'],'drill-1')
        self.assertEqual(set(load_workspace_bank(DATA/'q0_bank.csv').ids()),set(IDS))

if __name__ == '__main__':
    unittest.main()
