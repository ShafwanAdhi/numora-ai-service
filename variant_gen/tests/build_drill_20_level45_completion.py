"""Complete 13 indicator-20 generators; preserve all source originals and other assets."""
import hashlib
import importlib
import json
from copy import deepcopy
from pathlib import Path

from author_drill_20_23_level45_batch1 import ROOT,DATA
from bank import load_workspace_bank
from config_store import validate_config
from engine import assemble,build_values,generate
from filters import validate_candidate,signature
from expr import is_num,json_number
from lint import reproduce_original

REPO=ROOT.parent
REPORT=REPO/'docs/audits/2026-10-21-drill-20-level45-completion'
METADATA=DATA/'question_metadata.json'
IDS={'pg-20-4-1','pg-20-4-4','pg-20-4-5','mcma-20-4-6','mcma-20-4-8','kategori-20-4-10',
     'pg-20-5-1','pg-20-5-2','pg-20-5-3','pg-20-5-4','mcma-20-5-6','mcma-20-5-8','kategori-20-5-9'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(obj):return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def build():
    REPORT.mkdir(parents=True,exist_ok=True)
    manifest=REPORT/'prior-assets-baseline.json'
    if not manifest.exists():
        files={p.relative_to(REPO).as_posix():sha(p) for folder in ['variant_gen/data','variant_gen/configs','variant_gen/drafts','docs/sources','docs/audits']
               for p in (REPO/folder).rglob('*') if p.is_file() and REPORT not in p.parents and '__pycache__' not in p.parts}
        manifest.write_bytes(encoded(dict(files=files,source_metadata=json.loads(METADATA.read_text(encoding='utf-8')))))
    baseline=json.loads(manifest.read_text(encoding='utf-8'))
    bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
    evidence=[];outputs={}
    for kind in ['numeric','conceptual']:
        author=importlib.import_module(f'author_drill_20_level45_{kind}')
        oracle=importlib.import_module(f'oracle_drill_20_level45_{kind}')
        for entry in author.selected():
            qid=entry['question_id'];assert qid in IDS and not entry['issues'],qid
            original=bank.get(qid);cfg=author.author(entry).config(original)
            assert original['metadata']['generation_status']=='ACTIVE' and original['version']==1
            assert validate_config(cfg,original)==[],qid
            assert reproduce_original(original,cfg)==([],[]),qid
            assert cfg['variables']['k']['range']==[0,24],qid
            unique=set()
            for k in range(25):
                c=assemble(cfg,build_values(cfg,lambda name,spec,k=k:k));oracle.check_math(qid,c)
                if k:
                    assert validate_candidate(c,original,[])==[],(qid,k)
                    unique.add(signature(c['stem'],c['options']))
            assert len(unique)==24,qid
            made=[];samples=[]
            for seed in range(1,21):
                result=generate(original,cfg,seed,made);oracle.check_math(qid,result.cand);made.append(result.cand)
                samples.append(dict(seed=seed,values={n:json_number(v) if is_num(v) else v for n,v in result.values.items()},candidate=result.cand))
            assert len({signature(c['stem'],c['options']) for c in made})==20
            for seed in range(201,211):
                a=generate(original,cfg,seed,[]);b=generate(original,cfg,seed,[])
                assert a.cand==b.cand and a.values==b.values
                oracle.check_math(qid,a.cand)
            path=ROOT/'configs'/qid/'v1.json';content=encoded(cfg)
            if path.exists():assert path.read_bytes()==content,('Refusing config overwrite',qid)
            outputs[qid]=(path,content)
            evidence.append(dict(question_id=qid,kind=kind,source_number=original['metadata']['source_number'],
                original_version=original['version'],original_hash=original['hash'],config_version=1,
                config_sha256=hashlib.sha256(content).hexdigest(),declared_k=list(range(25)),effective_k=list(range(1,25)),
                capacity=24,samples=samples,approval_status='NOT_CURRICULUM_APPROVED',self_adjustment_enabled=False))
    assert set(outputs)==IDS
    metadata=deepcopy(baseline['source_metadata'])
    for e in evidence:
        metadata[e['question_id']].update(generator_status='IMPLEMENTED',
            generator_family_kind=e['kind'],generator_audit='docs/audits/2026-10-21-drill-20-level45-completion/evidence.json')
    # Preserve every other original and metadata field, including raw source numbers 31-50.
    current=json.loads(METADATA.read_text(encoding='utf-8'))
    assert current==baseline['source_metadata'] or current==metadata,'Unexpected concurrent metadata change'
    allowed=METADATA.relative_to(REPO).as_posix()
    for name,digest in baseline['files'].items():
        if name!=allowed:assert sha(REPO/name)==digest,name
    for path,content in outputs.values():
        path.parent.mkdir(exist_ok=True)
        if not path.exists():path.write_bytes(content)
    temporary=METADATA.with_suffix('.json.tmp');temporary.write_bytes(encoded(metadata));temporary.replace(METADATA)
    for name,digest in baseline['files'].items():
        if name!=allowed:assert sha(REPO/name)==digest,name
    result=dict(date='2026-10-21',new_generators=13,numeric_families=6,conceptual_families=7,
        parameter_cases=325,new_effective_variants=312,unique_samples=260,additional_replay_samples=130,
        source_originals_unchanged=True,previous_assets_unchanged_except_generator_metadata=True,
        protected_prior_files=len(baseline['files'])-1,baseline_manifest_sha256=sha(manifest),
        metadata_before=baseline['files'][allowed],metadata_after=sha(METADATA),entries=evidence)
    (REPORT/'evidence.json').write_bytes(encoded(result))
    print(json.dumps({k:v for k,v in result.items() if k!='entries'},indent=2))
    return result


if __name__=='__main__':build()
