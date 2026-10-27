"""Prepare effective local originals plus explicitly reviewed image mappings; no DB/R2 writes."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'variant_gen'))
from bank import load_workspace_bank

SOURCE=ROOT/'docs/sources/incoming/2026-10-26-tryout-images'
OUT=ROOT/'docs/audits/2026-10-26-tryout-database-r2'
FACTS={
 'tryout-1-b3-q02':(['20','14','setengah lingkaran'],'Taman persegi panjang 20 m kali 14 m dengan setengah lingkaran pada sisi lebarnya.'),
 'tryout-1-b3-q03':(['3x+15','5x-25','50'],'Diagram dua garis sejajar yang dipotong transversal serta segitiga dengan dua sudut diketahui.'),
 'tryout-1-b3-q04':(['12','18','2/3'],'Limas segi empat terbalik berisi air sampai dua pertiga tinggi total.'),
 'tryout-1-b3-q06':(['7','10','15','12'],'Dua rancangan penampung: tabung berkubah setengah bola dan balok, dengan ukuran dalam desimeter.'),
 'tryout-1-b4-q05':(['180','dadu'],'Dua dadu bermuka enam untuk percobaan sebanyak 180 kali.'),
}


def prepare():
 bank=load_workspace_bank(ROOT/'variant_gen/data/q0_bank.csv')
 manifest=json.loads((SOURCE/'image-manifest.json').read_text(encoding='utf-8'))
 images={i['candidate_local_question_id']:i for i in manifest['images']}
 assert set(images)==set(FACTS)
 questions=[];media=[]
 for group in bank.catalog():
  if group['activity']!='TRYOUT':continue
  assert group['package_id']=='tryout-1'
  for qid in group['question_ids']:
   original=bank.get(qid);m=original['metadata'];correct=[o['id'] for o in original['options'] if o['correct']]
   fmt=original['format'];labels=m.get('category_labels',['Benar','Salah'])
   answer=({'optionId':correct[0]} if fmt=='PG' else {'optionIds':correct} if fmt=='MCMA' else
           {'categoryByStatementId':{o['id']:'TRUE' if o['correct'] else 'FALSE' for o in original['options']}})
   metadata=dict(sourceLevelNumber=None,sourceOrder=len(questions)+1,source='Numora-ai-service effective local Tryout originals',
    originalHash=original['hash'],originalVersion=original['version'],cognitiveLevel=original['cognitive_level'],
    localQuestionId=qid,sourceChapter=group['chapter'],sourcePackage='tryout-1',assetManifest=[])
   if fmt=='KATEGORI':metadata['categories']=[dict(id='TRUE',label=labels[0]),dict(id='FALSE',label=labels[1])]
   stem=original['stem']
   if qid in images:
    image=images[qid];facts,alt=FACTS[qid];normalized=stem.replace('−','-')
    assert all(fact in normalized for fact in facts),qid
    path=SOURCE/image['local_path'];data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==image['image_sha256']
    asset=dict(externalId=qid,assetId='diagram-1',textMarker='[[asset:diagram-1]]',placement='STEM',itemId=None,
      assetOrder=1,altText=alt,objectKey=None,sha256=image['image_sha256'],contentType='image/png',byteLength=len(data),bucket='numora-bucket')
    metadata['assetManifest']=[asset];stem=asset['textMarker']+'\n\n'+stem
    metadata['imageMappingReview']=dict(sourceDocxSha256=manifest['source_sha256'],facts=facts,
      review='Visual diagram + source paragraph + local effective stem checked; no changed diagram numbers',date='2026-10-26')
    media.append(dict(**asset,contentVersion=1,filePath=path.relative_to(ROOT).as_posix()))
   questions.append(dict(externalId=qid,type={'PG':'SINGLE_CHOICE','MCMA':'MULTIPLE_CHOICE_MULTIPLE_ANSWER','KATEGORI':'CATEGORY'}[fmt],
     chapterCode={1:'CH-BIL',2:'CH-ALG',3:'CH-GP',4:'CH-DP'}[group['chapter']],subchapterCode=None,competencyCode=None,
     difficulty=None,stem={'text':stem},options=[dict(id=o['id'],content={'text':o['text']}) for o in original['options']],
     answer=answer,explanation={'text':m['original_explanation']},metadata=metadata))
 assert len(questions)==30 and len(media)==5 and len({q['externalId'] for q in questions})==30
 output=dict(sourceNamespace='NUMORA_AI_TRYOUT_1',package=dict(familyCode='NUMORA-AI-TRYOUT-1',packageVersion=1,
   name='Tryout 1 - Original lokal (30 soal)',assessmentType='TRYOUT',isDemo=False,
   source=dict(sourceNamespace='NUMORA_AI_TRYOUT_1',sourceName='Tryout 1 - original lokal + 5 gambar',
    sourceReference='Numora-ai-service/variant_gen/data/tryout-1 + docs/sources/incoming/2026-10-26-tryout-images')),
   questions=questions,media=media,approval=dict(date='2026-10-26',userInstruction='Unggah 5 gambar dan impor 30 soal sebagai DRAFT',publishApproved=False),
   localOriginalSha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'variant_gen/data/tryout-1').glob('*') if p.is_file()})
 OUT.mkdir(parents=True,exist_ok=True);path=OUT/'import-input.json'
 text=json.dumps(output,ensure_ascii=False,indent=2)+'\n'
 if path.exists():assert path.read_text(encoding='utf-8')==text,'Prepared input changed; review before replacing'
 else:path.write_text(text,encoding='utf-8')
 print(json.dumps(dict(questions=30,images=5,namespace=output['sourceNamespace'],path=str(path))))
 return output


if __name__=='__main__':prepare()
