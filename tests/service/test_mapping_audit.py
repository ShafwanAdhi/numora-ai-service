import copy
import unittest

from numora_service.mapping_audit import compare, media_assets


class MappingAuditTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(id='pg-1-1-1', hash='a'*64, version=1, format='PG', options=[{},{}],
            classification=dict(activity='DRILL', indicator=1, source_level=1, package_id='drill-1'))
        self.expected = dict(questionType='SINGLE_CHOICE', stem={'text':'question'},
            optionsOrStatements={'options':[{'id':'A','content':{'text':'yes'}}, {'id':'B','content':{'text':'no'}}]},
            answerKey={'optionId':'A'}, explanation={'text':'reason'})
        self.row = dict(kind='ORIGINAL', original_hash='a'*64, original_version='1', usage_type='DRILL',
            question_type='SINGLE_CHOICE', media={}, stem={'text':'question'},
            options_or_statements=copy.deepcopy(self.expected['optionsOrStatements']), answer_key={'optionId':'A'},
            explanation={'text':'reason'}, chapter_code='CH-BIL', competency_code='IND-001',
            curriculum_level_number=1, level_number=1, rubric_question_type='SINGLE_CHOICE',
            maximum_score_category=1, rubric_status='SEALED',content_status='READY',validation_state='CONTENT_VALID',
            contexts=['context'],config_ids=[],approval_ids=[],family_id='family',id='original',version_number=1,
            scoring_rubric_version_id='rubric',rubric_digest='b'*64, content_fingerprint=None, import_content_hash='c'*64)

    def test_existing_valid_source_is_not_an_import_instruction(self):
        result=compare(self.original,self.row,self.expected)
        self.assertTrue(result['identityValid'])
        self.assertTrue(result['contentMatches'])
        self.assertTrue(result['registrationReady'])
        self.assertIn('GENERATOR_APPROVAL_MISSING', result['blockers'])

    def test_stale_stem_not_hidden_by_matching_hash(self):
        self.row['stem']['text']='changed'
        result=compare(self.original,self.row,self.expected)
        self.assertTrue(result['identityValid'])
        self.assertFalse(result['contentMatches'])
        self.assertIn('STEM_MISMATCH',result['problems'])

    def test_taxonomy_key_and_rubric_are_independently_checked(self):
        self.row.update(competency_code='IND-002',level_number=2,answer_key={'optionId':'B'},rubric_status='DRAFT')
        result=compare(self.original,self.row,self.expected)
        self.assertEqual(set(result['problems']),{'INDICATOR_MISMATCH','LEVEL_MISMATCH','ANSWER_MISMATCH'})
        self.assertIn('RUBRIC_NOT_SEALED',result['blockers'])

    def test_marker_requires_a_matching_media_manifest(self):
        self.row['stem']['text']='[[asset:diagram-1]]\n\nquestion'
        self.assertIn('MEDIA_MARKER_UNRESOLVED',compare(self.original,self.row,self.expected)['problems'])
        self.row['media']=[{'assetId':'diagram-1','placement':'STEM'}]
        self.assertTrue(compare(self.original,self.row,self.expected)['contentMatches'])

    def test_missing_local_explanation_does_not_claim_full_match(self):
        self.expected['explanation']=None
        result=compare(self.original,self.row,self.expected)
        self.assertFalse(result['contentMatches'])
        self.assertIn('LOCAL_EXPLANATION_UNAVAILABLE',result['blockers'])

    def test_legacy_empty_media_and_invalid_shape(self):
        for value in (None,{},[],{'assets':[]}):self.assertEqual(media_assets(value),[])
        with self.assertRaisesRegex(ValueError,'MEDIA_SHAPE_INVALID'):media_assets({'unrecognized':True})


if __name__=='__main__':unittest.main()
