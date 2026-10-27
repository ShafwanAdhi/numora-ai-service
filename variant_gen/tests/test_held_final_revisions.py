"""Final held revisions: reproduction, exact arithmetic and stateless delivery."""
import re
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from bank import load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import assemble, build_values, generate
from lint import reproduce_original
from filters import signature, validate_candidate

KEYS = {'pg-1-2-1':'D', 'pg-5-3-3':'B', 'mcma-6-3-7':'ABC',
        'kategori-21-4-9':'1234', 'kategori-21-4-10':'4', 'mcma-21-5-6':'ABCD',
        'mcma-21-5-7':'ABE', 'pg-22-4-3':'D', 'mcma-22-4-7':'ABD',
        'kategori-22-4-9':'13', 'pg-23-4-5':'C', 'mcma-23-4-7':'ABC',
        'pg-23-5-3':'C', 'pg-23-5-4':'C', 'mcma-23-5-7':'ABC', 'mcma-23-5-8':'ABC'}


def numbers(text):
    return [F(x.replace('.', '').replace(',', '.')) for x in
            re.findall(r'(?<!\w)(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?', text)]


def check_math(q, c):
    """Independent computations from rendered data, not generator expressions."""
    key = ''.join(o['id'] for o in c['options'] if o['correct'])
    assert key == KEYS[q], (q, key)
    stem, opts = c['stem'], [o['text'] for o in c['options']]
    if q == 'pg-1-2-1':
        losses = [F(x.replace(',', '.')) for x in re.findall(r'-\s*(\d+(?:,\d+)?)%', stem)]
        if len(losses)==4: assert losses[3] == max(losses)
        else:
            assert '-(3)/(5)' in stem and '-0,62' in stem
            assert F(62,100)>max(F(3,5),F(55,100),F(58,100))
    elif q == 'pg-5-3-3':
        a,t,b,u = numbers(stem)
        assert b/u-a/t == numbers(opts[1])[0]
        assert [numbers(option)[0]==b/u-a/t for option in opts]==[o['correct'] for o in c['options']]
    elif q == 'mcma-6-3-7':
        a,t,b,u = numbers(stem)
        together,days = numbers(opts[1]); elapsed,added,left = numbers(opts[2])
        assert a*t == b*u and (a*t+b*u)/together == days
        assert (a*t-a*elapsed)/(a+added) == left
    elif q.startswith(('kategori-21','mcma-21','pg-22','mcma-22','kategori-22')):
        data = numbers(stem)
        if q == 'kategori-21-4-9':
            assert len(data)==5
            expected=[sum(data)/5,sorted(data)[2],max(set(data),key=data.count),max(data)-min(data)]
            assert [numbers(t)[0] for t in opts] == expected
        elif q == 'mcma-21-5-6':
            assert numbers(opts[0])[0] == sorted(data)[2]
            assert numbers(opts[1])[0] == sum(data)/5
            assert numbers(opts[2])[0] == max(data)-min(data)
            assert len(set(data))==5 and data[-1]>sum(data[:-1])/4
        else:
            assert len(data)==10, (q,data)
            a,b=data[:5],data[5:]
            assert sum(a)==sum(b)
            ra,rb=max(a)-min(a),max(b)-min(b)
            ma,mb=sorted(a)[2],sorted(b)[2]
            if q == 'kategori-21-4-10': truth=[sum(a)>sum(b),ma==mb,rb>ra,ra>rb]
            elif q == 'mcma-21-5-7':
                modes={x for x in a if a.count(x)==max(map(a.count,a))}
                truth=[ma==mb,set(numbers(opts[1]))==modes,sum(a)>sum(b),rb<ra,ra==rb]
            elif q == 'pg-22-4-3':
                assert 'lebih rendah' in opts[2]
                truth=[ma==mb and ra==rb,ra<rb,mb<ma,sum(a)==sum(b)]
            elif q == 'mcma-22-4-7': truth=[sum(a)==sum(b),ma==mb,ra>rb,ra==0,len(set(b))<5]
            elif q == 'kategori-22-4-9': truth=[ma==mb,sum(a)>sum(b),ra>rb,len(set(a))<5 and len(set(b))<5]
            assert truth==[o['correct'] for o in c['options']],q
    elif q == 'pg-23-4-5':
        total,count = numbers(stem)[:2]
        assert count/total > F(1,2) and numbers(opts[2])[0]==F(1,2)
    elif q == 'mcma-23-4-7':
        total,a,b = numbers(stem)
        assert a+b==total and a>b
        # Repeating decimals are displayed as exact fractions on generated cases.
        if '/' in opts[0]: assert F(opts[0].split('adalah ')[1].rstrip('.').replace('.',''))==a/total
        if '/' in opts[1]: assert F(opts[1].split('adalah ')[1].rstrip('.').replace('.',''))==b/total
    elif q == 'pg-23-5-3':
        n=int(numbers(stem)[0]) if numbers(stem) else 2
        option = opts[2]
        assert F(option.replace('.','').replace(',', '.')) == F(n,2**n)
    elif q == 'pg-23-5-4':
        total,count=numbers(stem)[:2]
        assert count/total>F(1,2) and numbers(opts[2])[0]==F(1,2)
    elif q == 'mcma-23-5-7':
        total,a,b=numbers(stem)
        assert a+b==total and a/total==numbers(opts[0])[0] and b/total==numbers(opts[1])[0]
    elif q == 'mcma-23-5-8':
        red,blue,total,count=numbers(stem)[:4]
        assert red/(red+blue)==numbers(opts[0])[0]
        assert count/total==numbers(opts[1])[0]
        assert (total-count)/total==numbers(opts[2])[0]
        assert red/(red+blue)!=count/total and count<total/2
    assert c['explanation'].strip()


class HeldRevisions(unittest.TestCase):
    def test_http_is_stateless_and_sources_match_provenance(self):
        import hashlib,json,tempfile,threading
        from unittest.mock import patch
        from urllib.request import Request,urlopen
        import webui
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        with tempfile.TemporaryDirectory() as tmp,patch('database.connection',side_effect=AssertionError('No DB')) as db:
            store=Path(tmp)/'unused.jsonl'
            with webui.make_server(0,store=store) as server:
                thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                try:
                    for q in KEYS:
                        o=bank.get(q);m=o['metadata']
                        self.assertEqual(hashlib.sha256((ROOT.parent/m['source_document']).read_bytes()).hexdigest(),m['source_document_sha256'])
                        for _ in range(2):
                            request=Request(f'http://127.0.0.1:{server.server_port}/api/generate',
                                            data=json.dumps(dict(question_id=q,seed=11)).encode(),headers={'Content-Type':'application/json'})
                            with urlopen(request) as response:record=json.load(response)
                            c=dict(stem=record['stem'],explanation=record['explanation'],options=[dict(p,correct=p['id'] in record['key'].split(',')) for p in record['options']])
                            check_math(q,c)
                finally:server.shutdown();thread.join(timeout=3)
            self.assertFalse(store.exists());db.assert_not_called()

    def test_all_sixteen_and_full_domains(self):
        from copy import deepcopy
        bank=load_workspace_bank(ROOT/'data/q0_bank.csv');store=ConfigStore(ROOT/'configs')
        for q in KEYS:
            with self.subTest(question=q):
                original=bank.get(q)
                self.assertEqual(original['metadata']['generation_status'],'ACTIVE')
                cfg,_=store.load(q)
                self.assertEqual(validate_config(cfg,original),[])
                self.assertEqual(reproduce_original(original,cfg),([],[]))
                unique=set()
                for k in range(cfg['variables']['k']['range'][1]+1):
                    c=assemble(cfg,build_values(cfg,lambda n,s:k));check_math(q,c)
                    if k:
                        self.assertEqual(validate_candidate(c,original,[]),[])
                        unique.add(signature(c['stem'],c['options']))
                self.assertEqual(len(unique),cfg['variables']['k']['range'][1])
                candidates=[]
                count=min(10,cfg['variables']['k']['range'][1])
                for seed in range(count):
                    candidate=generate(original,cfg,seed,candidates).cand
                    check_math(q,candidate);candidates.append(candidate)
                self.assertEqual(candidates[-1],generate(original,cfg,count-1,candidates[:-1]).cand)
                for index in range(len(candidates[-1]['options'])):
                    bad=deepcopy(candidates[-1]);bad['options'][index]['correct'] ^= True
                    with self.assertRaises(AssertionError):check_math(q,bad)


if __name__=='__main__': unittest.main()
