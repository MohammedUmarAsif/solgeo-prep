"""Reusable, provenance-first preparation utilities for Earth observation data."""

from .alphaearth import (
    DecodedEmbedding,
    annual_cosine_distance,
    cosine_distance,
    decode_signed_embeddings,
    encode_demo_embeddings,
    normalize_embeddings,
)
from .case import CaseConfig, build_method_preview, publish_case, read_case_config
from .catalog import AOIS, aoi_geometry, search_sentinel_items, select_clearest_items
from .change import agreement_mask, combine_change_evidence, persistent_mask
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
    "CaseConfig",
    "DecodedEmbedding",
    "SearchConfig",
    "RunManifest",
    "add_indices",
    "agreement_mask",
    "annual_cosine_distance",
    "aoi_geometry",
    "build_method_preview",
    "combine_change_evidence",
    "cosine_distance",
    "decode_signed_embeddings",
    "change_surface",
    "evidence_summary",
    "encode_demo_embeddings",
    "make_demo_cube",
    "explainable_change_score",
    "load_cube",
    "monthly_composite",
    "normalize_embeddings",
    "persistent_mask",
    "publish_case",
    "read_case_config",
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
