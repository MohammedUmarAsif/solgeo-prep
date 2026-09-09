"""Persistent, review-oriented Earth-observation change detection."""

from .detector import ChangeConfig, ChangeResult, detect_persistent_change

__all__ = ["ChangeConfig", "ChangeResult", "detect_persistent_change"]
