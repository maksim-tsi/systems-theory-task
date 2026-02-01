"""Generate Task 3 HTML report for chaos metrics."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import report_generator


def main() -> None:
    data_path = Path("data/golden_sample.parquet")
    output_path = Path("docs/reports/task3_chaos_report.html")
    report_generator.generate_task3_report(data_path=data_path, output_path=output_path)
    print(f"Saved report to {output_path}")


if __name__ == "__main__":
    main()
