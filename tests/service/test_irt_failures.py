import json
import unittest
from numora_service.irt.failures import EngineExecutionError


class EngineFailureTests(unittest.TestCase):
    def test_safe_diagnostics_survive_without_raw_message_or_call(self):
        error=EngineExecutionError({'engineStage':'COVARIANCE','scientificFailure':'MODEL_CONVERGENCE_FAILED',
            'engineError':'secret@example.test','engineCall':'select credentials'})
        self.assertEqual(str(error),'INTERNAL_ERROR')
        self.assertEqual(error.diagnostics['engineStage'],'COVARIANCE')
        self.assertNotIn('secret',json.dumps(error.diagnostics))
        self.assertNotIn('credentials',json.dumps(error.diagnostics))

    def test_untrusted_stage_and_scientific_code_are_not_persisted(self):
        error=EngineExecutionError({'engineStage':'participant@example.test','scientificFailure':'arbitrary input'})
        self.assertEqual(error.diagnostics['engineStage'],'UNKNOWN')
        self.assertEqual(error.diagnostics['scientificFailure'],'UNKNOWN')
