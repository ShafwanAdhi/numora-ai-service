"""Static conceptual geometry follows content identity, never random seed selection."""
import io
import json
from dataclasses import dataclass, replace
from pathlib import Path

from conceptual_stock import stock_record
from engine import original_record
from image_variants import ImageVariantError, build_scene, render_scene
from image_variants.models import ImageTemplate, LabelSpec
from image_variants.templates import _read_inside, canonical, definition_hash, sha256
from drill_images.registry import REVIEWED_RENDERER
from drill_images.templates import snapshot_sha
from .registry import REVIEWED_SCENARIOS

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'image_templates'
SOURCE = ROOT.parent / 'docs/sources/incoming/2026-10-27-indikator-16-19-final-images'
IDS = ('pg-16-4-2', 'mcma-16-4-6', 'mcma-16-4-7', 'pg-16-5-1')


@dataclass(frozen=True)
class ConceptScenario:
    image: ImageTemplate
    original_version: int
    original_hash: str
    original_full_sha256: str
    stock_variant_id: str | None
    stock_version: int | None
    stock_content_sha256: str | None
    geometry: dict


def scenario_name(qid, variant_id):
    if not isinstance(qid, str) or qid not in IDS:
        raise ImageVariantError('Conceptual image question is not supported')
    if variant_id is None: return 'original'
    if type(variant_id) is not str or variant_id not in (qid+':stock-01', qid+':stock-02'):
        raise ImageVariantError('Conceptual image stock must belong to the selected question')
    return variant_id.rsplit(':', 1)[1]


def load_scenario(question_id, stock_variant_id=None):
    name = scenario_name(question_id, stock_variant_id)
    try:
        folder = TEMPLATES / question_id / 'v1'
        spec_bytes = _read_inside(TEMPLATES, folder / (name+'.json'))
        if sha256(spec_bytes) != REVIEWED_SCENARIOS[question_id+':'+name]:
            raise ImageVariantError('Conceptual reviewed template pin mismatch')
        from image_variants.renderer import renderer_identity
        current = renderer_identity()
        if any(current.get(key) != value for key, value in REVIEWED_RENDERER.items()):
            raise ImageVariantError('Conceptual renderer pin mismatch')
        spec = json.loads(spec_bytes)
        if (spec['schema_version'] != 1 or spec['question_id'] != question_id
                or spec['template_version'] != 1 or spec['scenario'] != name
                or spec['canvas'] != [960,640] or spec['renderer'] != 'labels-v1'):
            raise ImageVariantError('Conceptual template identity mismatch')
        inventory_bytes = _read_inside(SOURCE, SOURCE/'image-inventory.json')
        if sha256(inventory_bytes) != spec['source_inventory_sha256']:
            raise ImageVariantError('Conceptual source inventory pin mismatch')
        inventory = json.loads(inventory_bytes)
        pin = inventory['family_pins'][question_id]
        asset = next(a for a in inventory['assets'] if a['question_id'] == question_id)
        if sha256(_read_inside(SOURCE,SOURCE/asset['file'])) != spec['source_sha256']:
            raise ImageVariantError('Conceptual source image pin mismatch')
        stock = next((s for s in pin['stocks'] if s['variant_id'] == stock_variant_id), None)
        expected = {'original_version':pin['original_version'], 'original_hash':pin['original_hash'],
                    'original_full_sha256':pin['original_full_sha256'],
                    'stock_variant_id':stock_variant_id,
                    'stock_version':stock['stock_version'] if stock else None,
                    'stock_content_sha256':stock['content_sha256'] if stock else None}
        if spec['compatibility'] != expected or (stock_variant_id is not None and stock is None):
            raise ImageVariantError('Conceptual content compatibility pin mismatch')
        base = _read_inside(TEMPLATES,folder/(name+'.png'))
        font = _read_inside(TEMPLATES,TEMPLATES/'fonts/DejaVuSans.ttf')
        license_bytes = _read_inside(TEMPLATES,TEMPLATES/'fonts/LICENSE.txt')
        font_manifest = json.loads(_read_inside(TEMPLATES,TEMPLATES/'fonts/manifest.json'))
        if (sha256(base) != spec['base_sha256'] or sha256(font) != spec['font_sha256']
                or sha256(font) != font_manifest['sha256']
                or sha256(license_bytes) != font_manifest['license_sha256']):
            raise ImageVariantError('Conceptual base/font integrity mismatch')
        from PIL import Image
        with Image.open(io.BytesIO(base)) as png:
            if png.format != 'PNG' or png.size != (960,640):
                raise ImageVariantError('Conceptual PNG identity mismatch')
            png.load()
        labels = tuple(LabelSpec(**{**label,'box':tuple(label['box'])}) for label in spec['labels'])
        if len({label.id for label in labels}) != len(labels) or not 1 <= len(labels) <= 40:
            raise ImageVariantError('Invalid conceptual labels')
        for label in labels:
            x0,y0,x1,y1=label.box
            if (not 0<=x0<x1<=960 or not 0<=y0<y1<=640
                    or not 5<=label.min_font_size<=label.font_size<=72
                    or not isinstance(label.text,str) or len(label.text)>500):
                raise ImageVariantError('Invalid conceptual label layout')
        image=ImageTemplate(question_id,1,960,640,(),(),labels,spec['alt_text'],base,font,
                            spec['source_sha256'],spec['base_sha256'],spec['font_sha256'],
                            sha256(canonical(spec)),'')
        image=replace(image,definition_sha256=definition_hash(image))
        return ConceptScenario(image,**expected,geometry=spec['geometry'])
    except ImageVariantError: raise
    except (OSError,KeyError,ValueError,TypeError,StopIteration) as exc:
        raise ImageVariantError('Cannot load pinned conceptual image scenario') from exc


def preview(bank, stocks, question_id, stock_variant_id=None):
    scenario=load_scenario(question_id,stock_variant_id)
    original=bank.get(question_id)
    if (original['version']!=scenario.original_version or original['hash']!=scenario.original_hash
            or snapshot_sha(original)!=scenario.original_full_sha256):
        raise ImageVariantError('Conceptual original pin mismatch; review required')
    if stock_variant_id is None:
        record=original_record(original)
    else:
        selected=[s for s in stocks.get(question_id,[]) if s.get('variant_id')==stock_variant_id]
        if (len(selected)!=1 or selected[0].get('stock_version')!=scenario.stock_version
                or snapshot_sha(selected[0])!=scenario.stock_content_sha256):
            raise ImageVariantError('Conceptual stock pin mismatch; review required')
        record=stock_record(original,selected[0])
    image=render_scene(scenario.image,build_scene(scenario.image,{}))
    content={'mode':'stock' if stock_variant_id else 'original','record_id':record['record_id'],
             'record_sha256':snapshot_sha(record),'original_version':scenario.original_version,
             'original_hash':scenario.original_hash,'original_full_sha256':scenario.original_full_sha256,
             'stock_variant_id':stock_variant_id,'stock_version':scenario.stock_version,
             'stock_content_sha256':scenario.stock_content_sha256}
    folder=Path(__file__).parent
    code=b'\n'.join(p.read_bytes().replace(b'\r\n',b'\n') for p in sorted(folder.glob('*.py')))
    provenance={**image.provenance,'render_artifact_id':image.provenance['artifact_id'],
                'content':content,'adapter':{'version':'drill-concept-images-v1','code_sha256':sha256(code)}}
    provenance.pop('artifact_id');provenance['artifact_id']=sha256(canonical(provenance))
    return record,replace(image,provenance=provenance)
