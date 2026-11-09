"""Bounded no-network R container. Only sanitized numerical work enters R."""
import json
import os
import re
from pathlib import Path, PureWindowsPath
import subprocess
import sys
import tempfile
import time
from uuid import uuid4


def run(work, heartbeat=lambda:None, image=None, timeout=900):
    image = image or os.environ.get('NUMORA_IRT_RESEARCH_IMAGE','')
    if not image.startswith('sha256:') or len(image)!=71:
        raise ValueError('POLICY_UNAVAILABLE')
    name='numora-irt-'+uuid4().hex
    shared=os.environ.get('NUMORA_IRT_WORK_ROOT')
    volume=os.environ.get('NUMORA_IRT_WORK_VOLUME')
    docker_root=os.environ.get('NUMORA_IRT_DOCKER_WORK_ROOT',shared)
    if volume and (not shared or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',volume)):
        raise ValueError('POLICY_UNAVAILABLE')
    if shared and not Path(shared).is_absolute() or docker_root and not shared:
        raise ValueError('POLICY_UNAVAILABLE')
    if docker_root and not (Path(docker_root).is_absolute() or PureWindowsPath(docker_root).is_absolute()):
        raise ValueError('POLICY_UNAVAILABLE')
    with tempfile.TemporaryDirectory(prefix='numora-irt-',dir=shared) as directory:
        folder=Path(directory)
        mount_folder=(docker_root.rstrip('/\\')+'/'+folder.name) if shared else str(folder)
        mount=('type=volume,source='+volume+',target=/work,volume-subpath='+folder.name) if volume else 'type=bind,source='+mount_folder+',target=/work'
        (folder/'input.json').write_text(json.dumps(work,allow_nan=False),encoding='utf-8')
        # stdout/stderr remain private; R data/errors are never echoed into service logs.
        with (folder/'runner.log').open('wb') as log:
            command=['docker','create','--name',name,'--network','none','--read-only',
                '--cap-drop','ALL','--security-opt','no-new-privileges',
                '--cpu-period','100000','--cpu-quota','200000','--memory','2g',
                '--pids-limit','128','--tmpfs','/tmp:rw,nosuid,size=256m',
                '--mount',mount]
            # Linux tempfile directories are 0700. R runs as the producer UID,
            # preserving private files without making them world-readable.
            if hasattr(os,'getuid'):command+=['--user',f'{os.getuid()}:{os.getgid()}']
            command += [image,
                '/work/input.json','/work/output.json']
            started=time.monotonic();next_heartbeat=started
            process=None;created=False
            try:
                # Create before start so cancellation cannot race container creation.
                try:
                    subprocess.run(command,stdout=log,stderr=log,timeout=30,check=True)
                    created=True
                except (subprocess.SubprocessError,OSError):raise ValueError('DEPENDENCY_UNAVAILABLE') from None
                process=subprocess.Popen(['docker','start','--attach',name],stdout=log,stderr=log)
                while process.poll() is None:
                    now=time.monotonic()
                    if now-started>=timeout: raise ValueError('TIMEOUT')
                    if now>=next_heartbeat:
                        heartbeat();next_heartbeat=now+15
                    time.sleep(.2)
                if process.returncode or not (folder/'output.json').exists():
                    raise ValueError('DEPENDENCY_UNAVAILABLE')
                result=json.loads((folder/'output.json').read_text(encoding='utf-8'))
                return result
            finally:
                primary_failure=sys.exc_info()[0] is not None
                cleanup_failed=False
                try:
                    if created:subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20,check=True)
                except (subprocess.SubprocessError,OSError):
                    cleanup_failed=True
                finally:
                    if process is not None and process.poll() is None:
                        try:process.wait(timeout=20)
                        except subprocess.TimeoutExpired:
                            try:
                                process.kill();process.wait(timeout=5)
                            except (subprocess.SubprocessError,OSError):cleanup_failed=True
                # Preserve TIMEOUT/stale authorization so cleanup failure cannot
                # silently turn a retryable failure into INTERNAL_ERROR.
                if cleanup_failed and not primary_failure:raise ValueError('DEPENDENCY_UNAVAILABLE')
