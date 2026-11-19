"""Run a frozen Drill fixture locally; never reads dotenv or a database."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from numora_service.irt.producer import policy, run
from numora_service.irt.runner import run as run_r


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def execute(value, image):
    dispatch = {
        'executionId': '66666666-6666-4666-8666-666666666666',
        'dispatchGeneration': 1,
    }
    return run(value, dispatch, lambda work: run_r(work, image=image))


def main():
    parser = argparse.ArgumentParser(description='Research-only Drill IRT fixture runner')
    parser.add_argument('--input', type=Path, default=Path('contracts/irt-calibration-v1/examples/drill-input.json'))
    parser.add_argument('--image', required=True, help='Pinned R producer image')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()

    image = subprocess.check_output(
        ['docker', 'image', 'inspect', args.image, '--format', '{{.Id}}'], text=True
    ).strip()
    value = json.loads(args.input.read_text(encoding='utf-8'))
    if value.get('ecosystem') != 'DRILL' or value.get('context', {}).get('scope') != 'LEVEL':
        raise SystemExit('DRILL_LEVEL_FIXTURE_REQUIRED')
    started = time.monotonic()
    result, diagnostics = execute(value, image)
    report = {
        'experimentKind': 'DRILL_RESEARCH_ONLY',
        'input': str(args.input),
        'image': image,
        'elapsedSeconds': time.monotonic() - started,
        'artifactDigest': digest(result),
        'result': result,
        'diagnostics': diagnostics,
    }
    if args.replay:
        replay, _ = execute(value, image)
        report['replayDigest'] = digest(replay)
        report['replayMatch'] = report['artifactDigest'] == report['replayDigest']
        if not report['replayMatch']:
            raise SystemExit('DRILL_REPLAY_DIGEST_MISMATCH')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({
        'state': result['outcome']['measurementState'],
        'scored': sum(r['status'] == 'SCORED' for r in result['outcome']['respondents']),
        'artifactDigest': report['artifactDigest'],
        'replayMatch': report.get('replayMatch'),
        'seconds': report['elapsedSeconds'],
    }))


if __name__ == '__main__':
    main()
