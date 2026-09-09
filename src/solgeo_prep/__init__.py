"""Reusable, provenance-first preparation utilities for Earth observation data."""

from .catalog import AOIS, aoi_geometry, search_sentinel_items, select_clearest_items
from .config import SearchConfig
from .cube import (
    add_indices,
    change_surface,
    explainable_change_score,
    load_cube,
    monthly_composite,
    quality_report,
    summarize_time_series,
    valid_pixel_fraction,
    validate_cube,
)
from .demo import make_demo_cube, run_demo
from .evidence import evidence_summary
from .export import write_cog
from .manifest import RunManifest, add_output_checksums, build_manifest, write_manifest

__all__ = [
    "AOIS",
    "SearchConfig",
    "RunManifest",
    "add_indices",
    "aoi_geometry",
    "change_surface",
    "evidence_summary",
    "make_demo_cube",
    "explainable_change_score",
    "load_cube",
    "monthly_composite",
    "quality_report",
    "search_sentinel_items",
    "select_clearest_items",
    "summarize_time_series",
    "valid_pixel_fraction",
    "validate_cube",
    "run_demo",
    "write_cog",
    "add_output_checksums",
    "build_manifest",
    "write_manifest",
]
