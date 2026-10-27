"""Read-only audit of local Tryout generators against the five extracted images.

Run from the AI repository root. Writes audit artifacts only, without DB/R2 access.
Visual bindings are manually transcribed from the original PNGs, not inferred by OCR.
"""
import csv
import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'variant_gen'))
sys.path.insert(0, str(ROOT / 'variant_gen/tests'))
from bank import OriginalBank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from expr import RejectDraw, to_num
from filters import validate_candidate
from lint import reproduce_original
from test_tryout import check_math

OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'docs/sources/incoming/2026-10-26-tryout-images'
BINDINGS = {
    'tryout-1-b3-q02': {
        'labels': {'p': 20, 'width': 14},
        'affected': ['p', 'r', 'width'],
        'freeze': {'p': 20, 'r': 7},
        'assessment': 'Numeric labels conflict when dimensions vary. Non-scale note does not resolve printed numbers.',
    },
    'tryout-1-b3-q03': {
        'labels': {'a': 3, 'b': 15, 'c': 5, 'offset': 25, 'other': 50},
        'affected': ['x', 'a', 'b', 'c', 'offset', 'angle', 'other', 'ans'],
        'freeze': {'x': 20, 'a': 3, 'b': 15, 'c': 5, 'other': 50},
        'assessment': 'Image repeats (3x+15), (5x-25), and 50 degrees. Active generation c=6..9 cannot match image c=5. Fixed labels determine x=20 and answer=55.',
    },
    'tryout-1-b3-q04': {
        'labels': {'s': 12, 'h': 18, 'p': 2, 'q': 3},
        'affected': ['s', 'h', 'p', 'q', 'ratio', 'sw', 'hw'],
        'freeze': {'s': 12, 'h': 18, 'p': 2, 'q': 3},
        'assessment': 'Two edge labels 12 cm, total height 18 cm, and water ratio 2/3. Ratio also controls visible fill position. Keeping ratio alone does not fix dimension labels.',
    },
    'tryout-1-b3-q06': {
        'labels': {'r': 7, 'h': 10, 'p': 15, 'l': 12, 't': 12},
        'affected': ['r', 'h', 'p', 'l', 't'],
        'freeze': {'r': 7, 'h': 10, 'p': 15, 'l': 12, 't': 12},
        'assessment': 'Radius 7 appears twice; diameter 14, cylinder height 10 and box 15x12x12 are fixed. Threshold is not printed, but changing only this false option fails current same-answer validator.',
    },
    'tryout-1-b4-q05': {
        'labels': {'times': 180},
        'affected': ['times'],
        'freeze': {'times': 180},
        'assessment': '180 appears twice. Dice faces are an illustration, not observed outcomes; threshold is absent from image. Four threshold variants survive current validation.',
    },
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = sorted((ROOT / 'variant_gen/data/tryout-1').rglob('*'))
    files += sorted((ROOT / 'variant_gen/configs').glob('tryout*/v*.json'))
    files += sorted(SOURCE.rglob('*'))
    before = {str(p.relative_to(ROOT)): digest(p) for p in files if p.is_file()}
    bank = OriginalBank(ROOT / 'variant_gen/data/tryout-1/q0_bank.csv')
    configs = ConfigStore(ROOT / 'variant_gen/configs')
    manifest = json.loads((SOURCE / 'image-manifest.json').read_text(encoding='utf-8'))
    images = {x['candidate_local_question_id']: x for x in manifest['images']}
    assert set(images) == set(BINDINGS)
    for entry in images.values():
        assert digest(SOURCE / entry['local_path']) == entry['image_sha256']
    rows = []
    oracle = unittest.TestCase()
    for qid in bank.ids():
        original = bank.get(qid)
        row = {'question_id': qid, 'original_version': original['version'],
               'original_hash': original['hash'], 'has_image': qid in images,
               'generator_available': bool(configs.versions(qid))}
        if not row['generator_available']:
            row['status'] = 'NO_GENERATOR_NO_IMAGE'
            row['reason'] = original['metadata']['reason']
            rows.append(row)
            continue
        cfg, cfg_hash = configs.load(qid)
        assert not validate_config(cfg, original), qid
        problems, warnings = reproduce_original(original, cfg)
        assert not problems, (qid, problems)
        row.update(config_version=cfg['config_version'], config_hash=cfg_hash,
                   config_file_sha256=digest(ROOT / 'variant_gen/configs' / qid / f"v{cfg['config_version']}.json"),
                   base_variables={k: v for k, v in cfg['variables'].items() if v['gen'] != 'derived'},
                   reproduction_warnings=warnings)
        if qid in BINDINGS:
            row.update(BINDINGS[qid])
            row['image_path'] = str((SOURCE / images[qid]['local_path']).relative_to(ROOT))
            row['image_sha256'] = images[qid]['image_sha256']
        mismatches = 0
        samples = []
        for seed in range(1, 21):
            result = generate(original, cfg, seed, [])
            check_math(oracle, qid, result.values, result.cand)
            mismatch = {k: {'image': target, 'generated': str(result.values[k])}
                        for k, target in BINDINGS.get(qid, {}).get('labels', {}).items()
                        if result.values[k] != to_num(target)}
            mismatches += bool(mismatch)
            if seed == 1:
                samples.append({'seed': seed, 'values': {k: str(v) for k, v in result.values.items()},
                                'mismatched_labels': mismatch, 'stem': result.cand['stem']})
        row.update(sample_seeds=[1, 20], generated_and_math_checked=20,
                   sample_image_mismatch_count=mismatches, sample_examples=samples)
        row['status'] = 'NO_EMBEDDED_IMAGE' if qid not in images else 'IMAGE_CONFLICT_WITH_CURRENT_CONFIG'
        if qid in BINDINGS:
            domain = range(8, 13) if qid.endswith('b4-q05') else range(500, 12001, 50) if qid.endswith('b3-q06') else [None]
            accepted, rejected, bad_constraints = [], Counter(), 0
            for value in domain:
                source_values = {**cfg['original_values'], **row['freeze']}
                if value is not None:
                    source_values['threshold'] = value
                try:
                    vals = build_values(cfg, lambda name, spec: to_num(source_values[name]))
                except RejectDraw:
                    bad_constraints += 1
                    continue
                candidate = assemble(cfg, vals)
                errors = validate_candidate(candidate, original, [])
                rejected.update(errors)
                if not errors:
                    accepted.append(value)
            row['frozen_image_probe'] = {'method': 'Inject fixed image-compatible inputs and enumerate the entire remaining threshold domain; no config edits. Injection checks constraints, not random-range membership.',
                'accepted_thresholds': accepted, 'constraint_rejections': bad_constraints,
                'validator_rejection_counts': dict(rejected)}
            if qid.endswith('b3-q03'):
                row['frozen_image_probe']['generation_domain_conflict'] = 'c=5 is outside current generation range [6,9]; fixed original is only a reproduction probe, not a drawable variant.'
        rows.append(row)
    after = {name: digest(ROOT / name) for name in before}
    assert before == after, 'Audited input files changed during audit'
    report = {'date': '2026-10-27', 'scope': 'Local Tryout package tryout-1 only; compatibility if its original images are reused for generated variants. Not a claim that runtime already attaches these images to variants.',
              'method': 'All 30 entries and 27 latest configs inspected; five PNGs visually inspected. Config validation and original reproduction, 20 seeds per generator with existing independent arithmetic oracle. Samples corroborate dependency analysis; sample counts are not exhaustive capacities.',
              'summary': {'originals': len(rows), 'generators': sum(r['generator_available'] for r in rows),
                          'generators_without_image': sum(r['status'] == 'NO_EMBEDDED_IMAGE' for r in rows),
                          'image_linked_generators': len(images), 'sampled_variants': 540,
                          'status_counts': dict(Counter(r['status'] for r in rows))},
              'approval': 'Analysis only. Proposed restrictions and wording changes are not applied or academically approved.',
              'input_hashes_before': before, 'input_hashes_after': after, 'inputs_unchanged': before == after,
              'entries': rows}
    (OUT / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    fields = ['question_id', 'original_version', 'config_version', 'config_hash', 'has_image', 'status', 'base_variables', 'affected', 'assessment', 'sample_image_mismatch_count', 'frozen_image_probe']
    with (OUT / 'entries.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})
    print(json.dumps(report['summary']))
    print('Source/config/image hashes unchanged:', report['inputs_unchanged'])
    for r in rows:
        if r['has_image']:
            print(r['question_id'], 'mismatches', r['sample_image_mismatch_count'], '/20;', r['frozen_image_probe'])


if __name__ == '__main__':
    main()
