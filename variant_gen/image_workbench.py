"""Local image-page application layer. No database, R2, network or implicit writes."""
import base64

import cli
from engine import build_values, original_record
from image_variants import ImageVariantError, build_scene, load_template, render_scene
from tryout_media import IMAGE_IDS
from drill_images import IDS as NUMERIC_IDS, preview as numeric_preview
from drill_concept_images import IDS as CONCEPT_IDS, preview as conceptual_preview


def catalog(bank, stocks):
    available=set(bank.ids())
    rows=[]
    for qid in sorted(set(IMAGE_IDS)|set(NUMERIC_IDS)|set(CONCEPT_IDS)):
        if qid not in available:continue
        original=bank.get(qid)
        conceptual=qid in CONCEPT_IDS
        rows.append({'id':qid,'stem':original['stem'],
                     'activity':'TRYOUT' if qid in IMAGE_IDS else 'DRILL',
                     'modes':['original','stock'] if conceptual else ['generator','original'],
                     'stocks':[{'variant_id':s['variant_id'],'stock_index':s['stock_index'],
                                'stock_version':s['stock_version']} for s in stocks.get(qid,[])] if conceptual else []})
    return rows


def generate(data, bank, configs, stocks):
    qid=data.get('question_id')
    if not isinstance(qid,str) or qid not in set(IMAGE_IDS)|set(NUMERIC_IDS)|set(CONCEPT_IDS):
        raise ImageVariantError('Soal belum memiliki template image variant.')
    if data.keys()-{'question_id','mode','seed','stock_variant_id'}:
        raise ImageVariantError('Parameter image variant tidak dikenal.')
    conceptual=qid in CONCEPT_IDS
    mode=data.get('mode','original' if conceptual else 'generator')
    allowed=('original','stock') if conceptual else ('generator','original')
    if not isinstance(mode,str) or mode not in allowed:
        raise ImageVariantError('Mode gambar tidak tersedia untuk soal ini.')
    if mode=='generator':
        seed=data.get('seed')
        if type(seed) is not int or not 1<=seed<=1_000_000_000:
            raise ImageVariantError('Seed harus bilangan bulat positif (maksimal 1.000.000.000).')
    elif mode=='original':
        if 'seed' in data and (type(data['seed']) is not int or data['seed']!=0):
            raise ImageVariantError('Original tidak menggunakan seed varian.')
        seed=0
    else:
        if 'seed' in data:raise ImageVariantError('Stok dipilih melalui ID, bukan seed.')
        seed=None
    variant=data.get('stock_variant_id')
    if mode=='stock':
        if not isinstance(variant,str):raise ImageVariantError('Pilih stock_variant_id yang tersedia.')
    elif 'stock_variant_id' in data:
        raise ImageVariantError('stock_variant_id hanya digunakan pada mode Stok.')
    try:
        if conceptual:
            record,image=conceptual_preview(bank,stocks,qid,variant)
        elif qid in NUMERIC_IDS:
            record,image=numeric_preview(bank,configs,qid,seed)
        elif mode=='original':
            original=bank.get(qid);config,_=cli.load_config(configs,original)
            values=build_values(config,lambda name,spec:config['original_values'][name])
            template=load_template(qid)
            record=original_record(original)
            image=render_scene(template,build_scene(template,values))
        else:
            images=[]
            def capture(original,config,result,record):
                template=load_template(qid)
                images.append(render_scene(template,build_scene(template,result.values)))
            record=cli.preview(bank,configs,qid,seed,on_generated=capture)
            image=images[0]
    except ImportError as exc:
        raise ImageVariantError('Dependensi gambar belum tersedia; pasang requirements-image.txt.') from exc
    return {'record':record,'mode':mode,
            'source':{'activity':'TRYOUT' if qid in IMAGE_IDS else 'DRILL',
                      'stock_variant_id':variant,'stock_version':record.get('variant_ver') if mode=='stock' else None},
            'image':{'base64':base64.b64encode(image.png_bytes).decode('ascii'),
                     'sha256':image.sha256,'width':image.width,'height':image.height,
                     'alt_text':image.scene.alt_text,'provenance':image.provenance}}
