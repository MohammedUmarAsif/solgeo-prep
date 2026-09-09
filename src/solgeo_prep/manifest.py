"""Reproducible run manifests and output checksums."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import SearchConfig


@dataclass(frozen=True)
class RunManifest:
    """Bounded evidence about one SolGeo Prep execution."""

    tool: str
    run_id: str
    aoi: str
    config: dict[str, Any]
    inputs: list[dict[str, Any]]
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = (
        "Spectral indices are screening proxies, not causal labels.",
        "SCL masking does not remove every atmospheric or geometric artefact.",
        "Results require local spatial and temporal validation before operational use.",
    )

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-compatible evidence with deterministic field ordering."""
        return asdict(self) | {"limitations": list(self.limitations)}


def build_manifest(
    *,
    aoi_name: str,
    config: SearchConfig,
    items: list[Any],
    outputs: dict[str, dict[str, Any]] | None = None,
    validation: dict[str, Any] | None = None,
) -> RunManifest:
    """Build a stable manifest whose ID changes when inputs/settings change."""
    inputs = [_item_record(item) for item in items]
    config_dict = asdict(config)
    fingerprint = json.dumps(
        {"aoi": aoi_name, "config": config_dict, "inputs": inputs},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    run_id = hashlib.sha256(fingerprint).hexdigest()[:16]
    return RunManifest(
        tool="solgeo-prep",
        run_id=run_id,
        aoi=aoi_name,
        config=config_dict,
        inputs=inputs,
        outputs=outputs or {},
        validation=validation or {},
    )


def add_output_checksums(manifest: RunManifest, root: str | Path) -> RunManifest:
    """Return a copy with file size and SHA-256 recorded for each output."""
    root = Path(root)
    outputs: dict[str, dict[str, Any]] = {}
    for name, metadata in manifest.outputs.items():
        relative = Path(str(metadata["path"]))
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        outputs[name] = metadata | {
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
    return RunManifest(
        tool=manifest.tool,
        run_id=manifest.run_id,
        aoi=manifest.aoi,
        config=manifest.config,
        inputs=manifest.inputs,
        outputs=outputs,
        validation=manifest.validation,
        limitations=manifest.limitations,
    )


def write_manifest(manifest: RunManifest, path: str | Path) -> Path:
    """Write an indented UTF-8 JSON manifest and return its path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _item_record(item: Any) -> dict[str, Any]:
    properties = getattr(item, "properties", {})
    timestamp = getattr(item, "datetime", None)
    return {
        "id": getattr(item, "id", "unknown"),
        "datetime": timestamp.isoformat() if timestamp is not None else None,
        "cloud_cover": properties.get("eo:cloud_cover"),
        "collection": properties.get("collection"),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
