from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from tools.verify_irt_linux import memory_mib,verify_sources


class LinuxHarnessTests(unittest.TestCase):
    def test_docker_memory_units_do_not_overstate_precision(self):
        self.assertEqual(memory_mib('1.5GiB / 2GiB'),1536)
        self.assertEqual(memory_mib('512KiB / 2GiB'),.5)
        self.assertAlmostEqual(memory_mib('1MB / 2GB'),1000000/1024**2)

    def test_changed_image_or_profile_cannot_reuse_capacity_evidence(self):
        root=Path(__file__).resolve().parents[2]
        manifest=json.loads((root/'research/irt-linux-image-v1.json').read_text())
        profile=json.loads((root/manifest['profile']).read_text())
        with patch('tools.verify_irt_linux.command',return_value=profile['producerImage']):
            verify_sources(manifest,profile)
        changed=deepcopy(manifest);changed['profileSha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Profile digest'):
            verify_sources(changed,profile)
        with patch('tools.verify_irt_linux.command',return_value='sha256:'+'0'*64):
            with self.assertRaisesRegex(ValueError,'Producer image'):
                verify_sources(manifest,profile)
