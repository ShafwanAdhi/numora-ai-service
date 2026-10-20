"""Combine independent academic evidence; never author/approve runtime content."""
import csv
import json
from collections import Counter
from audit_original_questions import ROOT, OUT, read, write, digest, normalize
from validate_intake_06_10 import DEST as INTAKE, protected_hashes

DEST = OUT/'stage-08-academic-indicators-06-10'
PARTS = ['part-06-07.json', 'part-08-09.json', 'part-10.json']


def load_parts():
    rows = []
    for name in PARTS:
        data = read(DEST/name)
        for raw in data['entries']:
            row = dict(raw)
            options = row.get('option_evaluation', row.get('option_evaluations'))
            assert isinstance(options, list), (name, row.get('audit_id'))
            row['option_evaluation'] = [dict(o, truth=o.get('truth', o.get('result'))) for o in options]
            if isinstance(row['independent_solution'], dict):
                row['independent_solution_detail'] = row['independent_solution']
                row['independent_solution'] = json.dumps(row['independent_solution'], ensure_ascii=False)
            row['recommendation_detail'] = row.get('recommendation', '')
            row['recommendation'] = (
                'HOLD_FOR_SOURCE_REVISION' if row['validity'] == 'INVALID' else
                'HOLD_FOR_CLARIFICATION' if row['validity'] == 'UNCERTAIN' else
                'REVISE_KEY' if row['answer_status'] == 'INCORRECT' else
                'REVIEW_KEY' if row['answer_status'] in ('UNCERTAIN', 'MISSING') else
                'REVISE_EXPLANATION' if row['explanation_status'] == 'INCORRECT' else
                'REVIEW_EXPLANATION' if row['explanation_status'] in ('UNCERTAIN', 'MISSING') else
                'REVIEW_NOTES_OR_EXTRACTION' if row['issues'] else 'NO_BLOCKING_ACADEMIC_FINDING')
            rows.append(row)
    return sorted(rows, key=lambda r: (r['indicator'], r['level'], r['source_number']))


def validate_reviews(rows):
    sources = {q['audit_id']: q for q in read(INTAKE/'validation.json')['entries']}
    assert len(rows) == 250 and len({r['audit_id'] for r in rows}) == 250
    assert set(sources) == {r['audit_id'] for r in rows}
    for r in rows:
        q = sources[r['audit_id']]
        pos = (q['indicator'], q['level'], q['source_number'])
        assert pos == (r['indicator'], r['level'], r['source_number']), pos
        assert r['validity'] in ('VALID', 'INVALID', 'UNCERTAIN'), pos
        for field in ('answer_status', 'explanation_status'):
            assert r[field] in ('CORRECT', 'INCORRECT', 'UNCERTAIN', 'MISSING'), (pos, field)
        evaluations = r['option_evaluation']
        # All approved formats have 4 choices or 3 Category statements. Extra parsed
        # items must be resolved from native paragraphs, not silently treated as choices.
        expected = 3 if q['format'] == 'KATEGORI' else 4
        assert len(evaluations) == expected, (pos, len(evaluations), expected)
        assert all(o['truth'] in ('TRUE', 'FALSE', 'UNCERTAIN') for o in evaluations), pos
        assert all(o.get('text') and o.get('reason') for o in evaluations), pos
        expected_ids = [str(i+1) if q['format'] == 'KATEGORI' else chr(65+i) for i in range(expected)]
        assert [o.get('id') for o in evaluations] == expected_ids, (pos, 'Option IDs/order')
        projection = r.get('source_projection_resolved', r['source_projection'])
        assert [normalize(o['text']) for o in evaluations] == [normalize(t) for t in projection['options']], (pos, 'Option text')
        native_text = normalize(' '.join(p['text'] for p in q['paragraphs']))
        assert all(normalize(o['text']) in native_text for o in evaluations), (pos, 'Option absent from source paragraphs')
        correct = r['independently_correct_ids']
        if correct is not None:
            assert correct == [o['id'] for o in evaluations if o['truth'] == 'TRUE'], (pos, 'Correct IDs')
            assert not any(o['truth'] == 'UNCERTAIN' for o in evaluations), pos
        else:
            assert r['validity'] != 'VALID' or r['answer_status'] == 'UNCERTAIN', pos
            cases = r.get('conditional_correct_ids')
            assert cases and all(c.get('condition') and set(c['ids']) <= set(expected_ids) for c in cases), (pos, 'Missing conditional evidence')
        assert len(r['independent_solution']) >= 20, pos
        if r['validity'] == 'VALID' and q['format'] == 'PG':
            assert sum(o['truth'] == 'TRUE' for o in evaluations) == 1, pos
        if any(r[f] not in ('VALID', 'CORRECT') for f in ('validity', 'answer_status', 'explanation_status')):
            assert r['issues'], pos
        location = r.get('source', r.get('source_location'))
        assert location is not None and location == q['source'], (pos, 'Source locator')


def counts(rows):
    return dict(entries=len(rows), entries_with_findings=sum(bool(r['issues']) for r in rows),
                entries_with_nonclean_component_status=sum(any(r[f] not in ('VALID', 'CORRECT') for f in
                    ('validity', 'answer_status', 'explanation_status')) for r in rows),
                **{field: dict(Counter(r[field] for r in rows))
                for field in ('validity', 'answer_status', 'explanation_status', 'recommendation')})


def run():
    intake = read(INTAKE/'validation.json')
    baseline = intake['protected_inputs_sha256']
    assert protected_hashes() == baseline, 'Protected inputs changed after structure validation'
    rows = load_parts()
    validate_reviews(rows)
    sources = {q['audit_id']: q for q in intake['entries']}
    for r in rows:
        q = sources[r['audit_id']]
        r['source'] = q['source']
        r['format'] = q['format']
        r['intake_review_flags'] = q['review_flags']
        r['raw_parser_projection'] = {k: q[k] for k in ('stem', 'options', 'key', 'explanation', 'additional_notes', 'declared_key_texts')}
        r['raw_source_paragraphs'] = q['paragraphs']
        r['source_tables'] = q['tables']
        r['approval_status'] = 'NOT_CURRICULUM_APPROVED'
        r['generator_matching_status'] = 'NOT_EVALUATED_IN_THIS_STAGE'
    old = read(OUT/'reviews/06-10.json')['reviews']
    old = {(r['indicator'], r['level'], r['source_number']): r for r in old}
    deltas = []
    for r in rows:
        pos = (r['indicator'], r['level'], r['source_number'])
        previous = old[pos]
        changed = [f for f in ('validity', 'answer_status', 'explanation_status') if previous[f] != r[f]]
        if changed:
            deltas.append(dict(audit_id=r['audit_id'], indicator=pos[0], level=pos[1], source_number=pos[2],
                               changed_status_fields=changed,
                               old_status={f: previous[f] for f in changed}, new_status={f: r[f] for f in changed}))
    summary = dict(scope='Indikator 6–10, seluruh 250 soal', review_date='2026-10-20', **counts(rows),
                   by_indicator={str(i): counts([r for r in rows if r['indicator'] == i]) for i in range(6, 11)},
                   source_sha256=intake['summary']['source_sha256'], extraction_evidence_sha256=digest(INTAKE/'validation.json'),
                   academic_parts_sha256={name: digest(DEST/name) for name in PARTS},
                   protected_files_checked=len(baseline), protected_hashes_unchanged=True,
                   previous_review_status_differences=len(deltas),
                   limitations=['Audit sumber, bukan persetujuan Kurikulum/IRT.',
                                'Tidak mencocokkan atau mengubah generator/runtime.',
                                'Notasi/versi yang ambigu tetap bersyarat atau tertahan.'])
    write(DEST/'audit.json', dict(summary=summary,
        academic_part_evidence={name: {k:v for k,v in read(DEST/name).items() if k != 'entries'} for name in PARTS},
        methodology=dict(independence='Solusi dan penilaian setiap opsi dihitung ulang dari stimulus; review sementara dan generator tidak digunakan sebagai oracle.',
                         source_fidelity='Seluruh paragraf, persamaan OMML dan tabel dibandingkan dengan XML DOCX pada tahap 7. Proyeksi parser asli dan bukti paragraf tetap disertakan.',
                         key_policy='Kunci asli, koreksi inline dan hasil independen dibedakan; tidak memilih revisi atau memperbaiki sumber otomatis.',
                         old_review='reviews/06-10.json dipertahankan sebagai histori sementara yang tidak andal; I6L1Q1 salah identitas temuan. Perbandingan hanya dilakukan setelah audit baru selesai.'),
        previous_review_status_differences=deltas, entries=rows))
    fields = ['audit_id', 'indicator', 'level', 'source_number', 'format', 'validity', 'answer_status',
              'explanation_status', 'recommendation', 'independent_solution', 'issues']
    for name, selected in [('entries.csv', rows), ('follow-up.csv', [r for r in rows if r['issues']])]:
        with (DEST/name).open('w', encoding='utf-8-sig', newline='') as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            for r in selected:
                writer.writerow({k: json.dumps(r[k], ensure_ascii=False) if isinstance(r[k], (list, dict)) else r[k] for k in fields})
    report = ['# Tahap 8 — Audit akademik indikator 6–10', '',
              '**250 soal diperiksa**, seluruh opsi/pernyataan, kunci, pembahasan dan catatan. '
              'Sumber tetap utuh; seluruh koreksi di laporan adalah **PROPOSED**, belum disahkan Kurikulum.', '',
              '| Indikator | Diperiksa | Tanpa tindak lanjut | Perlu tindak lanjut |', '|---|---:|---:|---:|']
    for i in range(6, 11):
        subset = [r for r in rows if r['indicator'] == i]
        clean = sum(not r['issues'] for r in subset)
        report.append(f'| {i} | 50 | {clean} | {50-clean} |')
    report += ['', '| Komponen | Benar/valid | Bermasalah | Belum pasti | Tidak tersedia |', '|---|---:|---:|---:|---:|']
    for field, label, good, bad in [('validity', 'Soal', 'VALID', 'INVALID'), ('answer_status', 'Kunci', 'CORRECT', 'INCORRECT'),
                                     ('explanation_status', 'Pembahasan', 'CORRECT', 'INCORRECT')]:
        c = summary[field]
        report.append(f"| {label} | {c.get(good,0)} | {c.get(bad,0)} | {c.get('UNCERTAIN',0)} | {c.get('MISSING',0)} |")
    report += ['', 'Hitungan komponen berdiri sendiri; jangan dijumlahkan menjadi jumlah soal bermasalah.', '',
               '## Temuan per soal', '', '| Lokasi | Status soal / kunci / pembahasan | Bukti dan usulan |', '|---|---|---|']
    for r in rows:
        if not r['issues']:
            continue
        details = ' '.join(f"{x.get('component','')}: {x.get('evidence','')} Usulan: {x.get('proposal','')}" for x in r['issues'])
        details = details.replace('|', '\\|').replace('\n', ' ')
        report.append(f"| I{r['indicator']} L{r['level']} Q{r['source_number']} | {r['validity']} / {r['answer_status']} / {r['explanation_status']} | {details} |")
    report += ['', '## Batas dan reproduksi', '',
               'Review sementara lama tidak dipakai sebagai oracle. Pada I6 L1 Q1, sumber membahas bahan kue dengan hasil '
               '375 gram, tetapi review lama menempelkan temuan persediaan makanan hari ke-10. Review baru mempertahankan identitas sumber per audit_id. '
               f"Ada {len(deltas)} entri dengan status berbeda dari review sementara; itu bukan seluruh ukuran perubahan bukti.", '',
               'Sebanyak 21 entri proyeksi parser ditandai untuk pemeriksaan batas opsi/pembahasan pada '
               '[tahap 7](../stage-07-extraction-06-10/README.md). Paragraf asli, tabel, proyeksi parser dan hasil pembacaan akademik '
               'tersimpan terpisah. Pembahasan inline tidak otomatis dinyatakan hilang.', '',
               f'Hash seluruh {len(baseline)} berkas sumber/bank/config/layanan tetap sama. '
               'Tidak ada koreksi sumber, perubahan bank/config, publikasi DB, API atau pemetaan runtime.', '',
               '[JSON lengkap 250 soal](audit.json) · [CSV seluruh soal](entries.csv) · [CSV tindak lanjut](follow-up.csv).', '',
               '```powershell', 'python -B variant_gen/tests/validate_intake_06_10.py',
               'python -B variant_gen/tests/audit_indicators_06_07_academic.py',
               'python -B variant_gen/tests/audit_indicators_08_09_academic.py',
               'python -B variant_gen/tests/audit_indicator_10_academic.py',
               'python -B variant_gen/tests/audit_indicators_06_10_academic.py',
               'python -B -m unittest discover -s variant_gen/tests -p test_audit_indicators_06_10.py -q', '```', '',
               'Audit indikator 11–15 dan pencocokan generator indikator 6–10 berada di luar tahap ini.', '']
    (DEST/'README.md').write_text('\n'.join(report), encoding='utf-8')
    assert protected_hashes() == baseline
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    run()
