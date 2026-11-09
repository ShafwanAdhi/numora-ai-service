"""Resumable 30-replication synthetic recovery experiment; explicit pinned image."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from numora_service.irt.math import convert,eap,posterior_grid
from research.irt.synthetic import generate


def summarize(folder):
    difficulty=[];log_a=[];steps=[];theta=[];covered=[];theta_covered=[];gates=Counter();failures=Counter();elapsed=[]
    for file in sorted(folder.glob('replication-*.json')):
        report=json.loads(file.read_text());truth=report['truth'];diagnostics=report['diagnostics']
        elapsed.append(report['elapsedSeconds']);parameters=diagnostics.get('estimates',{})
        if not diagnostics.get('converged'):failures[diagnostics.get('scientificFailure','NOT_CONVERGED')]+=1
        converted={}
        for qid,estimate in parameters.items():
            values,errors=convert(estimate['a'],estimate['intercepts'],estimate['covariance'])
            true_a,true_steps=truth['items'][qid]
            converted[qid]=(estimate['a'],values)
            log_a.append(math.log(estimate['a']/true_a))
            for value,target,se in zip(values,true_steps,errors):
                (difficulty if len(values)==1 else steps).append(value-target)
                covered.append(abs(value-target)<=1.96*se)
        for person in report['result']['outcome']['respondents']:
            gates['participant:'+person['status']]+=1
        if diagnostics.get('converged') and converted:
            # Recovery evidence is separate from adopted/scored participant results.
            # Include all identifiable simulated attempts, avoiding gate-selection bias.
            value,_=generate(truth['perArm'],truth['seed'],truth['design'])
            observations={p['attemptId']:[] for p in value['respondents']}
            for response in value['responses']:
                if response['questionVersionId'] in converted:
                    observations[response['attemptId']].append((response['questionVersionId'],response['scoreCategory']))
            grid=posterior_grid(converted,241)
            for aid,obs in observations.items():
                if not obs:continue
                estimate,sd=eap(obs,converted,prepared=grid)
                error=estimate-truth['theta'][aid];theta.append(error);theta_covered.append(abs(error)<=1.96*sd)
        for item in report['result']['outcome']['items']:
            gates.update(item['reasonCodes'])
    def rmse(values):return math.sqrt(sum(x*x for x in values)/len(values)) if values else None
    result={'replications':len(elapsed),'difficultyBias':sum(difficulty)/len(difficulty) if difficulty else None,
        'difficultyRMSE':rmse(difficulty),'logDiscriminationRMSE':rmse(log_a),'stepRMSE':rmse(steps),'thetaRMSE':rmse(theta),
        'difficultyStep95Coverage':sum(covered)/len(covered) if covered else None,
        'thetaConditional95Coverage':sum(theta_covered)/len(theta_covered) if theta_covered else None,
        'thetaRecoveryScope':'ALL_IDENTIFIED_SIMULATED_ATTEMPTS_RESEARCH_ONLY',
        'gateDistribution':dict(gates),'failureDistribution':dict(failures),'elapsedSeconds':elapsed}
    result['accepted']=result['replications']==30 and not failures and all(result[k] is not None and abs(result[k])<=v for k,v in
        {'difficultyBias':.15,'difficultyRMSE':.35,'logDiscriminationRMSE':.25,'stepRMSE':.45,'thetaRMSE':.65}.items())
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--replications',type=int,default=30);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    image=subprocess.check_output(['docker','image','inspect',args.image,'--format','{{.Id}}'],text=True).strip()
    for index in range(args.replications):
        file=args.output/f'replication-{index+1:02}.json'
        if file.exists():
            previous=json.loads(file.read_text())
            if previous['image']!=image:raise SystemExit('Image changed; choose a new output directory')
            continue
        subprocess.run([sys.executable,str(ROOT/'tools/run_irt_research.py'),'--image',image,
            '--seed',str(20261109+index),'--output',str(file)],check=True)
        print(f'Replication {index+1}/{args.replications} complete',flush=True)
    result=summarize(args.output)
    (args.output/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if not result['accepted']:raise SystemExit(1)


if __name__=='__main__':main()
