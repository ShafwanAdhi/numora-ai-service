"""Read-only DOCX fidelity check; suspicious parser projections stay explicit."""
import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from audit_original_questions import ROOT, OUT, W, digest, read, write, flatten, source_entries
from validate_intake_01_05 import M, tree_signature, native_projection

FOLDER = ROOT/'docs/sources/incoming/2026-10-19-indikator-6-10'
DEST = OUT/'stage-07-extraction-06-10'


def protected_hashes():
    assets = {p.relative_to(ROOT).as_posix(): digest(p)
            for folder in ('variant_gen/data', 'variant_gen/configs', 'numora_service', 'docs/sources/incoming')
            for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assets.update({p.relative_to(ROOT).as_posix(): digest(p) for p in (ROOT/'variant_gen').glob('*.py')})
    return assets


def check_tables(nodes, blocks):
    nodes = [n for n in nodes if n.tag in (W+'p', W+'tbl')]
    assert len(nodes) == len(blocks)
    for node, block in zip(nodes, blocks):
        if node.tag == W+'p':
            assert block['type'] == 'paragraph'
            continue
        assert block['type'] == 'table'
        rows = node.findall(W+'tr')
        assert len(rows) == len(block['rows'])
        for row, extracted in zip(rows, block['rows']):
            cells = row.findall(W+'tc')
            assert len(cells) == len(extracted)
            for cell, projected in zip(cells, extracted):
                span = cell.find(W+'tcPr/'+W+'gridSpan')
                merge = cell.find(W+'tcPr/'+W+'vMerge')
                assert projected['col_span'] == (int(span.get(W+'val', '1')) if span is not None else 1)
                assert projected['vertical_merge'] == (merge.get(W+'val', 'continue') if merge is not None else None)
                check_tables(list(cell), projected['blocks'])


def validate_spans(index, blocks):
    for n, q in enumerate(index):
        start, end = q['body_block_start_index'], q['body_block_end_exclusive']
        assert 0 <= start < end <= len(blocks)
        next_start = index[n+1]['body_block_start_index'] if n+1 < len(index) else len(blocks)
        assert end <= next_start
        gap = blocks[end:next_start]
        same_level = n+1 < len(index) and (q['source_indicator'], q['source_level']) == (
            index[n+1]['source_indicator'], index[n+1]['source_level'])
        if same_level or n+1 == len(index):
            assert not gap, (n, 'Question span truncated')
        else:
            assert len(gap) == 3
            assert all(b['type'] == 'paragraph' for b in gap)
            assert re.match(r'^Indikator\s+\d+\.', gap[0]['text'].strip())
            assert re.fullmatch(r'LEVEL\s+[1-5]', gap[1]['text'].strip())
            assert not gap[2]['text'].strip()


def validate_document():
    manifest, doc = read(FOLDER/'manifest.json'), read(FOLDER/'extracted.json')
    assert digest(FOLDER/'source.docx') == manifest['source_sha256']
    with zipfile.ZipFile(FOLDER/'source.docx') as archive:
        native = ET.fromstring(archive.read('word/document.xml'))
        media = [n for n in archive.namelist() if n.startswith('word/media/') and not n.endswith('/')]
    equations = list(native.iter(M+'oMath'))
    assert len(equations) == len(doc['equations']) == manifest['counts']['equations']
    for node, extracted in zip(equations, doc['equations']):
        assert tree_signature(node) == tree_signature(ET.fromstring(extracted['ooxml'])), extracted['id']
    math_map = {id(node): e for node, e in zip(equations, doc['equations'])}
    paragraphs, raw = list(flatten(doc['blocks'])), list(native.iter(W+'p'))
    assert len(paragraphs) == len(raw) == manifest['counts']['paragraphs']
    for node, paragraph in zip(raw, paragraphs):
        assert native_projection(node, math_map) == paragraph['text'], paragraph['paragraph_index']
        assert [math_map[id(m)]['id'] for m in node.iter(M+'oMath')] == paragraph['math_ids']
    check_tables(list(native.find(W+'body')), doc['blocks'])
    assert len(list(native.iter(W+'tbl'))) == manifest['counts']['tables']
    assert len(media) == manifest['counts']['embedded_media'] == 0
    entries = source_entries(FOLDER)
    index = read(FOLDER/'question-index.json')['questions']
    assert len(entries) == len(index) == 250
    assert {(q['indicator'], q['level'], q['source_number']) for q in entries} == {
        (i, level, number) for i in range(6, 11) for level in range(1, 6) for number in range(1, 11)}
    assert len({q['audit_id'] for q in entries}) == 250
    validate_spans(index, doc['blocks'])
    for q in index:
        first = doc['blocks'][q['body_block_start_index']]
        assert first['paragraph_index'] == q['paragraph_start_index']
        assert first['text'].strip() == q['source_heading']
    rows = []
    for q in entries:
        flags = list(q['parse_flags'])
        if len(q['options']) != (3 if q['format'] == 'KATEGORI' else 4):
            flags.append('OPTION_BOUNDARY_REVIEW')
        if q['explanation'] is None:
            flags.append('EXPLANATION_BOUNDARY_REVIEW')
        if q['key'] is None:
            flags.append('KEY_BOUNDARY_REVIEW')
        rows.append(dict(q, structural_status='REVIEW_REQUIRED' if flags else 'STRUCTURE_VERIFIED',
                         review_flags=flags, academic_status='SEPARATE_STAGE_08'))
    summary = dict(scope='Validasi ekstraksi indikator 6–10', source_sha256=manifest['source_sha256'],
                   source_entries=250, unique_positions=250, paragraphs_checked=len(raw),
                   tables_checked=len(list(native.iter(W+'tbl'))), omml_equations_checked=len(equations),
                   embedded_media=len(media), formats=dict(Counter(q['format'] for q in rows)),
                   structural_status=dict(Counter(q['structural_status'] for q in rows)),
                   native_numbered_paragraphs=sum(bool(p.get('native_label')) for q in entries for p in q['paragraphs']),
                   limitation='Salinan OOXML identik; proyeksi teks memakai LaTeX intake, bukan renderer OMML independen. Makna notasi dan batas opsi/pembahasan diperiksa terpisah pada tahap akademik.')
    return dict(summary=summary, entries=rows)


def run():
    before = protected_hashes()
    result = validate_document()
    assert protected_hashes() == before
    result['summary'].update(protected_files_checked=len(before), protected_hashes_unchanged=True)
    result['protected_inputs_sha256'] = before
    DEST.mkdir(parents=True, exist_ok=True)
    write(DEST/'validation.json', result)
    with (DEST/'entries.csv').open('w', encoding='utf-8-sig', newline='') as output:
        fields = ['audit_id', 'indicator', 'level', 'source_number', 'format', 'structural_status', 'review_flags', 'source']
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for q in result['entries']:
            writer.writerow({k: json.dumps(q[k], ensure_ascii=False) if isinstance(q[k], (dict, list)) else q[k] for k in fields})
    summary = result['summary']
    (DEST/'README.md').write_text(
        '# Tahap 7 — Validasi ekstraksi indikator 6–10\n\n'
        '**250 posisi unik**; 5 indikator × 5 level × 10 soal. Hash DOCX sesuai manifest.\n\n'
        f"Seluruh {summary['paragraphs_checked']} paragraf, {summary['tables_checked']} tabel (termasuk span/merge), "
        f"{summary['omml_equations_checked']} persamaan OMML dibandingkan dengan XML arsip. Tidak ada gambar tertanam.\n\n"
        f"Status proyeksi: {summary['structural_status']}. Opsi berlebih dan pembahasan yang tidak terpisah otomatis "
        'ditandai REVIEW_REQUIRED; bukan dianggap hilang atau dipilih salah satu secara otomatis. '
        'Penomoran asli dan seluruh paragraf dipertahankan dalam JSON.\n\n'
        'Validasi ini membuktikan kesetiaan struktur, bukan kebenaran akademik. Pembacaan batas yang ditandai '
        'dan audit matematika tersedia pada [tahap 8](../stage-08-academic-indicators-06-10/README.md).\n\n'
        'XML OMML tersimpan identik dengan arsip; proyeksi teks memakai LaTeX intake yang sama, sehingga '
        'bukan pembuktian independen kesetaraan LaTeX–OMML. Makna notasi ditinjau pada audit akademik.\n\n'
        f"Hash {len(before)} berkas sumber/bank/config/layanan tetap sama. [JSON](validation.json) · [CSV](entries.csv).\n\n"
        'Reproduksi: `python -B variant_gen/tests/validate_intake_06_10.py`.\n', encoding='utf-8')
    print(json.dumps(result['summary'], ensure_ascii=True, indent=2))


if __name__ == '__main__':
    run()
