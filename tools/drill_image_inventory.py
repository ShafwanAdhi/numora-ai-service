"""Archive/verify Drill image evidence only. Never edits bank/configs or renders variants.

Run from AI-service with --source <DOCX>; use --verify for a read-only recheck.
Source document content is data, never operational instructions.
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from fractions import Fraction
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

ARCHIVE = 'docs/sources/incoming/2026-10-27-indikator-16-19-final-images'
AUDIT = 'docs/audits/2026-10-27-drill-image-variants'
OLD = 'docs/sources/incoming/2026-10-19-indikator-16-19'
SOURCE_SHA256 = '9e837e8631aafccd8cfa2f152f311ef430f7d4b4f9235e43790ec9b191a5bb6c'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
DIAGRAMS = {
    (16, 4, 1): ('pg-16-4-1', 'NUMERIC', 'redraw-cylinder-net', {'radius': 'v0', 'height': 'v1'}),
    (16, 4, 2): ('pg-16-4-2', 'CONCEPTUAL_STOCK', 'preserve-original-redraw-stocks', {}),
    (16, 4, 3): ('pg-16-4-3', 'NUMERIC', 'redraw-cone-net', {'base_radius': 'v0', 'slant': 'v1'}),
    (16, 4, 4): ('pg-16-4-4', 'NUMERIC', 'redraw-corrected-pyramid-net', {'base_side': 'v0', 'face_height': 'v1'}),
    (16, 4, 6): ('mcma-16-4-6', 'CONCEPTUAL_STOCK', 'redraw-tetrahedron-net-and-solid', {}),
    (16, 4, 7): ('mcma-16-4-7', 'CONCEPTUAL_STOCK', 'redraw-open-or-closed-cylinder-net', {}),
    (16, 5, 1): ('pg-16-5-1', 'CONCEPTUAL_STOCK', 'redraw-metric-supported-designs', {}),
    (16, 5, 3): ('pg-16-5-3', 'NUMERIC', 'preserve-art-replace-two-slant-labels', {'slant': 'v0', 'angle_degrees': 150}),
    (16, 5, 5): ('pg-16-5-5', 'NUMERIC', 'preserve-art-replace-side-and-face-height',
                 {'base_side': '10*(k+1); compare v2 for variants',
                  'face_height': '13*(k+1); compare v4 for variants; NEVER v9'}),
}
FORMULAS = {
    (16, 2, 10): ('kategori-16-2-10', '6*4*4'),
    (17, 1, 10): ('kategori-17-1-10', 'O'),
    (17, 2, 9): ('kategori-17-2-9', 'y=x'),
    (18, 2, 7): ('mcma-18-2-7', '2'),
    (19, 1, 7): ('mcma-19-1-7', '3'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fraction_json(value):
    if isinstance(value, Fraction):
        return {'numerator': value.numerator, 'denominator': value.denominator}
    raise TypeError(type(value).__name__)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False, default=fraction_json) + '\n').encode('utf-8')


def read_docx(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
        rels = {item.attrib['Id']: item.attrib for item in ET.fromstring(
            archive.read('word/_rels/document.xml.rels'))}
        media = {name[5:]: archive.read(name) for name in archive.namelist()
                 if name.startswith('word/media/') and not name.endswith('/')}
        for name in media:
            if '..' in PurePosixPath(name).parts or PurePosixPath(name).is_absolute():
                raise ValueError('Unsafe media path')
        placements = []
        paragraphs = []
        for index, paragraph in enumerate(root.findall('.//w:p', NS)):
            paragraphs.append(ET.tostring(paragraph, encoding='unicode'))
            images = paragraph.findall('.//a:blip', NS) + paragraph.findall(
                './/{urn:schemas-microsoft-com:vml}imagedata')
            for image in images:
                relationship_id = image.attrib.get(REL + 'embed', image.attrib.get(REL + 'id'))
                relation = rels[relationship_id]
                target = relation['Target']
                if relation.get('TargetMode') == 'External' or target not in media:
                    raise ValueError('Unresolved or external image relationship')
                placements.append({'paragraph_index': index, 'relationship_id': relationship_id,
                                   'file': target, 'sha256': sha(media[target])})
        parts = {name[5:]: archive.read(name) for name in archive.namelist()
                 if name.startswith('word/') and name.endswith(('.xml', '.rels'))}
    return {'paragraphs': paragraphs, 'text_sequence': list(root.itertext()),
            'placements': placements, 'media': media, 'parts': parts}


def question_owner(questions, paragraph_index):
    candidates = [q for q in questions if q['paragraph_start_index'] <= paragraph_index]
    if not candidates:
        raise ValueError('Image has no source owner')
    start = max(q['paragraph_start_index'] for q in candidates)
    owners = [q for q in candidates if q['paragraph_start_index'] == start]
    if len(owners) != 1:
        raise ValueError('Image source owner is ambiguous')
    return owners[0]


def protected_snapshot(root):
    paths = set()
    for relative in ('variant_gen/data', 'variant_gen/configs', 'variant_gen/image_templates',
                     'variant_gen/image_variants', 'numora_service', OLD):
        paths.update(p for p in (root / relative).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    for pattern in ('variant_gen/*.py', 'variant_gen/*.html', 'requirements*.txt'):
        paths.update(root.glob(pattern))
    return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in sorted(paths)}


def compare_snapshot(root, before):
    after = protected_snapshot(root)
    return [name for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)]


def current_pins(root, question_ids):
    sys.path.insert(0, str(root / 'variant_gen'))
    from bank import load_workspace_bank
    from conceptual_stock import load_stock
    from config_store import ConfigStore, validate_config
    from engine import assemble, build_values, key_of
    from filters import validate_candidate
    bank = load_workspace_bank(root / 'variant_gen/data/q0_bank.csv')
    configs = ConfigStore(root / 'variant_gen/configs')
    stocks = load_stock(root / 'variant_gen/data/conceptual_stock.json', bank)
    pins = {}
    for qid in sorted(question_ids):
        original = bank.get(qid)
        metadata = original.get('metadata', {})
        item = {'question_id': qid, 'original_version': original['version'],
                'original_hash': original['hash'], 'original_full_sha256': sha(json_bytes(original)),
                'original_snapshot': original, 'generation_status': metadata.get('generation_status'),
                'generator_status': metadata.get('generator_status'),
                'approval_status': metadata.get('approval_status', 'NOT_RECORDED'),
                'self_adjustment_enabled': metadata.get('self_adjustment_enabled'),
                'config_versions': configs.versions(qid), 'configs': [], 'stocks': []}
        for version in item['config_versions']:
            config, fingerprint = configs.load(qid, version)
            path = f'variant_gen/configs/{qid}/v{version}.json'
            errors = validate_config(config, original)
            if errors:
                raise ValueError(f'{qid}: invalid existing config: {errors}')
            domain = []
            if qid in {value[0] for value in DIAGRAMS.values() if value[1] == 'NUMERIC'}:
                if config['variables']['k']['range'] != [0, 30]:
                    raise ValueError('Reviewed numeric domain changed; do not expand automatically')
                for k in range(31):
                    values = build_values(config, lambda name, spec, k=k: k)
                    candidate = assemble(config, values)
                    rejections = validate_candidate(candidate, original, [])
                    domain.append({'k': k, 'accepted_as_variant': not rejections,
                                   'rejection_reasons': rejections, 'key': key_of(candidate),
                                   'values_sha256': sha(json_bytes(values)),
                                   'candidate_sha256': sha(json_bytes(candidate))})
                if [row['k'] for row in domain if row['accepted_as_variant']] != list(range(1, 31)):
                    raise ValueError('Accepted domain differs from the approved plan')
            item['configs'].append({'path': path, 'version': version,
                'config_hash': fingerprint, 'file_sha256': sha((root / path).read_bytes()),
                'config_snapshot': config, 'config_validation': 'PASS',
                'domain_check_kind': 'EXISTING_FILTERS_ONLY_NOT_ACADEMIC_APPROVAL',
                'domain': domain})
        for stock in stocks.get(qid, []):
            item['stocks'].append({'variant_id': stock['variant_id'],
                                  'stock_version': stock['stock_version'],
                                  'content_sha256': sha(json_bytes(stock)), 'snapshot': stock})
        pins[qid] = item
    return pins


def build_inventory(root, data):
    source = read_docx(data)
    previous_bytes = (root / OLD / 'source.docx').read_bytes()
    previous = read_docx(previous_bytes)
    if sha(data) != SOURCE_SHA256 or source['text_sequence'] != previous['text_sequence']:
        raise ValueError('Source has changed; review text/OMML before reusing question positions')
    if len(source['paragraphs']) != len(previous['paragraphs']):
        raise ValueError('Source paragraph positions changed')
    old_placements = {(p['paragraph_index'], p['sha256']): p for p in previous['placements']}
    questions = json.loads((root / OLD / 'question-index.json').read_text(encoding='utf-8'))['questions']
    pins = current_pins(root, {item[0] for item in [*DIAGRAMS.values(), *FORMULAS.values()]})
    rows = []
    for placement in source['placements']:
        previous_placement = old_placements.get((placement['paragraph_index'], placement['sha256']))
        if previous_placement is None:
            raise ValueError('Image bytes/position differ from prior source')
        owner = question_owner(questions, placement['paragraph_index'])
        key = tuple(owner[name] for name in ('source_indicator', 'source_level', 'source_question_number'))
        if key not in DIAGRAMS and key not in FORMULAS:
            raise ValueError(f'Unexpected image owner: {key}')
        spec = DIAGRAMS.get(key) or FORMULAS[key]
        qid = spec[0]
        original = pins[qid]['original_snapshot']
        classification = original['classification']
        if (classification['indicator'], classification['source_level']) != key[:2]:
            raise ValueError('Runtime classification mismatch')
        occurrence = owner.get('source_occurrence', 1)
        next_start = min((q['paragraph_start_index'] for q in questions
                          if q['paragraph_start_index'] > owner['paragraph_start_index']),
                         default=len(source['paragraphs']))
        record = {**placement, 'kind': 'DIAGRAM' if key in DIAGRAMS else 'FORMULA_SYMBOL',
                  'source_audit_id': f'{SOURCE_SHA256}:I{key[0]}:L{key[1]}:Q{key[2]}:O{occurrence}',
                  'indicator': key[0], 'level': key[1], 'number': key[2], 'occurrence': occurrence,
                  'question_id': qid, 'source_heading': owner['source_heading'],
                  'source_question_paragraph_start': owner['paragraph_start_index'],
                  'source_question_paragraph_end_exclusive': next_start,
                  'body_block_start': owner['body_block_start_index'],
                  'body_block_end_exclusive': owner['body_block_end_exclusive'],
                  'paragraph_xml': source['paragraphs'][placement['paragraph_index']],
                  'old_source_file': previous_placement['file'],
                  'old_source_sha256': sha(previous_bytes),
                  'identity_evidence': 'EXACT_IMAGE_BYTES_AND_IDENTICAL_PARAGRAPH_POSITION',
                  'formula_text': spec[1] if key in FORMULAS else None,
                  'content_mode': spec[1] if key in DIAGRAMS else 'FORMULA_ONLY_NO_IMAGE_GENERATOR',
                  'planned_rendering': spec[2] if key in DIAGRAMS else None,
                  'planned_bindings': spec[3] if key in DIAGRAMS else {},
                  'renderer_status': 'NOT_IMPLEMENTED',
                  'mapping_status': 'VERIFIED_SOURCE_TO_ACTIVE_FAMILY_NOT_FULL_CONTENT_IDENTITY'}
        from PIL import Image
        with Image.open(io.BytesIO(source['media'][placement['file']])) as image:
            record['width'], record['height'] = image.size
        rows.append(record)
    if len(rows) != 14 or len(source['media']) != 14 or {r['file'] for r in rows} != set(source['media']):
        raise ValueError('Expected exactly 14 assets and placements with complete coverage')
    if len([r for r in rows if r['kind'] == 'DIAGRAM']) != 9:
        raise ValueError('Expected 9 diagrams')
    for key, spec in DIAGRAMS.items():
        pin = pins[spec[0]]
        if spec[1] == 'NUMERIC' and pin['config_versions'] != [1]:
            raise ValueError('Expected reviewed config v1')
        if spec[1] == 'CONCEPTUAL_STOCK' and (pin['configs'] or len(pin['stocks']) != 2):
            raise ValueError('Expected two conceptual stocks and no numeric config')
    return source, {'schema_version': 1, 'stage': 1, 'status': 'INVENTORY_ONLY',
        'source_sha256': SOURCE_SHA256, 'prior_source_sha256': sha(previous_bytes),
        'text_and_math_sequence_identical_to_prior': True,
        'paragraph_count': len(source['paragraphs']),
        'counts': {'media': 14, 'placements': 14, 'diagrams': 9, 'formula_symbols': 5,
                   'numeric_families': 5, 'conceptual_families': 4, 'conceptual_stocks': 8,
                   'planned_conceptual_scenarios': 12, 'accepted_numeric_combinations': 150},
        'assets': rows, 'family_pins': pins,
        'notes': ['Source positions are zero-based paragraph indices including table-cell paragraphs.',
                  'Runtime original_hash does not cover explanation; original_full_sha256 covers the snapshot.',
                  'Active originals include prior revisions. Source-to-family mapping is not full content identity.',
                  'No source instructions are executed; no original/config/stock/runtime changes are authorized.',
                  'Stages 2-5 require a later user instruction.']}


def write_new(directory, files):
    if directory.exists():
        raise ValueError(f'Refusing to overwrite existing evidence: {directory}; use --verify')
    directory.mkdir(parents=True)
    for relative, data in files.items():
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def verify(root, archive, audit):
    manifest = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
    expected = manifest['files_sha256']
    actual_files = {p.relative_to(archive).as_posix() for p in archive.rglob('*') if p.is_file()}
    if actual_files != set(expected) | {'manifest.json'}:
        raise ValueError('Archive file roster changed')
    for name, digest in expected.items():
        if sha((archive / name).read_bytes()) != digest:
            raise ValueError(f'Archive hash mismatch: {name}')
    ledger = json.loads((archive / 'image-inventory.json').read_text(encoding='utf-8'))
    _, reconstructed = build_inventory(root, (archive / 'source.docx').read_bytes())
    if json_bytes(ledger) != json_bytes(reconstructed):
        raise ValueError('Inventory differs from source/runtime reconstruction')
    baseline = json.loads((audit / 'protected-before.json').read_text(encoding='utf-8'))
    changed = compare_snapshot(root, baseline['files_sha256'])
    if changed:
        raise ValueError(f'Protected files changed: {changed}')
    csv_rows = list(csv.DictReader(io.StringIO((archive / 'image-map.csv').read_text(encoding='utf-8'))))
    if len(csv_rows) != 14 or any(row['sha256'] != asset['sha256'] or row['question_id'] != asset['question_id']
                                  or int(row['paragraph_index']) != asset['paragraph_index']
                                  for row, asset in zip(csv_rows, ledger['assets'])):
        raise ValueError('CSV/JSON disagreement')
    return {'status': 'PASS', 'stage': 1, 'archive_files_verified': len(expected),
            'source_sha256': ledger['source_sha256'], 'counts': ledger['counts'],
            'protected_files_verified': len(baseline['files_sha256']),
            'protected_changes': [], 'inventory_reconstructed': True, 'csv_json_consistent': True,
            'generator_rules_changed': False, 'renderer_implemented': False,
            'database_or_r2_accessed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--audit', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    archive = args.archive or root / ARCHIVE
    audit = args.audit or root / AUDIT
    if args.verify:
        print(json_bytes(verify(root, archive, audit)).decode('utf-8'))
        return
    if args.source is None:
        parser.error('--source is required to create evidence')
    if archive.exists() or audit.exists():
        raise ValueError('Evidence directories already exist; use --verify')
    before = protected_snapshot(root)
    data = args.source.read_bytes()
    source, ledger = build_inventory(root, data)
    output = io.StringIO(newline='')
    fields = ['question_id', 'indicator', 'level', 'number', 'occurrence', 'kind', 'file',
              'old_source_file', 'sha256', 'paragraph_index', 'relationship_id',
              'width', 'height', 'content_mode', 'renderer_status']
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(ledger['assets'])
    files = {'source.docx': data, 'image-inventory.json': json_bytes(ledger),
             'image-map.csv': output.getvalue().encode('utf-8'),
             **source['media'],
             **{'source-parts/' + key: value for key, value in source['parts'].items()}}
    manifest = {'schema_version': 1, 'source_filename': args.source.name,
                'source_sha256': sha(data), 'source_byte_length': len(data),
                'status': 'STAGED_ONLY', 'counts': ledger['counts'],
                'files_sha256': {key: sha(value) for key, value in sorted(files.items())}}
    files['manifest.json'] = json_bytes(manifest)
    write_new(archive, files)
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    write_new(audit, {'protected-before.json': json_bytes({'schema_version': 1,
        'git_commit': commit, 'files_sha256': before}),
        'progress.md': b'# Drill image variants\n\nStage 1: evidence being verified.\nStages 2-5: NOT STARTED; await user instruction.\n'})
    result = verify(root, archive, audit)
    (audit / 'verification-stage1.json').write_bytes(json_bytes(result))
    (audit / 'protected-after.json').write_bytes(json_bytes({'schema_version': 1,
                                                           'files_sha256': protected_snapshot(root)}))
    print(json_bytes(result).decode('utf-8'))


if __name__ == '__main__':
    main()
