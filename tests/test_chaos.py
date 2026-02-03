import numpy as np
import pandas as pd

from src import chaos_metrics
from src import chaos_analysis
from src import report_generator


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


def test_hurst_rs_details_valid():
    rng = np.random.default_rng(5)
    ts = rng.normal(size=2048)
    details = chaos_metrics.hurst_rs_details(ts)
    assert "H" in details
    assert details.get("valid") is True


def test_correlation_dimension_details_valid():
    rng = np.random.default_rng(6)
    ts = rng.normal(size=1500)
    details = chaos_metrics.correlation_dimension_details(ts, emb_dim=2, delay=1, num_radii=10)
    assert "D2" in details
    assert details.get("valid") is True


def test_correlation_dimension_scan_returns_m_d2():
    rng = np.random.default_rng(11)
    ts = rng.normal(size=1500)
    scan = chaos_metrics.correlation_dimension_scan(ts)
    assert set(scan.keys()) == {"m", "d2"}
    assert scan["m"] == [2, 3, 4, 5, 6]
    assert len(scan["d2"]) == 5
    assert all(np.isfinite(v) for v in scan["d2"])


def test_hurst_rs_details_sklearn_if_available():
    rng = np.random.default_rng(12)
    ts = rng.normal(size=2048)
    try:
        import sklearn  # noqa: F401
    except Exception:
        return
    details = chaos_metrics.hurst_rs_details(ts, use_sklearn=True)
    assert details.get("valid") is True


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


def test_generate_task3_report_writes_html(tmp_path, monkeypatch):
    df = pd.DataFrame(
        {
            "dt": pd.date_range("2024-01-01", periods=48, freq="H"),
            "hour_index": [i % 24 for i in range(48)],
            "sales": np.random.default_rng(1).normal(size=48),
            "is_stockout": [0] * 48,
        }
    )

    def _fake_read_parquet(_path):
        return df

    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)
    output_path = tmp_path / "task3.html"
    report_generator.generate_task3_report(
        data_path=tmp_path / "golden_sample.parquet",
        output_path=output_path,
    )
    assert output_path.exists()
