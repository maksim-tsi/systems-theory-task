"""Chaos and fractal metrics: Hurst exponent and correlation dimension."""
from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

try:  # Optional dependency
    import nolds  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    nolds = None


def hurst_rs(ts: Sequence[float]) -> float:
    """Estimate the Hurst exponent via rescaled range (R/S) analysis.

    Args:
        ts: 1D time series.

    Returns:
        Estimated Hurst exponent.
    """
    x = np.asarray(ts, dtype=float)
    n = len(x)
    if n < 64 or np.allclose(np.std(x), 0.0):
        return 0.5

    max_window = n // 4
    window_sizes = _logspace_windows(8, max_window)
    if len(window_sizes) < 2:
        return 0.5

    rs_values = []
    used_windows = []
    for w in window_sizes:
        n_segments = n // w
        if n_segments < 2:
            continue
        rs_segment = []
        for i in range(n_segments):
            segment = x[i * w : (i + 1) * w]
            seg_mean = segment.mean()
            dev = segment - seg_mean
            cum_dev = np.cumsum(dev)
            r = np.max(cum_dev) - np.min(cum_dev)
            s = np.std(segment, ddof=1)
            if s > 0:
                rs_segment.append(r / s)
        if rs_segment:
            rs_values.append(np.mean(rs_segment))
            used_windows.append(w)

    if len(rs_values) < 2:
        return 0.5

    log_rs = np.log(rs_values)
    log_w = np.log(used_windows)
    slope, _ = np.polyfit(log_w, log_rs, 1)
    return float(slope)


def correlation_dimension(ts: Sequence[float], k: int = 10) -> float:
    """Estimate correlation dimension D2 using a GP-style approach.

    Uses `nolds.corr_dim` if available, otherwise falls back to a simple
    Grassberger–Procaccia estimator with 2D embedding.

    Args:
        ts: 1D time series.
        k: Number of radii to evaluate (or passed to nolds).

    Returns:
        Estimated correlation dimension D2.
    """
    x = np.asarray(ts, dtype=float)
    if len(x) < 128 or np.allclose(np.std(x), 0.0):
        return 0.0

    if nolds is not None:
        try:
            return float(nolds.corr_dim(x, emb_dim=2, rvals=k))
        except Exception:
            pass

    return float(_corr_dim_gp(x, k=k))


def compute_chaos_metrics(ts: Sequence[float], k: int = 10) -> dict[str, float]:
    """Compute Hurst exponent and correlation dimension for a series.

    Args:
        ts: 1D time series.
        k: Parameter for correlation dimension.

    Returns:
        Dict with keys "hurst" and "d2".
    """
    return {
        "hurst": hurst_rs(ts),
        "d2": correlation_dimension(ts, k=k),
    }


def _logspace_windows(min_size: int, max_size: int) -> np.ndarray:
    sizes = np.unique(np.floor(np.logspace(np.log10(min_size), np.log10(max_size), 8)).astype(int))
    return sizes[sizes >= min_size]


def _corr_dim_gp(ts: Iterable[float], k: int = 10) -> float:
    """Grassberger–Procaccia estimator with 2D embedding."""
    x = np.asarray(list(ts), dtype=float)
    n = len(x)
    if n < 128 or np.allclose(np.std(x), 0.0):
        return 0.0

    # 2D time-delay embedding
    m = 2
    tau = 1
    embedded = np.column_stack([x[i : n - (m - 1) * tau + i] for i in range(0, m * tau, tau)])
    if embedded.shape[0] > 2000:
        idx = np.linspace(0, embedded.shape[0] - 1, 2000).astype(int)
        embedded = embedded[idx]

    diff = embedded[:, None, :] - embedded[None, :, :]
    dist = np.linalg.norm(diff, axis=2)
    dist = dist[np.triu_indices(dist.shape[0], k=1)]
    if dist.size == 0:
        return 0.0

    r_min = np.percentile(dist, 5)
    r_max = np.percentile(dist, 80)
    if r_min <= 0 or r_max <= r_min:
        return 0.0

    radii = np.logspace(np.log10(r_min), np.log10(r_max), k)
    c_vals = np.array([(dist < r).mean() for r in radii])
    valid = c_vals > 0
    if valid.sum() < 2:
        return 0.0

    log_r = np.log(radii[valid])
    log_c = np.log(c_vals[valid])
    slope, _ = np.polyfit(log_r, log_c, 1)
    return float(slope)
