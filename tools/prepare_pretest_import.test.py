import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('prep', Path(__file__).with_name('prepare_pretest_import.py'))
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)

class IntakeTests(unittest.TestCase):
    def test_all_source_questions_and_formats(self):
        data = prep.prepare(write=False)
        self.assertEqual([len(p['questions']) for p in data['packages']], [20]*4)
        self.assertEqual(len(data['audit']), 80)
        self.assertEqual(len(data['media']), 35)
        for p in data['packages']:
            self.assertEqual([q['metadata']['sourceOrder'] for q in p['questions']], list(range(1,21)))
            self.assertTrue(all(q['metadata']['sourceLevelNumber'] is None for q in p['questions']))
            self.assertEqual(sorted(__import__('collections').Counter(q['type'] for q in p['questions']).values()), [4,6,10])
    def test_appendix_and_subchapter_headings_never_enter_question(self):
        data = prep.prepare(write=False)
        for p in data['packages']:
            for q in p['questions']:
                text = q['stem']['text'] + q['explanation']['text']
                self.assertNotIn('LAMPIRAN', text)
                self.assertNotIn('SUB BAB', text)
                self.assertNotIn('REKAP KUNCI', text)
    def test_category_rows_tables_images_and_source_keys_are_preserved(self):
        d = prep.prepare(write=False)
        q = d['packages'][0]['questions'][15]
        self.assertIn('45', q['stem']['text'])
        self.assertIn('180', q['stem']['text'])
        self.assertEqual(len(q['options']), 3)
        self.assertEqual(q['answer']['categoryByStatementId'], {'A':'FALSE','B':'TRUE','C':'TRUE'})
        self.assertEqual(d['packages'][2]['questions'][4]['answer']['optionIds'], ['1','2'])
        a = next(a for a in d['audit'] if a['id']=='pretest-b3-q05')
        self.assertEqual(a['independent_answer'], ['1','2','3'])
        self.assertEqual(a['key_status'], 'BERMASALAH')
        self.assertIn('[[asset:diagram-1]]', d['packages'][0]['questions'][7]['stem']['text'])
        self.assertIn(r'20\%', d['packages'][0]['questions'][7]['stem']['text'])
        self.assertIn(r'\{−1,0,1,2,3\}', d['packages'][1]['questions'][11]['stem']['text'])
        self.assertIn(r'−5\;4', d['packages'][2]['questions'][7]['stem']['text'])

if __name__ == '__main__': unittest.main()
