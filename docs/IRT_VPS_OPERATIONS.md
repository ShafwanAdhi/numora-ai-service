# IRT isolated operations

ENGINEERING DECISION: synthetic research only; all flags default off. No production migration or participant jobs. Main publication remains explicit.

## Capacity gate

Run `python3 tools/irt_capacity.py` on the target **before** starting this stack. Require `READY`; swap does not count. Limits: API 256 MiB, worker 1 GiB, R 2 GiB, disposable PostgreSQL 512 MiB, host reserve 512 MiB; CPU limits sum to 3.25. Do not evict unrelated workloads to pass.

Read-only probe on 10 November 2026: 2 CPU, 3,915 MiB total, 1,615 MiB available, 1,722 MiB swap used. Result **BLOCKED_CAPACITY**; R and stack deployment **NOT_RUN** on VPS. Proposed upgrade: **4 vCPU / 8 GiB**, followed by a new capacity check. Upgrade is not automatic.

## Prepare

1. Load the pinned producer/R image archives into Docker; verify image IDs against `research/irt-runtime-linux-v2.json`. Local image IDs cannot be fetched as registry names. Record archive SHA-256 during transfer. Never retag an unrelated image to bypass verification.
2. Keep secrets outside Git in owner-readable files (`chmod 600`). `IRT_PRIVATE_ENV_FILE` contains `COMPUTE_DATABASE_URL`, `COMPUTE_SERVICE_PRINCIPAL_ID`, `NUMORA_IRT_RESEARCH_TOKEN` (random, at least 32 characters). Database URL uses loopback port 55432 and a **compute-only** login. Never use the PostgreSQL owner or Main role.
3. `IRT_POSTGRES_ENV_FILE` contains disposable `POSTGRES_DB=irt_research_test_<unique suffix>`, `POSTGRES_USER` and `POSTGRES_PASSWORD`. Apply Main's forward migrations and create restricted Main/compute logins in this disposable DB using the owned local harness. No automatic production bootstrap.
4. Export `IRT_PRODUCER_IMAGE`, absolute `IRT_RUNTIME_PROFILE_FILE`, both private environment paths and `IRT_DOCKER_GID` (`stat -c %g /var/run/docker.sock`). Profile/image must match; startup never regenerates pins. Set `NUMORA_IRT_RESEARCH_ENABLED=true` only for the isolated run.
5. After capacity passes, validate without dumping resolved secrets: `docker compose -f deploy/irt-research.compose.yaml --profile research config --quiet`. Start PostgreSQL, initialize the disposable schema/roles, then start API and worker with the same compose file/profile. API binds **127.0.0.1:18080**; PostgreSQL binds **127.0.0.1:55432**. API has no Docker socket. Only worker owns the work volume/socket; R children have no network or database credentials.
6. Tunnel from the workstation: `ssh -i "$env:USERPROFILE\.ssh\bonjermgu-prod" -o IdentitiesOnly=yes -L 18080:127.0.0.1:18080 -L 55432:127.0.0.1:55432 deploy@103.89.4.104`. Main test process uses its separate Main login, synthetic DB and frozen linux-v2 runtime.

## Health and monitoring

`GET /health/live` checks HTTP liveness only. Authenticated `GET /health/ready` checks exact runtime/source/dependency pins, compute role/schema/database and worker heartbeat younger than 45 seconds. Codes are sanitized; responses contain no connection details. Worker additionally verifies the pinned R image locally. Capabilities and execute/status endpoints remain authenticated.

Use Main's batch health and delivery-readiness endpoints alongside durable job/outbox rows. Track backlog count/oldest age, heartbeat/lease, timeout, generation/retry, artifact rejection, exact coverage, fallback mode and result deadline (72 hours). Alert destination, operator and approval owner: **TBD**. Container logs rotate at 10 MiB × 3; API access logs are disabled to avoid query-string digests in logs.

## Stop / rollback

1. Disable Main reconciler/new-job acceptance and publication flags. Stop API intake.
2. Stop worker with its 90-second grace period. SIGTERM stops new claims; interrupted execution exits through owned R-container cleanup without sealing an artifact. Lease expires durably; authorized retry uses existing generation/fencing rules, never automatic silent rerun.
3. Preserve database, artifacts, receipts and published results. Do **not** run `down --volumes`, delete history or execute a down migration.
4. Restore only an application image compatible with applied forward migrations. Its original matching runtime profile must be used; old profiles remain immutable.

## Activation decisions

Synthetic integration, host readiness and production activation are separate decisions. VPS currently blocked by capacity. Production additionally needs delivery acceptance, approved policy/scientific limitations, private connection configuration, operator and explicit Main publication authorization. No deployment follows from merging a PR.
