import copy
import json
import multiprocessing
import unittest
from pathlib import Path
from uuid import uuid4

from numora_service.bridge import config_hash, original_record, workspace
from numora_service.content import canonical, fingerprint, payload, record_content
from numora_service.contracts import validate_notification, validate_payload
from numora_service.errors import ServiceError
from numora_service.executor import generate_result, run_process
from numora_service.settings import Settings
from numora_service.task import validate_mapping


def source_for(original):
    content = record_content(original_record(original))
    return {"id": str(uuid4()), "family_id": str(uuid4()), "kind": "ORIGINAL", "question_type": content["questionType"],
            "stem": content["stem"], "options_or_statements": content["optionsOrStatements"], "answer_key": content["answerKey"],
            "explanation": {"text": "TEST source explanation"}, "media": [], "difficulty": "MEDIUM",
            "scoring_rubric_version_id": str(uuid4()), "content_status": "DRAFT", "validation_state": "DRAFT"}


class ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank, cls.configs = workspace()

    def work(self, qid="pg-6-1-1"):
        orig = self.bank.get(qid)
        cfg, _ = self.configs.load(qid)
        return {"original": orig, "config": cfg, "seed": 5, "source": source_for(orig)}

    def test_three_formats_and_determinism(self):
        for qid in ("pg-6-1-1", "mcma-16-1-7", "kategori-16-1-10"):
            with self.subTest(qid=qid):
                work = self.work(qid)
                first = generate_result(work)
                self.assertEqual(first, generate_result(work))
                validate_payload(first["payload"])
                self.assertEqual(first["payload"]["rubricVersionId"], work["source"]["scoring_rubric_version_id"])

    def test_category_preserves_custom_labels_and_ids(self):
        work = self.work("kategori-16-1-10")
        work["original"].setdefault("metadata", {})["category_labels"] = ["Sesuai", "Tidak Sesuai"]
        rec = original_record(work["original"])
        cats = [{"id": "yes", "label": "Sesuai"}, {"id": "no", "label": "Tidak Sesuai"}]
        content = record_content(rec, cats)
        self.assertEqual(content["optionsOrStatements"]["categories"], cats)
        self.assertEqual(set(content["answerKey"]["categoryByStatementId"].values()), {"yes", "no"})

    def test_latex_and_windows_newlines(self):
        work = self.work()
        rec = {"format": "PG", "stem": r"Hitung \(x^2\)" + "\r\nbaris", "options": [{"id": "A", "text": "1"}, {"id": "B", "text": "2"}],
               "key": "B", "explanation": r"\[x=2\]"}
        result = payload(rec, work["source"])
        self.assertEqual(result["stem"]["text"], r"Hitung \(x^2\)" + "\nbaris")
        self.assertEqual(result["explanation"]["text"], rec["explanation"])

    def test_media_and_invalid_answers_fail(self):
        work = self.work()
        work["source"]["media"] = [{"assetId": "image"}]
        with self.assertRaisesRegex(ServiceError, "MEDIA_NOT_SUPPORTED"):
            generate_result(work)
        candidate = generate_result(self.work())["payload"]
        candidate["answerKey"] = {"optionId": "foreign"}
        with self.assertRaises(ServiceError):
            validate_payload(candidate)
        candidate = generate_result(self.work())["payload"]
        candidate["stem"]["text"] = '<img src="media">'
        with self.assertRaisesRegex(ServiceError,"MEDIA_NOT_SUPPORTED"):
            validate_payload(candidate)

    def test_notification_rejects_injected_inputs(self):
        n = {"contractVersion": 3, "requestId": str(uuid4()), "inputDigest": "a"*64, "dispatchGeneration": 1}
        validate_notification(n)
        for key, value in (("seed", 42), ("dispatchGeneration", True), ("dispatchGeneration", 1.0), ("requestId", "00000000-0000-0000-0000-000000000000")):
            with self.assertRaises(ServiceError):
                validate_notification({**n, key: value})

    def test_mapping_exact_content_and_config(self):
        work = self.work()
        orig, cfg, source = (work[k] for k in ("original", "config", "source"))
        context = str(uuid4())
        p = {"serviceContract": "generator-service-v1", "questionExternalId": orig["id"],
             "originalVersion": orig["version"], "originalHash": orig["hash"], "parentQuestionVersionId": source["id"],
             "familyId": source["family_id"], "rubricVersionId": source["scoring_rubric_version_id"], "contextId": context,
             "sourceFingerprint": fingerprint(record_content(original_record(orig))), "configVersion": cfg["config_version"],
             "configHash": config_hash(cfg), "config": cfg}
        self.assertEqual(validate_mapping(p, orig, source, context), cfg)
        for field in ("originalHash", "configHash", "sourceFingerprint"):
            with self.assertRaises(ServiceError):
                validate_mapping({**p, field: "wrong"}, orig, source, context)
        changed = copy.deepcopy(source)
        changed["stem"]["text"] += " changed"
        with self.assertRaises(ServiceError):
            validate_mapping(p, orig, changed, context)

    def test_spawn_and_timeout_cleanup(self):
        work = self.work()
        self.assertEqual(run_process(work, lambda: None, Settings()), generate_result(work))
        with self.assertRaisesRegex(ServiceError, "GENERATION_TIMEOUT"):
            run_process(work, lambda: None, Settings(execution_seconds=0.001))
        def failed_heartbeat():
            raise ServiceError("COMPUTE_DATABASE_ERROR", 503)
        existing = {p.pid for p in multiprocessing.active_children()}
        with self.assertRaisesRegex(ServiceError, "COMPUTE_DATABASE_ERROR"):
            run_process(work, failed_heartbeat, Settings(heartbeat_seconds=0.001))
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, existing)

    def test_cross_language_fixtures(self):
        path = Path(__file__).resolve().parents[2] / "contracts/generator-service-v1/fingerprints.fixture.json"
        for f in json.loads(path.read_text(encoding="utf-8")):
            self.assertEqual(canonical(f["input"]), f["canonical"])
            self.assertEqual(fingerprint(f["input"]), f["sha256"])

    def test_candidate_contract_fixtures(self):
        path = Path(__file__).resolve().parents[2] / "contracts/generator-service-v1/candidates.fixture.json"
        fixtures = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(fixtures), 4)
        for f in fixtures:
            validate_payload(f["payload"])
        for number in (1.5, 9007199254740992):
            with self.assertRaisesRegex(ServiceError, "NON_CANONICAL_NUMBER"):
                canonical(number)
