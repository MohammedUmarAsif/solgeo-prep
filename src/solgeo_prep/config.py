"""Configuration objects shared by SolGeo preparation workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SearchConfig:
    """Reproducible settings for a bounded Sentinel-2 preparation run."""

    start: str = "2024-01-01"
    end: str = "2025-12-31"
    cloud_cover_max: float = 10.0
    collection: str = "sentinel-2-l2a"
    stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1"
    output_crs: str = "EPSG:32640"
    resolution_m: int = 20
    max_items: int = 200

    def __post_init__(self) -> None:
        try:
            start = date.fromisoformat(self.start)
            end = date.fromisoformat(self.end)
        except ValueError as exc:
            raise ValueError("start and end must be ISO dates (YYYY-MM-DD)") from exc
        if start > end:
            raise ValueError("start must not be after end")
        if not 0 <= self.cloud_cover_max <= 100:
            raise ValueError("cloud_cover_max must be between 0 and 100")
        if self.resolution_m <= 0:
            raise ValueError("resolution_m must be positive")
        if self.max_items <= 0:
            raise ValueError("max_items must be positive")
        if not self.output_crs.strip():
            raise ValueError("output_crs must not be empty")
