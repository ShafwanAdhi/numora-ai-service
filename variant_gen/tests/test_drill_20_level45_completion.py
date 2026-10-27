"""The 13 remaining indicator-20 originals must become usable without source revisions."""
import sys
import unittest
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from bank import load_workspace_bank
from config_store import ConfigStore,validate_config
from lint import reproduce_original
from engine import generate

IDS={'pg-20-4-1','pg-20-4-4','pg-20-4-5','mcma-20-4-6','mcma-20-4-8','kategori-20-4-10',
     'pg-20-5-1','pg-20-5-2','pg-20-5-3','pg-20-5-4','mcma-20-5-6','mcma-20-5-8','kategori-20-5-9'}


class Indicator20Completion(unittest.TestCase):
    def test_all_thirteen_configs_exist_and_keep_originals(self):
        b=load_workspace_bank(ROOT/'data/q0_bank.csv');s=ConfigStore(ROOT/'configs')
        self.assertEqual([qid for qid in sorted(IDS) if not s.versions(qid)],[])
        for qid in IDS:
            o=b.get(qid);cfg,_=s.load(qid)
            self.assertEqual(validate_config(cfg,o),[])
            self.assertEqual(reproduce_original(o,cfg),([],[]))
            self.assertEqual(o['version'],1)
            self.assertEqual(o['classification']['package_id'],'drill-1')
            self.assertEqual(o['metadata']['source_number'],int(qid.split('-')[-1])+(30 if qid.split('-')[2]=='4' else 40))

    def test_service_catalog_has_all_twenty_level45_generators(self):
        from numora_service.bridge import workspace,catalog
        b,s=workspace()
        items=[i for i in catalog(b,s) if (i.get('classification') or {}).get('indicator')==20 and i['classification']['source_level'] in (4,5)]
        self.assertEqual(len(items),20)
        self.assertEqual({i['mode'] for i in items},{'generator'})
        self.assertTrue(IDS<={i['questionExternalId'] for i in items})

    def test_sources_previous_configs_and_unrelated_metadata_are_preserved(self):
        from build_drill_20_level45_completion import REPORT,REPO,METADATA
        self.assertTrue((REPORT/'prior-assets-baseline.json').exists())
        baseline=json.loads((REPORT/'prior-assets-baseline.json').read_text(encoding='utf-8'))
        for name,digest in baseline['files'].items():
            if name!=METADATA.relative_to(REPO).as_posix():
                path=REPO/name;content=path.read_bytes()
                if path.name=='original_revisions.jsonl':
                    content=b''.join(line for line in content.splitlines(keepends=True)
                                     if 'Revisi final kurikulum22 Oktober2026' not in line.decode('utf8'))
                elif path.name=='question_metadata.json' and path.with_name('original_revisions.jsonl').exists():
                    metadata=json.loads(content);changed=False
                    for line in path.with_name('original_revisions.jsonl').read_text(encoding='utf8').splitlines():
                        revision=json.loads(line)
                        if revision['reason'].startswith('Revisi final kurikulum22 Oktober2026'):
                            metadata[revision['question_id']]=revision['original_metadata'];changed=True
                    if changed:content=(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n').encode('utf8')
                normalized=content.replace(b'\r\n',b'\n')
                self.assertIn(digest,{hashlib.sha256(content).hexdigest(),
                                      hashlib.sha256(normalized).hexdigest(),
                                      hashlib.sha256(normalized.replace(b'\n',b'\r\n')).hexdigest()},name)
        current=json.loads(METADATA.read_text(encoding='utf-8'))
        for line in METADATA.with_name('original_revisions.jsonl').read_text(encoding='utf8').splitlines():
            revision=json.loads(line)
            current[revision['question_id']]=revision['original_metadata']
        for qid,old in baseline['source_metadata'].items():
            new=dict(current[qid])
            if qid in IDS:
                self.assertEqual(new.pop('generator_status'),'IMPLEMENTED')
                new.pop('generator_family_kind');new.pop('generator_audit')
                old=dict(old);old.pop('generator_status')
            self.assertEqual(new,old,qid)

    def test_http_generation_for_all_13_without_database_or_persistence(self):
        import http.client
        import tempfile
        import threading
        from unittest.mock import patch
        import webui
        from author_drill_20_level45_numeric import IDS as NUMERIC
        from oracle_drill_20_level45_numeric import check_math as numeric
        from oracle_drill_20_level45_conceptual import check_math as conceptual
        with tempfile.TemporaryDirectory() as temporary,patch('database.connection',side_effect=AssertionError('No DB')) as db:
            path=Path(temporary)/'unused.jsonl'
            server=webui.make_server(0,store=path)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                for qid in IDS:
                    with self.subTest(qid=qid):
                        connection=http.client.HTTPConnection(*server.server_address,timeout=10)
                        connection.request('POST','/api/generate',json.dumps(dict(question_id=qid,seed=201)),{'Content-Type':'application/json'})
                        response=connection.getresponse();body=json.loads(response.read());connection.close()
                        self.assertEqual(response.status,200,body)
                        self.assertEqual(body['classification']['package_id'],'drill-1')
                        self.assertEqual(body['metadata']['approval_status'],'NOT_CURRICULUM_APPROVED')
                        self.assertFalse(body['metadata']['self_adjustment_enabled'])
                        flags=body['key'].split(',')
                        explanation,recap=body['explanation'].rsplit('\n\n',1)
                        self.assertTrue(recap.startswith(('Jawaban: ','Penilaian pernyataan: ')))
                        c=dict(stem=body['stem'],explanation=explanation,options=[dict(p,correct=p['id'] in flags) for p in body['options']])
                        (numeric if qid in NUMERIC else conceptual)(qid,c)
            finally:
                server.shutdown();thread.join();server.server_close()
            self.assertFalse(path.exists());db.assert_not_called()


if __name__=='__main__':unittest.main()
