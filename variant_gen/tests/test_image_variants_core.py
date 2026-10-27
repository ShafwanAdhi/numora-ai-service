"""Renderer contract and asset-integrity checks; no files written by rendering."""
import hashlib
import io
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from image_variants import ImageVariantError, build_scene, load_template, render_scene
    from image_variants.renderer import renderer_identity
except ImportError:
    ImageVariantError = None


class ImageCoreTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(ImageVariantError, 'Image renderer is not implemented')

    def test_missing_binding_and_unknown_template_fail(self):
        for qid in ('../secrets', 'https://example.com/image', 'pg-1-1-1'):
            with self.subTest(qid=qid), self.assertRaises(ImageVariantError):
                load_template(qid)
        for version in (True, 0, -1, '../v1'):
            with self.subTest(version=version), self.assertRaises(ImageVariantError):
                load_template('tryout-1-b4-q05', version)
        template = load_template('tryout-1-b4-q05')
        for values in ({}, {'times': True}, {'times': 180.0}, {'times': '180'}, {'times': -1}):
            with self.subTest(values=values), self.assertRaises(ImageVariantError):
                build_scene(template, values)

    def test_png_dimensions_size_and_determinism(self):
        t = load_template('tryout-1-b4-q05')
        scene = build_scene(t, {'times': 612})
        a, b = render_scene(t, scene), render_scene(t, scene)
        self.assertEqual(a.png_bytes, b.png_bytes)
        self.assertEqual(a.sha256, hashlib.sha256(a.png_bytes).hexdigest())
        self.assertEqual(a.byte_length, len(a.png_bytes))
        self.assertLess(a.byte_length, 5 * 1024 * 1024)
        with Image.open(io.BytesIO(a.png_bytes)) as im:
            self.assertEqual(im.format, 'PNG')
            self.assertEqual(im.size, (292, 255))
        self.assertEqual(a.provenance['status'], 'LOCAL_RENDERED')

    def test_corrupt_assets_and_mismatched_scene_fail_closed(self):
        t = load_template('tryout-1-b4-q05')
        s = build_scene(t, {'times': 180})
        for broken in (replace(t, base_bytes=b'broken'), replace(t, font_bytes=b'broken')):
            with self.assertRaises(ImageVariantError):
                render_scene(broken, s)
        with self.assertRaises(ImageVariantError):
            render_scene(t, replace(s, template_sha256='0' * 64))
        with self.assertRaises(ImageVariantError):
            render_scene(t, replace(s, alt_text='stale description'))

    def test_layout_overflow_is_explicit(self):
        t = load_template('tryout-1-b4-q05')
        label = replace(t.labels[0], text='123456789012345678901234567890')
        broken = replace(t, labels=(label, *t.labels[1:]))
        with self.assertRaisesRegex(ImageVariantError, 'fit|layout|integrity'):
            build_scene(broken, {'times': 180})
        with self.assertRaisesRegex(ImageVariantError, 'fit'):
            build_scene(t, {'times': 10**12})

    def test_changed_effective_template_cannot_reuse_identity(self):
        t = load_template('tryout-1-b4-q05')
        changed = replace(t, labels=(replace(t.labels[0], text='999'), *t.labels[1:]))
        with self.assertRaisesRegex(ImageVariantError, 'integrity'):
            render_scene(changed, build_scene(changed, {'times': 180}))

    def test_renderer_pins_formatter_compression_build_and_png(self):
        identity = renderer_identity()
        self.assertEqual(identity['formatter_sha256'], hashlib.sha256((ROOT/'expr.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest())
        self.assertTrue(identity['zlib'])
        self.assertTrue(identity['pillow_core_sha256'])
        t = load_template('tryout-1-b4-q05')
        image = render_scene(t, build_scene(t, {'times': 180}))
        self.assertEqual(image.provenance['png_sha256'], image.sha256)

    def test_pinned_environment_and_template_change_identity(self):
        t = load_template('tryout-1-b4-q05')
        a = render_scene(t, build_scene(t, {'times': 180}))
        with patch('image_variants.renderer.renderer_identity', return_value={**renderer_identity(), 'version': 'future'}):
            b = render_scene(t, build_scene(t, {'times': 180}))
        self.assertNotEqual(a.provenance['artifact_id'], b.provenance['artifact_id'])
        self.assertIn('font_sha256', a.provenance)
        self.assertIn('template_sha256', a.provenance)

    def test_render_changes_only_reviewed_label_regions(self):
        t = load_template('tryout-1-b4-q05')
        a = Image.open(io.BytesIO(render_scene(t, build_scene(t, {'times': 72})).png_bytes)).convert('RGB')
        b = Image.open(io.BytesIO(render_scene(t, build_scene(t, {'times': 612})).png_bytes)).convert('RGB')
        diff = ImageChops.difference(a, b)
        for label in t.labels:
            x0, y0, x1, y1 = label.box
            diff.paste((0, 0, 0), (max(0, x0-3), max(0, y0-3), min(t.width, x1+3), min(t.height, y1+3)))
        self.assertIsNone(diff.getbbox())


if __name__ == '__main__':
    unittest.main()
