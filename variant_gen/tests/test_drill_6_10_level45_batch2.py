"""Next twenty audited originals; reuse batch 1's integration contract."""
import unittest
from unittest.mock import patch
import test_drill_6_10_level45_batch1 as first

ROOT, AUDIT = first.ROOT, first.AUDIT
SELECTION = {6: {4: [5, 7]}, 7: {4: [1, 5, 7, 8], 5: [1, 4]},
             8: {4: [2, 3], 5: [1, 7]}, 9: {4: [5, 6, 7], 5: [9]},
             10: {4: [5, 8], 5: [3, 8]}}
IDS = [f'{"pg" if n < 6 else "mcma" if n < 9 else "kategori"}-{i}-{l}-{n}'
       for i, levels in SELECTION.items() for l, ns in levels.items() for n in ns]
DATA = ROOT/'data/drill-1-indicators-6-10-levels-4-5-batch2'

def check_math(qid, candidate):
    i = int(qid.split('-')[1])
    if i <= 7:
        from author_drill_6_7_level45_batch2 import check_math as check
    elif i <= 9:
        from author_drill_8_9_level45_batch2 import check_math as check
    else:
        from author_drill_10_level45_batch2 import check_math as check
    check(qid, candidate)

class Batch(first.Batch):
    def setUp(self):
        self.scope = patch.multiple(first, IDS=IDS, SELECTION=SELECTION, DATA=DATA, check_math=check_math)
        self.scope.start()
        self.addCleanup(self.scope.stop)

    def test_oracle_rejects_wrong_numeric_answers(self):
        from copy import deepcopy
        import re
        bank = first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        for qid, index in [('pg-7-4-1',2), ('mcma-7-4-8',0), ('pg-8-4-3',0),
                           ('mcma-9-4-7',0), ('pg-10-5-3',0), ('mcma-10-5-8',0)]:
            with self.subTest(qid=qid):
                cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
                c=first.generate(bank.get(qid),cfg,77,[]).cand
                bad=deepcopy(c)
                bad['options'][index]['text']=re.sub(r'\d[\d.,]*','999',bad['options'][index]['text'],count=1)
                self.assertNotEqual(c,bad)
                with self.assertRaises(AssertionError): check_math(qid,bad)

    def test_batch_membership_is_disjoint_and_cumulative(self):
        import json
        previous = set(json.loads((ROOT/'data/drill-1-indicators-6-10-levels-4-5-batch1/question_metadata.json').read_text(encoding='utf-8')))
        self.assertFalse(previous & set(IDS))
        self.assertEqual(len(previous | set(IDS)),40)

    def test_configs_match_reproducible_authoring(self):
        from build_drill_6_10_level45_batch1 import entries
        from build_drill_6_10_level45_batch2 import author
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        for e in entries():
            if e['source_number'] not in SELECTION.get(e['indicator'],{}).get(e['level'],[]):
                continue
            a=author(e)
            cfg,_=first.ConfigStore(ROOT/'configs').load(a.qid)
            self.assertEqual(cfg,a.config(bank.get(a.qid)),a.qid)

if __name__ == '__main__': unittest.main()
