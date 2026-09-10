# SolGeo Change Evidence — Luna Implementation Handoff

## Purpose

Build a readable, reproducible portfolio project that tests whether annual
AlphaEarth embeddings improve persistent urban-edge change review over a
seasonal Sentinel-2 baseline in Abu Dhabi.

The project serves two audiences: you as the learner, and recruiters or PhD
interviewers evaluating engineering and research judgment. Every concept is
introduced through a short module, runnable command, test, and exercise.

The hypothesis is:

> Under a fixed annotation budget, do annual embeddings improve spatial
> transfer and reduce false change alarms over seasonal optical baselines in
> arid landscapes?

## Current milestone

The first implementation milestone is a local method preview:

- `solgeo_prep.alphaearth` decodes signed-byte embeddings correctly and keeps
  `-128` as nodata.
- `solgeo_prep.change` combines spectral and embedding signals as a bounded
  heuristic score, never as a probability.
- `solgeo_prep.case` builds a deterministic bundle with images, COGs, GeoJSON,
  JSON evidence, and checksums.
- `web/` is a static Next.js research interface with an accessible slider,
  local MapLibre raster workspace, layer catalogue, chart, downloads, claim
  gate, research page, and reproduce page.
- All preview evidence is visibly marked synthetic. Accuracy claims are locked.

Run it:

```powershell
uv sync
uv run pytest
uv run solgeo-prep case build --config configs/abu-dhabi-urban-edge.yaml --output runs/abu-dhabi-urban-edge-preview
uv run solgeo-prep case publish --run runs/abu-dhabi-urban-edge-preview --web-root web/public
cd web
npm install
npm run dev
```

## Architecture

```text
case config → Python scientific functions → validated case bundle
                                     ↓
                            static Next.js reader
```

Python owns scientific computation. The website owns explanation and
interaction. Vercel serves static assets; it does not process rasters.

Keep boundaries short and single-purpose:

- `alphaearth.py`: decode, normalize, compare, and demo encoding.
- `change.py`: persistence, evidence fusion, and agreement.
- `case.py`: case configuration and bundle orchestration.
- `cube.py`: cube validation and spectral indices.
- `manifest.py`: deterministic run IDs and SHA-256 records.
- `demo.py`: deterministic offline fixture.
- `web/components/`: one interactive idea per component.
- `web/lib/types.ts`: the website data contract.

Do not put new scientific logic inside the notebook or React components.

## Evidence and claim policy

The current bundle is `method-preview`:

1. Evidence gate: real imagery, QA, source IDs, dates, maps, and methods can be
   shown.
2. Annotation gate: independent reviewed transitions and a fixed split are
   added.
3. Accuracy gate: precision, recall, F1, IoU, PR-AUC, calibration, and
   uncertainty are shown only after the annotation protocol passes review.

AlphaEarth distance is a candidate feature. It is not a probability, physical
quantity, or proof of urban construction. Native imagery remains necessary for
interpretation.

## Research upgrade path

1. Repair STAC pagination, provider scale/offset, SCL resampling, coverage QA,
   seasonal baselines, persistence, and complete manifests.
2. Add an official-index AlphaEarth COG adapter. Discover filenames from the
   index; never guess tile paths.
3. Create spatially blocked annotation templates and a locked test set.
4. Compare B0 spectral, B1 AlphaEarth, B2 fused, and later B3 SAR features
   under comparable tuning and annotation budgets.
5. Add failure slices: bright sand, roofs, irrigation, tides, cloud edges,
   registration offsets, and partial coverage.
6. Replace synthetic assets with real seasonal composites and reviewed labels.
7. Publish a paper-style report including null results, uncertainty, compute,
   limitations, and licences.

## Tool choices

- Taste skill: visual language for a research portfolio, not generic dashboard
  defaults.
- Serena MCP: semantic repository exploration and safe refactoring.
- Context7 MCP: current library contracts before dependency changes.
- Modern Python: `uv`, Ruff, pytest, and ty.
- Next.js App Router: static server-rendered shell with small client islands.
- MapLibre: local image source, avoiding a basemap credential.
- Browser verification: route, interaction, console, and responsive checks.

## Acceptance criteria

- `uv run pytest`, Ruff, `npm run typecheck`, and `npm run build` pass.
- Homepage, case page, research page, and reproduce page render.
- Slider, layer buttons, downloads, and MapLibre workspace work.
- No public preview text implies synthetic values are Abu Dhabi results.
- Every visible metric traces to `case-study.json` and `manifest.json`.
- A beginner can follow `docs/LEARNING-PATH.md` and `docs/REPRODUCE.md`.
