"""Numerical Drill images use pinned accepted values, never a new question draw."""
import copy
import hashlib
import io
import json
import math
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cli
from bank import load_workspace_bank
from config_store import ConfigStore
from engine import Result, assemble, build_values, make_record, original_record
from filters import validate_candidate
from image_variants import ImageVariantError, build_scene, render_scene
from drill_images import IDS, load_template, preview, render_accepted, render_original


class DrillNumericImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = load_workspace_bank(ROOT / 'data/q0_bank.csv')
        cls.configs = ConfigStore(ROOT / 'configs')

    def candidate(self, qid, k):
        original = self.bank.get(qid)
        cfg, cfg_hash = self.configs.load(qid)
        values = build_values(cfg, lambda name, spec: k)
        result = Result(values, assemble(cfg, values), 1, {})
        record = make_record(original, cfg, cfg_hash, 123, 1, result)
        return original, cfg, result, record

    def test_five_originals_use_original_records_without_random_draws(self):
        self.assertEqual(len(IDS), 5)
        for qid in IDS:
            with self.subTest(qid=qid), patch('cli.generate', side_effect=AssertionError('No original draw')):
                record, image = preview(self.bank, self.configs, qid, 0)
                self.assertEqual(record, original_record(self.bank.get(qid)))
                self.assertEqual(image.provenance['content']['mode'], 'original')
                self.assertEqual(hashlib.sha256(image.png_bytes).hexdigest(), image.sha256)
                from PIL import Image
                with Image.open(io.BytesIO(image.png_bytes)) as png:
                    self.assertEqual(png.size, (image.width, image.height))

    def test_all_150_candidates_match_input_dimensions_and_remain_unchanged(self):
        for qid in IDS:
            for k in range(1, 31):
                with self.subTest(qid=qid, k=k):
                    original, cfg, result, record = self.candidate(qid, k)
                    self.assertEqual(validate_candidate(result.cand, original, []), [])
                    before = copy.deepcopy((original, cfg, result, record))
                    image = render_accepted(original, cfg, result, record)
                    self.assertEqual(before, (original, cfg, result, record))
                    bound = dict(image.scene.bindings)
                    scale = k + 1
                    expected = {
                        'pg-16-4-1': {'radius': 7*scale, 'height': 10*scale, 'wrap': 44*scale},
                        'pg-16-4-3': {'radius': 14*scale, 'slant': 20*scale, 'angle': 252},
                        'pg-16-4-4': {'side': 12*scale, 'face_height': 10*scale},
                        'pg-16-5-3': {'slant': 12*scale, 'angle': 150},
                        'pg-16-5-5': {'side': 10*scale, 'face_height': 13*scale},
                    }[qid]
                    self.assertEqual(bound, expected)
                    if qid == 'pg-16-5-5':
                        self.assertNotEqual(bound['face_height'], result.values['v9'])
                        self.assertEqual(record['key'], 'C')
                    if qid == 'pg-16-5-3':
                        self.assertNotIn('radius', bound)
                        self.assertNotIn('jari-jari alas', image.scene.alt_text.lower())

    def test_generator_callback_draws_once_and_returns_identical_record(self):
        for qid in IDS:
            with self.subTest(qid=qid), patch('cli.generate', wraps=cli.generate) as generate:
                record, image = preview(self.bank, self.configs, qid, 7)
                self.assertEqual(generate.call_count, 1)
            expected = cli.preview(self.bank, self.configs, qid, 7)
            record.pop('created_at'); expected.pop('created_at')
            self.assertEqual(record, expected)
            self.assertEqual(image.provenance['content']['config_hash'], record['config_hash'])

    def test_render_failure_does_not_reroll_or_fall_back(self):
        with patch('cli.generate', wraps=cli.generate) as generate, patch(
                'drill_images.adapter.render_scene', side_effect=ImageVariantError('layout failed')):
            with self.assertRaisesRegex(ImageVariantError, 'layout failed'):
                preview(self.bank, self.configs, IDS[0], 7)
            self.assertEqual(generate.call_count, 1)

    def test_pin_mismatches_fail_for_original_config_and_record(self):
        original, cfg, result, record = self.candidate('pg-16-4-1', 1)
        changed_original = copy.deepcopy(original)
        changed_original['metadata']['original_explanation'] += ' Changed.'
        changed_config = copy.deepcopy(cfg)
        changed_config['variables']['k']['range'][1] = 31
        changed_record = copy.deepcopy(record); changed_record['stem'] += ' Changed.'
        for args in ((changed_original, cfg, result, record),
                     (original, changed_config, result, record),
                     (original, cfg, result, changed_record)):
            with self.assertRaises(ImageVariantError):
                render_accepted(*args)

    def test_invalid_exact_values_rejected(self):
        for bad in (True, 1.0, Fraction(3, 2), 0, 31):
            original, cfg, result, record = self.candidate('pg-16-4-1', 1)
            result.values['k'] = bad
            with self.assertRaises(ImageVariantError):
                render_accepted(original, cfg, result, record)
        original, cfg, result, record = self.candidate('pg-16-4-1', 1)
        result.values['v0'] = 14.0
        with self.assertRaises(ImageVariantError):
            render_accepted(original, cfg, result, record)

    def test_templates_are_integrity_checked_and_no_conceptual_fallback(self):
        for qid in ('../pg-16-4-1', 'pg-16-4-2', 'tryout-1-b3-q02'):
            with self.assertRaises(ImageVariantError): load_template(qid)
        contract = load_template('pg-16-4-1')
        image_template = contract.image
        with self.assertRaises(ImageVariantError):
            build_scene(replace(image_template, base_bytes=b'bad'), {'radius': 7, 'height': 10})
        with self.assertRaises(ImageVariantError):
            load_template('pg-16-4-1', 2)

    def test_repeat_labels_and_original_key_are_preserved(self):
        record, image = preview(self.bank, self.configs, 'pg-16-5-3', 0)
        texts = {label.id: label.text for label in image.scene.labels}
        self.assertEqual(texts['slant_left'], texts['slant_right'])
        self.assertIn('12', texts['slant_left'])
        record, image = preview(self.bank, self.configs, 'pg-16-5-5', 0)
        self.assertEqual(record['key'], 'D')
        self.assertEqual(dict(image.scene.bindings)['face_height'], 13)

    def test_determinism_and_unchanged_background_outside_label_regions(self):
        from PIL import Image, ImageChops
        for qid in IDS:
            with self.subTest(qid=qid):
                args = self.candidate(qid, 30)
                a, b = render_accepted(*args), render_accepted(*args)
                self.assertEqual(a.png_bytes, b.png_bytes)
                self.assertEqual(a.provenance, b.provenance)
                first = render_accepted(*self.candidate(qid, 1))
                diff = ImageChops.difference(Image.open(io.BytesIO(a.png_bytes)).convert('RGB'),
                                            Image.open(io.BytesIO(first.png_bytes)).convert('RGB'))
                for label in a.scene.labels:
                    x0, y0, x1, y1 = label.box
                    diff.paste((0, 0, 0), (max(0, x0-3), max(0, y0-3),
                                          min(a.width, x1+3), min(a.height, y1+3)))
                self.assertIsNone(diff.getbbox())

    def test_longest_cone_radius_label_does_not_touch_circle_outline(self):
        image = render_accepted(*self.candidate('pg-16-4-3', 30))
        label = next(label for label in image.scene.labels if label.id == 'radius')
        x0, y0, x1, y1 = (coordinate/2 for coordinate in label.ink_box)
        for point in ((x0,y0), (x1,y0), (x1,y1), (x0,y1)):
            self.assertLess(math.dist(point, (760,410)), 130)

    def test_alt_text_does_not_answer_pyramid_statements(self):
        for seed in (0,7):
            _, image = preview(self.bank,self.configs,'pg-16-5-5',seed)
            self.assertNotIn('bukan tinggi limas', image.scene.alt_text.lower())
            self.assertNotIn('benar', image.scene.alt_text.lower())

    def test_changed_template_requires_a_new_reviewed_pin(self):
        qid='pg-16-4-1'
        with tempfile.TemporaryDirectory() as temporary:
            folder=Path(temporary)
            shutil.copytree(ROOT/'image_templates/fonts',folder/'fonts')
            shutil.copytree(ROOT/'image_templates'/qid,folder/qid)
            path=folder/qid/'v1/template.json'
            data=json.loads(path.read_text(encoding='utf-8'))
            data['alt_text']='A different description under the old version'
            path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            with patch('drill_images.templates.TEMPLATES',folder):
                with self.assertRaisesRegex(ImageVariantError,'reviewed template'):
                    load_template(qid)

    def test_renderer_drift_requires_review(self):
        from image_variants.renderer import renderer_identity
        changed={**renderer_identity(),'code_sha256':'0'*64}
        with patch('image_variants.renderer.renderer_identity',return_value=changed):
            with self.assertRaisesRegex(ImageVariantError,'renderer pin'):
                load_template('pg-16-4-1')

    def test_exact_config_file_pin_rejects_whitespace_only_drift(self):
        from drill_images.adapter import verify_content
        original=self.bank.get('pg-16-4-1');config,_=self.configs.load(original['id'])
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'v1.json'
            path.write_bytes((ROOT/'configs/pg-16-4-1/v1.json').read_bytes()+b'\n')
            with self.assertRaisesRegex(ImageVariantError,'config file pin'):
                verify_content(load_template(original['id']),original,config,config_path=path)

    def test_preview_has_no_network_database_or_file_writes(self):
        import builtins
        real_open=builtins.open;real_path_open=Path.open
        def guarded_open(file,mode='r',*args,**kwargs):
            if any(flag in mode for flag in 'wax+'):
                raise AssertionError('Runtime image preview attempted a write')
            return real_open(file,mode,*args,**kwargs)
        def guarded_path_open(path,mode='r',*args,**kwargs):
            if any(flag in mode for flag in 'wax+'):
                raise AssertionError('Runtime image preview attempted a Path write')
            return real_path_open(path,mode,*args,**kwargs)
        with patch('builtins.open',guarded_open),patch.object(Path,'open',guarded_path_open),patch(
                'socket.socket',side_effect=AssertionError('No network')),patch(
                'database.connection',side_effect=AssertionError('No database')):
            for seed in (0,7):
                record,image=preview(self.bank,self.configs,'pg-16-4-1',seed)
                self.assertTrue(image.png_bytes)


if __name__ == '__main__':
    unittest.main()
