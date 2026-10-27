import io
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from image_variants import ImageVariantError, build_scene, load_template, render_scene
except ImportError:
    ImageVariantError = None


class DiceImageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(ImageVariantError, 'Image renderer is not implemented')

    def test_repeated_dice_labels_bind_times(self):
        t = load_template('tryout-1-b4-q05')
        for n in (72, 180, 612, 720):
            with self.subTest(times=n):
                s = build_scene(t, {'times': n, 'threshold': 12})
                labels = {label.id: label.text for label in s.labels}
                self.assertEqual(labels['card_count'], str(n))
                self.assertEqual(labels['trial_caption'], f'Banyak Percobaan\n(n) = {n} kali')
                self.assertIn(str(n), s.alt_text)
                self.assertNotIn('threshold', dict(s.bindings))

    def test_threshold_does_not_change_dice_pixels(self):
        t = load_template('tryout-1-b4-q05')
        a = render_scene(t, build_scene(t, {'times': 180, 'threshold': 8}))
        b = render_scene(t, build_scene(t, {'times': 180, 'threshold': 12}))
        self.assertEqual(a.png_bytes, b.png_bytes)
        self.assertEqual(a.provenance['artifact_id'], b.provenance['artifact_id'])

    def test_card_and_caption_both_change_pixels(self):
        t = load_template('tryout-1-b4-q05')
        a = Image.open(io.BytesIO(render_scene(t, build_scene(t, {'times': 72})).png_bytes))
        b = Image.open(io.BytesIO(render_scene(t, build_scene(t, {'times': 720})).png_bytes))
        for label in t.labels:
            self.assertIsNotNone(ImageChops.difference(a.crop(label.box), b.crop(label.box)).getbbox())


if __name__ == '__main__':
    unittest.main()
