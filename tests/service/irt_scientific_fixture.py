"""Deterministic engine double; never scientific recovery/production evidence."""
from numora_service.irt.math import probabilities


def scientific_fixture(work):
    estimates={};fit={}
    for item in work['items']:
        qid=item['questionVersionId'];m=item['maximumScoreCategory']
        steps=[(k-(m-1)/2)*.4 for k in range(m)]
        estimates[qid]={'a':1.,'intercepts':[-sum(steps[:k]) for k in range(1,m+1)],
            'covariance':[[.0001 if i==j else 0. for j in range(m+1)] for i in range(m+1)],
            'probabilityGrid':[probabilities(-4+.5*j,1.,steps) for j in range(17)]}
        column=next(j for j,i in enumerate(work['items']) if i['questionVersionId']==qid)
        observed={arm for arm,row in zip(work['groups'],work['matrix']) if row[column] is not None}
        for arm in observed:
            fit[arm+':'+qid]={'questionVersionId':qid,'group':arm,'sx2AdjustedP':1.,'adjustedQ3':0.}
    return {'converged':True,'estimates':estimates,'fit':fit,'anchors':{
        q:{'evaluated':True,'holmP':1.,'maximumLogSlopeDifference':0.,'maximumStepDifference':0.}
        for q in work['anchors']}}
