"""Single-worker durable research daemon; no FastAPI background-task queue."""
from copy import deepcopy
from datetime import datetime,timezone
import logging
import time
from .producer import run
from .runner import run as run_r
from .repository import Repository
from ..settings import Settings

LOG=logging.getLogger('numora.irt')


def execute_once(repository,runner=run_r):
    claim=repository.claim_next()
    if claim is None:return False
    job,source,notification=claim
    dispatch={'executionId':str(job['execution_id']),'dispatchGeneration':job['generation']}
    started=time.monotonic()
    last_heartbeat=None
    def heartbeat():
        nonlocal last_heartbeat
        now=time.monotonic()
        if now-started>=900:raise ValueError('TIMEOUT')
        if last_heartbeat is None or now-last_heartbeat>=15:
            repository.heartbeat(job,notification)
            last_heartbeat=time.monotonic()
    try:
        result,diagnostics=run(source['payload'],dispatch,lambda work:runner(work,
            heartbeat=heartbeat,image=source['runtime_profile']['image']),heartbeat=heartbeat)
    except Exception as error:
        code=str(error) if isinstance(error,ValueError) else 'INTERNAL_ERROR'
        if code not in ['TIMEOUT','DEPENDENCY_UNAVAILABLE','INVALID_INPUT','INPUT_DIGEST_MISMATCH','POLICY_UNAVAILABLE','UNSUPPORTED_CONTRACT']:
            code='INTERNAL_ERROR'
        result={k:deepcopy(source['payload'][k]) for k in ['contractVersion','requestId','snapshotId','inputDigest','calibrationId','context']}
        result.update(**dispatch,completedAt=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),executionStatus='FAILED',failure={'code':code,'retryable':code in ['TIMEOUT','DEPENDENCY_UNAVAILABLE']},outcome=None)
        diagnostics={'failureCode':code}
    repository.persist(job,source,notification,result,diagnostics)
    LOG.info('request_id=%s generation=%s status=%s',notification['requestId'],job['generation'],result['executionStatus'])
    return True


def main():
    import os
    if os.environ.get('NUMORA_IRT_RESEARCH_ENABLED')!='true':raise SystemExit('IRT_RESEARCH_DISABLED')
    from .api import settings_from_env
    repository=Repository(settings_from_env())
    while True:
        try:
            if not execute_once(repository):time.sleep(1)
        except Exception:
            LOG.warning('IRT_JOB_INTERRUPTED')
            time.sleep(1)


if __name__=='__main__':main()
