# SolGeo learning path

Use this project as a sequence of small wins. Read the concept, run the
command, open the output, then complete the exercise before adding another
library.

## Loop 0 — get oriented

Read `README.md`, `docs/REPRODUCE.md`, and `src/solgeo_prep/demo.py`.

```powershell
uv sync
uv run pytest
uv run solgeo-prep demo --output-dir outputs/solgeo-prep-demo --size 32
```

Learn packages, imports, functions, paths, JSON, and tests.

Exercise: find the deterministic random seed in `demo.py`. Change it, rebuild
the demo, and explain why the checksum changes.

## Loop 1 — pixels and masks

Read `src/solgeo_prep/cube.py` and `tests/test_core.py`.

Learn xarray dimensions, nodata, boolean masks, spectral indices, and why a
class mask must not be interpolated like reflectance.

Exercise: add a test for a NaN in one required band. Decide whether the pixel
should be valid and make the test describe your decision.

## Loop 2 — embeddings

Read `src/solgeo_prep/alphaearth.py` and `tests/test_research.py`.

Learn vectors, norms, cosine similarity, signed bytes, nonlinear decoding, and
nodata propagation.

Exercise: create identical and orthogonal vectors. Predict the distance before
running the test.

## Loop 3 — evidence fusion

Read `src/solgeo_prep/change.py` and `src/solgeo_prep/case.py`.

Learn thresholding, persistence, weighted signals, heuristic scores, and why
calibration requires labels.

Exercise: change the spectral/embedding weights. Record candidate area and
write one paragraph about the trade-off.

## Loop 4 — provenance

Read `src/solgeo_prep/manifest.py` and a generated `runs/.../manifest.json`.

Learn run IDs, checksums, COG metadata, and the difference between an input,
an output, and a claim.

Exercise: delete an output and run the checksum step. Why is a hard failure
safer than silently publishing an incomplete bundle?

## Loop 5 — interactive explanation

Read `web/components/BeforeAfter.tsx`, `EvidenceMap.tsx`, `CaseExplorer.tsx`,
and `web/app/globals.css`.

Learn client components, state, accessibility labels, MapLibre image sources,
and the separation between computation and presentation.

Exercise: add a visible active-layer description driven by the `CaseStudy` data
contract instead of a duplicated hard-coded string.

## Loop 6 — real evidence

Only start after the earlier loops feel comfortable. Learn STAC pagination,
provider encoding, seasonal compositing, AlphaEarth index discovery,
annotation design, spatial holdouts, and evaluation.

Deliver one small real AOI run with source IDs, QA, a manifest, and a
limitations paragraph. Do not add an accuracy score until labels are reviewed.

## Weekly rhythm

Spend one session reading, one changing one function, and one writing or
repairing a test. Keep a research log:

```text
I expected...
I observed...
Next I will...
```
