import numpy as np

from src import chaos_metrics
from src import chaos_analysis


def _ar1(phi: float, n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    eps = rng.normal(size=n)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + eps[i]
    return x


def test_hurst_white_noise_near_half():
    rng = np.random.default_rng(42)
    ts = rng.normal(size=2048)
    h = chaos_metrics.hurst_rs(ts)
    assert 0.35 < h < 0.65


def test_hurst_persistent_gt_half():
    n = 2048
    rng = np.random.default_rng(7)
    trend = np.linspace(0.0, 1.0, n)
    ts = trend + 0.05 * rng.normal(size=n)
    h = chaos_metrics.hurst_rs(ts)
    assert h > 0.55


def test_hurst_antipersistent_lt_half():
    ts = _ar1(phi=-0.7, n=2048, seed=21)
    h = chaos_metrics.hurst_rs(ts)
    assert h < 0.5


def test_correlation_dimension_reasonable_range():
    rng = np.random.default_rng(123)
    ts = rng.normal(size=1500)
    d2 = chaos_metrics.correlation_dimension(ts, k=12)
    assert 0.1 < d2 < 2.0


def test_compute_chaos_metrics_returns_keys():
    rng = np.random.default_rng(9)
    ts = rng.normal(size=1200)
    metrics = chaos_metrics.compute_chaos_metrics(ts)
    assert set(metrics.keys()) == {"hurst", "d2"}
    assert 0.0 <= metrics["d2"] <= 2.0


def test_save_analysis_writes_file(tmp_path):
    analysis = {
        "daytime_hourly": {"hurst": 0.5, "d2": 1.1},
        "daytime_daily": {"hurst": 0.6, "d2": 0.9},
        "n_hourly": 100,
        "n_daily": 10,
        "start_hour": 8,
        "end_hour": 22,
    }
    out_path = tmp_path / "chaos.txt"
    chaos_analysis.save_analysis(analysis, out_path)
    assert out_path.exists()
