"""Audit summaries only. Generated question content is never written."""
import csv
import hashlib
import json
from collections import Counter
from test_drill_6_10_level45_batch1 import ROOT, DATA, AUDIT, IDS, check_math
from bank import load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values
from filters import signature, validate_candidate
from lint import reproduce_original

OUTPUT=ROOT.parent/'docs/audits/2026-10-20-drill-6-10-level45-batch1'
BASELINE=ROOT/'tests/.batch6_10_baseline.json'

def main(*, IDS=IDS, OUTPUT=OUTPUT, BASELINE=BASELINE, check_math=check_math,
         prior_source_ids=(), stage=1):
    old=json.loads(BASELINE.read_text()) if BASELINE.exists() else json.loads((OUTPUT/'audit.json').read_text(encoding='utf-8'))['baseline']
    assert all(hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==h for p,h in old['hashes'].items()), 'Existing assets changed'
    bank=load_workspace_bank(ROOT/'data/q0_bank.csv'); store=ConfigStore(ROOT/'configs'); results=[]
    for qid in IDS:
        o=bank.get(qid); cfg,h=store.load(qid)
        assert validate_config(cfg,o)==[]
        assert reproduce_original(o,cfg)==([],[])
        signatures=set(); rejected=Counter(); spec=cfg['variables']['k']
        domain=list(range(spec['range'][0],spec['range'][1]+1,spec.get('step',1)))
        for k in domain:
            c=assemble(cfg,build_values(cfg,lambda name,spec:k)); check_math(qid,c)
            errors=validate_candidate(c,o,[])
            if errors: rejected.update(errors)
            else: signatures.add(signature(c['stem'],c['options']))
        assert len(signatures)>=20
        results.append(dict(question_id=qid,original_hash=o['hash'],config_hash=h,
            source_audit_id=o['metadata']['audit_id'],classification=o['classification'],
            declared_inputs=len(domain),exact_unique_capacity=len(signatures),rejections=dict(rejected)))
    chosen={r['source_audit_id'] for r in results} | set(prior_source_ids)
    completed=len(chosen)
    pending=[dict(audit_id=e['audit_id'],indicator=e['indicator'],level=e['level'],source_number=e['source_number'],
        status='NEXT_BATCH' if not e['issues'] else 'ACADEMIC_FOLLOW_UP',recommendation=e['recommendation'])
        for e in json.loads(AUDIT.read_text(encoding='utf-8'))['entries'] if e['level'] in (4,5) and e['audit_id'] not in chosen]
    assert len(pending)==100-completed
    report=dict(summary=dict(implemented=len(IDS),cumulative_implemented=completed,target=100,pending=len(pending),workspace_originals=len(bank.ids()),
        workspace_configs=len(list((ROOT/'configs').glob('*/v1.json'))),
        exhaustive_inputs=sum(r['declared_inputs'] for r in results),
        protected_files_unchanged=len(old['hashes']),
        min_unique_capacity=min(r['exact_unique_capacity'] for r in results)),entries=results,pending=pending,baseline=old)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (OUTPUT/'pending.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(pending[0])); w.writeheader(); w.writerows(pending)
    text=f'''# Generator indikator 6–10, level 4–5: tahap {stage}

{len(IDS)} generator ditambahkan pada tahap ini; total {completed}/100 soal diaktifkan.
Sumber dan pembahasan original dipertahankan; katalog Drill paket 1 memakai nomor asli.
{len(pending)} soal tersisa tercatat dalam pending.csv; temuan akademik tetap memerlukan tindak lanjut.

Seluruh domain parameter diperiksa oleh oracle matematika dari teks hasil render.
Reproduksi original, variasi unik, seed deterministik, serta workbench tanpa DB/penyimpanan diuji.
Audit hanya menyimpan ringkasan pemeriksaan dan hash, tanpa konten soal varian.

Rentang belum disetujui kurikulum atau dikalibrasi IRT; self-adjustment tetap nonaktif.
Panggilan Generate dapat diulang; domain numerik tiap konfigurasi tetap terbatas.

Jalankan dari root repo:
```
python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch{stage}.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch{stage}.py
```
'''
    text+='\n| Soal | Varian unik valid |\n| --- | ---: |\n'
    text+=''.join(f"| {r['question_id']} | {r['exact_unique_capacity']} |\n" for r in results)
    (OUTPUT/'README.md').write_text(text,encoding='utf-8')
    print(json.dumps(report['summary']))

if __name__=='__main__': main()
