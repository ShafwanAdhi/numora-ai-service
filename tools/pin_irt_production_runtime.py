"""Explicit immutable release step. Never run during startup; never overwrites a profile."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--producer-image',required=True);a=p.parse_args()
    if not re.fullmatch(r'sha256:[0-9a-f]{64}',a.producer_image):p.error('Immutable image ID required')
    targets=[('windows-v5','windows-v6','irt-research-windows-producer-v6','RESEARCH_ONLY'),('linux-v2','linux-v3','irt-research-linux-producer-v3','RESEARCH_ONLY'),('linux-v2','linux-production-v1','irt-production-linux-producer-v1','PRODUCTION')]
    paths=[ROOT/f'research/irt-runtime-{name}.json' for _,name,_,_ in targets]+[ROOT/'research/irt-linux-image-v4.json']
    if any(path.exists() for path in paths):raise SystemExit('IMMUTABLE_PROFILE_ALREADY_EXISTS')
    for base,name,version,purpose in targets:
        value=json.loads((ROOT/f'research/irt-runtime-{base}.json').read_text());value.update(version=version,purpose=purpose)
        if name.startswith('linux'):value['producerImage']=a.producer_image
        files=set(value['sourceSha256'])|{'numora_service/irt/mode.py','research/irt/policy-production-candidate-v1.json'}
        value['sourceSha256']={f:hashlib.sha256((ROOT/f).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for f in sorted(files)}
        (ROOT/f'research/irt-runtime-{name}.json').write_bytes((json.dumps(value,indent=2)+'\n').encode())
    manifest={'version':'irt-linux-image-manifest-v4','purpose':'RESEARCH_ONLY','productionApproved':False,'producerImage':a.producer_image,'rImage':value['image'],'profile':'research/irt-runtime-linux-v3.json','profileSha256':hashlib.sha256(paths[1].read_bytes()).hexdigest(),'runtimeSelection':'linux-v3','productionProfile':'research/irt-runtime-linux-production-v1.json','productionProfileSha256':hashlib.sha256(paths[2].read_bytes()).hexdigest(),'sourceSha256':{f:hashlib.sha256((ROOT/f).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for f in ['Dockerfile.irt-producer','research/irt-python-linux.lock','tools/verify_irt_linux.py']},'supersedes':'research/irt-linux-image-v3.json','revisionReason':'Explicit production authorization boundary; scientific method and thresholds unchanged.'}
    paths[-1].write_bytes((json.dumps(manifest,indent=2)+'\n').encode())


if __name__=='__main__':main()
