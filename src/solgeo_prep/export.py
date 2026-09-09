"""Small GeoTIFF/COG exports with explicit spatial metadata."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
import xarray as xr
from rasterio.enums import Resampling
from rasterio.transform import from_origin


def write_cog(
    data: xr.DataArray,
    path: str | Path,
    *,
    crs: str | None = None,
    nodata: float = -9999.0,
    dtype: str | None = None,
) -> Path:
    """Write a 2D xarray layer as a compressed GeoTIFF with COG-safe layout."""
    if set(data.dims) != {"y", "x"}:
        raise ValueError("data must be a 2D DataArray with y and x dimensions")
    if data.sizes["y"] <= 0 or data.sizes["x"] <= 0:
        raise ValueError("data must have positive spatial dimensions")
    if "x" not in data.coords or "y" not in data.coords:
        raise ValueError("data must provide x and y coordinates")
    x = np.asarray(data.coords["x"].values, dtype=float)
    y = np.asarray(data.coords["y"].values, dtype=float)
    if len(x) < 2 or len(y) < 2:
        raise ValueError("at least two x and y coordinates are required")
    x_step = float(np.median(np.diff(x)))
    y_step = float(np.median(np.diff(y)))
    if (
        not np.isclose(abs(x_step), abs(np.diff(x))).all()
        or not np.isclose(abs(y_step), abs(np.diff(y))).all()
    ):
        raise ValueError("x and y coordinates must be regularly spaced")
    if x_step <= 0:
        raise ValueError("x coordinates must increase")
    if y_step == 0:
        raise ValueError("y coordinates must be distinct")
    top = float(y.max() + abs(y_step) / 2)
    transform = from_origin(float(x.min() - x_step / 2), top, x_step, abs(y_step))
    values = np.asarray(data.transpose("y", "x").values, dtype=np.float32)
    if y_step > 0:
        values = np.flip(values, axis=0)
    values = np.where(np.isfinite(values), values, nodata)
    output_dtype = dtype or "float32"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    height, width = values.shape
    tiled = height >= 16 and width >= 16
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=output_dtype,
        crs=crs or data.attrs.get("crs"),
        transform=transform,
        nodata=nodata,
        compress="deflate",
        predictor=2,
        tiled=tiled,
        blockxsize=256 if tiled else None,
        blockysize=256 if tiled else None,
    ) as destination:
        destination.write(values.astype(output_dtype), 1)
        if tiled and min(height, width) >= 256:
            overview_levels = [level for level in (2, 4, 8, 16) if min(height, width) // level >= 16]
            if overview_levels:
                destination.build_overviews(overview_levels, Resampling.average)
                destination.update_tags(ns="rio_overview", resampling="average")
        destination.update_tags(SOLGEO_PRODUCT="SolGeo Prep raster output", SOLGEO_NODATA=str(nodata))
    return path
