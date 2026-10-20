"""Correct only mathematically determined keys, preserving raw evidence."""
from copy import deepcopy
from build_drill_6_10_level45_batch1 import main as build
from test_drill_6_10_level45_batch5 import SELECTION,DATA,KEYS
from author_drill_6_10_level45_batch5 import author

def review_entry(entry):
    e=deepcopy(entry)
    qid=f"{e['format'].lower()}-{e['indicator']}-{e['level']}-{e['source_number']}"
    assert qid in KEYS and e['validity']=='VALID'
    assert all(i['component'] in ('key','explanation') for i in e['issues'])
    raw=deepcopy(e.get('source_projection_resolved') or e['source_projection'])
    e.pop('source_projection_resolved',None)
    e['source_projection']=dict(deepcopy(raw),format=e['format'],key=KEYS[qid])
    e['generator_raw_source_projection']=raw
    e['generator_source_review']=dict(date='2026-10-21',status='ENGINEERING_REVIEWED_NOT_CURRICULUM_APPROVED',
        findings=e['issues'],source_validity=e['validity'],source_answer_status=e['answer_status'],
        actions=[f"Koreksi kunci {raw['key']} menjadi {KEYS[qid]} berdasarkan perhitungan independen; stimulus/opsi tidak berubah."])
    return e

if __name__=='__main__':
    build(SELECTION=SELECTION,DATA=DATA,author=author,expected_count=len(KEYS),
          batch='2026-10-21-indicators6-10-level45-batch5',review=review_entry)
