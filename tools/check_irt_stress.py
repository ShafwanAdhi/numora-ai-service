"""Engine stress experiments. No contract artifact, policy approval or student result."""
import argparse,json,sys,subprocess,random,math
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.irt.synthetic import generate
from numora_service.irt.producer import policy
from numora_service.irt.runner import run

p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--scenario',choices=['ALL','ANCHOR_DIF','LOCAL_DEPENDENCE','SINGULAR','NONCONVERGENCE'],default='ALL')
a=p.parse_args();reports={}
a.image=subprocess.check_output(['docker','image','inspect',a.image,'--format','{{.Id}}'],text=True).strip()
value,truth=generate(500)
for scenario in (['ANCHOR_DIF','LOCAL_DEPENDENCE','SINGULAR','NONCONVERGENCE'] if a.scenario=='ALL' else [a.scenario]):
    responses={person['attemptId']:{} for person in value['respondents']}
    for r in value['responses']:responses[r['attemptId']][r['questionVersionId']]=r['scoreCategory']
    qids=[item['questionVersionId'] for item in value['items']]
    matrix=[[responses[person['attemptId']].get(qid) for qid in qids] for person in value['respondents']]
    groups=[person['deliveredArmId'] for person in value['respondents']]
    profile=deepcopy(policy())
    if scenario=='ANCHOR_DIF':
        # Arm-specific +1.3 difficulty shift; retain nonempty categories.
        rng=random.Random(20261109)
        qid=value['anchorQuestionVersionIds'][0];column=qids.index(qid)
        slope,steps=truth['items'][qid]
        for person,row in zip(value['respondents'][500:],matrix[500:]):
            theta=truth['theta'][person['attemptId']]
            logits=[0]+[slope*(k*theta-sum(steps[:k])-1.3*k) for k in range(1,len(steps)+1)]
            weights=[math.exp(x-max(logits)) for x in logits]
            row[column]=rng.choices(range(len(weights)),weights=weights)[0]
    elif scenario=='LOCAL_DEPENDENCE':
        pairs=[]
        for package in value['packages']:
            same=[qids.index(q) for q in package['questionVersionIds'][5:] if next(i for i in value['items'] if i['questionVersionId']==q)['maximumScoreCategory']==1]
            pairs.append(same[:2])
        for index,row in enumerate(matrix):
            first,second=pairs[index//500]
            if index%5:row[second]=row[first]
    elif scenario=='SINGULAR':
        # No shared observed data leaves focal mean/variance unidentified.
        # This deliberately bypasses the producer's per-arm anchor guard.
        for row in matrix[500:]:
            for qid in value['anchorQuestionVersionIds']:row[qids.index(qid)]=None
    else:
        # Deliberate failure injection, never the pinned production/research policy.
        profile['version']='fault-injection-one-cycle';profile['engine']['maxIterations']=1
    output=run({'policy':profile,'items':value['items'],'matrix':matrix,'groups':groups,'groupOrder':[p['armId'] for p in value['packages']],'anchors':value['anchorQuestionVersionIds']},image=a.image)
    q3=[f['adjustedQ3'] for f in output.get('fit',{}).values() if f.get('adjustedQ3') is not None]
    anchors=output.get('anchors',{})
    reports[scenario]={'converged':output.get('converged'),'scientificFailure':output.get('scientificFailure'),'engineError':output.get('engineError'),
        'maximumAdjustedQ3':max(q3) if q3 else None,'anchorChecks':anchors}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(reports,indent=2))
    print(scenario,json.dumps(reports[scenario]),flush=True)
if 'LOCAL_DEPENDENCE' in reports:assert reports['LOCAL_DEPENDENCE']['maximumAdjustedQ3']>.20
if 'SINGULAR' in reports:assert not reports['SINGULAR']['converged']
if 'NONCONVERGENCE' in reports:assert not reports['NONCONVERGENCE']['converged']
if 'ANCHOR_DIF' in reports:
    assert reports['ANCHOR_DIF']['converged'],reports['ANCHOR_DIF']
    assert any(x.get('evaluated') and (x.get('maximumStepDifference',0)>.30 or (x.get('holmP') is not None and x['holmP']<.01)) for x in reports['ANCHOR_DIF']['anchorChecks'].values())
