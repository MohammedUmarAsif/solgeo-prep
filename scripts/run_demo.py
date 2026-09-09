"""Run a bounded UAE EO analysis and write inspectable outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from solgeo_prep import (  # noqa: E402
    AOIS,
    SearchConfig,
    add_indices,
    aoi_geometry,
    change_surface,
    evidence_summary,
    explainable_change_score,
    load_cube,
    search_sentinel_items,
    summarize_time_series,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi", choices=sorted(AOIS), default="Dubai urban cluster")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2025-03-31")
    parser.add_argument("--cloud", type=float, default=30.0)
    args = parser.parse_args()

    output = Path("outputs")
    output.mkdir(exist_ok=True)
    config = SearchConfig(start=args.start, end=args.end, cloud_cover_max=args.cloud)
    aoi = aoi_geometry(args.aoi)
    items = search_sentinel_items(config, aoi)
    if not items:
        raise RuntimeError("No acquisitions matched. Increase the date range or cloud threshold.")

    cube = add_indices(load_cube(items, config, aoi))
    ts = summarize_time_series(cube)
    change = explainable_change_score(change_surface(cube, "NDVI"))
    evidence = evidence_summary(items, config, args.aoi, ts)
    evidence["flagged_pixel_fraction"] = float(change["flagged"].mean().compute())

    ts.to_csv(output / "uae_index_timeseries.csv", index=False)
    (output / "uae_evidence.json").write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    change["baseline"].plot(ax=axes[0], cmap="viridis", vmin=-1, vmax=1)
    axes[0].set_title("NDVI baseline")
    change["latest"].plot(ax=axes[1], cmap="viridis", vmin=-1, vmax=1)
    axes[1].set_title("NDVI latest")
    change["score"].plot(ax=axes[2], cmap="magma", vmin=0, vmax=100)
    axes[2].set_title("Explainable stress score")
    fig.tight_layout()
    fig.savefig(output / "uae_ndvi_change.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"AOI: {args.aoi}")
    print(f"Acquisitions: {len(items)}")
    print(f"Date range: {ts['date'].min().date()} to {ts['date'].max().date()}")
    print(f"Flagged pixel fraction: {evidence['flagged_pixel_fraction']:.3f}")
    print(ts.to_string(index=False, formatters={k: "{:.4f}".format for k in ["NDVI", "NDWI", "NDBI", "EVI"]}))
    print("Wrote outputs/uae_index_timeseries.csv, outputs/uae_evidence.json, outputs/uae_ndvi_change.png")


if __name__ == "__main__":
    main()
