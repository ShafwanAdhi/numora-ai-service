// Read-only cross-repo verification using Numora's built canonical()/digest().
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import path from 'node:path';
const repo = process.env.NUMORA_REPO_PATH || 'D:/Dev/Numora';
const require = createRequire(path.join(repo, 'apps/api/package.json'));
const { canonical, digest } = require(path.join(repo, 'apps/api/dist/modules/content/content-import.validation.js'));
const Ajv = require('ajv/dist/2020').default;
const addFormats = require('ajv-formats').default;
const ajv = new Ajv({ strict: true, allErrors: true });
addFormats(ajv);
const dir = new URL('../../contracts/generator-service-v1/', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, dir)));
for (const name of ['notification','candidate','registration','response']) ajv.addSchema(read(name + '.schema.json'));
for (const f of read('fingerprints.fixture.json')) {
  if (canonical(f.input) !== f.canonical || digest(f.input) !== f.sha256) throw new Error('Numora fingerprint mismatch: ' + f.name);
}
const check = ajv.getSchema('urn:numora:generator-service-v1:candidate');
for (const f of read('candidates.fixture.json')) {
  if (!check(f.payload)) throw new Error(JSON.stringify(check.errors));
  const { contentFingerprint, ...content } = f.payload;
  if (digest(content) !== contentFingerprint) throw new Error('Numora candidate mismatch: ' + f.name);
}
console.log('Numora actual canonical/digest matched 7 fixtures; Ajv compiled 4 schemas and validated 4 candidates');
