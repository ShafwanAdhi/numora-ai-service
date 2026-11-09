"""Engine stress experiments. No contract artifact, policy approval or student result."""
import argparse,json,sys,subprocess
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.irt.synthetic import generate
from numora_service.irt.producer import policy
from numora_service.irt.runner import run

p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();reports={}
a.image=subprocess.check_output(['docker','image','inspect',a.image,'--format','{{.Id}}'],text=True).strip()
value,_=generate(500)
for scenario in ['ANCHOR_DIF','LOCAL_DEPENDENCE','SINGULAR','NONCONVERGENCE']:
    responses={person['attemptId']:{} for person in value['respondents']}
    for r in value['responses']:responses[r['attemptId']][r['questionVersionId']]=r['scoreCategory']
    qids=[item['questionVersionId'] for item in value['items']]
    matrix=[[responses[person['attemptId']].get(qid) for qid in qids] for person in value['respondents']]
    groups=[person['deliveredArmId'] for person in value['respondents']]
    profile=deepcopy(policy())
    if scenario=='ANCHOR_DIF':
        # Strong arm-specific response distortion on an identical anchor version.
        for row in matrix[500:]:row[0]=1
    elif scenario=='LOCAL_DEPENDENCE':
        pairs=[]
        for package in value['packages']:
            same=[qids.index(q) for q in package['questionVersionIds'][5:] if next(i for i in value['items'] if i['questionVersionId']==q)['maximumScoreCategory']==1]
            pairs.append(same[:2])
        for index,row in enumerate(matrix):
            first,second=pairs[index//500];row[second]=row[first]
    elif scenario=='SINGULAR':
        for row in matrix:
            for index in range(len(row)):
                if row[index] is not None:row[index]=0
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
assert reports['LOCAL_DEPENDENCE']['maximumAdjustedQ3']>.20
assert not reports['SINGULAR']['converged']
assert not reports['NONCONVERGENCE']['converged']
assert any(x.get('maximumStepDifference',0)>.30 or (x.get('holmP') is not None and x['holmP']<.01) or not x.get('evaluated') for x in reports['ANCHOR_DIF']['anchorChecks'].values())
