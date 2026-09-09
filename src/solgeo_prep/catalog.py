"""STAC discovery and small, reusable AOI helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from shapely.geometry import box, mapping

from .config import SearchConfig

AOIS: dict[str, dict[str, Any]] = {
    "Dubai urban cluster": {
        "bbox": (55.10, 25.00, 55.40, 25.30),
        "description": "A bounded Dubai urban-growth sample window",
    },
    "Abu Dhabi urban cluster": {
        "bbox": (54.35, 24.30, 54.70, 24.60),
        "description": "A bounded Abu Dhabi urban-growth sample window",
    },
    "Al Ain urban cluster": {
        "bbox": (55.60, 24.00, 55.90, 24.30),
        "description": "A bounded Al Ain urban/peri-urban sample window",
    },
}


def aoi_geometry(name: str) -> dict[str, Any]:
    """Return a GeoJSON geometry for a named AOI preset."""
    if name not in AOIS:
        raise KeyError(f"Unknown AOI {name!r}; choose from {sorted(AOIS)}")
    return mapping(box(*AOIS[name]["bbox"]))


def select_clearest_items(items: Iterable[Any]) -> list[Any]:
    """Keep the clearest item per acquisition date and tile deterministically."""
    best: dict[tuple[Any, Any], Any] = {}
    for item in items:
        timestamp = getattr(item, "datetime", None)
        properties = getattr(item, "properties", {})
        tile = properties.get("s2:mgrs_tile") or properties.get("mgrs:utm_zone") or "unknown"
        acquisition = timestamp.date() if timestamp is not None else getattr(item, "id", "unknown")
        key = (acquisition, tile)
        cloud = float(properties.get("eo:cloud_cover", 100.0))
        current = best.get(key)
        current_cloud = (
            float(getattr(current, "properties", {}).get("eo:cloud_cover", 100.0)) if current else 100.0
        )
        if current is None or cloud < current_cloud or (cloud == current_cloud and item.id < current.id):
            best[key] = item

    def sort_key(item: Any) -> str:
        timestamp = getattr(item, "datetime", None)
        return timestamp.isoformat() if timestamp is not None else getattr(item, "id", "")

    return sorted(best.values(), key=sort_key)


def search_sentinel_items(config: SearchConfig, aoi: dict[str, Any]) -> list[Any]:
    """Search public STAC metadata and keep the clearest item per date/tile."""
    import planetary_computer
    import pystac_client

    catalog = pystac_client.Client.open(config.stac_url, modifier=planetary_computer.sign_inplace)
    search = catalog.search(
        collections=[config.collection],
        intersects=aoi,
        datetime=f"{config.start}/{config.end}",
        query={"eo:cloud_cover": {"lte": config.cloud_cover_max}},
        max_items=config.max_items,
    )
    return select_clearest_items(search.items())
