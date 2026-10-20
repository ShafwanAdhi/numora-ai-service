"""Append an explicit v3 repair; preserve CSV, previous revisions and conceptual stocks."""
import json
from copy import deepcopy
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from bank import OriginalBank

QID='mcma-15-2-8'
DATA=ROOT/'data/drill-1-indicators-11-15'

def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    original=OriginalBank(DATA/'q0_bank.csv').get(QID)
    if original['version']==2:
        def row(o):
            return dict(id=o['id'],format=o['format'],cognitive_level=o['cognitive_level'],stem=o['stem'],
                options_json=json.dumps([v['text'] for v in o['options']],ensure_ascii=False),
                key=','.join(v['id'] for v in o['options'] if v['correct']),version=str(o['version']))
        revised=deepcopy(original)
        revised['version']=3
        revised['stem']=original['stem'].replace(', BC = 9 cm','')
        revised['options'][1]['text']='Panjang QR adalah 1,5 kali panjang BC.'
        metadata=deepcopy(original['metadata'])
        explanation='∠C = 180° - 75° - 65° = 40°, sehingga ∠R = 40°, bukan 65°. Skala PQ/AB = 9/6 = 1,5. QR = 1,5 kali BC; keliling PQR = 1,5 kali keliling ABC. Luas ABC : PQR = 4 : 9, bukan 2 : 3. B,D benar.'
        reason='Revisi lokal saat pengguna meminta generator nonkonseptual: hapus BC=9 yang bertentangan dengan sudut; opsi B memakai rasio QR/BC, sehingga data konsisten tanpa menambahkan trigonometri.'
        metadata.update(generation_status='ACTIVE',generator_status='IMPLEMENTED',source_review_status='LOCAL_REVISION_ENGINEERING_REVIEWED',
            reason=reason,original_explanation=explanation,raw_source_explanation=original['metadata']['original_explanation'],
            approval_status='NOT_CURRICULUM_APPROVED',self_adjustment_enabled=False,
            source_review=dict(date='2026-10-21',reason=reason,source_version=2,local_version=3,
                source_document_unchanged=True,source_text_preserved=True))
        revision=dict(question_id=QID,original_version=2,replacement_version=3,original_row=row(original),replacement_row=row(revised),
            original_metadata=original['metadata'],replacement_metadata=metadata,source_document_sha256=metadata['source_document_sha256'],reason=reason)
        ledger=DATA/'original_revisions.jsonl'
        with ledger.open('a',encoding='utf8',newline='\n') as f:
            f.write(json.dumps(revision,ensure_ascii=False)+'\n')
        all_metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
        all_metadata[QID]=metadata
        dump(DATA/'question_metadata.json',all_metadata)
    original=OriginalBank(DATA/'q0_bank.csv').get(QID)
    assert original['version']==3 and original['metadata']['generation_status']=='ACTIVE'
    cfg=dict(question_id=QID,config_version=1,original_hash=original['hash'],original_values={'k':0},
        variables=dict(k=dict(gen='range',range=[0,30]),pq=dict(gen='derived',expr='9+3*k',fmt='id'),
            ratio=dict(gen='derived',expr='(3+k)/2',fmt='id',decimals=1),
            denominator=dict(gen='derived',expr='3+k',fmt='id'),area_denominator=dict(gen='derived',expr='(3+k)**2',fmt='id')),
        constraints=[],stem=original['stem'].replace('PQ = 9 cm','PQ = {pq} cm'),
        options=[dict(o,text=o['text'].replace('1,5','{ratio}').replace('2 : 3','2 : {denominator}')) for o in original['options']],
        explanation='∠C = 180° - 75° - 65° = 40°, sehingga ∠R = 40°, bukan 65°. Skala PQ/AB = {pq}/6 = {ratio}. QR = {ratio} kali BC; keliling PQR = {ratio} kali keliling ABC. Luas ABC : PQR = 4 : {area_denominator}, bukan 2 : {denominator}. B,D benar.',
        shuffle=False,max_draws=1000)
    folder=ROOT/'configs'/QID; folder.mkdir(exist_ok=True); target=folder/'v1.json'
    if target.exists(): assert json.loads(target.read_text(encoding='utf8'))==cfg,'Refusing to overwrite changed config'
    else: dump(target,cfg)
    print('mcma-15-2-8: local original v3, generator v1; conceptual inventory unchanged.')

if __name__=='__main__': main()
