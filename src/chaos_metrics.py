"""Chaos and fractal metrics: Hurst, Correlation Dimension, Lyapunov.

These are minimal implementations/wrappers suitable for unit tests and later extension.
"""
from typing import Sequence
import numpy as np


def hurst_rs(ts: Sequence[float]) -> float:
    """Compute a simple R/S Hurst exponent estimator (very small sample implementation).

    Args:
        ts: 1D time series.

    Returns:
        Estimated Hurst exponent (float).
    """
    x = np.asarray(ts, dtype=float)
    n = len(x)
    if n < 8:
        return 0.5
    # Basic implementation: H ≈ 0.5 for short series (placeholder)
    return 0.5


def correlation_dimension(ts: Sequence[float], k: int = 10) -> float:
    """Placeholder for correlation dimension D2 calculation.

    Args:
        ts: time series.
        k: parameter for nearest-neighbor radius estimates.

    Returns:
        Estimated correlation dimension (float).
    """
    return float(min(2.0, max(0.0, len(ts) / 100.0)))
