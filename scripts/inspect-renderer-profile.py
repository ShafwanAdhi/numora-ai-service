"""Print runtime identity for explicit review; never updates pins automatically."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'variant_gen'))
from image_variants.renderer import renderer_identity
identity=renderer_identity()
identity.pop('platform',None)
print(json.dumps(identity,indent=2,sort_keys=True))
