"""Explicit review export is immutable, complete and separate from Tryout packages."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from bank import load_workspace_bank
from config_store import ConfigStore
from conceptual_stock import load_stock
from store import StoreError
from tryout_media import digest,json_bytes
from drill_media_review import build_review, verify_review_files, write_review
from drill_media_review import _preview
from tryout_media import stable_questions


class DrillMediaReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=load_workspace_bank(ROOT/'data/q0_bank.csv')
        cls.configs=ConfigStore(ROOT/'configs')
        cls.stock=load_stock(ROOT/'data/conceptual_stock.json',cls.bank)
        cls.files=build_review(cls.bank,cls.configs,cls.stock,seed=7)

    def test_seed_review_has_22_cases_nine_families_and_no_base64(self):
        summary=verify_review_files(self.files)
        self.assertEqual(summary['cases'],22)
        self.assertEqual(summary['families'],9)
        questions=json.loads(self.files['questions.json'])
        self.assertEqual(questions['kind'],'DRILL_IMAGE_REVIEW')
        self.assertNotIn('package_id',questions)
        self.assertEqual(sum(i['mode']=='original' for i in questions['items']),9)
        self.assertEqual(sum(i['mode']=='generator' for i in questions['items']),5)
        self.assertEqual(sum(i['mode']=='stock' for i in questions['items']),8)
        self.assertNotIn(b'"base64"',self.files['media-manifest.json'])

    def test_build_has_no_implicit_writes_or_database(self):
        with patch.object(Path,'write_bytes',side_effect=AssertionError('No implicit writes')),patch(
                'database.connection',side_effect=AssertionError('No database')):
            files=build_review(self.bank,self.configs,self.stock,seed=7)
        self.assertEqual(verify_review_files(files)['bundle_id'],verify_review_files(self.files)['bundle_id'])

    def test_tampered_png_preview_record_or_roster_is_rejected(self):
        png=next(name for name in self.files if name.startswith('images/'))
        for name in (png,'preview.html','questions.json'):
            files=dict(self.files);files[name]=files[name]+b'changed'
            with self.subTest(name=name),self.assertRaises(StoreError):verify_review_files(files)
        files=dict(self.files);files['../outside.png']=b'bad'
        with self.assertRaises(StoreError):verify_review_files(files)

    def test_atomic_write_retry_preserves_first_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'review'
            write_review(self.files,out)
            before={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
            write_review(self.files,out)
            self.assertEqual(before,{p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()})
            retry=dict(self.files);questions=json.loads(retry['questions.json'])
            next(i['record'] for i in questions['items'] if i['mode']=='generator')['created_at']='2099-01-01T00:00:00+00:00'
            retry['questions.json']=json_bytes(questions)
            manifest=json.loads(retry['media-manifest.json']);manifest['questions_sha256']=digest(retry['questions.json'])
            retry['media-manifest.json']=json_bytes(manifest)
            write_review(retry,out)
            self.assertEqual((out/'questions.json').read_bytes(),before['questions.json'])
            self.assertEqual(list(Path(temp).iterdir()),[out])

    def test_different_or_corrupted_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'review';write_review(self.files,out)
            target=out/'preview.html';target.write_bytes(b'keep me')
            with self.assertRaises(StoreError):write_review(self.files,out)
            self.assertEqual(target.read_bytes(),b'keep me')

    def test_invalid_seed_rejected(self):
        for seed in (0,True,-1,1.5):
            with self.assertRaises(StoreError):build_review(self.bank,self.configs,self.stock,seed=seed)

    def test_different_valid_seed_review_cannot_replace_existing_output(self):
        other=build_review(self.bank,self.configs,self.stock,seed=8)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'review';write_review(self.files,out)
            with self.assertRaises(StoreError):write_review(other,out)
            self.assertEqual((out/'media-manifest.json').read_bytes(),self.files['media-manifest.json'])

    def rewritten(self,change):
        files=dict(self.files);questions=json.loads(files['questions.json']);manifest=json.loads(files['media-manifest.json'])
        change(questions,manifest)
        files['questions.json']=json_bytes(questions);files['preview.html']=_preview(questions,manifest['assets'])
        manifest['questions_sha256']=digest(files['questions.json']);manifest['preview_sha256']=digest(files['preview.html'])
        manifest['bundle_id']=digest(json_bytes({'questions':stable_questions(questions),'assets':manifest['assets']}))
        files['media-manifest.json']=json_bytes(manifest)
        return files

    def test_rehashed_alt_text_cannot_contradict_renderer_provenance(self):
        files=self.rewritten(lambda q,m:m['assets'][0].update(alt_text='Radius is 999 cm'))
        with self.assertRaises(StoreError):verify_review_files(files)

    def test_rehashed_case_identity_must_follow_the_selection(self):
        def change(q,m):q['items'][0]['case_id']='nonsense';m['assets'][0]['case_id']='nonsense'
        with self.assertRaises(StoreError):verify_review_files(self.rewritten(change))

    def test_single_seed_metadata_must_match_every_numerical_request(self):
        with self.assertRaises(StoreError):verify_review_files(self.rewritten(lambda q,m:q.update(seed=8)))


if __name__=='__main__':unittest.main()
