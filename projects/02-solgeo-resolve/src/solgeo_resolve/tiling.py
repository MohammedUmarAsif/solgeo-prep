"""Deterministic overlapping windows for bounded-memory raster inference."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TileWindow:
    """A half-open source-image window."""

    y0: int
    y1: int
    x0: int
    x1: int

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def width(self) -> int:
        return self.x1 - self.x0


def _starts(length: int, tile_size: int, stride: int) -> list[int]:
    if length <= tile_size:
        return [0]
    starts = list(range(0, length - tile_size + 1, stride))
    final = length - tile_size
    if starts[-1] != final:
        starts.append(final)
    return starts


def plan_tiles(height: int, width: int, tile_size: int = 256, overlap: int = 32) -> list[TileWindow]:
    """Return complete-coverage overlapping source windows."""
    if height <= 0 or width <= 0:
        raise ValueError("height and width must be positive")
    if tile_size <= 0:
        raise ValueError("tile_size must be positive")
    if not 0 <= overlap < tile_size:
        raise ValueError("overlap must be non-negative and smaller than tile_size")
    stride = tile_size - overlap
    return [
        TileWindow(y, min(y + tile_size, height), x, min(x + tile_size, width))
        for y in _starts(height, tile_size, stride)
        for x in _starts(width, tile_size, stride)
    ]


def blend_weights(height: int, width: int, edge: int = 8) -> np.ndarray:
    """Create positive center-weighted blending weights for one tile."""
    if height <= 0 or width <= 0:
        raise ValueError("tile dimensions must be positive")
    edge = min(max(edge, 0), min(height, width) // 2)
    weights = np.ones((height, width), dtype=np.float32)
    if edge:
        ramp = np.linspace(0.2, 1.0, edge, dtype=np.float32)
        weights[:edge] *= ramp[:, None]
        weights[-edge:] *= ramp[::-1, None]
        weights[:, :edge] *= ramp[None, :]
        weights[:, -edge:] *= ramp[None, ::-1]
    return weights
