"""Preprocessing utilities: explode nested lists, impute stockouts, smoothing.

Functions are small, typed, and follow Google-style docstrings for maintainability.
"""
from typing import List
import pandas as pd
import numpy as np


def explode_hours_sale(df: pd.DataFrame, hours_col: str = "hours_sale") -> pd.DataFrame:
    """Explode a column of lists (`hours_sale`) into hourly rows.

    Args:
        df: Input dataframe with a column of lists (one list per row).
        hours_col: Column name containing the list to explode.

    Returns:
        Expanded DataFrame with one row per hour.
    """
    if hours_col not in df.columns:
        raise KeyError(f"Column {hours_col} not found in DataFrame")
    # Convert to lists if None
    df = df.copy()
    df[hours_col] = df[hours_col].apply(lambda x: x or [])
    exploded = df.explode(hours_col).reset_index(drop=True)
    return exploded


def impute_stockouts(df: pd.DataFrame, value_col: str = "sales") -> pd.DataFrame:
    """Impute zeros or stockouts intelligently using forward-fill and linear interpolation.

    Args:
        df: Time-indexed DataFrame with `sales` column.
        value_col: Column to impute.

    Returns:
        DataFrame with imputed `sales` values.
    """
    out = df.copy()
    if value_col not in out.columns:
        raise KeyError(f"Column {value_col} not found in DataFrame")
    out[value_col] = out[value_col].replace(0, np.nan)
    out[value_col] = out[value_col].interpolate(method="linear").ffill().fillna(0)
    return out


def filter_daytime_hours(
    df: pd.DataFrame,
    hour_col: str = "hour_index",
    start: int = 8,
    end: int = 22,
) -> pd.DataFrame:
    """Filter rows to a daytime hour window (inclusive).

    Args:
        df: DataFrame with an hour column.
        hour_col: Column containing hour indices 0-23.
        start: Starting hour (inclusive).
        end: Ending hour (inclusive).

    Returns:
        Filtered DataFrame.
    """
    if hour_col not in df.columns:
        raise KeyError(f"Column {hour_col} not found in DataFrame")
    if start > end:
        raise ValueError("start hour must be <= end hour")
    out = df.copy()
    mask = (out[hour_col] >= start) & (out[hour_col] <= end)
    return out.loc[mask].reset_index(drop=True)


def aggregate_daily(
    df: pd.DataFrame,
    dt_col: str = "dt",
    value_col: str = "sales",
    agg: str = "sum",
) -> pd.DataFrame:
    """Aggregate a time series to daily resolution.

    Args:
        df: DataFrame with a datetime column.
        dt_col: Name of the datetime column.
        value_col: Column to aggregate.
        agg: Aggregation method ("sum" or "mean").

    Returns:
        DataFrame with daily aggregated values and a normalized dt column.
    """
    if dt_col not in df.columns:
        raise KeyError(f"Column {dt_col} not found in DataFrame")
    if value_col not in df.columns:
        raise KeyError(f"Column {value_col} not found in DataFrame")
    if agg not in {"sum", "mean"}:
        raise ValueError("agg must be 'sum' or 'mean'")

    out = df.copy()
    out[dt_col] = pd.to_datetime(out[dt_col])
    out[dt_col] = out[dt_col].dt.normalize()
    grouped = out.groupby(dt_col, as_index=False)[value_col]
    if agg == "sum":
        return grouped.sum()
    return grouped.mean()
