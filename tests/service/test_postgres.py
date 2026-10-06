"""Connected tests against canonical migrations and distinct main/compute LOGINS."""
from concurrent.futures import ThreadPoolExecutor
import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import socket
import threading
import time
import unittest
from urllib.parse import urlparse, urlunparse
from uuid import uuid4
from unittest.mock import patch

import httpx
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
import uvicorn

from numora_service.api import create_app
from numora_service.bridge import config_hash, original_record, workspace
from numora_service.content import record_content
from numora_service.contracts import validate
from numora_service.errors import ServiceError
from numora_service.executor import Executor, generate_result
from numora_service.register import register
from numora_service.repository import Repository
from numora_service.settings import Settings
from numora_service.task import validate_task


URL = os.environ.get("TEST_COMPUTE_OWNER_URL")


@unittest.skipUnless(URL, "Run tests/service/check_postgres.py for an isolated migrated cluster")
class PostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parsed = urlparse(URL)
        if parsed.hostname not in ("localhost", "127.0.0.1") or not parsed.path.startswith("/generator_test_"):
            raise RuntimeError("Local disposable test database required")
        cls.owner_url = URL
        cls.bank, cls.configs = workspace()
        with psycopg.connect(URL, row_factory=dict_row) as db:
            cls.main_login = "main_" + uuid4().hex
            cls.compute_login = "compute_" + uuid4().hex
            for login, group in ((cls.main_login, "numora_main_runtime"), (cls.compute_login, "numora_irt_runtime")):
                db.execute(psycopg.sql.SQL("CREATE ROLE {} LOGIN INHERIT NOSUPERUSER NOBYPASSRLS").format(psycopg.sql.Identifier(login)))
                db.execute(psycopg.sql.SQL("GRANT {} TO {}").format(psycopg.sql.Identifier(group), psycopg.sql.Identifier(login)))
            cls.main_url = urlunparse(parsed._replace(netloc=f"{cls.main_login}@{parsed.hostname}:{parsed.port}"))
            cls.compute_url = urlunparse(parsed._replace(netloc=f"{cls.compute_login}@{parsed.hostname}:{parsed.port}"))
            cls.actor = db.execute("""INSERT INTO users(auth_user_id,role,display_name,email)
                VALUES(%s,'ADMIN','TEST reviewer',%s) RETURNING id""", (uuid4(), f"{uuid4()}@example.test")).fetchone()["id"]
            cls.principal = db.execute("INSERT INTO service_principals(code,enabled) VALUES(%s,true) RETURNING id", (str(uuid4()),)).fetchone()["id"]
            # Demonstrate the real precondition: existing canonical dispatch guard rejects generation.
            definition = db.execute("SELECT pg_get_functiondef('public.measurement_dispatch_guard()'::regprocedure) AS body").fetchone()["body"]
            if "r.request_type<>'CALIBRATE_TRYOUT'" not in definition:
                raise RuntimeError("Update TEST ONLY guard fixture after central migration changes")
            cls.old_dispatch_guard = definition
            cls.test_dispatch_guard = definition.replace("r.request_type<>'CALIBRATE_TRYOUT'", "r.request_type NOT IN ('CALIBRATE_TRYOUT','GENERATE_VARIANTS')")
        cls.settings = Settings(True, "test-token-" + "t"*32, cls.compute_url, str(cls.principal))
        cls.repository = Repository(cls.settings, cls.bank)

    @classmethod
    def db(cls, role="owner"):
        return psycopg.connect({"owner": cls.owner_url, "main": cls.main_url, "compute": cls.compute_url}[role], row_factory=dict_row)

    def fixture(self, qid="pg-6-1-1", seed=5, dispatch=True):
        orig = self.bank.get(qid)
        content = record_content(original_record(orig))
        key = "test-" + uuid4().hex
        with self.db() as db:
            chapter = db.execute("INSERT INTO chapters(code,slug,name,display_order) VALUES(%s,%s,'TEST chapter',%s) RETURNING id", (key,key, int(uuid4().hex[:7],16))).fetchone()["id"]
            sub = db.execute("INSERT INTO subchapters(chapter_id,code,slug,name,display_order) VALUES(%s,%s,%s,'TEST subchapter',1) RETURNING id", (chapter,key,key)).fetchone()["id"]
            level = db.execute("INSERT INTO levels(subchapter_id,level_number) VALUES(%s,1) RETURNING id", (sub,)).fetchone()["id"]
            comp = db.execute("INSERT INTO competencies(subchapter_id,code,description) VALUES(%s,%s,'TEST competency') RETURNING id", (sub,key)).fetchone()["id"]
            family = db.execute("INSERT INTO questions(primary_competency_id) VALUES(%s) RETURNING id", (comp,)).fetchone()["id"]
            variant = db.execute("INSERT INTO question_variants(question_id,variant_code,kind,origin) VALUES(%s,'O','ORIGINAL','TEST') RETURNING id", (family,)).fetchone()["id"]
            rubric = db.execute("""INSERT INTO scoring_rubric_versions(code,version,question_type,maximum_score_category,definition,digest,status,approved_by_user_id,approved_at)
                VALUES(%s,1,%s,1,'{"testOnly":true}','TEST-rubric','SEALED',%s,now()) RETURNING id""", (key,content["questionType"],self.actor)).fetchone()["id"]
            version = db.execute("""INSERT INTO question_versions(variant_id,version_number,question_type,stem,options_or_statements,answer_key,explanation,media,difficulty,level_id,scoring_rubric_version_id)
                VALUES(%s,1,%s,%s,%s,%s,%s,'[]','MEDIUM',%s,%s) RETURNING id""",
                (variant,content["questionType"],Jsonb(content["stem"]),Jsonb(content["optionsOrStatements"]),Jsonb(content["answerKey"]),Jsonb({"text":"TEST original explanation"}),level,rubric)).fetchone()["id"]
            context = db.execute("INSERT INTO measurement_contexts(ecosystem,dimension,level_id,scale_code) VALUES('DRILL','TEST',%s,%s) RETURNING id", (level,key)).fetchone()["id"]
        manifest = {"serviceContract": "generator-service-v1", "items": [{"questionExternalId": qid, "configVersion": self.configs.load(qid)[0]["config_version"],
            "parentQuestionVersionId": str(version), "familyId": str(family), "rubricVersionId": str(rubric), "contextId": str(context)}]}
        dry = register(self.repository, self.bank, self.configs, manifest)
        self.assertIsNone(dry["items"][0]["generatorConfigId"])
        registered = register(self.repository, self.bank, self.configs, manifest, apply=True, seal=True)["items"][0]
        self.assertEqual(register(self.repository, self.bank, self.configs, manifest, apply=True, seal=True)["items"][0], registered)
        with self.db("main") as db:
            approval = db.execute("""INSERT INTO configuration_approvals(generator_config_id,approved_digest,scope,approved_by_user_id,approved_at)
                VALUES(%s,%s,%s,%s,now()) RETURNING id""", (registered["generatorConfigId"],registered["digest"],Jsonb({"ecosystem":"DRILL","contextId":str(context)}),self.actor)).fetchone()["id"]
            wave = db.execute("INSERT INTO generation_waves(code,status,created_by_user_id,approved_at,constraints) VALUES(%s,'APPROVED',%s,now(),'{}') RETURNING id", (key,self.actor)).fetchone()["id"]
            item = db.execute("""INSERT INTO generation_wave_items(wave_id,original_question_version_id,context_id,generator_config_id,configuration_approval_id,target_count,max_regenerate_attempts,constraints)
                VALUES(%s,%s,%s,%s,%s,1,0,%s) RETURNING id""", (wave,version,context,registered["generatorConfigId"],approval,Jsonb({"serviceContract":"generator-service-v1","seed":seed}))).fetchone()["id"]
            req = db.execute("""INSERT INTO analysis_requests(idempotency_key,request_type,context_id,wave_item_id,configuration_pins,input_digest)
                VALUES(%s,'GENERATE_VARIANTS',%s,%s,%s,'') RETURNING id,input_digest""", (key,context,item,Jsonb([{"approvalId":str(approval),"digest":registered["digest"]}]))).fetchone()
        if dispatch:
            with self.db() as db:
                db.execute(self.test_dispatch_guard)
            self.dispatch(req["id"], 1)
        return {"notification": {"contractVersion":3,"requestId":str(req["id"]),"inputDigest":req["input_digest"],"dispatchGeneration":1},
                "version":version,"family":family,"variant":variant,"rubric":rubric,"level":level,"approval":approval,"manifest":manifest}

    def dispatch(self, request, generation):
        with self.db("main") as db:
            db.execute("""INSERT INTO analysis_request_dispatches(request_id,generation,operation_key,operation_fingerprint,actor_user_id)
                VALUES(%s,%s,%s,'TEST',%s)""", (request,generation,str(uuid4()),self.actor))
            if generation > 1:
                db.execute("UPDATE analysis_requests SET status='PENDING' WHERE id=%s", (request,))

    def count(self, table, req):
        with self.db() as db:
            if table == "candidates":
                return db.execute("SELECT count(*) AS n FROM irt_compute.generation_candidates c JOIN irt_compute.generation_runs r ON r.id=c.generation_run_id JOIN irt_compute.compute_executions e ON e.id=r.execution_id WHERE e.request_id=%s", (req,)).fetchone()["n"]
            return db.execute("SELECT count(*) AS n FROM irt_compute.compute_executions WHERE request_id=%s", (req,)).fetchone()["n"]

    def test_00_central_dispatch_migration_required(self):
        f = self.fixture(dispatch=False)
        with self.db() as db:
            db.execute(self.old_dispatch_guard)
        try:
            with self.assertRaises(psycopg.errors.CheckViolation):
                self.dispatch(f["notification"]["requestId"],1)
        finally:
            with self.db() as db:
                db.execute(self.test_dispatch_guard)

    def test_role_boundaries_and_readiness(self):
        self.repository.ready()
        for role, sql in (("compute", "SELECT email FROM public.users"), ("compute", "UPDATE public.question_versions SET content_status='READY'"),
                          ("main", "UPDATE irt_compute.generator_configs SET parameters='{}'"), ("compute", "CREATE TABLE irt_compute.illegal(id int)")):
            with self.db(role) as db:
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    db.execute(sql)
        unsafe = Repository(replace(self.settings,database_url=self.owner_url),self.bank)
        with self.assertRaisesRegex(ServiceError,"UNSAFE_COMPUTE_ROLE"):
            unsafe.ready()
        with self.db() as db:
            db.execute(psycopg.sql.SQL("GRANT UPDATE ON public.question_versions TO {}").format(psycopg.sql.Identifier(self.compute_login)))
        try:
            with self.assertRaisesRegex(ServiceError,"UNSAFE_COMPUTE_ROLE"):
                self.repository.ready()
        finally:
            with self.db() as db:
                db.execute(psycopg.sql.SQL("REVOKE UPDATE ON public.question_versions FROM {}").format(psycopg.sql.Identifier(self.compute_login)))

    def test_three_formats_real_process_replay_and_db_digest(self):
        for qid in ("pg-6-1-1","mcma-16-1-7","kategori-16-1-10"):
            with self.subTest(qid=qid):
                f = self.fixture(qid)
                result = Executor(self.repository,self.settings).execute(f["notification"])
                validate("response",result)
                self.assertEqual(result["status"],"SUCCEEDED")
                self.assertEqual(Executor(self.repository,self.settings).execute(f["notification"]),result)
                self.assertEqual(self.count("executions",result["requestId"]),1)
                self.assertEqual(self.count("candidates",result["requestId"]),1)
                with self.db() as db:
                    row = db.execute("SELECT payload,payload_digest,irt_compute.payload_digest(payload) AS actual FROM irt_compute.generation_candidates WHERE id=%s",(result["candidateIds"][0],)).fetchone()
                    self.assertEqual(row["payload_digest"],row["actual"])
                    self.assertEqual(db.execute("SELECT count(*) AS n FROM public.candidate_imports WHERE candidate_id=%s",(result["candidateIds"][0],)).fetchone()["n"],0)

    def test_concurrent_claim_and_stale_digest(self):
        f = self.fixture()
        with ThreadPoolExecutor(max_workers=2) as pool:
            claims = list(pool.map(lambda _: self.repository.claim(f["notification"]),range(2)))
        self.assertEqual(sum("execution" in c for c in claims),1)
        self.assertEqual(sum("response" in c for c in claims),1)
        claimed = next(c for c in claims if "execution" in c)
        self.repository.fail(claimed["execution"],"TEST_STOP")
        with self.assertRaisesRegex(ServiceError,"INPUT_DIGEST_MISMATCH"):
            self.repository.claim({**f["notification"],"inputDigest":"b"*64})

    def test_revocation_rollback_and_partial_insert_failure(self):
        f = self.fixture()
        claim = self.repository.claim(f["notification"])
        result = generate_result(claim["work"])
        with self.db("main") as db:
            db.execute("UPDATE configuration_approvals SET revoked_at=now() WHERE id=%s",(f["approval"],))
        with self.assertRaisesRegex(ServiceError,"CONFIG_APPROVAL_MISMATCH"):
            self.repository.persist(f["notification"],claim,result)
        self.assertEqual(self.count("candidates",f["notification"]["requestId"]),0)
        self.repository.fail(claim["execution"],"CONFIG_APPROVAL_MISMATCH")
        f = self.fixture()
        original_one = self.repository.one
        def injected(db,sql,params=()):
            if "INSERT INTO irt_compute.compute_outputs" in sql:
                raise ServiceError("TEST_AFTER_CANDIDATE")
            return original_one(db,sql,params)
        with patch.object(self.repository,"one",side_effect=injected):
            with self.assertRaisesRegex(ServiceError,"TEST_AFTER_CANDIDATE"):
                Executor(self.repository,self.settings,lambda w,h,s:generate_result(w)).execute(f["notification"])
        self.assertEqual(self.count("candidates",f["notification"]["requestId"]),0)

    def test_expiry_heartbeat_and_new_dispatch_retry(self):
        f = self.fixture()
        claim = self.repository.claim(f["notification"])
        self.repository.heartbeat(claim["execution"])
        with self.db() as db:
            db.execute("UPDATE irt_compute.compute_executions SET lease_expires_at=clock_timestamp()-interval '1 second' WHERE id=%s",(claim["execution"]["id"],))
        with self.assertRaisesRegex(ServiceError,"STALE_EXECUTION"):
            self.repository.heartbeat(claim["execution"])
        expired = self.repository.claim(f["notification"])["response"]
        self.assertEqual(expired["status"],"EXPIRED")
        self.dispatch(f["notification"]["requestId"],2)
        with self.assertRaisesRegex(ServiceError,"STALE_DISPATCH"):
            self.repository.claim(f["notification"])
        new = {**f["notification"],"dispatchGeneration":2}
        self.assertEqual(Executor(self.repository,self.settings).execute(new)["status"],"SUCCEEDED")
        self.assertEqual(self.count("executions",new["requestId"]),2)

    def test_timeout_and_heartbeat_failure_write_no_candidate(self):
        f = self.fixture()
        with self.assertRaisesRegex(ServiceError,"GENERATION_TIMEOUT"):
            Executor(self.repository,replace(self.settings,execution_seconds=0.001)).execute(f["notification"])
        self.assertEqual(self.repository.claim(f["notification"])["response"]["status"],"FAILED")
        f = self.fixture()
        def heartbeat_runner(work,heartbeat,settings):
            heartbeat()
            return generate_result(work)
        with patch.object(self.repository,"heartbeat",side_effect=ServiceError("COMPUTE_DATABASE_ERROR",503)):
            with self.assertRaises(ServiceError):
                Executor(self.repository,self.settings,heartbeat_runner).execute(f["notification"])
        self.assertEqual(self.count("candidates",f["notification"]["requestId"]),0)

    def test_import_guards_and_draft_replay(self):
        f = self.fixture()
        result = Executor(self.repository,self.settings).execute(f["notification"])
        with self.db() as db:
            candidate = db.execute("SELECT * FROM irt_compute.generation_candidates WHERE id=%s",(result["candidateIds"][0],)).fetchone()
        p = candidate["payload"]
        def import_draft(adopt=False, mutate=False, wrong_parent=None):
            with self.db("main") as db:
                if adopt:
                    db.execute("UPDATE analysis_requests SET accepted_execution_id=%s,status='COMPLETED' WHERE id=%s",(result["executionId"],result["requestId"]))
                existing = db.execute("SELECT question_version_id FROM candidate_imports WHERE candidate_id=%s",(candidate["id"],)).fetchone()
                if existing: return existing["question_version_id"]
                variant = db.execute("INSERT INTO question_variants(question_id,variant_code,kind,origin,original_variant_id) VALUES(%s,%s,'VARIANT','TEST',%s) RETURNING id",(f["family"],str(uuid4()),f["variant"])).fetchone()["id"]
                version = db.execute("""INSERT INTO question_versions(variant_id,version_number,question_type,stem,options_or_statements,answer_key,explanation,media,difficulty,level_id,scoring_rubric_version_id,parent_original_question_version_id,content_fingerprint)
                    VALUES(%s,1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",(variant,p["questionType"],Jsonb({"text":"tampered"} if mutate else p["stem"]),Jsonb(p["optionsOrStatements"]),Jsonb(p["answerKey"]),Jsonb(p["explanation"]),Jsonb(p["media"]),p["difficulty"],f["level"],p["rubricVersionId"],wrong_parent or f["version"],p["contentFingerprint"])).fetchone()["id"]
                db.execute("INSERT INTO candidate_imports(candidate_id,question_version_id,payload_digest,imported_by_user_id) VALUES(%s,%s,%s,%s)",(candidate["id"],version,candidate["payload_digest"],self.actor))
                return version
        with self.assertRaises(psycopg.errors.CheckViolation): import_draft()
        with self.assertRaises(psycopg.errors.CheckViolation): import_draft(adopt=True,mutate=True)
        # Correct content with an adopted artifact that does not list this candidate is rejected.
        f2 = self.fixture()
        with self.assertRaises(psycopg.errors.CheckViolation):
            import_draft(adopt=True, wrong_parent=f2["version"])
        claim2 = self.repository.claim(f2["notification"])
        generated2 = generate_result(claim2["work"])
        normal_one = self.repository.one
        def empty_artifact(db, sql, params=()):
            if "INSERT INTO irt_compute.compute_outputs" in sql:
                params = (*params[:2], Jsonb({"candidateIds": []}))
            return normal_one(db, sql, params)
        with patch.object(self.repository,"one",side_effect=empty_artifact):
            missing = self.repository.persist(f2["notification"],claim2,generated2)
        self.assertEqual(missing["candidateIds"],[])
        with self.db("main") as db:
            db.execute("UPDATE analysis_requests SET accepted_execution_id=%s,status='COMPLETED' WHERE id=%s",(missing["executionId"],missing["requestId"]))
        with self.db() as db:
            undeclared = db.execute("SELECT c.* FROM irt_compute.generation_candidates c JOIN irt_compute.generation_runs r ON r.id=c.generation_run_id WHERE r.execution_id=%s",(missing["executionId"],)).fetchone()
        p2 = undeclared["payload"]
        with self.db("main") as db:
            variant2 = db.execute("INSERT INTO question_variants(question_id,variant_code,kind,origin,original_variant_id) VALUES(%s,%s,'VARIANT','TEST',%s) RETURNING id",(f2["family"],str(uuid4()),f2["variant"])).fetchone()["id"]
            v2 = db.execute("""INSERT INTO question_versions(variant_id,version_number,question_type,stem,options_or_statements,answer_key,explanation,media,difficulty,level_id,scoring_rubric_version_id,parent_original_question_version_id,content_fingerprint)
                VALUES(%s,1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",(variant2,p2["questionType"],Jsonb(p2["stem"]),Jsonb(p2["optionsOrStatements"]),Jsonb(p2["answerKey"]),Jsonb(p2["explanation"]),Jsonb(p2["media"]),p2["difficulty"],f2["level"],p2["rubricVersionId"],f2["version"],p2["contentFingerprint"])).fetchone()["id"]
        with self.db("main") as db:
            with self.assertRaisesRegex(psycopg.errors.CheckViolation,"listed in the adopted generation artifact"):
                db.execute("INSERT INTO candidate_imports(candidate_id,question_version_id,payload_digest,imported_by_user_id) VALUES(%s,%s,%s,%s)",(undeclared["id"],v2,undeclared["payload_digest"],self.actor))
        version = import_draft(adopt=True)
        self.assertEqual(import_draft(),version)
        print("TEST ONLY draft proof: " + json.dumps({"parentOriginalVersionId": str(f["version"]),
              "candidateId": str(candidate["id"]), "draftVersionId": str(version)}))
        with self.db() as db:
            state = db.execute("SELECT content_status,parent_original_question_version_id FROM question_versions WHERE id=%s",(version,)).fetchone()
            self.assertEqual(state["content_status"],"DRAFT")
            self.assertEqual(state["parent_original_question_version_id"],f["version"])
            self.assertEqual(db.execute("SELECT count(*) AS n FROM question_variants WHERE question_id=%s AND kind='VARIANT'",(f["family"],)).fetchone()["n"],1)
            self.assertEqual(db.execute("SELECT count(*) AS n FROM question_versions WHERE variant_id=%s",(f["variant"],)).fetchone()["n"],1)
            # Immutable candidate and post-completion append protection.
            with self.assertRaises(psycopg.errors.CheckViolation):
                db.execute("UPDATE irt_compute.generation_candidates SET payload='{}' WHERE id=%s",(candidate["id"],))

    def test_wrong_rubric_config_target_and_fencing_rejected(self):
        f = self.fixture()
        claim = self.repository.claim(f["notification"])
        for key, field, value, code in (("rubric","question_type","CATEGORY","RUBRIC_MISMATCH"),
                                       ("config","status","DRAFT","UNAUTHORIZED_WAVE"),
                                       ("wave","target_count",2,"UNSUPPORTED_TARGET_COUNT")):
            task = copy.deepcopy(claim["task"])
            task[key][field] = value
            with self.assertRaisesRegex(ServiceError,code): validate_task(task,self.bank)
        result = generate_result(claim["work"])
        bad = {**claim, "execution": {**claim["execution"], "fencing_token": uuid4()}}
        with self.assertRaisesRegex(ServiceError,"STALE_EXECUTION"):
            self.repository.persist(f["notification"],bad,result)
        with self.db() as db:
            db.execute("UPDATE irt_compute.compute_executions SET lease_expires_at=clock_timestamp()-interval '1 second' WHERE id=%s",(claim["execution"]["id"],))
        with self.assertRaises(ServiceError): self.repository.persist(f["notification"],claim,result)
        self.assertEqual(self.count("candidates",f["notification"]["requestId"]),0)

    def test_pinned_config_survives_new_local_latest_and_payload_errors(self):
        f = self.fixture()
        # Local latest is irrelevant to execution: use the DB snapshot registered above.
        with patch("numora_service.bridge.ConfigStore.load", side_effect=RuntimeError("new local config")):
            self.assertEqual(Executor(self.repository,self.settings).execute(f["notification"])["status"],"SUCCEEDED")
        f = self.fixture()
        with self.db("main") as db:
            # The frozen wave prevents silently replacing seed/target after prepare.
            with self.assertRaises(psycopg.errors.CheckViolation):
                db.execute("UPDATE generation_wave_items SET target_count=2 WHERE id=(SELECT wave_item_id FROM analysis_requests WHERE id=%s)",(f["notification"]["requestId"],))
        with patch.object(self.bank,"get",side_effect=lambda qid: {**workspace()[0].get(qid),"hash":"bad"}):
            with self.assertRaisesRegex(ServiceError,"SOURCE_MAPPING_MISMATCH"):
                self.repository.claim(f["notification"])

    def test_real_http_and_lost_response_restart_replay(self):
        f = self.fixture()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1",0))
            sock.listen()
            port = sock.getsockname()[1]
            server = uvicorn.Server(uvicorn.Config(create_app(self.settings),log_level="critical",access_log=False))
            thread = threading.Thread(target=server.run,kwargs={"sockets":[sock]},daemon=True)
            thread.start()
            deadline = time.monotonic()+10
            while not server.started and time.monotonic()<deadline: time.sleep(0.02)
            try:
                response = httpx.post(f"http://127.0.0.1:{port}/api/v1/compute/execute",json=f["notification"],headers={"Authorization":"Bearer "+self.settings.token},timeout=40)
                self.assertEqual(response.status_code,200,response.text)
                result = response.json()
            finally:
                server.should_exit=True
                thread.join(timeout=10)
        # New repository/executor simulates restart after a committed response was lost.
        restarted = Executor(Repository(self.settings,self.bank),self.settings)
        self.assertEqual(restarted.execute(f["notification"]),result)
        self.assertEqual(self.count("candidates",result["requestId"]),1)
