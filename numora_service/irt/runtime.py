"""Explicit research runtime pin. Environment drift requires a new profile."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import os

ROOT=Path(__file__).resolve().parents[2]


def profile():
    names={'windows-v4':'irt-runtime-windows-v4.json','linux-v1':'irt-runtime-linux-v1.json'}
    selected=os.environ.get('NUMORA_IRT_RUNTIME_PROFILE','windows-v4')
    if selected not in names:raise ValueError('POLICY_UNAVAILABLE')
    return json.loads((ROOT/'research'/names[selected]).read_text(encoding='utf-8'))


def validate(value):
    expected=profile()
    candidate=dict(value)
    key=candidate.pop('pseudonymKeyVersion',None)
    if key is not None and (not isinstance(key,str) or not key):raise ValueError('POLICY_UNAVAILABLE')
    if candidate!=expected:raise ValueError('POLICY_UNAVAILABLE')
    runtime=expected['producerRuntime']
    if expected.get('producerImage') and os.environ.get('NUMORA_IRT_PRODUCER_IMAGE')!=expected['producerImage']:
        raise ValueError('POLICY_UNAVAILABLE')
    if (platform.python_version(),platform.system(),platform.machine())!=(runtime['python'],runtime['system'],runtime['machine']):
        raise ValueError('POLICY_UNAVAILABLE')
    for name,pin in runtime['dependencies'].items():
        if version(name)!=pin:raise ValueError('POLICY_UNAVAILABLE')
    for name,pin in expected['sourceSha256'].items():
        actual=hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        if actual!=pin:raise ValueError('POLICY_UNAVAILABLE')
