"""Indicators 4-5 completion: corrections, generators, and independent oracle."""
import copy
import re
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]

from engine import assemble, build_values
from filters import signature, validate_candidate
from lint import reproduce_original
from level45_completion_common import academic, entries, key, review_original
from author_level45_i45_completion import author, prepare
from oracle_level45_i45_completion import check_math


class Indicator45Completion(unittest.TestCase):
    def prepared(self):
        return [(prepare(e, academic(e)), status) for e, status in entries({4, 5})]

    def test_scope_and_correction_quarantine(self):
        rows = self.prepared()
        self.assertEqual(len(rows), 28)
        self.assertEqual(sum(s == 'NEXT_GENERATOR_BATCH' for _, s in rows), 15)
        self.assertEqual(sum(s == 'ACADEMIC_FOLLOW_UP' for _, s in rows), 13)
        for (corrected, reasons), status in rows:
            original = next(e for e, _ in entries({4, 5}) if key(e) == key(corrected))
            if status == 'NEXT_GENERATOR_BATCH':
                self.assertEqual(corrected, original)
                self.assertEqual(reasons, [])
            else:
                self.assertIsNot(corrected, original)
                self.assertTrue(reasons)

    def test_required_corrections(self):
        by_id = {key(e): prepare(e, academic(e))[0] for e, _ in entries({4, 5})}
        self.assertIn('komposisi', by_id['pg-4-4-4']['source_projection']['stem'].lower())
        self.assertIn('balok', by_id['pg-4-4-5']['source_projection']['stem'].lower())
        self.assertIn('dibandingkan dengan jadwal awal', by_id['pg-4-5-5']['source_projection']['stem'])
        self.assertIn('mula-mula kosong', by_id['pg-5-4-3']['source_projection']['stem'])
        self.assertEqual(by_id['pg-5-5-4']['source_projection']['key'], ['B'])

    def test_every_input_replays_and_has_twenty_unique_variants(self):
        for (entry, _), status in self.prepared():
            qid = key(entry)
            original = review_original(entry, draft=status == 'ACADEMIC_FOLLOW_UP')
            cfg = author(entry).config(original)
            self.assertEqual(reproduce_original(original, cfg), ([], []))
            self.assertEqual(set(cfg['original_values']), {'k'})
            self.assertEqual(cfg['original_values']['k'], 0)
            spec = cfg['variables']['k']
            inputs = spec.get('values', range(spec['range'][0], spec['range'][1] + 1, spec.get('step', 1)))
            seen = set()
            core = set()
            accepted = []
            for k in inputs:
                candidate = assemble(cfg, build_values(cfg, lambda name, variable: k))
                check_math(qid, candidate)
                seen.add(signature(candidate['stem'], candidate['options']))
                core.add(tuple(re.findall(r'\d+(?:[.,]\d+)*', candidate['stem'])))
                if k:
                    self.assertEqual(validate_candidate(candidate, original, accepted), [])
                    accepted.append(candidate)
            with self.subTest(qid=qid):
                self.assertGreaterEqual(len(seen), 20)
                self.assertGreaterEqual(len(core), 20)

    def test_oracle_rejects_key_and_explanation_corruption(self):
        for (entry, _), status in self.prepared():
            qid = key(entry)
            original = review_original(entry, draft=status == 'ACADEMIC_FOLLOW_UP')
            cfg = author(entry).config(original)
            candidate = assemble(cfg, build_values(cfg, lambda name, variable: 17))
            check_math(qid, candidate)
            bad = copy.deepcopy(candidate)
            bad['options'][0]['correct'] = not bad['options'][0]['correct']
            with self.subTest(qid=qid, mutation='key'):
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)
            bad = copy.deepcopy(candidate)
            bad['explanation'] = 'Pembahasan yang tidak memuat bukti hitungan.'
            with self.subTest(qid=qid, mutation='explanation'):
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)

    def test_oracle_rejects_stimulus_option_and_inline_equality_mutants(self):
        rows={key(e):(prepare(e,academic(e))[0],s) for e,s in entries({4,5})}
        for qid in ('pg-4-4-5','pg-5-4-3','mcma-5-4-7'):
            entry,status=rows[qid]; original=review_original(entry,draft=status=='ACADEMIC_FOLLOW_UP')
            cfg=author(entry).config(original); candidate=assemble(cfg,build_values(cfg,lambda n,v:7))
            bad=copy.deepcopy(candidate)
            bad['stem']=re.sub(r'\d+(?:[.,]\d+)*','999999',bad['stem'],count=1)
            with self.subTest(qid=qid,mutation='stimulus'):
                with self.assertRaises(AssertionError): check_math(qid,bad)
            bad=copy.deepcopy(candidate)
            target=next(o for o in bad['options'] if o['correct'])
            target['text']=re.sub(r'\d+(?:[.,]\d+)*','999999',target['text'],count=1)
            with self.subTest(qid=qid,mutation='option'):
                with self.assertRaises(AssertionError): check_math(qid,bad)
        entry,status=rows['pg-5-5-2']; original=review_original(entry,draft=status=='ACADEMIC_FOLLOW_UP')
        candidate=assemble(author(entry).config(original),build_values(author(entry).config(original),lambda n,v:0))
        bad=copy.deepcopy(candidate); bad['stem']=bad['stem'].replace('400×2=800','400×2=999')
        with self.assertRaises(AssertionError): check_math('pg-5-5-2',bad)


    def test_every_explanation_number_is_independently_verified(self):
        for (entry, _), status in self.prepared():
            original=review_original(entry,draft=status=='ACADEMIC_FOLLOW_UP')
            cfg=author(entry).config(original)
            for k in (0,9,24):
                candidate=assemble(cfg,build_values(cfg,lambda n,s,k=k:k))
                for match in re.finditer(r'\d+(?:[.,]\d+)*',candidate['explanation']):
                    bad=copy.deepcopy(candidate)
                    bad['explanation']=(candidate['explanation'][:match.start()]+'999999'+
                                        candidate['explanation'][match.end():])
                    with self.subTest(qid=key(entry),k=k,value=match[0]):
                        with self.assertRaises(AssertionError): check_math(key(entry),bad)


if __name__ == '__main__':
    unittest.main()
