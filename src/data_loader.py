"""Data loading utilities for FreshRetailNet-50K.

Streaming loader using Hugging Face `datasets` with optional filtering and batching.
"""
from typing import Iterator, Callable, Dict, Any, Optional, List
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
