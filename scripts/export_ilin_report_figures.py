"""Export static figures for the Ilin Systems Theory PDF report.

This script creates PDF/PNG assets that can be embedded into a LaTeX/Pandoc
pipeline reliably.

Outputs:
- docs/reports/figures/ilin_structural_diagram.(pdf|png)
- docs/reports/figures/task3_*.png

Run:
  conda activate tsi
  python scripts/export_ilin_report_figures.py
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src import chaos_metrics, preprocessing, visualization

FIG_DIR = ROOT / "docs" / "reports" / "figures"
TMP_DIR = ROOT / "docs" / "reports" / "tmp"
DATA_PATH = ROOT / "data" / "golden_sample.parquet"


def export_structural_diagram() -> None:
    """Convert the draw.io structural diagram SVG into PDF and PNG."""
    svg_path = TMP_DIR / "ilin_st_structural_diagram.drawio.svg"
    if not svg_path.exists():
        raise FileNotFoundError(f"Structural diagram SVG not found: {svg_path}")

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out_pdf = FIG_DIR / "ilin_structural_diagram.pdf"
    out_png = FIG_DIR / "ilin_structural_diagram.png"

    # Prefer librsvg CLI conversion for draw.io SVGs (more robust than cairosvg).
    try:
        import subprocess

        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(out_pdf), str(svg_path)],
            check=True,
        )
        subprocess.run(
            [
                "rsvg-convert",
                "-f",
                "png",
                "--dpi-x",
                "300",
                "--dpi-y",
                "300",
                "-o",
                str(out_png),
                str(svg_path),
            ],
            check=True,
        )
        return
    except Exception:
        # Fallback to cairosvg if rsvg-convert is unavailable.
        pass

    try:
        import cairosvg  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Failed to convert structural diagram via rsvg-convert, and cairosvg is unavailable. "
            "Install librsvg (brew install librsvg) or install cairosvg + cairo."
        ) from exc

    cairosvg.svg2pdf(url=str(svg_path), write_to=str(out_pdf))
    cairosvg.svg2png(url=str(svg_path), write_to=str(out_png), dpi=300)


def export_task3_figures(start_hour: int = 8, end_hour: int = 22) -> None:
    """Export Task 3 plots as static PNGs using Plotly+kaleido."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Golden sample parquet not found: {DATA_PATH}. "
            "Run: python src/data_loader.py"
        )

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_PATH)
    if "dt" not in df.columns:
        raise KeyError("dt column is required in golden sample")
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    if "hour_index" not in df.columns:
        df["hour_index"] = df["dt"].dt.hour

    df_day = preprocessing.filter_daytime_hours(df, "hour_index", start=start_hour, end=end_hour)
    hourly_series = df_day["sales"].to_numpy()

    hurst_res = chaos_metrics.hurst_rs_details(hourly_series)
    d2_res = chaos_metrics.correlation_dimension_details(hourly_series)

    fig_ts = visualization.plot_time_series_with_stockouts(
        df_day, time_col="dt", sales_col="sales", stockout_col="is_stockout"
    )
    fig_phase = visualization.plot_phase_portrait(hourly_series, delay=1)
    fig_hurst = visualization.plot_hurst_fit(hurst_res) if hurst_res.get("valid") else None
    fig_d2 = visualization.plot_correlation_dim(d2_res) if d2_res.get("valid") else None

    # Plotly static export uses kaleido.
    fig_ts.write_image(FIG_DIR / "task3_time_series.png", scale=2)
    fig_phase.write_image(FIG_DIR / "task3_phase_portrait.png", scale=2)

    if fig_hurst is not None:
        fig_hurst.write_image(FIG_DIR / "task3_hurst_rs.png", scale=2)

    if fig_d2 is not None:
        fig_d2.write_image(FIG_DIR / "task3_correlation_dimension.png", scale=2)


def main() -> None:
    export_structural_diagram()
    export_task3_figures()
    print(f"Saved figures under: {FIG_DIR}")


if __name__ == "__main__":
    main()
