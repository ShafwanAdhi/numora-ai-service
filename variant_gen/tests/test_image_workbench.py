import base64, hashlib, http.client, json, sys, threading, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import webui, cli

class ImageWorkbench(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=webui.make_server(0)
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.thread.join();cls.server.server_close()
 def request(self,route,payload=None,origin=None):
  c=http.client.HTTPConnection(*self.server.server_address,timeout=30)
  headers={'Content-Type':'application/json'}
  if origin:headers['Origin']=origin
  c.request('POST' if payload is not None else 'GET',route,json.dumps(payload) if payload is not None else None,headers)
  r=c.getresponse();status=r.status;raw=r.read();c.close();return status,raw
 def test_page_and_catalog(self):
  status,raw=self.request('/image-variants');self.assertEqual(status,200);self.assertIn(b'Unduh PNG',raw)
  status,raw=self.request('/api/image-variants');self.assertEqual(status,200)
  self.assertEqual(sum(row['activity']=='TRYOUT' for row in json.loads(raw)),5)
 def test_render_all_same_accepted_result(self):
  for qid in sorted(webui.IMAGE_IDS):
   with self.subTest(qid=qid),patch('cli.generate',wraps=cli.generate) as generate:
    status,raw=self.request('/api/image-variants/generate',{'question_id':qid,'seed':7})
    self.assertEqual(status,200,raw);self.assertEqual(generate.call_count,1)
    result=json.loads(raw);png=base64.b64decode(result['image']['base64'],validate=True)
    self.assertTrue(png.startswith(b'\x89PNG'));self.assertEqual(hashlib.sha256(png).hexdigest(),result['image']['sha256'])
    expected=cli.preview(self.server.bank,self.server.configs,qid,7)
    for key in ('stem','options','key','explanation','values_used','config_hash'):
     self.assertEqual(result['record'][key],expected[key])
 def test_reject_invalid_and_cross_origin(self):
  for payload in ({'question_id':'../x','seed':1},{'question_id':'tryout-1-b3-q02','seed':True},{'question_id':'tryout-1-b3-q02','seed':0}):
   self.assertEqual(self.request('/api/image-variants/generate',payload)[0],400)
  self.assertEqual(self.request('/api/image-variants/generate',{'question_id':'tryout-1-b3-q02','seed':1},'https://example.com')[0],403)
