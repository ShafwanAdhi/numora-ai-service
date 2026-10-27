"""Stage-one provenance checks; no renderer or generator behavior changes."""
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    'inventory', Path(__file__).with_name('drill_image_inventory.py'))
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_relationship_name_is_not_image_identity(self):
        def source(target):
            stream = BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                archive.writestr('word/document.xml', '''<w:document
                    xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
                    <w:body><w:p><w:r><w:t>Soal 1</w:t><a:blip r:embed="rId4"/>
                    </w:r></w:p></w:body></w:document>''')
                archive.writestr('word/_rels/document.xml.rels',
                    '<Relationships><Relationship Id="rId4" Target="media/' + target + '"/></Relationships>')
                archive.writestr('word/media/' + target, b'same-image-content')
            return inventory.read_docx(stream.getvalue())
        first, second = source('image1.png'), source('renamed.png')
        self.assertNotEqual(first['placements'][0]['file'], second['placements'][0]['file'])
        self.assertEqual(first['placements'][0]['sha256'], second['placements'][0]['sha256'])
        self.assertEqual(first['placements'][0]['paragraph_index'], 0)

    def test_snapshot_detects_modified_added_and_missing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / 'variant_gen/configs/example'
            folder.mkdir(parents=True)
            first = folder / 'v1.json'
            first.write_text('{}')
            before = inventory.protected_snapshot(root)
            self.assertEqual(inventory.compare_snapshot(root, before), [])
            first.write_text('{"changed":true}')
            self.assertTrue(inventory.compare_snapshot(root, before))
            first.unlink()
            (folder / 'v2.json').write_text('{}')
            changes = inventory.compare_snapshot(root, before)
            self.assertTrue(any('v1.json' in item for item in changes))
            self.assertTrue(any('v2.json' in item for item in changes))

    def test_ambiguous_source_owner_is_not_silently_selected(self):
        questions = [dict(paragraph_start_index=0, source_indicator=17, source_level=2,
                          source_question_number=10, source_occurrence=1),
                     dict(paragraph_start_index=0, source_indicator=17, source_level=2,
                          source_question_number=10, source_occurrence=2)]
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            inventory.question_owner(questions, 2)


if __name__ == '__main__':
    unittest.main()
