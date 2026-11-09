import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from numora_service.irt.math import probabilities,eap,reference_score


@unittest.skipUnless(os.environ.get('IRT_RESEARCH_TEST_IMAGE'),'Pinned R image required')
class ROracleTests(unittest.TestCase):
    def test_probtrace_and_independent_adaptive_integration(self):
        with tempfile.TemporaryDirectory(prefix='irt-oracle-') as directory:
            subprocess.run(['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL',
                '--tmpfs','/tmp:rw,nosuid,size=256m','--mount',f'type=bind,source={directory},target=/work',
                '--entrypoint','Rscript',os.environ['IRT_RESEARCH_TEST_IMAGE'],'--vanilla','/opt/irt/oracle.R','/work/result.json'],
                check=True,capture_output=True,timeout=90)
            oracle=json.loads((Path(directory)/'result.json').read_text())
        for item,steps in enumerate([[.4],[.8,-.6]]):
            for row,theta in enumerate(range(-4,5)):
                for actual,expected in zip(probabilities(theta,1.3,steps),oracle['probabilities'][item][row]):
                    self.assertLess(abs(actual-expected),1e-8)
        parameters={str(i):(1.3,[.8,-.6] if i==1 else [.4]) for i in range(30)}
        items=[{'questionVersionId':str(i),'maxPoints':'1','maximumScoreCategory':2 if i==1 else 1} for i in range(30)]
        patterns=[[0]*30,[1,2]+[1]*28,[1,1]+[0,1]*14]
        for pattern,target in zip(patterns,oracle['posteriors']):
            theta,sd=eap([(str(i),v) for i,v in enumerate(pattern)],parameters,points=241)
            self.assertLess(abs(theta-target['theta']),1e-4)
            self.assertLess(abs(sd-target['sd']),1e-4)
            prediction=100*sum(sum(k*p for k,p in enumerate(probabilities(theta,*parameters[str(i)])))/items[i]['maximumScoreCategory'] for i in range(30))/30
            self.assertLess(abs(prediction-target['unroundedScore']),1e-4)
            self.assertLessEqual(abs(reference_score(theta,items,parameters)-target['unroundedScore']),.00501)
