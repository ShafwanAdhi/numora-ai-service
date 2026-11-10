"""Explicit release step after build; never run during service startup."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--producer-image',required=True)
    a=p.parse_args()
    if not re.fullmatch(r'sha256:[0-9a-f]{64}',a.producer_image):p.error('Immutable image ID required')
    for base,name,version in [('windows-v4','windows-v5','irt-research-windows-producer-v5'),('linux-v1','linux-v2','irt-research-linux-producer-v2')]:
        value=json.loads((ROOT/f'research/irt-runtime-{base}.json').read_text())
        value['version']=version
        if name.startswith('linux'):value['producerImage']=a.producer_image
        files=set(value['sourceSha256'])|{'numora_service/irt/operations.py','Dockerfile.irt-producer','tools/irt_capacity.py'}
        value['sourceSha256']={name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in sorted(files)}
        (ROOT/f'research/irt-runtime-{name}.json').write_bytes((json.dumps(value,indent=2)+'\n').encode('utf8'))
    runtime_file=ROOT/'research/irt-runtime-linux-v2.json'
    runtime=json.loads(runtime_file.read_text())
    manifest={'version':'irt-linux-image-manifest-v3','purpose':'RESEARCH_ONLY','productionApproved':False,
              'producerImage':a.producer_image,'rImage':runtime['image'],'profile':'research/irt-runtime-linux-v2.json',
              'profileSha256':hashlib.sha256(runtime_file.read_bytes()).hexdigest(),
              'profileHashRecipe':'SHA256_EXACT_UTF8_LF_BYTES','runtimeSelection':'linux-v2',
              'supersedes':'research/irt-linux-image-v2.json',
              'revisionReason':'Operational readiness, shutdown and isolated deployment; scientific model and policy unchanged.',
              'sourceSha256':{name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in ['Dockerfile.irt-producer','research/irt-python-linux.lock','tools/verify_irt_linux.py']}}
    (ROOT/'research/irt-linux-image-v3.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf8'))


if __name__=='__main__':main()
