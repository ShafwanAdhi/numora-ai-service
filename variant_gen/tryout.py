"""Tryout response generation. No persistence or database access."""
from pathlib import Path

from bank import option_ids
from engine import original_record
from store import StoreError


def validate_manifest(manifest, bank=None):
    if (not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1
            or manifest.get('status') != 'LOCAL_PREVIEW'
            or not isinstance(manifest.get('package_id'), str)
            or type(manifest.get('seed')) is not int or not 1 <= manifest['seed'] <= 1_000_000_000
            or not isinstance(manifest.get('items'), list) or not manifest['items']):
        raise StoreError('Invalid local package manifest.')
    if bank is not None:
        groups=sorted((g for g in bank.catalog() if g['activity']=='TRYOUT' and g['package_id']==manifest['package_id']),key=lambda g:g['chapter'])
        roster=[qid for group in groups for qid in group['question_ids']]
        if not roster or [item.get('question_id') if isinstance(item,dict) else None for item in manifest['items']] != roster:
            raise StoreError('Package roster/order differs from the local catalog.')
    seen=set()
    for item in manifest['items']:
        if not isinstance(item, dict) or not isinstance(item.get('record'), dict):
            raise StoreError('Invalid package item.')
        rec=item['record'];qid=item.get('question_id')
        if (not isinstance(qid,str) or qid in seen or rec.get('question_id') != qid
                or item.get('status') not in ('VARIANT','ORIGINAL_ONLY')
                or not isinstance(rec.get('stem'),str) or not isinstance(rec.get('options'),list)
                or not isinstance(rec.get('key'),str)):
            raise StoreError('Invalid/duplicate package question.')
        seen.add(qid)
        options=rec['options']
        if (not options or any(not isinstance(o,dict) or not isinstance(o.get('id'),str)
                or not isinstance(o.get('text'),str) for o in options)):
            raise StoreError('Invalid package options.')
        ids=[o['id'] for o in options]
        expected_ids=option_ids(rec.get('format'),len(ids))
        if ids != expected_ids or rec.get('format') not in ('PG','MCMA','KATEGORI'):
            raise StoreError('Invalid package option identities/format.')
        correct=rec['key'].split(',') if rec['key'] else []
        if len(set(correct))!=len(correct) or not set(correct)<=set(ids) or (rec['format']=='PG' and len(correct)!=1):
            raise StoreError('Invalid package answer key.')
        if (not isinstance(rec.get('original_hash'),str) or type(rec.get('original_version')) is not int
                or rec['original_version']<1 or not isinstance(rec.get('explanation'),str) or not rec['explanation'].strip()):
            raise StoreError('Invalid package original identity/explanation.')
        if bank is not None:
            orig=bank.get(qid)
            deferred=orig.get('metadata',{}).get('generation_status')=='DEFERRED_CONCEPTUAL'
            if item['status'] != ('ORIGINAL_ONLY' if deferred else 'VARIANT') or rec.get('classification')!=orig.get('classification'):
                raise StoreError('Package classification/status differs from catalog.')
            if deferred and (rec!=original_record(orig) or item.get('reason')!=orig['metadata']['reason']):
                raise StoreError('Pinned original-only snapshot is missing or changed.')
        if item['status']=='VARIANT':
            ver=rec.get('variant_ver')
            if (type(rec.get('config_ver')) is not int or rec['config_ver']<1
                    or not isinstance(rec.get('config_hash'),str) or len(rec['config_hash'])!=16
                    or not isinstance(rec.get('values_used'),dict) or type(rec.get('draws_used')) is not int or rec['draws_used']<1
                    or rec.get('cognitive_level') not in ('C1','C2','C3','C4','C5','C6')):
                raise StoreError('Invalid pinned config provenance.')
            if (type(rec.get('seed')) is not int or rec['seed']!=manifest['seed'] or type(ver) is not int or ver<1
                    or rec.get('record_id')!=f"{qid}:s{manifest['seed']}:v{ver}"):
                raise StoreError('Invalid pinned variant identity.')
        elif type(rec.get('seed')) is not int or rec['seed']!=0 or not isinstance(item.get('reason'),str) or not item['reason']:
            raise StoreError('Original-only item needs seed 0 and a reason.')
    return manifest


def generate_package(bank, configs, package_id, seed):
    from cli import preview
    if not isinstance(package_id, str) or type(seed) is not int or not 1 <= seed <= 1_000_000_000:
        raise ValueError('Package ID and positive integer seed required.')
    groups = [g for g in bank.catalog() if g['activity'] == 'TRYOUT' and g['package_id'] == package_id]
    if not groups:
        raise StoreError('Tryout package not found.')
    items = []
    for group in sorted(groups, key=lambda g: g['chapter']):
        for qid in group['question_ids']:
            orig = bank.get(qid)
            if orig.get('metadata', {}).get('generation_status') == 'DEFERRED_CONCEPTUAL':
                items.append(dict(question_id=qid, status='ORIGINAL_ONLY', record=original_record(orig),
                                  reason=orig['metadata']['reason']))
            else:
                items.append(dict(question_id=qid, status='VARIANT', record=preview(bank, configs, qid, seed)))
    return validate_manifest(dict(schema_version=1, status='LOCAL_PREVIEW', package_id=package_id,
                                  seed=seed, items=items), bank)


def export_package(manifest, bank=None):
    """A local preview, deliberately without invented Numora canonical IDs."""
    if bank is None:
        from bank import load_workspace_bank
        bank=load_workspace_bank(Path(__file__).resolve().parent/'data/q0_bank.csv')
    validate_manifest(manifest,bank)
    return manifest
