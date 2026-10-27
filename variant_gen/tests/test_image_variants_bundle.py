import copy
import io
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cli
from bank import OriginalBank
from config_store import ConfigStore,config_hash
from store import StoreError
from tryout import generate_package
try:
    import tryout_media as media
except ImportError:
    media=None


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(media,'Media bundle integration is not implemented')
        self.bank=OriginalBank(ROOT/'data/tryout-1/q0_bank.csv')
        self.configs=ConfigStore(ROOT/'configs')

    def bundle(self,seed=1):
        return media.generate_media_bundle(self.bank,self.configs,'tryout-1',seed)

    def test_bundle_has_30_questions_and_5_images(self):
        b=self.bundle()
        self.assertEqual(len(b.questions['items']),30)
        self.assertEqual(len(b.images),5)
        self.assertEqual(len(b.media_manifest['assets']),5)
        self.assertEqual(sum(x['status']=='ORIGINAL_ONLY' for x in b.questions['items']),3)
        self.assertEqual([sum(x['record']['classification']['chapter']==c for x in b.questions['items']) for c in (1,2,3,4)],[8,8,7,7])

    def test_renderer_receives_same_accepted_result_without_second_generate(self):
        results={};seen=[];real=cli.generate;render=media.build_scene
        def generate(orig,cfg,seed,others):
            r=real(orig,cfg,seed,others);results[orig['id']]=r;return r
        def scene(template,values):
            seen.append(template.question_id)
            self.assertIs(values,results[template.question_id].values)
            return render(template,values)
        with patch.object(cli,'generate',side_effect=generate) as draw,patch.object(media,'build_scene',side_effect=scene):
            self.bundle()
        self.assertEqual(draw.call_count,27)
        self.assertEqual(len(seen),5)

    def test_existing_preview_and_package_json_unchanged_without_callback(self):
        a=generate_package(self.bank,self.configs,'tryout-1',1)
        b=generate_package(self.bank,self.configs,'tryout-1',1,on_generated=lambda *args:None)
        self.assertEqual(media.stable_questions(a),media.stable_questions(b))

    def test_callback_cannot_mutate_question_or_accepted_values(self):
        def broken(orig,cfg,result,record):record['stem']='corrupted'
        with self.assertRaises(StoreError):cli.preview(self.bank,self.configs,'tryout-1-b3-q02',1,on_generated=broken)

    def test_output_reuse_checks_all_hashes_and_rejects_different_content(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'bundle';b=self.bundle()
            media.write_media_bundle(b,target)
            before=(target/'questions.json').read_bytes()
            second=self.bundle()
            for item in second.questions['items']:
                if 'created_at' in item['record']:item['record']['created_at']='2099-01-01T00:00:00+00:00'
            # Operational timestamps are excluded from stable content identity.
            self.assertEqual(media.write_media_bundle(second,target),target.resolve())
            self.assertEqual((target/'questions.json').read_bytes(),before)
            with self.assertRaises(StoreError):media.write_media_bundle(self.bundle(2),target)
            png=next((target/'images').glob('*.png'));png.write_bytes(b'broken')
            with self.assertRaises(StoreError):media.write_media_bundle(b,target)

    def test_missing_image_or_failed_render_leaves_no_final_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'bundle';b=self.bundle()
            with self.assertRaises(StoreError):media.write_media_bundle(replace(b,images=b.images[:-1]),target)
            self.assertFalse(target.exists())
            with patch.object(media,'render_scene',side_effect=ValueError('bad image')):
                with self.assertRaises(ValueError):self.bundle()
            self.assertFalse(target.exists())

    def test_failed_disk_write_leaves_no_final_or_staging_bundle(self):
        b=self.bundle();real=Path.open
        def opening(path,*args,**kwargs):
            if path.name=='preview.html' and args and args[0]=='xb':raise OSError('simulated disk failure')
            return real(path,*args,**kwargs)
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(Path,'open',opening),self.assertRaises(OSError):
                media.write_media_bundle(b,Path(folder)/'bundle')
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_bundle_paths_cannot_escape_root(self):
        b=copy.deepcopy(self.bundle());b.media_manifest['assets'][0]['path']='../escape.png'
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(StoreError):media.write_media_bundle(b,Path(folder)/'bundle')
            self.assertFalse((Path(folder)/'escape.png').exists())

    def test_preview_escapes_untrusted_text(self):
        b=self.bundle();questions=copy.deepcopy(b.questions)
        questions['items'][0]['record']['stem']='<script>alert(1)</script>'
        html=media.build_preview(questions,b.media_manifest['assets'])
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('<script>',html)

    def test_local_manifest_does_not_claim_r2_verified_or_contain_signed_urls(self):
        b=self.bundle();serialized=json.dumps(b.media_manifest)
        self.assertEqual(b.media_manifest['status'],'LOCAL_RENDERED')
        for forbidden in ('uploadUrl','objectKey','R2_VERIFIED','https://','base64'):
            self.assertNotIn(forbidden,serialized)
        bad=copy.deepcopy(b);bad.media_manifest['status']='R2_VERIFIED'
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(StoreError):media.write_media_bundle(bad,Path(folder)/'bundle')

    def test_same_seed_changed_config_cannot_reuse_stale_asset(self):
        a=self.bundle();real=self.configs.load
        def revised(qid,version=None):
            cfg,_=real(qid,version);cfg=copy.deepcopy(cfg);cfg['config_version']+=1
            return cfg,config_hash(cfg)
        with patch.object(self.configs,'load',side_effect=revised):b=self.bundle()
        self.assertNotEqual(a.media_manifest['bundle_id'],b.media_manifest['bundle_id'])
        for x,y in zip(a.media_manifest['assets'],b.media_manifest['assets']):
            self.assertNotEqual(x['asset_identity'],y['asset_identity'])

    def test_changed_template_cannot_reuse_stale_asset(self):
        import image_variants.templates as templates
        a=self.bundle();real=templates._read_inside
        def read(root,path):
            data=real(root,path)
            if path.name=='template.json':
                spec=json.loads(data);spec['authoring']['review_revision']='new';return json.dumps(spec).encode()
            return data
        with patch.object(templates,'_read_inside',side_effect=read):b=self.bundle()
        self.assertNotEqual(a.media_manifest['bundle_id'],b.media_manifest['bundle_id'])

    def test_cli_exports_explicit_output_only(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'bundle';output=io.StringIO()
            with patch('sys.stdout',output):
                result=cli.main(['package-media','tryout-1','s1','--bank',str(ROOT/'data/tryout-1/q0_bank.csv'),'--output',str(target)])
            self.assertEqual(result,0)
            self.assertEqual(len(list((target/'images').glob('*.png'))),5)
            self.assertTrue((target/'preview.html').is_file())


if __name__=='__main__':unittest.main()
