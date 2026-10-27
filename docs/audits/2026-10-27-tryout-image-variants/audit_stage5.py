"""Reproduce the 20-seed local bundle audit; no database or R2 access."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'variant_gen'))
sys.path.insert(0,str(ROOT/'variant_gen/tests'))
import cli
from bank import OriginalBank
from config_store import ConfigStore
from test_tryout import check_math
from tryout_media import generate_media_bundle,write_media_bundle
from image_variants import build_scene,load_template


def main():
    bank=OriginalBank(ROOT/'variant_gen/data/tryout-1/q0_bank.csv');configs=ConfigStore(ROOT/'variant_gen/configs')
    output=Path(__file__).resolve().parent/'stage-5';output.mkdir(exist_ok=True)
    scratch=ROOT/'.scratch/tryout-image-variants/stage5-seeds'
    evidence=[];real=cli.generate;oracle=unittest.TestCase()
    for seed in range(1,21):
        accepted={}
        def capture(original,config,seed,others):
            result=real(original,config,seed,others)
            accepted[original['id']]=result
            check_math(oracle,original['id'],result.values,result.cand)
            return result
        with patch.object(cli,'generate',side_effect=capture) as draws:
            bundle=generate_media_bundle(bank,configs,'tryout-1',seed)
        assert draws.call_count==27 and len(bundle.questions['items'])==30
        for image in bundle.images:
            qid=image.provenance['question_id']
            assert image.scene==build_scene(load_template(qid),accepted[qid].values)
            assert not {'ans','water','expected'} & dict(image.scene.bindings).keys()
            assert hashlib.sha256(image.png_bytes).hexdigest()==image.sha256
        destination=output/'bundle-s1' if seed==1 else scratch/f's{seed}'
        path=write_media_bundle(bundle,destination)
        manifest=json.loads((path/'media-manifest.json').read_bytes())
        for asset in manifest['assets']:
            assert hashlib.sha256((path/asset['path']).read_bytes()).hexdigest()==asset['sha256']
        evidence.append({'seed':seed,'questions':30,'generations':draws.call_count,'images':5,
                         'bundle_id':manifest['bundle_id'],
                         'output':str(path.relative_to(ROOT)),
                         'assets':[{key:a[key] for key in ('question_id','path','sha256','asset_identity','original_hash','original_version','config_hash','config_version')} for a in manifest['assets']]})
    report={'scope':'LOCAL_RENDERED only; no automatic import/publication','seeds':[1,20],
            'bundles':20,'questions':600,'engine_calls':540,'image_assets':100,
            'independent_math_checks':540,'seed_1_preview':'stage-5/bundle-s1/preview.html',
            'note':'Assets are occurrences, not claims of100 unique PNG contents or equal difficulty.',
            'runs':evidence}
    (output/'seed-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: 20 bundles, 600 questions, 540 single engine calls/math checks, 100 matched image assets.')


if __name__=='__main__':main()
