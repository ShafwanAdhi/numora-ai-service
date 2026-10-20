"""Finish 80 originals without losing raw source, finite stock or mathematical checks."""
import json
import sys
import unittest
from pathlib import Path
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import OriginalBank,load_workspace_bank
from conceptual_stock import load_stock
from config_store import ConfigStore,validate_config
from engine import assemble,build_values,generate
from lint import reproduce_original
from filters import validate_candidate,signature


class Completion(unittest.TestCase):
    def test_complete_source_and_stock(self):
        from complete_drill_16_19_level45 import DATA,CONCEPTS
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv');local=OriginalBank(DATA/'q0_bank.csv')
        stock=load_stock(ROOT/'data/conceptual_stock.json',bank);configs=ConfigStore(ROOT/'configs')
        self.assertEqual(len(local.ids()),80)
        self.assertEqual(sum(bool(configs.versions(q)) for q in local.ids()),65)
        self.assertEqual(sum(bool(stock.get(q)) for q in local.ids()),15)
        self.assertEqual(sum(len(stock.get(q,[])) for q in local.ids()),30)
        for q in local.ids():
            o=local.get(q);self.assertNotEqual(o['metadata']['generation_status'],'HOLD_SOURCE')
            self.assertEqual(o,bank.get(q));self.assertEqual(bool(stock.get(q)),q in CONCEPTS)
        revisions=[json.loads(s) for s in (DATA/'original_revisions.jsonl').read_text(encoding='utf8').splitlines()]
        self.assertEqual(len(revisions),14)
        self.assertEqual(len({r['question_id'] for r in revisions}),14)
        for r in revisions:
            self.assertEqual((r['original_version'],r['replacement_version']),(1,2))
            self.assertEqual(local.get(r['question_id'])['version'],2)
            self.assertEqual(r['original_metadata']['generation_status'],'HOLD_SOURCE')
            self.assertEqual(r['original_metadata']['source_text'],local.get(r['question_id'])['metadata']['source_text'])

    def test_all_remaining_numeric_domains(self):
        from complete_drill_16_19_level45 import numeric_entries,check_math,DATA
        bank=OriginalBank(DATA/'q0_bank.csv');self.assertEqual(len(numeric_entries()),38)
        for e in numeric_entries():
            q=e['question_id']
            with self.subTest(q=q):
                o=bank.get(q);cfg,_=ConfigStore(ROOT/'configs').load(q)
                self.assertEqual(validate_config(cfg,o),[]);self.assertEqual(reproduce_original(o,cfg),([],[]))
                unique=set()
                for k in range(31):
                    c=assemble(cfg,build_values(cfg,lambda name,spec:k));check_math(q,c)
                    if k:
                        self.assertEqual(validate_candidate(c,o,[]),[])
                        unique.add(signature(c['stem'],c['options']))
                self.assertEqual(len(unique),30)
                prior=[]
                for seed in range(10):
                    c=generate(o,cfg,seed,prior).cand;check_math(q,c);prior.append(c)
                for index in range(4):
                    bad=deepcopy(c);bad['options'][index]['correct']=not bad['options'][index]['correct']
                    with self.assertRaises(AssertionError):check_math(q,bad)
                bad=deepcopy(c);bad['explanation']='Hasil = 999999999.'
                with self.assertRaises(AssertionError):check_math(q,bad)
                import re
                bad=deepcopy(c)
                index=next(i for i,o in enumerate(bad['options']) if o['correct'] and re.search(r'\d',o['text']))
                bad['options'][index]['text']=re.sub(r'\d+(?:\.\d{3})*(?:,\d+)?','999999',bad['options'][index]['text'],count=1)
                with self.assertRaises(AssertionError):check_math(q,bad)

    def test_http_numeric_and_reusable_stock_without_persistence(self):
        from complete_drill_16_19_level45 import numeric_entries,check_math,CONCEPTS
        import webui,tempfile,threading
        from unittest.mock import patch
        from urllib.request import Request,urlopen
        from urllib.error import HTTPError
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')) as db:
            path=Path(tmp)/'unused.jsonl'
            with webui.make_server(0,store=path) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
                base=f'http://127.0.0.1:{server.server_port}'
                try:
                    for e in numeric_entries():
                        req=Request(base+'/api/generate',data=json.dumps(dict(question_id=e['question_id'],seed=11)).encode(),
                                    headers={'Content-Type':'application/json'})
                        with urlopen(req) as response:r=json.load(response)
                        c=dict(stem=r['stem'],explanation=r['explanation'],
                               options=[dict(o,correct=o['id'] in r['key'].split(',')) for o in r['options']])
                        check_math(e['question_id'],c)
                    for q in sorted(CONCEPTS):
                        records=[]
                        for index in (1,2,1):
                            with urlopen(base+f'/api/question?id={q}&stock_variant={index}') as response:r=json.load(response)
                            self.assertEqual(r['variant_mode'],'stock')
                            self.assertEqual(len(r['stock_variants']),2)
                            records.append(r['variant'])
                        self.assertEqual(records[0],records[2]);self.assertNotEqual(records[0],records[1])
                    with self.assertRaises(HTTPError) as error:
                        urlopen(base+'/api/question?id=pg-16-4-2&stock_variant=3')
                    self.assertEqual(error.exception.code,400)
                finally:server.shutdown();worker.join(timeout=3)
            self.assertFalse(path.exists());db.assert_not_called()


if __name__=='__main__':unittest.main()
