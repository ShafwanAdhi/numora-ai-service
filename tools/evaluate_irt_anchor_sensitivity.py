"""Paired sample-size/DIF diagnostics, using the unchanged pinned R image/policy.

Small research experiment, not a new policy or evidence of production equivalence.
Each checkpoint binds all inputs and code pins before it can be resumed.
"""
import argparse
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research.irt.synthetic import generate
from numora_service.irt.gates import anchor_gate
from numora_service.irt.producer import policy,run
from numora_service.irt.runner import run as run_r


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def injected(value,truth,shift):
    value=deepcopy(value)
    if not shift:return value
    qid=value['anchorQuestionVersionIds'][0]
    original=value['packages'][0]['armId']
    people={p['attemptId']:p for p in value['respondents']}
    item=next(i for i in value['items'] if i['questionVersionId']==qid)
    a,steps=truth['items'][qid];rng=random.Random(truth['seed']+71)
    for response in value['responses']:
        if response['questionVersionId']!=qid or people[response['attemptId']]['deliveredArmId']==original:continue
        theta=truth['theta'][response['attemptId']]
        logits=[0.]+[a*(k*theta-sum(steps[:k])-shift*k) for k in range(1,len(steps)+1)]
        weights=[math.exp(x-max(logits)) for x in logits]
        category=rng.choices(range(len(weights)),weights=weights)[0]
        response.update(scoreCategory=category,awardedPoints=str(
            (Decimal(item['maxPoints'])*category/Decimal(item['maximumScoreCategory'])).quantize(Decimal('.01'))))
    return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--image',required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    image=subprocess.check_output(['docker','image','inspect',args.image,'--format','{{.Id}}'],text=True).strip()
    args.output.mkdir(parents=True,exist_ok=True)
    profile=policy();reports=[]
    pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
          for p in [Path(__file__),ROOT/'research/irt/synthetic.py',ROOT/'research/irt/policy-v1.json',
                    ROOT/'numora_service/irt/gates.py',ROOT/'numora_service/irt/producer.py',ROOT/'numora_service/irt/math.py']}
    for n in [500,2000]:
        for shift in [0.,1.3]:
            seed=20261119
            value,truth=generate(n,seed)
            value=injected(value,truth,shift)
            pin={'image':image,'sourceSha256':pins,'inputSha256':digest(value),'perArm':n,'seed':seed,'injectedDifficultyShift':shift}
            file=args.output/f'n{n}-shift{shift}.json'
            if file.exists():
                report=json.loads(file.read_text())
                if report['pin']!=pin:raise ValueError('Checkpoint provenance changed')
            else:
                result,diagnostics=run(value,{'executionId':'55555555-5555-4555-8555-555555555555','dispatchGeneration':1},
                    lambda work:run_r(work,image=image))
                report={'pin':pin,'measurementState':result['outcome']['measurementState'],
                    'participantStatuses':dict(Counter(r['status'] for r in result['outcome']['respondents'])),
                    'converged':diagnostics['converged'],'anchorGate':diagnostics['anchorGate'],
                    'anchors':diagnostics['anchors']}
                file.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            reports.append(report)
            print(json.dumps({k:v for k,v in report.items() if k not in ['anchors','anchorGate','pin']}),flush=True)
    summary={'purpose':'RESEARCH_ONLY','productionApproved':False,'policyChanged':False,'policy':profile,
        'limitations':['One paired seed per sample size; not a detection-rate estimate.',
            'No released-effect confidence intervals; absence of significance is not equivalence.',
            'No policy or threshold selected from this experiment.'],
        'cases':reports}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
