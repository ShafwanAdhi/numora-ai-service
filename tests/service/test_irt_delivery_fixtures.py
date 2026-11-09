"""Mirrored synthetic handoff. No database, R, dispatch or scientific estimates."""
import hashlib
import json
import os
from pathlib import Path
import unittest

from numora_service.irt_contracts import validate_input

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'tests/fixtures/irt-delivery-v1'


class DeliveryFixtureTests(unittest.TestCase):
    def test_mirror_is_identical_to_main_canonical_source(self):
        main = Path(os.environ.get('NUMORA_REPO_PATH', str(ROOT.parent / 'Numora')))
        canonical = main / 'packages/testing/fixtures/irt-delivery-v1'
        files = lambda root: {p.relative_to(root) for p in root.rglob('*') if p.is_file()}
        self.assertEqual(files(FIXTURES), files(canonical))
        for name in files(FIXTURES):
            self.assertEqual((FIXTURES / name).read_bytes(), (canonical / name).read_bytes(), str(name))

    def test_source_and_payload_hashes_match(self):
        recipe = json.loads((FIXTURES / 'recipe.json').read_text())
        for name, pin in recipe['sourceSha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest(), pin)
        manifest = json.loads((FIXTURES / 'small/manifest.json').read_text())
        self.assertEqual(manifest['inputDigests'], 'UNBOUND_UNTIL_POSTGRES_FREEZE')
        self.assertFalse(manifest['productionApproved'])
        for name, pin in manifest['files'].items():
            self.assertEqual(hashlib.sha256((FIXTURES / 'small' / name).read_bytes()).hexdigest(), pin)

    def test_small_payloads_cover_all_question_formats_and_common_anchors(self):
        for name, arms in [('two-arm', 2), ('three-arm-partial', 3)]:
            with self.subTest(case=name):
                value = json.loads((FIXTURES / 'small' / (name + '.input.json')).read_text())
                validate_input(value)
                self.assertEqual(len(value['respondents']), arms * 2)
                self.assertEqual(len(value['responses']), arms * 60)
                self.assertEqual({i['questionType'] for i in value['items']}, {'SINGLE_CHOICE', 'MULTIPLE_CHOICE_MULTIPLE_ANSWER', 'CATEGORY'})
                self.assertEqual(len(set.intersection(*(set(p['questionVersionIds']) for p in value['packages']))), 5)
                self.assertEqual(value['comparisons'], [])
                self.assertIsNone(value['policies']['comparison'])
                self.assertTrue(all(p['assignedArmId'] == p['deliveredArmId'] for p in value['respondents']))
                self.assertFalse({'truth', 'resources', 'fallback'} & value.keys())

    def test_full_design_has_explicit_underpowered_arm_without_relabelling_eligibility(self):
        recipe = json.loads((FIXTURES / 'recipe.json').read_text())
        self.assertEqual([c['perArm'] for c in recipe['cases']], [[1000, 1000], [1000, 1000, 100]])
        resources = json.loads((FIXTURES / 'small/research-resources.json').read_text())
        self.assertEqual(resources['definitions']['quality']['minimumArmCount'], 500)
        self.assertEqual(resources['fallback']['readiness'], 'BLOCKED_UNAPPROVED')
        self.assertFalse(resources['productionApproved'])


if __name__ == '__main__':
    unittest.main()
