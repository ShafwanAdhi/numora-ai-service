"""Full producer checks for per-arm anchor insufficiency and empty categories."""
import argparse,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.irt.synthetic import generate
from numora_service.irt.producer import run
from numora_service.irt.runner import run as run_r
p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
image=subprocess.check_output(['docker','image','inspect',a.image,'--format','{{.Id}}'],text=True).strip()
dispatch={'executionId':'55555555-5555-4555-8555-555555555555','dispatchGeneration':1}
value,_=generate(500)
variant=value['packages'][1]['armId'];original=value['packages'][0]['armId']
variant_attempts={x['attemptId'] for x in value['respondents'] if x['deliveredArmId']==variant}
for response in value['responses']:
    if response['attemptId'] in variant_attempts and response['questionVersionId'] in value['anchorQuestionVersionIds']:
        response.update(includedInCalibration=False,eligibilityReasons=['PRIOR_EXPOSURE'],exposureState='KNOWN_PRIOR',priorExposureSources=['PRETEST'])
started=time.monotonic()
result,diagnostics=run(value,dispatch,lambda work:run_r(work,image=image))
assert diagnostics['selection']['eligiblePerArm'][variant]==500
assert diagnostics['selection']['fittedPerArm'][variant]==0
assert diagnostics['selection']['fittedPerArm'][original]==500
assert result['outcome']['measurementState']=='PARTIAL',result['outcome']['packages']
assert sum(x['status']=='SCORED' for x in result['outcome']['respondents'])==500
reports={'partial':{'seconds':time.monotonic()-started,'state':result['outcome']['measurementState'],'packages':result['outcome']['packages'],'scored':500,'selection':diagnostics['selection']}}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(reports,indent=2));print('PARTIAL: 500 reference participants scored; insufficient arm preserved',flush=True)
value,_=generate(500)
for response in value['responses']:
    if response['questionVersionId']==value['anchorQuestionVersionIds'][0]:response.update(scoreCategory=0,awardedPoints='0.00')
def forbidden(_):raise AssertionError('Empty anchor category must stop fitting, not collapse categories')
result,diagnostics=run(value,dispatch,forbidden)
assert result['executionStatus']=='SUCCEEDED' and result['outcome']['measurementState']=='INSUFFICIENT'
assert len(result['outcome']['respondents'])==1000
assert all(x['score'] is None for x in result['outcome']['respondents'])
reports['emptyCategory']={'state':result['outcome']['measurementState'],'respondents':1000,'engineInvoked':False}
a.output.write_text(json.dumps(reports,indent=2));print('EMPTY CATEGORY: preserved; no engine or fabricated scores',flush=True)
