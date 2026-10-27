"""Local HTTP compatibility and mode contracts for Tryout plus Drill images."""
import base64
import hashlib
import http.client
import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cli
import webui


class ImageModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=webui.make_server(0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.thread.join();cls.server.server_close()
    def request(self,method,path,data=None,origin=None):
        c=http.client.HTTPConnection(*self.server.server_address,timeout=30)
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        c.request(method,path,json.dumps(data) if data is not None else None,headers)
        r=c.getresponse();raw=r.read();status=r.status;c.close()
        return status,json.loads(raw)

    def test_catalog_has_five_tryout_nine_drill_and_explicit_modes(self):
        status,rows=self.request('GET','/api/image-variants')
        self.assertEqual(status,200)
        self.assertEqual(len(rows),14)
        self.assertEqual(sum(r['activity']=='TRYOUT' for r in rows),5)
        self.assertEqual(sum(r['activity']=='DRILL' for r in rows),9)
        conceptual=next(r for r in rows if r['id']=='mcma-16-4-7')
        self.assertEqual(conceptual['modes'],['original','stock'])
        self.assertEqual(len(conceptual['stocks']),2)

    def test_legacy_tryout_request_and_explicit_original(self):
        payload={'question_id':'tryout-1-b3-q02','seed':7}
        status,data=self.request('POST','/api/image-variants/generate',payload)
        self.assertEqual(status,200,data);self.assertEqual(data['mode'],'generator')
        before=cli.preview(self.server.bank,self.server.configs,payload['question_id'],7)
        for key in ('stem','options','key','explanation','values_used','draws_used'):
            self.assertEqual(data['record'][key],before[key])
        with patch('cli.generate',side_effect=AssertionError('No original draw')):
            status,data=self.request('POST','/api/image-variants/generate',{'question_id':payload['question_id'],'mode':'original'})
        self.assertEqual(status,200,data);self.assertEqual(data['record']['seed'],0)

    def test_numeric_drill_modes_return_valid_png_and_same_record(self):
        for mode,extras in [('generator',{'seed':7}),('original',{})]:
            status,data=self.request('POST','/api/image-variants/generate',{'question_id':'pg-16-5-5','mode':mode,**extras})
            self.assertEqual(status,200,data)
            png=base64.b64decode(data['image']['base64'],validate=True)
            self.assertEqual(hashlib.sha256(png).hexdigest(),data['image']['sha256'])
            self.assertEqual(data['record']['key'],'C' if mode=='generator' else 'D')

    def test_every_conceptual_original_and_stock_is_available(self):
        _,rows=self.request('GET','/api/image-variants')
        count=0
        for row in rows:
            if row.get('modes')!=['original','stock']:continue
            for item in [None,*row['stocks']]:
                payload={'question_id':row['id'],'mode':'stock' if item else 'original'}
                if item:payload['stock_variant_id']=item['variant_id']
                status,data=self.request('POST','/api/image-variants/generate',payload)
                self.assertEqual(status,200,data)
                self.assertEqual(data['record']['variant_id'] if item else None,item['variant_id'] if item else None)
                count+=1
        self.assertEqual(count,12)

    def test_invalid_combinations_and_cross_origin_are_rejected(self):
        for payload in [
            {'question_id':'pg-16-4-2','mode':'generator','seed':1},
            {'question_id':'pg-16-4-1','mode':'stock','stock_variant_id':'pg-16-4-2:stock-01'},
            {'question_id':'pg-16-4-2','mode':'stock','stock_variant_id':'mcma-16-4-7:stock-01'},
            {'question_id':'pg-16-4-2','mode':'stock','stock_variant_id':'pg-16-4-2:stock-01','seed':1},
            {'question_id':'pg-16-4-1','mode':'generator','seed':True},
            {'question_id':'tryout-1-b3-q02','seed':0},
            {'question_id':'../x','mode':'original'}]:
            self.assertEqual(self.request('POST','/api/image-variants/generate',payload)[0],400,payload)
        self.assertEqual(self.request('POST','/api/image-variants/generate',{'question_id':'pg-16-4-1','seed':1},'https://example.com')[0],403)

    def test_original_mode_for_all_five_tryout_images_uses_no_rng(self):
        for qid in webui.IMAGE_IDS:
            with self.subTest(qid=qid),patch('cli.generate',side_effect=AssertionError('No original RNG')):
                status,data=self.request('POST','/api/image-variants/generate',{'question_id':qid,'mode':'original','seed':0})
                self.assertEqual(status,200,data)
                self.assertEqual(data['record']['original_hash'],self.server.bank.get(qid)['hash'])

    def test_conceptual_image_does_not_enable_general_generator(self):
        with patch('cli.generate',side_effect=AssertionError('Conceptual generator stays disabled')):
            status,data=self.request('POST','/api/generate',{'question_id':'pg-16-4-2','seed':7})
            self.assertEqual(status,400,data)


if __name__=='__main__':unittest.main()
