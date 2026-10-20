"""Approved source repairs, full rendered-domain checks and reusable conceptual stock."""
import json
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_drill_6_10_level45_batch1 as first

ROOT=first.ROOT
DATA=ROOT/'data/drill-1-indicators-6-10-levels-4-5-batch6'
SELECTION={6:{4:[2,4,8,10],5:[2,4,8,10]},7:{4:[4],5:[8,9]},
           9:{4:[1],5:[1,5,7]},10:{4:[2],5:[9]}}
IDS=[f'{"pg" if n<6 else "mcma" if n<9 else "kategori"}-{i}-{l}-{n}'
     for i,levels in SELECTION.items() for l,ns in levels.items() for n in ns]
STOCK_ID='mcma-7-5-6'

def check_math(qid,c):
    from author_drill_6_10_level45_batch6 import check_math as check
    check(qid,c)

class Batch(first.Batch):
    expected_count=17

    def setUp(self):
        scope=patch.multiple(first,IDS=IDS,SELECTION=SELECTION,DATA=DATA,check_math=check_math)
        scope.start(); self.addCleanup(scope.stop)

    def test_scope_provenance_and_originals(self):
        import hashlib
        from build_drill_6_10_level45_batch1 import entries
        from author_drill_6_10_level45_batch6 import revise,author
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        workspace=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(set(bank.ids()),set(IDS)|{STOCK_ID})
        sources={e['audit_id']:e for e in entries()}
        for qid in IDS:
            o=bank.get(qid); m=o['metadata']; e=sources[m['audit_id']]; r=revise(e)
            self.assertEqual(o,workspace.get(qid))
            self.assertEqual(o['stem'],r['source_projection']['stem'])
            self.assertEqual(m['raw_source_projection'],e.get('source_projection_resolved') or e['source_projection'])
            self.assertEqual(m['source_review']['authorization'],'USER_APPROVED_MINIMUM_LOCAL_REVISION')
            self.assertFalse(m['self_adjustment_enabled'])
            self.assertEqual(m['approval_status'],'NOT_CURRICULUM_APPROVED')
            self.assertEqual(hashlib.sha256((DATA/m['source_document']).read_bytes()).hexdigest(),m['source_document_sha256'])
            cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
            self.assertEqual(cfg,author(r).config(o))

    def test_service_catalog_and_custom_bank(self):
        from numora_service.bridge import catalog
        bank=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        items={r['questionExternalId']:r for r in catalog(bank,first.ConfigStore(ROOT/'configs'))}
        for qid in IDS: self.assertEqual(items[qid]['mode'],'generator')
        self.assertEqual(items[STOCK_ID]['mode'],'stock')
        self.assertEqual(items[STOCK_ID]['stockCount'],3)
        self.assertEqual(set(first.load_workspace_bank(DATA/'q0_bank.csv').ids()),set(IDS)|{STOCK_ID})

    def test_oracle_rejects_wrong_numeric_answers(self):
        import re
        bank=first.OriginalBank(DATA/'q0_bank.csv')
        for qid in IDS:
            cfg,_=first.ConfigStore(ROOT/'configs').load(qid)
            c=first.generate(bank.get(qid),cfg,77,[]).cand
            for index in [j for j,o in enumerate(c['options']) if o['correct']]:
                bad=deepcopy(c)
                bad['options'][index]['text']=re.sub(r'\d[\d.,]*','999',bad['options'][index]['text'],count=1)
                self.assertNotEqual(c,bad,qid)
                with self.assertRaises(AssertionError,msg=qid): check_math(qid,bad)
            bad=deepcopy(c); bad['explanation']='$1+1=999$'
            with self.assertRaises(AssertionError,msg=qid): check_math(qid,bad)

    def test_all_hundred_source_slots_available(self):
        bank=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        slots=[bank.get(f'{"pg" if n<6 else "mcma" if n<9 else "kategori"}-{i}-{l}-{n}')
               for i in range(6,11) for l in (4,5) for n in range(1,11)]
        self.assertEqual(len(slots),100)
        self.assertEqual(sum(o['metadata']['generation_status']=='ACTIVE' for o in slots),99)
        self.assertEqual({o['id'] for o in slots if o['metadata']['generation_status']!='ACTIVE'},{STOCK_ID})
        for i in range(6,11):
            for l in (4,5):
                group=next(g for g in bank.catalog() if g.get('indicator')==i and g.get('source_level')==l and g.get('package_id')=='drill-1')
                self.assertEqual([bank.get(q)['metadata']['source_number'] for q in group['question_ids']],list(range(1,11)))

class Conceptual(unittest.TestCase):
    def test_stock_math_provenance_and_reuse(self):
        from conceptual_stock import load_stock,stock_record
        from author_drill_6_10_level45_batch6 import check_stock
        bank=first.load_workspace_bank(ROOT/'data/q0_bank.csv')
        items=load_stock(ROOT/'data/conceptual_stock.json',bank)[STOCK_ID]
        self.assertEqual(len(items),3)
        self.assertFalse((ROOT/'configs'/STOCK_ID).exists())
        for index in (0,1,2,0):
            r=stock_record(bank.get(STOCK_ID),items[index]); check_stock(r)
            bad=deepcopy(r); bad['key']='A,B'
            with self.assertRaises(AssertionError): check_stock(bad)
            bad=deepcopy(r); bad['options'][2]['text']='Persamaan (iv) merupakan PLSV.'
            with self.assertRaises(AssertionError): check_stock(bad)

    def test_stock_cli_and_workbench_without_writes(self):
        import cli,webui,threading,tempfile,io,contextlib
        from pathlib import Path
        from urllib.request import urlopen
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')):
            store=Path(tmp)/'variants.jsonl'
            for index in (1,2,3,1):
                output=io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(cli.main(['stock',STOCK_ID,'--variant',str(index),'--json','--store',str(store)]),0)
                self.assertEqual(json.loads(output.getvalue())['stock_index'],index)
            with webui.make_server(0,store=store) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True); worker.start()
                try:
                    for index in (1,2,3,1):
                        with urlopen(f'http://127.0.0.1:{server.server_port}/api/question?id={STOCK_ID}&stock_variant={index}') as response:
                            r=json.load(response)
                        self.assertEqual(r['variant_mode'],'stock'); self.assertEqual(r['stock_count'],3)
                        self.assertEqual(r['variant']['stock_index'],index)
                finally: server.shutdown(); worker.join()
            self.assertFalse(store.exists())

if __name__=='__main__': unittest.main()
