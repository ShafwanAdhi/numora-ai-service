"""Promote the exact 28 user-approved proposals; never rewrite historical assets."""
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path

from level45_completion_common import ROOT,REPO,DRAFT_DATA
from bank import OriginalBank,load_workspace_bank
from config_store import ConfigStore,validate_config
from engine import generate
from lint import reproduce_original
from build_level45_completion import modules

DEST=ROOT/'data/drill-1-indicators-1-5-levels-4-5-approved'
REPORT=REPO/'docs/audits/2026-10-21-drill-1-5-level45-approved'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path,content):
    if path.exists():
        if path.read_bytes()!=content:
            raise ValueError(f'Refusing to overwrite an existing version: {path}')
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(content)


def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode('utf-8')


def clean_display(text):
    """Remove proposal lifecycle labels, leaving academic text/numbers untouched."""
    text=re.sub(r'^PROPOSED[^\n]*?review akademik\.\s*','',text)
    text=re.sub(r'\b[Kk]oreksi (?:draft|draf)\b','Koreksi disetujui pengguna',text)
    text=re.sub(r'\b(?:draft|draf) koreksi\b','koreksi',text,flags=re.I)
    return re.sub(r'\b(?:draft|draf)\b','versi yang disetujui',text,flags=re.I)


def runtime_metadata(original):
    metadata=deepcopy(original['metadata'])
    metadata['reviewed_proposal_explanation_sha256']=hashlib.sha256(metadata['original_explanation'].encode('utf-8')).hexdigest()
    metadata['original_explanation']=clean_display(metadata['original_explanation'])
    metadata['approved_key_caption']=clean_display(metadata.pop('proposed_key_caption'))
    metadata['additional_notes']=clean_display(metadata.pop('proposed_additional_notes'))
    return metadata


def activate():
    archive=OriginalBank(DRAFT_DATA/'q0_bank.csv')
    assert len(archive.ids())==28
    baseline=REPORT/'prior-assets-baseline.json'
    if not baseline.exists():
        files={}
        for prefix in ['variant_gen/data','variant_gen/configs','variant_gen/drafts','docs/sources','docs/audits']:
            for path in (REPO/prefix).rglob('*'):
                if path.is_file() and REPORT not in path.parents and '__pycache__' not in path.parts:
                    files[path.relative_to(REPO).as_posix()]=sha(path)
        REPORT.mkdir(parents=True,exist_ok=True)
        baseline.write_bytes(encoded(dict(date='2026-10-21',files=files)))
    # Confirm the archived proposals and all prior assets still match the frozen input.
    prior=json.loads(baseline.read_text(encoding='utf-8'))['files']
    for name,digest in prior.items():assert sha(REPO/name)==digest,name
    # Full runtime validation is performed in memory before any new bank is written.
    metadata={};evidence=[]
    for qid in archive.ids():
        original=archive.get(qid)
        active=deepcopy(original);active['metadata']=runtime_metadata(original);m=active['metadata']
        assert m['generation_status']=='HOLD_SOURCE' and m['review_only']
        assert original['version']==2
        m.update(generation_status='ACTIVE',reason='',review_only=False,
            approval_status='USER_APPROVED_CORRECTION',self_adjustment_enabled=False,
            approval_date='2026-10-21',approved_by='PROJECT_OWNER_USER',
            approval_scope=['SOURCE_CORRECTIONS','LOCAL_GENERATOR_ACTIVATION'],
            difficulty_equivalence_approved=False,database_publication_approved=False,
            proposal_archive='variant_gen/drafts/2026-10-20-level45-academic',
            approval_record='variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/approval.json',
            notes=['Koreksi dan aktivasi generator lokal disetujui pengguna 21 Oktober 2026.',
                   'Sumber v1 dan arsip draf tetap dipertahankan; tidak memublikasikan database atau mengaktifkan self-adjustment.'])
        cfg,digest=ConfigStore(DRAFT_DATA/'configs').load(qid)
        assert validate_config(cfg,active)==[],qid
        assert reproduce_original(active,cfg)==([],[]),qid
        oracle=modules(int(qid.split('-')[1]))[1]
        made=[]
        for seed in range(1,21):
            candidate=generate(active,cfg,seed,made).cand
            oracle.check_math(qid,candidate);made.append(candidate)
        metadata[qid]=m
        evidence.append(dict(question_id=qid,original_version=2,original_hash=active['hash'],
            config_version=1,config_hash=digest,config_sha256=sha(DRAFT_DATA/'configs'/qid/'v1.json')))
    approval=dict(date='2026-10-21',approved_by='PROJECT_OWNER_USER',
        user_instruction='aku setuju dengan koreksinya, masukkan dan buat generatornya',
        scope=['SOURCE_CORRECTIONS','LOCAL_GENERATOR_ACTIVATION'],
        curriculum_institutional_approval_claimed=False,difficulty_equivalence_approved=False,
        self_adjustment_enabled=False,database_published=False,
        reviewed_proposals_sha256=sha(DRAFT_DATA/'proposed_corrections.json'),
        prior_assets_baseline_sha256=sha(baseline),entries=evidence)
    # Source rows/configs are byte-identical; only the separate runtime metadata changes.
    for name in ('q0_bank.csv','question_catalog.json'):
        write_once(DEST/name,(DRAFT_DATA/name).read_bytes())
    write_once(DEST/'question_metadata.json',encoded(metadata))
    write_once(DEST/'approval.json',encoded(approval))
    for qid in archive.ids():
        write_once(ROOT/'configs'/qid/'v1.json',(DRAFT_DATA/'configs'/qid/'v1.json').read_bytes())
    workspace=load_workspace_bank(ROOT/'data/q0_bank.csv')
    assert set(archive.ids())<=set(workspace.ids()),'Approved bank must be registered in default loader'
    groups=[g for g in workspace.catalog() if g.get('activity')=='DRILL' and g.get('indicator') in range(1,6)]
    assert sum(len(g['question_ids']) for g in groups)==250
    levels=[g for g in groups if g['source_level'] in (4,5)]
    assert len(levels)==10 and all(len(g['question_ids'])==10 for g in levels)
    for name,digest in prior.items():assert sha(REPO/name)==digest,name
    report=dict(approval=approval,activated=28,indicator_1_5_originals=250,level_4_5_generators=100,
        all_previous_assets_unchanged=True,protected_assets=len(prior),workspace_originals=len(workspace.ids()),
        runtime_generator_families=len(list((ROOT/'configs').glob('*/v1.json'))))
    write_once(REPORT/'activation.json',encoded(report))
    print(json.dumps({k:v for k,v in report.items() if k!='approval'},indent=2))
    return report


if __name__=='__main__':activate()
