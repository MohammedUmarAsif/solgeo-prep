"""Model-agnostic tiled inference and deterministic interpolation baseline."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .tiling import blend_weights, plan_tiles

Predictor = Callable[[np.ndarray], np.ndarray]


def bilinear_resize(image: np.ndarray, scale_factor: int) -> np.ndarray:
    """Resize ``(bands, height, width)`` data without changing band values."""
    image = _validate_image(image)
    if scale_factor <= 0:
        raise ValueError("scale_factor must be positive")
    if scale_factor == 1:
        return image.copy()
    _, height, width = image.shape
    y = np.linspace(0, height - 1, height * scale_factor)
    x = np.linspace(0, width - 1, width * scale_factor)
    y0 = np.floor(y).astype(int)
    x0 = np.floor(x).astype(int)
    y1 = np.minimum(y0 + 1, height - 1)
    x1 = np.minimum(x0 + 1, width - 1)
    wy = (y - y0).astype(np.float32)
    wx = (x - x0).astype(np.float32)
    top = image[:, y0][:, :, x0] * (1 - wx)[None, None, :] + image[:, y0][:, :, x1] * wx[None, None, :]
    bottom = image[:, y1][:, :, x0] * (1 - wx)[None, None, :] + image[:, y1][:, :, x1] * wx[None, None, :]
    return (top * (1 - wy)[None, :, None] + bottom * wy[None, :, None]).astype(image.dtype)


def run_tiled_inference(
    image: np.ndarray,
    predictor: Predictor,
    scale_factor: int,
    tile_size: int = 256,
    overlap: int = 32,
) -> np.ndarray:
    """Run a predictor over overlapping tiles and blend the scaled outputs."""
    image = _validate_image(image)
    if scale_factor <= 0:
        raise ValueError("scale_factor must be positive")
    bands, height, width = image.shape
    output_height, output_width = height * scale_factor, width * scale_factor
    output = np.zeros((bands, output_height, output_width), dtype=np.float32)
    weights = np.zeros((output_height, output_width), dtype=np.float32)

    for window in plan_tiles(height, width, tile_size, overlap):
        tile = image[:, window.y0 : window.y1, window.x0 : window.x1]
        prediction = np.asarray(predictor(tile))
        expected_shape = (bands, window.height * scale_factor, window.width * scale_factor)
        if prediction.shape != expected_shape:
            raise ValueError(f"Predictor returned {prediction.shape}; expected {expected_shape}")
        edge = max(1, overlap * scale_factor // 2)
        tile_weights = blend_weights(prediction.shape[1], prediction.shape[2], edge=edge)
        ys = slice(window.y0 * scale_factor, window.y1 * scale_factor)
        xs = slice(window.x0 * scale_factor, window.x1 * scale_factor)
        output[:, ys, xs] += prediction.astype(np.float32) * tile_weights[None, :, :]
        weights[ys, xs] += tile_weights

    return output / np.maximum(weights[None, :, :], 1e-6)


def _validate_image(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image)
    if image.ndim != 3:
        raise ValueError("image must have shape (bands, height, width)")
    if min(image.shape) <= 0:
        raise ValueError("image dimensions must be positive")
    if not np.issubdtype(image.dtype, np.number):
        raise TypeError("image must contain numeric values")
    return image
