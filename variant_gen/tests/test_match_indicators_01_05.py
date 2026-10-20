import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from match_indicators_01_05 import norm,signature,find_matches,component_diff,full_equal


class MatchingBoundaries(unittest.TestCase):
    def fixture(self):
        return dict(format='PG',stem='Nilai -2 cm?',options=['1','2'],key=['B'],
            category_labels=None,key_caption='B. 2',explanation='Hasil 2.',additional_notes='Catatan.')

    def test_display(self):
        self.assertEqual(norm(r'$\sqrt{5 }$'),norm('sqrt(5)'))
        self.assertEqual(norm('Rp18.000,00'),norm('Rp18.000'))
        self.assertEqual(norm(' x  +  2 '),norm('x + 2'))
        self.assertNotEqual(norm('sqrt(16)'),norm('4'))
        self.assertNotEqual(norm('1 2'),norm('12'))
        self.assertEqual(norm(r'${2}^{3}$'),norm('2^(3)'))
        self.assertEqual(norm(r'$({2}^{3}{)}^{2}$'),norm('(2^(3))^(2)'))
        self.assertEqual(norm(r'3\frac{1}{2}kg'),norm('3 1/2kg'))
        self.assertNotEqual(norm(r'x^{a+b}'),norm('x^a+b'))
        self.assertNotEqual(norm(r'{x+y}^{2}'),norm('x+y^2'))
        self.assertNotEqual(norm(r'3\frac{1}{2}'),norm('3*(1)/(2)'))

    def test_every_material_component(self):
        a=self.fixture()
        for k,v in [('stem','Nilai 2 cm?'),('stem','Nilai -3 cm?'),('stem','Nilai -2 m?'),
                    ('options',['2','1']),('key',['A']),('explanation','Hasil 3.'),
                    ('additional_notes','Catatan lain.'),('key_caption','B. 3'),('format','MCMA')]:
            b=deepcopy(a);b[k]=v
            self.assertFalse(full_equal(a,b),(k,v))
        self.assertFalse(full_equal(a,dict(a,explanation=None)))

    def test_search_returns_all_duplicates_not_first_or_same_id(self):
        a=self.fixture();bank=[dict(a,id='moved-9'),dict(a,id='moved-3')]
        self.assertEqual(find_matches(a,bank),['moved-3','moved-9'])

    def test_explanation_change_keeps_only_core_match(self):
        a=self.fixture();b=dict(a,explanation='Baru.')
        self.assertEqual(signature(a),signature(b))
        self.assertFalse(component_diff(a,b)['explanation_equal'])


if __name__=='__main__':unittest.main()
