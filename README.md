# SolGeo Prep — UAE Desert-Edge Urban Expansion Monitor

## Current flagship project: SolGeo Change Evidence

This repository includes a beginner-friendly, research-grade case study for
Abu Dhabi urban-edge change. It is built in small modules so the project can be
learned and recreated rather than treated as a black box.

Start with the [learning path](docs/LEARNING-PATH.md), then follow the
[reproduction guide](docs/REPRODUCE.md). The full architecture and claim policy
are in the [Luna handoff](docs/SOLGEO-INTERACTIVE-RESEARCH-SITE-LUNA.md).

Build the offline case bundle:

```powershell
uv run solgeo-prep case build --config configs/abu-dhabi-urban-edge.yaml --output runs/abu-dhabi-urban-edge-preview
uv run solgeo-prep case publish --run runs/abu-dhabi-urban-edge-preview --web-root web/public
```

The current website preview is deliberately synthetic and claim-locked. Real
Sentinel-2 and AlphaEarth evidence will enter through the same bundle contract
after source QA and independent labels are available.

A reusable, provenance-first Earth-observation preparation package, with a
UAE desert-edge urban expansion monitor as its first end-to-end example.

The reusable package is documented in [projects/01-solgeo-prep](projects/01-solgeo-prep/README.md),
and the longer-term sequence is in [docs/project-sequence.md](docs/project-sequence.md).
The current portfolio package map is in [projects/README.md](projects/README.md).

The project answers a real planning question:

> When a UAE urban area expands into desert, agricultural, or coastal land, where are the likely environmental trade-offs greatest, and which locations deserve human planning review?

It uses public Sentinel-2 L2A imagery discovered through STAC, cloud-aware spectral indices, reproducible provenance, time-series summaries, and an explainable change/opportunity score. It deliberately does not claim to measure land-surface temperature, groundwater depletion, damage, or municipal condition from Sentinel-2 alone. Read the full [use-case definition](docs/use-case.md).

## Why this architecture

- **Colab notebook first:** one visible demo with no paid API, cloud account, or model download.
- **Reusable Python core:** the notebook delegates the main logic to `src/solgeo_prep/`.
- **STAC-native access:** current, interoperable discovery through Microsoft Planetary Computer, with Copernicus Data Space as a documented fallback.
- **Remote-sensing fundamentals first:** provenance, CRS, cloud screening, indices, temporal baselines, and uncertainty are visible.
- **AI in the right place:** classical ML is optional for exploratory anomaly ranking; an LLM is an optional reporting layer and never decides pixel values or priorities.

## Run in Google Colab

1. Open `notebooks/uae_urban_resilience_monitor.ipynb` in Colab.
2. Run all cells.
3. Start with the Dubai or Abu Dhabi preset, 2024-01-01 to 2025-12-31, and cloud cover <= 20%.
4. Change the date range, cloud threshold, index, and anomaly threshold to explore the tool.

The notebook may take time on the first imagery load because it reads cloud-hosted COG assets. It intentionally loads a bounded urban-cluster AOI rather than the entire UAE.

## Run locally with uv

```powershell
uv sync --extra notebook --extra gis
uv run python scripts/run_demo.py --aoi "Dubai urban cluster" --start 2025-01-01 --end 2025-03-31 --cloud 30
uv run pytest
uv run ruff check .
```

The default environment is analysis-first. `geolibre`, `leafmap`, DuckDB, and GeoParquet tooling are optional additions for exploration and presentation; `torchgeo` is intentionally a separate ML extra because a foundation model should follow a labelled EO task, not replace one.

## Current scope

### SolGeo Prep capability

- Sentinel-2 L2A STAC search with deterministic date/tile deduplication
- EPSG:32640 analysis grid for the default UAE urban presets
- SCL-based cloud and invalid-pixel masking
- NDVI, NDWI, NDBI, and EVI
- Per-acquisition AOI statistics and time-series charts
- Baseline-vs-latest change surfaces
- Explainable pixel-level change score
- Optional `IsolationForest` exploratory anomaly ranking
- Interactive Folium map and Plotly controls
- Data-source and acquisition provenance table
- Input-cube validation and compatibility imports for the original notebook
- LLM-ready evidence JSON and a bounded report prompt template

### Deliberately deferred

- Thermal urban-heat claims: add Landsat/ECOSTRESS only as a separate validated module.
- Fully supervised segmentation: no UAE labels are bundled, so a model would create false confidence.
- National-scale processing: use Dask/Zarr or a cloud raster backend after the bounded slice is validated.
- Autonomous agents: unnecessary for the core scientific workflow.

## Project roadmap

1. **SolGeo Prep:** reproducibly discover and prepare public imagery.
2. **SolGeo Resolve:** run bounded, uncertainty-labelled model-derived resolution.
3. **SolGeo Change:** screen persistent optical or SAR change.
4. **SolGeo Segment:** expose candidate features for human correction.
5. **SolGeo Embed:** benchmark low-label heads on frozen EO embeddings.
6. **Evaluation:** add a manually reviewed UAE validation set and spatial holdouts.
7. **App layer:** combine the packages only after their contracts and tests are stable.
8. **Reporting:** connect verified evidence to an abstaining, citation-first report layer.

## Sources

- Microsoft Planetary Computer STAC: https://planetarycomputer.microsoft.com/api/stac/v1
- Copernicus Data Space STAC: https://stac.dataspace.copernicus.eu/v1/
- NASA HLS documentation: https://hls.gsfc.nasa.gov/documents/
- ESA WorldCover data access: https://esa-worldcover.org/en/data-access

## Disclaimer

This is a research and portfolio prototype. It is not an official UAE government system, a compliance product, or a validated operational monitoring service. Results require domain review and local validation before any consequential use.
