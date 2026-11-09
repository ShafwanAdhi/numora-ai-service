from copy import deepcopy
import math
import unittest
from research.irt.synthetic import generate
from numora_service.irt.producer import run
from tests.service.irt_scientific_fixture import scientific_fixture


class IrtOutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value,_=generate(500)
        cls.dispatch={'executionId':'55555555-5555-4555-8555-555555555555','dispatchGeneration':1}

    def test_valid_extremes_omissions_and_missing_observations(self):
        value,_=generate(501)
        people=value['respondents'][:4];ids=[p['attemptId'] for p in people]
        items={i['questionVersionId']:i for i in value['items']}
        for response in value['responses']:
            if response['attemptId'] not in ids:continue
            pattern=ids.index(response['attemptId'])
            category=items[response['questionVersionId']]['maximumScoreCategory'] if pattern==1 else 0
            response.update(scoreCategory=category,awardedPoints=items[response['questionVersionId']]['maxPoints'] if category else '0.00')
            if pattern==2:response['responseState']='OMITTED'
            if pattern==3:response.update(responseState='NOT_PRESENTED',scoreCategory=None,awardedPoints=None,
                includedInCalibration=False,eligibilityReasons=['NOT_PRESENTED'])
        result,_=run(value,self.dispatch,scientific_fixture)
        rows={r['attemptId']:r for r in result['outcome']['respondents']}
        self.assertEqual(rows[ids[3]]['status'],'UNSCORABLE')
        self.assertIsNone(rows[ids[3]]['score'])
        for aid in ids[:3]:
            self.assertEqual(rows[aid]['status'],'SCORED')
            self.assertTrue(0<rows[aid]['score']<100)
        self.assertLess(rows[ids[0]]['theta'],0)
        self.assertGreater(rows[ids[1]]['theta'],0)
        self.assertEqual(rows[ids[0]]['score'],rows[ids[2]]['score'])

    def test_healthy_engine_double_scores_both_arms(self):
        result,_=run(self.value,self.dispatch,scientific_fixture)
        self.assertEqual(result['outcome']['measurementState'],'CALIBRATED')
        self.assertTrue(all(r['status']=='SCORED' and math.isfinite(r['theta']) for r in result['outcome']['respondents']))

    def test_nonconvergence_has_no_parameters_or_scores(self):
        result,_=run(self.value,self.dispatch,lambda _: {'converged':False,'estimates':{},'fit':{},'anchors':{}})
        self.assertEqual(result['executionStatus'],'SUCCEEDED')
        self.assertEqual(result['outcome']['measurementState'],'INSUFFICIENT')
        self.assertTrue(all(i['parameters'] is None for i in result['outcome']['items']))
        self.assertTrue(all(r['score'] is None for r in result['outcome']['respondents']))

    def test_link_failure_is_not_drift_and_keeps_values_null(self):
        def runner(work):
            result=scientific_fixture(work)
            result['anchors'][work['anchors'][0]]['maximumStepDifference']=1.3
            return result
        result,_=run(self.value,self.dispatch,runner)
        self.assertEqual(result['outcome']['measurementState'],'NOT_COMPARABLE')
        self.assertEqual(result['outcome']['comparisons'],[])
        self.assertTrue(all(r['status']=='NOT_COMPARABLE' and r['score'] is None for r in result['outcome']['respondents']))

    def test_local_dependence_or_missing_fit_never_produces_scores(self):
        for missing in [False,True]:
            def runner(work):
                result=scientific_fixture(work)
                for fit in result['fit'].values():fit['adjustedQ3']=None if missing else .8
                return result
            with self.subTest(missing=missing):
                result,_=run(self.value,self.dispatch,runner)
                self.assertTrue(all(r['score'] is None for r in result['outcome']['respondents']))
                if missing:
                    self.assertTrue(all(any(c['status']=='NOT_EVALUATED' for c in i['quality']['checks']) for i in result['outcome']['items']))

    def test_singular_covariance_cannot_be_adopted(self):
        def runner(work):
            result=scientific_fixture(work)
            for estimate in result['estimates'].values():
                estimate['covariance']=[[0.]*len(estimate['covariance']) for _ in estimate['covariance']]
            return result
        result,diagnostics=run(self.value,self.dispatch,runner)
        self.assertTrue(all(i['parameters'] is None for i in result['outcome']['items']))
        self.assertTrue(all(r['score'] is None for r in result['outcome']['respondents']))
        self.assertEqual(set(diagnostics['parameterFailures'].values()),{'INVALID_COVARIANCE'})

    def test_engine_error_retains_only_sanitized_diagnostics(self):
        from numora_service.irt.failures import EngineExecutionError
        with self.assertRaises(EngineExecutionError) as raised:
            run(self.value,self.dispatch,lambda _: {'engineError':'private data',
                'engineStage':'FIT','scientificFailure':'MODEL_CONVERGENCE_FAILED'})
        self.assertEqual(raised.exception.diagnostics['engineStage'],'FIT')
