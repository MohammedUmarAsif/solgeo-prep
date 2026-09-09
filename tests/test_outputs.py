import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import rasterio
import xarray as xr

from solgeo_prep import (
    SearchConfig,
    add_output_checksums,
    build_manifest,
    make_demo_cube,
    quality_report,
    run_demo,
    select_clearest_items,
    write_cog,
)


def _item(item_id: str, cloud: float, tile: str = "40R") -> SimpleNamespace:
    return SimpleNamespace(
        id=item_id,
        datetime=datetime(2024, 1, 1, tzinfo=UTC),
        properties={"eo:cloud_cover": cloud, "s2:mgrs_tile": tile, "collection": "sentinel-2-l2a"},
    )


def test_scene_selection_is_clear_and_deterministic():
    selected = select_clearest_items([_item("cloudy", 20), _item("clear", 5), _item("other", 3, "41R")])
    assert [item.id for item in selected] == ["clear", "other"]


def test_quality_report_counts_missing_reflectance():
    quality = quality_report(make_demo_cube(16).where(make_demo_cube(16)["B04"] > 0))
    assert set(("valid_pixel_fraction", "invalid_pixel_fraction")) <= set(quality.columns)
    assert quality["valid_pixel_fraction"].between(0, 1).all()


def test_manifest_id_and_output_checksum_are_reproducible(tmp_path: Path):
    config = SearchConfig(start="2024-01-01", end="2024-01-31")
    manifest = build_manifest(aoi_name="test", config=config, items=[])
    (tmp_path / "artifact.txt").write_text("stable\n", encoding="utf-8")
    with_outputs = build_manifest(
        aoi_name="test",
        config=config,
        items=[],
        outputs={"artifact": {"path": "artifact.txt", "type": "text"}},
    )
    checked = add_output_checksums(with_outputs, tmp_path)
    assert manifest.run_id == with_outputs.run_id
    assert checked.outputs["artifact"]["bytes"] == 8
    assert len(checked.outputs["artifact"]["sha256"]) == 64


def test_cog_export_has_crs_transform_and_nodata(tmp_path: Path):
    data = xr.DataArray(
        np.array([[1.0, np.nan], [3.0, 4.0]], dtype="float32"),
        dims=("y", "x"),
        coords={"y": [100.0, 80.0], "x": [500.0, 520.0]},
    )
    path = write_cog(data, tmp_path / "layer.tif", crs="EPSG:32640")
    with rasterio.open(path) as dataset:
        assert dataset.crs.to_string() == "EPSG:32640"
        assert dataset.transform.a == 20
        assert dataset.nodata == -9999
        assert dataset.read(1)[0, 1] == -9999


def test_cog_export_normalizes_ascending_y_coordinates(tmp_path: Path):
    data = xr.DataArray(
        np.array([[1.0, 2.0], [3.0, 4.0]], dtype="float32"),
        dims=("y", "x"),
        coords={"y": [80.0, 100.0], "x": [500.0, 520.0]},
    )
    path = write_cog(data, tmp_path / "ascending-y.tif", crs="EPSG:32640")
    with rasterio.open(path) as dataset:
        assert dataset.read(1).tolist() == [[3.0, 4.0], [1.0, 2.0]]


def test_offline_demo_writes_a_manifest_and_readable_outputs(tmp_path: Path):
    manifest_path = run_demo(tmp_path / "demo", size=16)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "solgeo-prep"
    assert payload["validation"]["acquisitions"] == 6
    assert (manifest_path.parent / "latest_ndvi.tif").is_file()
