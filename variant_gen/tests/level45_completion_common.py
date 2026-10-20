"""Offline authoring/review helpers; quarantined proposals are never workspace inputs."""
import csv
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import original_hash, option_ids
from build_drill_1_5_level45_batch1 import Author, safe_algebra

PRIOR_AUDIT = REPO/'docs/audits/2026-10-19-original-question-audit'
LIVE_DATA = ROOT/'data/drill-1-indicators-1-5-levels-4-5-batch2'
DRAFT_DATA = ROOT/'drafts/2026-10-20-level45-academic'


def entries(indicators=None):
    source = json.loads((PRIOR_AUDIT/'stage-06-matching-indicators-01-05/matching.json').read_text(encoding='utf-8'))['entries']
    with (REPO/'docs/audits/2026-10-20-drill-1-5-level45-batch1/pending.csv').open(encoding='utf-8',newline='') as f:
        pending = {p['audit_id']: p['status'] for p in csv.DictReader(f)}
    return [(e, pending[e['audit_id']]) for e in source if e['audit_id'] in pending and
            (indicators is None or e['indicator'] in indicators)]


def academic(entry):
    name = {1:'stage-02-academic-indicator-01', 2:'stage-03-academic-indicator-02',
            3:'stage-04-academic-indicator-03', 4:'stage-05-academic-indicators-04-05',
            5:'stage-05-academic-indicators-04-05'}[entry['indicator']]
    return next(e for e in json.loads((PRIOR_AUDIT/name/'audit.json').read_text(encoding='utf-8'))['entries']
                if e['audit_id'] == entry['audit_id'])


def review_original(entry, draft=False):
    """In-memory sandbox only: never persists ACTIVE for a held source/proposal."""
    s = entry['source_projection']
    qid = f"{s['format'].lower()}-{entry['indicator']}-{entry['level']}-{entry['source_number']}"
    ids = option_ids(s['format'],len(s['options']))
    o = dict(id=qid, format=s['format'], cognitive_level='', version=2 if draft else 1,
             stem=safe_algebra(s['stem']),
             options=[dict(id=i,text=safe_algebra(t),correct=i in s['key']) for i,t in zip(ids,s['options'])],
             metadata=dict(generation_status='ACTIVE', category_labels=s.get('category_labels') or ['Benar','Salah']))
    o['hash'] = original_hash(o)
    return o


def key(entry):
    s = entry['source_projection']
    return f"{s['format'].lower()}-{entry['indicator']}-{entry['level']}-{entry['source_number']}"
