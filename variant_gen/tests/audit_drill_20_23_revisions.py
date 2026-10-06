"""Audit revised generators in memory; write only requested audit/example artifacts."""
import argparse
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import generate, make_record, GenerationError
from lint import reproduce_original
from test_drill_20_23_revisions import REVISED, check_revised_math

def audit():
    folder=ROOT/'data/drill-1-indicators-20-23'
    bank=OriginalBank(folder/'q0_bank.csv');configs=ConfigStore(ROOT/'configs')
    test=unittest.TestCase();rows=[];examples=[]
    for q in REVISED:
        o=bank.get(q);cfg,h=configs.load(q)
        test.assertEqual(validate_config(cfg,o),[])
        test.assertEqual(reproduce_original(o,cfg),([],[]))
        check_revised_math(test,o,o)
        others=[];seeds=[];failed=[];draws=[]
        for seed in range(1,201):
            try:result=generate(o,cfg,seed,others)
            except GenerationError:failed.append(seed);continue
            check_revised_math(test,o,result.cand)
            if not others:examples.append(make_record(o,cfg,h,seed,1,result))
            others.append(result.cand);seeds.append(seed);draws.append(result.draws_used)
            if len(others)==20:break
        test.assertEqual(len(others),20,q)
        first=generate(o,cfg,37,[])
        test.assertEqual(first,generate(o,cfg,37,[]))
        for seed in range(101,201):check_revised_math(test,o,generate(o,cfg,seed,[]).cand)
        rows.append(dict(question_id=q,original_version=o['version'],original_hash=o['hash'],
                         config_version=cfg['config_version'],config_hash=h,
                         status='PASS',distinct_count=len(others),successful_seeds=seeds,
                         failed_seeds=failed,draws_used=draws,extra_seed_checks=100,
                         parameter_domains={n:s for n,s in cfg['variables'].items() if s['gen']!='derived'}))
        print(q,'PASS',len(others),flush=True)
    return dict(source_document_sha256=hashlib.sha256((folder/'source-revision-2026-10-07.docx').read_bytes()).hexdigest(),
                target=20,seed_limit=200,summary=dict(PASS=16,FAIL=0,distinct_count=320,extra_seed_checks=1600),rows=rows),examples

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    report,examples=audit();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    args.output.with_name('revision-generator-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(report['summary'])
