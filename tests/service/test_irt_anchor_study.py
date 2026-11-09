from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from research.irt.anchor_study import bootstrap_work, design, digest, read, summarize, wilson
from tools.study_irt_anchors import checkpoint, locked
from tests.service.test_irt_anchor_uncertainty import block


class AnchorStudyTests(unittest.TestCase):
    def test_preregistered_design_retains_five_anchors_and_structural_na(self):
        scenario = read('study.json')['scenarios'][3]
        work, truth = design(scenario, 31003000)
        self.assertEqual(sorted(truth['counts'].values()), [500, 2000])
        self.assertEqual(len(work['anchors']), 5)
        self.assertTrue(all(sum(x is not None for x in row) == 30 for row in work['matrix']))
        self.assertEqual(digest(work), digest(design(scenario, 31003000)[0]))

    def test_injected_dif_changes_only_target_arm_anchors_and_not_original(self):
        s = read('study.json')['scenarios'][4]
        work, truth = design(s, 31004000)
        arm1, arm2 = work['groupOrder']
        qid = work['anchors'][0]
        a, steps = truth['parametersByArm'][arm1][qid]
        b, target = truth['parametersByArm'][arm2][qid]
        self.assertEqual(a, b)
        for x, y in zip(steps, target): self.assertAlmostEqual(y - x, .6)
        clean = deepcopy(s); clean['stepShifts'] = []
        baseline, _ = design(clean, 31004000)
        original = [row for row, arm in zip(work['matrix'], work['groups']) if arm == arm1]
        self.assertEqual(original, [row for row, arm in zip(baseline['matrix'], baseline['groups']) if arm == arm1])

    def test_insufficient_and_failed_trials_stay_in_acceptance_denominator(self):
        study = read('study.json')
        rows = [{'phase': 'confirmation', 'scenario': 'equal-2000', 'truth': {'selectionSupported': True},
                 'evidence': {'gate': {'decision': 'EQUIVALENT' if i < 50 else 'INSUFFICIENT'}}} for i in range(100)]
        result = summarize(rows, study, 'confirmation')
        case = next(c for c in result['scenarios'] if c['scenario'] == 'equal-2000')
        self.assertEqual(case['completed'], 100)
        self.assertFalse(case['accepted'])
        self.assertLess(case['correctWilson95'][0], .5)
        self.assertEqual(result['status'], 'INCOMPLETE')

    def test_checkpoint_resumes_exact_pin_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            pin = {'image': 'test'}
            # Pin check is tested independently; cached path must not execute.
            value = {'pin': {'runtimeDigest': digest(pin), 'inputDigest': digest({'matrix': [1]}), 'seed': 7}, 'raw': {}}
            value['reportDigest'] = digest(value)
            file = folder / 'case.json'
            file.write_text(json.dumps(value))
            observed, created = checkpoint(folder, 'case', {'matrix': [1]}, pin, {'seed': 7}, lambda *_: self.fail('Cached case reran'))
            self.assertFalse(created)
            self.assertEqual(observed, value)
            with self.assertRaisesRegex(ValueError, 'PROVENANCE'):
                checkpoint(folder, 'case', {'matrix': [2]}, pin, {'seed': 7}, None)
            value['raw']['changed'] = True
            file.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, 'PROVENANCE'):
                checkpoint(folder, 'case', {'matrix': [1]}, pin, {'seed': 7}, None)

    def test_wilson_zero_errors_at_100_has_upper_bound_below_five_percent(self):
        self.assertLess(wilson(0, 100)[1], .05)
        self.assertIsNone(wilson(0, 0))

    def test_exclusive_study_lock_rejects_parallel_claim_and_releases(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            with locked(folder):
                with self.assertRaisesRegex(ValueError, 'ALREADY_RUNNING'):
                    with locked(folder): self.fail('Second runner claimed the lock')
            with locked(folder): pass

    def test_bootstrap_preserves_design_and_is_explicitly_not_full_linking(self):
        scenario = {'counts': [500, 500], 'stepShifts': [], 'logSlopeShift': 0}
        work, truth = design(scenario, 31500000, '2PL')
        values, mapping = [], {}
        for arm in work['groupOrder']:
            mapping[arm] = {}
            for item in work['items']:
                a, steps = truth['parametersByArm'][arm][item['questionVersionId']]
                index = len(values)
                values += [a, -a * steps[0]]
                mapping[arm][item['questionVersionId']] = {'a': index, 'intercepts': [index + 1]}
        parent = {'values': values, 'items': mapping,
                  'latent': {arm: {'mean': 0., 'variance': 1.} for arm in work['groupOrder']}}
        resampled, _ = bootstrap_work(work, parent, 51500000)
        self.assertEqual(resampled['operation'], 'BOOTSTRAP_REFIT')
        self.assertEqual([[x is None for x in row] for row in work['matrix']], [[x is None for x in row] for row in resampled['matrix']])
        self.assertNotEqual(work['matrix'], resampled['matrix'])


if __name__ == '__main__': unittest.main()
