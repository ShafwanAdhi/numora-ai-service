"""Load five pinned Drill contracts into the existing ImageTemplate protocol."""
import io
import json
from dataclasses import dataclass, replace
from pathlib import Path

from image_variants.models import BindingSpec, ImageTemplate, ImageVariantError, LabelSpec
from image_variants.templates import _integer, _read_inside, canonical, definition_hash, sha256
from .registry import REVIEWED_RENDERER, REVIEWED_TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
IDS = ('pg-16-4-1', 'pg-16-4-3', 'pg-16-4-4', 'pg-16-5-3', 'pg-16-5-5')
SOURCE = ROOT.parent / 'docs/sources/incoming/2026-10-27-indikator-16-19-final-images'
TEMPLATES = ROOT / 'image_templates'


def snapshot_sha(value):
    return sha256((json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                             allow_nan=False) + '\n').encode('utf-8'))


@dataclass(frozen=True)
class DrillTemplate:
    image: ImageTemplate
    original_version: int
    original_hash: str
    original_full_sha256: str
    config_version: int
    config_hash: str
    config_snapshot_sha256: str
    config_file_sha256: str
    # (alias, raw-variable, original dimension) - no student text parsing.
    dimensions: tuple[tuple[str, str, int], ...]
    original_bindings: tuple[tuple[str, int], ...]


def load_template(question_id, version=1):
    if not isinstance(question_id, str) or question_id not in IDS or type(version) is not int or version != 1:
        raise ImageVariantError('Numerical Drill template/version is not supported')
    try:
        folder = TEMPLATES / question_id / 'v1'
        spec_bytes = _read_inside(TEMPLATES, folder / 'template.json')
        if sha256(spec_bytes) != REVIEWED_TEMPLATES[question_id]:
            raise ImageVariantError('Drill reviewed template pin mismatch; new review/version required')
        from image_variants.renderer import renderer_identity
        current = renderer_identity()
        if any(current.get(key) != value for key, value in REVIEWED_RENDERER.items()):
            raise ImageVariantError('Drill renderer pin mismatch; renderer review required')
        spec = json.loads(spec_bytes)
        if (spec['schema_version'] != 1 or spec['question_id'] != question_id
                or spec['template_version'] != 1 or spec['renderer'] != 'labels-v1'
                or spec['canvas'] != [960, 640]):
            raise ImageVariantError('Drill template identity or canvas mismatch')
        inventory_bytes = _read_inside(SOURCE, SOURCE / 'image-inventory.json')
        if sha256(inventory_bytes) != spec['source_inventory_sha256']:
            raise ImageVariantError('Drill source inventory pin changed')
        inventory = json.loads(inventory_bytes)
        source = next(a for a in inventory['assets'] if a['question_id'] == question_id)
        source_bytes = _read_inside(SOURCE, SOURCE / source['file'])
        pin = inventory['family_pins'][question_id]
        config = pin['configs'][0]
        expected = {'original_version': pin['original_version'], 'original_hash': pin['original_hash'],
                    'original_full_sha256': pin['original_full_sha256'],
                    'config_version': config['version'], 'config_hash': config['config_hash'],
                    'config_snapshot_sha256': snapshot_sha(config['config_snapshot']),
                    'config_file_sha256': config['file_sha256']}
        if spec['compatibility'] != expected or spec['source_sha256'] != sha256(source_bytes):
            raise ImageVariantError('Drill source/content compatibility mismatch')
        base = _read_inside(TEMPLATES, folder / 'base.png')
        for name, digest in spec.get('prepared_asset_sha256', {}).items():
            if name != 'cleaned-source.png' or sha256(_read_inside(TEMPLATES, folder / name)) != digest:
                raise ImageVariantError('Drill prepared asset integrity mismatch')
        font = _read_inside(TEMPLATES, TEMPLATES / 'fonts/DejaVuSans.ttf')
        font_manifest = json.loads(_read_inside(TEMPLATES, TEMPLATES / 'fonts/manifest.json'))
        license_bytes = _read_inside(TEMPLATES, TEMPLATES / 'fonts/LICENSE.txt')
        if (sha256(base) != spec['base_sha256'] or sha256(font) != spec['font_sha256']
                or sha256(font) != font_manifest['sha256']
                or sha256(license_bytes) != font_manifest['license_sha256']):
            raise ImageVariantError('Drill template/font integrity mismatch')
        from PIL import Image
        with Image.open(io.BytesIO(base)) as png:
            if png.format != 'PNG' or png.size != (960, 640):
                raise ImageVariantError('Invalid Drill base PNG')
            png.load()
        bindings = tuple(BindingSpec(**b) for b in spec['bindings'])
        labels = tuple(LabelSpec(**{**label, 'box': tuple(label['box']),
                                    'color': tuple(label.get('color', (0, 0, 0)))})
                       for label in spec['labels'])
        if (not 1 <= len(bindings) <= 8 or not 1 <= len(labels) <= 16
                or len({b.name for b in bindings}) != len(bindings)
                or len({label.id for label in labels}) != len(labels)):
            raise ImageVariantError('Invalid Drill bindings/labels')
        for binding in bindings:
            if binding.number_type not in ('integer', 'rational') or binding.fmt not in ('id', 'raw', 'mixed'):
                raise ImageVariantError('Invalid Drill binding format')
        for label in labels:
            if not isinstance(label.text, str) or len(label.text) > 500 or len(label.box) != 4:
                raise ImageVariantError('Invalid Drill label')
            x0, y0, x1, y1 = label.box
            for value in label.box:
                _integer(value, 0, 960)
            if not (0 <= x0 < x1 <= 960 and 0 <= y0 < y1 <= 640):
                raise ImageVariantError('Drill label escapes canvas')
            _integer(label.font_size, 5, 72)
            _integer(label.min_font_size, 5, label.font_size)
            if len(label.color) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in label.color):
                raise ImageVariantError('Invalid Drill label color')
        image = ImageTemplate(question_id, 1, 960, 640, bindings, tuple(spec['constraints']),
                              labels, spec['alt_text'], base, font, spec['source_sha256'],
                              spec['base_sha256'], spec['font_sha256'], sha256(canonical(spec)), '')
        image = replace(image, definition_sha256=definition_hash(image))
        dimensions = tuple((d['alias'], d['variable'], d['original']) for d in spec['dimensions'])
        return DrillTemplate(image, **expected, dimensions=dimensions,
                             original_bindings=tuple(spec['original_bindings'].items()))
    except ImageVariantError:
        raise
    except (OSError, KeyError, ValueError, TypeError, StopIteration) as exc:
        raise ImageVariantError('Cannot load pinned numerical Drill template') from exc
