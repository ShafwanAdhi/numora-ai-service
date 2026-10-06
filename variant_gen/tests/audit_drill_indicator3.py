"""Reproduce indicator 3 audit in memory, without store or database access."""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore,validate_config
from engine import assemble,build_values,generate,make_record
from expr import RejectDraw
from filters import signature,validate_candidate
from lint import reproduce_original
from drill_indicator3_math import check_math

HOLD_REASONS={
    'pg-3-1-2':'Lahan persegi luas45m2 mempunyai diagonal sqrt(90), bukan sqrt(45); premis geometri bertentangan dengan besaran yang diminta.',
    'pg-3-1-3':'Stem hanya membulatkan harga satuan:3,25*25.000=81.250 tidak ada pada opsi. Pembahasan menambahkan pembulatan total tanpa instruksi stem.',
    'pg-3-1-5':'Aturan pembulatan operand menghasilkan20*7.000=140.000 tetapi kunci130.000 memakai pembulatan hasil riil; aturan estimasi tidak tunggal.',
    'pg-3-2-2':'Lahan persegi luas52m2 mempunyai diagonal sqrt(104), bukan sqrt(52); premis geometri bertentangan dengan panjang papan.',
    'pg-3-2-3':'Pembulatan harga satuan menghasilkan3,5*25.000=87.500 tanpa opsi yang sesuai. Pembahasan menambahkan pembulatan total dan mengizinkan87.000/88.000; kunci87.000 tidak tunggal.',
    'pg-3-2-4':'Hasil riil59,4*19,8/9,7=121,249484... membulat menjadi121,25. Stem dan opsi B menyatakan121,26; pembahasan menyatakan121,25.',
    'mcma-3-2-7':'Luas ubin persegi20,32,48cm2 disamakan dengan diagonal sqrt(20),sqrt(32),sqrt(48); diagonal seharusnya sqrt(dua kali luas).',
    'mcma-3-2-8':'Opsi C menyatakan semua komponen dibulatkan ke atas, tetapi12 botol dibulatkan menjadi10. Klaim alasan yang dikunci benar adalah salah.',
    'kategori-3-2-9':'Kunci sumber menyatakan(b) SALAH, tetapi2,45 dibulatkan ke satuan menjadi2 sehingga(b) BENAR. Instruksi koreksi dalam pembahasan tidak diterapkan.',
    'pg-3-3-3':'Total riil415.800. Opsi C450.000 dan D420.000 sama-sama batas atas aman; D lebih dekat. Stem tidak mensyaratkan kedua operand dibulatkan ke atas, sehingga kunci C tidak tunggal.'
}

def audit():
    bank=OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv');store=ConfigStore(ROOT/'configs')
    rows=[];examples=[]
    for qid in bank.ids():
        if qid.split('-')[1]!='3':continue
        original=deepcopy(bank.get(qid))
        row=dict(question_id=qid,status='HOLD_SOURCE' if qid in HOLD_REASONS else 'ACTIVE',
            reason=HOLD_REASONS.get(qid,'Audit sumber valid; template numerik mempertahankan stem/opsi/kunci asli, pembulatan half-up diverifikasi independen.'),
            original_hash=original['hash'],source_sha256=original['metadata']['source_document_sha256'],
            config_hash=None,stock_seeds=[],stock_count=0,count=0,extra_accepted=0,parameter_domain={})
        if qid in HOLD_REASONS:
            assert store.versions(qid)==[];row['sampling_status']='SKIP'
        else:
            # Provisional imported statuses are not changed on disk by this isolated audit.
            original['metadata']['generation_status']='ACTIVE'
            cfg,config_hash=store.load(qid)
            assert validate_config(cfg,original)==[]
            assert reproduce_original(original,cfg)==([],[])
            check_math(original,assemble(cfg,build_values(cfg,lambda n,s:cfg['original_values'][n])))
            stock=[];rejects=Counter()
            for seed in range(1,21):
                result=generate(original,cfg,seed,stock);check_math(original,result.cand)
                stock.append(result.cand);rejects.update(result.rejections)
            assert len({signature(c['stem'],c['options']) for c in stock})==20
            extra=[]
            for seed in range(201,251):
                result=generate(original,cfg,seed,[]);check_math(original,result.cand)
                extra.append(signature(result.cand['stem'],result.cand['options']));rejects.update(result.rejections)
            domain=[];domain_rejects=Counter()
            for k in range(81):
                try:c=assemble(cfg,build_values(cfg,lambda n,s:k))
                except RejectDraw as error:domain_rejects[str(error)]+=1;continue
                problems=validate_candidate(c,original,[])
                if problems:domain_rejects.update(problems);continue
                check_math(original,c);domain.append(signature(c['stem'],c['options']))
            row.update(config_hash=config_hash,config_version=1,stock_seeds=list(range(1,21)),stock_count=20,count=20,
                extra_seed_range=[201,250],extra_accepted=50,extra_unique=len(set(extra)),sampling_status='PASS',
                parameter_domain={name:spec for name,spec in cfg['variables'].items() if spec['gen']!='derived'},
                constraints=cfg['constraints'],finite_domain_draws=81,finite_domain_accepted=len(domain),
                finite_domain_unique=len(set(domain)),finite_domain_rejections=dict(domain_rejects),rejections=dict(rejects))
            assert row['finite_domain_unique']>=20
            if not any(e['format']==original['format'] for e in examples):
                examples.append(make_record(original,cfg,config_hash,250,1,result))
        rows.append(row)
        print(qid,row['sampling_status'],flush=True)
    assert len(rows)==30
    return dict(scope=dict(indicators=[3],levels=[1,2,3]),counts=dict(Counter(r['status'] for r in rows)),
        stock_count=sum(r['stock_count'] for r in rows),extra_accepted=sum(r['extra_accepted'] for r in rows),rows=rows),examples

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report,examples=audit();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    args.output.with_name(args.output.stem+'-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(report['counts'],report['stock_count'],report['extra_accepted'])
