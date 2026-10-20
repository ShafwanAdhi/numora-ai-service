"""Reproducible offline authoring of 20 audited originals; no generated variants saved."""
import csv
import json
import re
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import OriginalBank
from build_drill_1_5_level45_batch1 import safe_algebra
from test_drill_6_10_level45_batch1 import SELECTION, DATA, AUDIT

def entries():
    return json.loads(AUDIT.read_text(encoding='utf-8'))['entries']

def author(entry):
    i = entry['indicator']
    if i <= 7:
        from author_drill_6_7_level45_batch1 import author as make
    elif i <= 9:
        from author_drill_8_9_level45_batch1 import author as make
    else:
        from author_drill_10_level45_batch1 import author as make
    return make(entry)

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def main(*, SELECTION=SELECTION, DATA=DATA, author=author,
         batch='2026-10-20-indicators6-10-level45-batch1', expected_count=20, review=None):
    selected = [deepcopy(e) for e in entries() if e['source_number'] in SELECTION.get(e['indicator'], {}).get(e['level'], [])]
    assert len(selected) == expected_count
    if review is not None:
        selected = [review(e) for e in selected]
    DATA.mkdir(parents=True, exist_ok=True)
    source_index = json.loads((ROOT.parent/'docs/sources/incoming/2026-10-19-indikator-6-10/question-index.json').read_text(encoding='utf-8'))['questions']
    rows, metadata, groups = [], {}, {}
    for e in selected:
        if review is None:
            assert not e['issues'], e['audit_id']
            assert (e['validity'], e['answer_status'], e['explanation_status']) == ('VALID','CORRECT','CORRECT')
        s = e['source_projection'] = e.get('source_projection_resolved') or e['source_projection']
        s['format'] = e['format']
        qid = f"{e['format'].lower()}-{e['indicator']}-{e['level']}-{e['source_number']}"
        raw = next(q['extracted_content'] for q in source_index if
                   (q['source_indicator'],q['source_level'],q['source_question_number']) ==
                   (e['indicator'],e['level'],e['source_number']))
        cognitive = re.search(r'LEVEL KOGNITIF\s*:\s*(C\d)', raw, re.I)
        assert cognitive, qid
        rows.append(dict(id=qid, format=e['format'], cognitive_level=cognitive[1],
                         stem=safe_algebra(s['stem']), options_json=json.dumps([safe_algebra(t) for t in s['options']], ensure_ascii=False),
                         key=','.join(s['key']), version=1))
        groups.setdefault((e['indicator'], e['level']), []).append(qid)
        metadata[qid] = dict(generation_status='ACTIVE', reason='', source_number=e['source_number'],
            source_document='../../../docs/sources/incoming/2026-10-19-indikator-6-10/source.docx',
            source_document_sha256=e['source']['sha256'], source_location=e['source'], audit_id=e['audit_id'],
            original_explanation=s['explanation'], source_projection=s, source_text=raw,
            source_additional_notes=s.get('additional_notes', s.get('notes','')),
            approval_status='NOT_CURRICULUM_APPROVED', self_adjustment_enabled=False,
            batch=batch,
            notes=[f'{len(selected)} dari 100 soal level 4–5; nomor sumber tetap.',
                   'Rentang generator belum disetujui kurikulum atau dikalibrasi IRT.'])
        if s.get('category_labels'):
            metadata[qid]['category_labels'] = s['category_labels']
        if review is not None:
            metadata[qid]['source_review'] = e['generator_source_review']
            metadata[qid]['raw_source_projection'] = e['generator_raw_source_projection']
    with (DATA/'q0_bank.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    dump(DATA/'question_metadata.json', metadata)
    dump(DATA/'question_catalog.json', [dict(activity='DRILL', package_id='drill-1',indicator=i,source_level=l,question_ids=qs) for (i,l),qs in groups.items()])
    bank=OriginalBank(DATA/'q0_bank.csv')
    for e in selected:
        a=author(e); cfg=a.config(bank.get(a.qid)); folder=ROOT/'configs'/a.qid
        folder.mkdir(exist_ok=True)
        target=folder/'v1.json'
        if target.exists():
            assert json.loads(target.read_text(encoding='utf-8')) == cfg, f'Refusing to overwrite changed config: {target}'
        else:
            dump(target,cfg)
    print(f'Authored {len(selected)} originals/configs')

if __name__ == '__main__':
    main()
