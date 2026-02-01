"""Data loading utilities for FreshRetailNet-50K.

Loads the full dataset into memory, selects optimal time series with progress tracking,
and saves the result to Parquet.
"""
import sys
from pathlib import Path
from typing import Tuple, Optional, cast
import pandas as pd
import numpy as np
from tqdm import tqdm

try:
    import datasets
except ImportError:
    datasets = None

# Register tqdm for pandas (df.progress_apply)
tqdm.pandas()

def load_full_dataset(
    repo: str = "Dingdong-Inc/FreshRetailNet-50K",
    split: str = "train"
) -> pd.DataFrame:
    """Download and load the full dataset into Pandas with logging."""
    if datasets is None:
        raise RuntimeError("The 'datasets' library is required. Install via `pip install datasets`.")
    
    print(f"\n[1/4] Downloading dataset '{repo}' (split='{split}')...")
    try:
        # Load fully into memory (no streaming)
        ds = datasets.load_dataset(repo, split=split, streaming=False)
        print(f"      Dataset loaded via HuggingFace. Rows: {len(ds)}")
    except Exception as e:
        print(f"      CRITICAL ERROR downloading dataset: {e}")
        raise

    print(f"[2/4] Converting Arrow table to Pandas DataFrame...")
    if hasattr(datasets, "IterableDataset") and isinstance(ds, datasets.IterableDataset):
        raise RuntimeError("Streaming dataset detected. Set streaming=False to load fully.")

    df = cast(pd.DataFrame, ds.to_pandas())
    
    if df.empty:
        raise ValueError("Downloaded dataset is empty!")
        
    print(f"      Conversion complete. DataFrame shape: {df.shape}")
    print(f"      Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    return df

def find_golden_sample_vectorized(df: pd.DataFrame) -> Tuple[int | str, int | str]:
    """Find the best (Store, Product) pair using vectorized operations."""
    print(f"\n[3/4] Analyzing dataset to find 'Golden Sample' (Best SKU)...")
    
    # 1. Calculate stats per row using progress_apply
    print("      Calculating daily volumes and stockouts (this may take a moment)...")
    
    # Check if columns exist
    if 'hours_sale' not in df.columns or 'hours_stock_status' not in df.columns:
        raise KeyError(f"Missing required columns. Found: {df.columns.tolist()}")

    # Summing arrays in cells. progress_apply gives us a bar.
    # Note: Using numpy directly on list columns is tricky, pandas apply is safer here.
    df['daily_vol'] = df['hours_sale'].progress_apply(np.sum)
    df['daily_stockouts'] = df['hours_stock_status'].progress_apply(
        lambda x: np.sum(1 - np.array(x)) if isinstance(x, (list, np.ndarray)) else 0
    )
    
    print("      Grouping by (store_id, product_id)...")
    # 2. Group by (Store, Product) to get full history stats
    stats = df.groupby(['store_id', 'product_id']).agg({
        'daily_vol': 'mean',          # Avg daily sales
        'daily_stockouts': 'sum',     # Total stockout hours
        'dt': 'count'                 # Days of history
    }).rename(columns={'dt': 'days'})
    
    print(f"      Unique Time Series found: {len(stats)}")

    # 3. Filter candidates
    # Must have at least 60 days of history
    stats = stats[stats['days'] > 60]
    print(f"      Candidates > 60 days: {len(stats)}")
    
    # Must have some stockouts (for nonlinear dynamics) but not be always empty
    # Filter: At least 5 hours of stockout total, but less than 10 hours per day avg (avoid discontinued items)
    stats = stats[(stats['daily_stockouts'] > 5) & (stats['daily_stockouts'] < stats['days'] * 10)]
    print(f"      Candidates with valid stockout dynamics: {len(stats)}")
    
    # 4. Score = Volume
    if stats.empty:
        raise ValueError("No suitable candidates found after filtering!")
        
    best_idx = stats['daily_vol'].idxmax()
    if not isinstance(best_idx, tuple) or len(best_idx) != 2:
        raise ValueError("Expected MultiIndex (store_id, product_id) from grouping.")
    best_store, best_product = cast(Tuple[int | str, int | str], best_idx)
    
    metrics = stats.loc[best_idx]
    if not isinstance(metrics, pd.Series):
        raise ValueError("Expected a single row of metrics for best index.")

    avg_daily_sales = float(metrics["daily_vol"])
    days = int(metrics["days"])
    total_stockouts = int(metrics["daily_stockouts"])

    print(f"      WINNER FOUND: Store={best_store}, Product={best_product}")
    print(
        f"      Stats: Avg Daily Sales={avg_daily_sales:.2f}, "
        f"Days={days}, Total Stockout Hours={total_stockouts}"
    )
    
    return best_store, best_product

def explode_and_save(
    df: pd.DataFrame,
    store_id: int | str,
    product_id: int | str,
    output_path: Path
):
    """Filter for specific item, explode hourly data, and save."""
    print(f"\n[4/4] Processing and Saving...")
    
    # Filter
    subset = df[(df['store_id'] == store_id) & (df['product_id'] == product_id)].copy()
    subset = subset.sort_values('dt')
    print(f"      Filtered subset rows (days): {len(subset)}")
    
    records = []
    # Using tqdm to show progress of the explosion loop
    iterator = tqdm(subset.iterrows(), total=len(subset), desc="      Exploding hourly data")
    
    for _, row in iterator:
        base = {
            "dt": row['dt'],
            "price": row.get('discount', 1.0),
            "temp": row.get('avg_temperature', 0.0)
        }
        sales = row['hours_sale']
        stock = row['hours_stock_status']
        
        # Ensure lists are length 24
        if len(sales) != 24 or len(stock) != 24:
            continue

        for h in range(24):
            r = base.copy()
            r['hour_index'] = h
            r['sales'] = float(sales[h])
            # 0 = Stockout, 1 = Available. Invert for "is_stockout" flag (1=True)
            r['is_stockout'] = 1 if stock[h] == 0 else 0
            records.append(r)
            
    flat_df = pd.DataFrame(records)
    
    # Create sequential integer index for simplified ODE modeling later
    flat_df['time_step'] = range(len(flat_df))
    
    # Create output directory
    output_path = Path(output_path)
    if not output_path.parent.exists():
        print(f"      Creating directory: {output_path.parent.resolve()}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
    flat_df.to_parquet(output_path)
    print(f"\nSUCCESS! Data saved to: {output_path.resolve()}")
    print(f"Total hourly observations: {len(flat_df)}")
    print(f"Preview:\n{flat_df.head(3)}")

def run_pipeline():
    try:
        df = load_full_dataset()
        store_id, prod_id = find_golden_sample_vectorized(df)
        explode_and_save(df, store_id, prod_id, Path("data/golden_sample.parquet"))
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")
    except Exception as e:
        print(f"\nPipeline FAILED: {e}")
        # import traceback; traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()