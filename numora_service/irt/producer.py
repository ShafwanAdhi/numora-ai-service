"""Research-only scientific producer. Never writes grades, XP or publication."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from ..irt_contracts import validate_input, validate_result
from .math import convert, eap, probabilities, reference_score, posterior_grid

POLICY_PATH = Path(__file__).resolve().parents[2] / 'research/irt/policy-v1.json'


def policy():
    return json.loads(POLICY_PATH.read_text(encoding='utf-8'))


def check(code, passed, statistic=None):
    return {'code':code,'status':'NOT_EVALUATED' if passed is None else 'PASS' if passed else 'FAIL',
            'statistic':statistic,'standardError':None}


def anchor_support(people,items,responses,anchors,quality):
    counts=defaultdict(Counter)
    for response in responses:
        if response['questionVersionId'] in anchors:
            counts[(people[response['attemptId']]['deliveredArmId'],response['questionVersionId'])][response['scoreCategory']]+=1
    supported={arm for arm in {p['deliveredArmId'] for p in people.values()} if all(
        sum(counts[(arm,qid)].values())>=quality['minimumItemCount'] and
        all(counts[(arm,qid)][category]>=quality['minimumCategoryCount'] for category in range(items[qid]['maximumScoreCategory']+1))
        for qid in anchors)}
    evidence={arm:{qid:dict(counts[(arm,qid)]) for qid in anchors} for arm in {p['deliveredArmId'] for p in people.values()}}
    return supported,evidence


def run(value, dispatch, runner, profile=None, heartbeat=lambda:None):
    heartbeat()
    validate_input(value)
    profile = profile or policy()
    if profile != policy():
        raise ValueError('POLICY_UNAVAILABLE')
    if value['ecosystem'] != 'TRYOUT' or value['comparisons']:
        raise ValueError('UNSUPPORTED_CONTRACT')
    if len(value['respondents']) > profile['runtime']['maximumRespondents'] or len(value['packages']) > profile['runtime']['maximumArms']:
        raise ValueError('INVALID_INPUT')
    quality = profile['quality']
    people = {p['attemptId']:p for p in value['respondents']}
    items = {i['questionVersionId']:i for i in value['items']}
    packages = {(p['packageId'],p['packageVersion']):p for p in value['packages']}
    included = [r for r in value['responses'] if r['includedInCalibration']]
    counts = Counter(r['questionVersionId'] for r in included)
    categories = defaultdict(Counter)
    attempts = defaultdict(dict)
    for r in included:
        categories[r['questionVersionId']][r['scoreCategory']] += 1
        attempts[r['attemptId']][r['questionVersionId']] = r['scoreCategory']
    arm_people = defaultdict(set)
    for aid in attempts:
        arm_people[people[aid]['deliveredArmId']].add(aid)
    eligible_arms = {arm for arm,ids in arm_people.items() if len(ids)>=quality['minimumArmCount']}
    anchor_arms,anchor_counts=anchor_support(people,items,included,value['anchorQuestionVersionIds'],quality)
    fitted_arms=eligible_arms & anchor_arms
    fit_candidates=[r for r in included if people[r['attemptId']]['deliveredArmId'] in fitted_arms]
    fit_candidate_counts=Counter(r['questionVersionId'] for r in fit_candidates)
    fit_categories=defaultdict(Counter)
    for r in fit_candidates:fit_categories[r['questionVersionId']][r['scoreCategory']]+=1
    active = [qid for qid,item in items.items() if item['contentState']=='CONTENT_VALID'
              and fit_candidate_counts[qid]>=quality['minimumItemCount'] and all(fit_categories[qid][k]>=quality['minimumCategoryCount']
              for k in range(item['maximumScoreCategory']+1))]
    original = next(p for p in value['packages'] if p['armKind']=='ORIGINAL')
    good = original['armId'] in fitted_arms and set(value['anchorQuestionVersionIds'])<=set(active)
    scientific = {'converged':False,'estimates':{},'fit':{},'anchors':{}}
    fit_counts = Counter()
    if good:
        groups = [original['armId']] + sorted(fitted_arms-{original['armId']})
        aids = sorted(aid for aid in attempts if people[aid]['deliveredArmId'] in fitted_arms)
        fit_counts.update(qid for aid in aids for qid in attempts[aid] if qid in active)
        work = {'policy':profile,'items':[items[qid] for qid in active],
                'matrix':[[attempts[aid].get(qid) for qid in active] for aid in aids],
                'groups':[people[aid]['deliveredArmId'] for aid in aids], 'groupOrder':groups,
                'anchors':value['anchorQuestionVersionIds']}
        scientific = runner(work)
        if scientific.get('engineError'):
            raise ValueError('INTERNAL_ERROR')
    scientific['selection'] = {'eligiblePerArm':{arm:len(ids) for arm,ids in arm_people.items()},
        'fittedPerArm':{arm:len(ids) if good and arm in fitted_arms else 0 for arm,ids in arm_people.items()},
        'eligiblePerItem':dict(counts),'fittedPerItem':dict(fit_counts),'anchorCategoriesPerArm':anchor_counts}
    estimates = scientific.get('estimates',{})
    parameters, results = {}, []
    for qid,item in items.items():
        checks = [check('CONTENT_VALID',item['contentState']=='CONTENT_VALID'),
                  check('MINIMUM_ITEM_COUNT',fit_candidate_counts[qid]>=quality['minimumItemCount'],fit_candidate_counts[qid]),
                  check('CATEGORY_COVERAGE',qid in active)]
        reasons = []
        if item['contentState']!='CONTENT_VALID': reasons.append('CONTENT_INVALID')
        if qid not in active: reasons.append('INSUFFICIENT_SAMPLE')
        out = None
        estimate = estimates.get(qid)
        if qid in active and good:
            checks.append(check('CONVERGENCE_AND_INFORMATION',scientific['converged']))
            if not scientific['converged']: reasons.append('MODEL_CONVERGENCE_FAILED')
        if estimate and scientific['converged'] and not reasons:
            try:
                a, covariance = estimate['a'], estimate['covariance']
                steps, errors = convert(a,estimate['intercepts'],covariance)
                ase = math.sqrt(covariance[0][0])
                grid = estimate['probabilityGrid']
                if len(grid)!=17 or len(steps)!=item['maximumScoreCategory']:
                    raise ValueError('PARAMETERIZATION_MISMATCH')
                for i,theta in enumerate([-4+0.5*j for j in range(17)]):
                    predicted = probabilities(theta,a,steps)
                    if len(grid[i])!=len(predicted) or any(not math.isfinite(x) for x in grid[i]) or max(abs(x-y) for x,y in zip(predicted,grid[i]))>1e-8:
                        raise ValueError('PARAMETERIZATION_MISMATCH')
                precision = ase<=quality['maximumDiscriminationSE'] and max(errors)<=quality['maximumDifficultySE']
                checks.append(check('ITEM_PRECISION',precision,max([ase]+errors)))
                if not precision: reasons.append('LOW_PRECISION')
                evidence = [d for d in scientific['fit'].values() if d['questionVersionId']==qid]
                fit_ok = None if not evidence or any(d['sx2AdjustedP'] is None for d in evidence) else all(d['sx2AdjustedP']>=quality['fitAlpha'] for d in evidence)
                dependence_ok = None if not evidence or any(d['adjustedQ3'] is None for d in evidence) else all(d['adjustedQ3']<=quality['maximumAdjustedQ3'] for d in evidence)
                checks += [check('SX2_HOLM',fit_ok),check('LOCAL_DEPENDENCE_Q3',dependence_ok)]
                if not fit_ok: reasons.append('MODEL_FIT_FAILED')
                if not dependence_ok: reasons.append('LOCAL_DEPENDENCE')
                if not reasons:
                    parameters[qid] = (a,steps)
                    out = {'discriminationA':a,'discriminationStandardError':ase,
                           'difficultyB':steps[0] if item['modelFamily']=='2PL' else None,
                           'difficultyStandardError':errors[0] if item['modelFamily']=='2PL' else None,
                           'steps':[] if item['modelFamily']=='2PL' else [dict(step=k+1,value=d,standardError=errors[k]) for k,d in enumerate(steps)]}
            except (ValueError,KeyError,TypeError,OverflowError):
                reasons.append('MODEL_CONVERGENCE_FAILED')
        if out is None and not reasons: reasons.append('INSUFFICIENT_SAMPLE')
        calibrated = out is not None
        results.append({'questionVersionId':qid,'rubricVersionId':item['rubricVersionId'],'modelFamily':item['modelFamily'],
            'eligibleRespondentCount':counts[qid],'measurementState':'CALIBRATED' if calibrated else 'ANOMALY' if 'CONTENT_INVALID' in reasons else 'INSUFFICIENT',
            'parameters':out,'quality':{'gate':'PASSED' if calibrated else 'FAILED','checks':checks},'reasonCodes':list(dict.fromkeys(reasons))})
    anchors_calibrated = all(q in parameters for q in value['anchorQuestionVersionIds'])
    anchor_evidence = scientific.get('anchors',{})
    linking_required=len(fitted_arms)>1
    anchor_ok = not linking_required or len(anchor_evidence)==5 and all(a.get('evaluated') and
         a.get('holmP') is not None and a['holmP']>=quality['fitAlpha'] and
         a.get('maximumLogSlopeDifference',math.inf)<=quality['anchorLogSlopeTolerance'] and
         a.get('maximumStepDifference',math.inf)<=quality['anchorDifficultyTolerance'] for a in anchor_evidence.values())
    package_results = []
    for package in value['packages']:
        sample_ok = package['armId'] in eligible_arms
        coverage = sum(q in parameters for q in package['questionVersionIds'])
        anchor_sample_ok=package['armId'] in anchor_arms
        passed = sample_ok and anchor_sample_ok and anchors_calibrated and anchor_ok and coverage>=profile['respondent']['minimumValidItems']
        state = 'CALIBRATED' if passed else 'NOT_COMPARABLE' if sample_ok and anchor_sample_ok and anchors_calibrated and not anchor_ok else 'INSUFFICIENT'
        package_results.append({k:package[k] for k in ['packageId','packageVersion']}
            | {'measurementState':state,'quality':{'gate':'PASSED' if passed else 'FAILED','checks':[
                check('MINIMUM_ARM_COUNT',sample_ok,len(arm_people[package['armId']])),
                check('ANCHOR_RESPONSE_COVERAGE',anchor_sample_ok),
                check('ANCHOR_CALIBRATION',anchors_calibrated),check('ANCHOR_SENSITIVITY' if linking_required else 'REFERENCE_SCALE_NO_LINK_REQUIRED',anchor_ok),check('VALID_ITEM_COVERAGE',coverage>=profile['respondent']['minimumValidItems'],coverage)]},
               'reasonCodes':[] if passed else ['ANCHOR_UNSTABLE'] if state=='NOT_COMPARABLE' else ['INSUFFICIENT_SAMPLE']})
    states = {(p['packageId'],p['packageVersion']):p['measurementState'] for p in package_results}
    respondents = []
    posterior=posterior_grid(parameters,241)
    reference = [items[qid] for qid in value['referenceQuestionVersionIds']]
    by_attempt = defaultdict(list)
    for response in value['responses']:
        by_attempt[response['attemptId']].append(response)
    for index,person in enumerate(value['respondents']):
        if index%25==0:heartbeat()
        responses = by_attempt[person['attemptId']]
        observations = [(r['questionVersionId'],r['scoreCategory']) for r in responses
                        if r['questionVersionId'] in parameters and r['responseState'] in ('RESPONDED','OMITTED')]
        valid_observations = [r for r in responses if items[r['questionVersionId']]['contentState']=='CONTENT_VALID'
                              and r['responseState'] in ('RESPONDED','OMITTED')]
        package_state = states[(person['packageId'],person['packageVersion'])]
        status = 'UNSCORABLE' if not valid_observations else 'NOT_COMPARABLE' if package_state=='NOT_COMPARABLE' else 'INSUFFICIENT'
        reason = 'NO_VALID_ITEMS' if status=='UNSCORABLE' else 'LINKING_FAILED' if status=='NOT_COMPARABLE' else 'INSUFFICIENT_SAMPLE'
        row = {k:person[k] for k in ['respondentId','attemptId','packageId','packageVersion','batchId']}
        row.update(status=status,theta=None,standardError=None,score=None,scoreMapping=None,referencePackage=None,usedQuestionVersionIds=[],reasonCodes=[reason])
        if package_state=='CALIBRATED' and value['policies']['scoreMapping'] and reference and all(i['questionVersionId'] in parameters for i in reference) and len(observations)>=profile['respondent']['minimumValidItems']:
            theta,se = eap(observations,parameters,prepared=posterior)
            if se<=profile['respondent']['maximumPosteriorSD']:
                row.update(status='SCORED',theta=theta,standardError=se,score=reference_score(theta,reference,parameters),
                    scoreMapping=value['policies']['scoreMapping'],referencePackage=value['referencePackage'],
                    usedQuestionVersionIds=[q for q,_ in observations],reasonCodes=[])
            else: row['reasonCodes']=['RESPONDENT_PRECISION_INSUFFICIENT']
        respondents.append(row)
    state_list = list(states.values())
    n = state_list.count('CALIBRATED')
    state = 'CALIBRATED' if n==len(state_list) else 'PARTIAL' if n else 'NOT_COMPARABLE' if 'NOT_COMPARABLE' in state_list else 'INSUFFICIENT'
    result = {k:deepcopy(value[k]) for k in ['contractVersion','requestId','snapshotId','inputDigest','calibrationId','context']}
    result.update(executionId=dispatch['executionId'],dispatchGeneration=dispatch['dispatchGeneration'],
                  completedAt=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),
                  executionStatus='SUCCEEDED',failure=None,outcome={'measurementState':state,'items':results,
                    'packages':package_results,'respondents':respondents,'comparisons':[]})
    validate_result(result,value,dispatch)
    return result, scientific
