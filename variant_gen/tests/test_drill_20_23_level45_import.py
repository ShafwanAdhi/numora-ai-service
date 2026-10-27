"""Local source intake: complete structure, evidence, quarantine and HTTP visibility."""
import json
import sys
import tempfile
import threading
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from bank import OriginalBank,load_workspace_bank
from config_store import ConfigStore

DATA=ROOT/'data/drill-1-indicators-20-23-levels-4-5'


class Intake(unittest.TestCase):
    def test_docx_extraction_integrity(self):
        import zipfile,xml.etree.ElementTree as ET
        from import_drill_20_23_level45 import SOURCE
        from audit_original_questions import read,flatten,W
        paragraphs=list(flatten(read(SOURCE/'extracted.json')['blocks']))
        with zipfile.ZipFile(SOURCE/'source.docx') as z:
            native=list(ET.fromstring(z.read('word/document.xml')).iter(W+'p'))
        self.assertEqual(len(native),3064);self.assertEqual(len(paragraphs),len(native))
        for p,n in zip(paragraphs,native):
            self.assertEqual(''.join(p['text'].split()),''.join(''.join(t.text or '' for t in n.iter(W+'t')).split()))

    def test_complete_bank_and_provenance(self):
        self.assertTrue((DATA/'q0_bank.csv').exists(),'80 originals not imported')
        bank=OriginalBank(DATA/'q0_bank.csv');workspace=load_workspace_bank(ROOT/'data/q0_bank.csv')
        self.assertEqual(len(bank.ids()),80)
        self.assertEqual(Counter((bank.get(q)['classification']['indicator'],bank.get(q)['classification']['source_level']) for q in bank.ids()),
                         Counter({(i,l):10 for i in range(20,24) for l in (4,5)}))
        for q in bank.ids():
            o=bank.get(q);m=o['metadata'];self.assertEqual(o,workspace.get(q))
            self.assertEqual(o['classification']['package_id'],'drill-1')
            self.assertEqual(m['source_number'],(o['classification']['source_level']-1)*10+int(q.split('-')[-1]))
            self.assertTrue(m['source_text']);self.assertTrue(m['original_explanation'])
            self.assertEqual(m['approval_status'],'NOT_CURRICULUM_APPROVED')
            self.assertFalse(m['self_adjustment_enabled'])
            self.assertEqual(m['generator_status'],'IMPLEMENTED' if ConfigStore(ROOT/'configs').versions(q) else 'NOT_IMPLEMENTED')
        for i in range(20,24):
            ids=[q for q in workspace.ids() if workspace.get(q)['classification'].get('activity')=='DRILL' and workspace.get(q)['classification'].get('indicator')==i]
            self.assertEqual(len(ids),50)

    def test_extraction_and_source_conflicts(self):
        bank=OriginalBank(DATA/'q0_bank.csv')
        self.assertEqual(len(bank.get('mcma-20-4-6')['options']),5)
        self.assertEqual([p['id'] for p in bank.get('mcma-20-4-7')['options'] if p['correct']],list('ABCD'))
        self.assertIn('| Senin | 80 |',bank.get('kategori-20-4-9')['stem'])
        self.assertIn('| Setuju | 44 |',bank.get('kategori-20-5-10')['stem'])
        self.assertEqual(bank.get('kategori-20-5-9')['metadata']['category_labels'],['Layak','Tidak Layak'])
        self.assertTrue(all('\u2713' not in p['text'] for p in bank.get('kategori-20-5-9')['options']))
        self.assertIn('Rancangan pertanyaan yang paling layak',bank.get('pg-20-5-1')['stem'])
        self.assertNotIn('Rancangan pertanyaan yang paling layak',bank.get('pg-20-5-1')['options'][-1]['text'])
        self.assertTrue(bank.get('mcma-23-4-8')['options'][2]['text'].endswith('siswa B.'))
        for q in ('kategori-21-4-9','kategori-21-4-10','mcma-21-5-6','mcma-21-5-7','pg-22-4-3','mcma-22-4-7','kategori-22-4-9'):
            m=bank.get(q)['metadata'];self.assertEqual(m['generation_status'],'ACTIVE')
        o=bank.get('pg-22-4-3');self.assertFalse(o['options'][0]['correct']);self.assertTrue(o['options'][3]['correct'])
        audit=json.loads((DATA/'audit.json').read_text(encoding='utf8'))
        self.assertEqual(len(audit['entries']),80)
        for e in audit['entries']:
            o=bank.get(e['question_id']);p=e['source_projection']
            if o['metadata'].get('source_review_status')=='AUDITED_CURRICULUM_REVISION':
                revisions=[json.loads(t) for t in (DATA/'original_revisions.jsonl').read_text(encoding='utf8').splitlines()]
                historical=next(r for r in revisions if r['question_id']==e['question_id'])['original_row']
                self.assertEqual(historical['stem'],p['stem'])
                self.assertEqual(json.loads(historical['options_json']),p['options'])
                self.assertEqual(historical['key'].split(','),p['key'])
                self.assertTrue(e['independent_reasoning'])
                continue
            self.assertEqual(o['stem'],p['stem']);self.assertEqual([x['text'] for x in o['options']],p['options'])
            self.assertEqual([x['id'] for x in o['options'] if x['correct']],p['key'])
            self.assertTrue(e['independent_reasoning'])
            self.assertEqual(o['metadata']['generation_status'],'HOLD_SOURCE' if e['issues'] else 'ACTIVE')
        self.assertEqual(audit['counts'],dict(originals=80,active=67,hold=13,generators_added=0,stocks_added=0))
        for q in ('pg-23-4-5','mcma-23-4-7','pg-23-5-3','pg-23-5-4','mcma-23-5-7','mcma-23-5-8'):
            self.assertEqual(bank.get(q)['metadata']['generation_status'],'ACTIVE')

    def test_repeatable_import_refuses_changed_outputs(self):
        import import_drill_20_23_level45 as importer
        import contextlib,io,hashlib
        self.assertEqual(hashlib.sha256((importer.SOURCE/'source.docx').read_bytes()).hexdigest(),importer.SOURCE_HASH)
        files=importer.build()
        for path,text in files.items():
            if path.name=='question_metadata.json':
                current=json.loads(path.read_text(encoding='utf8'))
                for revision in (json.loads(t) for t in (DATA/'original_revisions.jsonl').read_text(encoding='utf8').splitlines()):
                    current[revision['question_id']]=revision['original_metadata']
                for item in current.values():
                    item['generator_status']='NOT_IMPLEMENTED'
                    item.pop('generator_family_kind',None)
                    item.pop('generator_audit',None)
                self.assertEqual(current,json.loads(text))
            else:self.assertEqual(path.read_bytes(),text.encode('utf8'))
        with tempfile.TemporaryDirectory() as tmp,patch.object(importer,'DATA',Path(tmp)/'bank'),contextlib.redirect_stdout(io.StringIO()):
            importer.main();before={p:p.read_bytes() for p in importer.DATA.iterdir()}
            importer.main();self.assertEqual(before,{p:p.read_bytes() for p in importer.DATA.iterdir()})
            target=importer.DATA/'question_metadata.json';target.write_bytes(b'local edit')
            edited={p:p.read_bytes() for p in importer.DATA.iterdir()}
            with self.assertRaisesRegex(ValueError,'Refusing overwrite'):importer.main()
            self.assertEqual(edited,{p:p.read_bytes() for p in importer.DATA.iterdir()})

    def test_http_originals_without_database_or_runtime_storage(self):
        import webui
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')) as db:
            store=Path(tmp)/'unused.jsonl'
            with webui.make_server(0,store=store) as server:
                worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
                try:
                    for q in OriginalBank(DATA/'q0_bank.csv').ids():
                        with urlopen(f'http://127.0.0.1:{server.server_port}/api/question?id={q}') as response:r=json.load(response)
                        self.assertEqual(r['original']['question_id'],q)
                        self.assertEqual(r['variant_mode'],'generator' if ConfigStore(ROOT/'configs').versions(q) else 'unavailable')
                        self.assertIsNone(r['variant'])
                        if OriginalBank(DATA/'q0_bank.csv').get(q)['metadata']['generation_status']=='HOLD_SOURCE':
                            req=Request(f'http://127.0.0.1:{server.server_port}/api/generate',data=json.dumps(dict(question_id=q,seed=1)).encode(),headers={'Content-Type':'application/json'})
                            with self.assertRaises(HTTPError) as error:urlopen(req)
                            self.assertEqual(error.exception.code,400)
                finally:server.shutdown();worker.join(timeout=3)
            self.assertFalse(store.exists());db.assert_not_called()


if __name__=='__main__':unittest.main()
