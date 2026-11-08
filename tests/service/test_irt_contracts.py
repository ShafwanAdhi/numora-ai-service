import json
import unittest
from pathlib import Path

from numora_service.irt_contracts import validate_input, validate_result

ROOT = Path(__file__).resolve().parents[2] / 'contracts/irt-calibration-v1'


class IrtContractBoundaryTests(unittest.TestCase):
    def test_service_imports_calibration_contract_without_starting_worker(self):
        read = lambda name: json.loads((ROOT / name).read_text(encoding='utf-8'))
        value = read('examples/tryout-input.json')
        self.assertIs(validate_input(value), value)
        output = read('examples/tryout-mixed-result.json')
        self.assertIs(validate_result(output, value, read('dispatch.fixture.json')), output)

    def test_service_rejects_legacy_generator_notification_as_calibration_input(self):
        with self.assertRaisesRegex(ValueError, '^IRT_SCHEMA_INVALID$'):
            validate_input({'contractVersion': 3, 'requestId': 'not-an-irt-snapshot'})
