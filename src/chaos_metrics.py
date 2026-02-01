"""Chaos and fractal metrics: Hurst exponent and correlation dimension."""
from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

try:  # Optional dependency
    import nolds  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    nolds = None

try:  # Optional dependency
    from sklearn.linear_model import LinearRegression  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    LinearRegression = None


def hurst_rs(ts: Sequence[float]) -> float:
    """Estimate the Hurst exponent via rescaled range (R/S) analysis.

    Args:
        ts: 1D time series.

    Returns:
        Estimated Hurst exponent.
    """
    details = hurst_rs_details(ts)
    return float(details["H"])


def hurst_rs_details(
    ts: Sequence[float],
    min_window: int = 8,
    num_scales: int = 20,
    use_sklearn: bool = False,
) -> dict[str, float | np.ndarray | bool]:
    """Estimate the Hurst exponent via R/S analysis with diagnostics.

    Args:
        ts: 1D time series.
        min_window: Smallest window size.
        num_scales: Number of log-spaced windows.

    Returns:
        Dict with H, scales_log, rs_log, r2, valid.
    """
    x = np.asarray(ts, dtype=float)
    n = len(x)
    if n < 64 or np.allclose(np.std(x), 0.0):
        return {"H": 0.5, "valid": False}

    max_window = max(min_window + 1, n // 4)
    window_sizes = _logspace_windows(min_window, max_window, num_scales)
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

    if len(rs_values) < 3:
        return {"H": 0.5, "valid": False}

    log_rs = np.log10(rs_values)
    log_w = np.log10(used_windows)
    slope, intercept, r2 = _fit_line(log_w, log_rs, use_sklearn=use_sklearn)
    return {
        "H": float(slope),
        "scales_log": log_w,
        "rs_log": log_rs,
        "r2": float(r2),
        "valid": True,
    }


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
    details = correlation_dimension_details(ts, emb_dim=2, delay=1, num_radii=k)
    return float(details["D2"])


def correlation_dimension_details(
    ts: Sequence[float],
    emb_dim: int = 2,
    delay: int = 1,
    num_radii: int = 15,
    use_sklearn: bool = False,
) -> dict[str, float | np.ndarray | bool]:
    """Estimate correlation dimension with diagnostics.

    Args:
        ts: 1D time series.
        emb_dim: Embedding dimension.
        delay: Time delay.
        num_radii: Number of radii in log-space.

    Returns:
        Dict with D2, radii_log, cr_log, r2, valid.
    """
    x = np.asarray(ts, dtype=float)
    if len(x) < 128 or np.allclose(np.std(x), 0.0):
        return {"D2": 0.0, "valid": False}

    if nolds is not None:
        try:
            d2 = float(nolds.corr_dim(x, emb_dim=emb_dim, rvals=num_radii))
            return {"D2": d2, "valid": True}
        except Exception:
            pass

    return _corr_dim_gp_details(
        x,
        emb_dim=emb_dim,
        delay=delay,
        num_radii=num_radii,
        use_sklearn=use_sklearn,
    )


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


def time_delay_embedding(series: Sequence[float], delay: int, dim: int) -> np.ndarray:
    """Create a time-delay embedding of a series."""
    x = np.asarray(series, dtype=float)
    n = len(x)
    if n < (dim - 1) * delay + 1:
        raise ValueError("Series too short for embedding")
    vectors = []
    for i in range(n - (dim - 1) * delay):
        vectors.append(x[i : i + dim * delay : delay])
    return np.asarray(vectors)


def _logspace_windows(min_size: int, max_size: int, num_scales: int) -> np.ndarray:
    sizes = np.unique(
        np.floor(
            np.logspace(np.log10(min_size), np.log10(max_size), num_scales)
        ).astype(int)
    )
    return sizes[sizes >= min_size]


def _corr_dim_gp_details(
    ts: Iterable[float],
    emb_dim: int,
    delay: int,
    num_radii: int,
    use_sklearn: bool,
    max_points: int = 2000,
) -> dict[str, float | np.ndarray | bool]:
    """Grassberger–Procaccia estimator with diagnostics."""
    x = np.asarray(list(ts), dtype=float)
    n = len(x)
    if n < 128 or np.allclose(np.std(x), 0.0):
        return {"D2": 0.0, "valid": False}

    embedded = time_delay_embedding(x, delay=delay, dim=emb_dim)
    if embedded.shape[0] > max_points:
        idx = np.linspace(0, embedded.shape[0] - 1, max_points).astype(int)
        embedded = embedded[idx]

    from scipy.spatial.distance import pdist

    dists = pdist(embedded, metric="euclidean")
    dists = dists[dists > 0]
    if dists.size == 0:
        return {"D2": 0.0, "valid": False}

    r_min = np.percentile(dists, 5)
    r_max = np.percentile(dists, 80)
    if r_min <= 0 or r_max <= r_min:
        return {"D2": 0.0, "valid": False}

    radii = np.logspace(np.log10(r_min), np.log10(r_max), num_radii)
    c_vals = np.array([(dists < r).mean() for r in radii])
    valid = (c_vals > 0) & (c_vals < 1)
    if valid.sum() < 3:
        return {"D2": 0.0, "valid": False}

    log_r = np.log10(radii[valid])
    log_c = np.log10(c_vals[valid])
    slope, intercept, r2 = _fit_line(log_r, log_c, use_sklearn=use_sklearn)
    return {
        "D2": float(slope),
        "radii_log": log_r,
        "cr_log": log_c,
        "r2": float(r2),
        "valid": True,
    }


def _fit_line(
    x: np.ndarray,
    y: np.ndarray,
    use_sklearn: bool,
) -> tuple[float, float, float]:
    if use_sklearn and LinearRegression is not None:
        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        slope = float(model.coef_[0])
        intercept = float(model.intercept_)
        r2 = float(model.score(x.reshape(-1, 1), y))
        return slope, intercept, r2

    slope, intercept = np.polyfit(x, y, 1)
    r2 = _r2_score(x, y, slope, intercept)
    return float(slope), float(intercept), float(r2)


def _r2_score(x: np.ndarray, y: np.ndarray, slope: float, intercept: float) -> float:
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot == 0:
        return 0.0
    return 1.0 - ss_res / ss_tot
