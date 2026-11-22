"""Preregistered synthetic anchor experiments, never imports DB/env loaders."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import random

from research.irt.synthetic import generate
from numora_service.irt.anchor_uncertainty import evaluate, transformed_contrasts
from numora_service.irt.gates import anchor_gate

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'research/irt/anchor-v2'


def read(name):
    return json.loads((DIRECTORY / name).read_text(encoding='utf-8'))


def digest(value):
    """Local research recipe, explicitly NOT PostgreSQL's canonical digest."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def sample(rng, theta, a, steps):
    # Independent implementation, not the service probability routine.
    logits = [0.] + [a * (k * theta - sum(steps[:k])) for k in range(1, len(steps) + 1)]
    weights = [math.exp(x - max(logits)) for x in logits]
    return rng.choices(range(len(weights)), weights=weights)[0]


def design(scenario, seed, model='MIXED'):
    counts = scenario['counts']
    value, truth = generate(max(counts), seed, model, len(counts))
    order = [p['armId'] for p in value['packages']]
    keep, seen = set(), Counter()
    for person in value['respondents']:
        arm = person['deliveredArmId']
        if seen[arm] < counts[order.index(arm)]:
            keep.add(person['attemptId'])
        seen[arm] += 1
    people = [p for p in value['respondents'] if p['attemptId'] in keep]
    items = value['items']
    anchors = value['anchorQuestionVersionIds']
    responses = {p['attemptId']: {} for p in people}
    by_arm = {arm: deepcopy(truth['items']) for arm in order}
    for arm in order[1:]:
        for j, shift in enumerate(scenario['stepShifts']):
            qid = anchors[j]
            a, steps = by_arm[arm][qid]
            by_arm[arm][qid] = (a, [x + shift for x in steps])
        if scenario['logSlopeShift']:
            qid = anchors[0]
            a, steps = by_arm[arm][qid]
            by_arm[arm][qid] = (a * math.exp(scenario['logSlopeShift']), steps)
    rng = random.Random(seed + 8071)
    people_map = {p['attemptId']: p for p in people}
    for row in value['responses']:
        aid = row['attemptId']
        if aid not in keep:
            continue
        arm = people_map[aid]['deliveredArmId']
        qid = row['questionVersionId']
        changed = arm != order[0] and (qid in anchors[:len(scenario['stepShifts'])] or scenario['logSlopeShift'] and qid == anchors[0])
        responses[aid][qid] = sample(rng, truth['theta'][aid], *by_arm[arm][qid]) if changed else row['scoreCategory']
    work = {'policy': read('policy.json'), 'items': items,
            'matrix': [[responses[p['attemptId']].get(i['questionVersionId']) for i in items] for p in people],
            'groups': [p['deliveredArmId'] for p in people], 'groupOrder': order, 'anchors': anchors}
    actual_counts = Counter(work['groups'])
    categories = {arm: {qid: Counter() for qid in anchors} for arm in order}
    for row, arm in zip(work['matrix'], work['groups']):
        for qid in anchors:
            categories[arm][qid][row[next(j for j, i in enumerate(items) if i['questionVersionId'] == qid)]] += 1
    quality = work['policy']['quality']
    supported = all(actual_counts[arm] >= quality['minimumArmCount'] and all(
        categories[arm][qid][k] >= quality['minimumCategoryCount'] for qid in anchors
        for k in range(next(i for i in items if i['questionVersionId'] == qid)['maximumScoreCategory'] + 1)) for arm in order)
    return work, {'seed': seed, 'parametersByArm': by_arm, 'counts': dict(actual_counts),
                  'anchorCategoryCounts': categories, 'selectionSupported': supported,
                  'model': model, 'hasInjectedDIF': bool(scenario['stepShifts'] or scenario['logSlopeShift'])}


def reference_sensitivity(raw, reference):
    refit = raw.get('referenceRefit', {})
    if refit.get('converged') is not True or refit.get('atParameterBoundary') is not False:
        return {'diagnosticOnly': True, 'evaluated': False}
    joint = raw['joint']
    rows = []
    for qid, pin in refit['items'][reference].items():
        first = joint['items'][reference][qid]
        def parameters(block, indexes):
            a = block['values'][indexes['a']]
            d = [block['values'][j] for j in indexes['intercepts']]
            return a, [-(value - (d[k - 1] if k else 0)) / a for k, value in enumerate(d)]
        a, steps = parameters(joint, first)
        b, other = parameters(refit, pin)
        if a <= 0 or b <= 0:
            return {'diagnosticOnly': True, 'evaluated': False, 'reason': 'INVALID_REFERENCE_PARAMETERS'}
        rows.append({'questionVersionId': qid, 'deltaLogA': math.log(b / a),
                     'stepDifferences': [y - x for x, y in zip(steps, other)]})
    return {'diagnosticOnly': True, 'evaluated': True, 'items': rows,
            'studentResultsProduced': False}


def evidence(raw, work, truth):
    gate = evaluate(raw, work['anchors'], work['groupOrder'][0], work['groupOrder'][1:], work['policy'])
    if not truth['selectionSupported']:
        gate.update(passed=False, decision='INSUFFICIENT', reason='ANCHOR_CATEGORY_OR_SAMPLE_COVERAGE')
    coverage = []
    for qid, check in gate['checks'].items():
        for row in check.get('contrasts', []):
            base_a, base_steps = truth['parametersByArm'][work['groupOrder'][0]][qid]
            a, steps = truth['parametersByArm'][row['armId']][qid]
            actual = math.log(a / base_a) if row['metric'] == 'LOG_A' else steps[int(row['metric'].split('_')[1]) - 1] - base_steps[int(row['metric'].split('_')[1]) - 1]
            coverage.append(row['lower'] <= actual <= row['upper'])
            row.update(trueEffect=actual, covered=coverage[-1])
    legacy = anchor_gate(raw.get('anchors', {}), work['anchors'], work['policy']['quality'])
    return {'gate': gate, 'legacyPointGate': legacy, 'allContrastsCovered': bool(coverage) and all(coverage),
            'contrastCount': len(coverage), 'referenceSensitivity': reference_sensitivity(raw, work['groupOrder'][0]) if raw.get('joint') else {'evaluated': False, 'diagnosticOnly': True}}


def bootstrap_work(parent_work, block, seed):
    """Sample a fitted model, retaining package structural missingness exactly."""
    work = deepcopy(parent_work)
    rng = random.Random(seed)
    truth = {'seed': seed, 'parametersByArm': {}, 'selectionSupported': True, 'bootstrapConditionalOnParent': True}
    for arm in work['groupOrder']:
        truth['parametersByArm'][arm] = {}
        for qid, pin in block['items'][arm].items():
            a = block['values'][pin['a']]
            d = [block['values'][j] for j in pin['intercepts']]
            truth['parametersByArm'][arm][qid] = (a, [-(v - (d[k - 1] if k else 0)) / a for k, v in enumerate(d)])
    for row, arm in zip(work['matrix'], work['groups']):
        latent = block['latent'][arm]
        theta = rng.gauss(latent['mean'], math.sqrt(latent['variance']))
        for j, item in enumerate(work['items']):
            if row[j] is not None:
                row[j] = sample(rng, theta, *truth['parametersByArm'][arm][item['questionVersionId']])
    work['operation'] = 'BOOTSTRAP_REFIT'
    work['bootstrapAnchor'] = work['anchors'][0]
    return work, truth


def wilson(k, n):
    if not n:
        return None
    z = 1.959963984540054
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [max(0., center - radius), min(1., center + radius)]


def summarize(records, study, phase):
    rows = []
    target = study['phases'][phase]['replications']
    for scenario in study['scenarios']:
        observed = [r for r in records if r['scenario'] == scenario['id'] and r['phase'] == phase]
        dif = bool(scenario['stepShifts'] or scenario['logSlopeShift'])
        correct = 'MATERIAL_DIFFERENCE' if dif else 'EQUIVALENT'
        wrong = 'EQUIVALENT' if dif else 'MATERIAL_DIFFERENCE'
        decisions = Counter(r.get('evidence', {}).get('gate', {}).get('decision', 'FAILED') for r in observed)
        supported = [r for r in observed if r.get('truth', {}).get('selectionSupported')]
        conditional = Counter(r.get('evidence', {}).get('gate', {}).get('decision', 'FAILED') for r in supported)
        n = len(observed)
        correct_interval, wrong_interval = wilson(decisions[correct], n), wilson(decisions[wrong], n)
        full = n == target
        power_required = scenario['id'] in study['acceptance']['powerScenarios']
        accepted = full and wrong_interval[1] <= study['acceptance']['maximumErrorUpperBound'] and (not power_required or correct_interval[0] >= study['acceptance']['minimumCorrectLowerBound']) if phase == 'confirmation' else None
        rows.append({'scenario': scenario['id'], 'completed': n, 'required': target, 'complete': full,
                     'decisions': dict(decisions), 'correctWilson95': correct_interval, 'wrongWilson95': wrong_interval,
                     'eligibleDenominator': len(supported), 'eligibleDecisions': dict(conditional),
                     'simultaneousCoverageWilson95': wilson(sum(r.get('evidence', {}).get('allContrastsCovered', False) for r in observed), n),
                     'accepted': accepted, 'legacyHeld': sum(not r.get('evidence', {}).get('legacyPointGate', {}).get('passed', False) for r in observed)})
    status = 'INCOMPLETE' if not all(r['complete'] for r in rows) else 'SCREENING_COMPLETE' if phase == 'screening' else 'ACCEPTED_RESEARCH_ONLY' if all(r['accepted'] for r in rows) else 'NOT_ACCEPTED'
    return {'purpose': 'RESEARCH_ONLY', 'productionApproved': False, 'phase': phase,
            'status': status,
            'scenarios': rows, 'allFailuresRemainInDenominator': True, 'canonicalScoring': False}
