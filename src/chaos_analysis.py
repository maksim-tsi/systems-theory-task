"""Run chaos metrics on the golden sample time series."""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import chaos_metrics, preprocessing


def analyze_golden_sample(
    data_path: Path,
    start_hour: int = 8,
    end_hour: int = 22,
) -> dict[str, Any]:
    """Compute chaos metrics for daytime and daily aggregated series.

    Args:
        data_path: Path to data/golden_sample.parquet.
        start_hour: Daytime window start (inclusive).
        end_hour: Daytime window end (inclusive).

    Returns:
        Dictionary with metrics and series lengths.
    """
    df = pd.read_parquet(data_path)
    if "sales" not in df.columns:
        raise KeyError("sales column is required")
    if "hour_index" not in df.columns:
        if "dt" not in df.columns:
            raise KeyError("hour_index or dt column is required")
        df = df.copy()
        df["dt"] = pd.to_datetime(df["dt"])
        df["hour_index"] = df["dt"].dt.hour

    df_day = preprocessing.filter_daytime_hours(df, "hour_index", start=start_hour, end=end_hour)
    hourly_series = df_day["sales"].to_numpy()

    daily = preprocessing.aggregate_daily(df_day, dt_col="dt", value_col="sales", agg="sum")
    daily_series = daily["sales"].to_numpy()

    return {
        "daytime_hourly": chaos_metrics.compute_chaos_metrics(hourly_series),
        "daytime_daily": chaos_metrics.compute_chaos_metrics(daily_series),
        "n_hourly": int(len(hourly_series)),
        "n_daily": int(len(daily_series)),
        "start_hour": int(start_hour),
        "end_hour": int(end_hour),
    }


def save_analysis(analysis: dict[str, Any], output_path: Path) -> None:
    """Persist analysis output as a text artifact."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chaos Metrics Analysis (Golden Sample)",
        f"Daytime window: {analysis['start_hour']:02d}:00-{analysis['end_hour']:02d}:00",
        f"Hourly samples: {analysis['n_hourly']}",
        f"Daily samples: {analysis['n_daily']}",
        "",
        "Daytime hourly metrics:",
        f"  Hurst (R/S): {analysis['daytime_hourly']['hurst']:.4f}",
        f"  Correlation dimension D2: {analysis['daytime_hourly']['d2']:.4f}",
        "",
        "Daytime daily metrics:",
        f"  Hurst (R/S): {analysis['daytime_daily']['hurst']:.4f}",
        f"  Correlation dimension D2: {analysis['daytime_daily']['d2']:.4f}",
    ]
    output_path.write_text("\n".join(lines))


def main() -> None:
    data_path = Path("data/golden_sample.parquet")
    artifact_path = Path("docs/reports/artifacts/2026-02-01/chaos_metrics_analysis.txt")
    analysis = analyze_golden_sample(data_path)
    save_analysis(analysis, artifact_path)
    print(f"Saved analysis to {artifact_path}")


if __name__ == "__main__":
    main()
