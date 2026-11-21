"""Resume pinned, serial anchor research. No database or service enablement.

run --phase screening|confirmation; bootstrap; summarize. A non-accepted or
incomplete report exits nonzero. Bootstrap is a covariance oracle only, never
a complete linking decision or participant artifact.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.irt.anchor_study import bootstrap_work, design, digest, evidence, read, summarize, wilson
from numora_service.irt.anchor_uncertainty import intervals, transformed_contrasts
from numora_service.irt.runner import run as run_r

SOURCES = ['Dockerfile.irt-anchor-v2', 'research/irt/anchor-v2/compute.R',
           'research/irt/anchor-v2/policy.json', 'research/irt/anchor-v2/study.json',
           'research/irt/anchor_study.py', 'research/irt/synthetic.py',
           'numora_service/irt/anchor_uncertainty.py', 'numora_service/irt/runner.py',
           'numora_service/irt/gates.py', 'tools/study_irt_anchors.py']
BASELINE = ['research/irt/policy-v1.json', 'research/irt/compute.R',
            'research/irt-runtime-linux-v1.json', 'research/irt-runtime-windows-v4.json']


def pins(image):
    return {'version': 'anchor-linking-cli-runtime-v2', 'purpose': 'RESEARCH_ONLY',
            'productionApproved': False, 'image': image,
            'python': platform.python_version(), 'system': platform.system(), 'machine': platform.machine(),
            'sourceHashRecipe': 'SHA256_UTF8_LF',
            'sourceSha256': {p: hashlib.sha256((ROOT / p).read_bytes().replace(b'\r\n', b'\n')).hexdigest() for p in SOURCES + BASELINE},
            'inputDigestRecipe': 'ANCHOR_RESEARCH_JSON_SORTED_V1_NOT_CANONICAL_PG',
            'concurrency': 1, 'timeoutSeconds': 900}


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    os.replace(temp, path)


@contextmanager
def locked(folder):
    """OS-released lock: crash/restart cannot leave a false running lock."""
    handle = (folder / '.study.lock').open('a+b')
    handle.seek(0)
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise ValueError('STUDY_ALREADY_RUNNING') from None
    try:
        yield
    finally:
        handle.close()


def checkpoint(folder, name, work, pin, metadata, execute):
    file = folder / (name + '.json')
    expected = {'runtimeDigest': digest(pin), 'inputDigest': digest(work), **metadata}
    if file.exists():
        report = json.loads(file.read_text(encoding='utf-8'))
        if report['pin'] != expected or report['reportDigest'] != digest({k: v for k, v in report.items() if k != 'reportDigest'}):
            raise ValueError('CHECKPOINT_PROVENANCE_CHANGED')
        return report, False
    started = time.monotonic()
    report = {'pin': expected, 'startedAt': datetime.now(timezone.utc).isoformat()}
    last = [started]
    def heartbeat():
        if time.monotonic() - last[0] >= 15:
            print(json.dumps({'progress': name, 'elapsedSeconds': round(time.monotonic() - started, 1)}), flush=True)
            last[0] = time.monotonic()
    try:
        # Source edits, even between cases, invalidate continuation rather than
        # silently pooling experiments with different scientific implementations.
        if pins(pin['image']) != pin:
            raise ValueError('SOURCE_PIN_CHANGED')
        report['raw'] = execute(work, heartbeat)
        if pins(pin['image']) != pin:
            raise ValueError('SOURCE_PIN_CHANGED')
    except ValueError as error:
        code = str(error)
        if code not in {'TIMEOUT', 'DEPENDENCY_UNAVAILABLE'}:
            raise
        report.update(raw={}, failureCode=code)
    report['elapsedSeconds'] = time.monotonic() - started
    report['reportDigest'] = digest(report)
    save(file, report)
    return report, True


def records(folder, pin):
    result = []
    for path in sorted(folder.glob('*-result.json')):
        row = json.loads(path.read_text(encoding='utf-8'))
        if row['runtimeDigest'] != digest(pin) or row['digest'] != digest({k: v for k, v in row.items() if k != 'digest'}):
            raise ValueError('RESULT_PROVENANCE_CHANGED')
        result.append(row)
    return result


def run_phase(args, folder, pin):
    study = read('study.json')
    completed = 0
    for index, scenario in enumerate(study['scenarios']):
        for replication in range(study['phases'][args.phase]['replications']):
            name = f'{args.phase}-{scenario["id"]}-{replication + 1:03}'
            seed = study['phases'][args.phase]['seedBase'] + index * 1000 + replication
            work, truth = design(scenario, seed)
            report, created = checkpoint(folder, name, work, pin,
                {'phase': args.phase, 'scenario': scenario['id'], 'seed': seed},
                lambda w, h: run_r(w, h, image=pin['image'], timeout=900) if truth['selectionSupported'] else {'converged': False, 'reason': 'SELECTION_INSUFFICIENT'})
            file = folder / (name + '-result.json')
            result = {'runtimeDigest': digest(pin), 'phase': args.phase, 'scenario': scenario['id'],
                      'replication': replication + 1, 'seed': seed, 'rawReportDigest': report['reportDigest'],
                      'truth': {k: v for k, v in truth.items() if k != 'parametersByArm'},
                      'failureCode': report.get('failureCode'), 'evidence': evidence(report['raw'], work, truth)}
            result['digest'] = digest(result)
            result = json.loads(json.dumps(result))
            if file.exists() and json.loads(file.read_text(encoding='utf-8')) != result:
                raise ValueError('RESULT_PROVENANCE_CHANGED')
            save(file, result)
            summary = summarize(records(folder, pin), study, args.phase)
            save(folder / (args.phase + '-summary.json'), summary)
            print(json.dumps({'case': name, 'cached': not created, 'decision': result['evidence']['gate']['decision'],
                              'seconds': round(report['elapsedSeconds'], 2), 'phaseStatus': summary['status']}), flush=True)
            completed += created
            if args.max_new is not None and completed >= args.max_new:
                return summary
    return summarize(records(folder, pin), study, args.phase)


def run_bootstrap(args, folder, pin):
    setting = read('study.json')['bootstrap']
    cases = []
    new = 0
    for model_index, model in enumerate(setting['models']):
        for shift_index, shift in enumerate(setting['stepShifts']):
            key = f'bootstrap-{model}-shift-{shift}'
            scenario = {'counts': [setting['perArm']] * 2, 'stepShifts': [shift] if shift else [], 'logSlopeShift': 0}
            work, _ = design(scenario, setting['parentSeedBase'] + model_index * 1000 + shift_index, model)
            parent, _ = checkpoint(folder, key + '-parent', work, pin, {'kind': 'BOOTSTRAP_PARENT', 'model': model, 'shift': shift},
                                   lambda w, h: run_r(w, h, image=pin['image']))
            block = parent['raw'].get('released', {}).get(work['anchors'][0])
            if not block or block.get('converged') is not True or block.get('atParameterBoundary') is not False:
                cases.append({'case': key, 'status': 'PARENT_UNAVAILABLE', 'required': setting['replications'], 'completed': 0})
                continue
            ref, arms = work['groupOrder'][0], work['groupOrder'][1:]
            actual, _ = transformed_contrasts(block['values'], block['mapping'], ref, arms)
            observed = []
            for i in range(setting['replications']):
                name = key + f'-{i + 1:03}'
                sampled, truth = bootstrap_work(work, block, setting['seedBase'] + model_index * 10000 + shift_index * 1000 + i)
                report, created = checkpoint(folder, name, sampled, pin,
                    {'kind': 'BOOTSTRAP_COVARIANCE_ORACLE_ONLY', 'parentDigest': parent['reportDigest'], 'replication': i + 1},
                    lambda w, h: run_r(w, h, image=pin['image']))
                try:
                    estimated = intervals(report['raw']['target'], ref, arms, work['policy'], 0)
                    contrasts = estimated['contrasts']
                    covered = all(r['lower'] <= t['estimate'] <= r['upper'] for r, t in zip(contrasts, actual))
                    row = {'replication': i + 1, 'covered': covered, 'estimates': [r['estimate'] for r in contrasts], 'standardErrors': [r['standardError'] for r in contrasts]}
                except (ValueError, KeyError, TypeError):
                    row = {'replication': i + 1, 'covered': False, 'failureCode': report.get('failureCode', 'BOOTSTRAP_REFIT_UNAVAILABLE')}
                observed.append(row)
                status = {'case': key, 'status': 'COMPLETE' if len(observed) == setting['replications'] else 'INCOMPLETE',
                          'completed': len(observed), 'required': setting['replications'],
                          'coverageWilson95': wilson(sum(r['covered'] for r in observed), len(observed)),
                          'failures': sum('failureCode' in r for r in observed), 'rows': observed,
                          'scope': 'CONDITIONAL_FITTED_MODEL_COVARIANCE_ORACLE_NOT_LINKING_APPROVAL'}
                usable = [r for r in observed if 'estimates' in r]
                status['components'] = [{
                    'metric': target['metric'], 'trueConditionalEffect': target['estimate'],
                    'usable': len(usable),
                    'empiricalSD': statistics.stdev(r['estimates'][j] for r in usable) if len(usable) > 1 else None,
                    'rmsEstimatedSE': (sum(r['standardErrors'][j] ** 2 for r in usable) / len(usable)) ** .5 if usable else None,
                    'bias': sum(r['estimates'][j] - target['estimate'] for r in usable) / len(usable) if usable else None
                } for j, target in enumerate(actual)]
                save(folder / (key + '-summary.json'), status)
                print(json.dumps({'case': name, 'covered': row['covered'], 'seconds': round(report['elapsedSeconds'], 2)}), flush=True)
                new += created
                if args.max_new is not None and new >= args.max_new:
                    return {'status': 'INCOMPLETE', 'cases': cases + [status]}
            cases.append(status)
    return {'purpose': 'RESEARCH_ONLY', 'status': 'COMPLETE' if len(cases) == 4 and all(c['status'] == 'COMPLETE' for c in cases) else 'INCOMPLETE', 'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'bootstrap', 'summarize'])
    parser.add_argument('--phase', choices=['screening', 'confirmation'], default='screening')
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-new', type=int, help='Checkpoint stop, never marks a partial phase complete')
    args = parser.parse_args()
    if args.max_new is not None and args.max_new < 1:
        parser.error('--max-new must be positive')
    profile = json.loads(args.profile.read_text(encoding='utf-8'))
    if profile != pins(profile['image']):
        raise ValueError('RUNTIME_OR_SOURCE_PIN_CHANGED')
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = args.output / 'runtime.json'
    if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8')) != profile:
        raise ValueError('CHECKPOINT_RUNTIME_CHANGED')
    if args.command != 'summarize':
        image = subprocess.check_output(['docker', 'image', 'inspect', profile['image'], '--format', '{{.Id}}'], text=True).strip()
        if image != profile['image']:
            raise ValueError('IMAGE_PIN_CHANGED')
        code = subprocess.check_output(['docker', 'run', '--rm', '--network', 'none', '--read-only',
            '--entrypoint', 'cat', image, '/opt/irt/compute.R'], timeout=30)
        if hashlib.sha256(code.replace(b'\r\n', b'\n')).hexdigest() != profile['sourceSha256']['research/irt/anchor-v2/compute.R']:
            raise ValueError('IMAGE_SOURCE_PIN_CHANGED')
    global_lock = ROOT / '.scratch/irt-anchor-v2-execution-lock'
    global_lock.mkdir(parents=True, exist_ok=True)
    with locked(global_lock), locked(args.output):
        save(manifest, profile)
        if args.command == 'run':
            result = run_phase(args, args.output, profile)
        elif args.command == 'bootstrap':
            result = run_bootstrap(args, args.output, profile)
            save(args.output / 'bootstrap-summary.json', result)
        else:
            result = summarize(records(args.output, profile), read('study.json'), args.phase)
        print(json.dumps(result), flush=True)
    if result['status'] not in {'ACCEPTED_RESEARCH_ONLY', 'COMPLETE', 'SCREENING_COMPLETE'}:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
