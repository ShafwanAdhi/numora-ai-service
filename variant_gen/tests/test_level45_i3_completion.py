"""Contract tests for the remaining indicator-3 level 4--5 authoring."""
import unittest
from copy import deepcopy
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]

from engine import assemble, build_values
from filters import signature, validate_candidate
from lint import reproduce_original
from level45_completion_common import academic, entries, review_original
from author_level45_i3_completion import prepare, author
from oracle_level45_i3_completion import check_math


class Indicator3Completion(unittest.TestCase):
    def proposals(self):
        for entry, status in entries({3}):
            corrected, rationale = prepare(entry, academic(entry))
            draft = status == 'ACADEMIC_FOLLOW_UP'
            yield entry, status, corrected, rationale, review_original(corrected, draft=draft)

    def test_prepare_only_changes_the_three_held_sources(self):
        changed = []
        unchanged = 0
        for entry, status, corrected, rationale, _ in self.proposals():
            if status == 'NEXT_GENERATOR_BATCH':
                self.assertEqual(corrected, entry)
                self.assertEqual(rationale, [])
                unchanged += 1
            else:
                self.assertNotEqual(corrected['source_projection'], entry['source_projection'])
                self.assertTrue(rationale)
                proposal = corrected['source_projection']
                self.assertNotEqual(status, 'NEXT_GENERATOR_BATCH')
                self.assertIn('draft', proposal['key_caption'].casefold())
                for answer in proposal['key']:
                    self.assertIn(answer, proposal['key_caption'])
                self.assertIn('draft koreksi', proposal['explanation'].casefold())
                changed.append((entry['level'], entry['source_number']))
        self.assertEqual(unchanged, 10)
        self.assertEqual(changed, [(4, 5), (5, 5), (5, 7)])

    def test_original_and_entire_domain_are_independently_valid(self):
        for _, _, corrected, _, original in self.proposals():
            with self.subTest(qid=original['id']):
                a = author(corrected)
                cfg = a.config(original)
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                self.assertEqual(cfg['original_values'], {'k': 0})
                self.assertEqual(set(n for n, s in cfg['variables'].items() if s['gen'] != 'derived'), {'k'})
                candidates = []
                for k in range(25):
                    c = assemble(cfg, build_values(cfg, lambda name, spec, k=k: k))
                    check_math(original['id'], c)
                    if k:
                        self.assertEqual(validate_candidate(c, original, candidates), [])
                        candidates.append(c)
                self.assertGreaterEqual(len({signature(c['stem'], c['options']) for c in candidates}), 20)
                self.assertEqual(assemble(cfg, build_values(cfg, lambda n, s: 17)),
                                 assemble(cfg, build_values(cfg, lambda n, s: 17)))

    def test_seed_replay_201_through_210(self):
        for _, _, corrected, _, original in self.proposals():
            cfg = author(corrected).config(original)
            for seed in range(201, 211):
                def render():
                    rng = random.Random(seed)
                    return assemble(cfg, build_values(
                        cfg, lambda _name, spec: rng.randint(*spec['range'])))
                first, second = render(), render()
                self.assertEqual(first, second)
                check_math(original['id'], first)

    def test_oracle_rejects_wrong_key_option_and_explanation(self):
        for _, _, corrected, _, original in self.proposals():
            with self.subTest(qid=original['id']):
                cfg = author(corrected).config(original)
                c = assemble(cfg, build_values(cfg, lambda n, s: 11))
                bad = deepcopy(c)
                bad['options'][0]['correct'] = not bad['options'][0]['correct']
                with self.assertRaises(AssertionError): check_math(original['id'], bad)
                bad = deepcopy(c)
                for option in [o for o in bad['options'] if o['correct']]:
                    changed = re.sub(r'(?<=\\sqrt\{)\d+', '999999', option['text'], count=1)
                    if changed == option['text']:
                        changed = re.sub(r'\d+(?:[.,]\d+)*', '999999', option['text'], count=1)
                    if changed != option['text']:
                        option['text'] = changed; break
                with self.assertRaises(AssertionError): check_math(original['id'], bad)
                bad = deepcopy(c); bad['explanation'] = 'Pembahasan salah: 1 = 999.'
                with self.assertRaises(AssertionError): check_math(original['id'], bad)

    def test_two_radical_operands_remain_distinct(self):
        from drill_1_5_level45_math import clean
        for _, _, corrected, _, original in self.proposals():
            if original['id']!='pg-3-5-2':
                continue
            cfg=author(corrected).config(original)
            for k in range(25):
                candidate=assemble(cfg,build_values(cfg,lambda n,s,k=k:k))
                radicands=re.findall(r'sqrt\((\d+)\)',clean(candidate['stem']))[:2]
                self.assertEqual(len(radicands),2)
                self.assertNotEqual(radicands[0],radicands[1])
                check_math(original['id'],candidate)

    def test_every_displayed_explanation_number_is_verified(self):
        for _, _, corrected, _, original in self.proposals():
            cfg = author(corrected).config(original)
            for k in (0, 9, 24):
                candidate = assemble(cfg, build_values(cfg, lambda n, s, k=k: k))
                for match in re.finditer(r"(?<![A-Za-z])\d+(?:[.,]\d+)*", candidate['explanation']):
                    bad = deepcopy(candidate)
                    bad['explanation'] = (candidate['explanation'][:match.start()] +
                                          '999999' + candidate['explanation'][match.end():])
                    with self.subTest(qid=original['id'], k=k, value=match[0]):
                        with self.assertRaises(AssertionError):
                            check_math(original['id'], bad)

    def test_oracle_rejects_stimulus_equation_approximation_and_root_mutants(self):
        kinds_seen = set()
        for _, _, corrected, _, original in self.proposals():
            cfg = author(corrected).config(original)
            c = assemble(cfg, build_values(cfg, lambda n, s: 9))
            mutants = []

            changed = re.sub(r'(?<![\w])\d+(?:[.,]\d+)*(?=\s*(?:×|\\times))',
                             '999999', c['stem'], count=1)
            if changed != c['stem']:
                mutants.append(('stimulus_operand', changed))

            changed = re.sub(r'(Evaluasi III:[\s\S]*?=)\s*\d+(?:[.,]\d+)*',
                             r'\1 999999', c['stem'], count=1)
            if changed == c['stem']:
                changed = re.sub(r'(?<==)\s*\d+(?:[.,]\d+)*',
                                 ' 999999', c['stem'], count=1)
            if changed != c['stem'] and not original['id'].endswith('-2'):
                mutants.append(('equation_result', changed))

            changed = re.sub(r'(Evaluasi III:[\s\S]*?(?:≈|\\approx))\s*\d+(?:[.,]\d+)*',
                             r'\1 999999', c['stem'], count=1)
            if changed == c['stem']:
                changed = re.sub(r'(≈|\\approx)\s*\d+(?:[.,]\d+)*',
                                 r'\1 999999', c['stem'], count=1)
            if changed != c['stem']:
                mutants.append(('approximation', changed))

            changed = re.sub(r'(?<=\\sqrt\{)\d+', '999999', c['stem'], count=1)
            if changed != c['stem']:
                mutants.append(('root', changed))

            for kind, stem in mutants:
                kinds_seen.add(kind)
                bad = deepcopy(c); bad['stem'] = stem
                with self.subTest(qid=original['id'], mutant=kind):
                    with self.assertRaises(AssertionError):
                        check_math(original['id'], bad)
        self.assertEqual(kinds_seen,
                         {'stimulus_operand', 'equation_result', 'approximation', 'root'})


if __name__ == '__main__':
    unittest.main()
