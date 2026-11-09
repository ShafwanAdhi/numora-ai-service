"""Explain the pinned anchor gate without changing scientific thresholds."""
import math


def anchor_gate(anchors, expected, quality, linking_required=True):
    if not linking_required:
        return {'passed':True,'scope':'REFERENCE_ONLY','checks':{}}
    checks={}
    for qid in expected:
        evidence=anchors.get(qid) or {}
        reasons=[]
        if evidence.get('evaluated') is not True:
            reasons.append('NOT_EVALUATED')
        for key,limit,reason in [
            ('holmP',quality['fitAlpha'],'HOLM_SIGNIFICANT'),
            ('maximumLogSlopeDifference',quality['anchorLogSlopeTolerance'],'LOG_SLOPE_DIFFERENCE'),
            ('maximumStepDifference',quality['anchorDifficultyTolerance'],'STEP_DIFFERENCE')]:
            value=evidence.get(key)
            valid=isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
            if not valid or value<0 or key=='holmP' and value>1:
                reasons.append('MISSING_OR_INVALID_'+key)
            elif (value<limit if key=='holmP' else value>limit):
                reasons.append(reason)
        checks[qid]={'passed':not reasons,'reasons':reasons}
    identity_ok=len(expected)==5 and set(anchors)==set(expected)
    return {'passed':identity_ok and all(c['passed'] for c in checks.values()),
            'scope':'ALL_FITTED_ARMS','identityValid':identity_ok,'checks':checks}
