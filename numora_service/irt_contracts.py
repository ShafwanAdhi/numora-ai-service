"""Opt-in IRT payload boundary; this module does not register an HTTP route or worker."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_path = Path(__file__).resolve().parent.parent / 'contracts/irt-calibration-v1/validate.py'
_spec = spec_from_file_location('numora_service._irt_calibration_v1', _path)
if _spec is None or _spec.loader is None:
    raise RuntimeError('IRT_CONTRACT_UNAVAILABLE')
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

validate_input = _module.validate_input
validate_result = _module.validate_result
