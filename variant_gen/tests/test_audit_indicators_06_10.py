"""Scope/fidelity checks plus report consistency; no runtime or DB dependencies."""
import json
import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_intake_06_10 import validate_document, validate_spans, OUT, FOLDER
from audit_original_questions import read, digest


class Intake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = validate_document()

    def test_exact_coverage_and_native_fidelity(self):
        summary = self.result['summary']
        self.assertEqual(summary['source_entries'], 250)
        self.assertEqual(summary['paragraphs_checked'], 5775)
        self.assertEqual(summary['omml_equations_checked'], 2277)
        self.assertEqual(summary['tables_checked'], 56)

    def test_parser_ambiguity_does_not_disappear(self):
        rows = self.result['entries']
        self.assertTrue(any('OPTION_BOUNDARY_REVIEW' in r['review_flags'] for r in rows))
        q = next(r for r in rows if (r['indicator'], r['level'], r['source_number']) == (6, 4, 4))
        self.assertIn('EXPLANATION_BOUNDARY_REVIEW', q['review_flags'])
        self.assertTrue(q['paragraphs'])

    def test_truncated_question_span_is_rejected(self):
        from copy import deepcopy
        index = deepcopy(read(FOLDER/'question-index.json')['questions'])
        index[0]['body_block_end_exclusive'] -= 1
        with self.assertRaises(AssertionError):
            validate_spans(index, read(FOLDER/'extracted.json')['blocks'])


class AcademicReport(unittest.TestCase):
    def test_final_report_and_csv_have_all_250_sources(self):
        from audit_indicators_06_10_academic import load_parts, validate_reviews, counts, DEST, PARTS
        rows = load_parts()
        validate_reviews(rows)
        self.assertEqual(len(rows), 250)
        final = read(DEST/'audit.json')
        self.assertEqual(len(final['entries']), 250)
        self.assertEqual({r['audit_id'] for r in rows}, {r['audit_id'] for r in final['entries']})
        for field, value in counts(rows).items():
            self.assertEqual(final['summary'][field], value)
        self.assertEqual(final['summary']['academic_parts_sha256'], {name:digest(DEST/name) for name in PARTS})
        final_rows = {r['audit_id']:r for r in final['entries']}
        for row in rows:
            for field in ('validity', 'answer_status', 'explanation_status', 'recommendation', 'issues',
                          'independently_correct_ids', 'option_evaluation', 'independent_solution'):
                self.assertEqual(final_rows[row['audit_id']][field], row[field])
        with (DEST/'entries.csv').open(encoding='utf-8-sig', newline='') as source:
            csv_rows = list(csv.DictReader(source))
        self.assertEqual(len(csv_rows), 250)
        self.assertEqual({r['audit_id'] for r in csv_rows}, set(final_rows))
        for r in csv_rows:
            for field in ('validity', 'answer_status', 'explanation_status', 'recommendation'):
                self.assertEqual(r[field], final_rows[r['audit_id']][field])
        with (DEST/'follow-up.csv').open(encoding='utf-8-sig', newline='') as source:
            self.assertEqual({r['audit_id'] for r in csv.DictReader(source)},
                             {r['audit_id'] for r in rows if r['issues']})

    def test_wrong_review_identity_and_missing_option_are_rejected(self):
        from copy import deepcopy
        from audit_indicators_06_10_academic import load_parts, validate_reviews
        rows = load_parts()
        wrong = deepcopy(rows)
        wrong[0]['audit_id'] = 'another-question'
        with self.assertRaises(AssertionError):
            validate_reviews(wrong)
        for mutate in ('duplicate_option', 'wrong_correct_ids', 'wrong_locator', 'forged_projection'):
            wrong = deepcopy(rows)
            if mutate == 'duplicate_option':
                wrong[0]['option_evaluation'][1]['id'] = wrong[0]['option_evaluation'][0]['id']
            elif mutate == 'wrong_correct_ids':
                wrong[0]['independently_correct_ids'] = ['foreign-option']
            elif mutate == 'forged_projection':
                wrong[0]['option_evaluation'][0]['text'] = 'This text is absent from the source'
                projection = wrong[0].get('source_projection_resolved', wrong[0]['source_projection'])
                projection['options'][0] = 'This text is absent from the source'
            else:
                wrong[0]['source']['paragraph_end'] -= 1
            with self.assertRaises(AssertionError):
                validate_reviews(wrong)
        wrong = deepcopy(rows)
        conditional = next(r for r in wrong if r['independently_correct_ids'] is None)
        conditional['conditional_correct_ids'] = []
        with self.assertRaises(AssertionError):
            validate_reviews(wrong)
        wrong = deepcopy(rows)
        wrong[0]['option_evaluation'] = wrong[0]['option_evaluation'][:-1]
        with self.assertRaises(AssertionError):
            validate_reviews(wrong)

    def test_known_cross_question_review_and_duplicate_pg_regressions(self):
        from audit_indicators_06_10_academic import load_parts
        rows = {(r['indicator'], r['level'], r['source_number']):r for r in load_parts()}
        cake = rows[(6, 1, 1)]
        self.assertEqual(cake['independently_correct_ids'], ['C'])
        self.assertIn('375', cake['independent_solution'])
        self.assertEqual(rows[(9, 5, 2)]['independently_correct_ids'], ['D'])
        self.assertEqual(rows[(10, 4, 2)]['validity'], 'INVALID')
        self.assertEqual(rows[(10, 4, 7)]['independently_correct_ids'], ['A','B','D'])


if __name__ == '__main__':
    unittest.main()
