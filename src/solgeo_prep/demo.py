"""Deterministic offline demonstration for portfolio and regression checks."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from .config import SearchConfig
from .cube import add_indices, change_surface, explainable_change_score, quality_report, summarize_time_series
from .evidence import evidence_summary
from .export import write_cog
from .manifest import add_output_checksums, build_manifest, write_manifest


def make_demo_cube(size: int = 64) -> xr.Dataset:
    """Create a deterministic desert-edge cube with vegetation and urban stress."""
    if size < 16:
        raise ValueError("size must be at least 16")
    rng = np.random.default_rng(20260910)
    time = pd.date_range("2024-01-01", periods=6, freq="MS")
    y = 2_760_000.0 - np.arange(size, dtype=float) * 20
    x = 500_000.0 + np.arange(size, dtype=float) * 20
    shape = (len(time), size, size)
    noise = rng.normal(0, 0.004, size=shape).astype("float32")
    base = {
        "B02": 0.14 + noise,
        "B03": 0.19 + noise,
        "B04": 0.25 + noise,
        "B08": 0.52 + noise,
        "B11": 0.34 + noise,
    }
    vegetation = np.zeros((size, size), dtype="float32")
    vegetation[size // 5 : size // 2, size // 5 : size // 2] = 0.08
    base["B08"] += vegetation
    base["B04"] -= vegetation * 0.25
    urban_change = np.zeros((size, size), dtype="float32")
    urban_change[size * 3 // 5 : size * 4 // 5, size // 8 : size * 3 // 8] = 0.07
    for band in ("B02", "B03", "B04"):
        base[band][3:, :, :] += urban_change
    base["B08"][3:, :, :] -= urban_change * 0.7
    scl = np.full(shape, 4, dtype="int16")
    scl[1, size // 2 : size // 2 + 4, :] = 9
    return xr.Dataset(
        {name: (("time", "y", "x"), values.astype("float32")) for name, values in base.items()}
        | {"SCL": (("time", "y", "x"), scl)},
        coords={"time": time, "y": y, "x": x},
        attrs={"crs": "EPSG:32640", "resolution_m": 20},
    )


def run_demo(output_dir: str | Path, size: int = 64) -> Path:
    """Run the offline workflow and return its manifest path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = SearchConfig(
        start="2024-01-01",
        end="2024-06-30",
        cloud_cover_max=30,
        output_crs="EPSG:32640",
        resolution_m=20,
    )
    cube = add_indices(make_demo_cube(size))
    quality = quality_report(cube)
    time_series = summarize_time_series(cube)
    change = explainable_change_score(change_surface(cube))

    quality_path = output_dir / "quality_report.csv"
    quality.to_csv(quality_path, index=False)
    evidence_path = output_dir / "evidence.json"
    evidence_path.write_text(
        json.dumps(evidence_summary([], config, "Dubai demo window", time_series, quality), indent=2) + "\n",
        encoding="utf-8",
    )
    write_cog(cube["NDVI"].isel(time=-1), output_dir / "latest_ndvi.tif", crs=config.output_crs)
    write_cog(change["score"], output_dir / "change_score.tif", crs=config.output_crs)
    write_cog(change["flagged"].astype("float32"), output_dir / "change_flagged.tif", crs=config.output_crs)

    output_metadata = {
        "quality_report": {"path": "quality_report.csv", "type": "CSV"},
        "evidence": {"path": "evidence.json", "type": "JSON"},
        "latest_ndvi": {"path": "latest_ndvi.tif", "type": "COG", "crs": config.output_crs},
        "change_score": {"path": "change_score.tif", "type": "COG", "crs": config.output_crs},
        "change_flagged": {"path": "change_flagged.tif", "type": "COG", "crs": config.output_crs},
    }
    manifest = build_manifest(
        aoi_name="Dubai demo window",
        config=config,
        items=[],
        outputs=output_metadata,
        validation={
            "acquisitions": int(cube.sizes["time"]),
            "minimum_valid_pixel_fraction": float(quality["valid_pixel_fraction"].min()),
            "flagged_pixels": int(change["flagged"].sum()),
            "change_score_definition": "100 * clipped negative index change / drop threshold",
        },
    )
    manifest = add_output_checksums(manifest, output_dir)
    return write_manifest(manifest, output_dir / "manifest.json")
