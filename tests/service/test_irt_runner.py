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
            self.assertEqual(value['Config']['User'],f'{os.getuid()}:{os.getgid()}' if hasattr(os,'getuid') else '65534:65534')
            self.assertFalse(any('DATABASE' in x for x in value['Config']['Env']))
            raise ValueError('STALE_EXECUTION')
        with patch('numora_service.irt.runner.uuid4',return_value=identifier):
            with self.assertRaisesRegex(ValueError,'STALE_EXECUTION'):
                run({},heartbeat=revoked,image=os.environ['IRT_RESEARCH_TEST_IMAGE'])
        self.removed(identifier)


class CleanupFailureTests(unittest.TestCase):
    def test_cleanup_timeout_preserves_primary_timeout(self):
        from unittest.mock import Mock
        process=Mock();process.poll.return_value=None
        with patch('numora_service.irt.runner.subprocess.run',side_effect=[subprocess.CompletedProcess([],0),subprocess.TimeoutExpired('docker rm',20)]), patch('numora_service.irt.runner.subprocess.Popen',return_value=process), patch('numora_service.irt.runner.time.monotonic',side_effect=[0,2]):
            with self.assertRaisesRegex(ValueError,'TIMEOUT'):run({},image='sha256:'+'a'*64,timeout=1)
        process.wait.assert_called_once()

    def test_cleanup_timeout_preserves_revocation(self):
        from unittest.mock import Mock
        process=Mock();process.poll.return_value=None
        def revoked():raise ValueError('STALE_EXECUTION')
        with patch('numora_service.irt.runner.subprocess.run',side_effect=[subprocess.CompletedProcess([],0),subprocess.TimeoutExpired('docker rm',20)]), patch('numora_service.irt.runner.subprocess.Popen',return_value=process), patch('numora_service.irt.runner.time.monotonic',side_effect=[0,0]):
            with self.assertRaisesRegex(ValueError,'STALE_EXECUTION'):run({},heartbeat=revoked,image='sha256:'+'a'*64)
