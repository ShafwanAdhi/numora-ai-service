"""Load only reviewed, content-pinned templates and bundled font bytes."""
import hashlib
import io
import json
import re
from dataclasses import asdict, replace
from pathlib import Path

from .models import BindingSpec, ImageTemplate, ImageVariantError, LabelSpec, PyramidSpec

TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / 'image_templates'
SUPPORTED = frozenset(('tryout-1-b3-q02', 'tryout-1-b3-q03', 'tryout-1-b3-q04',
                       'tryout-1-b3-q06', 'tryout-1-b4-q05'))
DIMENSIONS = {'tryout-1-b3-q02': (489, 240), 'tryout-1-b3-q03': (648, 318),
              'tryout-1-b3-q04': (653, 313), 'tryout-1-b3-q06': (646, 318),
              'tryout-1-b4-q05': (292, 255)}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def definition_hash(template: ImageTemplate) -> str:
    """Pin effective frozen fields, not just the file from which they were read."""
    fields = {name: getattr(template, name) for name in (
        'question_id', 'version', 'width', 'height', 'constraints', 'alt_text',
        'source_sha256', 'base_sha256', 'font_sha256', 'template_sha256', 'renderer')}
    fields['bindings'] = [asdict(b) for b in template.bindings]
    fields['labels'] = [asdict(label) for label in template.labels]
    fields['geometry'] = asdict(template.geometry) if template.geometry else None
    return sha256(canonical(fields))


def _read_inside(root: Path, path: Path) -> bytes:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ImageVariantError('Template asset escapes its root')
    return resolved.read_bytes()


def _integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ImageVariantError('Invalid template integer')
    return value


def load_template(question_id: str, version: int | None = None) -> ImageTemplate:
    if not isinstance(question_id, str) or question_id not in SUPPORTED:
        raise ImageVariantError('Unknown image template')
    if version is not None:
        _integer(version, 1, 100000)
    try:
        folder = TEMPLATE_ROOT / question_id
        if version is None:
            versions = [int(p.name[1:]) for p in folder.glob('v*')
                        if p.is_dir() and re.fullmatch(r'v[1-9][0-9]{0,5}', p.name)]
            if not versions:
                raise ImageVariantError('Image template is not implemented yet')
            version = max(versions)
        directory = folder / f'v{version}'
        spec_bytes = _read_inside(TEMPLATE_ROOT, directory / 'template.json')
        spec = json.loads(spec_bytes)
        if (spec['schema_version'] != 1 or spec['question_id'] != question_id
                or spec['template_version'] != version or spec['renderer'] not in ('labels-v1','pyramid-v1')
                or tuple(spec['canvas']) != DIMENSIONS[question_id]):
            raise ImageVariantError('Template identity or canvas mismatch')
        width, height = spec['canvas']
        geometry=None
        if spec['renderer']=='pyramid-v1':
            if question_id!='tryout-1-b3-q04':
                raise ImageVariantError('Pyramid geometry belongs to its reviewed question')
            geometry=PyramidSpec(tuple(spec['geometry']['apex']),tuple(tuple(v) for v in spec['geometry']['rim']))
            if len(geometry.apex)!=2 or len(geometry.rim)!=4 or any(len(v)!=2 for v in geometry.rim):
                raise ImageVariantError('Invalid pyramid vertices')
            for x,y in (geometry.apex,*geometry.rim):
                _integer(x,0,width-1);_integer(y,0,height-1)
            if len(set(geometry.rim))!=4 or not all(y<geometry.apex[1] for x,y in geometry.rim):
                raise ImageVariantError('Pyramid rim must be above the bottom apex')
            turns=[]
            for i in range(4):
                a,b,c=(geometry.rim[(i+k)%4] for k in (0,1,2))
                turns.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
            if not (all(t>0 for t in turns) or all(t<0 for t in turns)):
                raise ImageVariantError('Pyramid rim must be a nondegenerate convex quadrilateral')
        elif 'geometry' in spec:
            raise ImageVariantError('Unexpected template geometry')
        base = _read_inside(TEMPLATE_ROOT, directory / 'base.png')
        font_manifest = json.loads(_read_inside(TEMPLATE_ROOT, TEMPLATE_ROOT / 'fonts/manifest.json'))
        # File names are fixed; a template cannot supply filesystem paths or URLs.
        font = _read_inside(TEMPLATE_ROOT, TEMPLATE_ROOT / 'fonts/DejaVuSans.ttf')
        license_bytes = _read_inside(TEMPLATE_ROOT, TEMPLATE_ROOT / 'fonts/LICENSE.txt')
        if (sha256(base) != spec['base_sha256'] or sha256(font) != spec['font_sha256']
                or sha256(font) != font_manifest['sha256']
                or sha256(license_bytes) != font_manifest['license_sha256']):
            raise ImageVariantError('Template/font asset integrity mismatch')
        source_manifest = json.loads((TEMPLATE_ROOT.parents[1] / 'docs/sources/incoming/2026-10-26-tryout-images/image-manifest.json').read_text(encoding='utf-8'))
        source = next(x for x in source_manifest['images'] if x['candidate_local_question_id'] == question_id)
        if source['image_sha256'] != spec['source_sha256']:
            raise ImageVariantError('Original image provenance mismatch')
        from PIL import Image
        with Image.open(io.BytesIO(base)) as image:
            if image.format != 'PNG' or image.size != (width, height):
                raise ImageVariantError('Invalid template PNG dimensions')
            image.load()
        bindings = tuple(BindingSpec(**b) for b in spec['bindings'])
        labels = tuple(LabelSpec(**{**label, 'box': tuple(label['box']),
                                   'color': tuple(label.get('color', (0, 0, 0)))})
                       for label in spec['labels'])
        if not 1 <= len(bindings) <= 20 or not 1 <= len(labels) <= 20:
            raise ImageVariantError('Invalid template size')
        if len({b.name for b in bindings}) != len(bindings) or len({l.id for l in labels}) != len(labels):
            raise ImageVariantError('Duplicate template binding/label')
        for b in bindings:
            if (not re.fullmatch(r'[a-z][a-z0-9_]{0,30}', b.name) or b.fmt not in ('id', 'raw', 'mixed')
                    or b.number_type not in ('integer','rational')):
                raise ImageVariantError('Invalid template binding')
        for label in labels:
            if len(label.box) != 4 or not isinstance(label.text, str) or len(label.text) > 500:
                raise ImageVariantError('Invalid label layout')
            x0, y0, x1, y1 = label.box
            for n in label.box:
                _integer(n, 0, max(width, height))
            if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
                raise ImageVariantError('Label box is outside canvas')
            _integer(label.font_size, 5, 72)
            _integer(label.min_font_size, 5, label.font_size)
            if len(label.color) != 3:
                raise ImageVariantError('Invalid label color')
            for component in label.color:
                _integer(component, 0, 255)
        template = ImageTemplate(question_id, version, width, height, bindings,
                             tuple(spec['constraints']), labels, spec['alt_text'], base, font,
                             spec['source_sha256'], spec['base_sha256'], spec['font_sha256'],
                             sha256(canonical(spec)), '',spec['renderer'],geometry)
        return replace(template, definition_sha256=definition_hash(template))
    except ImageVariantError:
        raise
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        raise ImageVariantError('Cannot load verified image template') from exc
