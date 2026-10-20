"""Exhaustive finite-domain evidence, seed replays and immutable-input checks."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import load_workspace_bank, OriginalBank
from config_store import ConfigStore, validate_config
from engine import build_values, assemble, generate
from expr import RejectDraw
from filters import signature, validate_candidate
from lint import reproduce_original
from drill_1_5_level45_math import check_math
from test_drill_1_5_level45_batch1 import IDS, DATA

OUTPUT = REPO / 'docs/audits/2026-10-20-drill-1-5-level45-batch1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    bank = load_workspace_bank(ROOT / 'data/q0_bank.csv')
    configs = ConfigStore(ROOT / 'configs')
    results = []
    for qid in IDS:
        o = bank.get(qid)
        cfg, cfg_hash = configs.load(qid)
        assert not validate_config(cfg, o), qid
        assert reproduce_original(o, cfg) == ([], []), qid
        spec = cfg['variables']['k']
        declared = (list(range(spec['range'][0], spec['range'][1]+1, spec.get('step', 1)))
                    if spec['gen'] == 'range' else spec['values'])
        accepted, rejected, signatures = [], Counter(), set()
        for k in declared:
            try:
                values = build_values(cfg, lambda n, s: k)
            except RejectDraw as exc:
                rejected[str(exc)] += 1
                continue
            candidate = assemble(cfg, values)
            check_math(qid, candidate)  # Includes original values, before variant rejection.
            failures = validate_candidate(candidate, o, [])
            if failures:
                rejected.update(failures)
                continue
            sig = signature(candidate['stem'], candidate['options'])
            signatures.add(sig)
            accepted.append(k)
        assert len(signatures) >= 20, (qid, len(signatures))
        samples, made = [], []
        for seed in range(1, 21):
            r = generate(o, cfg, seed, made)
            check_math(qid, r.cand)
            made.append(r.cand)
            samples.append(dict(seed=seed, k=r.values['k'], candidate=r.cand))
        for seed in range(201, 251):
            a, b = generate(o, cfg, seed, []), generate(o, cfg, seed, [])
            assert a.cand == b.cand and a.values == b.values
            check_math(qid, a.cand)
        results.append(dict(question_id=qid, classification=o['classification'],
            source_number=o['metadata']['source_number'], source_audit_id=o['metadata']['audit_id'],
            source_sha256=o['metadata']['source_document_sha256'], source_location=o['metadata']['source_location'],
            original_version=o['version'], original_hash=o['hash'], config_version=1, config_hash=cfg_hash,
            config_sha256=digest(ROOT / 'configs' / qid / 'v1.json'),
            academic_approval='NOT_CURRICULUM_APPROVED', self_adjustment_enabled=False,
            declared_k=declared, effective_k=accepted, rejection_counts=dict(rejected),
            exact_distinct_variant_capacity=len(signatures), unique_seed_samples=len(made),
            additional_deterministic_seeds=[201,250], samples=samples))
    baseline_path = REPO / '.scratch/level45-before.json'
    old_files = (json.loads(baseline_path.read_text()) if baseline_path.exists() else
                 json.loads((OUTPUT/'audit.json').read_text(encoding='utf-8'))['prior_workspace_baseline'])
    changed = [p for p, h in old_files.items() if not (REPO/p).exists() or digest(REPO/p) != h]
    allowed = {'variant_gen/bank.py', 'readme.md', 'docs/GENERATOR.md',
        'variant_gen/tests/test_drill_1_2.py', 'variant_gen/tests/test_drill_3_5.py',
        'variant_gen/tests/test_drill_6_10.py', 'variant_gen/tests/test_drill_11_15.py',
        'variant_gen/tests/test_drill_20_23.py', 'tests/service/test_api.py'}
    assert not set(changed)-allowed, ('Unexpected modification to prior files', set(changed)-allowed)
    protected = {p: h for p, h in old_files.items() if p.startswith(('variant_gen/data/', 'variant_gen/configs/',
                  'docs/sources/', 'docs/audits/2026-10-19-original-question-audit/', 'numora_service/', 'contracts/'))}
    assert all(digest(REPO/p) == h for p,h in protected.items())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    all_level45 = json.loads((REPO/'docs/audits/2026-10-19-original-question-audit/stage-06-matching-indicators-01-05/matching.json').read_text(encoding='utf-8'))['entries']
    chosen = {r['source_audit_id'] for r in results}
    pending = []
    for e in all_level45:
        if e['level'] not in (4,5) or e['audit_id'] in chosen: continue
        pending.append(dict(audit_id=e['audit_id'], indicator=e['indicator'], level=e['level'],
            source_number=e['source_number'], format=e['source_projection']['format'],
            status='ACADEMIC_FOLLOW_UP' if e['recommendation']=='TERTAHAN_AKADEMIK' else 'NEXT_GENERATOR_BATCH'))
    report = dict(summary=dict(date='2026-10-20', target_originals=100, implemented=33, pending=67,
        pending_status=dict(Counter(p['status'] for p in pending)),
        by_indicator=dict(Counter(r['classification']['indicator'] for r in results)),
        by_level=dict(Counter(r['classification']['source_level'] for r in results)),
        formats=dict(Counter(bank.get(r['question_id'])['format'] for r in results)),
        exhaustive_parameter_tuples=sum(len(r['declared_k']) for r in results),
        exact_variant_capacity=sum(r['exact_distinct_variant_capacity'] for r in results),
        min_family_capacity=min(r['exact_distinct_variant_capacity'] for r in results),
        unique_seed_samples=660, additional_deterministic_samples=1650,
        workspace_originals=len(bank.ids()), drill_originals=sum(bank.get(q)['classification']['activity']=='DRILL' for q in bank.ids()),
        configs=len(list((ROOT/'configs').glob('*/v1.json'))),
        protected_before_after_files=len(protected), protected_files_unchanged=True),
        source_and_bank_hashes={str(p.relative_to(REPO)):digest(p) for p in [
            REPO/'docs/sources/incoming/2026-10-19-indikator-1-5/source.docx',
            DATA/'q0_bank.csv', DATA/'question_catalog.json', DATA/'question_metadata.json']},
        protected_baseline_sha256=hashlib.sha256(json.dumps(protected,sort_keys=True).encode()).hexdigest(),
        protected_baseline=protected, prior_workspace_baseline=old_files,
        changed_prior_files=changed, entries=results, pending=pending)
    (OUTPUT/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (OUTPUT/'entries.csv').open('w',encoding='utf-8',newline='') as f:
        keys=['question_id','source_number','original_version','original_hash','config_version','config_sha256',
              'exact_distinct_variant_capacity','unique_seed_samples','academic_approval','self_adjustment_enabled']
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        writer.writerows({key:r[key] for key in keys} for r in results)
    with (OUTPUT/'pending.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(pending[0]));writer.writeheader();writer.writerows(pending)
    print(json.dumps(report['summary'],indent=2))
    return report


if __name__ == '__main__':
    audit()
