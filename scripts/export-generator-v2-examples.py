"""Export sanitized contract examples from the local bank; no DB/network access."""
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('v2_examples',ROOT/'tests/service/test_v2.py')
tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
tests.V2Tests.setUpClass();case=tests.V2Tests()
from numora_service.v2_generate import generate_result, stock_manifest
target=ROOT/'contracts/generator-service-v2/examples';target.mkdir(exist_ok=True)
def write(name,value):
    (target/(name+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
for qid,name in [('pg-6-1-1','numeric-candidate'),('pg-16-4-1','media-candidate'),('pg-16-4-2','stock-candidate')]:
    work=case.work(qid)
    if qid in case.stocks:
        item=case.stocks[qid][0]
        work.update(mode='CONCEPTUAL_STOCK',stockItem=item,stockSetId='00000000-0000-4000-8000-000000000004',stockSetDigest='a'*64,reservation={'id':'00000000-0000-4000-8000-000000000005','reused':False,'cycle':1})
    else:work.update(mode='NUMERIC',config=case.configs.load(qid)[0],seed=42)
    result=generate_result(work);write(name,result['payload'])
write('notification',{'contractVersion':3,'requestId':'00000000-0000-4000-8000-000000000001','inputDigest':'a'*64,'dispatchGeneration':1})
write('response',{'serviceContract':'generator-service-v2','requestId':'00000000-0000-4000-8000-000000000001','executionId':'00000000-0000-4000-8000-000000000002','dispatchGeneration':1,'status':'SUCCEEDED','failureCode':None,'artifactId':'00000000-0000-4000-8000-000000000003','artifactDigest':'b'*64,'candidateIds':['00000000-0000-4000-8000-000000000004']})
print('Sanitized examples exported; no generated PNG bytes persisted')
