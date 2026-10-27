"""Pure PNG rendering from reviewed templates; no random draws or file writes."""
import io
import platform
from fractions import Fraction
from pathlib import Path

from .models import ImageScene, ImageTemplate, ImageVariantError, RenderedImage
from .scene import SCALE, _font, build_scene, verify_assets
from .templates import canonical, sha256


def renderer_identity() -> dict:
    import PIL
    from PIL import Image, _imagingft, features
    root = Path(__file__).parent
    code = b'\n'.join(p.read_bytes().replace(b'\r\n', b'\n')
                      for p in sorted(root.glob('*.py')))
    return {'version': 'tryout-images-v2', 'code_sha256': sha256(code),
            'formatter_sha256': sha256((root.parent/'expr.py').read_bytes().replace(b'\r\n', b'\n')),
            'pillow': PIL.__version__, 'freetype': features.version_module('freetype2'),
            'zlib': features.version_codec('zlib'), 'platform': platform.platform(),
            'pillow_core_sha256': sha256(Path(Image.core.__file__).read_bytes()),
            'pillow_font_core_sha256': sha256(Path(_imagingft.__file__).read_bytes()),
            'python': platform.python_version(), 'layout_engine': 'BASIC',
            'scale': SCALE, 'resampling': 'LANCZOS', 'png_compress_level': 9}


def render_scene(template: ImageTemplate, scene: ImageScene) -> RenderedImage:
    verify_assets(template)
    if scene.template_sha256 != template.template_sha256:
        raise ImageVariantError('Scene belongs to another template')
    # Regenerating layout is deterministic validation, not a second question draw.
    if scene != build_scene(template, dict(scene.bindings)):
        raise ImageVariantError('Scene labels, geometry or alt text are inconsistent')
    from PIL import Image, ImageDraw
    try:
        with Image.open(io.BytesIO(template.base_bytes)) as base:
            image = base.convert('RGB').resize((template.width*SCALE, template.height*SCALE), Image.Resampling.LANCZOS)
        if template.geometry is not None:
            from .geometry import draw_pyramid
            image=draw_pyramid(image,template.geometry,scene.geometry,SCALE)
        draw = ImageDraw.Draw(image)
        for label in scene.labels:
            draw.multiline_text(label.position, label.text, font=_font(template, label.font_size),
                                fill=label.color, spacing=2*SCALE, align='center')
        image = image.resize((template.width, template.height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format='PNG', compress_level=9, optimize=False)
        data = output.getvalue()
        if not 0 < len(data) <= 5 * 1024 * 1024:
            raise ImageVariantError('Rendered PNG exceeds 5 MiB')
        exact = {k: {'numerator': Fraction(v).numerator, 'denominator': Fraction(v).denominator}
                 for k, v in scene.bindings}
        provenance = {'status': 'LOCAL_RENDERED', 'question_id': template.question_id,
                      'template_version': template.version, 'template_sha256': template.template_sha256,
                      'source_sha256': template.source_sha256, 'base_sha256': template.base_sha256,
                      'font_sha256': template.font_sha256, 'renderer': renderer_identity(),
                      'definition_sha256': template.definition_sha256,
                      'png_sha256': sha256(data), 'byte_length': len(data),
                      'bindings': exact, 'bindings_sha256': sha256(canonical(exact)),
                      'alt_text': scene.alt_text, 'width': template.width, 'height': template.height}
        provenance['artifact_id'] = sha256(canonical(provenance))
        return RenderedImage(data, sha256(data), len(data), template.width, template.height,
                             scene, provenance)
    except ImageVariantError:
        raise
    except (OSError, ValueError) as exc:
        raise ImageVariantError('PNG rendering failed') from exc
