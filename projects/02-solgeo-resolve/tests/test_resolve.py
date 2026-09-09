import numpy as np
import pytest

from solgeo_resolve import (
    ensemble_uncertainty,
    index_preservation,
    make_product_metadata,
    plan_tiles,
    run_tiled_inference,
    spectral_angle_map,
)


def test_tile_plan_has_complete_non_duplicate_edges():
    tiles = plan_tiles(100, 130, tile_size=64, overlap=8)
    assert tiles[0].y0 == 0 and tiles[0].x0 == 0
    assert max(tile.y1 for tile in tiles) == 100
    assert max(tile.x1 for tile in tiles) == 130


def test_tiled_inference_reassembles_identity_scaled_predictor():
    image = np.arange(2 * 80 * 96, dtype=np.float32).reshape(2, 80, 96)
    result = run_tiled_inference(
        image,
        predictor=lambda tile: tile.repeat(2, axis=1).repeat(2, axis=2),
        scale_factor=2,
        tile_size=32,
        overlap=8,
    )
    assert result.shape == (2, 160, 192)
    np.testing.assert_allclose(result[:, ::2, ::2], image, rtol=0, atol=2e-3)


def test_metrics_report_zero_for_identical_products():
    image = np.ones((3, 4, 4), dtype=np.float32)
    assert np.all(spectral_angle_map(image, image) < 1e-6)
    assert index_preservation(image, image, red=0, nir=1) == 0


def test_uncertainty_and_metadata_are_explicit():
    predictions = np.stack([np.zeros((2, 3, 3)), np.ones((2, 3, 3))])
    summary = ensemble_uncertainty(predictions)
    assert summary["mean"].shape == (2, 3, 3)
    assert summary["mean_std"] > 0
    metadata = make_product_metadata(
        source_product="Sentinel-2 L2A",
        native_resolution_m=10,
        output_resolution_m=2.5,
        model_name="OpenSR",
        model_version="benchmark-pending",
    )
    assert metadata.scale_factor == 4
    assert "not sensor-measured" in metadata.to_dict()["product_status"]


def test_metadata_rejects_non_integer_scale_claim():
    with pytest.raises(ValueError, match="integer scale"):
        make_product_metadata(
            source_product="Sentinel-2 L2A",
            native_resolution_m=10,
            output_resolution_m=3,
            model_name="test",
            model_version="0",
        )
