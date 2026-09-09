# SolGeo Segment

SolGeo Segment is a human-correctable feature-extraction core for Earth
observation rasters. It converts a binary proposal mask into connected review
objects, preserves object-level provenance, and applies explicit human edits.

The package is ready for an optional SAMGeo or supervised-model adapter, but it
does not hide a foundation model behind a misleading one-line prediction.

## Capability

- threshold-based deterministic proposal masks;
- 4- or 8-connected component extraction;
- minimum mapping-unit filtering;
- compact object records with pixel area and bounding boxes;
- add/remove review edits with an edit log;
- probability-map conversion with boundary uncertainty and review routing;
- NumPy-only core suitable for GeoTIFF/GeoPackage adapters.

## Install and test

```powershell
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Scientific boundary

Proposals are not validated land-cover or building labels. Human review,
spatially separated reference data, topology checks, and task-specific accuracy
assessment are required before operational use.

```python
from solgeo_segment import segment_probability

result = segment_probability(probability_map, min_area_pixels=9)
review_pixels = result.needs_review
objects = result.objects
```
