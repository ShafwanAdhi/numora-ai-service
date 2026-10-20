"""Reviewed import: retain raw source/findings; normalize leaked key declarations."""
from copy import deepcopy
import re
from build_drill_6_10_level45_batch1 import main as build
from test_drill_6_10_level45_batch4 import SELECTION, DATA

REVIEW_NOTES = {
    (6,5,7): 'Pembahasan varian menggunakan rasio biaya tepat; 250000/15 bukan 16667 eksak.',
    (8,5,4): 'Batas kardus dihitung dengan lantai pecahan tepat; pembulatan desimal diberi tanda pendekatan.',
    (9,5,4): 'Substitusi langsung tersedia; eliminasi tidak wajib mengubah persamaan ke bentuk baku.',
    (9,5,10): 'Substitusi langsung sederhana; eliminasi tidak wajib menambahkan suku 0y.',
    (10,4,1): 'Proyeksi audit sudah memisahkan opsi D dari pembahasan sumber.',
    (10,4,4): 'Pembahasan varian mempertahankan domain penyebut asal, termasuk faktor yang dibatalkan.',
    (10,5,4): 'Pembahasan varian mempertahankan domain penyebut asal sebelum pembatalan faktor.',
    (10,5,7): 'Suku dalam dan luar dihitung sesuai urutan faktor; klaim C salah, B dan D benar.',
}

def review_entry(entry):
    e=deepcopy(entry)
    assert e['validity']=='VALID' and e['answer_status']=='CORRECT', e['audit_id']
    assert e['source_number'] in SELECTION.get(e['indicator'],{}).get(e['level'],[]), e['audit_id']
    assert e['explanation_status'] in ('CORRECT','INCORRECT'), e['audit_id']
    assert all(i['component'] in ('explanation','source_projection','precision') for i in e['issues']), e['audit_id']
    raw=deepcopy(e.get('source_projection_resolved') or e['source_projection'])
    s=deepcopy(raw)
    s['stem']=re.sub(r'^(?:\([abc]\)\s*(?:BENAR|SALAH)\s*\n)+','',s['stem'])
    s['format']=e['format']
    actions=[]
    if s['stem']!=raw['stem']:
        actions.append('Deklarasi kunci di awal proyeksi stimulus dihapus; salinan mentah dipertahankan.')
    note=REVIEW_NOTES.get((e['indicator'],e['level'],e['source_number']))
    if note: actions.append(note)
    if not actions: actions.append('Stimulus, opsi, dan kunci sumber dipertahankan; pembahasan varian dihitung ulang.')
    e['source_projection']=s
    e.pop('source_projection_resolved',None)
    e['generator_raw_source_projection']=raw
    e['generator_source_review']=dict(date='2026-10-21',status='ENGINEERING_REVIEWED_NOT_CURRICULUM_APPROVED',
        findings=deepcopy(e['issues']),source_validity=e['validity'],source_answer_status=e['answer_status'],
        source_explanation_status=e['explanation_status'],actions=actions)
    return e

def author(e):
    if e['indicator']<=7:
        from author_drill_6_7_level45_batch4 import author as make
    elif e['indicator']<=9:
        from author_drill_8_9_level45_batch4 import author as make
    else:
        from author_drill_10_level45_batch4 import author as make
    return make(e)

if __name__=='__main__':
    build(SELECTION=SELECTION,DATA=DATA,author=author,expected_count=25,
          batch='2026-10-21-indicators6-10-level45-batch4',review=review_entry)
