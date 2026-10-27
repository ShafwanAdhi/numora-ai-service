"""Bind exact accepted values and measure every label before drawing."""
import io
from fractions import Fraction
from functools import lru_cache

from expr import ExprError, RejectDraw, evaluate, is_num, norm, render
from .models import ImageScene, ImageTemplate, ImageVariantError, SceneLabel
from .templates import definition_hash, sha256

SCALE = 2


@lru_cache(maxsize=32)
def _font_bytes(font_bytes, size):
    from PIL import ImageFont
    return ImageFont.truetype(io.BytesIO(font_bytes), size * SCALE,
                              layout_engine=ImageFont.Layout.BASIC)


def _font(template, size):
    return _font_bytes(template.font_bytes, size)


def measure_label(template, label, text) -> SceneLabel:
    """Measure a label, including domain-boundary strings, without rendering a PNG."""
    from PIL import Image, ImageDraw
    draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    x0, y0, x1, y1 = (n * SCALE for n in label.box)
    for size in range(label.font_size, label.min_font_size - 1, -1):
        bounds = draw.multiline_textbbox((0, 0), text, font=_font(template, size),
                                         spacing=2*SCALE, align='center')
        w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
        if w <= x1-x0-2*SCALE and h <= y1-y0-2*SCALE:
            break
    else:
        raise ImageVariantError(f'Label {label.id} does not fit reviewed layout')
    left, top = x0+(x1-x0-w)//2, y0+(y1-y0-h)//2
    return SceneLabel(label.id, text, label.box, size,
                      (left-bounds[0], top-bounds[1]),
                      (left, top, left+w, top+h), label.color)


def verify_assets(template):
    if (definition_hash(template) != template.definition_sha256
            or sha256(template.base_bytes) != template.base_sha256
            or sha256(template.font_bytes) != template.font_sha256):
        raise ImageVariantError('Template/font asset integrity mismatch')


def build_scene(template: ImageTemplate, values: dict) -> ImageScene:
    verify_assets(template)
    if not isinstance(values, dict):
        raise ImageVariantError('Image values must be an accepted value dictionary')
    bound = {}
    try:
        for binding in template.bindings:
            value = (evaluate(binding.expr, bound) if binding.expr is not None
                     else values[binding.name])
            if (not is_num(value) or not 0 < value <= 10**12
                    or (binding.number_type=='integer' and Fraction(value).denominator!=1)):
                raise ImageVariantError(f'Binding {binding.name} requires an exact positive {binding.number_type}')
            if binding.name in values and not is_num(values[binding.name]):
                raise ImageVariantError(f'Binding {binding.name} must not use rounded float values')
            if binding.expr is not None and binding.name in values and values[binding.name] != value:
                raise ImageVariantError(f'Inconsistent derived binding {binding.name}')
            bound[binding.name] = norm(value)
        for constraint in template.constraints:
            if not evaluate(constraint, bound):
                raise ImageVariantError(f'Image constraint failed: {constraint}')
        formats = {b.name: {'fmt': b.fmt, 'decimals': b.decimals} for b in template.bindings}
        alt_text = render(template.alt_text, bound, formats)
        labels = []
        for label in template.labels:
            text = render(label.text, bound, formats)
            labels.append(measure_label(template, label, text))
        geometry=None
        if template.geometry is not None:
            from .geometry import build_pyramid_geometry
            geometry=build_pyramid_geometry(template.geometry,bound['ratio'])
        return ImageScene(template.template_sha256, tuple(bound.items()), tuple(labels), alt_text,geometry)
    except ImageVariantError:
        raise
    except (KeyError, TypeError, ValueError, ExprError, RejectDraw, OSError) as exc:
        raise ImageVariantError('Invalid image binding or font layout') from exc
