"""Real pinned R checks; explicit skip without the v2 experimental image."""
import json
import os
from pathlib import Path
import unittest

from numora_service.irt.anchor_uncertainty import evaluate
from numora_service.irt.math import probabilities
from numora_service.irt.runner import run
from research.irt.synthetic import generate
from copy import deepcopy


@unittest.skipUnless(os.environ.get('IRT_ANCHOR_V2_TEST_IMAGE'), 'requires explicit v2 R image')
class AnchorRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value, _ = generate(1000, 20261119)
        people = value['respondents']
        rows = {p['attemptId']: {} for p in people}
        for row in value['responses']: rows[row['attemptId']][row['questionVersionId']] = row['scoreCategory']
        cls.policy = json.loads((Path(__file__).resolve().parents[2] / 'research/irt/anchor-v2/policy.json').read_text())
        cls.work = {'policy': cls.policy, 'items': value['items'], 'anchors': value['anchorQuestionVersionIds'],
                    'groupOrder': [p['armId'] for p in value['packages']],
                    'groups': [p['deliveredArmId'] for p in people],
                    'matrix': [[rows[p['attemptId']].get(i['questionVersionId']) for i in value['items']] for p in people]}
        cls.result = run(cls.work, image=os.environ['IRT_ANCHOR_V2_TEST_IMAGE'])

    def test_covariance_mapping_probability_oracle_and_reference_diagnostic(self):
        work, result = self.work, self.result
        self.assertTrue(result['converged'], result.get('engineStage'))
        original, variant = work['groupOrder']
        for qid in work['anchors']:
            released = result['released'][qid]
            self.assertNotEqual(released['mapping'][original]['a'], released['mapping'][variant]['a'])
            self.assertEqual(len(released['values']), len(released['covariance']))
            for arm in work['groupOrder']:
                pin = released['mapping'][arm]
                a = released['values'][pin['a']]
                d = [released['values'][j] for j in pin['intercepts']]
                steps = [-(v - (d[k - 1] if k else 0)) / a for k, v in enumerate(d)]
                for theta, expected in zip([-2, 0, 2], released['probabilityOracle'][arm][qid]):
                    for observed, target in zip(probabilities(theta, a, steps), expected):
                        self.assertAlmostEqual(observed, target, delta=1e-8)
        gate = evaluate(result, work['anchors'], original, [variant], self.policy)
        self.assertNotEqual(gate['decision'], 'NOT_EVALUATED')
        self.assertTrue(result['referenceRefit']['converged'])
        self.assertTrue(result['referenceRefit']['diagnosticOnly'])
        if os.environ.get('IRT_ANCHOR_V2_TEST_OUTPUT'):
            Path(os.environ['IRT_ANCHOR_V2_TEST_OUTPUT']).write_text(json.dumps(result), encoding='utf-8')

    def test_bootstrap_refit_is_explicitly_not_a_linking_or_scoring_artifact(self):
        work = deepcopy(self.work)
        work.update(operation='BOOTSTRAP_REFIT', bootstrapAnchor=work['anchors'][0])
        raw = run(work, image=os.environ['IRT_ANCHOR_V2_TEST_IMAGE'])
        self.assertEqual(raw['operation'], 'BOOTSTRAP_REFIT')
        self.assertTrue(raw['target']['converged'])
        self.assertFalse(raw['canonicalScoring'])
        self.assertNotIn('respondents', raw)

    def test_unidentified_missing_anchor_data_do_not_produce_equivalence(self):
        work = deepcopy(self.work)
        anchors = set(work['anchors'])
        for row in work['matrix']:
            for j, item in enumerate(work['items']):
                if item['questionVersionId'] in anchors: row[j] = None
        raw = run(work, image=os.environ['IRT_ANCHOR_V2_TEST_IMAGE'])
        self.assertFalse(evaluate(raw, work['anchors'], work['groupOrder'][0], work['groupOrder'][1:], self.policy)['passed'])


if __name__ == '__main__': unittest.main()
