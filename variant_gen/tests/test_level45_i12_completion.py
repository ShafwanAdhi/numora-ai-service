"""Indicator 1-2 level 4-5 completion: source fidelity and independent maths."""
import sys
import unittest
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]

from config_store import validate_config
from engine import assemble, build_values, generate
from filters import signature, validate_candidate
from lint import reproduce_original
from level45_completion_common import academic, entries, key, review_original
from author_level45_i12_completion import author, prepare
from oracle_level45_i12_completion import check_math


class Indicator12Completion(unittest.TestCase):
    def prepared(self):
        for entry, status in entries({1, 2}):
            corrected, rationale = prepare(entry, academic(entry))
            yield entry, status, corrected, rationale

    def test_exact_scope_and_corrections_are_quarantined(self):
        rows = list(self.prepared())
        self.assertEqual(len(rows), 26)
        counts = {'NEXT_GENERATOR_BATCH': 0, 'ACADEMIC_FOLLOW_UP': 0}
        for original, status, corrected, rationale in rows:
            counts[status] += 1
            with self.subTest(qid=key(original)):
                if status == 'NEXT_GENERATOR_BATCH':
                    self.assertEqual(corrected['source_projection'], original['source_projection'])
                    self.assertEqual(rationale, [])
                else:
                    self.assertNotEqual(corrected['source_projection'], original['source_projection'])
                    self.assertTrue(rationale)
                    proposal = corrected['source_projection']
                    self.assertIn('Koreksi draft', proposal['additional_notes'])
                    for answer in proposal['key']:
                        self.assertIn(answer, proposal['key_caption'])
        self.assertEqual(counts, {'NEXT_GENERATOR_BATCH': 14, 'ACADEMIC_FOLLOW_UP': 12})

    def test_config_reproduces_each_review_copy(self):
        for _raw, status, entry, _rationale in self.prepared():
            qid = key(entry)
            with self.subTest(qid=qid):
                original = review_original(entry, draft=status != 'NEXT_GENERATOR_BATCH')
                cfg = author(entry).config(original)
                self.assertEqual(set(cfg['original_values']), {'k'})
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                check_math(qid, assemble(cfg, build_values(
                    cfg, lambda name, spec: cfg['original_values'][name])))

    def test_entire_domain_and_twenty_unique_variants(self):
        for _raw, status, entry, _rationale in self.prepared():
            qid = key(entry)
            with self.subTest(qid=qid):
                original = review_original(entry, draft=status != 'NEXT_GENERATOR_BATCH')
                cfg = author(entry).config(original)
                spec = cfg['variables']['k']
                domain = spec.get('values', range(spec['range'][0], spec['range'][1] + 1,
                                                   spec.get('step', 1)))
                valid = set()
                accepted = []
                for k in domain:
                    candidate = assemble(cfg, build_values(cfg, lambda name, spec, k=k: k))
                    check_math(qid, candidate)
                    if k:
                        failures = validate_candidate(candidate, original, accepted)
                        self.assertEqual(failures, [], (qid, k, failures))
                        accepted.append(candidate)
                        valid.add(signature(candidate['stem'], candidate['options']))
                self.assertGreaterEqual(len(valid), 20)
                for seed in range(201, 211):
                    value = seed % 25
                    first = assemble(cfg, build_values(cfg, lambda name, spec, value=value: value))
                    second = assemble(cfg, build_values(cfg, lambda name, spec, value=value: value))
                    self.assertEqual(first, second)
                    check_math(qid, first)

    def test_oracle_rejects_key_explanation_and_claim_mutations(self):
        for _raw, status, entry, _rationale in self.prepared():
            qid = key(entry)
            with self.subTest(qid=qid):
                original = review_original(entry, draft=status != 'NEXT_GENERATOR_BATCH')
                cfg = author(entry).config(original)
                candidate = assemble(cfg, build_values(cfg, lambda name, spec: 17))
                bad = deepcopy(candidate)
                bad['options'][0]['correct'] = not bad['options'][0]['correct']
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)
                bad = deepcopy(candidate)
                bad['explanation'] = re.sub(r'\d+(?:[.,]\d+)?', '999999',
                                            candidate['explanation'])
                self.assertNotEqual(bad['explanation'], candidate['explanation'])
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)
                bad = deepcopy(candidate)
                bad['options'][-1]['text'] += ' Klaim tambahan: 1 + 1 = 999.'
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)

    def test_runtime_generates_twenty_distinct_math_variants(self):
        """Exercise the production draw/filter path, not just direct assembly."""
        for _raw, status, entry, _rationale in self.prepared():
            qid = key(entry)
            with self.subTest(qid=qid):
                original = review_original(entry, draft=status != 'NEXT_GENERATOR_BATCH')
                cfg = author(entry).config(original)
                made = []
                numeric_inputs = set()
                for seed in range(400, 420):
                    result = generate(original, cfg, seed, made)
                    check_math(qid, result.cand)
                    made.append(result.cand)
                    # Values occur inside the task itself (before the response
                    # prompt), so a changing suffix cannot satisfy this guard.
                    task = re.split(r'Manakah|Tentukan status|Bentuk sederhana',
                                    result.cand['stem'], maxsplit=1)[0]
                    numeric_inputs.add(tuple(re.findall(r'-?\d+(?:[.,]\d+)?', task)))
                self.assertEqual(len(made), 20)
                self.assertGreaterEqual(len(numeric_inputs), 20)


if __name__ == '__main__':
    unittest.main()
