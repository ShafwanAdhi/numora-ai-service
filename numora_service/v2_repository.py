from psycopg.types.json import Jsonb

from .bridge import original_record, config_hash, validate_config, ConfigStore, ENGINE_ROOT
from .content import fingerprint, record_content, source_content, uuid
from .errors import ServiceError
from .repository import Repository
from .v2_content import normalized_source, source_fingerprint, validate_payload, local_record
from .v2_generate import media_profile, stock_manifest, stocks


class RepositoryV2(Repository):
    service_contract = 'generator-service-v2'
    validate_result = staticmethod(validate_payload)

    def task_work(self, db, task):
        r,w,g,s,a,rubric,c = (task[k] for k in ['request','wave','config','source','approval','rubric','context'])
        p, constraints = g['parameters'], w['constraints']
        required={'serviceContract','questionExternalId','mode','parentQuestionVersionId','familyId','rubricVersionId','contextId','mediaProfile','originalVersion','originalHash','sourceFingerprint'}
        required |= {'configVersion','configHash','config'} if p.get('mode')=='NUMERIC' else {'stockSetId','stockSetDigest'}
        if set(p)!=required:
            raise ServiceError('INVALID_CONFIG_MAPPING',422)
        if (r['request_type']!='GENERATE_VARIANTS' or r['snapshot_id'] is not None or w['target_count']!=1 or
            w['wave_status'] not in ('APPROVED','RUNNING') or g['status']!='SEALED' or
            str(w['context_id'])!=str(r['context_id']) or str(g['context_id'])!=str(r['context_id']) or
            str(w['original_question_version_id'])!=str(s['id']) or str(w['generator_config_id'])!=str(g['id'])):
            raise ServiceError('UNAUTHORIZED_V2_WAVE')
        if (a['revoked_at'] is not None or str(a['generator_config_id'])!=str(g['id']) or
            a['approved_digest']!=g['digest'] or a['scope'].get('contextId')!=str(r['context_id']) or
            a['scope'].get('ecosystem')!=c['ecosystem'] or
            r['configuration_pins'] != [{'approvalId':str(a['id']),'digest':g['digest']}]):
            raise ServiceError('CONFIG_APPROVAL_MISMATCH')
        if (rubric['status']!='SEALED' or rubric['question_type']!=s['question_type'] or
            str(rubric['id'])!=str(s['scoring_rubric_version_id'])):
            raise ServiceError('RUBRIC_MISMATCH')
        if s['content_status']!='READY' or s['validation_state']!='CONTENT_VALID':
            raise ServiceError('SOURCE_NOT_ELIGIBLE')
        original=self.bank.get(p['questionExternalId'])
        if (original['classification']['activity']!=c['ecosystem'] or
            (c['ecosystem']=='DRILL' and (s['level_id'] is None or str(s['level_id'])!=str(c['level_id']))) or
            (c['ecosystem']=='TRYOUT' and c['tryout_batch_id'] is None)):
            raise ServiceError('SOURCE_CONTEXT_SCOPE_MISMATCH')
        canonical=source_content(normalized_source(s))
        if (p['serviceContract']!=self.service_contract or constraints.get('serviceContract')!=self.service_contract or
            p['originalHash']!=original['hash'] or p['originalVersion']!=original['version'] or s['kind']!='ORIGINAL' or
            p['parentQuestionVersionId']!=str(s['id']) or p['familyId']!=str(s['family_id']) or
            p['rubricVersionId']!=str(rubric['id']) or p['contextId']!=str(c['id']) or
            p['sourceFingerprint']!=source_fingerprint(s) or
            canonical!=record_content(local_record(original_record(original)),canonical['optionsOrStatements']['categories'] or None)):
            raise ServiceError('SOURCE_MAPPING_MISMATCH')
        if p['mediaProfile']!=media_profile(original['id']):
            raise ServiceError('RENDERER_TEMPLATE_PIN_MISMATCH')
        work={'serviceContract':self.service_contract,'original':original,'source':s,
              'mediaProfile':p['mediaProfile'],'mode':p['mode']}
        if p['mode']=='NUMERIC':
            # JSONB object order is not an execution order. Reconcile the exact
            # pinned local version, then retain its reviewed variable ordering.
            cfg, local_hash=ConfigStore(ENGINE_ROOT/'configs').load(original['id'],p['configVersion'])
            if cfg!=p['config'] or local_hash!=p['configHash']:
                raise ServiceError('NUMERIC_CONFIG_HASH_MISMATCH')
            if set(constraints)!={'serviceContract','seed'} or type(constraints['seed']) is not int or not 1<=constraints['seed']<=1_000_000_000:
                raise ServiceError('INVALID_NUMERIC_CONSTRAINTS')
            if config_hash(cfg)!=p['configHash']:
                raise ServiceError('NUMERIC_CONFIG_HASH_MISMATCH')
            if cfg['config_version']!=p['configVersion'] or validate_config(cfg,original):
                raise ServiceError('CONFIG_PIN_MISMATCH')
            work.update(config=cfg,seed=constraints['seed'])
        elif p['mode']=='CONCEPTUAL_STOCK':
            if set(constraints)!={'serviceContract','stockReservationId'}:
                raise ServiceError('INVALID_STOCK_CONSTRAINTS')
            reservation=self.one(db,'SELECT * FROM public.irt_input_stock_reservations_v2 WHERE id=%s',(uuid(constraints['stockReservationId']),))
            inventory=self.one(db,'SELECT * FROM public.irt_input_stock_sets_v2 WHERE id=%s',(reservation['stock_set_id'],))
            local=stocks(self.bank).get(original['id'],[])
            if (str(reservation['wave_item_id'])!=str(w['id']) or str(inventory['id'])!=p['stockSetId'] or
                inventory['digest']!=p['stockSetDigest'] or inventory['definition']!=stock_manifest(local) or
                str(inventory['original_question_version_id'])!=str(s['id']) or
                str(inventory['family_id'])!=str(s['family_id'])):
                raise ServiceError('STOCK_PIN_MISMATCH')
            selected=[v for v in local if v['variant_id']==reservation['stock_variant_id']]
            if len(selected)!=1:raise ServiceError('STOCK_PIN_MISMATCH')
            task['stockInventory']=inventory;task['stockReservation']=reservation
            work.update(stockItem=selected[0],stockSetId=p['stockSetId'],stockSetDigest=p['stockSetDigest'],
                        reservation={**reservation,'id':str(reservation['id'])})
        else:raise ServiceError('INVALID_GENERATOR_MODE')
        return work

    def insert_candidate(self,db,task,claim,result):
        execution=claim['execution']; work=claim['work']
        # Binary bytes and candidate are sealed in the same transaction. No partial artifact commit.
        assets=result.get('mediaArtifacts',[])
        if len(assets)!=len(result['payload']['media']):raise ServiceError('MEDIA_ARTIFACT_MISMATCH')
        for artifact,descriptor in zip(assets,result['payload']['media']):
            import hashlib
            if (hashlib.sha256(artifact['pngBytes']).hexdigest()!=descriptor['sha256'] or
                len(artifact['pngBytes'])!=descriptor['byteLength'] or
                artifact['width']!=descriptor['width'] or artifact['height']!=descriptor['height'] or
                fingerprint(artifact['provenance'])!=descriptor['provenanceDigest']):
                raise ServiceError('MEDIA_ARTIFACT_MISMATCH')
            db.execute('''INSERT INTO irt_compute.generator_media_artifacts
             (execution_id,sha256,png_bytes,byte_length,width,height,provenance) VALUES(%s,%s,%s,%s,%s,%s,%s)''',
             (execution['id'],artifact['sha256'],artifact['pngBytes'],artifact['byteLength'],artifact['width'],artifact['height'],Jsonb(artifact['provenance'])))
        seed=str(work['seed']) if work['mode']=='NUMERIC' else None
        reservation=work['reservation']['id'] if work['mode']=='CONCEPTUAL_STOCK' else None
        run=self.one(db,'''INSERT INTO irt_compute.generation_runs
         (config_id,original_question_version_id,wave_item_id,execution_id,generator_version,random_seed,parameter_values,status,generation_mode,stock_reservation_id)
         VALUES(%s,%s,%s,%s,'numora-generator-service/2',%s,%s,'RUNNING',%s,%s) RETURNING id''',
         (task['config']['id'],task['source']['id'],task['wave']['id'],execution['id'],seed,Jsonb(result['provenance']),work['mode'],reservation))
        candidate=self.one(db,'''INSERT INTO irt_compute.generation_candidates
         (generation_run_id,parent_original_question_version_id,payload,random_seed,parameter_values,validation_status)
         VALUES(%s,%s,%s,%s,%s,'CONTENT_VALID') RETURNING id,payload_digest''',
         (run['id'],task['source']['id'],Jsonb(result['payload']),seed,Jsonb(result['provenance'])))
        return run,candidate
