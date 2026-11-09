from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from numora_service.bridge import ROOT, workspace
from tools.prepare_original_source_repairs import checked_asset


class OriginalMediaRepairsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank, _ = workspace()
        folder = ROOT / 'docs/audits/2026-10-27-drill-r2-upload'
        cls.assets = json.loads((folder / 'preflight.json').read_text(encoding='utf-8'))['assets']
        cls.receipts = json.loads((folder / 'media-receipts.json').read_text(encoding='utf-8'))

    def test_all_nine_assets_match_current_original_and_receipt(self):
        self.assertEqual(len(self.assets), 9)
        for asset in self.assets:
            qid = asset['externalId']
            result = checked_asset(self.bank.get(qid), asset, self.receipts[qid])
            self.assertEqual(result['placement'], 'STEM')
            self.assertEqual(result['sha256'], asset['sha256'])
            self.assertFalse(any('url' in key.lower() for key in result))

    def test_changed_receipt_or_source_is_rejected(self):
        asset = self.assets[0]
        original = self.bank.get(asset['externalId'])
        receipt = self.receipts[asset['externalId']]
        for field, value in [('sha256', '0'*64), ('status', 'PENDING')]:
            altered = {**receipt, field: value}
            with self.assertRaises(ValueError):
                checked_asset(original, asset, altered)
        with self.assertRaisesRegex(ValueError, 'SOURCE_PIN_MISMATCH'):
            checked_asset({**original, 'version': 999}, asset, receipt)

    def test_corrupted_local_png_is_rejected(self):
        asset = deepcopy(self.assets[0])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset['filePath'] = 'broken.png'
            (root / asset['filePath']).write_bytes(b'broken')
            with self.assertRaisesRegex(ValueError, 'LOCAL_IMAGE_MISMATCH'):
                checked_asset(self.bank.get(asset['externalId']), asset,
                              self.receipts[asset['externalId']], root)


if __name__ == '__main__':
    unittest.main()
