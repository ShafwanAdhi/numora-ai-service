"""Opt-in local bundle assembly. No database, R2, network, or implicit writes."""
import copy
import hashlib
import html
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

from expr import json_number
from image_variants import build_scene, load_template, render_scene
from image_variants.models import RenderedImage
from store import StoreError
from tryout import generate_package, validate_manifest

IMAGE_IDS=frozenset(('tryout-1-b3-q02','tryout-1-b3-q03','tryout-1-b3-q04','tryout-1-b3-q06','tryout-1-b4-q05'))
ROSTER=tuple(f'tryout-1-b{c}-q{n:02d}' for c,count in ((1,8),(2,8),(3,7),(4,7)) for n in range(1,count+1))


def exact(value):
    if isinstance(value,Fraction):return {'numerator':value.numerator,'denominator':value.denominator}
    raise TypeError(type(value).__name__)


def json_bytes(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,default=exact)+'\n').encode('utf-8')


def digest(data):return hashlib.sha256(data).hexdigest()


def stable_questions(questions):
    value=copy.deepcopy(questions)
    for item in value['items']:item['record'].pop('created_at',None)
    return value


def _record_identity(record):
    content=copy.deepcopy(record);content.pop('created_at',None)
    return {'question_id':record['question_id'],'record_id':record['record_id'],
            'seed':record['seed'],'variant_ver':record['variant_ver'],
            'original_version':record['original_version'],'original_hash':record['original_hash'],
            'config_version':record['config_ver'],'config_hash':record['config_hash'],
            'record_content_sha256':digest(json_bytes(content))}


@dataclass(frozen=True)
class MediaBundle:
    questions: dict
    images: tuple[RenderedImage,...]
    media_manifest: dict


def _asset(record,image):
    identity=_record_identity(record)
    return {**identity,'asset_id':'diagram-1','text_marker':'[[asset:diagram-1]]',
            'placement':'STEM','item_id':None,'asset_order':1,'status':'LOCAL_RENDERED',
            'path':f'images/{image.sha256}.png','sha256':image.sha256,
            'byte_length':image.byte_length,'width':image.width,'height':image.height,
            'alt_text':image.scene.alt_text,'scene':json.loads(json_bytes(asdict(image.scene))),
            'image_provenance':copy.deepcopy(image.provenance),
            'asset_identity':digest(json_bytes({'content':identity,'image_artifact_id':image.provenance['artifact_id']}))}


def _manifest(questions,images):
    validate_manifest(questions)
    if questions['package_id']!='tryout-1' or tuple(x['question_id'] for x in questions['items'])!=ROSTER:
        raise StoreError('Image bundles support the reviewed tryout-1 roster only.')
    records={x['question_id']:x['record'] for x in questions['items']}
    if len(images)!=5 or {x.provenance.get('question_id') for x in images}!=IMAGE_IDS:
        raise StoreError('Bundle requires exactly the five reviewed question images.')
    assets=[_asset(records[image.provenance['question_id']],image) for image in images]
    data={'schema_version':1,'status':'LOCAL_RENDERED','package_id':'tryout-1',
          'seed':questions['seed'],'assets':assets}
    data['bundle_id']=digest(json_bytes({'questions':stable_questions(questions),'media':data}))
    return data


def generate_media_bundle(bank,configs,package_id: str,seed: int) -> MediaBundle:
    if package_id!='tryout-1':raise StoreError('Image bundles support tryout-1 only.')
    images=[]
    def capture(original,config,result,record):
        if original['id'] in IMAGE_IDS:
            template=load_template(original['id'])
            images.append(render_scene(template,build_scene(template,result.values)))
    questions=generate_package(bank,configs,package_id,seed,on_generated=capture)
    images=tuple(images)
    return MediaBundle(questions,images,_manifest(questions,images))


def build_preview(questions,assets) -> str:
    esc=html.escape
    by_question={a['question_id']:a for a in assets}
    sections=[]
    for index,item in enumerate(questions['items'],1):
        record=item['record'];asset=by_question.get(item['question_id'])
        # Paths are fixed content-addressed PNG references, never arbitrary URLs.
        picture=(f'<img src="{esc(asset["path"],quote=True)}" alt="{esc(asset["alt_text"],quote=True)}" width="{asset["width"]}" height="{asset["height"]}">' if asset else '')
        options=''.join(f'<li><b>{esc(o["id"])}.</b> {esc(o["text"])}</li>' for o in record['options'])
        sections.append(f'<section><h2>{index}. {esc(item["question_id"])}</h2>{picture}<p class="stem">{esc(record["stem"])}</p><ul>{options}</ul><details><summary>Kunci dan pembahasan (operator)</summary><p>Kunci: {esc(record["key"])}</p><pre>{esc(record["explanation"])}</pre></details></section>')
    return ('<!doctype html><html lang="id"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src \'self\' file:; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
            '<title>Tryout 1 - Preview lokal</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:900px;margin:32px auto;padding:0 20px;color:#172530;background:#f4f6f8}section{background:white;padding:24px;margin:24px 0;border:1px solid #d8e0e5}h2{font-size:18px}img{display:block;max-width:100%;height:auto;margin:20px auto}p.stem,li,pre{white-space:pre-wrap}pre{font:inherit}ul{list-style:none;padding:0}li{margin:8px 0}summary{cursor:pointer}details{margin-top:20px}</style></head><body>'
            f'<h1>Tryout 1 - Preview lokal</h1><p>30 soal, 5 gambar. Seed {questions["seed"]}. LOCAL_RENDERED; untuk review operator, belum publikasi.</p>'
            +''.join(sections)+'</body></html>')


def bundle_files(bundle: MediaBundle) -> dict[str,bytes]:
    """Validate mutable metadata and actual rendered bytes again at the export boundary."""
    try:
        expected=_manifest(bundle.questions,bundle.images)
        if bundle.media_manifest!=expected:raise StoreError('Bundle manifest or identity was modified.')
        records={x['question_id']:x['record'] for x in bundle.questions['items']}
        for image in bundle.images:
            provenance=image.provenance
            if provenance.get('status')!='LOCAL_RENDERED' or digest(image.png_bytes)!=image.sha256:
                raise StoreError('Image bytes or local status do not match provenance.')
            template=load_template(provenance['question_id'],provenance['template_version'])
            verified=render_scene(template,image.scene)
            if verified!=image:raise StoreError('Image, scene or renderer provenance is stale.')
            values=records[template.question_id]['values_used']
            for binding in template.bindings:
                value=dict(image.scene.bindings)[binding.name]
                if binding.expr is None and binding.name not in values:
                    raise StoreError('Image inputs are missing from the question record.')
                if binding.name in values and values[binding.name]!=json_number(value):
                    raise StoreError('Image bindings differ from question values.')
        questions=json_bytes(bundle.questions)
        preview=build_preview(bundle.questions,expected['assets']).encode('utf-8')
        manifest={**expected,'questions_sha256':digest(questions),'preview_sha256':digest(preview)}
        files={'questions.json':questions,'media-manifest.json':json_bytes(manifest),'preview.html':preview}
        for image in bundle.images:files[f'images/{image.sha256}.png']=image.png_bytes
        return files
    except StoreError:raise
    except (ValueError,KeyError,TypeError) as error:
        raise StoreError('Invalid local media bundle.') from error


def write_media_bundle(bundle: MediaBundle,output: Path) -> Path:
    from tryout_media_io import write_files
    return write_files(bundle_files(bundle),output)
