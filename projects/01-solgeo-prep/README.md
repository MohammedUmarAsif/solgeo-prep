# SolGeo Prep

SolGeo Prep is a small, reusable Earth-observation preparation package. It
turns public Sentinel-2 STAC items into a bounded xarray analysis cube with
quality checks, common spectral indices, temporal summaries, transparent change
surfaces, and a serializable evidence package.

The UAE desert-edge urban monitor is the first example use case; the package is
not limited to the UAE.

## Intent

Repeated remote-sensing projects should not copy scene search, duplicate
selection, reflectance scaling, cloud masking, index formulas, and provenance
logic into separate notebooks. SolGeo Prep provides those stable building
blocks so future projects can focus on their question and validation.

## Capability

- discovers Sentinel-2 L2A items through a STAC API;
- keeps the clearest item per acquisition date and tile;
- loads a bounded, consistently projected xarray cube;
- applies conservative SCL masking and reflectance sanity checks;
- computes NDVI, NDWI, NDBI, and EVI;
- produces quality tables, monthly composites, temporal summaries, and a
  baseline-versus-latest change surface;
- writes provenance suitable for a human report or a constrained AI reporting
  layer;
- exports small analysis layers as compressed GeoTIFFs with CRS, transform,
  nodata, and checksum-backed run manifests;
- stays honest about proxies, uncertainty, and the need for local validation.

## Install and test

From the repository root:

```powershell
uv sync
uv run pytest
uv run ruff check .
```

The public API is available as `solgeo_prep`. The old
`src.uae_monitor` import remains as a compatibility shim for the UAE notebook.

The metadata-only CLI is useful for checking a run before loading imagery:

```powershell
solgeo-prep search --aoi "Dubai urban cluster" --start 2025-01-01 --end 2025-03-31
```

The offline showcase produces a complete, network-free evidence package:

```powershell
solgeo-prep demo --output-dir outputs/solgeo-prep-demo
```

It writes `manifest.json`, `evidence.json`, `quality_report.csv`, and three
georeferenced raster outputs: latest NDVI, a transparent change score, and a
binary review mask. The demo is synthetic and is labelled as such; it is a
regression and portfolio artifact, not a claim about real UAE conditions.

## Minimal usage

```python
from solgeo_prep import SearchConfig, add_indices, aoi_geometry, load_cube
from solgeo_prep import search_sentinel_items

config = SearchConfig(start="2025-01-01", end="2025-03-31", cloud_cover_max=30)
aoi = aoi_geometry("Dubai urban cluster")
items = search_sentinel_items(config, aoi)
cube = add_indices(load_cube(items, config, aoi))
```

## Scientific boundary

An index or change score is an interpretable screening signal, not proof of
construction, desertification, groundwater depletion, municipal condition, or
causality. Model-derived products from later SolGeo projects will carry an even
stronger native-resolution and hallucination warning.
