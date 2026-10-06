"""Reviewed, finite conceptual content. Reads assets; never generates or writes variants."""
import json
from copy import deepcopy
from pathlib import Path

from bank import BankError
from filters import validate_candidate
from store import StoreError

# ponytail: approved Drill 1 inventory only; review new families before extending this set.
CONCEPTUAL_IDS = frozenset('''
pg-1-1-4 mcma-1-1-8 kategori-1-1-10 kategori-1-2-10 kategori-1-3-10
pg-2-2-5 pg-2-3-1 pg-2-3-4 pg-2-3-5 pg-5-2-4
mcma-6-1-6 mcma-6-2-6 mcma-6-3-6 kategori-6-3-9
kategori-7-1-10 kategori-7-2-10 pg-7-3-1 kategori-9-1-10 kategori-10-2-10
pg-11-1-1 mcma-11-1-8 kategori-11-1-9 mcma-11-2-6 kategori-11-2-9 mcma-11-5-6
pg-12-2-4 kategori-12-3-10
pg-14-1-1 mcma-14-1-6 kategori-14-1-9 pg-14-2-1 pg-14-3-1 pg-14-4-1
pg-14-4-3 kategori-14-4-10 pg-14-5-1 kategori-14-5-10
pg-15-1-3 mcma-15-2-7 pg-15-3-3 pg-15-5-3
pg-16-1-1 pg-16-1-2 mcma-16-1-6 kategori-16-1-9 kategori-16-2-9 pg-16-3-2
pg-17-3-2 kategori-17-3-10
pg-20-1-1 mcma-20-1-6 kategori-20-1-9 kategori-20-1-10 pg-20-2-1 mcma-20-2-7
kategori-20-2-10 pg-20-3-5 mcma-20-3-8 pg-21-2-5
pg-22-1-4 mcma-22-1-8 pg-22-2-3 pg-22-2-5 mcma-22-2-8 pg-22-3-5
pg-23-1-1 pg-23-1-2
'''.split())


def load_stock(path: Path, bank) -> dict[str, list[dict]]:
    path = Path(path)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if (not isinstance(payload, dict) or type(payload.get('schema_version')) is not int
                or payload['schema_version'] != 1 or not isinstance(payload.get('variants'), list)):
            raise ValueError('expected schema_version 1 and variants array')
        groups, comparisons = {}, {}
        for item in payload['variants']:
            if not isinstance(item, dict):
                raise ValueError('stock item must be an object')
            qid = item.get('question_id')
            if not isinstance(qid, str) or qid not in CONCEPTUAL_IDS:
                raise ValueError(f'question outside approved conceptual inventory: {qid}')
            original = bank.get(qid)
            if original.get('metadata', {}).get('generation_status') == 'HOLD_SOURCE':
                raise ValueError(f'{qid}: source is on hold')
            for name in ('stock_index', 'stock_version', 'original_version'):
                if type(item.get(name)) is not int or item[name] < 1:
                    raise ValueError(f'{qid}: invalid {name}')
            if item['stock_index'] > 4 or item.get('variant_id') != f"{qid}:stock-{item['stock_index']:02d}":
                raise ValueError(f'{qid}: invalid variant ID/index (maximum 4)')
            if item.get('original_hash') != original['hash'] or item['original_version'] != original['version']:
                raise ValueError(f'{qid}: original hash/version mismatch')
            for name in ('stem', 'key', 'explanation', 'variation_note', 'review_note'):
                if not isinstance(item.get(name), str) or not item[name].strip() and name != 'key':
                    raise ValueError(f'{qid}: empty/invalid {name}')
            if item.get('review_status') not in ('DRAFT', 'VERIFIED'):
                raise ValueError(f'{qid}: invalid review status')
            options = item.get('options')
            ids = [o['id'] for o in original['options']]
            if (not isinstance(options, list) or len(options) != len(ids)
                    or any(not isinstance(o, dict) or not isinstance(o.get('text'), str)
                           or o.get('id') != oid for o, oid in zip(options, ids))):
                raise ValueError(f'{qid}: invalid options/IDs')
            keys = item['key'].split(',') if item['key'] else []
            if len(keys) != len(set(keys)) or set(keys) - set(ids):
                raise ValueError(f'{qid}: invalid key')
            cand = dict(stem=item['stem'], explanation=item['explanation'],
                        options=[dict(o, correct=o['id'] in keys) for o in options])
            problems = validate_candidate(cand, original, comparisons.get(qid, []), allow_same_answer=True)
            if problems:
                raise ValueError(f"{item['variant_id']}: {', '.join(problems)}")
            comparisons.setdefault(qid, []).append(cand)
            groups.setdefault(qid, []).append(item)
        for qid, items in groups.items():
            items.sort(key=lambda item: item['stock_index'])
            if len(items) > 4 or [i['stock_index'] for i in items] != list(range(1, len(items) + 1)):
                raise ValueError(f'{qid}: duplicate/noncontiguous indices or more than 4 items')
            verified = [i for i in items if i['review_status'] == 'VERIFIED']
            if [i['stock_index'] for i in verified] != list(range(1, len(verified) + 1)):
                raise ValueError(f'{qid}: VERIFIED indices must be a contiguous prefix')
        return {qid: deepcopy([i for i in items if i['review_status'] == 'VERIFIED'])
                for qid, items in groups.items() if any(i['review_status'] == 'VERIFIED' for i in items)}
    except (OSError, ValueError, BankError, KeyError, TypeError) as error:
        raise StoreError(f'Cannot load conceptual stock: {error}') from error


def stock_record(original: dict, item: dict) -> dict:
    if (item['question_id'] != original['id'] or item['original_hash'] != original['hash']
            or item['original_version'] != original['version'] or item['review_status'] != 'VERIFIED'):
        raise StoreError('Stock does not match this original or is not VERIFIED')
    labels = original.get('metadata', {}).get('category_labels', ['Benar', 'Salah'])
    return {
        'record_id': f"{item['variant_id']}:v{item['stock_version']}",
        'question_id': original['id'], 'source_kind': 'conceptual_stock',
        'variant_id': item['variant_id'], 'stock_index': item['stock_index'],
        'seed': None, 'variant_ver': item['stock_version'], 'config_ver': None,
        'config_hash': None, 'draws_used': None, 'values_used': {},
        'format': original['format'], 'cognitive_level': original['cognitive_level'],
        'classification': deepcopy(original.get('classification')),
        'original_hash': original['hash'], 'original_version': original['version'],
        'stem': item['stem'], 'options': deepcopy(item['options']), 'key': item['key'],
        'explanation': item['explanation'], 'variation_note': item['variation_note'],
        **({'answer_categories': {o['id']: labels[0] if o['id'] in item['key'].split(',') else labels[1]
                                  for o in item['options']}} if original['format'] == 'KATEGORI' else {}),
    }
