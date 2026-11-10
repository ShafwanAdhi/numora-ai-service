import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock,patch
from numora_service.irt import operations
from numora_service.irt.daemon import execute_once,WorkerStopped
from tools.irt_capacity import evaluate


class OperationsTests(unittest.TestCase):
    def test_capacity_counts_full_limits_and_ignores_swap(self):
        self.assertEqual(evaluate(2,1663)['status'],'BLOCKED_CAPACITY')
        self.assertEqual(evaluate(4,4352)['status'],'READY')
        self.assertEqual(evaluate(4,4351)['status'],'BLOCKED_CAPACITY')

    def test_readiness_requires_database_runtime_and_recent_matching_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'worker.json'
            with patch.object(operations,'profile',return_value={'version':'test'}),patch.object(operations,'validate'),patch.object(operations,'database_ready') as database,patch.object(operations,'heartbeat_path',return_value=path):
                self.assertEqual(operations.readiness(Mock()),'WORKER_NOT_READY')
                path.write_text(json.dumps({'at':time.time(),'profile':'test','status':'ready'}))
                self.assertIsNone(operations.readiness(Mock()))
                path.write_text(json.dumps({'at':time.time()-46,'profile':'test','status':'ready'}))
                self.assertEqual(operations.readiness(Mock()),'WORKER_NOT_READY')
                database.side_effect=RuntimeError('secret')
                self.assertEqual(operations.readiness(Mock()),'DATABASE_NOT_READY')

    def test_shutdown_does_not_claim_or_seal(self):
        stop=threading.Event();stop.set();repo=Mock()
        self.assertFalse(execute_once(repo,shutdown=stop));repo.claim_next.assert_not_called()
        stop.clear()
        job={'execution_id':'id','generation':1}
        source={'payload':{},'runtime_profile':{'image':'sha256:test'}}
        repo.claim_next.return_value=(job,source,{'requestId':'id'})
        def producer(value,dispatch,runner,heartbeat):
            stop.set();heartbeat()
        with patch('numora_service.irt.daemon.run',side_effect=producer):
            with self.assertRaises(WorkerStopped):execute_once(repo,shutdown=stop)
        repo.persist.assert_not_called()


if __name__=='__main__':unittest.main()
