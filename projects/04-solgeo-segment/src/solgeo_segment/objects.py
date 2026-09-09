"""Connected components and review-object summaries."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SegmentObject:
    """One connected review object in pixel coordinates."""

    object_id: int
    area_pixels: int
    y0: int
    y1: int
    x0: int
    x1: int
    review_status: str = "needs_review"

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return self.y0, self.y1, self.x0, self.x1


def connected_components(mask: np.ndarray, connectivity: int = 8) -> np.ndarray:
    """Label foreground pixels with deterministic breadth-first traversal."""
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2:
        raise ValueError("mask must have shape (height, width)")
    if connectivity not in {4, 8}:
        raise ValueError("connectivity must be 4 or 8")
    labels = np.zeros(mask.shape, dtype=np.int32)
    neighbours = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if connectivity == 8:
        neighbours += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    next_id = 1
    height, width = mask.shape
    for y, x in zip(*np.nonzero(mask), strict=True):
        if labels[y, x]:
            continue
        queue = deque([(int(y), int(x))])
        labels[y, x] = next_id
        while queue:
            cy, cx = queue.popleft()
            for dy, dx in neighbours:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and labels[ny, nx] == 0:
                    labels[ny, nx] = next_id
                    queue.append((ny, nx))
        next_id += 1
    return labels


def objects_from_mask(
    mask: np.ndarray, min_area_pixels: int = 1, connectivity: int = 8
) -> list[SegmentObject]:
    """Return sorted connected review objects after minimum-area filtering."""
    if min_area_pixels <= 0:
        raise ValueError("min_area_pixels must be positive")
    labels = connected_components(mask, connectivity=connectivity)
    objects: list[SegmentObject] = []
    for object_id in range(1, int(labels.max()) + 1):
        ys, xs = np.nonzero(labels == object_id)
        area = len(ys)
        if area < min_area_pixels:
            continue
        objects.append(
            SegmentObject(
                object_id=object_id,
                area_pixels=area,
                y0=int(ys.min()),
                y1=int(ys.max()) + 1,
                x0=int(xs.min()),
                x1=int(xs.max()) + 1,
            )
        )
    return sorted(objects, key=lambda item: (-item.area_pixels, item.object_id))
