"""Ten additional originals, reusing the established integration contract."""
import json
import unittest
from unittest.mock import patch
import test_drill_6_10_level45_batch1 as first

ROOT, AUDIT = first.ROOT, first.AUDIT
SELECTION = {7: {5: [3]}, 8: {4: [5,7,8], 5: [3,5,9,10]},
             9: {4: [10]}, 10: {5: [5]}}
IDS = [f'{"pg" if n < 6 else "mcma" if n < 9 else "kategori"}-{i}-{l}-{n}'
       for i, levels in SELECTION.items() for l, ns in levels.items() for n in ns]
DATA = ROOT/'data/drill-1-indicators-6-10-levels-4-5-batch3'

def check_math(qid, candidate):
    _,i,l,_ = qid.split('-')
    if i != '8':
        from author_drill_algebra_level45_batch3 import check_math as check
    elif l == '4':
        from author_drill_8_level4_batch3 import check_math as check
    else:
        from author_drill_8_level5_batch3 import check_math as check
    check(qid,candidate)

class Batch(first.Batch):
    expected_count = 10

    def setUp(self):
        scope=patch.multiple(first, IDS=IDS, SELECTION=SELECTION, DATA=DATA, check_math=check_math)
        scope.start(); self.addCleanup(scope.stop)

    def test_batch_membership_and_reproducible_configs(self):
        from build_drill_6_10_level45_batch1 import entries
        from build_drill_6_10_level45_batch3 import author
        prior=set()
        for stage in (1,2):
            prior.update(json.loads((ROOT/f'data/drill-1-indicators-6-10-levels-4-5-batch{stage}/question_metadata.json').read_text(encoding='utf-8')))
        self.assertFalse(prior & set(IDS))
        self.assertEqual(len(prior | set(IDS)),50)
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        for e in entries():
            if e['source_number'] not in SELECTION.get(e['indicator'],{}).get(e['level'],[]): continue
            a=author(e); cfg,_=first.ConfigStore(ROOT/'configs').load(a.qid)
            self.assertEqual(cfg,a.config(bank.get(a.qid)),a.qid)

    def test_oracle_rejects_wrong_numeric_answers(self):
        from copy import deepcopy
        import re
        bank=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        for qid,index in [('pg-7-5-3',3),('mcma-8-4-7',1),('pg-8-5-3',2),
                          ('kategori-8-5-9',0),('kategori-9-4-10',1),('pg-10-5-5',0)]:
            with self.subTest(qid=qid):
                cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
                c=first.generate(bank.get(qid),cfg,77,[]).cand
                bad=deepcopy(c)
                bad['options'][index]['text']=re.sub(r'\d+','999',bad['options'][index]['text'],count=1)
                self.assertNotEqual(c,bad)
                with self.assertRaises(AssertionError): check_math(qid,bad)

if __name__ == '__main__': unittest.main()
