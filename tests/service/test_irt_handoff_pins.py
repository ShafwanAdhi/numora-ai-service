"""Exact profile bytes must reproduce from Git, never normalized at verification."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tools import verify_irt_linux as verifier

ROOT = Path(__file__).resolve().parents[2]


class HandoffPinTests(unittest.TestCase):
    def test_manifest_matches_checkout_and_git_blob(self):
        manifest = json.loads((ROOT / 'research/irt-linux-image-v2.json').read_text())
        raw = (ROOT / manifest['profile']).read_bytes()
        blob = subprocess.run(['git', 'show', 'HEAD:' + manifest['profile']], cwd=ROOT,
                              capture_output=True, check=True).stdout
        self.assertNotIn(b'\r', raw)
        self.assertEqual(raw, blob)
        self.assertEqual(hashlib.sha256(blob).hexdigest(), manifest['profileSha256'])
        with patch.object(verifier, 'command', return_value=manifest['producerImage']):
            verifier.verify_sources(manifest, json.loads(raw))

    def test_changed_or_crlf_profile_is_rejected_without_docker(self):
        for raw in [b'{"a":1}\n', b'{"a":1}\r\n']:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'profile.json').write_bytes(raw)
                manifest = {'profile': 'profile.json',
                            'profileSha256': hashlib.sha256(b'{"a":0}\n').hexdigest()}
                with patch.object(verifier, 'ROOT', root), patch.object(verifier, 'command') as docker:
                    with self.assertRaisesRegex(ValueError, 'Profile digest changed'):
                        verifier.verify_sources(manifest, {})
                    docker.assert_not_called()

    def test_historical_manifest_and_runtime_semantics_are_preserved(self):
        old = json.loads((ROOT / 'research/irt-linux-image-v1.json').read_text())
        new = json.loads((ROOT / 'research/irt-linux-image-v2.json').read_text())
        raw = (ROOT / old['profile']).read_bytes()
        self.assertEqual(hashlib.sha256(raw.replace(b'\n', b'\r\n')).hexdigest(), old['profileSha256'])
        for key in ['producerImage', 'rImage', 'profile', 'sourceSha256']:
            self.assertEqual(old[key], new[key])


if __name__ == '__main__':
    unittest.main()
