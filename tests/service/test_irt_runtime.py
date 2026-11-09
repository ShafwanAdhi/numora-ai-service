from copy import deepcopy
import unittest
from unittest.mock import patch
from numora_service.irt.runtime import profile,validate


class RuntimeTests(unittest.TestCase):
    def test_exact_tested_environment_is_accepted(self):
        validate(profile())

    def test_changed_profile_or_dependency_is_rejected(self):
        changed=deepcopy(profile());changed['image']='sha256:'+'a'*64
        with self.assertRaisesRegex(ValueError,'POLICY_UNAVAILABLE'):validate(changed)
        with patch('numora_service.irt.runtime.version',return_value='0.0.0'):
            with self.assertRaisesRegex(ValueError,'POLICY_UNAVAILABLE'):validate(profile())
