"""Revised originals: exact reproduction, rendered math, stateless generation."""
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import Result, assemble, build_values, generate
from expr import RejectDraw
from filters import signature
from lint import reproduce_original
from drill_6_10_math import check_math

REVISED = ('pg-6-1-5', 'pg-7-1-2', 'pg-7-1-3', 'pg-7-2-4', 'pg-7-3-5',
           'mcma-8-2-8', 'pg-9-1-3', 'pg-9-1-5', 'pg-9-2-5', 'pg-9-3-2', 'pg-9-3-4')


class RevisedGenerators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = OriginalBank(ROOT/'data/drill-1-indicators-6-10/q0_bank.csv')
        cls.configs = ConfigStore(ROOT/'configs')

    def test_activation_reproduction_and_entire_default_domain(self):
        for q in REVISED:
            with self.subTest(question=q):
                original = self.bank.get(q)
                self.assertEqual(original['metadata']['generation_status'], 'ACTIVE')
                self.assertEqual(original['metadata']['generator_status'], 'IMPLEMENTED')
                self.assertEqual(original['version'], 2)
                cfg, _ = self.configs.load(q)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                for k in range(1, 41):
                    values = build_values(cfg, lambda name, spec: k)
                    check_math(self, original, Result(values, assemble(cfg, values), 0, Counter()))
                for k in (0, -1, 1.5):
                    with self.assertRaises(RejectDraw):
                        build_values(cfg, lambda name, spec: k)

    def test_matrix_latex_preserves_literal_braces(self):
        from expr import ExprError, placeholders, render
        text = r'$\begin{pmatrix} x \\ y \end{pmatrix}=\frac{1}{-11}\begin{pmatrix}{amount} \\ 2\end{pmatrix}$'
        self.assertEqual(placeholders(text), {'amount'})
        self.assertEqual(render(text, {'amount': 110000}), text.replace('{amount}', '110.000'))
        with self.assertRaises(ExprError): render('{missing}', {})

    def test_independent_seeds_and_repeatability(self):
        for q in REVISED:
            with self.subTest(question=q):
                original = self.bank.get(q)
                cfg, _ = self.configs.load(q)
                candidates = []
                for seed in range(1, 21):
                    result = generate(original, cfg, seed, candidates)
                    check_math(self, original, result)
                    candidates.append(result.cand)
                self.assertEqual(len({signature(c['stem'], c['options']) for c in candidates}), 20)
                for seed in range(201, 401):
                    result = generate(original, cfg, seed, [])
                    check_math(self, original, result)
                self.assertEqual(generate(original, cfg, 11, []).cand,
                                 generate(original, cfg, 11, []).cand)


if __name__ == '__main__': unittest.main()
