import json
import os
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]


class TransportTests(unittest.TestCase):
    def test_examples_and_schemas(self):
        folder=ROOT/'contracts/irt-calibration-service-v1'
        for name in ['notification','response']:
            Draft202012Validator.check_schema(json.loads((folder/(name+'.schema.json')).read_text()))
        schema=json.loads((folder/'response.schema.json').read_text())
        Draft202012Validator(schema).validate(json.loads((folder/'examples/accepted.json').read_text()))

    def test_repository_byte_parity(self):
        main=Path(os.environ.get('NUMORA_REPO_PATH',str(ROOT.parent/'Numora')))
        other=main/'packages/contracts/irt-calibration-service-v1'
        self.assertTrue(other.is_dir(),'Main contract repository required for compatibility test')
        local=ROOT/'contracts/irt-calibration-service-v1'
        for path in local.rglob('*'):
            if path.is_file():self.assertEqual(path.read_bytes(),(other/path.relative_to(local)).read_bytes(),str(path))


if __name__=='__main__':unittest.main()
