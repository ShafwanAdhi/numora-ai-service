"""Reproducible local audit; does not read/write snapshots or contact a DB."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import GenerationError, generate, make_record
from lint import reproduce_original
from drill_11_15_math import check_math


def audit(target=20, seed_limit=200, question_ids=None):
    bank=OriginalBank(ROOT/'data/drill-1-indicators-11-15/q0_bank.csv')
    configs=ConfigStore(ROOT/'configs');rows=[];examples=[]
    for qid in bank.ids():
        if question_ids is not None and qid not in question_ids: continue
        o=bank.get(qid);status=o['metadata']['generation_status']
        row=dict(question_id=qid,original_hash=o['hash'],original_version=o['version'],
                 source_document_sha256=o['metadata']['source_document_sha256'],
                 generation_status=status,reason=o['metadata'].get('reason',''))
        if status!='ACTIVE':
            assert not configs.versions(qid),(qid,'inactive config')
            row['sampling_status']='SKIP';rows.append(row);continue
        cfg,h=configs.load(qid)
        assert not validate_config(cfg,o),(qid,validate_config(cfg,o))
        assert reproduce_original(o,cfg)==([],[]),qid
        check_math(qid,o)
        others=[];success=[];failure=[];rejections=Counter();math_errors=[]
        for seed in range(1,seed_limit+1):
            try:
                result=generate(o,cfg,seed,others)
                try:check_math(qid,result.cand)
                except (AssertionError,ValueError,KeyError,IndexError) as e:math_errors.append(dict(seed=seed,error=str(e)))
                if not others:
                    again=generate(o,cfg,seed,others)
                    assert (again.cand,again.values,again.draws_used)==(result.cand,result.values,result.draws_used),qid
                    if not any(r['classification']['indicator']==o['classification']['indicator'] and r['format']==o['format'] for r in examples):
                        examples.append(make_record(o,cfg,h,seed,1,result))
                others.append(result.cand);success.append(seed);rejections.update(result.rejections)
                if len(others)>=target:break
            except GenerationError as e:failure.append(seed);rejections.update(e.rejections)
        row.update(config_version=cfg['config_version'],config_hash=h,successful_seeds=success,
                   failed_seeds=failure,distinct_count=len(others),math_errors=math_errors,
                   rejection_reasons=dict(rejections),
                   sampling_status='FAIL' if math_errors or not others else 'PASS' if len(others)>=target else 'SHORT',
                   finite_domain={k:s for k,s in cfg['variables'].items() if s['gen']!='derived'})
        rows.append(row)
        print(qid,row['sampling_status'],len(others),flush=True)
    return dict(target=target,seed_limit=seed_limit,rows=rows,summary=dict(Counter(r['sampling_status'] for r in rows))),examples


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--target',type=int,default=20);p.add_argument('--seeds',type=int,default=200)
    a=p.parse_args();report,examples=audit(a.target,a.seeds)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    a.output.with_name('examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(report['summary'])
    sys.exit(bool(report['summary'].get('FAIL')))
