import unittest
from research.irt.synthetic import generate
from numora_service.irt_contracts import validate_input


class SyntheticTests(unittest.TestCase):
    def test_designs_are_valid_and_reproducible(self):
        for model in ['2PL','GPCM','MIXED']:
            value,truth=generate(4,model=model)
            validate_input(value)
            self.assertEqual((value,truth),generate(4,model=model))
            self.assertEqual(len(value['responses']),240)
            self.assertEqual(len(truth['theta']),8)
            self.assertEqual(len(set.intersection(*(set(p['questionVersionIds']) for p in value['packages']))),5)

    def test_every_response_belongs_to_delivered_package(self):
        value,_=generate(8)
        packages={p['packageId']:set(p['questionVersionIds']) for p in value['packages']}
        people={p['attemptId']:p for p in value['respondents']}
        for response in value['responses']:
            self.assertIn(response['questionVersionId'],packages[people[response['attemptId']]['packageId']])

    def test_three_arm_design_has_five_common_versions_and_independent_focal_columns(self):
        value,truth=generate(3,arms=3)
        validate_input(value)
        self.assertEqual(len(value['items']),80)
        self.assertEqual(len(value['respondents']),9)
        self.assertEqual(len(truth['theta']),9)


if __name__=='__main__':unittest.main()
