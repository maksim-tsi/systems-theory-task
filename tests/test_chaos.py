from src import chaos_metrics


def test_hurst_rs_stub():
    h = chaos_metrics.hurst_rs([1, 2, 3, 4, 5, 6, 7, 8])
    assert isinstance(h, float)


def test_correlation_dimension_returns_float():
    d = chaos_metrics.correlation_dimension(list(range(200)), k=10)
    assert isinstance(d, float)
