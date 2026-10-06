"""In-memory indicator 5 audit, including source holds and independent math."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate, make_record
from filters import signature
from lint import reproduce_original
from drill_indicator5_math import check_math


def audit():
    path = ROOT/'data/drill-1-indicators-3-5/q0_bank.csv'
    bank = OriginalBank(path)
    configs = ConfigStore(ROOT/'configs')
    rows, examples = [], []
    for qid in bank.ids():
        if qid.split('-')[1] != '5': continue
        original = bank.get(qid)
        held = original['metadata']['generation_status']!='ACTIVE'
        status = original['metadata']['generation_status']
        reason = original['metadata']['reason'] if held else 'Source arithmetic consistent; declarative template, exact rendered-text oracle and bounded domain verified.'
        row = dict(question_id=qid,status=status,reason=reason,original_hash=original['hash'],
            config_hash=None,stock_count=0,stock_seeds=[],extra_accepted=0,parameter_domain={})
        if held:
            assert configs.versions(qid)==[]
            row['sampling_status']='SKIP'
        else:
            cfg,config_hash = configs.load(qid)
            assert validate_config(cfg,original)==[]
            assert reproduce_original(original,cfg)==([],[])
            check_math(original,assemble(cfg,build_values(cfg,lambda n,s:Fraction(str(cfg['original_values'][n])))))
            stock,seeds,rejections = [],[],Counter()
            for seed in range(1,201):
                result=generate(original,cfg,seed,stock)
                check_math(original,result.cand)
                stock.append(result.cand);seeds.append(seed);rejections.update(result.rejections)
                if len(stock)==20:break
            assert len(stock)==20
            assert len({signature(c['stem'],c['options']) for c in stock})==20
            unique=set()
            for seed in range(201,251):
                result=generate(original,cfg,seed,[])
                check_math(original,result.cand)
                unique.add(signature(result.cand['stem'],result.cand['options']))
                rejections.update(result.rejections)
            row.update(config_hash=config_hash,config_version=1,stock_count=20,stock_seeds=seeds,
                extra_seed_range=[201,250],extra_accepted=50,extra_unique=len(unique),
                sampling_status='PASS',rejections=dict(rejections),
                parameter_domain={n:s for n,s in cfg['variables'].items() if s['gen']!='derived'},
                constraints=cfg['constraints'])
            examples.append(make_record(original,cfg,config_hash,seed,1,result))
        rows.append(row)
        print(qid,row['sampling_status'],flush=True)
    return dict(scope=dict(indicators=[5],levels=[1,2,3]),counts=dict(Counter(r['status'] for r in rows)),
        source_bank_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        stock_count=sum(r['stock_count'] for r in rows),extra_accepted=sum(r['extra_accepted'] for r in rows),rows=rows),examples


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report,examples=audit()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    args.output.with_name(args.output.stem+'-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(report['counts'],report['stock_count'],report['extra_accepted'])
