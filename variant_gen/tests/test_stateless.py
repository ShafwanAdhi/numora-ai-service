"""Generation returns responses only; never creates a variant store or package file."""
import contextlib
import http.client
import io
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import cli
import webui


class Stateless(unittest.TestCase):
    def test_original_hash_ignores_windows_line_endings(self):
        from bank import load_workspace_bank, original_hash
        original = load_workspace_bank(ROOT / 'data/q0_bank.csv').get('pg-1-1-1')
        windows = dict(original, stem=original['stem'].replace('\r\n', '\n').replace('\n', '\r\n'))
        unix = dict(original, stem=original['stem'].replace('\r\n', '\n'))
        self.assertEqual(original_hash(windows), original_hash(unix))

    def test_cli_repeated_generation_does_not_exhaust_or_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'variants.jsonl'
            results = []
            for _ in range(12):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(cli.main(['gen', 'pg-18-1-5', 's4', '--store', str(path), '--json']), 0)
                results.append(json.loads(output.getvalue()))
            self.assertFalse(path.exists())
            self.assertTrue(all(r['stem'] == results[0]['stem'] for r in results))
            self.assertTrue(all(r['key'] == results[0]['key'] for r in results))

    def test_http_question_package_and_ui_are_stateless(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'variants.jsonl'
            server = webui.make_server(0, store=path)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                def request(method, route, payload=None):
                    connection = http.client.HTTPConnection(*server.server_address, timeout=15)
                    connection.request(method, route, json.dumps(payload) if payload else None,
                                       {'Content-Type': 'application/json'})
                    response = connection.getresponse()
                    raw = response.read().decode()
                    connection.close()
                    return response.status, raw

                payload = {'question_id': 'pg-18-1-5', 'seed': 4}
                for _ in range(12):
                    status, raw = request('POST', '/api/generate', payload)
                    self.assertEqual(status, 200, raw)
                    self.assertTrue(json.loads(raw)['explanation'])
                status, raw = request('GET', '/api/question?id=pg-18-1-5&seed=4')
                self.assertEqual(status, 200)
                self.assertIsNone(json.loads(raw)['variant'])
                self.assertEqual(request('POST', '/api/regen', payload)[0], 404)
                for _ in range(2):
                    status, raw = request('POST', '/api/tryout/generate-package', {'package_id': 'tryout-1', 'seed': 4})
                    self.assertEqual(status, 200, raw)
                    self.assertEqual(len(json.loads(raw)['items']), 30)
                _, html = request('GET', '/')
                self.assertNotIn('id="regen"', html)
                self.assertNotIn('id="version"', html)
                self.assertNotIn('id="export-package"', html)
                self.assertEqual(list(Path(tmp).rglob('*')), [])
            finally:
                server.shutdown()
                thread.join()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
