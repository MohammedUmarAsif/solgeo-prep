"""Explicit metadata for model-derived high-resolution products."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProductMetadata:
    source_product: str
    native_resolution_m: float
    output_resolution_m: float
    scale_factor: int
    model_name: str
    model_version: str
    input_item_ids: tuple[str, ...]
    uncertainty_method: str
    product_status: str = "model-derived super-resolution; not sensor-measured output"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "input_item_ids": list(self.input_item_ids),
            "warnings": [
                "Output detail is inferred from the model and input context.",
                "Do not use as cadastral, engineering, legal-boundary, or sub-pixel ground truth.",
            ],
        }


def make_product_metadata(
    *,
    source_product: str,
    native_resolution_m: float,
    output_resolution_m: float,
    model_name: str,
    model_version: str,
    input_item_ids: tuple[str, ...] = (),
    uncertainty_method: str = "not computed",
) -> ProductMetadata:
    """Create validated product metadata and reject physically inconsistent claims."""
    if native_resolution_m <= 0 or output_resolution_m <= 0:
        raise ValueError("resolutions must be positive")
    if output_resolution_m >= native_resolution_m:
        raise ValueError("output_resolution_m must be finer than native_resolution_m")
    scale = native_resolution_m / output_resolution_m
    rounded_scale = round(scale)
    if not np_isclose(scale, rounded_scale):
        raise ValueError("native/output resolution must define an integer scale factor")
    return ProductMetadata(
        source_product=source_product,
        native_resolution_m=native_resolution_m,
        output_resolution_m=output_resolution_m,
        scale_factor=rounded_scale,
        model_name=model_name,
        model_version=model_version,
        input_item_ids=input_item_ids,
        uncertainty_method=uncertainty_method,
    )


def np_isclose(first: float, second: float) -> bool:
    return abs(first - second) <= 1e-6 * max(1.0, abs(first), abs(second))
