"""Local UI checks: python -B -m unittest discover -s tests."""
import http.client
import json
import shutil
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
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

    def test_database_routes_validate_and_keep_local_bank_available(self):
        with patch.dict('os.environ', {'DATABASE_URL': ''}):
            status, result = self.request('GET', '/api/database/status')
            self.assertEqual(status, 503)
            self.assertIn('DATABASE_URL', result['error'])
            for path in ('package?id=bad', 'family?id=bad', 'packages?limit=0',
                         'packages?offset=-1', 'packages?type=INVALID', 'packages?limit=1&limit=2'):
                status, _ = self.request('GET', '/api/database/' + path)
                self.assertEqual(status, 400)
            status, _ = self.request('POST', '/api/database/package', {'id': 'anything'})
            self.assertEqual(status, 405)
            self.assertEqual(self.request('GET', '/api/questions')[0], 200)

    def test_database_http_returns_package_envelope(self):
        import database
        with patch('database.package', return_value={'package': {'name': 'Kosong'}, 'items': [],
                                                    'total': 0, 'limit': 100, 'offset': 0}) as read:
            status, result = self.request('GET', '/api/database/package?id=00000000-0000-0000-0000-000000000001')
            self.assertEqual(status, 200)
            self.assertEqual(result['items'], [])
            read.assert_called_once_with('00000000-0000-0000-0000-000000000001', 100, 0)

    def test_original_and_missing_config_are_readable_without_generating(self):
        from bank import OriginalBank
        status, questions = self.request("GET", "/api/questions")
        self.assertEqual(status, 200)
        self.assertEqual(len(questions), sum(len(OriginalBank(p).ids()) for p in (ROOT/'data').rglob('q0_bank.csv')))
        self.assertEqual({q['classification']['activity'] for q in questions}, {'DRILL','TRYOUT'})
        self.assertEqual({q['classification']['package_id'] for q in questions}, {'drill-1','tryout-1'})
        status, catalog = self.request('GET', '/api/catalog')
        self.assertEqual(status, 200)
        self.assertEqual(len(catalog), sum(len(json.loads(p.read_text(encoding='utf8'))) for p in (ROOT/'data').rglob('question_catalog.json')))
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
        self.assertEqual(first['classification'], dict(activity='DRILL', indicator=18,
                         source_level=3, package_id='drill-1'))
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
        from bank import OriginalBank
        self.assertEqual(len(json.loads(response.read())), sum(len(OriginalBank(p).ids()) for p in (ROOT/'data').rglob('q0_bank.csv')))

    def test_drill_20_23_local_lifecycle_and_hold_guards(self):
        with patch('database.connection',side_effect=AssertionError('Database must not be touched')):
            status, questions = self.request('GET','/api/questions')
            self.assertEqual(status,200)
            self.assertEqual({q['classification']['indicator'] for q in questions if q['classification']['activity']=='DRILL'},set(range(6,24)))
            status, catalog = self.request('GET','/api/catalog')
            groups=[g for g in catalog if g.get('indicator') in range(20,24)]
            self.assertEqual(len(groups),20)
            self.assertEqual(sum(not g['question_ids'] for g in groups),8)
            payload={'question_id':'pg-21-1-1','seed':11}
            status, first=self.request('POST','/api/generate',payload)
            self.assertEqual(status,200)
            saved=self.store.read_bytes()
            self.assertEqual(self.request('POST','/api/generate',payload),(200,first))
            self.assertEqual(self.store.read_bytes(),saved)
            status,second=self.request('POST','/api/regen',dict(payload,reason='review local'))
            self.assertEqual(status,200)
            self.assertEqual(second['variant_ver'],2)
            self.assertEqual(second['replacement_of'],1)
            self.assertEqual(self.request('GET','/api/question?id=pg-21-1-1&seed=11&version=1')[1]['variant'],first)
            status,data=self.request('GET','/api/question?id=pg-21-1-1&seed=11')
            before=self.store.read_bytes()
            self.assertTrue(self.request('POST','/api/lint',{'question_id':payload['question_id'],'config':data['config']})[1]['ok'])
            self.assertEqual(self.store.read_bytes(),before)
            draft={'question_id':payload['question_id'],'config':data['config'],'base_version':1,'base_hash':data['config_hash']}
            self.assertEqual(self.request('POST','/api/config',draft)[0],200)
            self.assertEqual(self.request('POST','/api/config',draft)[0],409)
            for qid in ['pg-20-3-3','pg-23-1-2','kategori-20-1-9']:
                status,data=self.request('GET','/api/question?id='+qid+'&seed=1')
                self.assertEqual(status,200)
                self.assertTrue(data['original']['explanation'])
                if qid=='kategori-20-1-9':
                    self.assertEqual(data['original']['answer_categories']['2'],'Kualitatif')
                # Forge a config file in the temporary folder; status must still win.
                forged=json.loads((ROOT/'configs/pg-21-1-1/v1.json').read_text(encoding='utf8'))
                forged['question_id']=qid
                directory=self.configs/qid;directory.mkdir(exist_ok=True)
                (directory/'v1.json').write_text(json.dumps(forged),encoding='utf8')
                for route in ['generate','regen','config','lint']:
                    status,result=self.request('POST','/api/'+route,{'question_id':qid,'seed':1,'reason':'test','config':forged,'base_version':0,'base_hash':None})
                    self.assertEqual(status,400,(route,result))
            self.assertEqual(self.store.read_bytes(),before)

    def test_drill_6_10_local_lifecycle_and_hold(self):
        with patch('database.connection', side_effect=AssertionError('Database must not be touched')):
            status, catalog = self.request('GET', '/api/catalog')
            self.assertEqual(status, 200)
            groups = [g for g in catalog if g.get('indicator') in range(6, 11)]
            self.assertEqual(len(groups), 25)
            self.assertEqual(sum(not g['question_ids'] for g in groups), 10)
            for qid in ['pg-6-1-1', 'mcma-8-1-6', 'kategori-10-1-9']:
                payload = {'question_id': qid, 'seed': 11}
                status, first = self.request('POST', '/api/generate', payload)
                self.assertEqual(status, 200, first)
                saved = self.store.read_bytes()
                self.assertEqual(self.request('POST', '/api/generate', payload), (200, first))
                self.assertEqual(self.store.read_bytes(), saved)
                status, second = self.request('POST', '/api/regen', dict(payload, reason='test history'))
                self.assertEqual(status, 200, second)
                self.assertEqual(second['replacement_of'], 1)
                status, historical = self.request('GET', f'/api/question?id={qid}&seed=11&version=1')
                self.assertEqual(historical['variant'], first)
                self.assertEqual(len(historical['history']), 2)
                if first['format'] == 'KATEGORI':
                    self.assertEqual([o['id'] for o in first['options']], ['1', '2', '3'])
                    self.assertEqual(first['key'], historical['original']['key'])
                config_path = self.configs / qid / 'v1.json'
                changed = json.loads(config_path.read_text(encoding='utf8'))
                changed['explanation'] += ' Edited in place.'
                config_path.write_text(json.dumps(changed), encoding='utf8')
                self.assertEqual(self.request('POST', '/api/regen', dict(payload, reason='stale'))[0], 400)
            before = self.store.read_bytes()
            for qid in ['pg-6-1-5', 'pg-7-1-2', 'mcma-6-1-6', 'pg-9-3-2']:
                status, data = self.request('GET', f'/api/question?id={qid}&seed=11')
                self.assertEqual(status, 200)
                if qid in ['pg-6-1-5', 'pg-7-1-2']:
                    self.assertEqual(data['original']['key'], '')
                    self.assertFalse(any(o.get('correct', False) for o in data['original']['options']))
                forged = json.loads((ROOT/'configs/pg-6-1-1/v1.json').read_text(encoding='utf8'))
                forged['question_id'] = qid
                directory = self.configs / qid
                directory.mkdir(exist_ok=True)
                (directory/'v1.json').write_text(json.dumps(forged), encoding='utf8')
                for route in ['generate', 'regen', 'config', 'lint']:
                    status, result = self.request('POST', '/api/'+route, dict(question_id=qid, seed=11,
                        reason='test', config=forged, base_version=0, base_hash=None))
                    self.assertEqual(status, 400, (route, result))
            self.assertEqual(self.store.read_bytes(), before)

    def test_drill_11_15_lifecycle_and_all_levels(self):
        with patch('database.connection',side_effect=AssertionError('local generation must not touch DB')):
            status,catalog=self.request('GET','/api/catalog')
            self.assertEqual(status,200)
            groups=[g for g in catalog if g.get('indicator') in range(11,16)]
            self.assertEqual(len(groups),25)
            self.assertEqual({len(g['question_ids']) for g in groups},{10})
            payload=dict(question_id='pg-11-1-4',seed=11)
            status,first=self.request('POST','/api/generate',payload)
            self.assertEqual(status,200)
            saved=self.store.read_bytes()
            self.assertEqual(self.request('POST','/api/generate',payload),(200,first))
            self.assertEqual(self.store.read_bytes(),saved)
            self.assertEqual(self.request('POST','/api/regen',payload)[0],400)
            status,second=self.request('POST','/api/regen',dict(payload,reason='local math review'))
            self.assertEqual(status,200)
            self.assertEqual(second['variant_ver'],2)
            self.assertEqual(self.request('GET','/api/question?id=pg-11-1-4&seed=11&version=1')[1]['variant'],first)
            status,data=self.request('GET','/api/question?id=pg-11-1-4&seed=11')
            draft=dict(question_id=payload['question_id'],config=data['config'],base_version=1,base_hash=data['config_hash'])
            self.assertEqual(self.request('POST','/api/config',draft)[0],200)
            self.assertEqual(self.request('POST','/api/config',draft)[0],409)
            for qid in ('mcma-11-1-7','pg-11-2-4','kategori-11-3-9','mcma-15-2-8','pg-15-4-2','pg-11-1-1'):
                status,data=self.request('GET','/api/question?id='+qid+'&seed=1')
                self.assertEqual(status,200)
                self.assertTrue(data['original']['metadata']['reason'])
                for route in ('generate','regen','lint','config'):
                    self.assertEqual(self.request('POST','/api/'+route,dict(question_id=qid,seed=1,config={},reason='review'))[0],400)


    def test_tryout_end_to_end_never_queries_database(self):
        with patch('database.connection',side_effect=AssertionError('Database must not be touched')):
            status, data=self.request('GET','/api/question?id=tryout-1-b2-q04&seed=5')
            self.assertEqual(status,200)
            self.assertEqual(data['original']['classification']['chapter'],2)
            self.assertEqual(data['original']['key'],'C')
            status, result=self.request('POST','/api/tryout/generate-package',dict(package_id='tryout-1',seed=5))
            self.assertEqual(status,200)
            self.assertEqual(len(result['items']),30)
            saved=self.store.read_bytes()
            status, same=self.request('POST','/api/tryout/generate-package',dict(package_id='tryout-1',seed=5))
            self.assertEqual(result,same);self.assertEqual(self.store.read_bytes(),saved)
            for route in ['generate','regen','config','lint']:
                status,_=self.request('POST','/api/'+route,dict(question_id='tryout-1-b4-q02',seed=5,config={}))
                self.assertEqual(status,400)
            self.assertEqual(self.store.read_bytes(),saved)
            for payload in [dict(package_id='../outside',seed=1),dict(package_id='tryout-1',seed=0),dict(package_id='tryout-1',seed=True)]:
                status,_=self.request('POST','/api/tryout/generate-package',payload)
                self.assertEqual(status,400)

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
