"""Reproducible case-study bundles for the SolGeo learning project.

The first bundle is an offline method preview.  It uses a deterministic
fixture so the website, tests, and learning exercises work without credentials
or a GPU.  The bundle schema is intentionally the same one used by the future
real Sentinel-2/AlphaEarth runner.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from shapely.geometry import box, mapping

from .alphaearth import annual_cosine_distance, encode_demo_embeddings
from .change import agreement_mask, combine_change_evidence
from .config import SearchConfig
from .cube import add_indices
from .demo import make_demo_cube
from .export import write_cog
from .manifest import add_output_checksums, build_manifest, write_manifest


@dataclass(frozen=True)
class CaseConfig:
    """Human-readable settings shared by the CLI, notebook, and website."""

    case_id: str = "abu-dhabi-urban-edge"
    title: str = "Abu Dhabi urban-edge change evidence"
    aoi_name: str = "Abu Dhabi urban cluster"
    bbox: tuple[float, float, float, float] = (54.35, 24.30, 54.70, 24.60)
    baseline_period: str = "2018-01/2018-03"
    comparison_period: str = "2025-01/2025-03"
    analysis_crs: str = "EPSG:32640"
    analysis_resolution_m: int = 20
    data_mode: str = "synthetic-method-preview"
    evidence_status: str = "method-preview"

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> CaseConfig:
        """Create a config while allowing a small YAML/JSON file to override defaults."""

        defaults = asdict(cls())
        defaults.update(values)
        if isinstance(defaults["bbox"], list):
            defaults["bbox"] = tuple(defaults["bbox"])
        if len(defaults["bbox"]) != 4:
            raise ValueError("bbox must contain west, south, east, north")
        return cls(**defaults)


def read_case_config(path: str | Path) -> CaseConfig:
    """Read a beginner-friendly JSON or YAML case configuration."""

    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        values = json.loads(text)
    else:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise RuntimeError("YAML configs require the pyyaml dependency") from exc
        values = yaml.safe_load(text)
    if not isinstance(values, dict):
        raise ValueError("case config must contain a mapping of settings")
    return CaseConfig.from_mapping(values)


def build_method_preview(output_dir: str | Path, config: CaseConfig | None = None, size: int = 64) -> Path:
    """Build deterministic images, scores, vectors, and a claim-aware manifest."""

    config = config or CaseConfig()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cube = add_indices(make_demo_cube(size))
    before = cube.isel(time=slice(0, 3)).median("time", skipna=True)
    after = cube.isel(time=slice(3, 6)).median("time", skipna=True)
    before_ndvi = np.asarray(before["NDVI"].values, dtype="float32")
    after_ndvi = np.asarray(after["NDVI"].values, dtype="float32")
    spectral_change = np.clip(-(after_ndvi - before_ndvi) / 0.15, 0, 1)

    baseline_vectors, comparison_vectors = _demo_embedding_pair(size)
    embedding_distance = annual_cosine_distance(baseline_vectors, comparison_vectors)
    score = combine_change_evidence(spectral_change, embedding_distance)
    agreement = agreement_mask(spectral_change, embedding_distance)

    assets = {
        "before_rgb": "before_rgb.png",
        "after_rgb": "after_rgb.png",
        "spectral_change": "spectral_change.png",
        "embedding_distance": "embedding_distance.png",
        "agreement": "agreement.png",
        "heuristic_score": "heuristic_score.tif",
        "embedding_distance_cog": "embedding_distance.tif",
        "candidates": "candidates.geojson",
    }
    _save_rgb(before, output_dir / assets["before_rgb"])
    _save_rgb(after, output_dir / assets["after_rgb"])
    _save_heatmap(spectral_change, output_dir / assets["spectral_change"], "magma", 0, 1)
    _save_heatmap(embedding_distance, output_dir / assets["embedding_distance"], "viridis", 0, 0.5)
    _save_heatmap(agreement.astype("float32"), output_dir / assets["agreement"], "Blues", 0, 1)

    score_layer = xr.DataArray(score, dims=("y", "x"), coords={"y": before.y, "x": before.x})
    distance_layer = xr.DataArray(embedding_distance, dims=("y", "x"), coords={"y": before.y, "x": before.x})
    write_cog(score_layer, output_dir / assets["heuristic_score"], crs=config.analysis_crs)
    write_cog(distance_layer, output_dir / assets["embedding_distance_cog"], crs=config.analysis_crs)

    candidates = _candidate_features(score, config.bbox)
    (output_dir / assets["candidates"]).write_text(
        json.dumps({"type": "FeatureCollection", "features": candidates}, indent=2) + "\n",
        encoding="utf-8",
    )

    time_series = _time_series(cube)
    quality = _quality_rows(cube)
    summary = {
        "case": asdict(config),
        "status": {
            "label": "Method preview",
            "evidence_status": config.evidence_status,
            "claims_locked": True,
            "synthetic_fixture": True,
            "message": (
                "Synthetic fixture for learning and interface testing. "
                "Replace with reviewed real imagery before making accuracy claims."
            ),
        },
        "question": (
            "Under a fixed annotation budget, do annual embeddings improve spatial transfer "
            "and reduce false change alarms over seasonal optical baselines?"
        ),
        "methods": [
            {"id": "s2", "name": "Seasonal Sentinel-2 features", "role": "Interpretation baseline"},
            {
                "id": "alphaearth",
                "name": "AlphaEarth annual embeddings",
                "role": "Representation change signal",
            },
            {"id": "fusion", "name": "Evidence fusion", "role": "Human-review prioritization"},
        ],
        "metrics": {
            "candidate_area_ha": round(float(np.sum(score >= 0.65) * 0.04), 2),
            "candidate_pixels": int(np.sum(score >= 0.65)),
            "agreement_fraction": round(float(np.mean(agreement)), 3),
            "embedding_distance_p95": round(float(np.nanpercentile(embedding_distance, 95)), 3),
            "minimum_valid_pixel_fraction": round(min(float(row["valid_fraction"]) for row in quality), 3),
        },
        "time_series": time_series,
        "quality": quality,
        "layers": [
            {"id": "before", "label": "Baseline composite", "path": assets["before_rgb"], "kind": "rgb"},
            {"id": "after", "label": "Comparison composite", "path": assets["after_rgb"], "kind": "rgb"},
            {
                "id": "spectral",
                "label": "Spectral change score",
                "path": assets["spectral_change"],
                "kind": "score",
            },
            {
                "id": "embedding",
                "label": "Embedding distance",
                "path": assets["embedding_distance"],
                "kind": "score",
            },
            {
                "id": "agreement",
                "label": "Evidence agreement",
                "path": assets["agreement"],
                "kind": "agreement",
            },
        ],
        "candidates": [
            {
                "id": feature["properties"]["id"],
                "label": feature["properties"]["label"],
                "area_ha": feature["properties"]["area_ha"],
                "score": feature["properties"]["heuristic_score"],
                "interpretation": (
                    "Review candidate: spectral and embedding signals are elevated in this fixture."
                ),
            }
            for feature in candidates
        ],
        "limitations": [
            "This preview uses a deterministic synthetic fixture and is not an observation of Abu Dhabi.",
            "Embedding distance is a screening score, not a calibrated probability of change.",
            "No accuracy number is shown until independent spatial labels are reviewed.",
        ],
        "learning": {
            "start_here": (
                "Read docs/LEARNING-PATH.md, then run the CLI command shown in docs/REPRODUCE.md."
            ),
            "next_exercise": (
                "Change the fusion weights, rebuild the bundle, and explain how the candidate area changes."
            ),
        },
    }
    data_path = output_dir / "case-study.json"
    data_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    output_metadata = {
        key: {"path": value, "type": "COG" if value.endswith(".tif") else "web-asset"}
        for key, value in assets.items()
    }
    manifest = build_manifest(
        aoi_name=config.aoi_name,
        config=SearchConfig(
            start="2018-01-01",
            end="2025-03-31",
            output_crs=config.analysis_crs,
            resolution_m=config.analysis_resolution_m,
        ),
        items=[],
        outputs=output_metadata | {"case_study": {"path": "case-study.json", "type": "JSON"}},
        validation={
            "status": config.evidence_status,
            "claims_locked": True,
            "synthetic_fixture": True,
            "candidate_count": len(candidates),
            "agreement_fraction": float(np.mean(agreement)),
        },
    )
    return write_manifest(add_output_checksums(manifest, output_dir), output_dir / "manifest.json")


def publish_case(run_dir: str | Path, web_root: str | Path) -> Path:
    """Copy a validated case bundle into the static website data directory."""

    run_dir = Path(run_dir)
    web_root = Path(web_root)
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"run is missing {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("validation", {}).get("claims_locked") is not True:
        raise ValueError("publishing requires an explicit claim gate")
    destination = web_root / "data" / "abu-dhabi-urban-edge"
    destination.mkdir(parents=True, exist_ok=True)
    for path in run_dir.iterdir():
        if path.is_file():
            shutil.copy2(path, destination / path.name)
    return destination


def _demo_embedding_pair(size: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(20260910)
    base = rng.normal(0, 1, size=(size, size, 64)).astype("float32")
    base /= np.linalg.norm(base, axis=-1, keepdims=True)
    comparison = base.copy()
    changed = np.zeros((size, size), dtype=bool)
    changed[size * 3 // 5 : size * 4 // 5, size // 8 : size * 3 // 8] = True
    comparison[changed, :8] += 0.9
    comparison /= np.linalg.norm(comparison, axis=-1, keepdims=True)
    return encode_demo_embeddings(base), encode_demo_embeddings(comparison)


def _save_rgb(layer: xr.Dataset, path: Path) -> None:
    red = np.asarray(layer["B04"].values, dtype="float32")
    green = np.asarray(layer["B03"].values, dtype="float32")
    blue = np.asarray(layer["B02"].values, dtype="float32")
    rgb = np.stack([red, green, blue], axis=-1)
    low, high = np.nanpercentile(rgb, [2, 98])
    rgb = np.clip((rgb - low) / max(high - low, 1e-6), 0, 1) ** 0.85
    plt.imsave(path, np.nan_to_num(rgb, nan=0.0))


def _save_heatmap(values: np.ndarray, path: Path, cmap: str, minimum: float, maximum: float) -> None:
    masked = np.ma.masked_invalid(np.asarray(values, dtype="float32"))
    plt.imsave(path, masked, cmap=cmap, vmin=minimum, vmax=maximum)


def _time_series(cube: xr.Dataset) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for timestamp in cube.time.values:
        rows.append(
            {
                "date": str(timestamp)[:10],
                "ndvi": round(float(cube["NDVI"].sel(time=timestamp).median()), 3),
                "ndbi": round(float(cube["NDBI"].sel(time=timestamp).median()), 3),
            }
        )
    return rows


def _quality_rows(cube: xr.Dataset) -> list[dict[str, float | str]]:
    rows = []
    for timestamp in cube.time.values:
        finite = np.isfinite(cube["B04"].sel(time=timestamp).values)
        rows.append({"date": str(timestamp)[:10], "valid_fraction": round(float(finite.mean()), 3)})
    return rows


def _candidate_features(score: np.ndarray, bbox: tuple[float, float, float, float]) -> list[dict[str, Any]]:
    mask = np.asarray(score) >= 0.65
    rows, cols = np.where(mask)
    if len(rows) == 0:
        return []
    height, width = score.shape
    west, south, east, north = bbox
    min_col, max_col = int(cols.min()), int(cols.max()) + 1
    min_row, max_row = int(rows.min()), int(rows.max()) + 1
    x0 = west + (east - west) * min_col / width
    x1 = west + (east - west) * max_col / width
    y1 = north - (north - south) * min_row / height
    y0 = north - (north - south) * max_row / height
    feature = {
        "type": "Feature",
        "geometry": mapping(box(x0, y0, x1, y1)),
        "properties": {
            "id": "candidate-001",
            "label": "Synthetic urban-edge candidate",
            "area_ha": round(float(len(rows) * 0.04), 2),
            "heuristic_score": round(float(np.nanmean(score[mask])), 3),
        },
    }
    return [feature]
