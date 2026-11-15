import unittest
from numora_service.irt.producer import policy
from tools.run_irt_threshold_study import profiles
class ThresholdStudyTests(unittest.TestCase):
    def test_candidate_grid_does_not_mutate_baseline(self):
        baseline = policy(); candidates = list(profiles(baseline))
        self.assertEqual(len(candidates), 243); self.assertEqual(policy(), baseline)
        self.assertTrue(all(p['purpose'] == 'RESEARCH_ONLY' and not p['productionApproved'] for p in candidates))

    def test_candidate_grid_is_full_research_only_grid(self):
        self.assertEqual(len(list(profiles(policy()))), 243)
if __name__ == '__main__': unittest.main()
