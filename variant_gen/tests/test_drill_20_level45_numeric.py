"""Actual survey data must vary coherently and keep the source's inference valid."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import load_workspace_bank
from config_store import validate_config
from engine import assemble,build_values,generate
from filters import signature,validate_candidate
from lint import reproduce_original


class NumericSurvey(unittest.TestCase):
    def test_every_domain_and_twenty_runtime_variants(self):
        from author_drill_20_level45_numeric import selected,author
        from oracle_drill_20_level45_numeric import check_math
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(len(selected()),6)
        for e in selected():
            with self.subTest(qid=e['question_id']):
                o=bank.get(e['question_id']);cfg=author(e).config(o)
                self.assertEqual(validate_config(cfg,o),[])
                self.assertEqual(reproduce_original(o,cfg),([],[]))
                unique=set()
                for k in range(25):
                    c=assemble(cfg,build_values(cfg,lambda n,s,k=k:k));check_math(o['id'],c)
                    if k:
                        self.assertEqual(validate_candidate(c,o,[]),[])
                        unique.add(signature(c['stem'],c['options']))
                self.assertEqual(len(unique),24)
                made=[]
                for seed in range(1,21):
                    c=generate(o,cfg,seed,made).cand;check_math(o['id'],c);made.append(c)
                self.assertEqual(len({signature(c['stem'],c['options']) for c in made}),20)
                self.assertEqual(generate(o,cfg,201,[]).cand,generate(o,cfg,201,[]).cand)

    def test_oracle_rejects_wrong_claim_key_and_calculation(self):
        from author_drill_20_level45_numeric import selected,author
        from oracle_drill_20_level45_numeric import check_math
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        for e in selected():
            o=bank.get(e['question_id']);cfg=author(e).config(o)
            c=assemble(cfg,build_values(cfg,lambda n,s:11))
            for index in range(len(c['options'])):
                bad=deepcopy(c);bad['options'][index]['correct']=not bad['options'][index]['correct']
                with self.assertRaises(AssertionError):check_math(o['id'],bad)
            bad=deepcopy(c);bad['explanation']='Jumlah responden = 999999.'
            with self.assertRaises(AssertionError):check_math(o['id'],bad)
            import re
            bad=deepcopy(c);bad['stem']=re.sub(r'\d+','999999',c['stem'],count=1)
            with self.assertRaises(AssertionError):check_math(o['id'],bad)
            bad=deepcopy(c)
            index=next(i for i,p in enumerate(c['options']) if p['correct'] and re.search(r'\d',p['text']))
            bad['options'][index]['text']=re.sub(r'\d+(?:\.\d{3})*(?:,\d+)?','999999',bad['options'][index]['text'],count=1)
            with self.assertRaises(AssertionError):check_math(o['id'],bad)


if __name__=='__main__':unittest.main()
