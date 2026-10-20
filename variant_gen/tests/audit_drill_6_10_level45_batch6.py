"""Capacity, provenance and immutable historical assets; never persist generated bodies."""
import csv
import hashlib
import json
from collections import Counter
from test_drill_6_10_level45_batch6 import ROOT,DATA,IDS,STOCK_ID,check_math
from bank import load_workspace_bank
from config_store import ConfigStore,validate_config
from engine import assemble,build_values
from filters import signature,validate_candidate
from lint import reproduce_original
from conceptual_stock import load_stock,stock_record
from author_drill_6_10_level45_batch6 import check_stock

OUTPUT=ROOT.parent/'docs/audits/2026-10-21-drill-6-10-level45-batch6'
BASELINE=ROOT/'tests/.batch6_10_batch6_baseline.json'

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()

def main():
    baseline=json.loads(BASELINE.read_text(encoding='utf8')) if BASELINE.exists() else json.loads((OUTPUT/'audit.json').read_text(encoding='utf8'))['baseline']
    if 'stock' in baseline:
        baseline['stock_hashes']=[digest(s) for s in baseline.pop('stock')['variants']]
    assert all(hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==h for p,h in baseline['hashes'].items()),'Historical assets changed'
    inventory=json.loads((ROOT/'data/conceptual_stock.json').read_text(encoding='utf8'))['variants']
    assert [digest(s) for s in inventory[:len(baseline['stock_hashes'])]]==baseline['stock_hashes'],'Historical stock changed'
    assert len(inventory)==len(baseline['stock_hashes'])+3
    bank=load_workspace_bank(ROOT/'data/q0_bank.csv'); configs=ConfigStore(ROOT/'configs')
    results=[]
    for qid in IDS:
        o=bank.get(qid); cfg,h=configs.load(qid)
        assert validate_config(cfg,o)==[] and reproduce_original(o,cfg)==([],[])
        signatures=set(); rejected=Counter()
        for k in range(31):
            c=assemble(cfg,build_values(cfg,lambda name,spec:k)); check_math(qid,c)
            reasons=validate_candidate(c,o,[])
            if reasons: rejected.update(reasons)
            else: signatures.add(signature(c['stem'],c['options']))
        assert len(signatures)==30,(qid,len(signatures))
        results.append(dict(question_id=qid,original_hash=o['hash'],config_hash=h,
            declared_inputs=31,exact_unique_capacity=len(signatures),rejections=dict(rejected),
            source_audit_id=o['metadata']['audit_id'],classification=o['classification']))
    stock=load_stock(ROOT/'data/conceptual_stock.json',bank)[STOCK_ID]
    assert len(stock)==3 and not configs.versions(STOCK_ID)
    for item in stock: check_stock(stock_record(bank.get(STOCK_ID),item))
    scope=[bank.get(f'{"pg" if n<6 else "mcma" if n<9 else "kategori"}-{i}-{l}-{n}')
           for i in range(6,11) for l in (4,5) for n in range(1,11)]
    modes=Counter('stock' if q['id']==STOCK_ID else 'generator' if configs.versions(q['id']) else 'unavailable' for q in scope)
    assert modes==dict(generator=99,stock=1)
    summary=dict(implemented_generators=17,implemented_stock_originals=1,stock_variants=3,
        cumulative_generators=99,cumulative_stock_originals=1,served_originals=100,target=100,pending=0,
        exhaustive_inputs=527,min_unique_capacity=30,protected_files_unchanged=len(baseline['hashes']),
        preserved_stock_variants=len(baseline['stock_hashes']),workspace_originals=len(bank.ids()))
    report=dict(summary=summary,entries=results,conceptual=dict(question_id=STOCK_ID,stock_count=3,
        original_hash=bank.get(STOCK_ID)['hash'],stock_hashes=[digest(s) for s in stock]),baseline=baseline)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
    (OUTPUT/'source-review.json').write_text(json.dumps({q:m['source_review'] for q,m in metadata.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with (OUTPUT/'pending.csv').open('w',encoding='utf8',newline='') as f:
        csv.DictWriter(f,fieldnames=['question_id','reason']).writeheader()
    text='''# Indikator 6–10 level 4–5: penyelesaian

Seluruh 100 soal Drill paket 1 terlayani: 99 generator dan 1 soal konseptual dengan 3 stok berulang.
Tahap ini menambah 17 generator serta stok `mcma-7-5-6`. Tidak ada soal antrean.
Generator dan stok tersedia pada katalog service, CLI, serta workbench lokal.

Revisi lokal minimum disetujui pengguna. Sumber mentah, pembahasan sumber, temuan audit,
dan perubahan sebelum/sesudah tersedia dalam metadata serta `source-review.json`.
Original lokal menampilkan naskah dan pembahasan revisi yang konsisten; DOCX/audit historis tidak diubah.

Semua 527 kombinasi input diperiksa dari teks hasil render; tiap generator mempunyai 30 varian unik valid.
Nilai original direproduksi pada k=0; nilai tersebut ditolak sebagai varian oleh validator yang sama.
Tiga stok konseptual diperiksa melalui derajat dan jumlah variabel persamaan.
Stok ini adalah inventaris editorial yang ditulis offline; hasil generate runtime tidak disimpan.
Stok dapat dipilih kembali tanpa penghitung pemakaian atau perubahan database.

Rentang belum dikalibrasi IRT atau disetujui kurikulum; self-adjustment tetap nonaktif.

## Batas verifikasi repo

Suite service API masih mempunyai satu kegagalan di luar cakupan batch ini:
`test_level45_local_generators_are_visible_but_review_drafts_are_not` merujuk
`variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch2/q0_bank.csv` yang belum tersedia.
Berkas/implementasi indikator 1–5 tersebut tidak diubah oleh pekerjaan ini.

```powershell
python -B variant_gen/tests/build_drill_6_10_level45_batch6.py
python -B variant_gen/tests/audit_drill_6_10_level45_batch6.py
python -B -m unittest discover -s variant_gen/tests -p 'test_drill_6_10_level45_batch*.py'
```

| Indikator | Generator level 4–5 | Soal dengan stok |
|---|---:|---:|
| 6 | 20 | 0 |
| 7 | 19 | 1 |
| 8 | 20 | 0 |
| 9 | 20 | 0 |
| 10 | 20 | 0 |

## Kapasitas generator tahap ini

| Soal | Varian unik valid |
|---|---:|
'''
    text+=''.join(f"| {r['question_id']} | {r['exact_unique_capacity']} |\n" for r in results)
    (OUTPUT/'README.md').write_text(text,encoding='utf8')
    print(json.dumps(summary))

if __name__=='__main__': main()
