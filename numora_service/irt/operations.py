"""Private worker heartbeat and sanitized operational readiness; no estimates."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import threading
import time
from .runtime import profile, validate


def database_ready(repository):
    with repository.connection() as db:
        repository.check_role(db)
        for relation in ('public.irt_calibration_inputs_v1','irt_compute.calibration_jobs_v1','irt_compute.calibration_artifacts_v1'):
            db.execute('SELECT 1 FROM '+relation+' LIMIT 0')


def metrics(repository):
    with repository.connection() as db:
        repository.check_role(db)
        return dict(db.execute("""SELECT
            count(*) FILTER(WHERE j.status='ACCEPTED') AS backlog,
            coalesce(max(extract(epoch FROM clock_timestamp()-j.created_at)) FILTER(WHERE j.status='ACCEPTED'),0)::float8 AS oldest_pending_seconds,
            count(*) FILTER(WHERE j.status='RUNNING') AS running,
            count(*) FILTER(WHERE j.status='RUNNING' AND j.lease_expires_at<=clock_timestamp()) AS expired_leases,
            coalesce(max(extract(epoch FROM clock_timestamp()-j.heartbeat_at)) FILTER(WHERE j.status='RUNNING'),0)::float8 AS oldest_heartbeat_seconds,
            count(*) FILTER(WHERE j.failure_code='TIMEOUT') AS timeouts,
            count(*) FILTER(WHERE j.generation>1) AS retry_executions,
            count(*) FILTER(WHERE j.status IN ('FAILED','EXPIRED')) AS technical_failures,
            count(*) FILTER(WHERE j.status IN ('ACCEPTED','RUNNING') AND (s.body#>>'{window,resultDueAt}')::timestamptz<=clock_timestamp()+interval '6 hours') AS deadline_within_six_hours
            FROM irt_compute.calibration_jobs_v1 j JOIN public.irt_calibration_inputs_v1 s ON s.id=j.request_id
            WHERE j.generation=s.current_generation""").fetchone())


def heartbeat_path():
    path=Path(os.environ.get('NUMORA_IRT_WORKER_HEARTBEAT',''))
    if not path.is_absolute():raise ValueError('WORKER_HEARTBEAT_NOT_CONFIGURED')
    return path


def readiness(repository):
    try:
        runtime=profile()
        validate(runtime)
    except Exception:return 'RUNTIME_NOT_READY'
    try:database_ready(repository)
    except Exception:return 'DATABASE_NOT_READY'
    try:
        value=json.loads(heartbeat_path().read_text())
        age=time.time()-value['at']
        if value['profile']!=runtime['version'] or value['status']!='ready' or not 0<=age<45:
            return 'WORKER_NOT_READY'
    except Exception:return 'WORKER_NOT_READY'
    return None


@contextmanager
def worker_health(repository,shutdown):
    path=heartbeat_path()
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    stop=threading.Event()
    runtime=profile()
    validate(runtime)
    # API has no Docker socket; only worker verifies the server-pinned R image.
    result=subprocess.run(['docker','image','inspect','--format','{{.Id}}',runtime['image']],capture_output=True,text=True,timeout=10,check=True)
    if result.stdout.strip()!=runtime['image']:raise ValueError('RUNTIME_NOT_READY')
    def write():
        status='blocked'
        try:
            database_ready(repository)
            if not shutdown.is_set():status='ready'
        except Exception:pass
        temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'at':time.time(),'profile':runtime['version'],'status':status}))
        os.replace(temporary,path)
    def pulse():
        while not stop.wait(10):
            try:write()
            except Exception:pass
    write()
    thread=threading.Thread(target=pulse,daemon=True,name='irt-readiness')
    thread.start()
    try:yield
    finally:
        stop.set();thread.join(timeout=10)
        path.unlink(missing_ok=True)
