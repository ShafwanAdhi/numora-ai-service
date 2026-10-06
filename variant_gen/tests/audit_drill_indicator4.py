"""Indicator 4 source decisions, finite-domain stock, and independent math audit."""
import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate, make_record
from filters import signature
from lint import reproduce_original
from drill_indicator4_math import check_math

HOLD={
    'pg-4-1-1':'Header kunci B menyebut12 hari; KPK(12,18)=36 hari sesuai opsi C dan pembahasan. Kunci akademik perlu disahkan.',
    'pg-4-2-2':'Beras,gula,minyak dapat dibagi dalam massa pecahan. Tanpa syarat isi tiap paket berupa kg bulat, jumlah paket tidak mempunyai maksimum12 seperti kunci.',
    'pg-4-2-5':'Caption header C menyebut2^2*3=12, tetapi opsi C dan pembahasan2^2*3^2=36. Instruksi koreksi dalam DOCX adalah konten sumber, bukan izin mengganti kunci akademik.',
    'pg-4-3-1':'Analisis I dan III sama-sama benar:60 hari setelah1 Maret adalah30 April. PG tidak boleh memilih III saja. Stem juga menyebut3 analisis tetapi mencantumkan4.'
}
HOLD.update({
    'mcma-4-1-8':'Stem tidak menetapkan jumlah kantong maksimum.14 kantong sama isi sah memuat6 buku,4 pensil,2 penggaris;3 buku per kantong hanya berlaku jika memakai28 kantong.',
    'mcma-4-2-8':'Stem tidak menetapkan jumlah ruangan maksimum.12 ruangan sama isi sah mendapat6 tetikus dan8 papan ketik; kunci3 dan4 mengasumsikan24 ruangan.',
    'mcma-4-3-8':'Stem tidak menetapkan jumlah kelompok maksimum.8 kelompok sama isi sah mendapat10 pak kertas dan14 botol; kunci5 dan7 mengasumsikan16 kelompok.',
    'kategori-4-1-9':'Stem tidak menetapkan jumlah piring maksimum.9 piring sama isi sah memuat8 bolu dan10 lapis; selisih2, bukan1 pada kunci. Pembahasan mengasumsikan18 piring.',
    'kategori-4-2-9':'Stem tidak menetapkan jumlah kardus maksimum.9 kardus sama isi sah memuat6 botol apel dan8 jeruk; total14, bukan7. Kunci mengasumsikan18 kardus.',
    'kategori-4-3-9':'Stem tidak menetapkan jumlah kotak maksimum.6 kotak sama isi sah memuat10 mikroskop dan14 kaca; total24, bukan12. Kunci mengasumsikan12 kotak.',
    'kategori-4-1-10':'Stem meminta potongan sama panjang, tanpa syarat terpanjang. Potongan5cm menghasilkan9 potongan dari pita pertama, bukan3. Kunci mengasumsikan panjang15cm.',
    'kategori-4-2-10':'Stem meminta potongan sama panjang, tanpa syarat terpanjang. Pita60/90cm dipotong15cm menghasilkan10 potongan, bukan5. Kunci mengasumsikan panjang30cm.',
    'kategori-4-3-10':'Stem meminta potongan sama panjang, tanpa syarat terpanjang. Pita75/105cm dipotong5cm menghasilkan36 potongan, bukan12. Kunci mengasumsikan panjang15cm.'
})

def audit():
    bank=OriginalBank(ROOT/'data/drill-1-indicators-3-5/q0_bank.csv');configs=ConfigStore(ROOT/'configs')
    rows=[];examples=[]
    for qid in bank.ids():
        if qid.split('-')[1]!='4':continue
        original=copy.deepcopy(bank.get(qid))
        assert original['metadata']['source_text'] and original['metadata']['original_explanation']
        row=dict(question_id=qid,status='HOLD_SOURCE' if qid in HOLD else 'ACTIVE',
                 reason=HOLD.get(qid,'Source key, options and explanation agree. Parameterized arithmetic verified independently from rendered stimulus and options.'),
                 original_hash=original['hash'],config_hash=None,stock_seeds=[],stock_count=0,extra_accepted=0,parameter_domain={},
                 source_text_sha256=hashlib.sha256(original['metadata']['source_text'].encode()).hexdigest())
        if qid in HOLD:
            assert configs.versions(qid)==[]
            row['sampling_status']='SKIP'
        else:
            # Root merges final source statuses only after all independent indicator audits finish.
            original['metadata']['generation_status']='ACTIVE'
            cfg,h=configs.load(qid)
            assert validate_config(cfg,original)==[],qid
            assert reproduce_original(original,cfg)==([],[]),qid
            check_math(original,assemble(cfg,build_values(cfg,lambda n,s:cfg['original_values'][n])))
            stock=[];seeds=[];rejects=Counter()
            for seed in range(1,201):
                result=generate(original,cfg,seed,stock);check_math(original,result.cand)
                stock.append(result.cand);seeds.append(seed);rejects.update(result.rejections)
                if len(stock)==20:break
            assert len(stock)==20
            assert len({signature(c['stem'],c['options']) for c in stock})==20
            distinct=set()
            for seed in range(201,251):
                result=generate(original,cfg,seed,[]);check_math(original,result.cand)
                distinct.add(signature(result.cand['stem'],result.cand['options']));rejects.update(result.rejections)
            domain={n:s for n,s in cfg['variables'].items() if s['gen']!='derived'}
            cardinality=1
            for spec in domain.values():cardinality*=len(spec['values']) if spec['gen']=='choice' else (spec['range'][1]-spec['range'][0])//spec.get('step',1)+1
            row.update(config_hash=h,config_version=1,stock_seeds=seeds,stock_count=20,extra_accepted=50,
                       extra_seed_range=[201,250],extra_unique=len(distinct),parameter_domain=domain,
                       raw_domain_cardinality=cardinality,sampling_status='PASS',rejections=dict(rejects),
                       domain_note='Finite declared domain; original-equivalent candidates rejected. Twenty distinct candidates checked; extra seeds sampled independently, not claimed unique.')
            examples.append(make_record(original,cfg,h,250,1,result))
        rows.append(row);print(qid,row['sampling_status'],flush=True)
    assert len(rows)==30
    return dict(scope=dict(indicators=[4],levels=[1,2,3]),counts=dict(Counter(r['status'] for r in rows)),
                stock_count=sum(r['stock_count'] for r in rows),extra_accepted=sum(r['extra_accepted'] for r in rows),rows=rows),examples

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report,examples=audit();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(report['counts'],report['stock_count'],report['extra_accepted'])
