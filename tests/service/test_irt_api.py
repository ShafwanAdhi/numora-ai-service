from unittest.mock import Mock
import unittest
from uuid import uuid4
from fastapi.testclient import TestClient
from numora_service.settings import Settings
from numora_service.irt.api import create_app


class IrtApiTests(unittest.TestCase):
    def setUp(self):
        self.repo=Mock()
        self.settings=Settings(enabled=True,token='s'*32,database_url='test',principal_id=str(uuid4()))
        self.client=TestClient(create_app(self.settings,self.repo),raise_server_exceptions=False)
        self.auth={'Authorization':'Bearer '+self.settings.token}
        self.message={'contractVersion':3,'requestId':str(uuid4()),'inputDigest':'a'*64,'dispatchGeneration':1}

    def test_disabled_and_unauthorized(self):
        self.assertEqual(self.client.get('/api/v1/irt/capabilities').status_code,401)
        client=TestClient(create_app(Settings(),self.repo),raise_server_exceptions=False)
        self.assertEqual(client.get('/api/v1/irt/capabilities').status_code,503)
        self.repo.assert_not_called()

    def test_accept_is_async_and_does_not_return_scientific_payload(self):
        self.repo.accept.return_value={'status':'ACCEPTED','requestId':self.message['requestId']}
        result=self.client.post('/api/v1/irt/compute/execute',headers=self.auth,json=self.message)
        self.assertEqual(result.status_code,202)
        self.assertNotIn('respondents',result.json())
        self.repo.accept.assert_called_once_with(self.message)

    def test_malformed_duplicate_and_large_json_rejected(self):
        for body in ['{"requestId":1,"requestId":2}','NaN','x'*17000]:
            result=self.client.post('/api/v1/irt/compute/execute',headers={**self.auth,'Content-Type':'application/json'},content=body)
            self.assertIn(result.status_code,[413,422])
        self.repo.accept.assert_not_called()

    def test_private_database_errors_are_not_returned(self):
        self.repo.accept.side_effect=RuntimeError('password=secret')
        result=self.client.post('/api/v1/irt/compute/execute',headers=self.auth,json=self.message)
        self.assertEqual(result.status_code,500)
        self.assertNotIn('secret',result.text)


if __name__=='__main__':unittest.main()
