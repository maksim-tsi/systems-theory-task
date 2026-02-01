"""Data loading utilities for FreshRetailNet-50K.

Streaming loader using Hugging Face `datasets` with optional filtering and batching.
Implements an ETL-style pipeline for streaming selection and hourly expansion.
"""
from typing import Iterator, Callable, Dict, Any, Optional, List, Tuple
from pathlib import Path
import math
import pandas as pd

try:
    import datasets
except Exception:  # pragma: no cover - tests will mock or runtime will raise later
    datasets = None


def stream_fresh_retail(
    repo: str,
    batch_size: int = 1000,
    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    split: str = "train",
) -> Iterator[pd.DataFrame]:
    """Stream dataset from HuggingFace and yield pandas DataFrame batches.

    Args:
        repo: repository identifier, e.g. "Dingdong-Inc/FreshRetailNet-50K".
        batch_size: Number of records per yielded DataFrame.
        filter_fn: Optional predicate to filter records (receives one record dict).
        split: Dataset split to load (default: "train").

    Yields:
        DataFrames of partitioned dataset (minibatches).
    """
    if datasets is None:
        raise RuntimeError("datasets library is required but not available")
    ds_iter = datasets.load_dataset(repo, split=split, streaming=True)
    batch: List[Dict[str, Any]] = []
    for rec in ds_iter:
        if filter_fn and not filter_fn(rec):
            continue
        batch.append(rec)
        if len(batch) >= batch_size:
            yield pd.DataFrame(batch)
            batch = []
    if batch:
        yield pd.DataFrame(batch)


def _normalize_dtypes(
    df: pd.DataFrame,
    sales_col: str = "sales",
    stockout_col: str = "is_stockout",
) -> pd.DataFrame:
    """Normalize dtypes for memory efficiency."""
    out = df.copy()
    if sales_col in out.columns:
        out[sales_col] = out[sales_col].astype("float32")
    if stockout_col in out.columns:
        out[stockout_col] = out[stockout_col].astype("int8")
    return out


def iter_hourly_records(
    ds_iter: Iterator[Dict[str, Any]],
    hours_sale_key: str = "hours_sale",
    hours_stock_status_key: str = "hours_stock_status",
    hour_index_key: str = "hour_index",
    sales_key: str = "sales",
    stockout_key: str = "is_stockout",
) -> Iterator[Dict[str, Any]]:
    """Explode day-level records into hourly records.

    Args:
        ds_iter: Iterator of raw dataset records.
        hours_sale_key: Key for list of hourly sales.
        hours_stock_status_key: Key for list of hourly stock status.
        hour_index_key: Key to store hour index in expanded rows.
        sales_key: Output key for hourly sales.
        stockout_key: Output key for hourly stockout flag.

    Yields:
        Hourly records with normalized fields.
    """
    for rec in ds_iter:
        hours_sale = rec.get(hours_sale_key) or []
        hours_stock_status = rec.get(hours_stock_status_key)
        base = {
            k: v
            for k, v in rec.items()
            if k not in {hours_sale_key, hours_stock_status_key}
        }
        for idx, sale in enumerate(hours_sale):
            row = dict(base)
            row[hour_index_key] = idx
            row[sales_key] = float(sale) if sale is not None else 0.0
            if isinstance(hours_stock_status, list) and idx < len(hours_stock_status):
                # Dataset convention: 0 indicates stockout/censored.
                row[stockout_key] = 1 if hours_stock_status[idx] == 0 else 0
            elif isinstance(rec.get(stockout_key), list):
                stock_list = rec.get(stockout_key)
                row[stockout_key] = int(stock_list[idx]) if idx < len(stock_list) else 0
            elif stockout_key in rec:
                row[stockout_key] = int(bool(rec.get(stockout_key)))
            yield row


def stream_hourly_fresh_retail(
    repo: str,
    batch_size: int = 1000,
    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    split: str = "train",
) -> Iterator[pd.DataFrame]:
    """Stream dataset and yield hourly-expanded DataFrame batches."""
    if datasets is None:
        raise RuntimeError("datasets library is required but not available")
    ds_iter = datasets.load_dataset(repo, split=split, streaming=True)
    batch: List[Dict[str, Any]] = []
    for rec in ds_iter:
        if filter_fn and not filter_fn(rec):
            continue
        for hourly in iter_hourly_records(iter([rec])):
            batch.append(hourly)
            if len(batch) >= batch_size:
                yield _normalize_dtypes(pd.DataFrame(batch))
                batch = []
    if batch:
        yield _normalize_dtypes(pd.DataFrame(batch))


def _safe_list(x: Any) -> List[Any]:
    if isinstance(x, list):
        return x
    return []


def _compute_stats_for_record(rec: Dict[str, Any]) -> Tuple[float, int, int, int]:
    hours_sale = _safe_list(rec.get("hours_sale"))
    hours_stock_status = _safe_list(rec.get("hours_stock_status"))
    total_hours = len(hours_sale)
    total_sales = float(sum(hours_sale)) if hours_sale else 0.0
    nonzero_hours = sum(1 for x in hours_sale if x and x > 0)
    if hours_stock_status:
        stockout_hours = sum(1 for s in hours_stock_status if s == 0)
    else:
        stockout_hours = 1 if rec.get("is_stockout") else 0
    return total_sales, total_hours, nonzero_hours, stockout_hours


def scan_and_select(
    repo: str,
    split: str = "train",
    max_records: int = 10000,
    category_allowlist: Optional[List[str]] = None,
    min_avg_sales: float = 5.0,
    min_stockout_rate: float = 0.05,
    max_stockout_rate: float = 0.2,
    key_fields: Tuple[str, str] = ("store_id", "product_id"),
    category_field: str = "category",
) -> Dict[str, Any]:
    """Scan streaming dataset and select a "golden sample" key via heuristic ranking."""
    if datasets is None:
        raise RuntimeError("datasets library is required but not available")
    ds_iter = datasets.load_dataset(repo, split=split, streaming=True)
    stats: Dict[Tuple[Any, Any], Dict[str, Any]] = {}
    seen = 0
    for rec in ds_iter:
        if seen >= max_records:
            break
        seen += 1
        if category_allowlist and rec.get(category_field) not in category_allowlist:
            continue
        key = (rec.get(key_fields[0]), rec.get(key_fields[1]))
        total_sales, total_hours, nonzero_hours, stockout_hours = _compute_stats_for_record(rec)
        if key not in stats:
            stats[key] = {
                "total_sales": 0.0,
                "total_hours": 0,
                "nonzero_hours": 0,
                "stockout_hours": 0,
            }
        stats[key]["total_sales"] += total_sales
        stats[key]["total_hours"] += total_hours
        stats[key]["nonzero_hours"] += nonzero_hours
        stats[key]["stockout_hours"] += stockout_hours

    best_key: Optional[Tuple[Any, Any]] = None
    best_score = -1.0
    for key, s in stats.items():
        total_hours = s["total_hours"]
        if total_hours == 0:
            continue
        avg_sales = s["total_sales"] / total_hours
        stockout_rate = s["stockout_hours"] / total_hours
        nonzero_density = s["nonzero_hours"] / total_hours
        if avg_sales < min_avg_sales:
            continue
        if s["stockout_hours"] == 0:
            continue
        if stockout_rate < min_stockout_rate or stockout_rate > max_stockout_rate:
            continue
        score = nonzero_density * math.log1p(s["total_sales"])
        if score > best_score:
            best_score = score
            best_key = key

    if best_key is None:
        raise ValueError("No suitable golden sample found under current criteria")

    return {
        "store_id": best_key[0],
        "product_id": best_key[1],
        "score": best_score,
        "stats": stats[best_key],
    }


def materialize_golden_sample(
    repo: str,
    output_path: Path,
    split: str = "train",
    scan_records: int = 10000,
    batch_size: int = 5000,
    category_allowlist: Optional[List[str]] = None,
    min_avg_sales: float = 5.0,
    min_stockout_rate: float = 0.05,
    max_stockout_rate: float = 0.2,
    max_rows: Optional[int] = None,
) -> Dict[str, Any]:
    """Select a golden sample and materialize hourly data to disk."""
    selection = scan_and_select(
        repo=repo,
        split=split,
        max_records=scan_records,
        category_allowlist=category_allowlist,
        min_avg_sales=min_avg_sales,
        min_stockout_rate=min_stockout_rate,
        max_stockout_rate=max_stockout_rate,
    )
    store_id = selection["store_id"]
    product_id = selection["product_id"]

    def _filter(rec: Dict[str, Any]) -> bool:
        return rec.get("store_id") == store_id and rec.get("product_id") == product_id

    rows: List[pd.DataFrame] = []
    collected = 0
    for batch in stream_hourly_fresh_retail(
        repo=repo,
        batch_size=batch_size,
        filter_fn=_filter,
        split=split,
    ):
        rows.append(batch)
        collected += len(batch)
        if max_rows and collected >= max_rows:
            break

    if not rows:
        raise ValueError("No rows materialized for selected golden sample")

    df = pd.concat(rows, ignore_index=True)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path)
    selection["output_path"] = str(output_path)
    selection["row_count"] = int(len(df))
    return selection


def dataset_requires_auth(repo: str, split: str = "train") -> bool:
    """Check if loading the dataset requires authentication.

    Tries to fetch a single example and inspects raised errors for authentication indicators
    such as HTTP 401 / "Unauthorized".

    Returns:
        True if an authentication issue was detected, False otherwise.
    """
    if datasets is None:
        raise RuntimeError("datasets library is required but not available")
    try:
        ds_iter = datasets.load_dataset(repo, split=split, streaming=True)
        # Try to fetch first example
        next(iter(ds_iter))
    except Exception as e:  # inspect message for auth clues
        msg = str(e)
        if "401" in msg or "Unauthorized" in msg or "Authentication" in msg:
            return True
        return False
    return False
