"""User-approved corrections become runtime originals; the proposal archive stays immutable."""
import sys
import hashlib
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import OriginalBank,load_workspace_bank
from config_store import ConfigStore,validate_config
from engine import generate,assemble,build_values
from filters import signature,validate_candidate
from lint import reproduce_original
from build_level45_completion import modules

ARCHIVE=ROOT/'drafts/2026-10-20-level45-academic'
APPROVED=ROOT/'data/drill-1-indicators-1-5-levels-4-5-approved'


class ApprovedCorrections(unittest.TestCase):
    def test_250_originals_and_100_level45_generators_in_original_package(self):
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        groups=[g for g in bank.catalog() if g.get('activity')=='DRILL' and g.get('indicator') in range(1,6)]
        self.assertEqual(sum(len(g['question_ids']) for g in groups),250)
        levels=[g for g in groups if g['source_level'] in (4,5)]
        self.assertEqual(len(levels),10)
        for group in levels:
            self.assertEqual(group['package_id'],'drill-1')
            self.assertEqual([bank.get(q)['metadata']['source_number'] for q in group['question_ids']],list(range(1,11)))
            for q in group['question_ids']:
                self.assertEqual(bank.get(q)['metadata']['generation_status'],'ACTIVE')
                self.assertTrue(ConfigStore(ROOT/'configs').versions(q))

    def test_approved_content_and_config_equal_reviewed_proposals(self):
        self.assertTrue((APPROVED/'approval.json').exists())
        archived=OriginalBank(ARCHIVE/'q0_bank.csv')
        active=OriginalBank(APPROVED/'q0_bank.csv')
        self.assertEqual(set(active.ids()),set(archived.ids()))
        self.assertEqual(len(active.ids()),28)
        for qid in active.ids():
            with self.subTest(qid=qid):
                old,new=archived.get(qid),active.get(qid)
                for field in ('stem','options','hash','version','classification'):
                    self.assertEqual(new[field],old[field])
                self.assertEqual(new['version'],2)
                self.assertEqual(old['metadata']['generation_status'],'HOLD_SOURCE')
                self.assertEqual(new['metadata']['generation_status'],'ACTIVE')
                self.assertEqual(new['metadata']['approval_status'],'USER_APPROVED_CORRECTION')
                self.assertFalse(new['metadata']['review_only'])
                self.assertFalse(new['metadata']['self_adjustment_enabled'])
                for field in ('source_text','source_original_explanation','source_original_key'):
                    self.assertEqual(new['metadata'][field],old['metadata'][field])
                self.assertEqual(new['metadata']['original_explanation'].partition('\n')[2],
                                 old['metadata']['original_explanation'].partition('\n')[2])
                self.assertEqual(new['metadata']['reviewed_proposal_explanation_sha256'],
                    hashlib.sha256(old['metadata']['original_explanation'].encode('utf-8')).hexdigest())
                self.assertNotIn('proposed_additional_notes',new['metadata'])
                self.assertNotIn('proposed_key_caption',new['metadata'])
                for field in ('original_explanation','approved_key_caption','additional_notes'):
                    self.assertNotRegex(new['metadata'][field],r'(?i)\b(?:draft|draf|PROPOSED|karantina)\b')
                self.assertEqual((ROOT/'configs'/qid/'v1.json').read_bytes(),(ARCHIVE/'configs'/qid/'v1.json').read_bytes())

    def test_all_28_runtime_configs_reproduce_and_generate_valid_math(self):
        self.assertTrue((APPROVED/'q0_bank.csv').exists())
        bank=OriginalBank(APPROVED/'q0_bank.csv')
        for qid in bank.ids():
            with self.subTest(qid=qid):
                original=bank.get(qid);cfg,_=ConfigStore(ROOT/'configs').load(qid)
                self.assertEqual(validate_config(cfg,original),[])
                self.assertEqual(reproduce_original(original,cfg),([],[]))
                oracle=modules(int(qid.split('-')[1]))[1]
                capacity=set()
                for k in range(25):
                    c=assemble(cfg,build_values(cfg,lambda n,s,k=k:k))
                    oracle.check_math(qid,c)
                    if not validate_candidate(c,original,[]):capacity.add(signature(c['stem'],c['options']))
                self.assertEqual(len(capacity),24)
                made=[]
                for seed in range(1,21):
                    candidate=generate(original,cfg,seed,made).cand
                    oracle.check_math(qid,candidate);made.append(candidate)
                self.assertEqual(len({signature(c['stem'],c['options']) for c in made}),20)


if __name__=='__main__':unittest.main()
