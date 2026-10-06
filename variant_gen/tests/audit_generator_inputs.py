"""Offline Drill input audit. Only --output artifacts are written; runtime is unchanged.

Capacity uses the runtime's order-independent stem/options/key identity, not draw count.
Large domains expose witnessed lower bounds and conservative upper bounds explicitly.
Neither feasibility nor a numerical workload proxy authorizes automatic adjustment.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
import random
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values
from expr import RejectDraw, expr_names, json_number, placeholders, to_num
from filters import check_variable, correct_set, signature, validate_candidate
from lint import reproduce_original

HOLD_IDS = {'pg-1-2-1', 'pg-5-3-3', 'mcma-6-3-7', 'mcma-15-2-8'}
REVISED_6_10 = {'pg-6-1-5', 'pg-7-1-2', 'pg-7-1-3', 'pg-7-2-4',
                'pg-7-3-5', 'mcma-8-2-8', 'pg-9-1-3', 'pg-9-1-5',
                'pg-9-2-5', 'pg-9-3-2', 'pg-9-3-4'}
REVISED_11_15 = {'mcma-11-1-7', 'pg-11-2-4', 'kategori-11-3-9', 'pg-15-4-2'}
REVISED_16_19 = {'mcma-17-1-8', 'kategori-17-2-10'}
REVISED_20_23 = {'pg-20-3-3', 'pg-21-2-2', 'pg-21-3-1', 'pg-21-3-4',
                 'pg-21-3-5', 'mcma-21-3-8', 'kategori-21-3-9', 'pg-22-1-1',
                 'mcma-22-1-6', 'mcma-22-1-7', 'mcma-22-3-8', 'pg-23-3-2',
                 'pg-23-3-5', 'mcma-23-3-7', 'mcma-23-3-8', 'kategori-23-3-9'}
SHIFT_REVISIONS = {'pg-20-3-3', 'pg-21-2-2', 'pg-21-3-4', 'mcma-21-3-8',
                   'kategori-21-3-9', 'pg-21-3-5', 'pg-22-1-1',
                   'mcma-22-1-6', 'mcma-22-1-7', 'mcma-22-3-8'}
PROFILE_NAMES = {'case', 'false_slot', 'rotation', 'flip', 'winner', 'role', 'mode'}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def encode(value):
    return json_number(value) if isinstance(value, (int, Fraction)) and not isinstance(value, bool) else value


def input_domain(spec):
    """Exact selectable domain after local filters; range values are multiples of step."""
    if spec['gen'] == 'choice':
        values = [to_num(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v for v in spec['values']]
    elif spec['gen'] == 'range':
        low, high = map(to_num, spec['range'])
        step = to_num(spec.get('step', 1))
        values = [i * step for i in range(math.ceil(Fraction(low) / step), math.floor(Fraction(high) / step) + 1)]
    else:
        raise ValueError('Audit requires an explicit finite domain; unsupported input type: ' + spec['gen'])
    return list(dict.fromkeys(v for v in values if not check_variable('input', spec, v)))


def dependency_map(cfg):
    dependencies = {}
    for name, spec in cfg['variables'].items():
        dependencies[name] = ({name} if spec['gen'] != 'derived' else
                              set().union(*(dependencies[n] for n in expr_names(spec['expr']))))
    outputs = dict(stem=placeholders(cfg['stem']),
                   option_text=set().union(*(placeholders(o['text']) for o in cfg['options'])),
                   correctness=set().union(*(expr_names(o['correct']) for o in cfg['options'] if isinstance(o['correct'], str))),
                   explanation=placeholders(cfg['explanation']),
                   constraints=set().union(*(expr_names(c) for c in cfg.get('constraints', []))))
    return dependencies, {target: set().union(*(dependencies[n] for n in names)) for target, names in outputs.items()}


def workload_proxy(candidate):
    """Reading/arithmetic representation signals, not a difficulty score or direction."""
    text = candidate['stem'] + ' ' + ' '.join(o['text'] for o in candidate['options'])
    tokens = re.findall(r'(?<![\w])-?\d+(?:[.,]\d+)*', text)
    return (sum(len(re.sub(r'\D', '', x)) for x in tokens),
            max((len(re.sub(r'\D', '', x)) for x in tokens), default=0),
            sum(x.startswith('-') for x in tokens),
            sum(',' in x for x in tokens), text.count('/'), text.count('√'))


def classify(qid, name, effective, deps, contrast):
    if len(effective) < 2 or not any(name in deps[x] for x in ('stem', 'option_text', 'correctness')):
        return 'NO_EFFECT', 'Only one effective value, or no dependency on rendered question/answer.'
    if name == 'labels' and qid in REVISED_11_15:
        return 'DISPLAY_CONTEXT', 'Reviewed set/point renaming; mathematical task remains identical with other inputs fixed.'
    if qid == 'pg-18-3-1' and name == 'r1':
        return 'NUMERIC_CONTEXT', 'Area ratio is k squared; radius cancels. Radius changes stimulus, not the area-ratio answer.'
    if qid in REVISED_16_19 and name == 'k':
        return 'NUMERIC_CONTEXT', 'Property judgement only; selected factors obey abs(k)!=1. No coordinate or scaling calculation is requested.'
    if not any(name in deps[target] for target in ('option_text', 'correctness')):
        return 'NUMERIC_CONTEXT', 'Only stimulus/explanation depend on this input, not answer text or correctness; representation signals are separate from a change in the mathematical task.'
    if name == 't' and qid in SHIFT_REVISIONS:
        return 'NUMERIC_CONTEXT', 'Common data translation preserves ordering, gaps and comparison relations; displayed digit changes are recorded separately.'
    if name in PROFILE_NAMES:
        return 'CONTENT_PROFILE', 'Selects a statement/data/role profile. Review the changed claims and reasoning; it is not a proven numeric difficulty control.'
    if contrast['output_changes'] == 0 and contrast['pairs']:
        return 'NO_EFFECT', 'Controlled contrasts with every other input fixed produced identical rendered content.'
    return 'POTENTIAL_WORKLOAD', 'Numeric stimulus/answer input with explicit dependencies; possible arithmetic/reading burden, without student evidence or an assumed direction.'


def domain_record(values, exact, unresolved):
    numeric = bool(values) and all(isinstance(v, (int, Fraction)) and not isinstance(v, bool) for v in values)
    ordered = sorted(values) if numeric else sorted(values, key=str)
    return dict(exact=exact, values=[encode(v) for v in ordered],
                minimum=encode(min(ordered)) if numeric else None,
                maximum=encode(max(ordered)) if numeric else None,
                unresolved_values=[encode(v) for v in unresolved])


def audit_one(orig, cfg, cfg_hash, exhaustive_limit=100000, probes=1000, checker=None):
    problems = validate_config(cfg, orig)
    if problems:
        raise ValueError((orig['id'], problems))
    reproduction, warnings = reproduce_original(orig, cfg)
    if reproduction:
        raise ValueError((orig['id'], reproduction))
    specs = {n: s for n, s in cfg['variables'].items() if s['gen'] != 'derived'}
    names = list(specs)
    domains = [input_domain(s) for s in specs.values()]
    space = math.prod(map(len, domains))
    exhaustive = space <= exhaustive_limit
    dependencies, outputs = dependency_map(cfg)
    accepted = 0
    checked = 0
    signatures = set()
    seen_tuples = set() if not exhaustive else None
    effective = {n: set() for n in names}
    anchors = []
    rejections = Counter()
    contrasts = {n: dict(pairs=0, output_changes=0, answer_changes=0,
                         key_changes=0, proxy_changes=0, witnesses=[]) for n in names}
    contexts = {n: {} for n in names}
    oracle_checks = 0

    def inspect(inputs):
        nonlocal checked, accepted, oracle_checks
        inputs = tuple(inputs)
        if seen_tuples is not None:
            if inputs in seen_tuples:
                return
            seen_tuples.add(inputs)
        checked += 1
        source = dict(zip(names, inputs))
        try:
            values = build_values(cfg, lambda name, spec: source[name])
            cand = assemble(cfg, values)
        except RejectDraw as error:
            rejections[str(error)] += 1
            return
        errors = validate_candidate(cand, orig, [])
        if errors:
            rejections.update(errors)
            return
        if checker:
            checker(orig, cand, values)
            oracle_checks += 1
        accepted += 1
        content = digest(signature(cand['stem'], cand['options']))
        signatures.add(content)
        answer = digest(sorted(correct_set(cand['options'])))
        key = tuple(o['id'] for o in cand['options'] if o['correct'])
        proxy = workload_proxy(cand)
        if len(anchors) < 12:
            anchors.append(inputs)
        for i, name in enumerate(names):
            effective[name].add(inputs[i])
            context = inputs[:i] + inputs[i+1:]
            before = contexts[name].get(context)
            if before is None:
                contexts[name][context] = (inputs[i], content, answer, key, proxy)
            elif inputs[i] != before[0]:
                stats = contrasts[name]
                stats['pairs'] += 1
                changes = (content != before[1], answer != before[2], key != before[3], proxy != before[4])
                for field, changed in zip(('output_changes', 'answer_changes', 'key_changes', 'proxy_changes'), changes):
                    stats[field] += int(changed)
                if len(stats['witnesses']) < 2 and any(changes):
                    stats['witnesses'].append(dict(fixed_other_inputs={n: encode(v) for n, v in source.items() if n != name},
                                                  before=encode(before[0]), after=encode(inputs[i]),
                                                  content_changed=changes[0], answer_changed=changes[1],
                                                  key_changed=changes[2], numeric_proxy_before=list(before[4]),
                                                  numeric_proxy_after=list(proxy)))

    if exhaustive:
        for inputs in itertools.product(*domains):
            inspect(inputs)
    elif space:
        rng = random.Random(int(hashlib.sha256(orig['id'].encode()).hexdigest()[:16], 16))
        for _ in range(probes):
            inspect([rng.choice(d) for d in domains])
        # Sweep every value with valid contexts. This can prove an input projection
        # complete even when the full Cartesian product was not enumerated.
        bases = list(anchors)
        for base in bases:
            for i, domain in enumerate(domains):
                for value in domain:
                    inputs = list(base)
                    inputs[i] = value
                    inspect(inputs)
        exhaustive = checked == space
    if not signatures:
        raise ValueError((orig['id'], 'No feasible candidate', dict(rejections)))
    input_rows = {}
    for name, spec, domain in zip(names, specs.values(), domains):
        vals = effective[name]
        unresolved = [] if exhaustive else [v for v in domain if v not in vals]
        projection_exact = exhaustive or len(vals) == len(domain)
        group, reason = classify(orig['id'], name, vals, outputs, contrasts[name])
        # One witnessed value in a non-exhaustive domain is not proof of no effect.
        if group == 'NO_EFFECT' and not projection_exact:
            group, reason = 'NEEDS_REVIEW', 'Incomplete effective projection; no-effect cannot be concluded from a bounded probe.'
        input_rows[name] = dict(declared_spec=spec,
                                locally_filtered_domain=domain_record(domain, True, []),
                                effective_domain=domain_record(vals, projection_exact, unresolved),
                                feasible=bool(vals), effect_group=group, rationale=reason,
                                depends_on={target: name in deps for target, deps in outputs.items()},
                                derived_dependents=[n for n, deps in dependencies.items() if n != name and name in deps],
                                controlled_contrasts=contrasts[name],
                                approval_status='NO_APPROVED_CONTROL', adjustment_enabled=False,
                                difficulty_direction=None, student_evidence=False)
    row = dict(question_id=orig['id'], classification=orig.get('classification', {}),
                original_version=orig['version'], original_hash=orig['hash'],
                config_version=cfg['config_version'], config_hash=cfg_hash,
                method='EXHAUSTIVE' if exhaustive else 'BOUNDED_PROBE',
                reproduction_warnings=warnings, constraints=cfg.get('constraints', []),
                locally_filtered_tuple_count=space, checked_input_tuples=checked,
                accepted_input_tuples=accepted, rejection_reasons=dict(rejections),
                observed_distinct_count=len(signatures),
                capacity=dict(exact=len(signatures) if exhaustive else None,
                              lower_bound=len(signatures), upper_bound=len(signatures) if exhaustive else space,
                              identity='normalized stem + unordered (option text, correctness); explanation/option order excluded'),
                independent_math_checks=oracle_checks, inputs=input_rows,
                approval_status='NO_APPROVED_CONTROL', adjustment_enabled=False)
    apply_analytic_proof(orig, cfg, row)
    return row


def apply_analytic_proof(original, cfg, row):
    """Two injective integer-stimulus families have exact closed-form capacities.

    Guard every formula/constraint/template needed by the proof. Reduced-domain
    exhaustive tests check these counts against the actual rendering/validators.
    These proofs count feasible content, not mathematical/difficulty approval.
    """
    qid = original['id']
    if qid not in ('pg-17-2-5', 'pg-20-1-3'):
        return
    domains = {n: input_domain(s) for n, s in cfg['variables'].items() if s['gen'] != 'derived'}
    assert all(all(isinstance(v, int) and not isinstance(v, bool) and abs(v) < 1000 for v in d) for d in domains.values())
    assert placeholders(cfg['stem']) == set(domains), (qid, 'Stimulus must expose each independent integer input')
    assert all(cfg['variables'][n].get('fmt', 'id') in ('id', 'raw') for n in domains)
    if qid == 'pg-17-2-5':
        assert cfg['stem'] == 'Titik E({x}, {y}) ditranslasikan berturut-turut oleh T₁({c1}, {d1}) dan T₂({c2}, {d2}). Koordinat bayangan akhir titik E adalah...'
        formulas = dict(o1x='x + c1 + c2', o1y='y + d2', o2x='x + c1 + c2', o2y='y + d1 + d2',
                        o3x='x + c1 - c2', o3y='y + d1 + d2', o4x='x + c1 - c2', o4y='y + d2')
        assert {n: s['expr'] for n, s in cfg['variables'].items() if s['gen'] == 'derived'} == formulas
        assert not cfg.get('constraints') and 0 not in domains['c2'] and 0 not in domains['d1']
        assert cfg['options'] == [dict(id=chr(65+i), text='({o'+str(i+1)+'x}, {o'+str(i+1)+'y})', correct=i == 1) for i in range(4)]
        correct = next(o['text'] for o in original['options'] if o['correct'])
        match = re.fullmatch(r'\((-?\d+),\s*(-?\d+)\)', correct)
        assert match, correct
        target_x, target_y = map(int, match.groups())
        xs = Counter(sum(v) for v in itertools.product(domains['x'], domains['c1'], domains['c2']))
        ys = Counter(sum(v) for v in itertools.product(domains['y'], domains['d1'], domains['d2']))
        assert len(xs) > 1 and len(ys) > 1
        total = sum(xs.values()) * sum(ys.values())
        count = total - xs[target_x] * ys[target_y]
        proof = dict(name='TWO_TRANSLATIONS_INTEGER_INJECTION', total_tuples=total,
                     forbidden_x_count=xs[target_x], forbidden_y_count=ys[target_y],
                     formula='total - forbidden_x_count * forbidden_y_count',
                     reasoning='c2 and d1 are nonzero, so four coordinate options are pairwise distinct. Only original-correct coordinate is rejected. Six displayed integer inputs identify a unique stimulus.')
        effective_domains = domains
    else:
        assert cfg['stem'] == 'Perhatikan data jumlah pengunjung perpustakaan berikut.\nHari | Jumlah Pengunjung\nSenin | {mon}\nSelasa | {tue}\nRabu | {wed}\nKamis | {thu}\nJumat | {fri}\nBerdasarkan data tersebut, hari dengan jumlah pengunjung terbanyak adalah ....'
        assert set(cfg['variables']) == {'mon', 'tue', 'wed', 'thu', 'fri', 'maximum'}
        assert cfg['variables']['maximum']['expr'] == 'max(mon,tue,wed,thu,fri)'
        assert cfg.get('constraints') == ['maximum > thu', 'mon != tue', 'mon != wed', 'mon != fri', 'tue != wed', 'tue != fri', 'wed != fri']
        targets = ['mon', 'tue', 'wed', 'fri']
        labels = ['Senin', 'Selasa', 'Rabu', 'Jumat']
        assert cfg['options'] == [dict(id=chr(65+i), text=label, correct=name+' == maximum') for i, (name, label) in enumerate(zip(targets, labels))]
        values = domains['mon']
        assert all(d == values for d in domains.values()) and len(values) >= 4 and values == sorted(set(values))
        original_label = next(o['text'] for o in original['options'] if o['correct'])
        original_day = targets[labels.index(original_label)]
        count = 3 * sum((m-1) * (m-1) * (m-2) * (m-3) for m in range(4, len(values)+1))
        proof = dict(name='WEEKDAY_MAXIMUM_COMBINATORICS', domain_size=len(values),
                     formula='3 * sum((m-1)^2 * (m-2) * (m-3), m=4..domain_size)',
                     reasoning='Three allowed winning weekdays exclude the original correct day. For maximum rank m, choose three distinct lower values in order and any of m-1 lower Thursday values. Five labelled integer counts identify the stimulus.')
        effective_domains = {n: values[:-1] if n in ('thu', original_day) else values for n in domains}
    if row['method'] == 'EXHAUSTIVE':
        assert count == row['capacity']['exact'], (qid, count, row['capacity'])
    assert count >= row['capacity']['lower_bound']
    proof['config_hash'] = row['config_hash']
    row['capacity'].update(exact=count, lower_bound=count, upper_bound=count)
    row['analytic_proof'] = proof
    if row['method'] != 'EXHAUSTIVE':
        row['method'] = 'ANALYTIC_WITH_PROBE'
    for name, values in effective_domains.items():
        observed = row['inputs'][name]['effective_domain']['values']
        assert set(observed) <= set(values)
        row['inputs'][name]['effective_domain'] = domain_record(values, True, [])


def checker_for(qid):
    """Reuse the reviewed text-based oracles; they do not authorize adjustment."""
    import unittest
    test = unittest.TestCase()
    if qid in REVISED_6_10:
        from collections import Counter
        from engine import Result
        from drill_6_10_math import check_math
        return lambda original, candidate, values: check_math(test, original, Result(values, candidate, 0, Counter()))
    if qid in REVISED_11_15:
        from drill_11_15_math import check_math
        return lambda original, candidate, values: check_math(qid, candidate)
    if qid in REVISED_16_19:
        from test_transform_property_generators import TransformPropertyGenerators
        probe = TransformPropertyGenerators()
        return lambda original, candidate, values: probe.check_rendered(original, candidate)
    if qid in REVISED_20_23:
        from test_drill_20_23_revisions import check_revised_math
        return lambda original, candidate, values: check_revised_math(test, original, candidate)
    return None


def source_manifest():
    paths = list((ROOT / 'data').rglob('*')) + list((ROOT / 'configs').rglob('*.json'))
    paths += [ROOT / name for name in ('bank.py', 'config_store.py', 'engine.py', 'expr.py', 'filters.py', 'randomizer.py', 'lint.py')]
    return {str(p.relative_to(ROOT.parent)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def run(output, exhaustive_limit=100000, probes=1000):
    manifest = source_manifest()
    bank = load_workspace_bank(ROOT / 'data/q0_bank.csv')
    configs = ConfigStore(ROOT / 'configs')
    rows, excluded, queue = [], [], []
    for qid in sorted(bank.ids()):
        original = bank.get(qid)
        if original.get('classification', {}).get('activity') != 'DRILL':
            continue
        metadata = original.get('metadata', {})
        if metadata.get('generation_status', 'ACTIVE') == 'HOLD_SOURCE':
            excluded.append(dict(question_id=qid, reason=metadata.get('reason'), original_version=original['version'], original_hash=original['hash']))
            continue
        if not configs.versions(qid):
            if original['version'] >= 2 and metadata.get('source_review_status') == 'REVISED_CURRICULUM':
                queue.append(dict(question_id=qid, original_version=original['version'], original_hash=original['hash'],
                                  status='WAITING_FOR_GENERATOR', approval_status='NO_APPROVED_CONTROL',
                                  adjustment_enabled=False, reason=metadata.get('reason')))
            continue
        cfg, cfg_hash = configs.load(qid)
        row = audit_one(original, cfg, cfg_hash, exhaustive_limit, probes, checker_for(qid))
        row['evidence'] = evidence_paths(qid)
        rows.append(row)
        print(f"{len(rows)} {qid} {row['method']} capacity={row['capacity']['exact'] or str(row['capacity']['lower_bound'])+'..'+str(row['capacity']['upper_bound'])}", flush=True)
    if manifest != source_manifest():
        raise ValueError('Bank/config/runtime files changed during audit; rerun against a stable snapshot.')
    assert len(rows) == 679, len(rows)
    assert {r['question_id'] for r in excluded} == HOLD_IDS, excluded
    assert len(queue) == 40, len(queue)
    report = dict(audit_date='2026-10-07', scope='Step 1 only: 679 Drill generators; Tryout and stock excluded',
                  adjustment_enabled=False, approval_status='NO_APPROVED_CONTROL',
                  limits=dict(exhaustive_tuple_limit=exhaustive_limit, random_probes_per_large_domain=probes, valid_context_anchors=12),
                  methodology=dict(feasibility='Runtime filters, constraints and global validators; no others to measure the whole family.',
                                   independence='Per-input contrasts fix all other direct inputs; graph paths and text-based revised oracles supplement observations.',
                                   workload='Digit/sign/decimal/fraction/radical representation proxy only; not a psychometric or monotonic difficulty score.',
                                   capacity='Exact for exhaustive domains; lower/upper bounds for probes. A complete witnessed input projection is not a complete joint domain.',
                                   exclusions='Four HOLD_SOURCE originals; forty revised originals without configs queued. No student data or automatic adjustment.'),
                  source_sha256=manifest, summary=summarize(rows, excluded, queue),
                  generators=rows, excluded_hold=excluded, waiting_for_generator=queue)
    review_report(report, bank, configs)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_csv(output.with_suffix('.csv'), rows)
    print(json.dumps(report['summary']), flush=True)
    return report


def review_report(report, bank, configs):
    """Finalize interpretation from pinned numeric evidence without resampling."""
    assert report['source_sha256'] == source_manifest(), 'Stale source evidence'
    for row in report['generators']:
        original = bank.get(row['question_id'])
        cfg, cfg_hash = configs.load(original['id'])
        assert (original['version'], original['hash'], cfg['config_version'], cfg_hash) == (row['original_version'], row['original_hash'], row['config_version'], row['config_hash'])
        apply_analytic_proof(original, cfg, row)
        _, deps = dependency_map(cfg)
        for name, item in row['inputs'].items():
            group, reason = classify(original['id'], name, item['effective_domain']['values'], deps, item['controlled_contrasts'])
            if group == 'NO_EFFECT' and not item['effective_domain']['exact']:
                group, reason = 'NEEDS_REVIEW', 'Incomplete projection: no-effect is not proven.'
            item.update(effect_group=group, rationale=reason, classification_status='PROPOSED_STATIC_AUDIT')
            item['review_groups'] = dict(feasible_within_current_rules=item['feasible'],
                                       potential_workload=group in ('POTENTIAL_WORKLOAD', 'CONTENT_PROFILE'),
                                       display_or_numeric_context=group in ('DISPLAY_CONTEXT', 'NUMERIC_CONTEXT'),
                                       no_approved_adjustment=True)
        metadata = original.get('metadata', {})
        row['source_review_status'] = metadata.get('source_review_status', 'NOT_RECORDED')
        row['generator_implementation_status'] = metadata.get('generator_status', 'CONFIG_AVAILABLE')
        row['evidence_sha256'] = {p: hashlib.sha256((ROOT.parent / p).read_bytes()).hexdigest() for p in row['evidence']}
    report['summary'] = summarize(report['generators'], report['excluded_hold'], report['waiting_for_generator'])
    report['audit_tool_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['checker_source_sha256'] = {str(p.relative_to(ROOT.parent)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in sorted((ROOT / 'tests').glob('*math.py'))}


def evidence_paths(qid):
    if qid in REVISED_6_10:
        return ['docs/audits/2026-10-07-revised-6-10-generator-audit.md', 'variant_gen/tests/test_drill_6_10_revised_generators.py']
    if qid in REVISED_11_15:
        return ['docs/audits/2026-10-07-revised-11-15-generator-audit.md', 'variant_gen/tests/test_drill_11_15_revisions.py']
    if qid in REVISED_16_19:
        return ['docs/audits/2026-10-07-drill-16-19-source-revision.md', 'variant_gen/tests/test_transform_property_generators.py']
    if qid in REVISED_20_23:
        return ['docs/audits/2026-10-07-revised-20-23-generator-audit.md', 'variant_gen/tests/test_drill_20_23_revisions.py']
    return ['docs/GENERATOR.md', 'variant_gen/tests/test_variant_gen.py']


def summarize(rows, excluded, queue):
    inputs = [i for row in rows for i in row['inputs'].values()]
    return dict(generators=len(rows), direct_inputs=len(inputs),
                methods=dict(Counter(row['method'] for row in rows)),
                effect_groups=dict(Counter(i['effect_group'] for i in inputs)),
                exact_effective_projections=sum(i['effective_domain']['exact'] for i in inputs),
                witnessed_feasible_inputs=sum(i['feasible'] for i in inputs),
                independent_math_checks=sum(row['independent_math_checks'] for row in rows),
                checked_input_tuples=sum(row['checked_input_tuples'] for row in rows),
                inputs_with_numeric_representation_changes=sum(i['controlled_contrasts']['proxy_changes'] > 0 for i in inputs),
                excluded_hold=len(excluded), waiting_for_generator=len(queue),
                approved_controls=0, enabled_adjustments=0)


def write_csv(path, rows):
    fields = ['question_id', 'input', 'original_version', 'original_hash', 'config_version', 'config_hash',
              'method', 'effective_domain_exact', 'effective_values', 'unresolved_values', 'effect_group',
              'rationale', 'capacity_exact', 'capacity_lower', 'capacity_upper', 'proxy_changed_pairs',
              'approval_status', 'adjustment_enabled']
    with path.open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            for name, item in row['inputs'].items():
                writer.writerow(dict(question_id=row['question_id'], input=name,
                                     **{f: row[f] for f in ('original_version', 'original_hash', 'config_version', 'config_hash', 'method')},
                                     effective_domain_exact=item['effective_domain']['exact'],
                                     effective_values=json.dumps(item['effective_domain']['values']),
                                     unresolved_values=json.dumps(item['effective_domain']['unresolved_values']),
                                     effect_group=item['effect_group'], rationale=item['rationale'],
                                     capacity_exact=row['capacity']['exact'], capacity_lower=row['capacity']['lower_bound'],
                                     capacity_upper=row['capacity']['upper_bound'],
                                     proxy_changed_pairs=item['controlled_contrasts']['proxy_changes'],
                                     approval_status=item['approval_status'], adjustment_enabled=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--exhaustive-limit', type=int, default=100000)
    parser.add_argument('--probes', type=int, default=1000)
    args = parser.parse_args()
    run(args.output, args.exhaustive_limit, args.probes)
