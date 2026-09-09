"""Resolution-aware audits for model-derived super-resolution products."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .metrics import spectral_angle_map


@dataclass(frozen=True)
class SRAuditConfig:
    """Thresholds for flagging spectral or spatially suspicious output."""

    max_rmse: float = 0.05
    min_rank_agreement: float = 0.9
    uncertainty_threshold: float = 0.45

    def __post_init__(self) -> None:
        if self.max_rmse <= 0:
            raise ValueError("max_rmse must be positive")
        if not 0 < self.min_rank_agreement <= 1:
            raise ValueError("min_rank_agreement must be between 0 and 1")
        if not 0 < self.uncertainty_threshold < 1:
            raise ValueError("uncertainty_threshold must be between 0 and 1")


@dataclass(frozen=True)
class SRAuditResult:
    """Compact, serializable evidence about a derived-resolution product."""

    rmse_by_band: np.ndarray
    mae_by_band: np.ndarray
    bias_by_band: np.ndarray
    spectral_rank_agreement: float
    uncertainty: np.ndarray
    hallucination_warning: np.ndarray
    product_label: str
    uncertainty_threshold: float

    def summary(self) -> dict[str, object]:
        """Return JSON-friendly aggregate evidence for reports and model cards."""
        return {
            "rmse_by_band": self.rmse_by_band.tolist(),
            "mae_by_band": self.mae_by_band.tolist(),
            "bias_by_band": self.bias_by_band.tolist(),
            "spectral_rank_agreement": self.spectral_rank_agreement,
            "uncertain_pixels": int(np.count_nonzero(self.uncertainty > self.uncertainty_threshold)),
            "warning_pixels": int(np.count_nonzero(self.hallucination_warning)),
            "product_label": self.product_label,
        }


def audit_super_resolution(
    native: np.ndarray,
    derived: np.ndarray,
    scale: int,
    band_names: tuple[str, ...] | None = None,
    config: SRAuditConfig | None = None,
) -> SRAuditResult:
    """Compare native pixels with block-reduced model-derived output.

    ``derived`` is evaluated only after reduction to the native grid. The
    result is an audit, not proof that the inferred fine detail is real.
    """
    config = config or SRAuditConfig()
    native = _validate_cube(native, "native")
    derived = _validate_cube(derived, "derived")
    if not isinstance(scale, int) or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if derived.shape[0] != native.shape[0]:
        raise ValueError("native and derived must have the same band count")
    expected = (native.shape[1] * scale, native.shape[2] * scale)
    if derived.shape[1:] != expected:
        raise ValueError(f"derived spatial shape must be {expected}")
    if band_names is not None and len(band_names) != native.shape[0]:
        raise ValueError("band_names must match the band count")

    reduced = derived.reshape(derived.shape[0], native.shape[1], scale, native.shape[2], scale).mean(
        axis=(2, 4)
    )
    residual = reduced - native
    rmse = np.sqrt(np.nanmean(residual**2, axis=(1, 2)))
    mae = np.nanmean(np.abs(residual), axis=(1, 2))
    bias = np.nanmean(residual, axis=(1, 2))
    spectral_angle = spectral_angle_map(native, reduced)
    uncertainty = np.clip(spectral_angle / np.pi, 0, 1).astype(np.float32)
    native_rank = np.argsort(native, axis=0)
    derived_rank = np.argsort(reduced, axis=0)
    rank_agreement = float(np.mean(native_rank == derived_rank))
    warning = (uncertainty > config.uncertainty_threshold) | (
        np.max(np.abs(residual), axis=0) > config.max_rmse
    )
    return SRAuditResult(
        rmse_by_band=rmse.astype(np.float32),
        mae_by_band=mae.astype(np.float32),
        bias_by_band=bias.astype(np.float32),
        spectral_rank_agreement=rank_agreement,
        uncertainty=uncertainty,
        hallucination_warning=warning,
        product_label="model-derived output; not genuine sensor resolution",
        uncertainty_threshold=config.uncertainty_threshold,
    )


def _validate_cube(cube: np.ndarray, name: str) -> np.ndarray:
    cube = np.asarray(cube, dtype=np.float32)
    if cube.ndim != 3 or min(cube.shape) <= 0:
        raise ValueError(f"{name} must have shape (bands, height, width)")
    if not np.isfinite(cube).all():
        raise ValueError(f"{name} must contain only finite values")
    return cube
