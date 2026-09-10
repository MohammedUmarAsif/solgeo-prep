"""Command-line entry points for small, reproducible preparation tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .case import build_method_preview, publish_case, read_case_config
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
    case = subparsers.add_parser("case", help="Build or publish a reproducible research case bundle")
    case_subparsers = case.add_subparsers(dest="case_command", required=True)
    build = case_subparsers.add_parser("build", help="Build the offline method preview")
    build.add_argument("--config", type=Path, default=Path("configs/abu-dhabi-urban-edge.yaml"))
    build.add_argument("--output", type=Path, default=Path("runs/abu-dhabi-urban-edge-preview"))
    build.add_argument("--size", type=int, default=64)
    publish = case_subparsers.add_parser("publish", help="Publish a validated run into the web data folder")
    publish.add_argument("--run", type=Path, required=True)
    publish.add_argument("--web-root", type=Path, default=Path("web/public"))
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
    elif args.command == "case" and args.case_command == "build":
        config = read_case_config(args.config)
        manifest = build_method_preview(args.output, config=config, size=args.size)
        print(f"Wrote {config.evidence_status} case bundle to {manifest.parent}")
    elif args.command == "case" and args.case_command == "publish":
        destination = publish_case(args.run, args.web_root)
        print(f"Published case bundle to {destination}")
    return 0
