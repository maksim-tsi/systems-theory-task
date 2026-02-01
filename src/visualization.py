"""Plotting utilities using Plotly for time series and chaos diagnostics."""
from pathlib import Path

import numpy as np
import pandas as pd


def plot_time_series(df: pd.DataFrame, x: str, y: str, out_path: str) -> str:
    """Create and save a simple time-series plot (Plotly)."""
    fig = _safe_line_plot(df, x=x, y=y, title=f"{y} over {x}")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(out_path)
    return out_path


def plot_time_series_with_stockouts(
    df: pd.DataFrame,
    time_col: str,
    sales_col: str,
    stockout_col: str,
):
    """Plot sales time series with stockout markers."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[time_col],
            y=df[sales_col],
            name="Sales",
            line=dict(color="blue", width=1),
        )
    )
    if stockout_col in df.columns:
        stockouts = df[df[stockout_col] == 1]
        fig.add_trace(
            go.Scatter(
                x=stockouts[time_col],
                y=stockouts[sales_col],
                mode="markers",
                name="Stockout",
                marker=dict(color="red", size=4),
            )
        )
    fig.update_layout(title="Sales with Stockouts", template="plotly_white")
    return fig


def plot_phase_portrait(series: np.ndarray, delay: int = 1):
    """2D phase portrait x(t) vs x(t+tau)."""
    import plotly.graph_objects as go

    if delay <= 0 or delay >= len(series):
        raise ValueError("delay must be in [1, len(series)-1]")
    x = series[:-delay]
    y = series[delay:]
    fig = go.Figure(
        data=go.Scatter(x=x, y=y, mode="lines", line=dict(width=0.5, color="purple"), opacity=0.7)
    )
    fig.update_layout(
        title=f"Phase Space Reconstruction (delay={delay})",
        xaxis_title="x(t)",
        yaxis_title=f"x(t+{delay})",
        template="plotly_white",
        width=600,
        height=600,
    )
    return fig


def plot_hurst_fit(metrics: dict):
    """Log-log plot for R/S analysis."""
    import plotly.graph_objects as go

    log_n = metrics.get("scales_log")
    log_rs = metrics.get("rs_log")
    h = metrics.get("H")
    fig = go.Figure()
    if log_n is not None and log_rs is not None:
        fig.add_trace(go.Scatter(x=log_n, y=log_rs, mode="markers", name="R/S Data"))
        line_y = log_rs[0] + h * (log_n - log_n[0])
        fig.add_trace(go.Scatter(x=log_n, y=line_y, mode="lines", name=f"Fit (H={h:.3f})"))
    fig.update_layout(
        title=f"Hurst Exponent (H={h:.3f})",
        xaxis_title="log(n)",
        yaxis_title="log(R/S)",
        template="plotly_white",
    )
    return fig


def plot_correlation_dim(metrics: dict):
    """Log-log plot for correlation dimension."""
    import plotly.graph_objects as go

    log_r = metrics.get("radii_log")
    log_c = metrics.get("cr_log")
    d2 = metrics.get("D2")
    fig = go.Figure()
    if log_r is not None and log_c is not None:
        fig.add_trace(go.Scatter(x=log_r, y=log_c, mode="markers", name="C(r)"))
        line_y = log_c[0] + d2 * (log_r - log_r[0])
        fig.add_trace(go.Scatter(x=log_r, y=line_y, mode="lines", name=f"Fit (D2={d2:.3f})"))
    fig.update_layout(
        title=f"Correlation Dimension (D2={d2:.3f})",
        xaxis_title="log(r)",
        yaxis_title="log(C(r))",
        template="plotly_white",
    )
    return fig


def _safe_line_plot(df: pd.DataFrame, x: str, y: str, title: str):
    try:
        import plotly.express as px
    except Exception:
        import plotly.graph_objects as go

        return go.Figure()
    return px.line(df, x=x, y=y, title=title)
