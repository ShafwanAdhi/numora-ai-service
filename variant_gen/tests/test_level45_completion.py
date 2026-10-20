"""Finish the 100-source scope: 39 live originals and 28 quarantined proposals."""
import sys
import unittest
from pathlib import Path
import csv
import json
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]


class Completion(unittest.TestCase):
    def test_remaining_assets_exist(self):
        self.assertTrue((ROOT/'data/drill-1-indicators-1-5-levels-4-5-batch2/q0_bank.csv').exists(),
                        'The remaining 39 valid originals have not been imported')
        self.assertTrue((ROOT/'drafts/2026-10-20-level45-academic/q0_bank.csv').exists(),
                        'The 28 academic proposals have not been prepared')

    def test_workspace_merges_same_package_level_in_source_order(self):
        from bank import load_workspace_bank, OriginalBank
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for directory, number in [('first', 2), ('second', 1)]:
                folder = Path(tmp)/directory
                folder.mkdir()
                qid = f'pg-1-4-{number}'
                path = folder/'q0_bank.csv'
                with path.open('w',encoding='utf-8',newline='') as f:
                    w = csv.DictWriter(f,fieldnames=['id','format','stem','options_json','key','version'])
                    w.writeheader()
                    w.writerow(dict(id=qid,format='PG',stem=f'Example {number}',options_json='["1","2"]',key='A',version=1))
                (folder/'question_metadata.json').write_text(json.dumps({qid:dict(generation_status='ACTIVE',source_number=number)}))
                (folder/'question_catalog.json').write_text(json.dumps([dict(activity='DRILL',package_id='drill-1',
                    indicator=1,source_level=4,question_ids=[qid])]))
                paths.append(path)
            bank = load_workspace_bank(paths[0], [paths[1]])
            self.assertEqual(len(bank.catalog()), 1)
            self.assertEqual(bank.catalog()[0]['question_ids'], ['pg-1-4-1','pg-1-4-2'])
            self.assertEqual(OriginalBank(paths[0]).catalog()[0]['question_ids'], ['pg-1-4-2'])

    def test_scope_100_live_with_28_immutable_proposal_archives(self):
        self.test_remaining_assets_exist()
        from bank import OriginalBank, load_workspace_bank
        from level45_completion_common import ROOT, LIVE_DATA, DRAFT_DATA, entries, key
        from config_store import ConfigStore, validate_config, ConfigError
        from engine import generate
        live=OriginalBank(LIVE_DATA/'q0_bank.csv')
        held=OriginalBank(DRAFT_DATA/'q0_bank.csv')
        workspace=load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(len(live.ids()),39)
        self.assertEqual(len(held.ids()),28)
        expected={key(e) for e,s in entries()}
        self.assertEqual(set(live.ids())|set(held.ids()),expected)
        self.assertFalse(set(live.ids())&set(held.ids()))
        self.assertTrue(set(held.ids())<=set(workspace.ids()))
        self.assertTrue(set(live.ids())<=set(workspace.ids()))
        families=[g for g in workspace.catalog() if g.get('activity')=='DRILL' and
                  g.get('indicator') in range(1,6) and g.get('source_level') in (4,5)]
        self.assertEqual(len(families),10)
        self.assertEqual(sum(len(g['question_ids']) for g in families),100)
        for g in families:
            numbers=[workspace.get(q)['metadata']['source_number'] for q in g['question_ids']]
            self.assertEqual(numbers,sorted(numbers))
        proposals=json.loads((DRAFT_DATA/'proposed_corrections.json').read_text(encoding='utf-8'))
        self.assertEqual({p['question_id'] for p in proposals},set(held.ids()))
        self.assertEqual(len(proposals),28)
        for proposal in proposals:
            self.assertTrue(proposal['component_changes'])
            self.assertTrue(proposal['rationale'])
            self.assertEqual(proposal['approval_status'],'PROPOSED_NOT_APPROVED')
        for qid in held.ids():
            with self.subTest(qid=qid):
                o=held.get(qid)
                self.assertEqual(o['metadata']['generation_status'],'HOLD_SOURCE')
                self.assertTrue(o['metadata']['review_only'])
                self.assertEqual(o['metadata']['source_original_version'],1)
                self.assertEqual(o['metadata']['proposed_original_version'],2)
                self.assertFalse(o['metadata']['self_adjustment_enabled'])
                self.assertEqual(o['version'],2)
                self.assertEqual(o['metadata']['approval_status'],'PROPOSED_NOT_APPROVED')
                self.assertTrue(ConfigStore(ROOT/'configs').versions(qid))
                self.assertEqual(workspace.get(qid)['metadata']['approval_status'],'USER_APPROVED_CORRECTION')
                cfg,_=ConfigStore(DRAFT_DATA/'configs').load(qid)
                self.assertTrue(validate_config(cfg,o))
                with self.assertRaises(ConfigError):generate(o,cfg,1,[])

    def test_all_67_reproduce_and_all_finite_inputs_have_independent_evidence(self):
        self.test_remaining_assets_exist()
        from copy import deepcopy
        from bank import OriginalBank, load_workspace_bank
        from config_store import ConfigStore, validate_config
        from engine import assemble, build_values, generate
        from filters import validate_candidate, signature
        from lint import reproduce_original
        from expr import RejectDraw
        from level45_completion_common import ROOT, LIVE_DATA, DRAFT_DATA, entries, key
        from build_level45_completion import modules
        workspace=load_workspace_bank(ROOT/'data/q0_bank.csv')
        held=OriginalBank(DRAFT_DATA/'q0_bank.csv')
        for e,status in entries():
            qid=key(e);draft=status=='ACADEMIC_FOLLOW_UP'
            with self.subTest(qid=qid,draft=draft):
                o=held.get(qid) if draft else workspace.get(qid)
                if draft:o['metadata']['generation_status']='ACTIVE'  # Review sandbox only.
                root=DRAFT_DATA/'configs' if draft else ROOT/'configs'
                cfg,_=ConfigStore(root).load(qid)
                self.assertEqual(validate_config(cfg,o),[])
                self.assertEqual(reproduce_original(o,cfg),([],[]))
                _,oracle=modules(e['indicator'])
                spec=cfg['variables']['k']
                inputs=spec['values'] if spec['gen']=='choice' else range(spec['range'][0],spec['range'][1]+1,spec.get('step',1))
                signatures=set();core_math=set()
                for k in inputs:
                    try:values=build_values(cfg,lambda name,spec:k)
                    except RejectDraw:continue
                    candidate=assemble(cfg,values)
                    oracle.check_math(qid,candidate)
                    if not validate_candidate(candidate,o,[]):
                        signatures.add(signature(candidate['stem'],candidate['options']))
                        core_math.add(tuple(re.findall(r'-?\d+(?:[.,]\d+)*',candidate['stem'][:len(o['stem'])])))
                self.assertGreaterEqual(len(signatures),20)
                self.assertGreaterEqual(len(core_math),20,
                    "Actual task data must vary; appended labels do not count")
                made=[]
                for seed in range(1,21):
                    c=generate(o,cfg,seed,made).cand
                    oracle.check_math(qid,c);made.append(c)
                self.assertEqual(len({signature(c['stem'],c['options']) for c in made}),20)
                for seed in range(201,211):
                    a=generate(o,cfg,seed,[]).cand;b=generate(o,cfg,seed,[]).cand
                    self.assertEqual(a,b);oracle.check_math(qid,a)
                c=deepcopy(made[0]);c['options'][0]['correct']=not c['options'][0]['correct']
                with self.assertRaises(AssertionError):oracle.check_math(qid,c)
                c=deepcopy(made[0]);c['explanation']='1+1=999'
                with self.assertRaises(AssertionError):oracle.check_math(qid,c)


    def test_workbench_exposes_39_local_and_28_user_approved_generators(self):
        self.test_remaining_assets_exist()
        import http.client
        import threading
        from unittest.mock import patch
        import webui
        from level45_completion_common import DRAFT_DATA, LIVE_DATA
        from bank import OriginalBank
        from build_level45_completion import modules
        live = OriginalBank(LIVE_DATA/'q0_bank.csv')
        held = OriginalBank(DRAFT_DATA/'q0_bank.csv')
        with tempfile.TemporaryDirectory() as temporary, patch(
                'database.connection', side_effect=AssertionError('Database access forbidden')):
            store = Path(temporary)/'unused.jsonl'
            server = webui.make_server(0, store=store)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            def request(method, path, payload=None):
                connection = http.client.HTTPConnection(*server.server_address, timeout=10)
                connection.request(method, path, json.dumps(payload) if payload else None,
                                   {'Content-Type': 'application/json'})
                response = connection.getresponse()
                status, body = response.status, json.loads(response.read())
                connection.close()
                return status, body
            try:
                status, groups = request('GET', '/api/catalog')
                self.assertEqual(status, 200)
                ids = {q for group in groups for q in group['question_ids']}
                self.assertTrue(set(live.ids()) <= ids)
                self.assertTrue(set(held.ids()) <= ids)
                for qid in live.ids():
                    with self.subTest(qid=qid):
                        status, result = request('POST', '/api/generate',
                                                {'question_id': qid, 'seed': 777})
                        self.assertEqual(status, 200, result)
                        self.assertEqual(result['classification']['package_id'], 'drill-1')
                        self.assertEqual(result['metadata']['approval_status'], 'NOT_CURRICULUM_APPROVED')
                        flags = result['key'].split(',')
                        # HTTP records append an answer recap to the mathematical explanation.
                        explanation, recap=result['explanation'].rsplit('\n\n',1)
                        self.assertTrue(recap.startswith(('Jawaban: ', 'Penilaian pernyataan: ')))
                        candidate = dict(stem=result['stem'], explanation=explanation,
                            options=[dict(option, correct=option['id'] in flags) for option in result['options']])
                        _, oracle = modules(int(qid.split('-')[1]))
                        oracle.check_math(qid, candidate)
                for qid in held.ids():
                    with self.subTest(held=qid):
                        status, body = request('POST', '/api/generate',
                                               {'question_id': qid, 'seed': 777})
                        self.assertEqual(status,200,body)
                        self.assertEqual(body['metadata']['approval_status'],'USER_APPROVED_CORRECTION')
                        flags=body['key'].split(',')
                        explanation,recap=body['explanation'].rsplit('\n\n',1)
                        self.assertTrue(recap.startswith(('Jawaban: ','Penilaian pernyataan: ')))
                        candidate=dict(stem=body['stem'],explanation=explanation,
                            options=[dict(o,correct=o['id'] in flags) for o in body['options']])
                        modules(int(qid.split('-')[1]))[1].check_math(qid,candidate)
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
            self.assertFalse(store.exists())


if __name__ == '__main__':
    unittest.main()
