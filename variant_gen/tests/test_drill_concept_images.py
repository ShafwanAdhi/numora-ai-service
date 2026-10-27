"""Every original/stock gets its own pinned, academically matching diagram."""
import copy
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bank import load_workspace_bank
from conceptual_stock import load_stock, stock_record
from engine import original_record
from image_variants import ImageVariantError
from drill_concept_images import IDS, load_scenario, preview


class ConceptImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        cls.stock=load_stock(ROOT/'data/conceptual_stock.json',cls.bank)

    def test_all_12_scenarios_preserve_records_and_never_draw(self):
        self.assertEqual(len(IDS),4)
        count=0
        for qid in IDS:
            for item in [None,*self.stock[qid]]:
                before=copy.deepcopy(self.stock)
                variant=item['variant_id'] if item else None
                with self.subTest(qid=qid,variant=variant),patch('cli.generate',side_effect=AssertionError('No conceptual RNG')):
                    record,image=preview(self.bank,self.stock,qid,variant)
                expected=stock_record(self.bank.get(qid),item) if item else original_record(self.bank.get(qid))
                self.assertEqual(record,expected)
                self.assertEqual(self.stock,before)
                self.assertEqual(hashlib.sha256(image.png_bytes).hexdigest(),image.sha256)
                self.assertEqual((image.width,image.height),(960,640))
                self.assertEqual(image.provenance['content']['stock_variant_id'],variant)
                self.assertNotIn('jawaban',image.scene.alt_text.lower())
                count+=1
        self.assertEqual(count,12)

    def test_open_closed_cylinder_counts_are_per_scenario(self):
        for variant,circles in [(None,2),('mcma-16-4-7:stock-01',1),('mcma-16-4-7:stock-02',2)]:
            scenario=load_scenario('mcma-16-4-7',variant)
            self.assertEqual(scenario.geometry['panels'][0]['circle_count'],circles)
            self.assertEqual(scenario.geometry['panels'][0]['rectangle_count'],1)

    def test_panels_follow_stocks_instead_of_reusing_original(self):
        one=load_scenario('pg-16-4-2','pg-16-4-2:stock-01')
        two=load_scenario('pg-16-4-2','pg-16-4-2:stock-02')
        self.assertEqual([p['id'] for p in one.geometry['panels']],list('ABCD'))
        self.assertEqual(one.geometry['panels'][2]['triangle_count'],3)
        self.assertEqual(two.geometry['panels'][3]['arc_relation'],'shorter')
        self.assertNotEqual(one.image.base_sha256,two.image.base_sha256)

    def test_single_cylinder_stock_does_not_display_the_requested_formula(self):
        scenario=load_scenario('pg-16-5-1','pg-16-5-1:stock-02')
        self.assertEqual(len(scenario.geometry['panels']),1)
        text=' '.join(label.text for label in scenario.image.labels)
        self.assertNotIn('2πr',text)
        self.assertNotIn('2*pi*r',text)
        self.assertNotIn('sama dengan keliling',scenario.image.alt_text)

    def test_tetrahedron_has_four_faces_and_six_solid_edges(self):
        scenario=load_scenario('mcma-16-4-6')
        geometry=scenario.geometry
        self.assertEqual(len(geometry['net_faces']),4)
        self.assertEqual(len(geometry['solid_vertices']),4)
        self.assertEqual(len(geometry['solid_edges']),6)
        self.assertEqual(len({tuple(sorted(e)) for e in geometry['solid_edges']}),6)

    def test_changed_original_stock_or_foreign_selection_fails_closed(self):
        bank=copy.copy(self.bank)
        qid='pg-16-4-2'
        changed=self.bank.get(qid);changed['stem']+=' Changed'
        with patch.object(bank,'get',return_value=changed):
            with self.assertRaises(ImageVariantError):preview(bank,self.stock,qid)
        stock=copy.deepcopy(self.stock);stock[qid][0]['explanation']+=' Changed'
        with self.assertRaises(ImageVariantError):preview(self.bank,stock,qid,stock[qid][0]['variant_id'])
        for variant in ('mcma-16-4-7:stock-01','pg-16-4-2:stock-03','../x'):
            with self.assertRaises(ImageVariantError):preview(self.bank,self.stock,qid,variant)
        with self.assertRaises(ImageVariantError):load_scenario('../x')

    def test_deterministic_and_no_network_or_storage(self):
        with patch('socket.socket',side_effect=AssertionError('No network')),patch(
                'database.connection',side_effect=AssertionError('No database')),patch.object(
                Path,'write_bytes',side_effect=AssertionError('No image writes')),patch.object(
                Path,'write_text',side_effect=AssertionError('No text writes')):
            a=preview(self.bank,self.stock,'pg-16-4-2')[1]
            b=preview(self.bank,self.stock,'pg-16-4-2')[1]
        self.assertEqual(a.png_bytes,b.png_bytes)
        self.assertEqual(a.provenance,b.provenance)


if __name__=='__main__':unittest.main()
