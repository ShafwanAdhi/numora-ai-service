import io
import itertools
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from config_store import ConfigStore
from engine import build_values
from expr import RejectDraw, to_num
from image_variants import ImageVariantError, build_scene, load_template, render_scene
try:
    from image_variants.geometry import pyramid_water_vertices
except ImportError:
    pyramid_water_vertices=None


class PyramidImageTests(unittest.TestCase):
    def test_crossed_or_degenerate_template_rim_is_rejected(self):
        import image_variants.templates as loader
        original=loader._read_inside
        for rim in (((154,83),(518,28),(272,28),(405,87)),
                    ((150,50),(250,50),(350,50),(450,50))):
            def read(root,path):
                data=original(root,path)
                if path.name=='template.json':
                    spec=json.loads(data);spec['geometry']['rim']=rim
                    return json.dumps(spec).encode('utf-8')
                return data
            with self.subTest(rim=rim),patch.object(loader,'_read_inside',side_effect=read),self.assertRaises(ImageVariantError):
                load_template('tryout-1-b3-q04')

    def test_modified_water_geometry_cannot_be_rendered_as_original_scene(self):
        t=load_template('tryout-1-b3-q04')
        scene=build_scene(t,{'s':12,'h':18,'p':1,'q':3})
        forged=replace(scene,geometry=replace(scene.geometry,ratio=Fraction(2,3)))
        with self.assertRaises(ImageVariantError):render_scene(t,forged)

    def test_water_vertices_interpolate_exact_fraction(self):
        self.assertIsNotNone(pyramid_water_vertices,'Water geometry is not implemented')
        apex=(0,90);rim=((-30,0),(0,-15),(30,0),(0,15))
        for ratio in (Fraction(1,3),Fraction(2,3)):
            water=pyramid_water_vertices(apex,rim,ratio)
            self.assertEqual(len(water),4)
            for point,top in zip(water,rim):
                self.assertEqual(point,tuple(Fraction(p)+ratio*(v-p) for p,v in zip(apex,top)))
                self.assertTrue(all(isinstance(x,Fraction) for x in point))

    def test_water_stays_inside_vessel_and_moves_monotonically(self):
        t=load_template('tryout-1-b3-q04')
        a=build_scene(t,{'s':12,'h':18,'p':1,'q':3}).geometry
        b=build_scene(t,{'s':12,'h':18,'p':2,'q':3}).geometry
        for low,high,top in zip(a.water,b.water,t.geometry.rim):
            self.assertTrue(top[1]<high[1]<low[1]<t.geometry.apex[1])
        def area(points):
            return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2
        self.assertEqual(area(b.water),4*area(a.water))

    def test_same_dimensions_different_ratio_changes_fill_and_label(self):
        t=load_template('tryout-1-b3-q04')
        a=render_scene(t,build_scene(t,{'s':12,'h':18,'p':1,'q':3}))
        b=render_scene(t,build_scene(t,{'s':12,'h':18,'p':2,'q':3}))
        self.assertEqual(a.scene.geometry.ratio,Fraction(1,3))
        self.assertIn('1/3',a.scene.alt_text)
        self.assertIn('2/3',b.scene.alt_text)
        images=[Image.open(io.BytesIO(r.png_bytes)).convert('RGB') for r in (a,b)]
        self.assertIsNotNone(ImageChops.difference(*(im.crop((150,30,520,304)) for im in images)).getbbox())
        empty,filled=(im.getpixel((320,180)) for im in images)
        self.assertLess(abs(empty[2]-empty[0]),15)
        self.assertGreater(filled[2]-filled[0],20)

    def test_original_and_seed_one_math_matches_exact_scene(self):
        t=load_template('tryout-1-b3-q04')
        cfg,_=ConfigStore(ROOT/'configs').load(t.question_id)
        for values,expected in (({'s':12,'h':18,'p':2,'q':3},(12,8,256)),
                                ({'s':9,'h':27,'p':1,'q':3},(9,3,27))):
            v=build_values(cfg,lambda k,s:to_num(values[k]))
            scene=build_scene(t,v)
            ratio=scene.geometry.ratio
            self.assertEqual((v['h']*ratio,v['s']*ratio,Fraction(v['s']**2*v['h'],3)*ratio**3),expected)
            self.assertEqual((v['hw'],v['sw'],v['water']),expected)
            self.assertNotIn('water',dict(scene.bindings))
            self.assertNotIn('water',scene.alt_text)

    def test_invalid_ratios_and_rounded_float_inputs_are_rejected(self):
        t=load_template('tryout-1-b3-q04')
        for p,q in ((0,3),(3,3),(4,3),(-1,3),(1,0)):
            with self.subTest(p=p,q=q),self.assertRaises(ImageVariantError):
                build_scene(t,{'s':12,'h':18,'p':p,'q':q})
        for ratio in (0.333333,1/3,True):
            with self.assertRaises(ImageVariantError):
                build_scene(t,{'s':12,'h':18,'p':1,'q':3,'ratio':ratio})

    def test_repeated_edge_labels_and_fraction_format(self):
        scene=build_scene(load_template('tryout-1-b3-q04'),{'s':30,'h':45,'p':2,'q':3})
        labels={l.id:l.text for l in scene.labels}
        self.assertEqual(labels['edge_front'],'30 cm')
        self.assertEqual(labels['edge_back'],'30 cm')
        self.assertIn('45 cm',labels['total_height'])
        self.assertIn('2/3',labels['water_height'])
        self.assertNotIn('0,67',labels['water_height'])

    def test_entire_config_domain_renders_without_expanding_constraints(self):
        t=load_template('tryout-1-b3-q04');cfg,_=ConfigStore(ROOT/'configs').load(t.question_id)
        seen=accepted=0
        for s,h,p in itertools.product(range(6,31,3),range(9,46,3),(1,2)):
            seen+=1
            source={'s':s,'h':h,'p':p,'q':3}
            try:values=build_values(cfg,lambda k,sp:to_num(source[k]))
            except RejectDraw:continue
            accepted+=1
            r=render_scene(t,build_scene(t,values))
            self.assertEqual((r.width,r.height),(653,313))
            self.assertLess(r.byte_length,5*1024*1024)
            for l in r.scene.labels:
                x0,y0,x1,y1=(n*2 for n in l.box);a,b,c,d=l.ink_box
                self.assertTrue(x0<=a<c<=x1 and y0<=b<d<=y1)
        self.assertEqual(seen,234)
        self.assertGreater(accepted,0)


if __name__=='__main__':
    unittest.main()
