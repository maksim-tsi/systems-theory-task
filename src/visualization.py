"""Plotting utilities using Plotly for time series visualizations.

Functions save plots to files and return the filepath for downstream use.
"""
from pathlib import Path
import pandas as pd


def plot_time_series(df: pd.DataFrame, x: str, y: str, out_path: str) -> str:
    """Create and save a simple time-series plot (Plotly).

    Args:
        df: DataFrame with data to plot.
        x: x-axis column name.
        y: y-axis column name.
        out_path: file path to save HTML plot.

    Returns:
        The output path (str).
    """
    try:
        import plotly.express as px
    except Exception:
        # If plotly not available, just touch the file and return path
        Path(out_path).write_text("plot placeholder")
        return out_path
    fig = px.line(df, x=x, y=y, title=f"{y} over {x}")
    fig.write_html(out_path)
    return out_path
