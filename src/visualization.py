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


def plot_phase_portrait_with_nullclines(
    params: dict,
    i_range: tuple[float, float],
    r_range: tuple[float, float],
    grid_size: int = 15,
    t: np.ndarray | None = None,
    y0: np.ndarray | None = None,
):
    """Phase portrait with nullclines and vector field for (I, R).

    Args:
        params: Model parameters.
        i_range: (min, max) range for inventory axis.
        r_range: (min, max) range for replenishment axis.
        grid_size: Grid resolution for quiver field.
        t: Optional time vector for trajectory.
        y0: Optional initial state [I0, R0].
    """
    import plotly.figure_factory as ff
    import plotly.graph_objects as go

    from src import nonlinear_model

    i_min, i_max = i_range
    r_min, r_max = r_range
    i_vals = np.linspace(i_min, i_max, grid_size)
    r_vals = np.linspace(r_min, r_max, grid_size)
    ii, rr = np.meshgrid(i_vals, r_vals)

    decay = params.get("inventory_decay_rate", 0.01)
    temp_sens = params.get("temperature_sensitivity", 0.0)
    temperature = params.get("temperature", 20.0)
    decay = decay * (1 + temp_sens * (temperature - 20.0))
    demand = params.get("demand", 0.0)
    alpha = params.get("replenishment_gain", 1.0)
    beta = params.get("replenishment_decay", 1.0)
    i_target = params.get("i_target", 1.0)

    d_i = rr - demand - decay * ii
    d_r = alpha * (i_target - ii) - beta * rr

    fig = ff.create_quiver(
        ii.flatten(),
        rr.flatten(),
        d_i.flatten(),
        d_r.flatten(),
        scale=0.25,
        arrow_scale=0.3,
        name="Vector Field",
    )

    nullcline_i, nullcline_r = nonlinear_model.compute_nullclines(params)
    i_line = np.linspace(i_min, i_max, 200)
    r_null_i = nullcline_i(i_line)
    r_null_r = nullcline_r(i_line)
    fig.add_trace(
        go.Scatter(
            x=i_line,
            y=r_null_i,
            mode="lines",
            name="dI/dt = 0",
            line=dict(color="green", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=i_line,
            y=r_null_r,
            mode="lines",
            name="dR/dt = 0",
            line=dict(color="orange", width=2),
        )
    )

    eq = nonlinear_model.compute_equilibrium(params)
    fig.add_trace(
        go.Scatter(
            x=[eq[0]],
            y=[eq[1]],
            mode="markers",
            name="Equilibrium",
            marker=dict(symbol="star", size=12, color="black"),
        )
    )

    if t is None:
        t = np.linspace(0.0, 50.0, 500)
    if y0 is None:
        y0 = np.array(
            [
                params.get("initial_inventory", eq[0]),
                params.get("initial_replenishment", eq[1]),
            ],
            dtype=float,
        )
    traj = nonlinear_model.integrate_inventory_system(y0, t, params)
    fig.add_trace(
        go.Scatter(
            x=traj[:, 0],
            y=traj[:, 1],
            mode="lines",
            name="Trajectory",
            line=dict(color="purple", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[y0[0]],
            y=[y0[1]],
            mode="markers",
            name="Start",
            marker=dict(symbol="circle", size=8, color="purple"),
        )
    )

    fig.update_layout(
        title="Phase Portrait with Nullclines",
        xaxis_title="Inventory I",
        yaxis_title="Replenishment R",
        template="plotly_white",
        width=700,
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


def plot_dimension_saturation(m_values: list[int], d2_values: list[float]):
    """Plot correlation dimension saturation vs embedding dimension."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=m_values,
            y=d2_values,
            mode="lines+markers",
            name="D2(m)",
            line=dict(color="blue"),
        )
    )
    max_m = max(m_values) if m_values else 1
    fig.add_trace(
        go.Scatter(
            x=[1, max_m],
            y=[1, max_m],
            mode="lines",
            name="Noise baseline y=x",
            line=dict(color="gray", dash="dash"),
        )
    )
    fig.update_layout(
        title="Correlation Dimension Saturation",
        xaxis_title="Embedding Dimension (m)",
        yaxis_title="Correlation Dimension (D2)",
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
