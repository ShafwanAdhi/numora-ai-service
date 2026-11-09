from copy import deepcopy
import json
from pathlib import Path
import unittest
from numora_service.irt.producer import run


class IrtProducerTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[2]/'contracts/irt-calibration-v1'
        self.value=json.loads((root/'examples/tryout-input.json').read_text())
        self.value['comparisons']=[]
        self.dispatch=json.loads((root/'dispatch.fixture.json').read_text())

    def test_insufficient_data_is_complete_scientific_success_without_engine(self):
        result,_=run(self.value,self.dispatch,lambda _:self.fail('Should not fit insufficient data'))
        self.assertEqual(result['executionStatus'],'SUCCEEDED')
        self.assertEqual(result['outcome']['measurementState'],'INSUFFICIENT')
        self.assertEqual(len(result['outcome']['respondents']),len(self.value['respondents']))
        self.assertTrue(all(p['score'] is None for p in result['outcome']['respondents']))

    def test_unsupported_comparisons_are_not_fabricated_as_insufficient(self):
        self.value['comparisons']=[{'comparisonId':'10000000-0000-4000-8000-000000009999',
            'originalQuestionVersionId':self.value['packages'][0]['questionVersionIds'][-1],
            'variantQuestionVersionId':self.value['packages'][1]['questionVersionIds'][-1]}]
        # Use the existing valid fixture comparison lineage.
        root=Path(__file__).resolve().parents[2]/'contracts/irt-calibration-v1'
        self.value=json.loads((root/'examples/tryout-input.json').read_text())
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_CONTRACT'):
            run(self.value,self.dispatch,lambda _:None)

    def test_unreviewed_profile_cannot_silently_lower_thresholds(self):
        from numora_service.irt.producer import policy
        profile=deepcopy(policy());profile['quality']['minimumArmCount']=1
        with self.assertRaisesRegex(ValueError,'POLICY_UNAVAILABLE'):
            run(self.value,self.dispatch,lambda _:None,profile)

    def test_valid_zero_and_omitted_answers_are_not_unscorable(self):
        for response in self.value['responses']:
            response.update(responseState='OMITTED',scoreCategory=0,awardedPoints='0.00')
        result,_=run(self.value,self.dispatch,lambda _:self.fail('Insufficient categories'))
        self.assertTrue(all(p['status']=='INSUFFICIENT' for p in result['outcome']['respondents']))

    def test_no_presented_observations_is_unscorable_with_null_score(self):
        for response in self.value['responses']:
            response.update(responseState='NOT_PRESENTED',scoreCategory=None,awardedPoints=None,
                includedInCalibration=False,eligibilityReasons=['NOT_PRESENTED'])
        result,_=run(self.value,self.dispatch,lambda _:self.fail('No data'))
        self.assertTrue(all(p['status']=='UNSCORABLE' and p['score'] is None for p in result['outcome']['respondents']))


if __name__=='__main__':unittest.main()
