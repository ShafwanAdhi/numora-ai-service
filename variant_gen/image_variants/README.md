# Local Tryout image renderer — stages 1–5

Five templates are available: `tryout-1-b4-q05` (dice), `tryout-1-b3-q02`
(garden), `tryout-1-b3-q06` (tanks), `tryout-1-b3-q03` (angles), and
`tryout-1-b3-q04` (pyramid with dynamic water). An opt-in local package command
now exports 30 questions and five images; production compute/R2 integration
remains later work. This module does not change math configs.

From the AI repository root:

```powershell
python -m pip install -r requirements-image.txt
python -B variant_gen/cli.py package-media tryout-1 s1 --output .scratch/tryout-media-s1
python docs/audits/2026-10-27-tryout-image-variants/render_examples.py
python docs/audits/2026-10-27-tryout-image-variants/render_stage34_examples.py
python -m unittest discover -s variant_gen/tests -p 'test_image_variants_*.py' -v
```

The example exporter explicitly writes local PNGs, contact sheets and scene
evidence to the audit directory. Importing/building/rendering itself writes
nothing. Core CLI and workbench retain their existing behavior.

`package-media` writes `questions.json`, `media-manifest.json`, five hashed PNG
references and `preview.html` to the explicitly named output directory. Retry
verifies/reuses the first matching bundle; different or corrupted contents are
rejected. See [the integration handoff](../../docs/handoffs/TRYOUT_IMAGE_VARIANTS.md).

To render from an accepted generator result (imports use `variant_gen` on
`sys.path`, following the existing engine modules):

```python
from image_variants import load_template, build_scene, render_scene

# result is the SAME engine.generate result used for the question text.
template = load_template(original['id'])
scene = build_scene(template, result.values)
image = render_scene(template, scene)
# image.png_bytes is PNG data; only an explicit caller writes it to disk.
```

Input values must be exact integers or `Fraction` values, not floats or numbers
recovered from the rendered stem. Integer bindings reject nonintegral fractions;
the pyramid ratio explicitly supports rational values and uses mixed-fraction
formatting. Unused variables such as the dice
and tank `threshold` do not affect pixels. Derived width/diameter bindings are
checked against supplied values, and missing/invalid bindings fail explicitly.

Templates and font are local, versioned and hashed. Label-only patches were
cleaned using built-in imagegen once; no image model is called at runtime.
For dice, garden, tanks and angles, pixels outside reviewed erasure regions
remain identical to the original source. The pyramid uses a native geometry
redraw on a blank grid: water vertices follow `P + (p/q) * (V-P)`, so original
water/labels cannot remain in its background. Runtime text uses the bundled DejaVu Sans font and shared
generator formatter; output identity includes effective template fields,
renderer/formatter sources, Pillow/FreeType/zlib/build information and PNG hash.

The returned provenance is a regular dictionary for local serialization.
Treat it as read-only. `LOCAL_RENDERED` is not a VERIFIED R2 receipt, publication
approval, or a server authorization decision. No production consumer is enabled
by these stages; a future exporter/service must independently validate provenance
and actual media receipts rather than trusting a caller-supplied status.
