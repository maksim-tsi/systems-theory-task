"""Run chaos metrics on the golden sample using scikit-learn fits."""
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
		"daytime_hourly": {
			"hurst": chaos_metrics.hurst_rs_details(hourly_series, use_sklearn=True),
			"d2": chaos_metrics.correlation_dimension_details(hourly_series, use_sklearn=True),
		},
		"daytime_daily": {
			"hurst": chaos_metrics.hurst_rs_details(daily_series, use_sklearn=True),
			"d2": chaos_metrics.correlation_dimension_details(daily_series, use_sklearn=True),
		},
		"n_hourly": int(len(hourly_series)),
		"n_daily": int(len(daily_series)),
		"start_hour": int(start_hour),
		"end_hour": int(end_hour),
	}


def save_analysis(analysis: dict[str, Any], output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	lines = [
		"Chaos Metrics Analysis (Golden Sample, scikit-learn)",
		f"Daytime window: {analysis['start_hour']:02d}:00-{analysis['end_hour']:02d}:00",
		f"Hourly samples: {analysis['n_hourly']}",
		f"Daily samples: {analysis['n_daily']}",
		"",
		"Daytime hourly metrics:",
		f"  Hurst (R/S): {analysis['daytime_hourly']['hurst'].get('H', 0.0):.4f}",
		f"  Hurst R2: {analysis['daytime_hourly']['hurst'].get('r2', 0.0):.4f}",
		f"  Correlation dimension D2: {analysis['daytime_hourly']['d2'].get('D2', 0.0):.4f}",
		f"  D2 R2: {analysis['daytime_hourly']['d2'].get('r2', 0.0):.4f}",
		"",
		"Daytime daily metrics:",
		f"  Hurst (R/S): {analysis['daytime_daily']['hurst'].get('H', 0.0):.4f}",
		f"  Hurst R2: {analysis['daytime_daily']['hurst'].get('r2', 0.0):.4f}",
		f"  Correlation dimension D2: {analysis['daytime_daily']['d2'].get('D2', 0.0):.4f}",
		f"  D2 R2: {analysis['daytime_daily']['d2'].get('r2', 0.0):.4f}",
	]
	output_path.write_text("\n".join(lines))


def _parse_metrics(text: str) -> dict[str, float]:
	out = {}
	for line in text.splitlines():
		if "Hurst (R/S)" in line:
			out.setdefault("hurst", []).append(float(line.split(":")[-1]))
		if "Correlation dimension D2" in line:
			out.setdefault("d2", []).append(float(line.split(":")[-1]))
	return {
		"hurst_hourly": out.get("hurst", [0.0, 0.0])[0],
		"hurst_daily": out.get("hurst", [0.0, 0.0, 0.0])[1],
		"d2_hourly": out.get("d2", [0.0, 0.0])[0],
		"d2_daily": out.get("d2", [0.0, 0.0, 0.0])[1],
	}


def save_comparison(
	baseline_path: Path,
	sklearn_path: Path,
	output_path: Path,
) -> None:
	base_text = baseline_path.read_text()
	skl_text = sklearn_path.read_text()
	base = _parse_metrics(base_text)
	skl = _parse_metrics(skl_text)

	def _delta(key: str) -> float:
		return skl[key] - base[key]

	lines = [
		"Chaos Metrics Comparison (Baseline vs scikit-learn)",
		f"Baseline: {baseline_path}",
		f"Sklearn: {sklearn_path}",
		"",
		f"Hourly Hurst: {base['hurst_hourly']:.4f} -> {skl['hurst_hourly']:.4f} (Δ={_delta('hurst_hourly'):.4f})",
		f"Daily Hurst: {base['hurst_daily']:.4f} -> {skl['hurst_daily']:.4f} (Δ={_delta('hurst_daily'):.4f})",
		f"Hourly D2: {base['d2_hourly']:.4f} -> {skl['d2_hourly']:.4f} (Δ={_delta('d2_hourly'):.4f})",
		f"Daily D2: {base['d2_daily']:.4f} -> {skl['d2_daily']:.4f} (Δ={_delta('d2_daily'):.4f})",
	]
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.write_text("\n".join(lines))


def main() -> None:
	data_path = Path("data/golden_sample.parquet")
	sklearn_path = Path("docs/reports/artifacts/2026-02-01/chaos_metrics_analysis_sklearn.txt")
	baseline_path = Path("docs/reports/artifacts/2026-02-01/chaos_metrics_analysis.txt")
	comparison_path = Path("docs/reports/artifacts/2026-02-01/chaos_metrics_comparison.txt")

	analysis = analyze_golden_sample(data_path)
	save_analysis(analysis, sklearn_path)
	if baseline_path.exists():
		save_comparison(baseline_path, sklearn_path, comparison_path)
	print(f"Saved analysis to {sklearn_path}")
	if comparison_path.exists():
		print(f"Saved comparison to {comparison_path}")


if __name__ == "__main__":
	main()
