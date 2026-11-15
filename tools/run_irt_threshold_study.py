"""Screen sample/arm and candidate threshold sensitivity; research-only."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.irt.synthetic import generate
from numora_service.irt.producer import policy, run
from numora_service.irt.runner import run as run_r

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def profiles(base):
    for slope, step, category, discrimination, difficulty in product(
        [0.10, 0.20, 0.30], [0.20, 0.30, 0.50], [10, 20, 30],
        [0.20, 0.30, 0.40], [0.30, 0.40, 0.50]
    ):
        p = deepcopy(base)
        p['quality'].update(anchorLogSlopeTolerance=slope, anchorDifficultyTolerance=step, minimumCategoryCount=category, maximumDiscriminationSE=discrimination, maximumDifficultySE=difficulty)
        yield p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--per-arm', type=int, nargs='+', default=[500, 1000, 1500, 2000])
    parser.add_argument('--arms', type=int, nargs='+', choices=[2], default=[2])
    parser.add_argument('--seeds', type=int, nargs='+', default=[20261115, 20261116, 20261117])
    parser.add_argument('--sensitivity', action='store_true')
    args = parser.parse_args()
    image = subprocess.check_output(['docker', 'image', 'inspect', args.image, '--format', '{{.Id}}'], text=True).strip()
    base = policy(); args.output.mkdir(parents=True, exist_ok=True)
    selected = list(profiles(base)) if args.sensitivity else [base]; rows = []
    for arms in args.arms:
        for n in args.per_arm:
            for seed in args.seeds:
                for profile in selected:
                    started = time.monotonic()
                    value, _ = generate(n, seed, 'MIXED', arms)
                    profile['runtime']['maximumRespondents'] = max(profile['runtime']['maximumRespondents'], n * arms)
                    try:
                        result, diagnostics = run(value, {'executionId': '55555555-5555-4555-8555-555555555555', 'dispatchGeneration': 1}, lambda work: run_r(work, image=image), profile=profile, allow_research_profile=True)
                        outcome = result['outcome']
                        row = {'arms': arms, 'participantsPerArm': n, 'seed': seed, 'policyDigest': digest(profile), 'inputDigest': digest(value), 'image': image, 'measurementState': outcome['measurementState'], 'calibratedArmCount': sum(p['measurementState'] == 'CALIBRATED' for p in outcome['packages']), 'totalArmCount': len(outcome['packages']), 'scoredRespondentCount': sum(r['status'] == 'SCORED' for r in outcome['respondents']), 'anchorReasons': dict(Counter(reason for c in diagnostics.get('anchorGate', {}).get('checks', {}).values() for reason in c.get('reasons', []))), 'itemFailureReasons': dict(Counter(reason for i in outcome['items'] for reason in i.get('reasonCodes', []))), 'converged': diagnostics.get('converged'), 'durationSeconds': round(time.monotonic() - started, 3)}
                    except Exception as exc:
                        row = {'arms': arms, 'participantsPerArm': n, 'seed': seed, 'policyDigest': digest(profile), 'inputDigest': digest(value), 'image': image, 'measurementState': 'BLOCKED', 'error': type(exc).__name__ + ': ' + str(exc), 'durationSeconds': round(time.monotonic() - started, 3)}
                    rows.append(row); print(json.dumps(row), flush=True)
    (args.output / 'summary.json').write_text(json.dumps({'purpose': 'RESEARCH_ONLY', 'productionApproved': False, 'image': image, 'rows': rows, 'note': 'Synthetic sensitivity study. No production threshold or bank approval follows.'}, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__': raise SystemExit(main())
