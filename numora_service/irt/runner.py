"""Bounded no-network R container. Only sanitized numerical work enters R."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from uuid import uuid4


def run(work, heartbeat=lambda:None, image=None, timeout=900):
    image = image or os.environ.get('NUMORA_IRT_RESEARCH_IMAGE','')
    if not image.startswith('sha256:') or len(image)!=71:
        raise ValueError('POLICY_UNAVAILABLE')
    name='numora-irt-'+uuid4().hex
    with tempfile.TemporaryDirectory(prefix='numora-irt-') as directory:
        folder=Path(directory)
        (folder/'input.json').write_text(json.dumps(work,allow_nan=False),encoding='utf-8')
        # stdout/stderr remain private; R data/errors are never echoed into service logs.
        with (folder/'runner.log').open('wb') as log:
            command=['docker','run','--rm','--name',name,'--network','none','--read-only',
                '--cap-drop','ALL','--security-opt','no-new-privileges','--cpus','2','--memory','2g',
                '--pids-limit','128','--tmpfs','/tmp:rw,nosuid,size=256m',
                '--mount','type=bind,source='+str(folder)+',target=/work',image,
                '/work/input.json','/work/output.json']
            process=subprocess.Popen(command,stdout=log,stderr=log)
            started=time.monotonic();next_heartbeat=started
            try:
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
                if process.poll() is None:
                    subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20)
                    process.wait(timeout=20)
