"""Immutable renderer inputs and output; no persistence or remote resources."""
from dataclasses import dataclass
from fractions import Fraction


class ImageVariantError(ValueError):
    """An asset, binding or layout cannot be safely rendered."""


@dataclass(frozen=True)
class BindingSpec:
    name: str
    expr: str | None = None
    fmt: str = 'id'
    decimals: int = 2
    number_type: str = 'integer'


@dataclass(frozen=True)
class LabelSpec:
    id: str
    text: str
    box: tuple[int, int, int, int]
    font_size: int
    min_font_size: int
    color: tuple[int, int, int] = (0, 0, 0)


@dataclass(frozen=True)
class PyramidSpec:
    apex: tuple[int, int]
    rim: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class PyramidGeometry:
    ratio: Fraction
    water: tuple[tuple[Fraction, Fraction], ...]
    surface_center: tuple[Fraction, Fraction]


@dataclass(frozen=True)
class ImageTemplate:
    question_id: str
    version: int
    width: int
    height: int
    bindings: tuple[BindingSpec, ...]
    constraints: tuple[str, ...]
    labels: tuple[LabelSpec, ...]
    alt_text: str
    base_bytes: bytes
    font_bytes: bytes
    source_sha256: str
    base_sha256: str
    font_sha256: str
    template_sha256: str
    definition_sha256: str
    renderer: str = 'labels-v1'
    geometry: PyramidSpec | None = None


@dataclass(frozen=True)
class SceneLabel:
    id: str
    text: str
    box: tuple[int, int, int, int]
    font_size: int
    # Coordinates and bounding box in the internal 2x canvas, not rounded floats.
    position: tuple[int, int]
    ink_box: tuple[int, int, int, int]
    color: tuple[int, int, int]


@dataclass(frozen=True)
class ImageScene:
    template_sha256: str
    bindings: tuple[tuple[str, int | Fraction], ...]
    labels: tuple[SceneLabel, ...]
    alt_text: str
    geometry: PyramidGeometry | None = None


@dataclass(frozen=True)
class RenderedImage:
    png_bytes: bytes
    sha256: str
    byte_length: int
    width: int
    height: int
    scene: ImageScene
    provenance: dict
