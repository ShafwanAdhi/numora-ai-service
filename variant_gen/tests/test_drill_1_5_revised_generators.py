"""Revised curriculum originals: recipes, rendered arithmetic, stateless integration."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from filters import signature
from lint import reproduce_original

REVISED = (
    'pg-1-1-5','pg-1-2-3','mcma-1-2-6','pg-1-3-1','pg-1-3-5','mcma-1-3-6',
    'pg-2-1-1','pg-2-1-2','pg-2-1-3','pg-2-1-5','pg-2-2-1','pg-2-2-2',
    'pg-2-2-4','mcma-2-2-6','mcma-2-2-7','mcma-2-3-6',
    'pg-3-1-2','pg-3-1-3','pg-3-1-5','pg-3-2-2','pg-3-2-3','pg-3-2-4',
    'mcma-3-2-7','mcma-3-2-8','kategori-3-2-9','pg-3-3-3',
    'pg-4-1-1','mcma-4-1-8','kategori-4-1-9','kategori-4-1-10',
    'pg-4-2-2','pg-4-2-5','mcma-4-2-8','kategori-4-2-9','kategori-4-2-10',
    'pg-4-3-1','mcma-4-3-8','kategori-4-3-9','kategori-4-3-10','pg-5-1-5',
)


class RevisedGenerators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.originals = {q:b.get(q) for b in (
            OriginalBank(ROOT/'data/drill-1-indicators-1-2/q0_bank.csv'),
            OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv')) for q in b.ids()}
        cls.configs = ConfigStore(ROOT/'configs')

    def test_all_forty_revisions_have_active_matching_recipes(self):
        self.assertEqual(len(REVISED),40)
        for q in REVISED:
            with self.subTest(question=q):
                original = self.originals[q]
                self.assertEqual(original['metadata']['generation_status'],'ACTIVE')
                self.assertEqual(original['metadata']['generator_status'],'IMPLEMENTED')
                self.assertEqual(original['version'],2)
                cfg,_ = self.configs.load(q)
                self.assertEqual(validate_config(cfg,original),[])
                self.assertEqual(reproduce_original(original,cfg),([],[]))

    def test_twenty_unique_and_independent_seeds(self):
        from drill_1_5_revised_math import check_math
        for q in REVISED:
            with self.subTest(question=q):
                original = self.originals[q];cfg,_ = self.configs.load(q)
                values = build_values(cfg,lambda name,spec:cfg['original_values'][name])
                check_math(original,assemble(cfg,values))
                name,spec = next((n,s) for n,s in cfg['variables'].items() if s['gen']!='derived')
                domain = spec['values'] if spec['gen']=='choice' else range(spec['range'][0],spec['range'][1]+1)
                for value in domain:
                    check_math(original,assemble(cfg,build_values(cfg,lambda n,s:value)))
                if spec['gen']=='range':
                    from expr import RejectDraw
                    for invalid in (0,-1,1.5,spec['max']+1):
                        with self.assertRaises(RejectDraw):build_values(cfg,lambda n,s:invalid)
                candidates = []
                for seed in range(1,21):
                    c = generate(original,cfg,seed,candidates).cand
                    check_math(original,c);candidates.append(c)
                self.assertEqual(len({signature(c['stem'],c['options']) for c in candidates}),20)
                for seed in range(201,251):
                    check_math(original,generate(original,cfg,seed,[]).cand)
                self.assertEqual(generate(original,cfg,11,[]).cand,generate(original,cfg,11,[]).cand)
                bad = copy.deepcopy(candidates[0]);bad['options'][0]['correct'] ^= True
                with self.assertRaises(AssertionError):check_math(original,bad)
                bad = copy.deepcopy(candidates[0]);bad['explanation']='Hasil = 999999.'
                with self.assertRaises(AssertionError):check_math(original,bad)

    def test_two_source_conflicts_remain_blocked(self):
        from config_store import ConfigError
        for q in ('pg-1-2-1','pg-5-3-3'):
            self.assertEqual(self.originals[q]['metadata']['generation_status'],'HOLD_SOURCE')
            self.assertEqual(self.configs.versions(q),[])
            with self.assertRaises(ConfigError):generate(self.originals[q],{},11,[])

    def test_temperature_latex_unit_is_literal(self):
        from expr import placeholders,render
        text = r'$-{value}^\circ\text{C}$'
        self.assertEqual(placeholders(text),{'value'})
        from fractions import Fraction
        self.assertEqual(render(text,{'value':Fraction(7,2)}),r'$-3,5^\circ\text{C}$')

    def test_prime_factorization_rejects_unreviewed_bases(self):
        from expr import RejectDraw
        for q in ('mcma-4-1-8','pg-4-2-5'):
            cfg,_=self.configs.load(q)
            for invalid in (0,1,3,5,8,9,1.5):
                with self.subTest(question=q,base=invalid):
                    with self.assertRaises(RejectDraw):build_values(cfg,lambda n,s:invalid)

    def test_cli_generates_revisions_without_storage(self):
        import contextlib,io,tempfile,cli
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            store = Path(tmp)/'variants.jsonl'
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                for q in ('pg-1-3-1','pg-2-2-4','pg-3-2-4','pg-4-3-1','pg-5-1-5'):
                    for _ in range(2):
                        self.assertEqual(cli.main(['gen',q,'s11','--store',str(store)]),0)
            self.assertFalse(store.exists())


if __name__ == '__main__':unittest.main()
