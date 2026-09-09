# Build plan

## North-star demo

In five minutes, a reviewer should be able to select Dubai, Abu Dhabi, or Al Ain; choose dates and a cloud threshold; see the available acquisitions; inspect an NDVI/NDWI/NDBI/EVI time series; compare a baseline to the latest scene; inspect a desert-edge expansion/cooling-opportunity surface; and export a provenance-rich evidence package for human planning review.

## Phase 0 — validated foundation

- Read the shared MadinatAI project brief and preserve its engineering principles.
- Choose a bounded, scientifically defensible UAE use case.
- Use STAC/COGs rather than manual downloads.
- Establish AOI presets, UTM analysis CRS, cloud/SCL masking, and provenance.

## Phase 1 — first working vertical slice

- Search Sentinel-2 L2A metadata.
- Load only the AOI at 20 m.
- Calculate and chart four indices.
- Build a baseline/latest change surface.
- Rank changes with an explainable 0–100 score.
- Show results in a notebook map and export JSON evidence.
- Add unit tests for masking, index creation, and score bounds.

## Phase 2 — data-fusion upgrade

- Add Sentinel-1 VV/VH and, where feasible, temporal backscatter/coherence for cloud-independent structural context and construction-change confirmation.
- Add ESA WorldCover 2021 as a land-cover context layer.
- Add HLS v2.0 when a longer, harmonized Landsat/Sentinel time series is needed.
- Add thermal observations from Landsat or MODIS only when the project is ready to validate a heat/cooling claim.
- Add spatially separated validation samples and report precision/recall of flags.

## Phase 3 — application upgrade

- Convert notebook controls to Streamlit or Panel.
- Add cached STAC searches and reproducible run manifests.
- Add GeoTIFF/GeoJSON export and a compact report page.
- Keep the notebook as the scientific audit trail.

## Phase 4 — advanced GeoAI, only if justified

- Define a labelled task first: land-cover segmentation, impervious-surface mapping, or disturbance detection at an urban edge.
- Establish a rule-based and Random Forest baseline.
- Benchmark TorchGeo/TerraTorch pretrained models with spatial splits.
- Report uncertainty, class imbalance, spatial leakage risk, and failure examples.

## Phase 5 — optional LLM reporting

- Pass only the evidence JSON, metadata, and limitations to the model.
- Require structured output, acquisition-ID citations, and abstention.
- Log prompt/model/version and keep human review in the loop.
- Never let the LLM choose pixels, labels, or operational actions.

## Definition of done for the MVP

- Fresh Colab runtime succeeds with the install cell.
- At least one public STAC search returns UAE acquisitions.
- The AOI crop stays bounded and the output is inspectable.
- Tests pass for the deterministic core.
- The notebook exposes the main controls and includes limitations.
- The project can be explained in terms of data, algorithm, evaluation, and failure modes.
