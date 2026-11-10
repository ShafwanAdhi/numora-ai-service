"""Single-worker durable research daemon; no FastAPI background-task queue."""
from copy import deepcopy
from datetime import datetime,timezone
import logging
import time
import threading
import signal
from .producer import run
from .runner import run as run_r
from .failures import EngineExecutionError
from .repository import Repository
from .mode import enabled

LOG=logging.getLogger('numora.irt')

class WorkerStopped(BaseException):
    """Exit through runner cleanup without sealing an interrupted execution."""


def execute_once(repository,runner=run_r,shutdown=None):
    if shutdown is not None and shutdown.is_set():return False
    claim=repository.claim_next()
    if claim is None:return False
    job,source,notification=claim
    dispatch={'executionId':str(job['execution_id']),'dispatchGeneration':job['generation']}
    started=time.monotonic()
    stop=threading.Event()
    heartbeat_error=[]
    def heartbeat():
        if shutdown is not None and shutdown.is_set():raise WorkerStopped()
        if time.monotonic()-started>=900:raise ValueError('TIMEOUT')
        if heartbeat_error:raise heartbeat_error[0]
    def pulse():
        while not stop.wait(15):
            if shutdown is not None and shutdown.is_set():return
            try:
                heartbeat()
                repository.heartbeat(job,notification)
            except Exception as error:
                heartbeat_error.append(error)
                return
    repository.heartbeat(job,notification)
    monitor=threading.Thread(target=pulse,daemon=True,name='irt-lease')
    monitor.start()
    try:
        try:
            result,diagnostics=run(source['payload'],dispatch,lambda work:runner(work,
                heartbeat=heartbeat,image=source['runtime_profile']['image']),heartbeat=heartbeat)
            heartbeat()
        except Exception as error:
            code=str(error) if isinstance(error,ValueError) else 'INTERNAL_ERROR'
            if code not in ['TIMEOUT','DEPENDENCY_UNAVAILABLE','INVALID_INPUT','INPUT_DIGEST_MISMATCH','POLICY_UNAVAILABLE','UNSUPPORTED_CONTRACT']:
                code='INTERNAL_ERROR'
            result={k:deepcopy(source['payload'][k]) for k in ['contractVersion','requestId','snapshotId','inputDigest','calibrationId','context']}
            result.update(**dispatch,completedAt=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),executionStatus='FAILED',failure={'code':code,'retryable':code in ['TIMEOUT','DEPENDENCY_UNAVAILABLE']},outcome=None)
            diagnostics={'failureCode':code}
            if isinstance(error,EngineExecutionError):diagnostics.update(error.diagnostics)
        repository.persist(job,source,notification,result,diagnostics)
    finally:
        stop.set();monitor.join(timeout=20)
    LOG.info('request_id=%s generation=%s status=%s',notification['requestId'],job['generation'],result['executionStatus'])
    return True


def main():
    import os
    if not enabled():raise SystemExit('IRT_DISABLED')
    from .api import settings_from_env
    repository=Repository(settings_from_env())
    shutdown=threading.Event()
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *_:shutdown.set())
    from .operations import worker_health
    with worker_health(repository,shutdown):
      while not shutdown.is_set():
        try:
            if not execute_once(repository,shutdown=shutdown):shutdown.wait(1)
        except WorkerStopped:
            break
        except Exception:
            LOG.warning('IRT_JOB_INTERRUPTED')
            shutdown.wait(1)


if __name__=='__main__':main()
