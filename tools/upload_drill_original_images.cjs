// Explicit owner-authorized R2 upload only. Never updates question content or publication.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const { createRequire } = require('node:module');
const ai = path.resolve(__dirname, '..');
const main = path.resolve(ai, '../Numora');
const bundle = path.join(ai, 'docs/audits/2026-10-27-drill-image-variants/stage-5/review-full');
const job = path.join(ai, 'docs/audits/2026-10-27-drill-r2-upload');
const bundleId = 'c948bf0bfd6f8b71514aaff0fefac3b1dfed7438a90b4e42c65c1e2e0e89ddc3';
const actor = '0ed807a0-3524-4deb-9aea-452f4a9ba400';
const IDS = ['pg-16-4-1','pg-16-4-2','pg-16-4-3','pg-16-4-4','mcma-16-4-6','mcma-16-4-7','pg-16-5-1','pg-16-5-3','pg-16-5-5'];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const normalizeSnapshot = value => JSON.parse(JSON.stringify(value));
function save(file, value) { fs.mkdirSync(path.dirname(file), {recursive:true}); fs.writeFileSync(file, JSON.stringify(value,null,2)+'\n'); }

function selectOriginalAssets(questions, manifest, base) {
  assert.equal(questions.kind,'DRILL_IMAGE_REVIEW'); assert.equal(manifest.kind,'DRILL_IMAGE_REVIEW');
  assert.equal(manifest.bundle_id,bundleId);
  const originals = questions.items.filter(item => item.mode === 'original');
  assert.deepEqual(originals.map(item=>item.question_id).sort(), [...IDS].sort());
  return originals.map(item => {
    const qid=item.question_id, record=item.record;
    assert.equal(item.case_id,qid+':original'); assert.equal(record.seed,0);
    const assets=manifest.assets.filter(asset=>asset.case_id===item.case_id);
    assert.equal(assets.length,1);
    const asset=assets[0]; assert.equal(asset.mode,'original'); assert.equal(asset.question_id,qid);
    assert.equal(asset.provenance.content.original_hash,record.original_hash);
    assert.equal(asset.provenance.content.original_version,record.original_version);
    assert.equal(asset.path,`images/${asset.sha256}.png`);
    const file=path.resolve(base,asset.path); assert(file.startsWith(path.resolve(base,'images')+path.sep));
    const bytes=fs.readFileSync(file); assert.equal(sha(bytes),asset.sha256);
    assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
    assert.equal(bytes.readUInt32BE(16),960); assert.equal(bytes.readUInt32BE(20),640);
    assert(bytes.length>0 && bytes.length<=5242880);
    const assetId=`drill-original-${bundleId.slice(0,16)}-diagram-1`;
    return {externalId:qid,assetId,contentVersion:record.original_version,contentType:'image/png',
      byteLength:bytes.length,sha256:asset.sha256,filePath:path.relative(ai,file).split(path.sep).join('/'),
      sourceOriginalHash:record.original_hash,sourceOriginalVersion:record.original_version,
      altText:asset.alt_text,imageProvenance:asset.provenance};
  });
}

async function run(mode) {
  assert(['--check','--upload','--verify'].includes(mode));
  process.loadEnvFile(path.join(main,'.env'));
  const req=createRequire(path.join(main,'apps/api/package.json')); req('reflect-metadata');
  const {assertDevelopmentTarget}=require(path.join(main,'apps/api/scripts/import-local-tryout.cjs'));
  assertDevelopmentTarget(process.env);
  const database=req('@tka/database');
  const {ConfigService}=req('@nestjs/config');
  const {R2MediaStorage}=require(path.join(main,'apps/api/dist/modules/content/r2-media.storage.js'));
  const {MediaUploadsRepository}=require(path.join(main,'apps/api/dist/modules/content/media-uploads.repository.js'));
  const {MediaUploadsService}=require(path.join(main,'apps/api/dist/modules/content/media-uploads.service.js'));
  const questions=read(path.join(bundle,'questions.json')), manifest=read(path.join(bundle,'media-manifest.json'));
  assert.equal(sha(fs.readFileSync(path.join(bundle,'questions.json'))),manifest.questions_sha256);
  const assets=selectOriginalAssets(questions,manifest,bundle);
  const storage=new R2MediaStorage(new ConfigService({...process.env,R2_MEDIA_UPLOADS_ENABLED:mode==='--upload'?'true':process.env.R2_MEDIA_UPLOADS_ENABLED}));
  assert.equal(storage.settings(true).bucket,'numora-bucket');
  const uploader=new MediaUploadsService(new MediaUploadsRepository(),storage);
  const sql=database.getDatabase().client;
  async function businessSnapshot() {
    const versions=await sql`select i.external_id,v.id,v.version_number,v.content_status,md5(row_to_json(v)::text) as hash,
      iv.provenance->>'originalHash' as original_hash from content_import_identities i
      join question_variants q on q.question_id=i.question_id and q.kind='ORIGINAL'
      join question_versions v on v.variant_id=q.id
      left join content_import_versions iv on iv.question_version_id=v.id
      where i.external_id in ${sql(IDS)} order by i.external_id,v.version_number`;
    assert.equal(versions.length,9);
    const packageItems=await sql`select p.id,md5(row_to_json(p)::text) as hash from package_items p
      where p.question_version_id in ${sql(versions.map(v=>v.id))} order by p.id`;
    return normalizeSnapshot({versions,packageItems});
  }
  try {
    const admins=await sql`select role,admin_role from users where id=${actor}`;
    assert.equal(admins.length,1); assert.equal(admins[0].role,'ADMIN');
    assert(['SUPER_ADMIN','CONTENT_DATA_MODERATION'].includes(admins[0].admin_role));
    const current=await businessSnapshot();
    for (const asset of assets) {
      const row=current.versions.find(v=>v.external_id===asset.externalId);
      assert.equal(row.version_number,asset.contentVersion);
      assert.equal(row.original_hash,asset.sourceOriginalHash);
    }
    const baselinePath=path.join(job,'preflight.json');
    if (mode==='--check') {
      if (fs.existsSync(baselinePath)) assert.deepEqual(read(baselinePath).business,current);
      else save(baselinePath,{bundleId,assets,business:current,scope:'UPLOAD_ORIGINAL_PNG_ONLY',actorRole:admins[0].admin_role});
      console.log(JSON.stringify({mode,images:9,sourceMode:'original',businessUnchanged:true}));return;
    }
    assert(fs.existsSync(baselinePath),'Run --check first');
    assert.deepEqual(read(baselinePath).assets,assets);assert.deepEqual(read(baselinePath).business,current);
    const receiptPath=path.join(job,'media-receipts.json');
    const receipts=fs.existsSync(receiptPath)?read(receiptPath):{};
    if (mode==='--upload') {
      for (const a of assets) {
        const key='DRILL_ORIGINAL_'+sha(JSON.stringify({externalId:a.externalId,assetId:a.assetId,contentVersion:a.contentVersion,sha256:a.sha256})).slice(0,40);
        const dto=Object.fromEntries(['externalId','assetId','contentVersion','contentType','byteLength','sha256'].map(k=>[k,a[k]]));
        const reservation=await uploader.reserve(actor,key,dto);
        if (reservation.status!=='VERIFIED') {
          const response=await fetch(reservation.uploadUrl,{method:'PUT',headers:reservation.headers,
            body:fs.readFileSync(path.join(ai,a.filePath)),signal:AbortSignal.timeout(30000)});
          assert(response.ok,'R2 upload failed');
        }
        const receipt=await uploader.complete(actor,reservation.uploadId);
        assert.equal(receipt.status,'VERIFIED');
        for (const k of ['externalId','assetId','contentType','byteLength','sha256']) assert.equal(receipt[k],a[k]);
        receipts[a.externalId]={...receipt,contentVersion:a.contentVersion,sourceOriginalHash:a.sourceOriginalHash};
        save(receiptPath,receipts);
        console.log(JSON.stringify({externalId:a.externalId,status:'VERIFIED'}));
      }
    }
    assert.deepEqual(Object.keys(receipts).sort(),[...IDS].sort());
    const verified=[];
    for (const a of assets) {
      const receipt=receipts[a.externalId];assert.equal(receipt.status,'VERIFIED');
      assert.equal(receipt.objectKey,`question-media/${a.externalId}/v${a.contentVersion}/${a.assetId}-${a.sha256}.png`);
      assert.equal(receipt.sha256,a.sha256);
      const rows=await sql`select status,sha256,content_version from content_media_uploads where id=${receipt.uploadId} and external_id=${a.externalId}`;
      assert.equal(rows.length,1);assert.equal(rows[0].status,'VERIFIED');assert.equal(rows[0].sha256,a.sha256);assert.equal(rows[0].content_version,a.contentVersion);
      const link=await storage.readLink(receipt.bucket,receipt.objectKey);
      const response=await fetch(link.url,{signal:AbortSignal.timeout(20000)});
      assert.equal(response.status,200);const bytes=Buffer.from(await response.arrayBuffer());assert.equal(sha(bytes),a.sha256);assert.equal(bytes.length,a.byteLength);
      verified.push({externalId:a.externalId,status:'VERIFIED',httpStatus:200,sha256:a.sha256,contentVersion:a.contentVersion});
    }
    assert.deepEqual(await businessSnapshot(),read(baselinePath).business);
    const result={mode,images:9,verifiedDownloads:verified,scope:'ORIGINAL_ONLY',
      questionVersionsOrPackagesChanged:false,attachedToQuestions:false,published:false,bundleId};
    save(path.join(job,mode.slice(2)+'-result.json'),result);
    console.log(JSON.stringify({mode,images:9,verifiedR2Downloads:9,questionVersionsOrPackagesChanged:false,attachedToQuestions:false}));
  } finally {await database.closeDatabaseConnection();}
}

module.exports={selectOriginalAssets,IDS,normalizeSnapshot};
if (require.main===module) run(process.argv[2]||'--check').catch(error=>{
  console.error(JSON.stringify({operationFailed:true,code:error?.getResponse?.()?.code||error?.code||error?.name||'UPLOAD_FAILED'}));
  process.exitCode=1;
});
