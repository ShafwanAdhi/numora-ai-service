"""Similarity generator: revision lineage, exact ratios, complete domain, ephemeral HTTP."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import OriginalBank,load_workspace_bank
from config_store import ConfigStore,validate_config
from engine import assemble,build_values,generate
from filters import validate_candidate,signature
from lint import reproduce_original
from drill_11_15_math import check_math

QID='mcma-15-2-8'
DATA=ROOT/'data/drill-1-indicators-11-15'

class Similarity(unittest.TestCase):
    def test_provenance_and_conceptual_questions_unchanged(self):
        bank=OriginalBank(DATA/'q0_bank.csv'); o=bank.get(QID)
        self.assertEqual(o['version'],3)
        self.assertEqual(o['metadata']['generation_status'],'ACTIVE')
        self.assertFalse(o['metadata']['self_adjustment_enabled'])
        self.assertNotIn('BC =',o['stem'])
        history=[json.loads(s) for s in (DATA/'original_revisions.jsonl').read_text(encoding='utf8').splitlines() if json.loads(s)['question_id']==QID]
        self.assertEqual([(r['original_version'],r['replacement_version']) for r in history],[(1,2),(2,3)])
        self.assertIn('BC = 9 cm',history[-1]['original_row']['stem'])
        self.assertEqual(history[-1]['original_metadata']['generation_status'],'HOLD_SOURCE')
        self.assertEqual(sum(bank.get(q)['metadata']['generation_status']=='DEFERRED_CONCEPTUAL' for q in bank.ids()),22)
        self.assertEqual(load_workspace_bank(ROOT/'data/q0_bank.csv').get(QID),o)

    def test_entire_domain_and_corruption(self):
        o=OriginalBank(DATA/'q0_bank.csv').get(QID); cfg,_=ConfigStore(ROOT/'configs').load(QID)
        self.assertEqual(validate_config(cfg,o),[])
        self.assertEqual(reproduce_original(o,cfg),([],[]))
        signatures=set()
        for k in range(31):
            c=assemble(cfg,build_values(cfg,lambda n,s:k)); check_math(QID,c)
            if k:
                self.assertEqual(validate_candidate(c,o,[]),[])
                signatures.add(signature(c['stem'],c['options']))
            for index in range(4):
                bad=deepcopy(c); bad['options'][index]['correct']=not bad['options'][index]['correct']
                with self.assertRaises(AssertionError): check_math(QID,bad)
            for index in (1,3):
                bad=deepcopy(c); bad['options'][index]['text']=bad['options'][index]['text'].replace('kali','999 kali')
                with self.assertRaises(AssertionError): check_math(QID,bad)
            bad=deepcopy(c); bad['explanation']='Skala = 999.'
            with self.assertRaises(AssertionError): check_math(QID,bad)
        self.assertEqual(len(signatures),30)
        self.assertEqual(generate(o,cfg,77,[]).cand,generate(o,cfg,77,[]).cand)

    def test_workbench_without_database_or_persistence(self):
        import webui,tempfile,threading
        from urllib.request import Request,urlopen
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            store=Path(tmp)/'unused.jsonl'
            with webui.make_server(0,store=store) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True); worker.start()
                try:
                    address=f'http://127.0.0.1:{server.server_port}'
                    for seed in (1,777,1):
                        req=Request(address+'/api/generate',data=json.dumps(dict(question_id=QID,seed=seed)).encode(),headers={'Content-Type':'application/json'})
                        with urlopen(req) as response: result=json.load(response)
                        self.assertEqual(result['classification']['source_level'],2)
                        self.assertEqual(result['metadata']['approval_status'],'NOT_CURRICULUM_APPROVED')
                        check_math(QID,dict(stem=result['stem'],explanation=result['explanation'],options=[dict(o,correct=o['id'] in result['key'].split(',')) for o in result['options']]))
                finally: server.shutdown(); worker.join()
            self.assertFalse(store.exists())

if __name__=='__main__': unittest.main()
