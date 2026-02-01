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
