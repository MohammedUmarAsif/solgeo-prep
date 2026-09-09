"""Serializable provenance for reports and optional AI-assisted explanations."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from .config import SearchConfig


def evidence_summary(
    items: Iterable[Any],
    config: SearchConfig,
    aoi_name: str,
    ts: pd.DataFrame,
    quality: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Create a bounded evidence package with methods and limitations."""
    acquisitions = [
        {
            "id": item.id,
            "datetime": item.datetime.isoformat() if item.datetime else None,
            "cloud_cover": item.properties.get("eo:cloud_cover"),
            "collection": config.collection,
        }
        for item in items
    ]
    return {
        "tool": "solgeo-prep",
        "aoi": aoi_name,
        "stac_url": config.stac_url,
        "collection": config.collection,
        "analysis_crs": config.output_crs,
        "resolution_m": config.resolution_m,
        "indices": {
            "NDVI": "(B08-B04)/(B08+B04)",
            "NDWI": "(B03-B08)/(B03+B08)",
            "NDBI": "(B11-B08)/(B11+B08)",
            "EVI": "2.5*(B08-B04)/(B08+6B04-7.5B02+1)",
        },
        "acquisitions": acquisitions,
        "time_series": ts.assign(date=ts["date"].astype(str)).to_dict(orient="records"),
        "quality_report": (
            quality.assign(date=quality["date"].astype(str)).to_dict(orient="records")
            if quality is not None
            else []
        ),
        "limitations": [
            "Spectral indices are proxies, not municipal-condition ground truth.",
            "Cloud/SCL masking does not remove every atmospheric or geometric artefact.",
            "The anomaly score is exploratory and requires local validation.",
        ],
    }
