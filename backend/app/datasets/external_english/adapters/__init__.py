"""Adapters for external English sentence-simplification benchmark datasets."""

from app.datasets.external_english.adapters.asset_adapter import ASSETAdapter
from app.datasets.external_english.adapters.deferred_adapter import SyntheticDeferredAdapter

__all__ = ["ASSETAdapter", "SyntheticDeferredAdapter"]
