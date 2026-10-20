"""27 numeric generators: complete domains, rendered mathematics and HTTP without persistence."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT),str(Path(__file__).parent)]
from bank import load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from filters import validate_candidate, signature
from lint import reproduce_original

SELECTION = {16:{5:[4,10]},17:{4:[1,2,3,4,5],5:[2,4,5]},
             18:{4:[1,2,4,5,6],5:[1,2,4,5]},19:{4:[1,2,3,4,6],5:[1,3,4]}}


class Batch(unittest.TestCase):
    def test_domain_and_math(self):
        from author_drill_16_19_level45_batch1 import selected, check_math
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(len(selected()),27)
        for e in selected():
            q=e['question_id']
            with self.subTest(q=q):
                o=bank.get(q);cfg,_=ConfigStore(ROOT/'configs').load(q)
                self.assertEqual(validate_config(cfg,o),[])
                self.assertEqual(reproduce_original(o,cfg),([],[]))
                unique=set()
                for k in range(31):
                    c=assemble(cfg,build_values(cfg,lambda name,spec:k))
                    check_math(q,c)
                    if k:
                        self.assertEqual(validate_candidate(c,o,[]),[])
                        unique.add(signature(c['stem'],c['options']))
                self.assertEqual(len(unique),30)
                prior=[]
                for seed in range(10):
                    result=generate(o,cfg,seed,prior)
                    check_math(q,result.cand)
                    self.assertEqual(validate_candidate(result.cand,o,prior),[])
                    prior.append(result.cand)
                c=generate(o,cfg,77,[]).cand
                self.assertEqual(c,generate(o,cfg,77,[]).cand)
                check_math(q,c)
                for idx in range(4):
                    bad=deepcopy(c);bad['options'][idx]['correct']=not bad['options'][idx]['correct']
                    with self.assertRaises(AssertionError):check_math(q,bad)
                bad=deepcopy(c);bad['explanation']='Jawaban: 999999.'
                with self.assertRaises(AssertionError):check_math(q,bad)
                import re
                bad=deepcopy(c);idx=next(i for i,o in enumerate(bad['options']) if o['correct'])
                bad['options'][idx]['text']=re.sub(r'\d+(?:\.\d{3})*(?:,\d+)?', '999999',bad['options'][idx]['text'],count=1)
                with self.assertRaises(AssertionError):check_math(q,bad)

    def test_http_no_storage(self):
        from author_drill_16_19_level45_batch1 import selected,check_math
        import webui,tempfile,threading
        from unittest.mock import patch
        from urllib.request import Request,urlopen
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            path=Path(tmp)/'unused.jsonl'
            with webui.make_server(0,store=path) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
                try:
                    for e in selected():
                        req=Request(f'http://127.0.0.1:{server.server_port}/api/generate',
                            data=json.dumps(dict(question_id=e['question_id'],seed=11)).encode(),
                            headers={'Content-Type':'application/json'})
                        with urlopen(req) as response:r=json.load(response)
                        candidate=dict(stem=r['stem'],explanation=r['explanation'],
                            options=[dict(o,correct=o['id'] in r['key'].split(',')) for o in r['options']])
                        check_math(e['question_id'],candidate)
                finally:server.shutdown();worker.join(timeout=3)
            self.assertFalse(path.exists())


if __name__=='__main__':unittest.main()
