"""Local UI checks: python -B -m unittest discover -s tests."""
import http.client
import json
import shutil
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class WebUI(unittest.TestCase):
    def setUp(self):
        import webui
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.configs = self.directory / "configs"
        shutil.copytree(ROOT / "configs", self.configs)
        self.store = self.directory / "variants.jsonl"
        self.server = webui.make_server(0, configs=self.configs, store=self.store)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def request(self, method, path, payload=None, headers=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=10)
        body = json.dumps(payload) if payload is not None else None
        connection.request(method, path, body, headers or {"Content-Type": "application/json"})
        response = connection.getresponse()
        raw = response.read()
        connection.close()
        return response.status, json.loads(raw)

    def question(self, seed=3):
        status, data = self.request("GET", f"/api/question?id=pg-18-3-1&seed={seed}")
        self.assertEqual(status, 200)
        return data

    def test_original_and_missing_config_are_readable_without_generating(self):
        status, questions = self.request("GET", "/api/questions")
        self.assertEqual(status, 200)
        self.assertEqual(len(questions), 120)
        status, data = self.request("GET", "/api/question?id=pg-16-1-1&seed=1")
        self.assertEqual(status, 200)
        self.assertEqual(data["original"]["seed"], 0)
        self.assertIsNone(data["variant"])
        self.assertIsNone(data["config"])
        self.assertFalse(self.store.exists())

    def test_generate_is_idempotent_and_regen_preserves_history(self):
        payload = {"question_id": "pg-18-3-1", "seed": 3}
        status, first = self.request("POST", "/api/generate", payload)
        self.assertEqual(status, 200)
        self.assertEqual(first["variant_ver"], 1)
        saved = self.store.read_bytes()
        status, same = self.request("POST", "/api/generate", payload)
        self.assertEqual(status, 200)
        self.assertEqual(same, first)
        self.assertEqual(self.store.read_bytes(), saved)
        status, error = self.request("POST", "/api/regen", payload)
        self.assertEqual(status, 400)
        self.assertIn("reason", error["error"])
        self.assertEqual(self.store.read_bytes(), saved)
        status, second = self.request("POST", "/api/regen", dict(payload, reason="review angka"))
        self.assertEqual(status, 200)
        self.assertEqual(second["variant_ver"], 2)
        self.assertTrue(self.store.read_bytes().startswith(saved))
        status, historical = self.request("GET", "/api/question?id=pg-18-3-1&seed=3&version=1")
        self.assertEqual(status, 200)
        self.assertEqual(historical["variant"], first)
        self.assertEqual(len(historical["history"]), 2)

    def test_config_save_versions_validates_and_rejects_stale_editor(self):
        data = self.question()
        cfg = data["config"]
        previous = (self.configs / "pg-18-3-1" / "v1.json").read_bytes()
        payload = {"question_id": "pg-18-3-1", "config": cfg,
                   "base_version": 1, "base_hash": data["config_hash"]}
        invalid = dict(cfg, stem="original berubah")
        status, _ = self.request("POST", "/api/config", dict(payload, config=invalid))
        self.assertEqual(status, 400)
        self.assertFalse((self.configs / "pg-18-3-1" / "v2.json").exists())
        cfg["variables"]["r1"]["range"] = [3, 15]
        status, result = self.request("POST", "/api/config", payload)
        self.assertEqual(status, 200)
        self.assertEqual(result["config_version"], 2)
        self.assertEqual((self.configs / "pg-18-3-1" / "v1.json").read_bytes(), previous)
        saved = (self.configs / "pg-18-3-1" / "v2.json").read_bytes()
        status, _ = self.request("POST", "/api/config", payload)
        self.assertEqual(status, 409)
        self.assertEqual((self.configs / "pg-18-3-1" / "v2.json").read_bytes(), saved)
        self.assertFalse((self.configs / "pg-18-3-1" / "v3.json").exists())

    def test_lint_draft_never_writes(self):
        data = self.question()
        status, result = self.request("POST", "/api/lint",
                                      {"question_id": "pg-18-3-1", "config": data["config"]})
        self.assertEqual(status, 200)
        self.assertTrue(result["ok"])
        self.assertFalse(self.store.exists())
        self.assertEqual(len(list((self.configs / "pg-18-3-1").glob("*.json"))), 1)

    def test_invalid_steps_and_unicode_never_leave_a_config_file(self):
        data = self.question()
        for field, value in (("step", 0), ("filters", ["step0"]), ("note", "\ud800")):
            cfg = json.loads(json.dumps(data["config"]))
            if field == "note":
                cfg[field] = value
            else:
                cfg["variables"]["r1"][field] = value
            with self.subTest(field=field):
                status, result = self.request("POST", "/api/config", {
                    "question_id": "pg-18-3-1", "config": cfg,
                    "base_version": 1, "base_hash": data["config_hash"]})
                self.assertEqual(status, 400)
                self.assertIn("error", result)
                self.assertFalse((self.configs / "pg-18-3-1" / "v2.json").exists())
        self.assertEqual(self.question()["latest_config_version"], 1)

    def test_idle_browser_connection_does_not_block_subsequent_requests(self):
        idle = socket.create_connection(self.server.server_address, timeout=3)
        self.addCleanup(idle.close)
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=3)
        self.addCleanup(connection.close)
        connection.request("GET", "/api/questions")
        response = connection.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(len(json.loads(response.read())), 120)

    def test_invalid_inputs_and_cross_origin_writes_are_rejected(self):
        cases = (
            ({"question_id": "../outside", "seed": 1}, None),
            ({"question_id": "pg-18-3-1", "seed": 0}, None),
            ({"question_id": "pg-18-3-1", "seed": True}, None),
            ([], None),
            ({"question_id": "pg-18-3-1", "seed": 1},
             {"Content-Type": "application/json", "Origin": "https://evil.example"}),
            ({"question_id": "pg-18-3-1", "seed": 1}, {"Content-Type": "text/plain"}),
        )
        for payload, headers in cases:
            with self.subTest(payload=payload, headers=headers):
                status, result = self.request("POST", "/api/generate", payload, headers)
                self.assertIn(status, (400, 403, 415))
                self.assertIn("error", result)
        status, _ = self.request("POST", "/api/config", {"question_id": "pg-18-3-1", "config": []})
        self.assertEqual(status, 400)
        status, _ = self.request("GET", "/api/questions", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)
        self.assertFalse(self.store.exists())


if __name__ == "__main__":
    unittest.main()
