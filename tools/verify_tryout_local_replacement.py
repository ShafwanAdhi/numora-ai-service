"""Independent read-only comparison of the committed package with local bundle seed1."""
import json
from collections import Counter
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]


def main():
    env=dotenv_values(ROOT.parent/'Numora/.env')
    assert env['SUPABASE_PROJECT_REF']=='pkamenfnwmoeisccnrnk' and env['NODE_ENV']=='development'
    bundle=ROOT/'docs/audits/2026-10-27-tryout-image-variants/stage-5/bundle-s1'
    local=json.loads((bundle/'questions.json').read_text(encoding='utf-8'))
    media={a['question_id']:a for a in json.loads((bundle/'media-manifest.json').read_text(encoding='utf-8'))['assets']}
    job=ROOT/'docs/audits/2026-10-27-tryout-local-replacement'
    prepared=json.loads((job/'replacement-input.json').read_text(encoding='utf-8'))
    parent={x['localQuestionId']:x['parentVersionId'] for x in prepared['items']}
    with psycopg.connect(env['DATABASE_URL'],connect_timeout=10,row_factory=dict_row) as db:
        db.execute('set transaction read only')
        package=db.execute('select id,name,status,content_revision from assessment_packages where id=%s',(prepared['targetPackageId'],)).fetchone()
        assert package['status']=='DRAFT' and package['content_revision']==2
        rows=db.execute('''select p.display_order,v.*,qv.kind,qv.question_id,i.external_id
        from package_items p join question_versions v on v.id=p.question_version_id
        join question_variants qv on qv.id=v.variant_id
        join content_import_identities i on i.question_id=qv.question_id
        where p.package_id=%s order by p.display_order''',(prepared['targetPackageId'],)).fetchall()
        assert len(rows)==30
        for index,(row,item) in enumerate(zip(rows,local['items']),1):
            r=item['record'];qid=item['question_id'];stem=row['stem']['text']
            assert row['external_id']==qid and row['display_order']==index
            assert row['question_type']=={'PG':'SINGLE_CHOICE','MCMA':'MULTIPLE_CHOICE_MULTIPLE_ANSWER','KATEGORI':'CATEGORY'}[r['format']]
            if qid in media:
                assert len(row['media'])==1
                a=row['media'][0];assert a['sha256']==media[qid]['sha256'] and a['objectKey']
                assert stem.startswith(a['textMarker']+'\n\n');stem=stem[len(a['textMarker'])+2:]
            else:assert row['media']==[]
            assert stem==r['stem'] and row['explanation']['text']==r['explanation']
            assert row['options_or_statements']['options']==[{'id':o['id'],'content':{'text':o['text']}} for o in r['options']]
            correct=set(r['key'].split(','))
            key=({'optionId':r['key']} if r['format']=='PG' else
                 {'optionIds':sorted(correct)} if r['format']=='MCMA' else
                 {'categoryByStatementId':{o['id']:'TRUE' if o['id'] in correct else 'FALSE' for o in r['options']}})
            assert row['answer_key']==key
            assert row['content_status']=='DRAFT'
            if item['status']=='VARIANT':assert row['kind']=='VARIANT' and str(row['parent_original_question_version_id'])==parent[qid]
            else:assert row['kind']=='ORIGINAL' and str(row['id'])==parent[qid]
        report={'questionsMatched':30,'imagesMatched':5,'status':package['status'],
                'revision':package['content_revision'],'packageId':str(package['id']),
                'types':dict(Counter(row['question_type'] for row in rows)),
                'kinds':dict(Counter(row['kind'] for row in rows)),
                'compared':['order','family identity','stem excluding asset marker','all options','answer key','explanation','image SHA256','original parent lineage'],
                'readOnlyVerification':True}
    (job/'independent-source-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
