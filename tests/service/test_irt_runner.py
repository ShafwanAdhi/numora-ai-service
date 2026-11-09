import json
import os
import subprocess
import unittest
from unittest.mock import patch
from uuid import uuid4
from numora_service.irt.runner import run


@unittest.skipUnless(os.environ.get('IRT_RESEARCH_TEST_IMAGE'),'Pinned Docker R image required')
class RunnerTests(unittest.TestCase):
    def removed(self,identifier):
        result=subprocess.run(['docker','inspect','numora-irt-'+identifier.hex],capture_output=True)
        self.assertNotEqual(result.returncode,0)

    def test_timeout_kills_and_removes_container(self):
        identifier=uuid4()
        with patch('numora_service.irt.runner.uuid4',return_value=identifier):
            with self.assertRaisesRegex(ValueError,'TIMEOUT'):
                run({},image=os.environ['IRT_RESEARCH_TEST_IMAGE'],timeout=.01)
        self.removed(identifier)

    def test_revocation_kills_container_with_expected_isolation(self):
        identifier=uuid4()
        def revoked():
            value=json.loads(subprocess.check_output(['docker','inspect','numora-irt-'+identifier.hex],text=True))[0]
            host=value['HostConfig']
            self.assertEqual(host['NetworkMode'],'none')
            self.assertTrue(host['ReadonlyRootfs'])
            self.assertEqual(host['Memory'],2*1024**3)
            self.assertEqual(host['CpuQuota']/host['CpuPeriod'],2)
            self.assertEqual(value['Config']['User'],'65534:65534')
            self.assertFalse(any('DATABASE' in x for x in value['Config']['Env']))
            raise ValueError('STALE_EXECUTION')
        with patch('numora_service.irt.runner.uuid4',return_value=identifier):
            with self.assertRaisesRegex(ValueError,'STALE_EXECUTION'):
                run({},heartbeat=revoked,image=os.environ['IRT_RESEARCH_TEST_IMAGE'])
        self.removed(identifier)
