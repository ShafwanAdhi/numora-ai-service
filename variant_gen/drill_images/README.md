# Numerical Drill image adapter

Opt-in Python API for five reviewed numerical families. Stage 2 only: this is not
yet connected to the workbench, compute API, database, R2, or conceptual stock.

```python
import sys
from pathlib import Path
sys.path.insert(0, 'variant_gen')
from bank import load_workspace_bank
from config_store import ConfigStore
from drill_images import preview

bank = load_workspace_bank(Path('variant_gen/data/q0_bank.csv'))
configs = ConfigStore(Path('variant_gen/configs'))
record, image = preview(bank, configs, 'pg-16-4-1', seed=1)
print(record['stem'])
# Explicit caller-controlled save, never an implicit runtime cache:
Path('drill-preview.png').write_bytes(image.png_bytes)
```

`preview(bank, configs, question_id, seed=0)` returns the unmodified existing
record plus a `RenderedImage`. Seed 0 uses `original_record`; positive seeds use
one `cli.preview` accepted-result callback. A layout failure raises immediately,
with no image fallback or new random draw.

`render_accepted(original, config, result, record, *, config_path=None)` reads
raw accepted values, checks their exact types and pinned formulas, validates
the record, then maps dimensions to ImageScene bindings. `build_values` and
`assemble` are used only for deterministic integrity checks with the existing k;
they do not draw variables or invoke the RNG.

`render_original(original, config, *, config_path=None)` uses pinned original
dimensions without creating or accepting a k=0 candidate. `config_path` defaults
to the canonical local v1 config; preview supplies the ConfigStore's actual path.

All configs remain v1 with k=0..30. Existing filters accept k=1..30; there are
30 variants per family, not unlimited unique images. Dimensions scale uniformly,
so a fixed net geometry with variable labels is appropriate throughout the domain.

## Integrity boundaries

- registry.py externally pins the exact template JSON and reviewed rendering
  code, formatter, Pillow/FreeType/zlib builds, font engine, Python version and PNG settings.
- Template compatibility pins the full original snapshot (including explanation
  and metadata), runtime original hash/version, complete config snapshot/hash,
  exact config bytes, staged source inventory, image bytes, prepared base/font
  and optional cleaned-source assets.
- A version/hash mismatch fails closed. Do not auto-refresh the registry after
  config, template, Python or renderer upgrades: review and version the affected
  template explicitly. OS display name is provenance only; rendering builds are pinned.
- Images keep core render provenance and add a separate content/adapter identity.
  The common Tryout renderer and its existing artifact identities are untouched.
- PNGs, geometry, labels and source-preservation masks are deterministic. The
  image model was used only once during preparation of two blank-label assets.
  Runtime generation has no model/network/storage calls.

On pg-16-5-5, bind side/face height from v2/v4 (10 and 13 times k+1), not v9.
Its original key D and generated key C are unchanged. On pg-16-5-3 only slant
and the supplied 150-degree angle appear; the radius being asked is not exposed.

Static review artifacts, per-k seed mapping and independent mathematical checks
are under docs/audits/2026-10-27-drill-image-variants/stage-2. This is engineering
review evidence, not publication, academic approval, or IRT equivalence.
