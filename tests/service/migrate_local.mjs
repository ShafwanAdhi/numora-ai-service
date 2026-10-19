// Uses the canonical Numora migrator; this file never reads a repository .env.
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const repo = process.env.NUMORA_REPO_PATH;
const url = new URL(process.env.TEST_COMPUTE_OWNER_URL);
if (!repo || !['127.0.0.1', 'localhost'].includes(url.hostname) || !url.pathname.startsWith('/generator_test_'))
  throw new Error('Isolated local generator test database required');
const { default: postgres } = await import(pathToFileURL(path.join(repo, 'packages/database/node_modules/postgres/src/index.js')));
const { migrateIntegratedDatabase } = await import(pathToFileURL(path.join(repo, 'packages/database/dist/integrated-migrations.js')));
const db = postgres(url.toString(), { max: 1, onnotice: () => {} });
try {
  await migrateIntegratedDatabase(db, path.join(repo, 'packages/database/drizzle'));
  console.log('Canonical Numora migration stream applied to isolated local database');
} finally { await db.end(); }
