"""Materialize the requested remaining 67: 39 valid + 28 quarantined review drafts."""
import csv
import importlib
import json
import re
from copy import deepcopy
from pathlib import Path

from level45_completion_common import ROOT, REPO, LIVE_DATA, DRAFT_DATA, entries, academic, key, safe_algebra
from bank import OriginalBank


def modules(indicator):
    suffix = 'i12' if indicator in (1,2) else 'i3' if indicator == 3 else 'i45'
    return (importlib.import_module(f'author_level45_{suffix}_completion'),
            importlib.import_module(f'oracle_level45_{suffix}_completion'))


def dump(path, value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def prepare_all():
    result = []
    for source, status in entries():
        draft = status == 'ACADEMIC_FOLLOW_UP'
        mod, oracle = modules(source['indicator'])
        proposed, reasons = mod.prepare(deepcopy(source),academic(source))
        assert key(proposed) == key(source), 'Do not move or renumber original questions'
        changes = {k:dict(before=source['source_projection'].get(k),after=v)
                   for k,v in proposed['source_projection'].items() if source['source_projection'].get(k)!=v}
        if draft:
            assert changes and reasons, (key(source), 'Draft needs explicit correction and rationale')
        else:
            assert not changes, (key(source),'Valid source must not be changed')
        result.append(dict(source=source,entry=proposed,draft=draft,reasons=reasons,changes=changes))
    assert len(result)==67 and sum(x['draft'] for x in result)==28
    return result


def build():
    prepared = prepare_all()
    index = json.loads((REPO/'docs/sources/incoming/2026-10-19-indikator-1-5/question-index.json').read_text(encoding='utf-8'))['questions']
    source_by_position = {(q['source_indicator'],q['source_level'],q['source_question_number']):q['extracted_content'] for q in index}
    for draft, folder in [(False,LIVE_DATA),(True,DRAFT_DATA)]:
        folder.mkdir(parents=True,exist_ok=True)
        selected = [p for p in prepared if p['draft']==draft]
        metadata, groups, rows, proposals = {}, {}, [], []
        for p in selected:
            e, source = p['entry'], p['source']
            s = e['source_projection']; qid = key(e)
            position = e['indicator'],e['level'],e['source_number']
            raw = source_by_position[position]
            label = re.search(r'Level Kognitif:\s*(C\d)',raw)
            rows.append(dict(id=qid,format=s['format'],cognitive_level=label[1] if label else '',
                stem=safe_algebra(s['stem']),options_json=json.dumps([safe_algebra(t) for t in s['options']],ensure_ascii=False),
                key=','.join(s['key']),version=2 if draft else 1))
            groups.setdefault(position[:2],[]).append(qid)
            metadata[qid] = dict(generation_status='HOLD_SOURCE' if draft else 'ACTIVE',
                reason='Draf usulan koreksi akademik dan generator; belum disetujui Kurikulum, tidak boleh diaktifkan.' if draft else '',
                source_number=e['source_number'],source_document_sha256=source['source']['sha256'],
                source_location=source['source'],audit_id=source['audit_id'],source_text=raw,
                original_explanation=s['explanation'],source_original_explanation=source['source_projection']['explanation'],
                source_original_key=source['source_projection']['key'],source_key_caption=source['source_projection']['key_caption'],
                source_additional_notes=source['source_projection']['additional_notes'],
                proposed_key_caption=s['key_caption'],proposed_additional_notes=s['additional_notes'],
                approval_status='PROPOSED_NOT_APPROVED' if draft else 'NOT_CURRICULUM_APPROVED',
                self_adjustment_enabled=False,review_only=draft,source_original_version=1,
                batch='2026-10-20-level45-completion',
                notes=['Nomor dan posisi sumber dipertahankan. Tidak ada publikasi database.',
                       'Draft akademik tidak masuk bank/config default.' if draft else 'Generator lokal, bukan approval kesetaraan kesulitan.'])
            if s.get('category_labels'):metadata[qid]['category_labels']=s['category_labels']
            if draft:
                metadata[qid]['proposed_original_version']=2
                metadata[qid]['correction_rationale']=p['reasons']
                proposals.append(dict(question_id=qid,audit_id=source['audit_id'],
                    approval_status='PROPOSED_NOT_APPROVED',source_location=source['source'],
                    source_original=source['source_projection'],proposed_original=s,
                    component_changes=p['changes'],rationale=p['reasons'],source_issues=academic(source)['issues']))
        with (folder/'q0_bank.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        dump(folder/'question_metadata.json',metadata)
        dump(folder/'question_catalog.json',[dict(activity='DRILL',package_id='drill-1',indicator=i,
            source_level=l,question_ids=qs) for (i,l),qs in groups.items()])
        if draft:dump(folder/'proposed_corrections.json',proposals)
        bank = OriginalBank(folder/'q0_bank.csv')
        for p in selected:
            e=p['entry']; qid=key(e); mod,_=modules(e['indicator'])
            original=bank.get(qid)
            config=mod.author(e).config(original)
            root=folder/'configs' if draft else ROOT/'configs'
            dest=root/qid;dest.mkdir(parents=True,exist_ok=True)
            dump(dest/'v1.json',config)
    print('Prepared 39 live generators and 28 quarantined proposals/configs')
    return prepared


if __name__=='__main__':
    build()
