"""Read-only original reconciliation. Never registers, imports, approves or repairs data."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from .bridge import ROOT, workspace, original_record
from .content import fingerprint, TYPES

NAMESPACES = ('NUMORA_AI_DRILL_1', 'NUMORA_AI_TRYOUT_1')
VERSION = 'original-mapping-audit-v1'


def media_assets(value):
    if value in (None, {}, []):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and isinstance(value.get('assets'), list):
        return value['assets']
    raise ValueError('MEDIA_SHAPE_INVALID')


def text(value):
    if not isinstance(value, dict) or not isinstance(value.get('text'), str):
        raise ValueError('TEXT_SHAPE_INVALID')
    return value['text'].replace('\r\n', '\n')


def source_projection(original, configs):
    """Use local explanations or reproduce original values; never copy DB text as truth."""
    record = original_record(original)
    correct = record['key'].split(',') if record['key'] else []
    labels = original.get('metadata', {}).get('category_labels', ['Benar', 'Salah'])
    categories = [{'id': 'category_1', 'label': labels[0]}, {'id': 'category_2', 'label': labels[1]}] if original['format'] == 'KATEGORI' else []
    answer = ({'optionId': correct[0]} if original['format'] == 'PG' else {'optionIds': correct}
              if original['format'] == 'MCMA' else {'categoryByStatementId': {
                  o['id']: categories[0 if o['id'] in correct else 1]['id'] for o in record['options']}})
    content = dict(questionType=TYPES[original['format']], stem={'text': record['stem'].replace('\r\n', '\n')},
        optionsOrStatements={'options': [{'id': o['id'], 'content': {'text': o['text'].replace('\r\n', '\n')}}
                                        for o in record['options']], 'categories': categories}, answerKey=answer)
    metadata = original.get('metadata', {})
    explanation = metadata.get('original_explanation') or metadata.get('explanation')
    origin = 'LOCAL_METADATA' if explanation else None
    if not explanation and configs.versions(original['id']):
        from engine import assemble, build_values, key_of
        from expr import to_num
        cfg, _ = configs.load(original['id'])
        if cfg['original_hash'] != original['hash']:
            raise ValueError('CONFIG_SOURCE_STALE')
        raw = {k: to_num(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
               for k, v in cfg['original_values'].items()}
        result = assemble(cfg, build_values(cfg, lambda name, spec: raw[name], check=False))
        if key_of(result) != original_record(original)['key']:
            raise ValueError('ORIGINAL_REPRODUCTION_KEY_MISMATCH')
        explanation = result['explanation']
        origin = 'CONFIG_ORIGINAL_VALUES'
    content['explanation'] = {'text': explanation.replace('\r\n', '\n')} if explanation else None
    return content, origin


def compare(original, row, expected, explanation_origin=None):
    problems, blockers = [], []
    def require(condition, code):
        if not condition:
            problems.append(code)
    require(row['kind'] == 'ORIGINAL', 'NOT_ORIGINAL')
    require(row['original_hash'] == original['hash'], 'ORIGINAL_HASH_MISMATCH')
    require(str(row['original_version']) == str(original['version']), 'ORIGINAL_VERSION_MISMATCH')
    cls = original['classification']
    require(row['usage_type'] == cls['activity'], 'USAGE_MISMATCH')
    require(row['question_type'] == expected['questionType'], 'QUESTION_TYPE_MISMATCH')
    assets = media_assets(row['media'])
    canonical_stem = text(row['stem'])
    # Imported image markers are a presentation addition, not silently ignored text.
    markers = re.findall(r'\[\[asset:([^\]]+)\]\]', canonical_stem)
    asset_ids = {a.get('assetId') for a in assets if a.get('placement') == 'STEM'}
    require(set(markers) <= asset_ids, 'MEDIA_MARKER_UNRESOLVED')
    plain_stem = re.sub(r'\[\[asset:[^\]]+\]\]\s*', '', canonical_stem)
    require(plain_stem == expected['stem']['text'], 'STEM_MISMATCH')
    collection = row['options_or_statements']
    collection = {'options': collection, 'categories': []} if isinstance(collection, list) else collection
    options = [{'id': o['id'], 'content': {'text': text(o['content'])}} for o in collection['options']]
    require(options == expected['optionsOrStatements']['options'], 'OPTIONS_MISMATCH')
    cats = collection.get('categories', [])
    answer = row['answer_key']
    if original['format'] == 'KATEGORI':
        labels = {c['label']: c['id'] for c in cats}
        local_cats = expected['optionsOrStatements']['categories']
        require(set(labels) == {c['label'] for c in local_cats}, 'CATEGORY_LABEL_MISMATCH')
        ids = {c['id']: c['label'] for c in cats}
        local_ids = {c['id']: c['label'] for c in local_cats}
        actual = {k: ids.get(v) for k, v in answer.get('categoryByStatementId', {}).items()}
        local = {k: local_ids[v] for k, v in expected['answerKey']['categoryByStatementId'].items()}
        require(actual == local, 'ANSWER_MISMATCH')
    elif original['format'] == 'MCMA':
        require(set(answer.get('optionIds', [])) == set(expected['answerKey']['optionIds']), 'ANSWER_MISMATCH')
    else:
        require(answer == expected['answerKey'], 'ANSWER_MISMATCH')
    if expected['explanation'] is None:
        blockers.append('LOCAL_EXPLANATION_UNAVAILABLE')
    else:
        require(text(row['explanation']) == expected['explanation']['text'], 'EXPLANATION_MISMATCH')
    chapter = cls.get('chapter') or (1 if cls['indicator'] <= 6 else 2 if cls['indicator'] <= 13
                                   else 3 if cls['indicator'] <= 19 else 4)
    require(row['chapter_code'] == {1: 'CH-BIL', 2: 'CH-ALG', 3: 'CH-GP', 4: 'CH-DP'}[chapter], 'CHAPTER_MISMATCH')
    if cls['activity'] == 'DRILL':
        require(row['competency_code'] == f"IND-{cls['indicator']:03d}", 'INDICATOR_MISMATCH')
        require(row['curriculum_level_number'] == cls['source_level'] == row['level_number'], 'LEVEL_MISMATCH')
    maximum = 1 if original['format'] == 'PG' else len(original['options'])
    require(row['rubric_question_type'] == row['question_type'] and
            row['maximum_score_category'] == maximum, 'RUBRIC_SHAPE_MISMATCH')
    if row['rubric_status'] != 'SEALED':
        blockers.append('RUBRIC_NOT_SEALED')
    if row['content_status'] != 'READY' or row['validation_state'] != 'CONTENT_VALID':
        blockers.append('CONTENT_NOT_APPROVED_FOR_DELIVERY')
    if not row['contexts']:
        blockers.append('CONTEXT_NOT_REGISTERED')
    if not row['config_ids']:
        blockers.append('GENERATOR_NOT_REGISTERED')
    if not row['approval_ids']:
        blockers.append('GENERATOR_APPROVAL_MISSING')
    if original['id'] in IMAGE_IDS and not assets:
        blockers.append('ORIGINAL_MEDIA_NOT_LINKED')
    identity_errors = {'NOT_ORIGINAL', 'ORIGINAL_HASH_MISMATCH', 'ORIGINAL_VERSION_MISMATCH', 'USAGE_MISMATCH'}
    return dict(questionExternalId=original['id'], activity=cls['activity'], classification=cls,
                familyId=row['family_id'], parentQuestionVersionId=row['id'],
                canonicalVersion=row['version_number'], originalVersion=original['version'],
                originalHash=original['hash'], rubricVersionId=row['scoring_rubric_version_id'],
                rubricDigest=row['rubric_digest'], rubricStatus=row['rubric_status'],
                sourceFingerprint=fingerprint({'questionType': row['question_type'], 'stem': row['stem'],
                    'optionsOrStatements': row['options_or_statements'], 'answerKey': row['answer_key'],
                    'explanation': row['explanation'], 'media': assets}),
                canonicalContentFingerprint=row['content_fingerprint'],
                importContentHash=row['import_content_hash'], explanationOrigin=explanation_origin,
                contextIds=row['contexts'], generatorConfigIds=row['config_ids'],
                generatorApprovalIds=row['approval_ids'], mediaCount=len(assets),
                media=assets, identityValid=not identity_errors.intersection(problems),
                contentMatches=not problems and expected['explanation'] is not None, registrationReady=not problems and
                    not set(blockers).intersection({'LOCAL_EXPLANATION_UNAVAILABLE','RUBRIC_NOT_SEALED',
                        'CONTEXT_NOT_REGISTERED','ORIGINAL_MEDIA_NOT_LINKED'}),
                problems=problems, blockers=blockers)


IMAGE_IDS = frozenset(('pg-16-4-1','pg-16-4-2','pg-16-4-3','pg-16-4-4','mcma-16-4-6',
    'mcma-16-4-7','pg-16-5-1','pg-16-5-3','pg-16-5-5','tryout-1-b3-q02','tryout-1-b3-q03',
    'tryout-1-b3-q04','tryout-1-b3-q06','tryout-1-b4-q05'))

SQL = """
SELECT i.external_id,i.source_namespace,v.id::text,v.version_number,a.kind,
 i.question_id::text family_id,q.usage_type,q.curriculum_level_number,
 c.code competency_code,ch.code chapter_code,l.level_number,v.level_id::text,
 v.question_type,v.stem,v.options_or_statements,v.answer_key,v.explanation,v.media,
 v.content_fingerprint,v.content_status,v.validation_state,v.scoring_rubric_version_id::text,
 r.question_type rubric_question_type,r.maximum_score_category,r.status rubric_status,r.digest rubric_digest,
 iv.content_hash import_content_hash,iv.provenance->>'originalHash' original_hash,
 iv.provenance->>'originalVersion' original_version,
 ARRAY(SELECT ctx.id::text FROM public.measurement_contexts ctx WHERE
   (q.usage_type='DRILL' AND ctx.ecosystem='DRILL' AND ctx.level_id=v.level_id)
   OR (q.usage_type='TRYOUT' AND ctx.ecosystem='TRYOUT' AND EXISTS
     (SELECT 1 FROM public.tryout_batches b JOIN public.package_items pi ON pi.package_id=b.package_id
      WHERE b.id=ctx.tryout_batch_id AND pi.question_version_id=v.id))) contexts,
 ARRAY(SELECT g.id::text FROM irt_compute.generator_configs g
   WHERE g.parameters->>'parentQuestionVersionId'=v.id::text) config_ids,
 ARRAY(SELECT ap.id::text FROM public.configuration_approvals ap JOIN irt_compute.generator_configs g
   ON g.id=ap.generator_config_id WHERE g.parameters->>'parentQuestionVersionId'=v.id::text
   AND ap.revoked_at IS NULL AND ap.approved_digest=g.digest
   AND ap.scope->>'contextId'=g.context_id::text) approval_ids
FROM public.content_import_identities i JOIN public.questions q ON q.id=i.question_id
JOIN public.question_variants a ON a.question_id=q.id AND a.kind='ORIGINAL'
JOIN public.question_versions v ON v.variant_id=a.id
LEFT JOIN public.content_import_versions iv ON iv.question_version_id=v.id
LEFT JOIN public.scoring_rubric_versions r ON r.id=v.scoring_rubric_version_id
LEFT JOIN public.competencies c ON c.id=q.primary_competency_id
LEFT JOIN public.chapters ch ON ch.id=q.chapter_id
LEFT JOIN public.levels l ON l.id=v.level_id
WHERE i.source_namespace=ANY(%s) ORDER BY i.external_id,v.version_number
"""


def audit(url, bank, configs):
    with psycopg.connect(url, connect_timeout=8, prepare_threshold=None, row_factory=dict_row) as db:
        db.read_only = True
        db.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
        db.execute("SET LOCAL statement_timeout='15s'")
        if db.execute('SHOW transaction_read_only').fetchone()['transaction_read_only'] != 'on':
            raise ValueError('READ_ONLY_REQUIRED')
        rows = db.execute(SQL, (list(NAMESPACES),)).fetchall()
        receipts = db.execute("SELECT external_id,asset_id,bucket,object_key,sha256,byte_length,status FROM public.content_media_uploads WHERE status='VERIFIED'").fetchall()
        groups = {}
        for row in rows:
            groups.setdefault(row['external_id'], []).append(row)
        output = []
        for qid in sorted(bank.ids()):
            original = bank.get(qid)
            matches = groups.get(qid, [])
            if len(matches) != 1:
                output.append(dict(questionExternalId=qid, identityValid=False, contentMatches=False,
                    registrationReady=False, problems=['MAPPING_MISSING' if not matches else 'MAPPING_AMBIGUOUS'], blockers=[]))
                continue
            try:
                projection, origin = source_projection(original, configs)
                item = compare(original, matches[0], projection, origin)
                for asset in item['media']:
                    if not any(all(r.get(k) == asset.get(j) for k,j in
                        [('external_id','externalId'),('asset_id','assetId'),('bucket','bucket'),
                         ('object_key','objectKey'),('sha256','sha256'),('byte_length','byteLength')]) for r in receipts):
                        item['problems'].append('MEDIA_RECEIPT_MISMATCH')
                        item['contentMatches'] = item['registrationReady'] = False
                output.append(item)
            except (ValueError, KeyError, TypeError) as error:
                output.append(dict(questionExternalId=qid, identityValid=False, contentMatches=False,
                    registrationReady=False, problems=['LOCAL_PROJECTION_OR_CANONICAL_SHAPE_INVALID'], blockers=[],
                    diagnostic=type(error).__name__))
        return dict(contractVersion=VERSION, readOnly=True, rows=output,
            summary=dict(originals=len(output), identityValid=sum(i['identityValid'] for i in output),
                contentMatches=sum(i['contentMatches'] for i in output),
                registrationReady=sum(i['registrationReady'] for i in output),
                problems=dict(Counter(p for i in output for p in i['problems'])),
                blockers=dict(Counter(p for i in output for p in i['blockers']))))


def main():
    import os
    from dotenv import load_dotenv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify-media', action='store_true', help='Read linked media bytes using the main storage adapter')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env', override=False)
    bank, configs = workspace()
    result = audit(os.environ['DATABASE_URL'], bank, configs)
    if args.verify_media:
        import subprocess
        main_repo = Path(os.environ.get('NUMORA_REPO_PATH', str(ROOT.parent / 'Numora')))
        assets = [a for row in result['rows'] for a in row.get('media', [])]
        completed = subprocess.run(['node', str(main_repo / 'scripts/audit-original-media.mjs')],
            input=json.dumps(assets), text=True, capture_output=True, cwd=main_repo, timeout=120)
        if completed.returncode:
            raise SystemExit('Media verifier failed; no database writes were performed')
        result['mediaVerification'] = json.loads(completed.stdout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
