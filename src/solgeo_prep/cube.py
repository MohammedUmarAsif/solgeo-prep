"""Quality-controlled xarray cube operations for Sentinel-2 preparation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from .config import SearchConfig

REFLECTANCE_BANDS = ("B02", "B03", "B04", "B08", "B11")
REQUIRED_BANDS = (*REFLECTANCE_BANDS, "SCL")
INVALID_SCL_CLASSES = (0, 1, 3, 8, 9, 10, 11)


def validate_cube(cube: xr.Dataset) -> None:
    """Raise a useful error when a cube cannot be processed safely."""
    missing = sorted(set(REQUIRED_BANDS) - set(cube.data_vars))
    if missing:
        raise ValueError(f"Cube is missing required bands: {missing}")
    if "time" not in cube.dims:
        raise ValueError("Cube must have a time dimension")
    spatial_dims = {"x", "y"}.intersection(cube.dims)
    if spatial_dims != {"x", "y"}:
        raise ValueError("Cube must have x and y spatial dimensions")
    if cube.sizes["time"] == 0:
        raise ValueError("Cube contains no acquisitions")
    expected_dims = {"time", "y", "x"}
    for band in REQUIRED_BANDS:
        if set(cube[band].dims) != expected_dims:
            raise ValueError(f"Band {band} must have dimensions time, y, and x")
        if cube[band].sizes != cube["B02"].sizes:
            raise ValueError(f"Band {band} does not share the cube shape")
    if not np.issubdtype(cube.time.dtype, np.datetime64):
        raise ValueError("Cube time coordinate must use datetime64 values")
    for dimension in ("x", "y"):
        coordinates = np.asarray(cube[dimension].values)
        if coordinates.ndim != 1 or len(coordinates) != cube.sizes[dimension]:
            raise ValueError(f"Cube {dimension} coordinate must be one-dimensional")
        if len(coordinates) > 1 and not np.all(np.diff(coordinates) != 0):
            raise ValueError(f"Cube {dimension} coordinate must not repeat")


def load_cube(items: Iterable[Any], config: SearchConfig, aoi: dict[str, Any] | None = None) -> xr.Dataset:
    """Load a small, consistently gridded cube from STAC items."""
    from odc.stac import load

    items = list(items)
    if not items:
        raise ValueError("No imagery matched the AOI/date/cloud filters.")

    cube = load(
        items,
        bands=list(REQUIRED_BANDS),
        crs=config.output_crs,
        resolution=config.resolution_m,
        groupby="solar_day",
        geopolygon=aoi,
        chunks={"time": 1, "x": 1024, "y": 1024},
    ).astype("float32")
    for band in REFLECTANCE_BANDS:
        # Sentinel-2 L2A commonly stores reflectance as integer scale 10,000.
        # The check also keeps already-scaled test fixtures and custom STAC
        # collections usable without a second division.
        if float(cube[band].max()) > 2.0:
            cube[band] = cube[band] / 10000.0
    validate_cube(cube)
    return cube


def _invalid_pixels(cube: xr.Dataset) -> xr.DataArray:
    return cube["SCL"].isin(INVALID_SCL_CLASSES)


def add_indices(cube: xr.Dataset) -> xr.Dataset:
    """Return a copy with cloud-masked NDVI, NDWI, NDBI, and EVI layers."""
    validate_cube(cube)
    cube = cube.copy()
    invalid = _invalid_pixels(cube)
    blue, green, red, nir, swir = (cube[x] for x in REFLECTANCE_BANDS)

    for band in REFLECTANCE_BANDS:
        cube[band] = cube[band].where((cube[band] >= 0) & (cube[band] <= 1.5))

    def ratio(numerator: xr.DataArray, denominator: xr.DataArray) -> xr.DataArray:
        return xr.where(np.abs(denominator) > 1e-6, numerator / denominator, np.nan)

    cube["NDVI"] = ratio(nir - red, nir + red).where(~invalid)
    cube["NDWI"] = ratio(green - nir, green + nir).where(~invalid)
    cube["NDBI"] = ratio(swir - nir, swir + nir).where(~invalid)
    cube["EVI"] = (2.5 * ratio(nir - red, nir + 6 * red - 7.5 * blue + 1)).where(~invalid)
    formulas = {
        "NDVI": "(B08-B04)/(B08+B04)",
        "NDWI": "(B03-B08)/(B03+B08)",
        "NDBI": "(B11-B08)/(B11+B08)",
        "EVI": "2.5*(B08-B04)/(B08+6B04-7.5B02+1)",
    }
    for name, formula in formulas.items():
        cube[name].attrs.update({"formula": formula, "mask": "SCL invalid classes removed"})
    return cube


def valid_pixel_fraction(cube: xr.Dataset) -> xr.DataArray:
    """Return the valid-pixel fraction for each acquisition."""
    validate_cube(cube)
    invalid = _invalid_pixels(cube)
    valid_reflectance: list[xr.DataArray] = [cube[band].notnull() for band in REFLECTANCE_BANDS]
    finite_reflectance = xr.concat(valid_reflectance, dim="band").all("band")
    valid = (~invalid) & finite_reflectance
    return valid.mean(dim=[d for d in valid.dims if d != "time"])


def quality_report(cube: xr.Dataset) -> pd.DataFrame:
    """Create a compact acquisition-level QA table for notebook review."""
    valid = valid_pixel_fraction(cube).compute()
    return (
        pd.DataFrame(
            {
                "date": pd.to_datetime(cube.time.values),
                "valid_pixel_fraction": np.asarray(valid.values, dtype="float64"),
                "invalid_pixel_fraction": 1 - np.asarray(valid.values, dtype="float64"),
            }
        )
        .sort_values("date")
        .reset_index(drop=True)
    )


def monthly_composite(cube: xr.Dataset) -> xr.Dataset:
    """Create robust monthly medians after per-pixel quality masking."""
    validate_cube(cube)
    masked = cube.copy()
    invalid = _invalid_pixels(masked)
    for variable in masked.data_vars:
        if variable != "SCL":
            masked[variable] = masked[variable].where(~invalid)
    return masked.resample(time="1MS").median(skipna=True)


def summarize_time_series(
    cube: xr.Dataset,
    indices: tuple[str, ...] = ("NDVI", "NDWI", "NDBI", "EVI"),
) -> pd.DataFrame:
    """Return AOI-median index values by acquisition date."""
    missing = sorted(set(indices) - set(cube.data_vars))
    if missing:
        raise KeyError(f"Indices are not in the cube: {missing}")
    rows: list[dict[str, Any]] = []
    for timestamp in cube.time.values:
        row: dict[str, Any] = {"date": pd.Timestamp(timestamp)}
        for index in indices:
            row[index] = float(cube[index].sel(time=timestamp).median(skipna=True).compute())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def change_surface(cube: xr.Dataset, index: str = "NDVI", baseline_fraction: float = 0.5) -> xr.Dataset:
    """Compare the latest acquisition with an early temporal baseline."""
    validate_cube(cube)
    if index not in cube:
        raise KeyError(f"Index {index!r} is not in the cube")
    if not 0 < baseline_fraction < 1:
        raise ValueError("baseline_fraction must be greater than 0 and less than 1")
    n = cube.sizes["time"]
    split = max(1, int(np.floor(n * baseline_fraction)))
    if split >= n:
        raise ValueError("cube needs at least one acquisition after the baseline")
    baseline = cube[index].isel(time=slice(0, split)).median("time", skipna=True)
    latest = cube[index].isel(time=-1)
    delta = latest - baseline
    return xr.Dataset(
        {
            "baseline": baseline,
            "latest": latest,
            "delta": delta,
            "drop": xr.where(delta < 0, -delta, 0),
        }
    )


def explainable_change_score(change: xr.Dataset, drop_threshold: float = 0.15) -> xr.Dataset:
    """Create a transparent 0-100 stress score from index change."""
    if drop_threshold <= 0:
        raise ValueError("drop_threshold must be positive")
    if "drop" not in change:
        raise ValueError("change dataset must contain a 'drop' variable")
    drop_component = np.clip(change["drop"] / drop_threshold, 0, 1)
    score = (100 * drop_component).clip(0, 100)
    return change.assign(score=score, flagged=score >= 50)
