"""Run an isolated synthetic scientific check, never reads a database or dotenv."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.irt.synthetic import generate
from numora_service.irt.producer import run
from numora_service.irt.runner import run as run_r


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--image',required=True)
    parser.add_argument('--per-arm',type=int,default=1000)
    parser.add_argument('--seed',type=int,default=20261109)
    parser.add_argument('--arms',type=int,choices=[2,3],default=2)
    parser.add_argument('--model',choices=['MIXED','2PL','GPCM'],default='MIXED')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    image=subprocess.check_output(['docker','image','inspect',args.image,'--format','{{.Id}}'],text=True).strip()
    value,truth=generate(args.per_arm,args.seed,args.model,args.arms)
    dispatch={'executionId':'55555555-5555-4555-8555-555555555555','dispatchGeneration':1}
    started=time.monotonic()
    result,diagnostics=run(value,dispatch,lambda work:run_r(work,image=image))
    report={'image':image,'elapsedSeconds':time.monotonic()-started,'result':result,'diagnostics':diagnostics,'truth':truth}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,allow_nan=False),encoding='utf-8')
    print(json.dumps({'state':result['outcome']['measurementState'],'scored':sum(p['status']=='SCORED' for p in result['outcome']['respondents']),
        'converged':diagnostics.get('converged'),'seconds':report['elapsedSeconds']}))


if __name__=='__main__':main()
