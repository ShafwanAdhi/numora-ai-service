// Independent implementation of Numora's canonical() / digest() for shared fixtures.
import { readFileSync } from 'node:fs';
import { canonical, fingerprint, contentFingerprint } from '../../contracts/generator-service-v1/fingerprint.ts';
const fixtures = JSON.parse(readFileSync(new URL('../../contracts/generator-service-v1/fingerprints.fixture.json', import.meta.url)));
for (const f of fixtures) {
  const serialized = canonical(f.input);
  if (serialized !== f.canonical || fingerprint(f.input) !== f.sha256)
    throw new Error('Fingerprint mismatch: ' + f.name);
}
const candidates = JSON.parse(readFileSync(new URL('../../contracts/generator-service-v1/candidates.fixture.json', import.meta.url)));
for (const f of candidates) {
  if (contentFingerprint(f.payload) !== f.payload.contentFingerprint) throw new Error('Candidate mismatch: ' + f.name);
}
console.log(`${fixtures.length} TypeScript fingerprints + ${candidates.length} candidate fixtures passed`);
