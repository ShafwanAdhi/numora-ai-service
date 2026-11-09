"""Research compute inbox/lease/artifacts; cannot write canonical business tables."""
from datetime import datetime,timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from ..repository import Repository as GeneratorRepository
from ..contracts import validate_notification
from ..irt_contracts import validate_input,validate_result
from .producer import policy


class Repository(GeneratorRepository):
    def __init__(self,settings):
        super().__init__(settings,None)

    def source(self,db,notification):
        validate_notification(notification)
        self.check_role(db)
        source=self.one(db,'SELECT * FROM public.irt_calibration_inputs_v1 WHERE id=%s',(notification['requestId'],))
        if source['input_digest']!=notification['inputDigest']:raise ValueError('INPUT_DIGEST_MISMATCH')
        if source['current_generation']!=notification['dispatchGeneration']:raise ValueError('STALE_DISPATCH')
        if source['cancelled'] or not source['approvals_valid']:raise ValueError('POLICY_UNAVAILABLE')
        value=source['payload'];validate_input(value)
        if value['ecosystem']!='TRYOUT' or value['comparisons']:raise ValueError('UNSUPPORTED_CONTRACT')
        profile=policy()
        expected={'model':('IRT_MODEL',profile['engine']),'quality':('QUALITY_GATE',profile['quality']),
            'eligibility':('IRT_ELIGIBILITY',{'version':profile['version'],'purpose':'RESEARCH_ONLY'}),
            'scoring':('IRT_SCORING',{'categoryPoints':'PROPORTIONAL_TO_MAXIMUM','purpose':'RESEARCH_ONLY'}),
            'scoreMapping':('SCORE_MAPPING',profile['mapping'])}
        if set(source['resources'])!=set(expected):raise ValueError('POLICY_UNAVAILABLE')
        for key,(kind,definition) in expected.items():
            resource=source['resources'][key]
            if resource['ref']!=value['policies'][key] or resource['kind']!=kind or resource['definition']!=definition:
                raise ValueError('POLICY_UNAVAILABLE')
        if source['runtime_profile'].get('purpose')!='RESEARCH_ONLY':raise ValueError('POLICY_UNAVAILABLE')
        return source

    @staticmethod
    def status(job,source,artifact=None):
        return {'serviceContract':'irt-calibration-service-v1','requestId':str(job['request_id']),
            'inputDigest':source['input_digest'],'dispatchGeneration':job['generation'],
            'executionId':str(job['execution_id']) if job['execution_id'] else None,'status':job['status'],
            'failureCode':job['failure_code'],'artifactId':str(artifact['id']) if artifact else None,
            'artifactDigest':artifact['digest'] if artifact else None}

    def accept(self,notification):
        with self.connection() as db:
            source=self.source(db,notification)
            db.execute('INSERT INTO irt_compute.calibration_jobs_v1(request_id,generation) VALUES(%s,%s) ON CONFLICT(request_id,generation) DO NOTHING',(notification['requestId'],notification['dispatchGeneration']))
            job=self.one(db,'SELECT * FROM irt_compute.calibration_jobs_v1 WHERE request_id=%s AND generation=%s',(notification['requestId'],notification['dispatchGeneration']))
            artifact=db.execute('SELECT id,digest FROM irt_compute.calibration_artifacts_v1 WHERE job_id=%s',(job['id'],)).fetchone()
            return self.status(job,source,artifact)

    def get(self,notification):
        with self.connection() as db:
            source=self.source(db,notification)
            job=self.one(db,'SELECT * FROM irt_compute.calibration_jobs_v1 WHERE request_id=%s AND generation=%s',(notification['requestId'],notification['dispatchGeneration']))
            artifact=db.execute('SELECT id,digest FROM irt_compute.calibration_artifacts_v1 WHERE job_id=%s',(job['id'],)).fetchone()
            return self.status(job,source,artifact)

    def claim_next(self):
        with self.connection() as db:
            self.check_role(db)
            # Serialize claim decisions across daemon processes; concurrency=1 is durable.
            if not db.execute('SELECT pg_try_advisory_xact_lock(20261109,1) AS locked').fetchone()['locked']:
                return None
            # Expired work never silently reruns the same generation.
            db.execute("UPDATE irt_compute.calibration_jobs_v1 SET status='EXPIRED',failure_code='LEASE_EXPIRED',finished_at=clock_timestamp() WHERE status='RUNNING' AND lease_expires_at<=clock_timestamp()")
            row=db.execute("SELECT j.*,s.input_digest FROM irt_compute.calibration_jobs_v1 j JOIN public.irt_calibration_inputs_v1 s ON s.id=j.request_id WHERE j.status='ACCEPTED' AND NOT EXISTS(SELECT 1 FROM irt_compute.calibration_jobs_v1 WHERE status='RUNNING') AND NOT s.cancelled AND s.approvals_valid AND j.generation=s.current_generation ORDER BY j.created_at,j.id FOR UPDATE OF j SKIP LOCKED LIMIT 1").fetchone()
            if not row:return None
            notification={'contractVersion':3,'requestId':str(row['request_id']),'inputDigest':row['input_digest'],'dispatchGeneration':row['generation']}
            source=self.source(db,notification)
            job=self.one(db,"UPDATE irt_compute.calibration_jobs_v1 SET status='RUNNING',execution_id=%s,lease_expires_at=clock_timestamp()+interval '60 seconds',heartbeat_at=clock_timestamp() WHERE id=%s RETURNING *",(uuid4(),row['id']))
            return job,source,notification

    def heartbeat(self,job,notification):
        with self.connection() as db:
            self.source(db,notification)
            row=db.execute("UPDATE irt_compute.calibration_jobs_v1 SET heartbeat_at=clock_timestamp(),lease_expires_at=clock_timestamp()+interval '60 seconds' WHERE id=%s AND execution_id=%s AND fencing_token=%s AND status='RUNNING' AND lease_expires_at>clock_timestamp() RETURNING id",(job['id'],job['execution_id'],job['fencing_token'])).fetchone()
            if not row:raise ValueError('STALE_EXECUTION')

    def persist(self,job,source,notification,result,diagnostics):
        validate_result(result,source['payload'],{'executionId':str(job['execution_id']),'dispatchGeneration':job['generation']})
        with self.connection() as db:
            current=self.source(db,notification)
            if current['payload']!=source['payload'] or current['resources']!=source['resources']:raise ValueError('INPUT_DIGEST_MISMATCH')
            db.execute('SELECT id FROM irt_compute.calibration_jobs_v1 WHERE id=%s FOR UPDATE',(job['id'],))
            artifact=self.one(db,"INSERT INTO irt_compute.calibration_artifacts_v1(job_id,payload,diagnostics,digest) VALUES(%s,%s,%s,'') RETURNING id,digest",(job['id'],Jsonb(result),Jsonb(diagnostics)))
            finished=self.one(db,"UPDATE irt_compute.calibration_jobs_v1 SET status=%s,failure_code=%s,finished_at=clock_timestamp() WHERE id=%s AND execution_id=%s AND fencing_token=%s AND status='RUNNING' AND lease_expires_at>clock_timestamp() RETURNING *",('SUCCEEDED' if result['executionStatus']=='SUCCEEDED' else 'FAILED',result['failure']['code'] if result['failure'] else None,job['id'],job['execution_id'],job['fencing_token']))
            return self.status(finished,source,artifact)
