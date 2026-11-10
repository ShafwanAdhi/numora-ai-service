# Local Tryout release acceptance

Owner-approved synthetic research scope, 10 November 2026. Main PR
[Numora #149](https://github.com/ayiinee/Numora/pull/149) adds restricted adoption,
whole-delivered-arm fallback and atomic publication. Main owns decisions, DDL,
private identities and student results. AI continues to emit unmodified
`irt-calibration-v1`; comparison and self-adjustment remain unsupported.

```powershell
python tools/verify_irt_linux.py --main-repo '<Main checkout>' --delivery --main-release-check --output .scratch/irt-release
```

Build the Main database/orchestration packages first. The optional release check
requires canonical `--delivery` fixtures, uses Main's fixed
`scripts/test-irt-release-cases.mjs`, and only receives loopback disposable DB
connections owned by this harness. Fixture setup uses the fixture role;
application assertions use the restricted Main runtime role.
It verifies adoption/publication replay, exact coverage, reader gating and
unchanged attempt/answer/XP contents. Output is aggregate synthetic evidence.
The callback does not run in the producer image or alter runtime/source pins.

All release policy fixtures are `RESEARCH_ONLY`; production activation is not
authorized. Follow Main's `docs/IRT_TRYOUT_RELEASE_HANDOFF.md` for configuration,
release endpoints, monitoring and rollback. Read the actual `cases` and
`releaseChecks` in the report: transport success does not imply scientific
calibration/linking success. Never rewrite a sealed artifact to force a result.
Default invocation without `--main-release-check` retains compute-only behavior.

To resume only a missing scenario, add `--delivery-case DELIVERY_PARTIAL`
(or `DELIVERY_TWO_ARM` / `INSUFFICIENT`). The report records that selection;
one selected case is not evidence that other cases passed. Source/image pins
are verified before every invocation. This does not change runtime concurrency.
