"""Technical registration only. Dry-run by default; never creates content approvals."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb
from .bridge import config_hash, original_record, validate_config
from .content import fingerprint, record_content, source_content, uuid
from .errors import ServiceError
from .v2_content import normalized_source, source_fingerprint, local_record
from .v2_generate import media_profile, stock_manifest, stocks


def register(repository,bank,configs,manifest,apply=False,seal=False):
    schema=json.loads((Path(__file__).resolve().parents[1]/'contracts/generator-service-v2/registration.schema.json').read_text())
    if next(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(manifest),None):
        raise ServiceError('INVALID_V2_REGISTRATION',422)
    if seal and not apply:raise ServiceError('SEAL_REQUIRES_APPLY',422)
    output=[];seen=set()
    with repository.connection() as db:
        repository.check_role(db)
        for item in manifest['items']:
            original=bank.get(item['questionExternalId'])
            source=repository.one(db,'SELECT * FROM public.irt_input_content_v3 WHERE id=%s',(uuid(item['parentQuestionVersionId']),))
            rubric=repository.one(db,'SELECT * FROM public.irt_input_rubrics_v3 WHERE id=%s',(uuid(item['rubricVersionId']),))
            context=repository.one(db,'SELECT * FROM public.irt_input_contexts_v3 WHERE id=%s',(uuid(item['contextId']),))
            if (original['classification']['activity']!=context['ecosystem'] or
                (context['ecosystem']=='DRILL' and (source['level_id'] is None or str(source['level_id'])!=str(context['level_id']))) or
                (context['ecosystem']=='TRYOUT' and context['tryout_batch_id'] is None)):
                raise ServiceError('SOURCE_CONTEXT_SCOPE_MISMATCH')
            canonical=source_content(normalized_source(source))
            if (source['kind']!='ORIGINAL' or str(source['family_id'])!=item['familyId'] or
                str(source['scoring_rubric_version_id'])!=item['rubricVersionId'] or
                source['content_status']!='READY' or source['validation_state']!='CONTENT_VALID' or
                rubric['status']!='SEALED' or rubric['question_type']!=source['question_type'] or
                context['ecosystem'] not in ['DRILL','TRYOUT'] or
                canonical!=record_content(local_record(original_record(original)),canonical['optionsOrStatements']['categories'] or None)):
                raise ServiceError('SOURCE_MAPPING_MISMATCH')
            if item['mediaProfile']!=media_profile(original['id']):raise ServiceError('RENDERER_TEMPLATE_PIN_MISMATCH')
            parameters={'serviceContract':'generator-service-v2',**item,'originalVersion':original['version'],
                        'originalHash':original['hash'],'sourceFingerprint':source_fingerprint(source)}
            if item['mode']=='NUMERIC':
                cfg,digest=configs.load(original['id'],item['configVersion'])
                if validate_config(cfg,original):raise ServiceError('CONFIG_PIN_MISMATCH')
                parameters.update(config=cfg,configHash=digest)
                version=item['configVersion']
            else:
                stock=repository.one(db,'SELECT * FROM public.irt_input_stock_sets_v2 WHERE id=%s',(uuid(item['stockSetId']),))
                local=stocks(bank).get(original['id'],[])
                if (str(stock['family_id'])!=item['familyId'] or str(stock['original_question_version_id'])!=item['parentQuestionVersionId'] or
                    stock['definition']!=stock_manifest(local) or not local):raise ServiceError('STOCK_PIN_MISMATCH')
                parameters['stockSetDigest']=stock['digest'];version=stock['version']
            identity='generator-v2-'+fingerprint({k:parameters[k] for k in ['questionExternalId','parentQuestionVersionId','contextId','mode','familyId','rubricVersionId','mediaProfile']})
            key=(identity,version)
            if key in seen:raise ServiceError('DUPLICATE_REGISTRATION',422)
            seen.add(key)
            if apply:db.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,4))',(identity,))
            digest=repository.one(db,'SELECT irt_compute.payload_digest(%s) AS digest',(Jsonb(parameters),))['digest']
            existing=db.execute('SELECT * FROM irt_compute.generator_configs WHERE template_or_competency_id=%s AND config_version=%s',key).fetchone()
            if existing and (existing['parameters']!=parameters or existing['digest']!=digest or str(existing['context_id'])!=item['contextId']):
                raise ServiceError('REGISTRATION_CONFLICT')
            row=existing
            if apply and row is None:
                row=repository.one(db,"INSERT INTO irt_compute.generator_configs(template_or_competency_id,config_version,parameters,curriculum_limits,context_id,digest,status) VALUES(%s,%s,%s,'{}',%s,%s,'DRAFT') RETURNING *",(*key,Jsonb(parameters),item['contextId'],digest))
            if apply and seal and row['status']=='DRAFT':
                row=repository.one(db,"UPDATE irt_compute.generator_configs SET status='SEALED' WHERE id=%s RETURNING *",(row['id'],))
            output.append({'questionExternalId':original['id'],'mode':item['mode'],'generatorConfigId':str(row['id']) if row else None,
                           'digest':digest,'status':row['status'] if row else 'DRY_RUN','sourceFingerprint':parameters['sourceFingerprint']})
    return {'serviceContract':'generator-service-v2','applied':apply,'items':output}
