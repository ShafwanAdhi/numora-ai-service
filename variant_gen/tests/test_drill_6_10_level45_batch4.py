"""Twenty-five reviewed source questions, with original provenance preserved."""
import hashlib
import json
import unittest
from unittest.mock import patch
import test_drill_6_10_level45_batch1 as first

ROOT, AUDIT = first.ROOT, first.AUDIT
SELECTION = {6:{4:[9],5:[7,9]},7:{4:[6,10],5:[10]},
             8:{4:[4,6,10],5:[4,6]},9:{4:[3,4,8],5:[3,4,10]},
             10:{4:[1,4,9,10],5:[2,4,7,10]}}
IDS = [f'{"pg" if n < 6 else "mcma" if n < 9 else "kategori"}-{i}-{l}-{n}'
       for i, levels in SELECTION.items() for l, ns in levels.items() for n in ns]
DATA = ROOT/'data/drill-1-indicators-6-10-levels-4-5-batch4'

def check_math(qid,candidate):
    i=int(qid.split('-')[1])
    if i<=7:
        from author_drill_6_7_level45_batch4 import check_math as check
    elif i<=9:
        from author_drill_8_9_level45_batch4 import check_math as check
    else:
        from author_drill_10_level45_batch4 import check_math as check
    check(qid,candidate)

class Batch(first.Batch):
    expected_count=25

    def setUp(self):
        scope=patch.multiple(first,IDS=IDS,SELECTION=SELECTION,DATA=DATA,check_math=check_math)
        scope.start(); self.addCleanup(scope.stop)

    def test_scope_provenance_and_originals(self):
        from build_drill_6_10_level45_batch4 import review_entry
        from build_drill_1_5_level45_batch1 import safe_algebra
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        workspace=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        sources={e['audit_id']:e for e in json.loads(AUDIT.read_text(encoding='utf-8'))['entries']}
        self.assertEqual(set(bank.ids()),set(IDS)); self.assertEqual(len(IDS),25)
        for qid in IDS:
            with self.subTest(qid=qid):
                o=bank.get(qid); m=o['metadata']; e=sources[m['audit_id']]
                raw=e.get('source_projection_resolved') or e['source_projection']
                reviewed=review_entry(e); s=reviewed['source_projection']
                self.assertEqual(o,workspace.get(qid))
                self.assertEqual(o['stem'],safe_algebra(s['stem']))
                self.assertEqual([p['text'] for p in o['options']],[safe_algebra(t) for t in raw['options']])
                self.assertEqual([p['id'] for p in o['options'] if p['correct']],raw['key'])
                self.assertEqual(m['original_explanation'],raw['explanation'])
                self.assertEqual(m['raw_source_projection'],raw)
                self.assertEqual(m['source_review']['findings'],e['issues'])
                self.assertEqual(hashlib.sha256((DATA/m['source_document']).read_bytes()).hexdigest(),m['source_document_sha256'])
                self.assertFalse(m['self_adjustment_enabled'])
                self.assertEqual(m['approval_status'],'NOT_CURRICULUM_APPROVED')
                self.assertEqual(o['classification'],dict(activity='DRILL',package_id='drill-1',indicator=e['indicator'],source_level=e['level']))
                self.assertFalse(o['stem'].startswith('(a)'))

    def test_cumulative_scope_and_reproducible_configs(self):
        from build_drill_6_10_level45_batch1 import entries
        from build_drill_6_10_level45_batch4 import author,review_entry
        prior=set()
        for stage in (1,2,3):
            prior.update(json.loads((ROOT/f'data/drill-1-indicators-6-10-levels-4-5-batch{stage}/question_metadata.json').read_text(encoding='utf-8')))
        self.assertFalse(prior & set(IDS)); self.assertEqual(len(prior | set(IDS)),75)
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        for e in entries():
            if e['source_number'] not in SELECTION.get(e['indicator'],{}).get(e['level'],[]): continue
            a=author(review_entry(e)); cfg,_=first.ConfigStore(ROOT/'configs').load(a.qid)
            self.assertEqual(cfg,a.config(bank.get(a.qid)),a.qid)

    def test_oracle_rejects_wrong_numeric_answers(self):
        from copy import deepcopy
        import re
        bank=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        for qid,index in [('kategori-6-4-9',0),('mcma-6-5-7',1),('pg-8-5-4',0),
                          ('pg-10-4-1',1),('mcma-10-5-7',1)]:
            with self.subTest(qid=qid):
                cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
                c=first.generate(bank.get(qid),cfg,77,[]).cand; bad=deepcopy(c)
                bad['options'][index]['text']=re.sub(r'\d+','999',bad['options'][index]['text'],count=1)
                self.assertNotEqual(c,bad)
                with self.assertRaises(AssertionError): check_math(qid,bad)

    def test_review_never_accepts_uncertain_stimuli_or_wrong_keys(self):
        from build_drill_6_10_level45_batch4 import review_entry
        from build_drill_6_10_level45_batch1 import entries
        for e in entries():
            if e['level'] not in (4,5): continue
            if e['validity']!='VALID' or e['answer_status']!='CORRECT':
                with self.assertRaises(AssertionError): review_entry(e)

    def test_oracle_rejects_false_step_explanations(self):
        from copy import deepcopy
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        for qid in ('pg-10-4-4','pg-10-5-4'):
            cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
            c=first.generate(bank.get(qid),cfg,77,[]).cand
            for text in (c['options'][3]['text'].replace('Langkah 4','Langkah 1'),
                         'Langkah 4 salah karena faktorisasi pembilang tidak benar.'):
                bad=deepcopy(c); bad['options'][3]['text']=text
                with self.assertRaises(AssertionError): check_math(qid,bad)

if __name__=='__main__': unittest.main()
