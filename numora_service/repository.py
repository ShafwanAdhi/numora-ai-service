"""Compute-only PostgreSQL persistence compatible with Numora's v3 guards."""
from contextlib import contextmanager

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from . import GENERATOR_VERSION, SERVICE_CONTRACT
from .content import uuid
from .contracts import validate_notification, validate_payload
from .errors import ServiceError
from .task import validate_task


class Repository:
    def __init__(self, settings, bank):
        self.settings, self.bank = settings, bank

    @contextmanager
    def connection(self):
        try:
            info = conninfo_to_dict(self.settings.database_url)
            local = all(h in ("127.0.0.1", "localhost", "::1") for h in info.get("host", "").split(","))
            tls = {} if local else {"sslmode": "verify-full"}
            with psycopg.connect(self.settings.database_url, connect_timeout=5, prepare_threshold=None,
                                 options="-c statement_timeout=5000 -c lock_timeout=5000",
                                 row_factory=dict_row, **tls) as db:
                yield db
        except psycopg.Error:
            raise ServiceError("COMPUTE_DATABASE_ERROR", 503) from None

    @staticmethod
    def one(db, sql, params=()):
        row = db.execute(sql, params).fetchone()
        if row is None:
            raise ServiceError("COMPUTE_INPUT_NOT_FOUND", 404)
        return row

    def check_role(self, db):
        role = self.one(db, """SELECT r.rolsuper,r.rolbypassrls,r.rolcreatedb,r.rolcreaterole,
            pg_has_role(current_user,'numora_irt_runtime','MEMBER') AS compute,
            pg_has_role(current_user,'numora_main_runtime','MEMBER') AS main,
            EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                WHERE n.nspname IN ('public','irt_compute') AND pg_has_role(r.oid,c.relowner,'USAGE')) AS owner,
            has_schema_privilege(current_user,'public','CREATE') OR
                has_schema_privilege(current_user,'irt_compute','CREATE') AS ddl,
            EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                WHERE n.nspname='public' AND c.relkind IN ('r','p') AND
                has_table_privilege(current_user,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')) AS canonical_writer
            FROM pg_roles r WHERE r.rolname=current_user""")
        if (role["rolsuper"] or role["rolbypassrls"] or role["rolcreatedb"] or role["rolcreaterole"] or
                role["main"] or role["owner"] or role["ddl"] or role["canonical_writer"] or not role["compute"]):
            raise ServiceError("UNSAFE_COMPUTE_ROLE", 503)
        self.one(db, "SELECT id FROM public.irt_input_principals_v3 WHERE id=%s AND enabled",
                 (uuid(self.settings.principal_id),))

    def ready(self):
        with self.connection() as db:
            self.check_role(db)
            for view in ("requests", "dispatches", "wave_items", "content", "approvals", "rubrics", "contexts"):
                # Fixed internal allowlist, never a user identifier.
                db.execute(f"SELECT 1 FROM public.irt_input_{view}_v3 LIMIT 0")
            db.execute("SELECT 1 FROM irt_compute.generator_configs LIMIT 0")

    def request(self, db, notification):
        row = self.one(db, "SELECT * FROM public.irt_input_requests_v3 WHERE id=%s", (notification["requestId"],))
        if row["contract_version"] != 3 or row["input_digest"] != notification["inputDigest"]:
            raise ServiceError("INPUT_DIGEST_MISMATCH")
        if row["request_type"] != "GENERATE_VARIANTS":
            raise ServiceError("UNSUPPORTED_REQUEST", 422)
        dispatch = self.one(db, """SELECT * FROM public.irt_input_dispatches_v3 WHERE request_id=%s
                                  ORDER BY generation DESC LIMIT 1""", (notification["requestId"],))
        if dispatch["generation"] != notification["dispatchGeneration"]:
            raise ServiceError("STALE_DISPATCH")
        return row, dispatch

    def load_task(self, db, request):
        wave = self.one(db, "SELECT * FROM public.irt_input_wave_items_v3 WHERE id=%s", (request["wave_item_id"],))
        config = self.one(db, "SELECT *,irt_compute.payload_digest(parameters) AS actual_digest FROM irt_compute.generator_configs WHERE id=%s", (wave["generator_config_id"],))
        if config["digest"] != config["actual_digest"]:
            raise ServiceError("CONFIG_PIN_MISMATCH")
        source = self.one(db, "SELECT * FROM public.irt_input_content_v3 WHERE id=%s", (wave["original_question_version_id"],))
        approval = self.one(db, "SELECT * FROM public.irt_input_approvals_v3 WHERE id=%s", (wave["configuration_approval_id"],))
        rubric = self.one(db, "SELECT * FROM public.irt_input_rubrics_v3 WHERE id=%s", (source["scoring_rubric_version_id"],))
        context = self.one(db, "SELECT * FROM public.irt_input_contexts_v3 WHERE id=%s", (request["context_id"],))
        for pin in request["configuration_pins"]:
            extra = self.one(db, "SELECT * FROM public.irt_input_approvals_v3 WHERE id=%s", (pin["approvalId"],))
            if extra["revoked_at"] is not None or extra["approved_digest"] != pin["digest"]:
                raise ServiceError("CONFIG_APPROVAL_MISMATCH")
        task = dict(request=request, wave=wave, config=config, source=source, approval=approval, rubric=rubric, context=context)
        try:
            work = validate_task(task, self.bank)
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ServiceError("INVALID_COMPUTE_INPUT", 422) from None
        return task, work

    def response(self, db, notification, execution):
        artifacts = db.execute("""SELECT id,digest,payload FROM irt_compute.compute_outputs
            WHERE execution_id=%s AND kind='GENERATE_VARIANTS' ORDER BY sequence_number""", (execution["id"],)).fetchall()
        return {"serviceContract": SERVICE_CONTRACT, "requestId": notification["requestId"],
                "dispatchGeneration": notification["dispatchGeneration"], "executionId": str(execution["id"]),
                "status": execution["status"], "failureCode": execution.get("failure_code"),
                "artifactId": str(artifacts[0]["id"]) if artifacts else None,
                "artifactDigest": artifacts[0]["digest"] if artifacts else None,
                "candidateIds": artifacts[0]["payload"]["candidateIds"] if artifacts else []}

    def claim(self, notification):
        validate_notification(notification)
        with self.connection() as db:
            self.check_role(db)
            db.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,3))", (notification["requestId"],))
            request, dispatch = self.request(db, notification)
            db.execute("""UPDATE irt_compute.compute_executions SET status='EXPIRED',finished_at=clock_timestamp(),
                failure_code='LEASE_EXPIRED' WHERE request_id=%s AND status='RUNNING' AND lease_expires_at<=clock_timestamp()""",
                       (request["id"],))
            existing = db.execute("SELECT * FROM irt_compute.compute_executions WHERE dispatch_id=%s", (dispatch["id"],)).fetchone()
            if existing:
                return {"response": self.response(db, notification, existing)}
            if request["status"] != "PENDING":
                raise ServiceError("REQUEST_NOT_PENDING")
            task, work = self.load_task(db, request)
            execution = self.one(db, """INSERT INTO irt_compute.compute_executions
                (request_id,attempt_number,service_principal_id,lease_expires_at,dispatch_id)
                SELECT %s,coalesce(max(attempt_number),0)+1,%s,clock_timestamp()+(%s * interval '1 second'),%s
                FROM irt_compute.compute_executions WHERE request_id=%s RETURNING *""",
                (request["id"], self.settings.principal_id, self.settings.lease_seconds, dispatch["id"], request["id"]))
            return dict(execution=execution, task=task, work=work)

    def heartbeat(self, execution):
        with self.connection() as db:
            self.check_role(db)
            row = db.execute("""UPDATE irt_compute.compute_executions SET heartbeat_at=clock_timestamp(),
                lease_expires_at=clock_timestamp()+(%s * interval '1 second') WHERE id=%s AND fencing_token=%s
                AND status='RUNNING' AND lease_expires_at>clock_timestamp() RETURNING id""",
                (self.settings.lease_seconds, execution["id"], execution["fencing_token"])).fetchone()
            if row is None:
                raise ServiceError("STALE_EXECUTION")

    def finish(self, db, execution, failure=None):
        row = db.execute("""UPDATE irt_compute.compute_executions SET status=%s,failure_code=%s,finished_at=clock_timestamp()
            WHERE id=%s AND fencing_token=%s AND status='RUNNING' AND lease_expires_at>clock_timestamp() RETURNING *""",
            ("FAILED" if failure else "SUCCEEDED", failure, execution["id"], execution["fencing_token"])).fetchone()
        if row is None:
            raise ServiceError("STALE_EXECUTION")
        return row

    def fail(self, execution, code):
        with self.connection() as db:
            self.check_role(db)
            self.finish(db, execution, code)

    def persist(self, notification, claim, result):
        validate_payload(result["payload"])
        execution = claim["execution"]
        with self.connection() as db:
            self.check_role(db)
            db.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,3))", (notification["requestId"],))
            current = self.one(db, "SELECT * FROM irt_compute.compute_executions WHERE id=%s FOR UPDATE", (execution["id"],))
            if current["fencing_token"] != execution["fencing_token"] or current["status"] != "RUNNING":
                raise ServiceError("STALE_EXECUTION")
            request, _ = self.request(db, notification)
            task, _ = self.load_task(db, request)  # Recheck revoked approvals, rubric, and source before any insert.
            # Claim advances PENDING -> RUNNING through the DB trigger. Compare only immutable inputs.
            pinned_task = {**claim["task"], "request": {k: v for k, v in claim["task"]["request"].items() if k != "status"}}
            current_task = {**task, "request": {k: v for k, v in task["request"].items() if k != "status"}}
            if request["status"] != "RUNNING" or current_task != pinned_task:
                raise ServiceError("COMPUTE_INPUT_CHANGED")
            run = self.one(db, """INSERT INTO irt_compute.generation_runs
                (config_id,original_question_version_id,wave_item_id,execution_id,generator_version,random_seed,parameter_values,status)
                VALUES(%s,%s,%s,%s,%s,%s,%s,'RUNNING') RETURNING id""",
                (task["config"]["id"], task["source"]["id"], task["wave"]["id"], execution["id"],
                 GENERATOR_VERSION, str(claim["work"]["seed"]), Jsonb(result["provenance"])))
            candidate = self.one(db, """INSERT INTO irt_compute.generation_candidates
                (generation_run_id,parent_original_question_version_id,payload,random_seed,parameter_values,validation_status)
                VALUES(%s,%s,%s,%s,%s,'CONTENT_VALID') RETURNING id,payload_digest""",
                (run["id"], task["source"]["id"], Jsonb(result["payload"]), str(claim["work"]["seed"]), Jsonb(result["provenance"])))
            self.one(db, """INSERT INTO irt_compute.compute_outputs
                (execution_id,kind,sequence_number,input_digest,digest,payload,scientific_decision)
                VALUES(%s,'GENERATE_VARIANTS',1,%s,'',%s,'CONTENT_VALID') RETURNING id""",
                (execution["id"], request["input_digest"], Jsonb({"candidateIds": [str(candidate["id"])]})))
            db.execute("UPDATE irt_compute.generation_runs SET status='SUCCEEDED',finished_at=clock_timestamp() WHERE id=%s", (run["id"],))
            finished = self.finish(db, execution)
            return self.response(db, notification, finished)
