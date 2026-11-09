"""Real isolated roles/guards/HTTP/daemon. Harness owns all database resources."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
import subprocess
from pathlib import Path
import unittest
from urllib.parse import urlparse,urlunparse
from uuid import uuid4
from unittest.mock import patch
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from fastapi.testclient import TestClient
from numora_service.settings import Settings
from numora_service.irt.api import create_app
from numora_service.irt.repository import Repository
from numora_service.irt.daemon import execute_once
from numora_service.irt.producer import policy

URL=os.environ.get('IRT_RESEARCH_LOCAL_URL')


@unittest.skipUnless(URL,'Use disposable main harness')
class IrtPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=urlparse(URL)
        assert p.hostname=='127.0.0.1' and p.path.startswith('/irt_research_test_')
        cls.urls={}
        with psycopg.connect(URL,row_factory=dict_row) as db:
            for role in ['main','compute']:
                login='irt_test_'+role+'_'+uuid4().hex
                db.execute(psycopg.sql.SQL('CREATE ROLE {} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS').format(psycopg.sql.Identifier(login)))
                db.execute(psycopg.sql.SQL('GRANT {} TO {}').format(psycopg.sql.Identifier('numora_main_runtime' if role=='main' else 'numora_irt_runtime'),psycopg.sql.Identifier(login)))
                cls.urls[role]=urlunparse(p._replace(netloc=f'{login}@{p.hostname}:{p.port}'))
            cls.actor=db.execute("INSERT INTO users(auth_user_id,role,admin_role,display_name,email) VALUES(%s,'ADMIN','CONTENT_DATA_MODERATION','TEST ONLY',%s) RETURNING id",(uuid4(),str(uuid4())+'@example.test')).fetchone()['id']
            cls.principal=db.execute('INSERT INTO service_principals(code,enabled) VALUES(%s,true) RETURNING id',(uuid4().hex,)).fetchone()['id']
            package=db.execute("INSERT INTO assessment_packages(family_code,package_version,name,assessment_type) VALUES(%s,1,'TEST ONLY','TRYOUT') RETURNING id",(uuid4().hex,)).fetchone()['id']
            cls.batch=db.execute("INSERT INTO tryout_batches(package_id,starts_at,closes_at,cutoff_at,result_due_at) VALUES(%s,now(),now()+interval '1 day',now()+interval '1 day',now()+interval '4 days') RETURNING id",(package,)).fetchone()['id']
            cls.context=db.execute("INSERT INTO measurement_contexts(ecosystem,dimension,tryout_batch_id,scale_code) VALUES('TRYOUT','RESEARCH',%s,%s) RETURNING id",(cls.batch,uuid4().hex)).fetchone()['id']
        cls.settings=Settings(enabled=True,token='TEST_ONLY_'+'t'*32,database_url=cls.urls['compute'],principal_id=str(cls.principal))
        cls.repo=Repository(cls.settings)

    def fixture(self,value=None):
        root=Path(__file__).resolve().parents[2]
        value=deepcopy(value) if value is not None else json.loads((root/'contracts/irt-calibration-v1/examples/tryout-input.json').read_text())
        value.update(requestId=str(uuid4()),snapshotId=str(uuid4()),calibrationId=str(uuid4()),comparisons=[])
        value['context'].update(contextId=str(self.context),batchId=str(self.batch),scaleId='T:'+str(self.batch))
        for person in value['respondents']:person['batchId']=str(self.batch)
        value['policies']['comparison']=None
        profile=policy()
        definitions={'model':('IRT_MODEL',profile['engine']),'quality':('QUALITY_GATE',profile['quality']),
            'eligibility':('IRT_ELIGIBILITY',profile['eligibility']),
            'scoring':('IRT_SCORING',profile['scoring']),
            'scoreMapping':('SCORE_MAPPING',profile['mapping'])}
        resources={}
        with psycopg.connect(URL,row_factory=dict_row) as db:
            for key,(kind,definition) in definitions.items():
                target=db.execute("INSERT INTO irt_compute.technical_policy_versions(code,version,kind,definition,digest,status) VALUES(%s,1,%s,%s,irt_compute.payload_digest(%s),'SEALED') RETURNING id,digest",(uuid4().hex,kind,Jsonb(definition),Jsonb(definition))).fetchone()
                approval=db.execute('INSERT INTO configuration_approvals(technical_policy_version_id,approved_digest,scope,approved_by_user_id,approved_at) VALUES(%s,%s,%s,%s,now()) RETURNING id',(target['id'],target['digest'],Jsonb({'ecosystem':'TRYOUT','contextId':str(self.context),'purpose':'RESEARCH_ONLY'}),self.actor)).fetchone()['id']
                ref={'id':str(target['id']),'version':1,'digest':target['digest'],'approvalId':str(approval)}
                resources[key]={'ref':ref,'kind':kind,'definition':definition};value['policies'][key]=ref
        body=deepcopy(value);body.pop('inputDigest')
        with psycopg.connect(self.urls['main'],row_factory=dict_row) as db:
            row=db.execute("INSERT INTO irt_calibration_requests_v1(id,snapshot_id,context_id,body,resources,runtime_profile,input_digest) VALUES(%s,%s,%s,%s,%s,%s,'') RETURNING input_digest",(value['requestId'],value['snapshotId'],self.context,Jsonb(body),Jsonb(resources),Jsonb({'purpose':'RESEARCH_ONLY','image':os.environ.get('IRT_RESEARCH_TEST_IMAGE','sha256:'+'a'*64)}))).fetchone()
            db.execute('INSERT INTO irt_calibration_dispatches_v1(request_id,generation,actor_user_id) VALUES(%s,1,%s)',(value['requestId'],self.actor))
        return {'contractVersion':3,'requestId':value['requestId'],'inputDigest':row['input_digest'],'dispatchGeneration':1},resources

    def test_01_http_daemon_artifact_complete_and_replay(self):
        n,_=self.fixture();client=TestClient(create_app(self.settings,self.repo),raise_server_exceptions=False)
        auth={'Authorization':'Bearer '+self.settings.token}
        self.assertEqual(client.post('/api/v1/irt/compute/execute',headers=auth,json=n).status_code,202)
        self.assertTrue(execute_once(self.repo,lambda *a,**kw:self.fail('Insufficient sample must not invoke R')))
        done=client.post('/api/v1/irt/compute/execute',headers=auth,json=n)
        self.assertEqual(done.status_code,200,done.text)
        self.assertEqual(done.json()['status'],'SUCCEEDED')
        with psycopg.connect(self.urls['main'],row_factory=dict_row) as db:
            result=db.execute('SELECT payload FROM irt_compute.calibration_artifacts_v1 WHERE id=%s',(done.json()['artifactId'],)).fetchone()['payload']
        self.assertEqual(result['outcome']['measurementState'],'INSUFFICIENT')
        self.assertEqual(len(result['outcome']['respondents']),2)
        main=Path(os.environ['NUMORA_REPO_PATH'])
        script="""import postgres from './packages/database/node_modules/postgres/src/index.js';
import {verifyCalibrationResearchArtifact} from './packages/irt-orchestration/src/calibration-research.mjs';
const sql=postgres(process.env.IRT_VERIFY_URL,{max:1,onnotice:()=>{}});
try {const r=await verifyCalibrationResearchArtifact(sql,process.env.IRT_VERIFY_ID); if(!r.verified||r.publication)throw Error('Verification failed');}
finally {await sql.end();}"""
        subprocess.run(['node','--input-type=module','-e',script],cwd=main,
            env={**os.environ,'IRT_VERIFY_URL':self.urls['main'],'IRT_VERIFY_ID':n['requestId']},check=True,timeout=20)

    def test_02_concurrent_accept_has_one_durable_job(self):
        n,_=self.fixture()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _:self.repo.accept(n),range(8)))
        with psycopg.connect(URL) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM irt_compute.calibration_jobs_v1 WHERE request_id=%s',(n['requestId'],)).fetchone()[0],1)

    def test_03_wrong_digest_and_revoked_approval_rejected(self):
        n,resources=self.fixture()
        with self.assertRaisesRegex(ValueError,'INPUT_DIGEST_MISMATCH'):self.repo.accept({**n,'inputDigest':'f'*64})
        with psycopg.connect(URL) as db:
            db.execute('UPDATE configuration_approvals SET revoked_at=now() WHERE id=%s',(resources['model']['ref']['approvalId'],))
        with self.assertRaisesRegex(ValueError,'POLICY_UNAVAILABLE'):self.repo.accept(n)

    def test_04_compute_cannot_write_canonical_or_frozen_input(self):
        for query in ["DELETE FROM users", "DELETE FROM irt_calibration_requests_v1"]:
            with psycopg.connect(self.urls['compute']) as db:
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):db.execute(query)

    def test_05_frozen_input_immutable(self):
        n,_=self.fixture()
        with psycopg.connect(self.urls['main']) as db:
            with self.assertRaises(psycopg.Error):db.execute('UPDATE irt_calibration_requests_v1 SET body=body WHERE id=%s',(n['requestId'],))

    def test_05b_postgres_digest_matches_frozen_cross_language_vector(self):
        root=Path(__file__).resolve().parents[2]
        vector=json.loads((root/'contracts/irt-calibration-service-v1/digest-vector.json').read_text())
        with psycopg.connect(URL) as db:
            text,digest=db.execute('SELECT %s::jsonb::text,irt_compute.payload_digest(%s::jsonb)',(Jsonb(vector['value']),Jsonb(vector['value']))).fetchone()
        self.assertEqual(text,vector['postgresJsonbText'])
        self.assertEqual(digest,vector['sha256'])

    def test_06_outbox_is_atomic_and_cancellation_fences_execution(self):
        n,_=self.fixture()
        with psycopg.connect(URL,row_factory=dict_row) as db:
            event=db.execute("SELECT o.payload FROM analytics_outbox o JOIN outbox_deliveries d ON d.outbox_id=o.id WHERE o.entity_id=%s AND d.consumer='irt_research'",(n['requestId'],)).fetchone()
            self.assertEqual(event['payload'],n)
        self.repo.accept(n)
        with psycopg.connect(self.urls['main']) as db:
            db.execute('INSERT INTO irt_calibration_cancellations_v1(request_id,actor_user_id) VALUES(%s,%s)',(n['requestId'],self.actor))
        with self.assertRaisesRegex(ValueError,'POLICY_UNAVAILABLE'):self.repo.get(n)

    def test_07_technical_failure_is_retryable_but_never_a_scientific_score(self):
        # Drain earlier accepted jobs so this case owns the next claim.
        while execute_once(self.repo):pass
        n,_=self.fixture();self.repo.accept(n)
        with patch('numora_service.irt.daemon.run',side_effect=ValueError('TIMEOUT')):
            self.assertTrue(execute_once(self.repo))
        self.assertEqual(self.repo.get(n)['status'],'FAILED')
        with psycopg.connect(self.urls['main'],row_factory=dict_row) as db:
            row=db.execute('INSERT INTO irt_calibration_dispatches_v1(request_id,generation,actor_user_id) VALUES(%s,2,%s) RETURNING generation',(n['requestId'],self.actor)).fetchone()
        new={**n,'dispatchGeneration':row['generation']}
        with self.assertRaisesRegex(ValueError,'STALE_DISPATCH'):self.repo.accept(n)
        self.repo.accept(new);self.assertTrue(execute_once(self.repo))
        self.assertEqual(self.repo.get(new)['status'],'SUCCEEDED')
        with psycopg.connect(self.urls['main']) as db:
            with self.assertRaises(psycopg.Error):db.execute('INSERT INTO irt_calibration_dispatches_v1(request_id,generation,actor_user_id) VALUES(%s,3,%s)',(n['requestId'],self.actor))

    def test_08_only_one_daemon_can_hold_live_work(self):
        n,_=self.fixture();other,_=self.fixture()
        self.repo.accept(n);self.repo.accept(other)
        with ThreadPoolExecutor(max_workers=2) as pool:
            claims=list(pool.map(lambda _:self.repo.claim_next(),range(2)))
        self.assertEqual(sum(c is not None for c in claims),1)
        job,source,notification=next(c for c in claims if c)
        self.repo.heartbeat(job,notification)
        with psycopg.connect(self.urls['main']) as db:
            db.execute('INSERT INTO irt_calibration_cancellations_v1(request_id,actor_user_id) VALUES(%s,%s)',(notification['requestId'],self.actor))
        with self.assertRaisesRegex(ValueError,'POLICY_UNAVAILABLE'):self.repo.heartbeat(job,notification)

    @unittest.skipUnless(os.environ.get('IRT_RESEARCH_TEST_IMAGE'),'Requires pinned R image; run full scientific harness')
    def test_09_synthetic_http_r_artifact(self):
        from research.irt.synthetic import generate
        with psycopg.connect(URL) as db:
            db.execute("UPDATE irt_compute.calibration_jobs_v1 SET status='EXPIRED',failure_code='LEASE_EXPIRED',finished_at=now() WHERE status IN ('RUNNING','ACCEPTED')")
        value,_=generate(1000)
        n,_=self.fixture(value)
        client=TestClient(create_app(self.settings,self.repo),raise_server_exceptions=False)
        response=client.post('/api/v1/irt/compute/execute',headers={'Authorization':'Bearer '+self.settings.token},json=n)
        self.assertEqual(response.status_code,202,response.text)
        self.assertTrue(execute_once(self.repo))
        status=self.repo.get(n)
        self.assertEqual(status['status'],'SUCCEEDED')
        with psycopg.connect(self.urls['main'],row_factory=dict_row) as db:
            artifact=db.execute('SELECT payload,diagnostics FROM irt_compute.calibration_artifacts_v1 WHERE id=%s',(status['artifactId'],)).fetchone()
        self.assertTrue(artifact['diagnostics']['converged'],artifact['diagnostics'])
        self.assertEqual(len(artifact['payload']['outcome']['respondents']),2000)


if __name__=='__main__':unittest.main()
