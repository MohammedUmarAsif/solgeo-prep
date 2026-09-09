# SolGeo Resolve

SolGeo Resolve is a model-agnostic, low-VRAM foundation for trustworthy
Sentinel-2 super-resolution. It provides the engineering that is usually left
to each experiment: overlapping tiles, weighted seam blending, bounded memory,
uncertainty summaries, spectral-fidelity metrics, and metadata that says the
result is model-derived rather than sensor-measured.

The default scientific backend is intended to be an ESA OpenSR/SEN2SR adapter.
This repository deliberately keeps that heavyweight dependency optional. The
core can be tested with any callable predictor and a deterministic bilinear
baseline.

## Intent

AI super-resolution may infer plausible fine structure, but it cannot recover
measurements that Sentinel-2 never observed. Every output must therefore carry
the warning: **model-derived high-resolution output from native Sentinel-2; not
genuine sensor data at the output spacing**.

## Capability

- validates native/output resolution claims and model-derived product metadata;
- plans memory-bounded overlapping windows for large rasters;
- runs any predictor through tiled, weighted, seam-reduced inference;
- supplies a dependency-free bilinear baseline;
- computes spectral-angle and normalized-difference preservation metrics;
- summarizes ensemble or repeated-inference uncertainty;
- audits native-grid reconstruction with per-band RMSE, spectral rank agreement,
  uncertainty maps, and explicit hallucination-warning pixels;
- keeps OpenSR integration optional so CPU tests and lightweight installs remain
  reliable.

## Install and test

```powershell
uv sync
uv run pytest
uv run ruff check .
```

## Minimal usage

```python
import numpy as np

from solgeo_resolve import run_tiled_inference

image = np.random.default_rng(7).random((4, 128, 128), dtype=np.float32)
output = run_tiled_inference(
    image,
    predictor=lambda tile: tile.repeat(4, axis=1).repeat(4, axis=2),
    scale_factor=4,
    tile_size=64,
    overlap=8,
)
```

## Scientific boundary

Visual sharpness is not sufficient evidence of quality. Compare native,
interpolated, and model-derived products using spectral fidelity, downstream
task performance, uncertainty, and failure cases around bright sand, rooftops,
roads, coastlines, and shadows. Do not use these outputs for cadastral,
engineering, legal-boundary, or sub-pixel ground-truth claims.

```python
from solgeo_resolve import audit_super_resolution

audit = audit_super_resolution(native_cube, model_derived_cube, scale=4)
print(audit.summary())
```
