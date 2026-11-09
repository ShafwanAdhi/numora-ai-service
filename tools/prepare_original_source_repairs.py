"""Prepare guarded local repair proposals. Database/storage access is read-only."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from numora_service.bridge import workspace
from numora_service.mapping_audit import SQL, NAMESPACES, compare, source_projection


def checked_asset(original, asset, receipt, root=ROOT):
    """Bind local bytes, current original and receipt; never accept a signed URL."""
    for field in ('externalId', 'assetId', 'byteLength', 'sha256', 'contentType',
                  'contentVersion', 'sourceOriginalHash'):
        if receipt.get(field) != asset.get(field):
            raise ValueError('RECEIPT_PIN_MISMATCH')
    if (asset['externalId'], asset['sourceOriginalHash'], asset['sourceOriginalVersion']) != (
            original['id'], original['hash'], original['version']):
        raise ValueError('SOURCE_PIN_MISMATCH')
    if receipt['status'] != 'VERIFIED':
        raise ValueError('RECEIPT_NOT_VERIFIED')
    file = (root / asset['filePath']).resolve()
    if not file.is_relative_to(root.resolve()):
        raise ValueError('ASSET_PATH_INVALID')
    data = file.read_bytes()
    if (hashlib.sha256(data).hexdigest() != asset['sha256'] or len(data) != asset['byteLength']
            or data[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', data[16:24]) != (960, 640)):
        raise ValueError('LOCAL_IMAGE_MISMATCH')
    result = {k: receipt[k] for k in ('externalId', 'assetId', 'bucket', 'objectKey',
              'contentType', 'byteLength', 'sha256')}
    return {**result, 'placement': 'STEM', 'altText': asset['altText']}


def main():
    from dotenv import load_dotenv
    import psycopg
    from psycopg.rows import dict_row
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify-storage', action='store_true')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env')
    bank, configs = workspace()
    upload = ROOT / 'docs/audits/2026-10-27-drill-r2-upload'
    preflight = json.loads((upload / 'preflight.json').read_text(encoding='utf-8'))
    receipts = json.loads((upload / 'media-receipts.json').read_text(encoding='utf-8'))
    explanations = {qid for qid in bank.ids()
                    if bank.get(qid).get('metadata', {}).get('original_explanation_provenance')}
    media_ids = {a['externalId'] for a in preflight['assets']}
    proposals, media = [], []
    with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=8, row_factory=dict_row) as db:
        db.read_only = True
        db.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
        db.execute("SET LOCAL statement_timeout='15s'")
        assert db.execute('SHOW transaction_read_only').fetchone()['transaction_read_only'] == 'on'
        rows = db.execute(SQL, (list(NAMESPACES),)).fetchall()
        for qid in sorted(explanations | media_ids):
            matches = [r for r in rows if r['external_id'] == qid]
            if len(matches) != 1:
                raise ValueError('MAPPING_MISSING_OR_AMBIGUOUS')
            row = matches[0]
            original = bank.get(qid)
            expected, origin = source_projection(original, configs)
            audit = compare(original, row, expected, origin)
            if not audit['identityValid'] or set(audit['problems']) - {'EXPLANATION_MISMATCH'}:
                raise ValueError('CANONICAL_SOURCE_MISMATCH')
            item = {'questionExternalId': qid, 'parentQuestionVersionId': row['id'],
                    'expectedSourceFingerprint': audit['sourceFingerprint'],
                    'originalHash': original['hash'], 'originalVersion': original['version'],
                    'patch': {}, 'comparison': 'EXACT', 'localSimulation': False}
            simulated = deepcopy(row)
            if qid in explanations:
                item['localExplanation'] = expected['explanation']
                item['canonicalExplanation'] = row['explanation']
                if row['explanation'] != expected['explanation']:
                    # Exact reviewed representation equivalences, never a broad text normalizer.
                    canonical = row['explanation']['text']
                    local = expected['explanation']['text']
                    if qid == 'kategori-17-3-10' and canonical == local.replace('k^(2)', '(k)^(2)').replace('3^(2)', '(3)^(2)'):
                        item['comparison'] = 'EQUIVALENT_EXPONENT_PARENTHESES'
                        expected['explanation'] = row['explanation']
                    elif qid == 'pg-17-3-2' and canonical == "Refleksi sumbu X: B(x,y) menjadi B′(x,-y).\nRefleksi sumbu Y: B′(x,-y) menjadi B″(-x,-y).\nHasil akhir (-x,-y) sama dengan rotasi 180° terhadap titik pusat (0,0).":
                        item['comparison'] = 'EQUIVALENT_CANONICAL_ALREADY_CORRECTED'
                        expected['explanation'] = row['explanation']
                    elif qid == 'mcma-16-1-6' and local.startswith(canonical + '\nPernyataan 4:'):
                        item['comparison'] = 'ADD_MISSING_STATEMENT_4'
                        item['patch']['explanation'] = expected['explanation']
                        simulated['explanation'] = expected['explanation']
                    else:
                        raise ValueError('UNREVIEWED_EXPLANATION_DIFFERENCE')
            if qid in media_ids:
                asset = next(a for a in preflight['assets'] if a['externalId'] == qid)
                receipt = receipts[qid]
                linked = checked_asset(original, asset, receipt)
                live = db.execute('SELECT status,sha256,byte_length,bucket,object_key,external_id,asset_id FROM public.content_media_uploads WHERE id=%s', (receipt['uploadId'],)).fetchone()
                if not live or any(live[k] != receipt[v] for k, v in (
                        ('status','status'),('sha256','sha256'),('byte_length','byteLength'),
                        ('bucket','bucket'),('object_key','objectKey'),('external_id','externalId'),('asset_id','assetId'))):
                    raise ValueError('LIVE_RECEIPT_MISMATCH')
                if row['media'] not in (None, {}, [], {'assets': []}):
                    raise ValueError('EXISTING_MEDIA_REQUIRES_REVIEW')
                item['patch']['media'] = [linked]
                item['patch']['stem'] = {'text': '[[asset:' + linked['assetId'] + ']]\n\n' + row['stem']['text'], 'assetKeys': [linked['assetId']]}
                simulated.update(item['patch'])
                media.append(linked)
            result = compare(original, simulated, expected, origin)
            if result['problems'] or not result['contentMatches'] or 'ORIGINAL_MEDIA_NOT_LINKED' in result['blockers']:
                raise ValueError('LOCAL_SIMULATION_FAILED: ' + qid + ': ' + ','.join(result['problems']))
            item['localSimulation'] = True
            proposals.append(item)
    verification = None
    if args.verify_storage:
        main_repo = ROOT.parent / 'Numora'
        result = subprocess.run(['node', str(main_repo / 'scripts/audit-original-media.mjs')],
            input=json.dumps(media), capture_output=True, text=True, cwd=main_repo, timeout=180)
        if result.returncode:
            raise ValueError('STORAGE_VERIFIER_FAILED')
        verification = json.loads(result.stdout)
        if verification['verified'] != len(media):
            raise ValueError('STORAGE_BYTES_UNVERIFIED')
    report = {'kind': 'LOCAL_ORIGINAL_REPAIR_PROPOSAL', 'readOnly': True, 'appliedToDatabase': False,
              'curriculumApprovalAdded': False, 'items': proposals, 'storageVerification': verification,
              'summary': {'explanationsRecovered': len(explanations), 'imageLinksPrepared': len(media),
                          'localSimulationsPassed': len(proposals),
                          'explanationUpdatesNeeded': sum('explanation' in p['patch'] for p in proposals)}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report['summary']))


if __name__ == '__main__':
    main()
