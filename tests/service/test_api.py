import unittest
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient

from numora_service.api import create_app
from numora_service.errors import ServiceError
from numora_service.settings import Settings


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.repo = Mock()
        self.settings = Settings(enabled=True, token="t" * 32, database_url="test", principal_id=str(uuid4()))
        self.client = TestClient(create_app(self.settings, self.repo), raise_server_exceptions=False)
        self.auth = {"Authorization": "Bearer " + self.settings.token}
        self.notification = {"contractVersion": 3, "requestId": str(uuid4()), "inputDigest": "a" * 64, "dispatchGeneration": 1}

    def test_health_auth_disabled(self):
        self.assertEqual(self.client.get("/health/live").status_code, 200)
        self.assertEqual(self.client.get("/health/ready").status_code, 401)
        disabled = TestClient(create_app(Settings(), self.repo))
        self.assertEqual(disabled.get("/api/v1/generators").json()["code"], "GENERATOR_DISABLED")

    def test_readiness_and_catalog(self):
        self.assertEqual(self.client.get("/health/ready", headers=self.auth).status_code, 200)
        items = self.client.get("/api/v1/generators", headers=self.auth).json()["items"]
        import csv
        from pathlib import Path
        root=Path(__file__).resolve().parents[2]/'variant_gen/data'
        expected=set()
        for path in root.rglob('q0_bank.csv'):
            with path.open(encoding='utf-8-sig',newline='') as file:
                expected.update(row['id'] for row in csv.DictReader(file))
        self.assertEqual({item['questionExternalId'] for item in items},expected)
        self.assertTrue({i["mode"] for i in items} <= {"generator", "stock", "held", "unavailable"})
        self.assertIn("generator", {i["mode"] for i in items})

    def test_level45_all_100_generators_include_the_user_approved_corrections(self):
        import csv
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        def ids(path):
            with path.open(encoding='utf-8-sig', newline='') as file:
                return {row['id'] for row in csv.DictReader(file)}
        local = ids(root/'variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch1/q0_bank.csv')
        local |= ids(root/'variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch2/q0_bank.csv')
        drafts = ids(root/'variant_gen/drafts/2026-10-20-level45-academic/q0_bank.csv')
        approved=ids(root/'variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/q0_bank.csv')
        self.assertEqual(approved,drafts)
        local |= approved
        self.assertEqual(len(local),100)
        self.assertEqual(len(drafts),28)
        items = self.client.get('/api/v1/generators',headers=self.auth).json()['items']
        catalog = {item['questionExternalId']:item for item in items}
        self.assertTrue(drafts <= catalog.keys())
        for question_id in approved:
            self.assertEqual(catalog[question_id]['originalVersion'],2)
        for question_id in local:
            with self.subTest(question_id=question_id):
                self.assertEqual(catalog[question_id]['mode'],'generator')
                self.assertEqual(catalog[question_id]['classification']['package_id'],'drill-1')

    def test_execute_replay_and_running(self):
        for status, http_status in (("RUNNING", 202), ("SUCCEEDED", 200), ("FAILED", 200), ("EXPIRED", 200)):
            self.repo.claim.return_value = {"response": {"status": status, "executionId": str(uuid4())}}
            r = self.client.post("/api/v1/compute/execute", headers=self.auth, json=self.notification)
            self.assertEqual(r.status_code, http_status)
            self.assertEqual(r.json()["status"], status)

    def test_boundary_errors_are_sanitized(self):
        route = "/api/v1/compute/execute"
        self.assertEqual(self.client.post(route, json=self.notification).status_code, 401)
        self.assertEqual(self.client.post(route, json={**self.notification, "config": {}}, headers=self.auth).status_code, 422)
        self.assertEqual(self.client.post(route, content=b"x" * 16385, headers=self.auth).status_code, 413)
        self.assertEqual(self.client.post(route, content="{}", headers=self.auth).status_code, 415)
        duplicate = '{"contractVersion":3,"contractVersion":3}'
        self.assertEqual(self.client.post(route, content=duplicate, headers={**self.auth,"Content-Type":"application/json"}).json()["code"], "INVALID_JSON")
        self.repo.claim.side_effect = ServiceError("COMPUTE_DATABASE_ERROR", 503)
        response = self.client.post(route, json=self.notification, headers=self.auth)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["content-type"], "application/problem+json")
        self.repo.claim.side_effect = RuntimeError("secret credential")
        response = self.client.post(route, json=self.notification, headers=self.auth)
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("secret", response.text)
