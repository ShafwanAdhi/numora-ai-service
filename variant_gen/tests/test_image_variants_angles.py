import io
import itertools
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore
from engine import build_values, generate
from expr import to_num
from image_variants import build_scene, load_template, render_scene


class AngleImageTests(unittest.TestCase):
    def test_erased_expression_baselines_have_no_old_ink(self):
        template=load_template('tryout-1-b3-q03')
        base=Image.open(io.BytesIO(template.base_bytes)).convert('L')
        for box in ((32,203,119,209),(409,261,518,265)):
            self.assertEqual(sum(v<95 for v in base.crop(box).tobytes()),0)

    def test_angle_labels_repeat_expression_without_leaking_answer(self):
        template = load_template('tryout-1-b3-q03')
        bank = OriginalBank(ROOT/'data/tryout-1/q0_bank.csv')
        cfg, _ = ConfigStore(ROOT/'configs').load('tryout-1-b3-q03')
        result = generate(bank.get('tryout-1-b3-q03'), cfg, 1, [])
        scene = build_scene(template, result.values)
        labels = {label.id: label.text for label in scene.labels}
        self.assertEqual(labels['parallel_first'], '(4x+17)°')
        self.assertEqual(labels['triangle_first'], '(4x+17)°')
        self.assertEqual(labels['parallel_second'], '(8x−51)°')
        self.assertEqual(labels['triangle_second'], '70°')
        self.assertNotIn('25°', labels.values())
        self.assertNotIn('ans', dict(scene.bindings))
        self.assertNotIn('x', dict(scene.bindings))
        source = ROOT.parent/'docs/sources/incoming/2026-10-26-tryout-images/images/bab-03/soal-03/image-01.png'
        original = Image.open(source).convert('RGB')
        base = Image.open(io.BytesIO(template.base_bytes)).convert('RGB')
        self.assertIsNone(ImageChops.difference(original.crop((485,91,516,123)), base.crop((485,91,516,123))).getbbox())
        self.assertEqual((render_scene(template, scene).width, render_scene(template, scene).height), (648,318))

    def test_original_expression_can_render_even_if_outside_random_draw_domain(self):
        cfg, _ = ConfigStore(ROOT/'configs').load('tryout-1-b3-q03')
        values = build_values(cfg, lambda k,s:to_num(cfg['original_values'][k]), check=False)
        scene = build_scene(load_template('tryout-1-b3-q03'), values)
        labels = {l.id:l.text for l in scene.labels}
        self.assertEqual(labels['parallel_first'], '(3x+15)°')
        self.assertEqual(labels['parallel_second'], '(5x−25)°')
        self.assertEqual(labels['triangle_second'], '50°')
        self.assertEqual(cfg['variables']['c']['range'], [6,9])

    def test_all_constraint_valid_angle_labels_fit_without_collision(self):
        from image_variants.scene import measure_label
        template = load_template('tryout-1-b3-q03')
        strings = {key:set() for key in ('parallel_first','triangle_first','parallel_second','triangle_second')}
        checked = 0
        for x,a,b,c,other in itertools.product(range(5,26),range(2,6),range(5,21),range(6,10),range(30,76,5)):
            angle=a*x+b;offset=c*x-angle
            if offset<=0 or angle+other>=170:
                continue
            checked+=1
            strings['parallel_first'].add(f'({a}x+{b})°')
            strings['triangle_first'].add(f'({a}x+{b})°')
            strings['parallel_second'].add(f'({c}x−{offset})°')
            strings['triangle_second'].add(f'{other}°')
        self.assertGreater(checked,10000)
        for label in template.labels:
            for text in strings.get(label.id, {label.text}):
                placed=measure_label(template,label,text)
                x0,y0,x1,y1=(v*2 for v in label.box)
                a,b,c,d=placed.ink_box
                self.assertTrue(x0<=a<c<=x1 and y0<=b<d<=y1)
        for i,a in enumerate(template.labels):
            for b in template.labels[i+1:]:
                self.assertTrue(a.box[2]<=b.box[0] or b.box[2]<=a.box[0] or a.box[3]<=b.box[1] or b.box[3]<=a.box[1])


if __name__=='__main__':
    unittest.main()
