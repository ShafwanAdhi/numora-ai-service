"""Reproducible in-memory audit; user store and DB are never accessed."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore,validate_config
from engine import generate,make_record,GenerationError,assemble,build_values
from lint import reproduce_original
from filters import signature
from expr import to_num
from drill_indicator3_math import check_math as check3
from drill_indicator4_math import check_math as check4
from drill_indicator5_math import check_math as check5

def check_math(original,candidate):
    {3:check3,4:check4,5:check5}[original['classification']['indicator']](original,candidate)

def audit():
    bank=OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv');configs=ConfigStore(ROOT/'configs')
    rows=[];examples=[]
    for qid in bank.ids():
        o=bank.get(qid);status=o['metadata']['generation_status']
        row=dict(question_id=qid,status=status,reason=o['metadata']['reason'],original_hash=o['hash'])
        if status=='ACTIVE':
            cfg,h=configs.load(qid);assert validate_config(cfg,o)==[];assert reproduce_original(o,cfg)==([],[])
            check_math(o,assemble(cfg,build_values(cfg,lambda n,s:to_num(cfg['original_values'][n]))))
            stock=[];seeds=[];rejects=Counter()
            for seed in range(1,201):
                result=generate(o,cfg,seed,stock);check_math(o,result.cand)
                stock.append(result.cand);seeds.append(seed);rejects.update(result.rejections)
                if len(stock)==20:break
            assert len(stock)==20,qid
            distinct=set();count=0
            for seed in range(201,251):
                result=generate(o,cfg,seed,[]);check_math(o,result.cand)
                distinct.add(signature(result.cand['stem'],result.cand['options']));rejects.update(result.rejections);count+=1
            row.update(config_hash=h,config_version=1,sampling_status='PASS',stock_count=len(stock),stock_seeds=seeds,
                extra_seed_range=[201,250],extra_accepted=count,extra_unique=len(distinct),rejections=dict(rejects),
                parameter_domain={n:s for n,s in cfg['variables'].items() if s['gen']!='derived'})
            if not any(r['classification']['indicator']==o['classification']['indicator'] and r['format']==o['format'] for r in examples):
                examples.append(make_record(o,cfg,h,seed,1,result))
        else:
            assert configs.versions(qid)==[];row['sampling_status']='SKIP'
        rows.append(row);print(qid,row['sampling_status'],flush=True)
    return dict(source_sha256=hashlib.sha256((ROOT/'data/drill-1-indicators-3-5/source.docx').read_bytes()).hexdigest(),
        scope=dict(indicators=[3,4,5],levels=[1,2,3]),counts=dict(Counter(r['status'] for r in rows)),
        extra_accepted=sum(r.get('extra_accepted',0) for r in rows),rows=rows),examples

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report,examples=audit();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    a.output.with_name(a.output.stem+'-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(report['counts'],report['extra_accepted'],flush=True)
