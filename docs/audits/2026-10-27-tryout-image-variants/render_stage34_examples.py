"""Export stage 3–4 review artifacts explicitly; preserve earlier stage evidence."""
import hashlib
import io
import json
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'variant_gen'))
from bank import OriginalBank
from config_store import ConfigStore
from engine import build_values,generate
from expr import to_num
from image_variants import load_template,build_scene,render_scene


def exact(value):
    if isinstance(value,Fraction):return {'numerator':value.numerator,'denominator':value.denominator}
    raise TypeError(type(value).__name__)


def main():
    from PIL import Image,ImageDraw,ImageFont
    output=Path(__file__).resolve().parent
    bank=OriginalBank(ROOT/'variant_gen/data/tryout-1/q0_bank.csv');configs=ConfigStore(ROOT/'variant_gen/configs')
    manifest=json.loads((ROOT/'docs/sources/incoming/2026-10-26-tryout-images/image-manifest.json').read_text(encoding='utf-8'))
    sources={x['candidate_local_question_id']:x for x in manifest['images']};records=[]
    for qid,stage,name in (('tryout-1-b3-q03',3,'angles'),('tryout-1-b3-q04',4,'pyramid')):
        folder=output/f'stage-{stage}';folder.mkdir(exist_ok=True)
        t=load_template(qid);cfg,cfg_hash=configs.load(qid);orig=bank.get(qid)
        fixtures=[('original-values',cfg['original_values'])]
        if stage==3:
            fixtures.extend([('long-expression',{'x':25,'a':2,'b':5,'c':9,'other':75}),
                             ('obtuse-angle',{'x':20,'a':5,'b':20,'c':9,'other':30})])
        else:
            fixtures.extend([('water-1-3',{'s':12,'h':18,'p':1,'q':3}),
                             ('water-2-3',{'s':12,'h':18,'p':2,'q':3}),
                             ('min-dimensions',{'s':6,'h':9,'p':1,'q':3}),
                             ('max-dimensions',{'s':30,'h':45,'p':2,'q':3})])
        examples=[(label,build_values(cfg,lambda k,sp:to_num(vals[k]),check=False),None) for label,vals in fixtures]
        for seed in range(1,21):
            r=generate(orig,cfg,seed,[]);examples.append((f'seed-{seed}',r.values,r.cand))
        source_path=ROOT/'docs/sources/incoming/2026-10-26-tryout-images'/sources[qid]['local_path']
        panels=[('Original source',Image.open(source_path).convert('RGB'))]
        for label,values,candidate in examples:
            r=render_scene(t,build_scene(t,values));filename=f'{name}-{label}.png';(folder/filename).write_bytes(r.png_bytes)
            records.append({'question_id':qid,'example':label,'file':f'stage-{stage}/{filename}',
                            'kind':'generated' if candidate else 'review-fixture',
                            'original_version':orig['version'],'original_hash':orig['hash'],
                            'config_version':cfg['config_version'],'config_hash':cfg_hash,
                            'raw_values':values,'candidate':candidate,'sha256':r.sha256,'byte_length':r.byte_length,
                            'scene':asdict(r.scene),'provenance':r.provenance})
            if label in ('original-values','seed-1','long-expression','obtuse-angle','water-1-3','water-2-3','max-dimensions'):
                panels.append((label,Image.open(io.BytesIO(r.png_bytes)).convert('RGB')))
        width,height=t.width+20,t.height+42
        sheet=Image.new('RGB',(width*3,height*((len(panels)+2)//3)),'#eef1f4');d=ImageDraw.Draw(sheet)
        font=ImageFont.truetype(io.BytesIO(t.font_bytes),14)
        for i,(label,panel) in enumerate(panels):
            x,y=(i%3)*width,(i//3)*height;d.text((x+10,y+6),label,font=font,fill='black');sheet.paste(panel,(x+10,y+30))
        sheet.save(folder/f'{name}-contact-sheet.png')
    (output/'examples-stage34.json').write_text(json.dumps({'scope':'LOCAL_RENDERED stages3-4; no package integration or DB/R2 writes','examples':records},ensure_ascii=False,indent=2,default=exact)+'\n',encoding='utf-8')
    print(f'Exported {len(records)} PNGs and 2 contact sheets; earlier stage artifacts preserved.')


if __name__=='__main__':main()
