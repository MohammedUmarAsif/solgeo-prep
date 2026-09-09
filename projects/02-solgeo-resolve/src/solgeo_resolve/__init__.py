"""Trustworthy, low-VRAM building blocks for model-derived EO resolution."""

from .audit import SRAuditConfig, SRAuditResult, audit_super_resolution
from .inference import run_tiled_inference
from .metadata import ProductMetadata, make_product_metadata
from .metrics import ensemble_uncertainty, index_preservation, spectral_angle_map
from .tiling import TileWindow, plan_tiles

__all__ = [
    "ProductMetadata",
    "SRAuditConfig",
    "SRAuditResult",
    "audit_super_resolution",
    "TileWindow",
    "ensemble_uncertainty",
    "index_preservation",
    "make_product_metadata",
    "plan_tiles",
    "run_tiled_inference",
    "spectral_angle_map",
]
