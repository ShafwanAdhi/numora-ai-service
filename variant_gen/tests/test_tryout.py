"""Tryout checks use temporary stores; never connect to Numora's database."""
import json
import sys
import tempfile
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bank import OriginalBank, BankError
from config_store import ConfigStore, validate_config
from engine import generate, key_of
from expr import render
from lint import reproduce_original
from store import StoreError
from unittest.mock import patch
from engine import make_record
import statistics

DEFERRED = {'tryout-1-b1-q07', 'tryout-1-b4-q02', 'tryout-1-b4-q06'}


class TryoutTests(unittest.TestCase):
    def setUp(self):
        self.bank = OriginalBank(ROOT / 'data/tryout-1/q0_bank.csv')
        self.configs = ConfigStore(ROOT / 'configs')

    def test_bank_inventory_and_source_corrections(self):
        self.assertEqual(len(self.bank.ids()), 30)
        self.assertEqual(Counter(self.bank.get(q)['format'] for q in self.bank.ids()),
                         dict(PG=18, MCMA=6, KATEGORI=6))
        self.assertEqual(Counter(self.bank.get(q)['cognitive_level'] for q in self.bank.ids()),
                         dict(C3=8, C4=15, C5=7))
        self.assertEqual({q for q in self.bank.ids() if self.bank.get(q)['metadata']['generation_status'] == 'DEFERRED_CONCEPTUAL'}, DEFERRED)
        original = self.bank.get('tryout-1-b2-q04')
        self.assertEqual(original['version'], 2)
        self.assertEqual([o['id'] for o in original['options'] if o['correct']], ['C'])
        self.assertIn('16.000', original['options'][2]['text'])
        self.assertEqual([len(g['question_ids']) for g in self.bank.catalog()], [8,8,7,7])

    def test_workspace_bank_isolation(self):
        from bank import load_workspace_bank
        self.assertEqual(len(OriginalBank(ROOT / 'data/q0_bank.csv').ids()), 120)
        workspace=load_workspace_bank(ROOT / 'data/q0_bank.csv')
        self.assertEqual(len(workspace.ids()),sum(len(OriginalBank(p).ids()) for p in (ROOT/'data').rglob('q0_bank.csv')))
        self.assertEqual(len(load_workspace_bank(ROOT / 'data/tryout-1/q0_bank.csv').ids()), 30)
        with self.assertRaises(BankError):
            load_workspace_bank(ROOT / 'data/q0_bank.csv', [ROOT / 'data/q0_bank.csv'])

    def test_malformed_metadata_is_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            for name in ['q0_bank.csv','question_catalog.json','original_revisions.jsonl','question_metadata.json']:
                shutil.copyfile(ROOT/'data/tryout-1'/name,Path(tmp)/name)
            path=Path(tmp)/'question_metadata.json'; original=json.loads(path.read_text())
            from copy import deepcopy
            for qid,field,value in [('tryout-1-b1-q01','notes',1),('tryout-1-b1-q07','reason',True)]:
                changed=deepcopy(original); changed[qid][field]=value
                path.write_text(json.dumps(changed),encoding='utf-8')
                with self.assertRaises(BankError): OriginalBank(Path(tmp)/'q0_bank.csv')

    def test_configs_reproduce_and_generate(self):
        for qid in self.bank.ids():
            with self.subTest(question=qid):
                if qid in DEFERRED:
                    self.assertEqual(self.configs.versions(qid), [])
                    continue
                orig = self.bank.get(qid)
                cfg, _ = self.configs.load(qid)
                self.assertEqual(validate_config(cfg, orig), [])
                self.assertEqual(reproduce_original(orig, cfg), ([], []))
                candidates = []
                for seed in range(1,21):
                    result = generate(orig, cfg, seed, candidates)
                    check_math(self, qid, result.values, result.cand)
                    self.assertTrue(result.cand['explanation'].strip())
                    self.assertEqual(result.cand, generate(orig, cfg, seed, candidates).cand)
                    self.assertEqual(sum(o['correct'] for o in result.cand['options']), sum(o['correct'] for o in orig['options']))
                    candidates.append(result.cand)

    def test_package_returns_preview_without_persistence(self):
        from tryout import generate_package,export_package
        first=generate_package(self.bank,self.configs,'tryout-1',7)
        self.assertEqual(len(first['items']),30)
        self.assertEqual(Counter(i['status'] for i in first['items']),dict(VARIANT=27,ORIGINAL_ONLY=3))
        second=generate_package(self.bank,self.configs,'tryout-1',7)
        self.assertEqual([i['record']['stem'] for i in first['items']],[i['record']['stem'] for i in second['items']])
        self.assertEqual(export_package(first),first)

    def test_modified_manifest_is_rejected(self):
        from copy import deepcopy
        from tryout import generate_package,export_package
        first=generate_package(self.bank,self.configs,'tryout-1',7)
        malformed=[]
        changed=deepcopy(first);changed['items'].pop();malformed.append(changed)
        changed=deepcopy(first);changed['items'].reverse();malformed.append(changed)
        changed=deepcopy(first);changed['items'][6]['record']['stem']='tampered';malformed.append(changed)
        changed=deepcopy(first);changed['items'][0]['record']['options']=[None];malformed.append(changed)
        changed=deepcopy(first);del changed['items'][0]['record']['config_hash'];malformed.append(changed)
        for changed in malformed:
            with self.assertRaises(StoreError):export_package(changed)

    def test_failed_package_has_no_partial_output(self):
        from tryout import generate_package
        real_load=self.configs.load
        def bad_load(qid,*args):
            if qid.endswith('b4-q07'):raise ValueError('bad config')
            return real_load(qid,*args)
        with patch.object(self.configs,'load',side_effect=bad_load),self.assertRaises(ValueError):
            generate_package(self.bank,self.configs,'tryout-1',9)
        self.assertEqual(len(generate_package(self.bank,self.configs,'tryout-1',9)['items']),30)


class FractionTests(unittest.TestCase):
    def test_mixed_fraction_rendering(self):
        for value, expected in [(Fraction(13,3),'4 1/3'), (Fraction(-13,3),'-4 1/3'),
                                (Fraction(2,6),'1/3'), (2,'2'), (0,'0')]:
            self.assertEqual(render('{x}', {'x':value}, {'x':{'fmt':'mixed'}}), expected)
        self.assertEqual(render('{x}', {'x':Fraction(13,3)}), '4,33')
        from expr import ExprError
        with self.assertRaises(ExprError):
            render('{x}', {'x':'text'}, {'x':{'fmt':'mixed'}})


def check_math(test, qid, v, cand):
    """Independent arithmetic oracle. Never evaluates the config's formulas."""
    q = qid.removeprefix('tryout-1-')
    expected = {}
    if q == 'b1-q01': expected = dict(ans=v['a']+v['b'])
    elif q == 'b1-q02': expected = dict(ans=v['money']-v['book']-v['tools'])
    elif q == 'b1-q03': expected = dict(first=v['a']+v['b']*v['c'], second=(v['a']+v['b'])*v['c'])
    elif q == 'b1-q04':
        answer = Fraction(v['dividend'],v['divisor'])-v['c']
        reports=[v[f's{i}'] for i in range(4)]
        test.assertEqual(sum(value==answer for value in reports), 1)
        test.assertEqual([o['correct'] for o in cand['options']], [value==answer for value in reports])
        expected=dict(ans=answer)
    elif q == 'b1-q05': expected=dict(out=v['m']*v['x']-v['b'], o3=Fraction(v['m']*v['x']-2*v['b'],v['m']))
    elif q == 'b1-q06':
        expected=dict(sum=v['a']+v['b'], product=v['c']*v['e'], difference=v['f']-v['g'])
        test.assertNotEqual(v['baddiv'],Fraction(v['dividend'],v['d']))
        test.assertNotEqual(v['badsub'],v['f']-v['g'])
    elif q == 'b1-q08': expected=dict(discount=Fraction(v['price']*v['pct'],100), total=Fraction(v['price']*(100-v['pct']),100)+v['fee'])
    elif q == 'b2-q01': expected=dict(coef=v['a']*v['b']+v['d']*v['e'], const=v['a']*v['c']-v['d']*v['f'])
    elif q == 'b2-q02': expected=dict(ans=v['a']+(v['n']-1)*v['d'])
    elif q == 'b2-q03':
        ans=(v['budget']-v['fixed'])//v['unit']
        expected=dict(ans=ans)
        test.assertLessEqual(v['unit']*ans+v['fixed'],v['budget'])
        test.assertGreater(v['unit']*(ans+1)+v['fixed'],v['budget'])
    elif q == 'b2-q04':
        x=Fraction(2*v['t1']-v['t2'],4); y=Fraction(v['t2']-2*x,4)
        expected=dict(x=x,y=y,ans=x+y)
    elif q == 'b2-q05':
        expected=dict(claim1=[v[f'r{i}'] for i in range(1,5)]==[v['base']+v['rate']*i for i in range(1,5)], claim2=v['hours'] in range(1,5))
        a,b=expected['claim1'],expected['claim2']
        test.assertEqual([o['correct'] for o in cand['options']],[a and b,a and not b,not a and b,not a and not b])
    elif q == 'b2-q06':
        a=Fraction(3*v['t2']-v['t1'],10); b=v['t2']-4*a
        expected=dict(a=a,b=b,diff=a-b,total=2*a+2*b)
    elif q == 'b2-q07':
        deposits=[v['a']+i*v['d'] for i in range(v['n'])]
        expected=dict(last=deposits[-1],total=sum(deposits),mean=Fraction(sum(deposits),len(deposits)))
    elif q == 'b2-q08':
        expected=dict(coef=v['a']-v['c'],const=v['a']*v['b']+v['c']*v['d'],value=v['a']*(v['x']+v['b'])-v['c']*(v['x']-v['d']))
    elif q == 'b3-q01': expected=dict(ox=v['y']+v['dx'],oy=v['x']+v['dy'])
    elif q == 'b3-q02': expected=dict(ans=2*v['r']*v['p']+Fraction(11*v['r']**2,7))
    elif q == 'b3-q03':
        x=Fraction(v['b']+v['offset'],v['c']-v['a']); angle=v['a']*x+v['b']
        expected=dict(x=x,angle=angle,ans=180-angle-v['other'])
    elif q == 'b3-q04': expected=dict(water=Fraction(v['s']**2*v['h'],3)*Fraction(v['p'],v['q'])**3)
    elif q == 'b3-q05':
        width=v['w']-2*v['m']; height=Fraction(width*v['h'],v['w'])
        expected=dict(fh=height,bottom=v['h']-height-v['m'],remainder=v['w']*v['h']-width*height)
        test.assertEqual(Fraction(v['rn'],v['rd']),Fraction(width**2,v['w']**2))
        test.assertNotEqual(v['wrong'],expected['remainder'])
    elif q == 'b3-q06':
        cyl=Fraction(22,7)*v['r']**2*v['h']; hem=Fraction(44,21)*v['r']**3; box=v['p']*v['l']*v['t']
        expected=dict(cyl=cyl,hem=hem,total=cyl+hem,box=box)
        test.assertLess(cyl,box);test.assertLess(box,cyl+hem);test.assertLess(hem,v['threshold'])
        # Fraction integer rounding oracle: exactly half up, without using expr.round.
        diff=cyl+hem-box; expected['diff']=Fraction((diff*100+Fraction(1,2)).numerator//(diff*100+Fraction(1,2)).denominator,100)
    elif q == 'b3-q07': expected=dict(rx2=v['k']*v['x'],ry2=v['k']*(v['y']+3*v['scale']),area2=6*v['scale']**2*v['k']**2,hyp=5*v['scale']*abs(v['k']))
    elif q == 'b4-q01':
        data=[v['a'],v['mode'],v['b'],v['mode'],v['d']]
        test.assertEqual(statistics.multimode(data),[v['mode']])
    elif q == 'b4-q03':
        freq=[v[f'f{i}'] for i in range(1,6)]; n=sum(freq); total=sum((i+1)*f for i,f in enumerate(freq)); mean=Fraction(total,n)
        count=sum(f for i,f in enumerate(freq) if i+1>=mean)
        expected=dict(n=n,total=total,mean=mean,count=count,pct=Fraction(100*count,n))
    elif q == 'b4-q04':
        x=[v['mu']+a*v['sx'] for a in [-6,-3,0,3,6]]
        y=[v['mu']+a*v['sy'] for a in [-13,-3,-3,7,12]]
        if v['swap']:x,y=y,x
        expected=dict(mean=statistics.mean(x),rangex=max(x)-min(x),rangey=max(y)-min(y),maxx=max(x),maxy=max(y),medx=statistics.median(x),medy=statistics.median(y))
        test.assertTrue(all(0<=score<=100 for score in x+y))
        test.assertEqual(v['smaller'],'X' if max(x)-min(x)<max(y)-min(y) else 'Y')
    elif q == 'b4-q05':
        pairs=[(a,b) for a in range(1,7) for b in range(1,7)]
        ways=sum(a+b>=v['threshold'] for a,b in pairs); primes=sum(a+b in {2,3,5,7,11} for a,b in pairs)
        expected=dict(ways=ways,expected=Fraction(ways*v['times'],36),prime=Fraction(primes*v['times'],36))
    elif q == 'b4-q07':
        data=[v[n] for n in ['a','d2','d3','d4','d5','b','max']]
        test.assertEqual(data,sorted(set(data)))
        expected=dict(range=max(data)-min(data),mean=Fraction(sum(data),7))
        test.assertEqual(statistics.median(data),statistics.median(data[:-1]+[v['newmax']]))
    for name, value in expected.items():
        test.assertEqual(v[name],value,f'{qid}: {name}')
    # Compare rendered answers against independently calculated results, not config keys.
    from expr import format_number
    f=format_number
    answers={
        'b1-q01':lambda:f"{f(expected['ans'])}°C",
        'b1-q02':lambda:f"Rp{f(expected['ans'])},00",
        'b1-q03':lambda:f"Hasil Budi adalah {f(expected['first'])} dan hasil Andi adalah {f(expected['second'])}.",
        'b1-q05':lambda:f"Bilangan tersebut diperoleh dari ({f(expected['out'])} + {f(v['b'])}) ÷ {f(v['m'])}, sehingga hasilnya {f(v['x'])}.",
        'b2-q01':lambda:f"{f(expected['coef'])}x+{f(expected['const'])}",
        'b2-q02':lambda:f"{f(expected['ans'])} kursi",
        'b2-q03':lambda:f"{f(expected['ans'])} buah",
        'b2-q04':lambda:f"Rp{f(expected['ans'])},00",
        'b3-q01':lambda:f"({f(expected['ox'])}, {f(expected['oy'])})",
        'b3-q02':lambda:f"{f(expected['ans'])} m²",
        'b3-q03':lambda:f"{f(expected['ans'])}°",
        'b3-q04':lambda:f"{f(expected['water'])} cm³",
        'b4-q01':lambda:f(v['mode']),
        'b4-q03':lambda:f"{f(expected['pct'])}%",
        'b4-q04':lambda:f"Kelas {v['smaller']} memiliki rentang nilai lebih sempit karena selisih nilai maksimum dan minimum lebih kecil.",
    }
    if q in answers:
        answer=answers[q]()
        test.assertEqual(sum(o['text']==answer for o in cand['options']),1,qid)
        test.assertEqual([o['correct'] for o in cand['options']],[o['text']==answer for o in cand['options']],qid)
    truths={
        'b1-q06':lambda:[v['sum']==v['a']+v['b'],v['baddiv']==Fraction(v['dividend'],v['d']),v['product']==v['c']*v['e'],v['badsub']==v['f']-v['g']],
        'b1-q08':lambda:[v['discount']==expected['discount'],v['total']==v['price']-expected['discount'],v['total']==expected['total'],v['wrongtotal']==expected['total']],
        'b2-q06':lambda:[v['a']==expected['a'],v['b']==expected['b'],v['diff']==expected['diff'],v['total']==expected['total']],
        'b2-q07':lambda:[v['last']==expected['last'],v['total']==expected['total'],v['mean']==expected['mean']],
        'b2-q08':lambda:[v['coef']==expected['coef'] and v['const']==expected['const'],v['a']*v['b']-v['c']*v['d']==expected['const'],v['value']==expected['value']],
        'b3-q05':lambda:[v['fh']==expected['fh'],v['bottom']==expected['bottom'],Fraction(v['rn'],v['rd'])==Fraction((v['w']-2*v['m'])**2,v['w']**2),v['wrong']==expected['remainder']],
        'b3-q06':lambda:[expected['total']>expected['box'],v['diff']==expected['diff'],expected['hem']>v['threshold'],expected['cyl']<expected['box']],
        'b3-q07':lambda:[v['rx2']==expected['rx2'] and v['ry2']==expected['ry2'],v['factor']==v['k']**2,v['hyp']==expected['hyp']],
        'b4-q05':lambda:[Fraction(sum(a+b==7 for a,b in pairs),36)==Fraction(1,6),Fraction(sum(a==b for a,b in pairs),36)==Fraction(1,12),v['expected']==expected['expected'],v['prime']==expected['prime']],
        'b4-q07':lambda:[Fraction(sum(data),7)==v['mean'],statistics.multimode(data)==[v['d4']],statistics.median(data[:-1]+[v['newmax']])==statistics.median(data)+1],
    }
    if q in truths:
        test.assertEqual([o['correct'] for o in cand['options']],truths[q](),qid)


if __name__ == '__main__':
    unittest.main()
