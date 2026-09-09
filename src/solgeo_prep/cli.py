"""Command-line entry points for small, reproducible preparation tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import AOIS, aoi_geometry, search_sentinel_items
from .config import SearchConfig
from .demo import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="solgeo-prep",
        description="Discover and prepare bounded Earth-observation inputs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    search = subparsers.add_parser("search", help="Search Sentinel-2 STAC metadata")
    search.add_argument("--aoi", choices=sorted(AOIS), default="Dubai urban cluster")
    search.add_argument("--start", default="2025-01-01")
    search.add_argument("--end", default="2025-03-31")
    search.add_argument("--cloud", type=float, default=30.0)
    search.add_argument("--output", type=Path, default=Path("outputs/solgeo_search.json"))
    demo = subparsers.add_parser("demo", help="Run the deterministic offline showcase")
    demo.add_argument("--output-dir", type=Path, default=Path("outputs/solgeo_demo"))
    demo.add_argument("--size", type=int, default=64, help="Synthetic raster width and height")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "search":
        config = SearchConfig(start=args.start, end=args.end, cloud_cover_max=args.cloud)
        items = search_sentinel_items(config, aoi_geometry(args.aoi))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "tool": "solgeo-prep",
            "aoi": args.aoi,
            "config": config.__dict__,
            "items": [
                {
                    "id": item.id,
                    "datetime": item.datetime.isoformat() if item.datetime else None,
                    "cloud_cover": item.properties.get("eo:cloud_cover"),
                }
                for item in items
            ],
        }
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Found {len(items)} acquisitions; wrote {args.output}")
    elif args.command == "demo":
        manifest = run_demo(args.output_dir, size=args.size)
        print(f"Wrote deterministic SolGeo Prep demo to {manifest.parent}")
    return 0
