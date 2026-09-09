import numpy as np
import xarray as xr

from solgeo_prep import SearchConfig, validate_cube
from src.uae_monitor import (
    add_indices,
    aoi_geometry,
    change_surface,
    explainable_change_score,
)


def synthetic_cube() -> xr.Dataset:
    values = {"B02": 0.1, "B03": 0.2, "B04": 0.3, "B08": 0.6, "B11": 0.4, "SCL": 4}
    coords = {
        "time": np.array(["2024-01-01", "2024-02-01"], dtype="datetime64[ns]"),
        "y": [0, 1],
        "x": [0, 1],
    }
    return xr.Dataset(
        {
            key: (("time", "y", "x"), np.full((2, 2, 2), value, dtype="float32"))
            for key, value in values.items()
        },
        coords=coords,
    )


def test_indices_are_added_and_masked():
    original = synthetic_cube()
    result = add_indices(original)
    assert {"NDVI", "NDWI", "NDBI", "EVI"}.issubset(result.data_vars)
    assert float(result["NDVI"].isel(time=0).mean()) > 0
    assert "NDVI" not in original


def test_cloud_shadow_class_is_masked():
    cube = synthetic_cube()
    cube["SCL"].loc[{"time": cube.time[0]}] = 9
    result = add_indices(cube)
    assert np.isnan(result["NDVI"].isel(time=0)).all()


def test_change_score_is_bounded():
    result = explainable_change_score(change_surface(add_indices(synthetic_cube())))
    assert float(result["score"].min()) >= 0
    assert float(result["score"].max()) <= 100


def test_aoi_is_geojson_polygon():
    assert aoi_geometry("Dubai urban cluster")["type"] == "Polygon"


def test_search_config_rejects_invalid_cloud_threshold():
    import pytest

    with pytest.raises(ValueError, match="cloud_cover_max"):
        SearchConfig(cloud_cover_max=101)


def test_cube_validation_requires_scl():
    cube = synthetic_cube().drop_vars("SCL")
    import pytest

    with pytest.raises(ValueError, match="SCL"):
        validate_cube(cube)


def test_change_parameters_are_validated():
    import pytest

    with pytest.raises(ValueError, match="baseline_fraction"):
        change_surface(add_indices(synthetic_cube()), baseline_fraction=0)

    with pytest.raises(ValueError, match="drop_threshold"):
        explainable_change_score(change_surface(add_indices(synthetic_cube())), drop_threshold=0)
