"""Bounded scientific failure metadata; never persist arbitrary R error text."""
import re


class EngineExecutionError(ValueError):
    def __init__(self, output):
        super().__init__('INTERNAL_ERROR')
        stage=output.get('engineStage')
        allowed=isinstance(stage,str) and re.fullmatch(
            r'FIT|COVARIANCE|ANCHOR_RELEASE|GROUP_[1-3]|GROUP_FIT_[1-3]|PARAMETER_[1-3]_[1-9][0-9]?',stage)
        failure=output.get('scientificFailure')
        self.diagnostics={'failureCode':'INTERNAL_ERROR','engineErrorPresent':True,
            'engineStage':stage if allowed else 'UNKNOWN',
            'scientificFailure':failure if failure in ['MODEL_CONVERGENCE_FAILED','INVALID_COVARIANCE'] else 'UNKNOWN'}
