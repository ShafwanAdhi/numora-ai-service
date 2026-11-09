from copy import deepcopy
import unittest
from numora_service.irt.gates import anchor_gate
from numora_service.irt.producer import policy


class AnchorGateTests(unittest.TestCase):
    def setUp(self):
        self.ids=[str(i) for i in range(5)]
        self.evidence={q:{'evaluated':True,'holmP':1.,'maximumLogSlopeDifference':.1,
                          'maximumStepDifference':.2} for q in self.ids}
        self.quality=policy()['quality']

    def gate(self,evidence=None):
        return anchor_gate(self.evidence if evidence is None else evidence,self.ids,self.quality)

    def test_pinned_thresholds_and_identity(self):
        self.assertTrue(self.gate()['passed'])
        wrong=deepcopy(self.evidence);wrong['other']=wrong.pop('0')
        self.assertFalse(self.gate(wrong)['passed'])
        self.assertFalse(self.gate(wrong)['identityValid'])

    def test_practical_difference_is_not_erased_by_nonsignificance(self):
        self.evidence['0']['maximumStepDifference']=.31
        result=self.gate()
        self.assertFalse(result['passed'])
        self.assertEqual(result['checks']['0']['reasons'],['STEP_DIFFERENCE'])

    def test_missing_nonfinite_or_invalid_statistics_fail_closed(self):
        for key in ['holmP','maximumLogSlopeDifference','maximumStepDifference']:
            for value in [None,float('nan'),float('inf'),-1,True]:
                with self.subTest(key=key,value=value):
                    evidence=deepcopy(self.evidence);evidence['0'][key]=value
                    self.assertFalse(self.gate(evidence)['passed'])

    def test_reference_only_does_not_claim_linking_was_evaluated(self):
        result=anchor_gate({},self.ids,self.quality,False)
        self.assertTrue(result['passed'])
        self.assertEqual(result['scope'],'REFERENCE_ONLY')
