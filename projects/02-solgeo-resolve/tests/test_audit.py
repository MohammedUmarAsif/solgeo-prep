import numpy as np
import pytest

from solgeo_resolve import SRAuditConfig, audit_super_resolution


def test_audit_reports_fidelity_and_explicit_product_boundary():
    native = np.array([[[0.2, 0.4], [0.6, 0.8]], [[0.8, 0.6], [0.4, 0.2]]], dtype=np.float32)
    derived = np.repeat(np.repeat(native, 2, axis=1), 2, axis=2)
    result = audit_super_resolution(native, derived, scale=2)
    assert np.all(result.rmse_by_band < 1e-6)
    assert result.spectral_rank_agreement == 1.0
    assert "not genuine sensor resolution" in result.product_label


def test_audit_threshold_is_reflected_in_summary():
    native = np.ones((2, 2, 2), dtype=np.float32)
    derived = np.ones((2, 4, 4), dtype=np.float32)
    result = audit_super_resolution(
        native,
        derived,
        scale=2,
        config=SRAuditConfig(uncertainty_threshold=0.8),
    )
    assert result.summary()["uncertain_pixels"] == 0


def test_audit_rejects_wrong_derived_shape():
    with pytest.raises(ValueError, match="derived spatial shape"):
        audit_super_resolution(np.ones((2, 2, 2)), np.ones((2, 3, 3)), scale=2)
