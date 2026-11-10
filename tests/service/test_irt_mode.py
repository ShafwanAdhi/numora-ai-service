from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from numora_service.irt.mode import purpose,enabled,token
from numora_service.irt.producer import policy


class ModeTests(unittest.TestCase):
    def test_production_is_explicit_and_research_cannot_be_mixed(self):
        with patch.dict('os.environ',{},clear=True):
            self.assertEqual(purpose(),'RESEARCH_ONLY');self.assertFalse(enabled())
            with patch.dict('os.environ',{'NUMORA_IRT_MODE':'PRODUCTION','NUMORA_IRT_PRODUCTION_ENABLED':'true','NUMORA_IRT_TOKEN':'PRIVATE_TEST_ONLY'}):
                self.assertTrue(enabled());self.assertEqual(token(),'PRIVATE_TEST_ONLY')
                with patch.dict('os.environ',{'NUMORA_IRT_RESEARCH_ENABLED':'true'}):self.assertFalse(enabled())
            with patch.dict('os.environ',{'NUMORA_IRT_MODE':'unexpected'}):
                with self.assertRaisesRegex(ValueError,'IRT_MODE_INVALID'):purpose()

    def test_candidate_changes_scope_without_changing_science(self):
        with patch.dict('os.environ',{'NUMORA_IRT_MODE':'PRODUCTION'}):candidate=policy()
        baseline=json.loads((Path(__file__).resolve().parents[2]/'research/irt/policy-v1.json').read_text())
        self.assertFalse(candidate['productionApproved'])
        baseline['version']=candidate['version'];baseline['purpose']='PRODUCTION'
        for key in ['eligibility','scoring']:baseline[key]['purpose']='PRODUCTION'
        self.assertEqual(candidate,baseline)


if __name__=='__main__':unittest.main()
