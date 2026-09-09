# SolGeo Change

SolGeo Change detects persistent candidate change from a time-by-pixel feature
stack. It is intentionally sensor-agnostic: the input can be an optical index,
a SAR backscatter feature, a texture metric, or a model output from another
SolGeo project.

## Intent

A single before/after difference confuses seasonality, atmosphere, landscaping,
construction, and geometric artefacts. SolGeo Change compares a robust early
baseline with later observations, normalizes by baseline variability, and only
flags locations whose change persists across the post-baseline window.

The result is a **review candidate**, never an automatic construction,
desertification, damage, or causality label.

## Capability

- robust median/MAD baseline estimation;
- increase, decrease, or absolute-change directions;
- valid-observation gates for missing/cloud-masked pixels;
- persistence fraction and explainable 0–100 candidate score;
- uncertainty from persistence and valid-observation coverage;
- NumPy-only core suitable for xarray/Dask adapters in downstream projects;
- deterministic tests with synthetic failure and success cases.

## Install and test

```powershell
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Minimal usage

```python
import numpy as np
from solgeo_change import ChangeConfig, detect_persistent_change

observations = np.random.default_rng(4).normal(size=(12, 64, 64)).astype("float32")
result = detect_persistent_change(
    observations,
    ChangeConfig(direction="decrease", threshold=3.0),
)
review_mask = result.candidate
uncertainty = result.uncertainty
```

## Scientific boundary

Candidates need seasonal controls, cloud/geometry QA, multi-sensor
confirmation, spatial validation, and human review before any operational use.
