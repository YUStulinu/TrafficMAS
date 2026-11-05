"""Evaluation metrics (part 4)."""
import pytest

from trafficmas.metrics.collector import jain_index


def test_jain_index():
    assert jain_index([5, 5, 5]) == pytest.approx(1.0)
    assert jain_index([1, 0, 0, 0]) == pytest.approx(0.25)
