"""Check cross-repo handoff byte parity, contracts and pinned local sources."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def check(main):
    pairs=[('docs/IRT_AI_HANDOFF.md','docs/IRT_AI_HANDOFF.md'),
        ('research/irt/README.md','docs/IRT_RESEARCH_RUNTIME.md'),
        ('research/irt/acceptance-report-v1.json','docs/IRT_RESEARCH_ACCEPTANCE_V1.json'),
        ('research/irt/outcome-acceptance-v1.json','docs/IRT_OUTCOME_ACCEPTANCE_V1.json'),
        ('research/irt/linux-acceptance-v1.json','docs/IRT_LINUX_ACCEPTANCE_V1.json')]
    for left,right in pairs:
        if (ROOT/left).read_bytes()!=(main/right).read_bytes():raise ValueError('Handoff parity mismatch: '+left)
    count=0
    for name in ['irt-calibration-v1','irt-calibration-service-v1']:
        local=ROOT/'contracts'/name;remote=main/'packages/contracts'/name
        files=lambda root:{p.relative_to(root) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
        if files(local)!=files(remote):raise ValueError('Contract file set mismatch: '+name)
        for file in files(local):
            if (local/file).read_bytes()!=(remote/file).read_bytes():raise ValueError('Contract mismatch: '+name+'/'+str(file))
            count+=1
    manifest=json.loads((ROOT/'research/irt-linux-image-v2.json').read_text())
    profile=json.loads((ROOT/manifest['profile']).read_text())
    if hashlib.sha256((ROOT/manifest['profile']).read_bytes()).hexdigest()!=manifest['profileSha256']:
        raise ValueError('Linux profile digest mismatch')
    for name,pin in {**manifest['sourceSha256'],**profile['sourceSha256']}.items():
        if hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=pin:raise ValueError('Source pin mismatch: '+name)
    return {'handoffFiles':len(pairs),'contractFiles':count,'sourcePins':len(profile['sourceSha256']),
            'parity':'PASS','productionApproved':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--main-repo',type=Path,required=True);args=parser.parse_args()
    print(json.dumps(check(args.main_repo),indent=2))
