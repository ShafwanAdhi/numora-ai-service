"""Independent seeded categorical simulator; no R/mirt sampling code is used."""
from copy import deepcopy
from decimal import Decimal
import json
import hashlib
import math
from pathlib import Path
import random
from uuid import UUID, uuid5

NAMESPACE=UUID('58d45273-1a7f-456f-9ea4-d330e4222603')


def generate(n=1000, seed=20261109, model='MIXED', arms=2, include_mcma=False):
    if arms not in (2,3):raise ValueError('Synthetic design supports two or three arms')
    root=Path(__file__).resolve().parents[2]
    value=json.loads((root/'contracts/irt-calibration-v1/examples/tryout-input.json').read_text())
    value['comparisons']=[];value['policies']['comparison']=None
    if include_mcma:
        if model!='MIXED':raise ValueError('MCMA fixture requires MIXED model')
        family=value['items'][5]['familyId']
        replacements={item['questionVersionId']:str(uuid5(NAMESPACE,'mcma:'+item['questionVersionId']))
                      for item in value['items'] if item['familyId']==family}
        for item in value['items']:
            if item['familyId']==family:
                item['originalQuestionVersionId']=replacements[item['originalQuestionVersionId']]
                item['questionVersionId']=replacements[item['questionVersionId']]
                item['rubricVersionId']=str(uuid5(NAMESPACE,'mcma:'+item['rubricVersionId']))
                item['contentDigest']=hashlib.sha256(item['questionVersionId'].encode()).hexdigest()
                item.update(questionType='MULTIPLE_CHOICE_MULTIPLE_ANSWER',modelFamily='GPCM',maximumScoreCategory=4,maxPoints='3.00')
        for package in value['packages']:
            package['questionVersionIds']=[replacements.get(q,q) for q in package['questionVersionIds']]
        value['referenceQuestionVersionIds']=[replacements.get(q,q) for q in value['referenceQuestionVersionIds']]
    if arms==3:
        package=deepcopy(value['packages'][1]);package['packageId']=str(uuid5(NAMESPACE,'package:third'))
        package['armId']=str(uuid5(NAMESPACE,'arm:third'))
        replacements={}
        for item in list(value['items']):
            if item['questionVersionId'] in package['questionVersionIds'][5:]:
                copy=deepcopy(item);qid=str(uuid5(NAMESPACE,'third:'+item['questionVersionId']))
                replacements[item['questionVersionId']]=qid;copy['questionVersionId']=qid
                copy['contentDigest']=hashlib.sha256(qid.encode()).hexdigest();value['items'].append(copy)
        package['questionVersionIds']=[replacements.get(q,q) for q in package['questionVersionIds']]
        value['packages'].append(package)
    rng=random.Random(seed)
    parameters={}
    for j,item in enumerate(value['items']):
        if model=='2PL':
            item.update(modelFamily='2PL',questionType='SINGLE_CHOICE',maximumScoreCategory=1)
        elif model=='GPCM':
            item.update(modelFamily='GPCM',questionType='CATEGORY',maximumScoreCategory=3)
        m=item['maximumScoreCategory']
        a=math.exp(rng.uniform(-.25,.25));center=rng.uniform(-1,1)
        steps=[center+(k-(m-1)/2)*.6 for k in range(m)]
        parameters[item['questionVersionId']]=(a,steps)
    items={i['questionVersionId']:i for i in value['items']}
    person_template=value['respondents'][0];response_template=value['responses'][0]
    value['respondents']=[];value['responses']=[];truth={}
    for arm,package in enumerate(value['packages']):
        for index in range(n):
            label=f'{seed}:{arm}:{index}'
            person=deepcopy(person_template)
            person.update(respondentId=str(uuid5(NAMESPACE,'person:'+label)),attemptId=str(uuid5(NAMESPACE,'attempt:'+label)),
                packageId=package['packageId'],packageVersion=package['packageVersion'],
                assignedArmId=package['armId'],deliveredArmId=package['armId'])
            theta=rng.gauss(arm*.25,1+arm*.1)
            truth[person['attemptId']]=theta
            value['respondents'].append(person)
            for qid in package['questionVersionIds']:
                item=items[qid];a,steps=parameters[qid]
                # Independent cumulative-logit softmax, deliberately separate from production math.
                logits=[0]+[a*(k*theta-sum(steps[:k])) for k in range(1,len(steps)+1)]
                weights=[math.exp(x-max(logits)) for x in logits]
                category=rng.choices(range(len(weights)),weights=weights)[0]
                response=deepcopy(response_template)
                response.update(respondentId=person['respondentId'],attemptId=person['attemptId'],
                    attemptItemId=str(uuid5(NAMESPACE,'item:'+label+':'+qid)),questionVersionId=qid,
                    rubricVersionId=item['rubricVersionId'],scoreCategory=category,
                    awardedPoints=format(Decimal(item['maxPoints'])*category/Decimal(len(steps)),'.2f'))
                value['responses'].append(response)
    return value,{'items':parameters,'theta':truth,'seed':seed,'perArm':n,'design':model}
