const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {selectOriginalAssets,IDS,normalizeSnapshot}=require('./upload_drill_original_images.cjs');
const base=path.resolve(__dirname,'../docs/audits/2026-10-27-drill-image-variants/stage-5/review-full');
const q=JSON.parse(fs.readFileSync(path.join(base,'questions.json'),'utf8'));
const m=JSON.parse(fs.readFileSync(path.join(base,'media-manifest.json'),'utf8'));
test('selects exactly nine originals, never 150 variants or eight stocks',()=>{
 const result=selectOriginalAssets(q,m,base);assert.equal(result.length,9);
 assert.deepEqual(result.map(a=>a.externalId).sort(),[...IDS].sort());
 assert(result.every(a=>a.contentVersion===1||a.contentVersion===2));
});
test('missing and duplicate original families fail before upload',()=>{
 const a=structuredClone(q);a.items=a.items.filter(i=>i.case_id!=='pg-16-4-1:original');
 assert.throws(()=>selectOriginalAssets(a,m,base));
 const b=structuredClone(q);b.items.push(b.items.find(i=>i.mode==='original'));
 assert.throws(()=>selectOriginalAssets(b,m,base));
});
test('wrong bundle, source version, or image bytes fail before upload',()=>{
 const a=structuredClone(m);a.bundle_id='other';assert.throws(()=>selectOriginalAssets(q,a,base));
 const b=structuredClone(q);b.items.find(i=>i.mode==='original').record.original_version=999;
 assert.throws(()=>selectOriginalAssets(b,m,base));
 const c=structuredClone(m);c.assets.find(a=>a.mode==='original').sha256='0'.repeat(64);
 assert.throws(()=>selectOriginalAssets(q,c,base));
});
test('driver result arrays compare to persisted plain JSON without false conflicts',()=>{
 class Result extends Array {}
 const versions=new Result({external_id:'pg-16-4-1',version_number:2});versions.count=1;
 const business={versions,packageItems:new Result()};
 const stored=JSON.parse(JSON.stringify(business));
 assert.deepEqual(normalizeSnapshot(business),stored);
});
