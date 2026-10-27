# Local image variant workbench

ENGINEERING DECISION: add an opt-in local page to the existing Python workbench. No product API, database, R2, configuration, or question-bank changes.

Visual direction: retain the existing neutral surface and teal action, with a large diagram beside the generated question. Controls select one of five reviewed Tryout questions and a positive seed. Loading, empty, error and generated states are explicit; changing inputs clears the result and invalidates pending responses.

## Run

From Numora-ai-service: `python -B variant_gen/webui.py` then open http://127.0.0.1:8765/image-variants. Install requirements-image.txt if Pillow is absent.

- GET /image-variants: page (also linked from existing workbench).
- GET /api/image-variants: reviewed five-question catalog.
- POST /api/image-variants/generate: JSON question_id and integer seed (1..1000000000).

The response contains the normal question record and ephemeral base64 PNG with dimensions, SHA-256, alt text and renderer provenance. This HTTP representation is for local preview/download only; it does not change the persisted media bundle or DB/R2 contracts. The browser creates a revocable PNG Blob URL. No image cache or output files are written by the endpoint.

A single preview invocation supplies the accepted raw Result.values to the renderer callback. Fraction values are not reconstructed from rounded exported values. Current generator and template versions are used; seed reproducibility requires unchanged configs/templates/rendering environment. Config and original hashes and renderer provenance are available in Detail hasil.

## Verification

- Red phase: new routes failed with 404 before implementation.
- 3 new HTTP tests pass, covering all five renderers, one generation call per response, question equivalence, PNG hash, invalid seeds/IDs and cross-origin rejection.
- Existing image renderer/bundle tests: 44 pass.
- Existing stateless workbench tests: 4 pass.
- Browser: 1600x900 desktop and 390x844 mobile; no horizontal overflow; actual PNG loaded. Download Blob SHA-256 matched response metadata (garden seed 1: 92a3d6c175d9a81f5739975648e4b23f05140ba3c2ce14c083f223a2ebc6bb00).
- Independent read-only code review: no Critical/Important findings. Cosmetic separators corrected after review.

Screenshots: desktop.png and mobile.png. No DB/R2 requests were performed by these tests or page generation.
