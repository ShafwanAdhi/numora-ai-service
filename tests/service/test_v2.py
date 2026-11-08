"""Local bank coverage, no database/approval/storage writes."""
import copy
from pathlib import Path
import unittest
from uuid import UUID
from numora_service.bridge import workspace, original_record
from numora_service.content import record_content
from numora_service.errors import ServiceError
from numora_service.v2_generate import generate_result, media_profile, stocks
from numora_service.v2_content import validate_payload, local_record

class V2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,cls.configs=workspace()
        cls.stocks=stocks(cls.bank)

    def work(self,qid):
        original=self.bank.get(qid)
        content=record_content(local_record(original_record(original)))
        source={'id':UUID(int=1),'family_id':UUID(int=2),'kind':'ORIGINAL',
                'question_type':content['questionType'],'stem':content['stem'],
                'options_or_statements':content['optionsOrStatements'],'answer_key':content['answerKey'],
                'explanation':{'text':'TEST ONLY canonical source'},'media':[],
                'difficulty':'MEDIUM','scoring_rubric_version_id':UUID(int=3)}
        return {'serviceContract':'generator-service-v2','original':original,'source':source,
                'mediaProfile':media_profile(qid)}

    def test_all_1094_numeric_and_all_verified_stocks(self):
        numeric=stock_count=stock_families=0
        for qid in self.bank.ids():
            with self.subTest(qid=qid):
                work=self.work(qid)
                if qid in self.stocks:
                    stock_families+=1
                    for item in self.stocks[qid]:
                        result=generate_result({**work,'mode':'CONCEPTUAL_STOCK','stockItem':item,
                          'stockSetId':str(UUID(int=4)),'stockSetDigest':'a'*64,
                          'reservation':{'id':str(UUID(int=5)),'reused':False,'cycle':1}})
                        validate_payload(result['payload'])
                        self.assertNotIn('seed',result['provenance'])
                        self.assertNotIn('configVersion',result['provenance'])
                        stock_count+=1
                else:
                    cfg,_=self.configs.load(qid)
                    result=generate_result({**work,'mode':'NUMERIC','config':cfg,'seed':42})
                    validate_payload(result['payload'])
                    numeric+=1
        self.assertEqual((numeric,stock_families),(1094,86))
        self.assertGreaterEqual(stock_count,172)

    def test_contracts_are_identical_in_both_repos(self):
        root=Path(__file__).resolve().parents[2]
        main=root.parent/'Numora/packages/contracts/generator-service-v2'
        for file in (root/'contracts/generator-service-v2').rglob('*.json'):
            relative=file.relative_to(root/'contracts/generator-service-v2')
            self.assertEqual(file.read_bytes(),(main/relative).read_bytes(),str(relative))

    def test_media_tampering_and_replay(self):
        qid='pg-16-4-1'
        cfg,_=self.configs.load(qid)
        work={**self.work(qid),'mode':'NUMERIC','config':cfg,'seed':42}
        a=generate_result(work);b=generate_result(work)
        self.assertEqual(a,b)
        altered=copy.deepcopy(a['payload']);altered['media'][0]['sha256']='b'*64
        with self.assertRaises(ServiceError):validate_payload(altered)
        wrong=copy.deepcopy(work);wrong['mediaProfile']['renderer']['python']='0.0.0'
        with self.assertRaises(ServiceError):generate_result(wrong)

    def test_v2_catalog_requires_explicit_flag_and_no_fake_stock_config(self):
        from fastapi.testclient import TestClient
        from numora_service.api import create_app
        from numora_service.settings import Settings
        token='test-only-v2-token-with-at-least-32-characters'
        settings=dict(enabled=True,token=token,principal_id=str(UUID(int=1)),database_url='postgresql://unused@127.0.0.1/unused')
        headers={'Authorization':'Bearer '+token}
        with TestClient(create_app(Settings(**settings))) as client:
            self.assertEqual(client.get('/api/v2/generators',headers=headers).status_code,503)
        with TestClient(create_app(Settings(**settings,v2_enabled=True))) as client:
            self.assertEqual(client.get('/api/v2/generators').status_code,401)
            response=client.get('/api/v2/generators',headers=headers)
            self.assertEqual(response.status_code,200)
            rows=response.json()['items']
            stock=[r for r in rows if r['mode']=='CONCEPTUAL_STOCK']
            self.assertEqual(len(stock),86)
            self.assertEqual(sum(r['mode']=='NUMERIC' for r in rows),1094)
            for item in stock:
                self.assertFalse({'seed','configVersion','configHash','config'} & set(item))

if __name__=='__main__':unittest.main()
