from copy import deepcopy
import json
import math
from pathlib import Path
import unittest

from numora_service.irt.anchor_uncertainty import cholesky, evaluate, intervals, transformed_contrasts

ROOT = Path(__file__).resolve().parents[2]
POLICY = json.loads((ROOT / 'research/irt/anchor-v2/policy.json').read_text())


def block(shift=0., error=.01):
    return {'converged': True, 'atParameterBoundary': False,
            'values': [1., 0., 1., -shift],
            'covariance': [[error ** 2 if i == j else 0. for j in range(4)] for i in range(4)],
            'mapping': {'original': {'a': 0, 'intercepts': [1]}, 'variant': {'a': 2, 'intercepts': [3]}}}


def scientific(shift=0., error=.01):
    b = block(shift, error)
    return {'converged': True, 'atParameterBoundary': False,
            'joint': {'covariance': b['covariance']}, 'released': {str(i): deepcopy(b) for i in range(5)}}


class AnchorUncertaintyTests(unittest.TestCase):
    def test_full_jacobian_matches_finite_difference_with_unordered_steps(self):
        values = [1.3, -.4, .6, .9, -.7, .8]
        mapping = {'a': {'a': 0, 'intercepts': [1, 2]}, 'b': {'a': 3, 'intercepts': [4, 5]}}
        rows, jacobian = transformed_contrasts(values, mapping, 'a', ['b'])
        for j in range(len(values)):
            plus, minus = values.copy(), values.copy()
            plus[j] += 1e-6
            minus[j] -= 1e-6
            upper, _ = transformed_contrasts(plus, mapping, 'a', ['b'])
            lower, _ = transformed_contrasts(minus, mapping, 'a', ['b'])
            for k in range(len(rows)):
                self.assertAlmostEqual(jacobian[k][j], (upper[k]['estimate'] - lower[k]['estimate']) / 2e-6, places=8)

    def test_cross_arm_covariance_changes_uncertainty(self):
        first = block()
        second = deepcopy(first)
        second['covariance'][1][3] = second['covariance'][3][1] = .00008
        a = intervals(first, 'original', ['variant'], POLICY, 0)
        b = intervals(second, 'original', ['variant'], POLICY, 0)
        self.assertAlmostEqual(a['contrasts'][1]['standardError'] ** 2, .0002)
        self.assertAlmostEqual(b['contrasts'][1]['standardError'] ** 2, .00004)

    def test_equivalence_material_and_uncertain_are_distinct_and_deterministic(self):
        for shift, error, decision in [(0., .01, 'EQUIVALENT'), (.8, .01, 'MATERIAL_DIFFERENCE'), (.3, .01, 'INSUFFICIENT'), (0., .2, 'INSUFFICIENT')]:
            evidence = scientific(shift, error)
            result = evaluate(evidence, [str(i) for i in range(5)], 'original', ['variant'], POLICY)
            self.assertEqual(result['decision'], decision)
            self.assertEqual(result['passed'], decision == 'EQUIVALENT')
            self.assertEqual(result, evaluate(evidence, [str(i) for i in range(5)], 'original', ['variant'], POLICY))
            self.assertAlmostEqual(result['checks']['0']['blockLevel'], .998)

    def test_missing_anchor_wrong_identity_and_release_diagnostics_fail_closed(self):
        for mutation in ['missing', 'wrong', 'covariance', 'boundary', 'convergence', 'mapping']:
            s = scientific()
            if mutation == 'missing': del s['released']['0']
            if mutation == 'wrong': s['released']['other'] = s['released'].pop('0')
            if mutation == 'covariance': del s['released']['0']['covariance']
            if mutation == 'boundary': s['released']['0']['atParameterBoundary'] = True
            if mutation == 'convergence': s['released']['0']['converged'] = False
            if mutation == 'mapping': s['released']['0']['mapping']['variant']['a'] = -1
            result = evaluate(s, [str(i) for i in range(5)], 'original', ['variant'], POLICY)
            self.assertFalse(result['passed'])
            self.assertEqual(result['decision'], 'NOT_EVALUATED')

    def test_covariance_failures_never_supply_guessed_uncertainty(self):
        for matrix in [[[1, 1], [1, 1]], [[1, 2], [2, 1]], [[1, .1], [0, 1]], [[1, 0], [0, math.nan]], [[1], [0, 1]]]:
            with self.assertRaises(ValueError): cholesky(matrix)
        s = scientific()
        s['joint']['covariance'] = [[0.]]
        self.assertFalse(evaluate(s, [str(i) for i in range(5)], 'original', ['variant'], POLICY)['passed'])

    def test_shared_constraint_derivatives_cancel_instead_of_inventing_independence(self):
        rows, jacobian = transformed_contrasts([1., .2, .3],
            {'a': {'a': 0, 'intercepts': [1]}, 'b': {'a': 0, 'intercepts': [2]}}, 'a', ['b'])
        self.assertEqual(rows[0]['estimate'], 0.)
        self.assertEqual(jacobian[0], [0., 0., 0.])
        self.assertAlmostEqual(jacobian[1][0], .1)


if __name__ == '__main__': unittest.main()
