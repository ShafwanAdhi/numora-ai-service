import io
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore
from engine import generate
from image_variants import ImageVariantError, build_scene, load_template, render_scene


class DimensionImageTests(unittest.TestCase):
    def test_garden_width_is_twice_radius(self):
        t = load_template('tryout-1-b3-q02')
        for p, r in ((20, 7), (56, 7), (80, 28), (29, 14), (43, 21)):
            s = build_scene(t, {'p': p, 'r': r, 'width': 2*r})
            labels = {l.id: l.text for l in s.labels}
            self.assertEqual(labels['length'], f'{p} m')
            self.assertEqual(labels['width'], f'{2*r} m')
            self.assertIn('tidak berskala', labels['schematic'])
        with self.assertRaises(ImageVariantError):
            build_scene(t, {'p': 56, 'r': 7, 'width': 28})

    def test_tank_labels_do_not_swap_cylinder_and_box_height(self):
        t = load_template('tryout-1-b3-q06')
        s = build_scene(t, {'r': 14, 'h': 15, 'p': 14, 'l': 27, 't': 30})
        labels = {l.id: l.text for l in s.labels}
        self.assertEqual(labels['dome_radius'], 'r = 14 dm')
        self.assertEqual(labels['cylinder_radius'], 'r = 14 dm')
        self.assertEqual(labels['diameter'], '28 dm')
        self.assertEqual(labels['cylinder_height'], 't = 15 dm')
        self.assertEqual(labels['box_height'], 't = 30 dm')
        self.assertEqual(labels['box_width'], 'l = 27 dm')
        self.assertEqual(labels['box_length'], 'p = 14 dm')

    def test_threshold_does_not_change_tank_pixels(self):
        t = load_template('tryout-1-b3-q06')
        values = {'r': 7, 'h': 10, 'p': 15, 'l': 12, 't': 12}
        a = render_scene(t, build_scene(t, {**values, 'threshold': 750}))
        b = render_scene(t, build_scene(t, {**values, 'threshold': 12000}))
        self.assertEqual(a.png_bytes, b.png_bytes)

    def test_accepted_generator_values_and_dimension_limits_fit(self):
        bank = OriginalBank(ROOT/'data/tryout-1/q0_bank.csv')
        configs = ConfigStore(ROOT/'configs')
        for qid, dims in (('tryout-1-b3-q02', (489,240)), ('tryout-1-b3-q06', (646,318))):
            template = load_template(qid)
            cfg, _ = configs.load(qid)
            for seed in range(1, 21):
                with self.subTest(qid=qid, seed=seed):
                    result = generate(bank.get(qid), cfg, seed, [])
                    scene = build_scene(template, result.values)
                    image = render_scene(template, scene)
                    self.assertEqual((image.width, image.height), dims)
                    self.assertLess(image.byte_length, 5 * 1024 * 1024)
                    for label in scene.labels:
                        x0, y0, x1, y1 = (n*2 for n in label.box)
                        a,b,c,d = label.ink_box
                        self.assertTrue(x0 <= a < c <= x1 and y0 <= b < d <= y1)
                    if qid.endswith('q06'):
                        exact = image.provenance['bindings']['diameter']
                        self.assertEqual(Fraction(exact['numerator'],exact['denominator']), 2*result.values['r'])

    def test_cylinder_and_cuboid_extreme_labels_fit(self):
        template = load_template('tryout-1-b3-q06')
        # Renderer layout test only: all boundaries occur in config domains;
        # this tuple need not satisfy the question's volume inequalities.
        for values in ({'r':7,'h':8,'p':10,'l':10,'t':8},
                       {'r':21,'h':25,'p':35,'l':30,'t':30}):
            scene = build_scene(template, values)
            self.assertEqual(len(scene.labels), 8)
            render_scene(template, scene)

    def test_source_outside_erasure_regions_is_preserved(self):
        import json
        for qid in ('tryout-1-b4-q05','tryout-1-b3-q02','tryout-1-b3-q06'):
            folder=ROOT/'image_templates'/qid/'v1'
            spec=json.loads((folder/'template.json').read_text(encoding='utf-8'))
            manifest=json.loads((ROOT.parent/'docs/sources/incoming/2026-10-26-tryout-images/image-manifest.json').read_text(encoding='utf-8'))
            source=next(x for x in manifest['images'] if x['candidate_local_question_id']==qid)
            original=Image.open(ROOT.parent/'docs/sources/incoming/2026-10-26-tryout-images'/source['local_path']).convert('RGB')
            base=Image.open(folder/'base.png').convert('RGB')
            diff=ImageChops.difference(original,base)
            for box in spec['authoring']['erasure_regions']:
                diff.paste((0,0,0),tuple(box))
            self.assertIsNone(diff.getbbox(), qid)

    def test_tank_old_labels_are_erased_and_bottom_captions_preserved(self):
        source = ROOT.parent/'docs/sources/incoming/2026-10-26-tryout-images/images/bab-03/soal-06/image-01.png'
        original = Image.open(source).convert('RGB')
        base = Image.open(io.BytesIO(load_template('tryout-1-b3-q06').base_bytes)).convert('RGB')
        for box in ((73,261,150,280), (396,248,470,267)):
            def dark_count(image):
                return sum(v < 90 for v in image.crop(box).convert('L').tobytes())
            self.assertLess(dark_count(base), dark_count(original)//4,
                            'Old diameter or box-length text is still visible')
        self.assertIsNone(ImageChops.difference(original.crop((0,283,646,318)),
                                              base.crop((0,283,646,318))).getbbox())


if __name__ == '__main__':
    unittest.main()
