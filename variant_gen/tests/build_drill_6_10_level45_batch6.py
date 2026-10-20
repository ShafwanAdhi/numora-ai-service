"""Offline authoring only: approved revisions, configs and finite conceptual inventory."""
import csv
import json
import re
from copy import deepcopy
from build_drill_6_10_level45_batch1 import main as build,entries,dump
from author_drill_6_10_level45_batch6 import revise,author
from test_drill_6_10_level45_batch6 import ROOT,DATA,SELECTION,STOCK_ID
from bank import OriginalBank

def main():
    build(SELECTION=SELECTION,DATA=DATA,author=author,review=revise,expected_count=17,
          batch='2026-10-21-indicators6-10-level45-batch6')
    e=next(e for e in entries() if (e['indicator'],e['level'],e['source_number'])==(7,5,6))
    assert not e['issues'] and e['validity']=='VALID' and e['answer_status']=='CORRECT'
    s=deepcopy(e.get('source_projection_resolved') or e['source_projection'])
    s['format']=e['format']
    source=json.loads((ROOT.parent/'docs/sources/incoming/2026-10-19-indikator-6-10/question-index.json').read_text(encoding='utf8'))['questions']
    text=next(q['extracted_content'] for q in source if (q['source_indicator'],q['source_level'],q['source_question_number'])==(7,5,6))
    with (DATA/'q0_bank.csv').open(encoding='utf8',newline='') as f:
        reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
    rows.append(dict(id=STOCK_ID,format='MCMA',cognitive_level=re.search(r'LEVEL KOGNITIF\s*:\s*(C\d)',text)[1],
        stem=s['stem'],options_json=json.dumps(s['options'],ensure_ascii=False),key=','.join(s['key']),version=1))
    with (DATA/'q0_bank.csv').open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
    metadata[STOCK_ID]=dict(generation_status='DEFERRED_CONCEPTUAL',reason='Klasifikasi PLSV menggunakan tiga stok konseptual terverifikasi yang dapat dipakai ulang.',
        source_number=6,source_document='../../../docs/sources/incoming/2026-10-19-indikator-6-10/source.docx',
        source_document_sha256=e['source']['sha256'],source_location=e['source'],audit_id=e['audit_id'],
        original_explanation=s['explanation'],source_projection=s,raw_source_projection=deepcopy(s),source_text=text,
        approval_status='NOT_CURRICULUM_APPROVED',self_adjustment_enabled=False,
        source_review=dict(authorization='USER_APPROVED_MINIMUM_LOCAL_REVISION',actions=['Sumber valid dipertahankan; tiga stok klasifikasi PLSV ditulis dan diperiksa secara matematis.']),
        batch='2026-10-21-indicators6-10-level45-batch6')
    dump(DATA/'question_metadata.json',metadata)
    catalog=json.loads((DATA/'question_catalog.json').read_text(encoding='utf8'))
    group=next(g for g in catalog if g['indicator']==7 and g['source_level']==5)
    group['question_ids'].append(STOCK_ID)
    for group in catalog: group['question_ids'].sort(key=lambda q:int(q.rsplit('-',1)[1]))
    dump(DATA/'question_catalog.json',catalog)
    original=OriginalBank(DATA/'q0_bank.csv').get(STOCK_ID)
    path=ROOT/'data/conceptual_stock.json'
    payload=json.loads(path.read_text(encoding='utf8'))
    families=[
        (r'4x+3=19',r'x^{2}-9=0',r'\frac{x-2}{3}=4',r'3x+y=15'),
        (r'7x-4=3x+12',r'2x^{2}=18',r'\frac{2x+5}{3}=7',r'x-2y=6'),
        (r'5(x-1)=2x+7',r'(x-3)(x+3)=0',r'\frac{x+6}{4}=5',r'2x+3y=12')]
    stocks=[]
    for index,equations in enumerate(families,1):
        stem='Evaluasi klasifikasi persamaan berikut.\n'+'\n'.join(f'({label}) ${equation}$' for label,equation in zip(('i','ii','iii','iv'),equations))+'\nManakah pernyataan yang benar? (Jawaban benar lebih dari satu)'
        options=['Persamaan (i) dan (iii) merupakan Persamaan Linear Satu Variabel (PLSV).',
                 'Persamaan (ii) merupakan PLSV karena hanya memiliki satu variabel.',
                 'Persamaan (iv) bukan PLSV karena melibatkan dua variabel.',
                 'Persamaan (iii) bukan PLSV karena bentuknya pecahan.']
        stocks.append(dict(variant_id=f'{STOCK_ID}:stock-{index:02d}',question_id=STOCK_ID,
            stock_index=index,stock_version=1,original_hash=original['hash'],original_version=original['version'],
            stem=stem,options=[dict(id=chr(65+j),text=t) for j,t in enumerate(options)],key='A,C',
            explanation='A benar: (i) dan (iii) memiliki satu variabel berderajat satu setelah penyederhanaan. B salah: (ii) berderajat dua. C benar: (iv) memiliki dua variabel. D salah: penyebut konstan tidak mengubah derajat linear.',
            variation_note=f'Keluarga klasifikasi {index}: linear biasa, kuadrat, pecahan dengan penyebut konstan, serta dua variabel.',
            review_status='VERIFIED',review_note='Pemeriksaan rekayasa: jumlah variabel dan derajat polinom diperiksa dari teks render. Belum approval kurikulum atau kalibrasi IRT.'))
    existing=[s for s in payload['variants'] if s['question_id']==STOCK_ID]
    assert not existing or existing==stocks,'Refusing to overwrite changed conceptual stock'
    if not existing:
        payload['variants'].extend(stocks); dump(path,payload)
    print('18 originals: 17 generators and one conceptual question with three reusable stock variants.')

if __name__=='__main__': main()
