"""Audit bounds must distinguish exhaustive evidence, projections and observations."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from audit_generator_inputs import audit_one, input_domain


class GeneratorInputAudit(unittest.TestCase):
    def fixture(self):
        original = dict(id='pg-test', format='PG', version=1, hash='fixture',
                        stem='Nilai 1?', cognitive_level='C3',
                        options=[dict(id='A', text='1', correct=True),
                                 dict(id='B', text='2', correct=False)])
        config = dict(question_id=original['id'], config_version=1,
                      original_hash='fixture', original_values=dict(k=1, unused=0),
                      variables=dict(k=dict(gen='choice', values=[1, 2, 3]),
                                     unused=dict(gen='choice', values=[0, 1]),
                                     wrong=dict(gen='derived', expr='k+1')),
                      stem='Nilai {k}?',
                      options=[dict(id='A', text='{k}', correct=True),
                               dict(id='B', text='{wrong}', correct=False)],
                      explanation='Nilainya {k}.')
        return original, config

    def test_exact_capacity_counts_content_not_parameter_tuples(self):
        original, config = self.fixture()
        row = audit_one(original, config, 'config-fixture')
        self.assertEqual(row['capacity']['exact'], 2)
        self.assertEqual(row['accepted_input_tuples'], 4)
        self.assertEqual(row['inputs']['k']['effective_domain']['values'], [2, 3])
        self.assertTrue(row['inputs']['k']['effective_domain']['exact'])
        self.assertEqual(row['inputs']['unused']['effect_group'], 'NO_EFFECT')
        self.assertFalse(row['adjustment_enabled'])
        self.assertEqual(row['approval_status'], 'NO_APPROVED_CONTROL')

    def test_small_domain_is_not_counted_as_large_from_unfiltered_bounds(self):
        self.assertEqual(input_domain(dict(gen='range', range=[-2, 2], filters=['nozero'])), [-2, -1, 1, 2])
        self.assertEqual(input_domain(dict(gen='range', range=[1, 7], step=2)), [2, 4, 6])
        self.assertEqual(input_domain(dict(gen='choice', values=[1, 1, 2])), [1, 2])

    def test_constraints_and_original_answer_rejection_reduce_domain(self):
        original, config = self.fixture()
        config['constraints'] = ['k < 3']
        row = audit_one(original, config, 'config-fixture')
        self.assertEqual(row['capacity']['exact'], 1)
        self.assertEqual(row['inputs']['k']['effective_domain']['values'], [2])
        self.assertEqual(row['inputs']['k']['effect_group'], 'NO_EFFECT')

    def test_bounded_probe_does_not_claim_exact_capacity(self):
        original, config = self.fixture()
        config['variables']['k']['values'] = list(range(1, 51))
        config['variables']['unused']['values'] = list(range(50))
        row = audit_one(original, config, 'config-fixture', exhaustive_limit=1, probes=2)
        self.assertIsNone(row['capacity']['exact'])
        self.assertGreater(row['capacity']['lower_bound'], 0)
        self.assertGreaterEqual(row['capacity']['upper_bound'], row['capacity']['lower_bound'])
        self.assertEqual(row['method'], 'BOUNDED_PROBE')

    def test_analytic_translations_match_exhaustive_reduced_domain(self):
        import json
        from engine import assemble, build_values
        cfg = json.loads((ROOT / 'configs/pg-17-2-5/v1.json').read_text(encoding='utf-8'))
        for name in ('x', 'y', 'c1', 'd1', 'c2', 'd2'):
            cfg['variables'][name]['range'] = [-1, 1]
        cfg['original_values'] = dict(x=0, y=0, c1=1, d1=1, c2=-1, d2=-1)
        values = build_values(cfg, lambda name, spec: cfg['original_values'][name])
        original = dict(assemble(cfg, values), id=cfg['question_id'], format='PG', version=1, hash=cfg['original_hash'])
        exact = audit_one(original, cfg, 'fixture')
        bounded = audit_one(original, cfg, 'fixture', exhaustive_limit=1, probes=10)
        self.assertEqual(bounded['capacity']['exact'], exact['capacity']['exact'])
        self.assertEqual(bounded['method'], 'ANALYTIC_WITH_PROBE')

    def test_analytic_weekdays_match_exhaustive_reduced_domain(self):
        import json
        from bank import load_workspace_bank
        cfg = json.loads((ROOT / 'configs/pg-20-1-3/v1.json').read_text(encoding='utf-8'))
        for name in ('mon', 'tue', 'wed', 'thu', 'fri'):
            cfg['variables'][name]['range'] = [5, 20]
        original = load_workspace_bank(ROOT / 'data/q0_bank.csv').get(cfg['question_id'])
        exact = audit_one(original, cfg, 'fixture')
        bounded = audit_one(original, cfg, 'fixture', exhaustive_limit=1, probes=100)
        self.assertEqual(bounded['capacity']['exact'], exact['capacity']['exact'])
        self.assertEqual(bounded['capacity']['exact'], 54)
        self.assertEqual(bounded['inputs']['fri']['effective_domain']['values'], [5, 10, 15])
        self.assertTrue(bounded['inputs']['fri']['effective_domain']['exact'])


if __name__ == '__main__':
    unittest.main()
