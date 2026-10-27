"""Prepare the reviewed seed-1 bundle for owner-authorized DRAFT replacement; no cloud writes."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'docs/audits/2026-10-27-tryout-image-variants/stage-5/bundle-s1'
OUT=ROOT/'docs/audits/2026-10-27-tryout-local-replacement'


def prepare():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=json.loads((BUNDLE/'media-manifest.json').read_text(encoding='utf-8'))
    assert manifest['bundle_id']=='083125b756f4107d143ade49f3ccd824f3be1fdb6ab1ed7d9a70eff6c8e92162'
    assert sha(BUNDLE/'questions.json')==manifest['questions_sha256']
    records=json.loads((BUNDLE/'questions.json').read_text(encoding='utf-8'))['items']
    oldjob=ROOT/'docs/audits/2026-10-26-tryout-database-r2'
    oldinput=json.loads((oldjob/'import-input.json').read_text(encoding='utf-8'))
    oldresult=json.loads((oldjob/'apply-result.json').read_text(encoding='utf-8'))
    parents={q['externalId']:q['id'] for q in oldresult['questionVersions']}
    originals={q['externalId']:q for q in oldinput['questions']}
    assets={a['question_id']:a for a in manifest['assets']};items=[];media=[]
    for item in records:
        r=item['record'];qid=item['question_id'];q=copy.deepcopy(originals[qid])
        external='LTV-'+manifest['bundle_id'][:24]+'-'+qid
        q['externalId']=external;q['stem']={'text':r['stem']}
        q['options']=[{'id':o['id'],'content':{'text':o['text']}} for o in r['options']]
        correct=set(r['key'].split(','))
        q['answer']=({'optionId':r['key']} if r['format']=='PG' else
                     {'optionIds':[o['id'] for o in r['options'] if o['id'] in correct]} if r['format']=='MCMA' else
                     {'categoryByStatementId':{o['id']:'TRUE' if o['id'] in correct else 'FALSE' for o in r['options']}})
        q['explanation']={'text':r['explanation']};q['metadata']['assetManifest']=[]
        if qid in assets:
            a=assets[qid];file=(BUNDLE/a['path']).resolve();assert file.is_relative_to(BUNDLE.resolve())
            assert sha(file)==a['sha256']
            asset={'externalId':external,'assetId':'diagram-1','textMarker':'[[asset:diagram-1]]',
                   'placement':'STEM','itemId':None,'assetOrder':1,'altText':a['alt_text'],
                   'objectKey':None,'sha256':a['sha256'],'contentType':'image/png',
                   'byteLength':a['byte_length'],'bucket':'numora-bucket'}
            q['stem']['text']=asset['textMarker']+'\n\n'+r['stem']
            q['metadata']['assetManifest']=[asset]
            media.append({**asset,'contentVersion':1,'filePath':file.relative_to(ROOT).as_posix(),
                          'localQuestionId':qid,'imageProvenance':a['image_provenance']})
        items.append({'localQuestionId':qid,'status':item['status'],'parentVersionId':parents[qid],
                      'question':q,'record':r})
    assert len(items)==30 and len(media)==5 and sum(i['status']=='VARIANT' for i in items)==27
    result={'targetPackageId':oldresult['packageId'],'targetFamilyCode':'NUMORA-AI-TRYOUT-1',
            'targetName':'Tryout 1 - Varian lokal seed 1 (30 soal)','bundleId':manifest['bundle_id'],
            'variantCode':'LOCAL-'+manifest['bundle_id'],'items':items,'media':media,
            'bundleHashes':{p.name:sha(p) for p in (BUNDLE/'questions.json',BUNDLE/'media-manifest.json')},
            'originalQuestions':oldinput['questions'],
            'authorization':'User requested replacement of the30 existing Tryout items with the local30, including matching images. DRAFT only.'}
    OUT.mkdir(parents=True,exist_ok=True);p=OUT/'replacement-input.json'
    data=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if p.exists():assert p.read_text(encoding='utf-8')==data,'Prepared input changed'
    else:p.write_text(data,encoding='utf-8')
    print(json.dumps({'prepared':30,'generated':27,'original_only':3,'images':5,'targetPackageId':result['targetPackageId']}))


if __name__=='__main__':prepare()
