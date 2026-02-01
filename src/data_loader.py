"""Data loading utilities for FreshRetailNet-50K.

Streaming loader using Hugging Face `datasets`.
Implements an ETL-style pipeline for streaming selection and hourly expansion.
"""
from typing import Iterator, Callable, Dict, Any, Optional, List, Tuple
from pathlib import Path
import math
import pandas as pd
import numpy as np

try:
    import datasets
except Exception:  # pragma: no cover - tests will mock or runtime will raise later
    datasets = None


def stream_hourly_fresh_retail(
    repo: str,
    batch_size: int = 1000,
    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    split: str = "train",
) -> Iterator[pd.DataFrame]:
    """Stream dataset and yield hourly-expanded DataFrame batches."""
    if datasets is None:
        raise RuntimeError("datasets library is required")

    ds_iter = datasets.load_dataset(repo, split=split, streaming=True)

    batch: List[Dict[str, Any]] = []
    for rec in ds_iter:
        if filter_fn and not filter_fn(rec):
            continue

        hours_sale = rec.get("hours_sale") or []
        hours_stock = rec.get("hours_stock_status") or []

        base = {
            "dt": rec.get("dt"),
            "store_id": rec.get("store_id"),
            "product_id": rec.get("product_id"),
            "category_id": rec.get("first_category_id"),
            "price": rec.get("discount", 1.0),
            "temperature": rec.get("avg_temperature", 20.0),
        }

        for hour_idx in range(24):
            row = base.copy()
            row["hour_index"] = hour_idx

            s_val = float(hours_sale[hour_idx]) if hour_idx < len(hours_sale) else 0.0
            st_val = int(hours_stock[hour_idx]) if hour_idx < len(hours_stock) else 1

            row["sales"] = s_val
            row["is_stockout"] = 1 if st_val == 0 else 0

            batch.append(row)

        if len(batch) >= batch_size * 24:
            yield pd.DataFrame(batch)
            batch = []

    if batch:
        yield pd.DataFrame(batch)


def scan_and_select(
    repo: str,
    split: str = "train",
    scan_records: int = 50000,
    min_avg_daily_sales: float = 2.0,
) -> Dict[str, Any]:
    """Heuristic ranking to find the "Golden Sample" (Best SKU)."""
    if datasets is None:
        raise RuntimeError("datasets library missing")

    print(f"Scanning first {scan_records} records for high-velocity items...")
    ds_iter = datasets.load_dataset(repo, split=split, streaming=True)

    candidates: Dict[Tuple[Any, Any], Dict[str, Any]] = {}

    for i, rec in enumerate(ds_iter):
        if i >= scan_records:
            break

        key = (rec.get("store_id"), rec.get("product_id"))

        sales = rec.get("hours_sale") or []
        daily_vol = sum(float(x) for x in sales if x)

        if key not in candidates:
            candidates[key] = {"days": 0, "total_vol": 0.0, "zeros": 0}

        candidates[key]["days"] += 1
        candidates[key]["total_vol"] += daily_vol
        if daily_vol == 0:
            candidates[key]["zeros"] += 1

    best_key: Optional[Tuple[Any, Any]] = None
    best_score = -1.0

    print(f"Analyzed {len(candidates)} unique SKU/Store pairs.")

    for key, stats in candidates.items():
        if stats["days"] < 10:
            continue

        avg_daily = stats["total_vol"] / stats["days"]
        if avg_daily < min_avg_daily_sales:
            continue

        consistency = 1.0 - (stats["zeros"] / stats["days"])
        score = avg_daily * consistency

        if score > best_score:
            best_score = score
            best_key = key

    if not best_key:
        raise ValueError("No suitable golden sample found. Try lowering min_avg_daily_sales.")

    print(f"Winner: Store={best_key[0]}, Product={best_key[1]} (Score={best_score:.2f})")
    return {"store_id": best_key[0], "product_id": best_key[1]}


def materialize_golden_sample(
    output_path: Path,
    repo: str = "Dingdong-Inc/FreshRetailNet-50K",
    scan_depth: int = 50000,
) -> pd.DataFrame:
    """Pipeline: Select best -> Stream filter -> Save Parquet."""
    target = scan_and_select(repo, scan_records=scan_depth)
    s_id, p_id = target["store_id"], target["product_id"]

    def is_target(rec: Dict[str, Any]) -> bool:
        return (rec.get("store_id") == s_id) and (rec.get("product_id") == p_id)

    print(f"Materializing full history for Target {target}...")
    chunks: List[pd.DataFrame] = []
    for df_chunk in stream_hourly_fresh_retail(repo, filter_fn=is_target):
        chunks.append(df_chunk)
        print(f"Collected {len(df_chunk)} hourly records...", end="\r")

    if not chunks:
        raise ValueError("No rows materialized for selected golden sample")

    full_df = pd.concat(chunks).sort_values(["dt", "hour_index"]).reset_index(drop=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    full_df.to_parquet(output_path)
    print(f"\nSuccess! Saved {len(full_df)} rows to {output_path}")
    return full_df
