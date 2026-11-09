import math
import unittest
from numora_service.irt.math import probabilities, eap, reference_score, convert


class IrtMathTests(unittest.TestCase):
    def test_2pl_matches_logistic_and_extremes_are_finite(self):
        for theta in [-1000, -2, 0, 2, 1000]:
            p = probabilities(theta, 1.2, [0.4])
            self.assertAlmostEqual(sum(p), 1)
            if abs(theta) < 10:
                self.assertAlmostEqual(p[1], 1/(1+math.exp(-1.2*(theta-0.4))))

    def test_gpcm_unordered_absolute_steps(self):
        p = probabilities(0, 2, [1, -1])
        self.assertAlmostEqual(p[0], p[2])
        self.assertGreater(p[0], p[1])
        steps, se = convert(2, [-2, 0], [[.04, .01, 0], [.01, .09, .02], [0, .02, .16]])
        self.assertEqual(steps, [1, -1])
        # db/da = -0.5, db/dd1 = -0.5: include both cross-covariance terms.
        self.assertAlmostEqual(se[0]**2, .0375)
        self.assertTrue(all(x > 0 for x in se))

    def test_extreme_patterns_have_finite_posteriors_and_scores(self):
        parameters = {str(i): (1.2, [0]) for i in range(30)}
        items = [{'questionVersionId':str(i), 'maxPoints':'2', 'maximumScoreCategory':1} for i in range(30)]
        for category in [0, 1]:
            theta, se = eap([(str(i), category) for i in range(30)], parameters)
            self.assertTrue(math.isfinite(theta) and se > 0)
            score = reference_score(theta, items, parameters)
            self.assertGreater(score, 0)
            self.assertLess(score, 100)
        with self.assertRaises(ValueError): eap([], parameters)


if __name__ == '__main__': unittest.main()
