"""HTML report generation for Task 3 chaos analysis."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.io as pio

from src import chaos_metrics, preprocessing, visualization


def generate_task3_report(
    data_path: Path,
    output_path: Path,
    start_hour: int = 8,
    end_hour: int = 22,
) -> None:
    """Generate a Task 3 HTML report with chaos metrics and plots.

    Args:
        data_path: Path to golden_sample.parquet.
        output_path: Output HTML report path.
        start_hour: Start of daytime window (inclusive).
        end_hour: End of daytime window (inclusive).
    """
    df = pd.read_parquet(data_path)
    if "dt" not in df.columns:
        raise KeyError("dt column is required")
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df["hour_index"] = df["dt"].dt.hour if "hour_index" not in df.columns else df["hour_index"]

    df_day = preprocessing.filter_daytime_hours(df, "hour_index", start=start_hour, end=end_hour)
    hourly_series = df_day["sales"].to_numpy()
    daily = preprocessing.aggregate_daily(df_day, dt_col="dt", value_col="sales", agg="sum")
    daily_series = daily["sales"].to_numpy()

    hurst_hourly = chaos_metrics.hurst_rs_details(hourly_series)
    d2_hourly = chaos_metrics.correlation_dimension_details(hourly_series)
    hurst_daily = chaos_metrics.hurst_rs_details(daily_series)
    d2_daily = chaos_metrics.correlation_dimension_details(daily_series)

    figs = _build_figures(df_day, hourly_series, hurst_hourly, d2_hourly)
    html = _build_html(
        title="Task 3 — Chaos Metrics Report",
        summary=_summary_block(start_hour, end_hour, hourly_series, daily_series, hurst_hourly, d2_hourly, hurst_daily, d2_daily),
        figures=figs,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


def _summary_block(
    start_hour: int,
    end_hour: int,
    hourly_series,
    daily_series,
    hurst_hourly: Dict,
    d2_hourly: Dict,
    hurst_daily: Dict,
    d2_daily: Dict,
) -> str:
    return """
    <h2>Summary</h2>
    <ul>
      <li>Daytime window: {start:02d}:00–{end:02d}:00</li>
      <li>Hourly samples: {n_hourly}</li>
      <li>Daily samples: {n_daily}</li>
      <li>Hourly Hurst: {h_hourly:.4f} (R²={h_r2:.3f})</li>
      <li>Hourly D2: {d2_hourly:.4f} (R²={d2_r2:.3f})</li>
      <li>Daily Hurst: {h_daily:.4f} (R²={h2_r2:.3f})</li>
      <li>Daily D2: {d2_daily:.4f} (R²={d22_r2:.3f})</li>
    </ul>
    """.format(
        start=start_hour,
        end=end_hour,
        n_hourly=len(hourly_series),
        n_daily=len(daily_series),
        h_hourly=hurst_hourly.get("H", 0.0),
        h_r2=hurst_hourly.get("r2", 0.0),
        d2_hourly=d2_hourly.get("D2", 0.0),
        d2_r2=d2_hourly.get("r2", 0.0),
        h_daily=hurst_daily.get("H", 0.0),
        h2_r2=hurst_daily.get("r2", 0.0),
        d2_daily=d2_daily.get("D2", 0.0),
        d22_r2=d2_daily.get("r2", 0.0),
    )


def _build_figures(df_day, hourly_series, hurst_hourly, d2_hourly):
    figs = {
        "time_series": visualization.plot_time_series_with_stockouts(
            df_day, time_col="dt", sales_col="sales", stockout_col="is_stockout"
        ),
        "phase": visualization.plot_phase_portrait(hourly_series, delay=1),
        "hurst": visualization.plot_hurst_fit(hurst_hourly),
        "d2": visualization.plot_correlation_dim(d2_hourly),
    }
    return figs


def _build_html(title: str, summary: str, figures: Dict[str, object]) -> str:
    fig_html = "\n".join(
        [
            f"<h2>{name.replace('_', ' ').title()}</h2>" + pio.to_html(fig, include_plotlyjs="cdn", full_html=False)
            for name, fig in figures.items()
        ]
    )
    return f"""
    <html>
      <head><meta charset="utf-8"><title>{title}</title></head>
      <body>
        <h1>{title}</h1>
        {summary}
        {fig_html}
      </body>
    </html>
    """
