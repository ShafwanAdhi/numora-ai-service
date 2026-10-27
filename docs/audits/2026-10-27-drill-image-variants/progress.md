# Drill image variants

# SDD ledger - plan: docs/superpowers/plans/2026-10-27-drill-image-variants.md

Stage 1: COMPLETE - archive, 14 placements, 9 diagram families, 5 formula/symbol assets,
5 numeric config v1 pins, 8 conceptual stock pins, source/runtime evidence and hashes.

TDD: three new provenance tests failed before the inventory helper existed,
then passed after implementation (renamed media, protected changes, ambiguous owner).

Verification: archive reconstructed from source plus active runtime; 27 archive
payload files verified, 1265 protected files unchanged, CSV/JSON consistent.

Ruling: implement only Stage 1 this turn - the user's approved plan explicitly
requires waiting for instructions between stages; this overrides skill defaults
that would otherwise continue all implementation tasks.

Ruling: reuse existing isolated feat/tryout-image-variants workspace. Read pins
from the original AI-service checkout because it contains the latest local
uncommitted bank/config state. Copy only this task's newly created artifacts
back with no-clobber checks; no reset/merge/commit of unrelated user changes.

Ruling: archive-to-family mapping does not assert full content identity. Preserve
active revisions, approval status and historical source byte hashes separately.

Runtime edits: NONE. Generator rule edits: NONE. DB/R2 operations: NONE.
Stages 2-5 at Stage-1 checkpoint: NOT STARTED; await user instruction.

## Stage 2: COMPLETE

User instruction: "lanjut ke tahap berikutnya" authorizes Stage 2 only.

- Five numerical v1 templates plus an isolated drill_images adapter reuse the
  existing ImageTemplate/build_scene/render_scene protocol. No existing core,
  bank, config, stock, service or workbench file is edited.
- Three nets are deterministic geometry. Two source illustrations were cleaned
  via built-in image_gen, composited only inside reviewed masks, then used as
  static backgrounds. No runtime model calls.
- TDD red: adapter initially absent; later renderer/template/config pin drift
  and maximum cone label clearance tests failed before fixes. Green: 15 tests.
- Full real-seed audit: 5 originals + all 150 accepted variants; exact question
  record equality, independent math, geometry, label bounds and PNG hashes PASS.
- Regression: 44 image/bundle + 14 Tryout + 4 stateless + 3 workbench tests PASS.
  Total focused/regression tests: 80.
- Independent review: three Important pinning findings fixed; regrade reports
  no remaining Important/Critical issues. Original right tick and maximum-label
  clearance polished and visually checked.
- Desktop 1600x900 and mobile 390x844 preview: 155 cards, images load, no overflow.
- All 1265 pre-existing protected files remain byte-identical in the original
  AI-service checkout. New files are recorded in verification-stage2.json.

Ruling: do not add Drill IDs to the generic Tryout template loader yet. Use a
separate Drill loader/adapter implementing the same image_variants protocol;
this avoids changing existing Tryout renderer code or its artifact identities.
Workbench integration remains Stage 4.

Ruling: pin exact template bytes and reviewed renderer build externally in
registry.py; runtime never refreshes pins. ConfigStore's actual file bytes are
checked in addition to semantic config hashes. A review/version update is
required after renderer/build drift, including Python/Pillow upgrades.

Ruling: five worktree config files had Git CRLF conversion. Restore their exact
original-checkout bytes only inside the worktree (normalized text was equal),
so exact-file pin tests exercise the real inputs. No original config changed.

Ruling: native net proportions are fixed because all accepted numerical inputs
scale by k+1, preserving shape. Numeric labels vary; no random geometry is added.
For pg-16-5-5, attach the dynamic face-height annotation to the horizontal face
altitude. Never bind the v9 statement claim or reveal the hidden cone radius.

Runtime existing-file edits: NONE. Generator rule edits: NONE. DB/R2 calls: NONE.
Stages 3-5: NOT STARTED; wait for the next user instruction.

## Stages 3 and 4: COMPLETE

User instruction: "lanjut sampai tahap 4" explicitly authorizes both stages.

- Stage3: four conceptual originals + eight stocks, 12 scenarios/8 unique PNGs.
  Preserved pg-16-4-2 source original; native geometry for other scenarios.
- Full original/stock snapshot pins, external scenario allowlist, source/font/
  renderer pins; no seed selection, RNG, DB/R2, or runtime image writes.
- Stage4: catalog5 Tryout+9 Drill; mode-aware controls and explicit stock ID.
  Legacy Tryout question_id+seed requests preserved; explicit originals do not draw.
- Generation orchestration is isolated in image_workbench.py. Conceptual image
  route precedes ACTIVE-only generic generation gate, but /api/generate still
  rejects conceptual questions. No generic generator/stock/bank policy changed.
- TDD red: conceptual module absent and HTTP modes/catalog missing; green after
  implementation. 94 relevant tests pass. Independent review reports no findings.
- Browser smoke PASS: delayed response invalidation, catalog-load disabling,
  catalog error/retry, generation error, safe source text, stock download name,
  PNG SHA match and desktop/mobile layout.

Ruling: keep conceptual implementation in sibling drill_concept_images package
so Stage2 numerical adapter code identity and its reviewed template pins remain
unchanged. Common image_variants core remains unchanged for Tryout.

Ruling: same diagram pixels may serve multiple matching records. Record identity
and provenance stay distinct; report 12 scenario occurrences and 8 unique PNGs.

Ruling: do not add p=2*pi*r to pg-16-5-1 stock02 diagram; that is the condition
being asked. Use p, r, h as diagram symbols, without numerical random inputs.

Ruling: dynamic UI script is a fixed same-origin /image-variants.js route;
no arbitrary filesystem serving. Catalog loading disables all controls to avoid
invalidating the pending initial catalog with a stale input event.

Only intended existing runtime edits: webui.py and image_variants.html.
Generator numbers/rules, source bank/revisions/config/stock and numeric/Tryout
template files remain unchanged. DB/R2/publishing: NONE. Stage5: NOT STARTED.

## Stage 5: COMPLETE

User authorized the next stage and explicitly required testing Drill diagrams
in the interface. All 167 selections across all nine families were exercised
through real browser controls on the original checkout's running workbench.

- New opt-in Drill review exporter, separate DRILL_IMAGE_REVIEW kind, no Tryout
  package/schema changes. Full domain167 records/163 distinct PNGs; one-seed
  mode22 records. Reuses existing atomic writer without modifying it.
- No new image/render/math rules. Accepted k search uses existing generator;
  only new k values are rendered from the same accepted Result. Original and
  stock paths never draw. No implicit disk writes, DB/R2, or publishing.
- TDD initial missing-module failure, then7 tests passed. Independent review
  found an Important metadata/provenance binding gap and two Minor consistency
  gaps. Three regression tests reproduced them, then all10 exporter tests passed.
- Fix pass binds asset alt/qid/dimensions/byte length to render provenance,
  derives case IDs from selections and enforces declared common single seed.
  Independent regrade: no remaining findings.
- Final104 related tests pass; independent math155 + conceptual12 PASS.
- Browser167 case proofs match key/stem/mode/original/stock identity and PNG
  bytes. Desktop1600x900/mobile390x844 reviewed; no overflow.
- Final full bundle ID c948bf0bfd6f8b71514aaff0fefac3b1dfed7438a90b4e42c65c1e2e0e89ddc3.

Ruling: expose review export via an explicit standalone tools command, not a
write endpoint or automatic UI cache. Existing interface already supports all
required modes; verify all167 through it rather than adding unrelated controls.

Ruling: retained first export was moved within the isolated workspace's owned
scratch directory after verifying resolved source/target containment. Final
review regenerated under the corrected seed/provenance contract; no user file
or historical source/bank/config was overwritten.

All five local stages complete. Curriculum/IRT approval and cloud/student
activation remain outside scope and unchanged.
