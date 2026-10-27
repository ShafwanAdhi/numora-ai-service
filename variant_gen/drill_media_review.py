"""Explicit local Drill review export. This is not a Tryout package or DB payload."""
import copy
import html
import io
import json
from pathlib import Path

import cli
from drill_images import IDS as NUMERIC, preview as numeric_preview, render_accepted
from drill_concept_images import IDS as CONCEPTUAL, preview as conceptual_preview
from drill_images.adapter import exact_sha
from drill_images.templates import snapshot_sha
from store import StoreError
from tryout_media import digest, json_bytes, stable_questions
from tryout_media_io import write_files

KIND='DRILL_IMAGE_REVIEW'


def _stable_record(record):
    value=copy.deepcopy(record);value.pop('created_at',None);return value


def _preview(questions,assets):
    cards=[]
    for item,asset in zip(questions['items'],assets):
        record=item['record'];esc=html.escape
        cards.append(f'<article id="case-{len(cards)}"><h2>{esc(item["case_id"])}</h2>'+
                     f'<img loading="lazy" src="{asset["path"]}" width="{asset["width"]}" height="{asset["height"]}" alt="{esc(asset["alt_text"],quote=True)}">'+
                     f'<p>{esc(record["stem"])}</p><ol type="A">'+
                     ''.join(f'<li>{esc(o["text"])}</li>' for o in record['options'])+
                     f'</ol><details><summary>Kunci {esc(record["key"])} dan pembahasan</summary><pre>{esc(record.get("explanation",""))}</pre></details></article>')
    return ('''<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Review gambar Drill</title><link rel="icon" href="data:,"><style>*{box-sizing:border-box}body{font:15px/1.6 system-ui;background:#f5f7f8;color:#182b34;margin:0}main{max-width:1080px;margin:auto;padding:24px}article{background:white;padding:24px;margin:24px 0;border:1px solid #d2dde1}h1{font-size:26px}h2{font-size:18px;overflow-wrap:anywhere}img{max-width:100%;height:auto}p,pre{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer}</style><main><h1>Review lokal gambar Drill</h1><p>Indikator 16-19: diagram terdapat pada indikator 16. Record original, generator, dan stok tetap mengikuti sistem existing. Untuk review operator, bukan publikasi siswa.</p>'''+''.join(cards)+'</main></html>').encode('utf-8')


def build_review(bank,configs,stocks,*,seed=None):
    """None collects every accepted k; positive seed collects one variant per family."""
    if seed is not None and (type(seed) is not int or not 1<=seed<=1_000_000_000):
        raise StoreError('Review seed must be a positive integer, or omitted for the full domain.')
    items=[];assets=[];images={}
    def retain(qid,mode,record,image,request,k=None):
        suffix='original' if mode=='original' else request['stock_variant_id'].rsplit(':',1)[1] if mode=='stock' else f'k{k}'
        case_id=f'{qid}:{suffix}'
        path=f'images/{image.sha256}.png'
        items.append({'case_id':case_id,'question_id':qid,'mode':mode,'k':k,
                      'request':request,'record':record})
        assets.append({'case_id':case_id,'question_id':qid,'mode':mode,'path':path,
                       'sha256':image.sha256,'width':image.width,'height':image.height,
                       'alt_text':image.scene.alt_text,'record_content_sha256':digest(json_bytes(_stable_record(record))),
                       'provenance':copy.deepcopy(image.provenance)})
        images[path]=image.png_bytes
    def order(qid):
        original=bank.get(qid)
        return original['classification']['source_level'],original['metadata']['source_number']
    for qid in sorted((*NUMERIC,*CONCEPTUAL),key=order):
        if qid in CONCEPTUAL:
            record,image=conceptual_preview(bank,stocks,qid)
            retain(qid,'original',record,image,{'question_id':qid,'mode':'original'})
            for stock in stocks.get(qid,[]):
                variant=stock['variant_id'];record,image=conceptual_preview(bank,stocks,qid,variant)
                retain(qid,'stock',record,image,{'question_id':qid,'mode':'stock','stock_variant_id':variant})
        else:
            record,image=numeric_preview(bank,configs,qid,0)
            retain(qid,'original',record,image,{'question_id':qid,'mode':'original'},0)
            if seed is not None:
                record,image=numeric_preview(bank,configs,qid,seed)
                retain(qid,'generator',record,image,{'question_id':qid,'mode':'generator','seed':seed},record['values_used']['k'])
            else:
                accepted={}
                for candidate_seed in range(1,5001):
                    def capture(original,config,result,record):
                        k=result.values['k']
                        if k not in accepted:
                            path=configs.root/qid/f"v{config['config_version']}.json"
                            image=render_accepted(original,config,result,record,config_path=path)
                            accepted[k]=(record,image,candidate_seed)
                    cli.preview(bank,configs,qid,candidate_seed,on_generated=capture)
                    if len(accepted)==30:break
                if sorted(accepted)!=list(range(1,31)):
                    raise StoreError('Existing accepted domain not fully covered; no automatic expansion.')
                for k,(record,image,selected_seed) in sorted(accepted.items()):
                    retain(qid,'generator',record,image,{'question_id':qid,'mode':'generator','seed':selected_seed},k)
    questions={'schema_version':1,'kind':KIND,'coverage':'full_domain' if seed is None else 'single_seed','seed':seed,
               'items':items}
    identity=digest(json_bytes({'questions':stable_questions(questions),'assets':assets}))
    preview=_preview(questions,assets)
    question_bytes=json_bytes(questions)
    manifest={'schema_version':1,'kind':KIND,'status':'LOCAL_RENDERED','bundle_id':identity,
              'assets':assets,'questions_sha256':digest(question_bytes),'preview_sha256':digest(preview)}
    files={'questions.json':question_bytes,'media-manifest.json':json_bytes(manifest),
           'preview.html':preview,**images}
    verify_review_files(files)
    return files


def verify_review_files(files):
    """Cross-check bytes, complete coverage, record/image binding and deterministic preview."""
    try:
        questions=json.loads(files['questions.json']);manifest=json.loads(files['media-manifest.json'])
        if (questions['kind']!=KIND or manifest['kind']!=KIND or questions['schema_version']!=1
                or manifest['schema_version']!=1 or manifest['status']!='LOCAL_RENDERED'):
            raise StoreError('Not a versioned local Drill review.')
        if questions['coverage'] not in ('full_domain','single_seed'):
            raise StoreError('Unknown Drill review coverage mode.')
        selected_seed=questions.get('seed')
        if (questions['coverage']=='single_seed' and (type(selected_seed) is not int or not 1<=selected_seed<=1_000_000_000)
                or questions['coverage']=='full_domain' and selected_seed is not None):
            raise StoreError('Invalid Drill review seed metadata.')
        items=questions['items'];assets=manifest['assets'];expected_count=167 if questions['coverage']=='full_domain' else 22
        if len(items)!=expected_count or len(assets)!=len(items) or len({i['case_id'] for i in items})!=len(items):
            raise StoreError('Drill review has incomplete or duplicate coverage.')
        expected_files={'questions.json','media-manifest.json','preview.html'}
        counts={qid:[] for qid in (*NUMERIC,*CONCEPTUAL)}
        from PIL import Image
        for item,asset in zip(items,assets):
            qid=item['question_id'];record=item['record'];request=item['request'];mode=item['mode']
            if qid not in counts or asset['case_id']!=item['case_id'] or asset['question_id']!=qid or asset['mode']!=mode:
                raise StoreError('Drill review identity mismatch.')
            if record['question_id']!=qid or request['question_id']!=qid or request['mode']!=mode:
                raise StoreError('Drill review request/record mismatch.')
            suffix='original' if mode=='original' else record.get('variant_id','').rsplit(':',1)[-1] if mode=='stock' else f"k{item['k']}"
            if item['case_id']!=f'{qid}:{suffix}':
                raise StoreError('Drill case identity does not follow its selection.')
            counts[qid].append(item)
            path=f"images/{asset['sha256']}.png"
            if asset['path']!=path or digest(files[path])!=asset['sha256']:
                raise StoreError('Drill review PNG hash/path mismatch.')
            with Image.open(io.BytesIO(files[path])) as png:
                if png.format!='PNG' or png.size!=(asset['width'],asset['height']):
                    raise StoreError('Drill review PNG dimensions mismatch.')
            expected_files.add(path)
            provenance=asset['provenance'];content=provenance['content']
            stable=_stable_record(record)
            expected_record_hash=exact_sha(stable) if qid in NUMERIC else snapshot_sha(record)
            if (digest(json_bytes(stable))!=asset['record_content_sha256']
                    or content['record_sha256']!=expected_record_hash
                    or provenance['png_sha256']!=asset['sha256'] or content['mode']!=mode
                    or provenance['question_id']!=qid or provenance['alt_text']!=asset['alt_text']
                    or provenance['width']!=asset['width'] or provenance['height']!=asset['height']
                    or provenance['byte_length']!=len(files[path])
                    or content['record_id']!=record['record_id']
                    or content['original_hash']!=record['original_hash']
                    or content['original_version']!=record['original_version']):
                raise StoreError('Drill record/image content binding mismatch.')
            if mode=='generator':
                if (qid not in NUMERIC or request.get('seed')!=record['seed'] or record['values_used']['k']!=item['k']
                        or questions['coverage']=='single_seed' and request['seed']!=selected_seed
                        or content['config_hash']!=record['config_hash']):
                    raise StoreError('Drill generator selection mismatch.')
            elif mode=='stock':
                if (qid not in CONCEPTUAL or request.get('stock_variant_id')!=record['variant_id']
                        or content['stock_variant_id']!=record['variant_id'] or 'seed' in request):
                    raise StoreError('Drill stock selection mismatch.')
            elif mode!='original' or record['seed']!=0:
                raise StoreError('Drill original selection mismatch.')
        for qid,rows in counts.items():
            if sum(r['mode']=='original' for r in rows)!=1:
                raise StoreError('Each family requires one original.')
            if qid in NUMERIC:
                variants=[r['k'] for r in rows if r['mode']=='generator']
                if (sorted(variants)!=list(range(1,31)) if questions['coverage']=='full_domain' else len(variants)!=1):
                    raise StoreError('Numerical domain coverage mismatch.')
            elif sorted(r['record'].get('stock_index') for r in rows if r['mode']=='stock')!=[1,2]:
                raise StoreError('Conceptual stock coverage mismatch.')
        identity=digest(json_bytes({'questions':stable_questions(questions),'assets':assets}))
        if (manifest['bundle_id']!=identity or digest(files['questions.json'])!=manifest['questions_sha256']
                or digest(files['preview.html'])!=manifest['preview_sha256']
                or files['preview.html']!=_preview(questions,assets) or set(files)!=expected_files):
            raise StoreError('Drill review manifest/preview/roster mismatch.')
        return {'status':'LOCAL_RENDERED','bundle_id':identity,'cases':len(items),'families':len(counts),
                'unique_images':len(expected_files)-3,'coverage':questions['coverage']}
    except StoreError:raise
    except (KeyError,TypeError,ValueError,OSError) as exc:
        raise StoreError('Invalid local Drill review files.') from exc


def write_review(files,output):
    verify_review_files(files)
    # Only the existing generic atomic file writer is reused; no Tryout package schema is changed.
    return write_files(files,Path(output))
