"""Unambiguous key corrections; historical source remains inspectable."""
import json
import unittest
from unittest.mock import patch
import test_drill_6_10_level45_batch1 as first

ROOT=first.ROOT
DATA=ROOT/'data/drill-1-indicators-6-10-levels-4-5-batch5'
SELECTION={6:{4:[1],5:[1,3]},7:{4:[3],5:[5]},9:{5:[2]},10:{4:[7]}}
KEYS={'pg-6-4-1':['D'],'pg-6-5-1':['A'],'pg-6-5-3':['B'],
      'pg-7-4-3':['C'],'pg-7-5-5':['A'],'pg-9-5-2':['D'],'mcma-10-4-7':['A','B','D']}
IDS=list(KEYS)

def check_math(qid,c):
    from author_drill_6_10_level45_batch5 import check_math as check
    check(qid,c)

class Batch(first.Batch):
    expected_count=7

    def setUp(self):
        scope=patch.multiple(first,IDS=IDS,SELECTION=SELECTION,DATA=DATA,check_math=check_math)
        scope.start(); self.addCleanup(scope.stop)

    def test_scope_provenance_and_originals(self):
        from build_drill_6_10_level45_batch1 import entries
        from build_drill_6_10_level45_batch5 import review_entry,author
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        self.assertEqual(set(bank.ids()),set(IDS))
        for e in entries():
            qid=f"{e['format'].lower()}-{e['indicator']}-{e['level']}-{e['source_number']}"
            if qid not in IDS: continue
            o=bank.get(qid); m=o['metadata']; raw=e.get('source_projection_resolved') or e['source_projection']
            self.assertEqual([t['id'] for t in o['options'] if t['correct']],KEYS[qid])
            self.assertEqual(o['stem'],raw['stem'])
            self.assertEqual([t['text'] for t in o['options']],raw['options'])
            self.assertEqual(m['raw_source_projection'],raw)
            self.assertEqual(m['original_explanation'],raw['explanation'])
            self.assertFalse(m['self_adjustment_enabled'])
            self.assertEqual(m['approval_status'],'NOT_CURRICULUM_APPROVED')
            cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
            self.assertEqual(cfg,author(review_entry(e)).config(o))

    def test_oracle_rejects_wrong_numeric_answers(self):
        import re
        from copy import deepcopy
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        for qid in IDS:
            cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
            c=first.generate(bank.get(qid),cfg,77,[]).cand
            bad=deepcopy(c)
            index=next(j for j,o in enumerate(bad['options']) if o['correct'])
            bad['options'][index]['text']=re.sub(r'\d[\d.,]*','999',bad['options'][index]['text'],count=1)
            with self.assertRaises(AssertionError): check_math(qid,bad)
            bad=deepcopy(c); bad['explanation']='$1+1=999$'
            with self.assertRaises(AssertionError): check_math(qid,bad)

if __name__=='__main__': unittest.main()
