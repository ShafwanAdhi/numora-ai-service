"""27 numeric families: source reproduction, full domains, adversarial checks and HTTP."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import load_workspace_bank
from config_store import ConfigStore,validate_config
from engine import assemble,build_values,generate
from filters import signature,validate_candidate
from lint import reproduce_original


class Batch(unittest.TestCase):
    def test_generators_exist(self):
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv');store=ConfigStore(ROOT/'configs')
        from author_drill_20_23_level45_batch1 import selected
        ids=[e['question_id'] for e in selected()]
        self.assertEqual(len(ids),27)
        self.assertEqual([q for q in ids if not store.versions(q)],[])

    def test_full_domain_and_mutations(self):
        from author_drill_20_23_level45_batch1 import selected
        from oracle_drill_20_23_level45_batch1 import check_math
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv');store=ConfigStore(ROOT/'configs')
        self.assertEqual(len(selected()),27)
        for e in selected():
            q=e['question_id']
            with self.subTest(question=q):
                o=bank.get(q);self.assertEqual(o['metadata']['generation_status'],'ACTIVE')
                cfg,_=store.load(q);self.assertEqual(validate_config(cfg,o),[])
                self.assertEqual(reproduce_original(o,cfg),([],[]))
                unique=set()
                for k in range(31):
                    c=assemble(cfg,build_values(cfg,lambda name,spec:k));check_math(q,c)
                    if k:
                        self.assertEqual(validate_candidate(c,o,[]),[]);unique.add(signature(c['stem'],c['options']))
                self.assertEqual(len(unique),30)
                prior=[]
                for seed in range(10):
                    c=generate(o,cfg,seed,prior).cand;check_math(q,c);prior.append(c)
                self.assertEqual(c,generate(o,cfg,9,prior[:-1]).cand)
                for index in range(len(c['options'])):
                    bad=deepcopy(c);bad['options'][index]['correct']=not bad['options'][index]['correct']
                    with self.assertRaises(AssertionError):check_math(q,bad)
                bad=deepcopy(c);bad['explanation']='Hasil = 999999.'
                with self.assertRaises(AssertionError):check_math(q,bad)
                import re
                bad=deepcopy(c)
                index=next(i for i,p in enumerate(c['options']) if p['correct'] and re.search(r'\d',p['text']))
                bad['options'][index]['text']=re.sub(r'\d+(?:\.\d{3})*(?:,\d+)?','999999',bad['options'][index]['text'],count=1)
                with self.assertRaises(AssertionError):check_math(q,bad)

    def test_http_without_database_or_persistence(self):
        from author_drill_20_23_level45_batch1 import selected
        from oracle_drill_20_23_level45_batch1 import check_math
        import webui,tempfile,threading
        from unittest.mock import patch
        from urllib.request import Request,urlopen
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')) as db:
            path=Path(tmp)/'unused.jsonl'
            with webui.make_server(0,store=path) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
                try:
                    for e in selected():
                        req=Request(f'http://127.0.0.1:{server.server_port}/api/generate',data=json.dumps(dict(question_id=e['question_id'],seed=11)).encode(),headers={'Content-Type':'application/json'})
                        with urlopen(req) as response:r=json.load(response)
                        c=dict(stem=r['stem'],explanation=r['explanation'],options=[dict(p,correct=p['id'] in r['key'].split(',')) for p in r['options']])
                        check_math(e['question_id'],c)
                finally:server.shutdown();worker.join(timeout=3)
            self.assertFalse(path.exists());db.assert_not_called()


if __name__=='__main__':unittest.main()
