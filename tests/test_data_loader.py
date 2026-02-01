import pytest
import pandas as pd
from src import data_loader


class DummyDataset:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def to_pandas(self) -> pd.DataFrame:
        return self._df

    def __len__(self) -> int:
        return len(self._df)


def test_load_full_dataset_uses_non_streaming(monkeypatch):
    df = pd.DataFrame({"a": [1, 2, 3]})

    def fake_load_dataset(repo, split=None, streaming=False):
        assert streaming is False
        return DummyDataset(df)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)

    result = data_loader.load_full_dataset("Dingdong-Inc/FreshRetailNet-50K", split="train")
    assert isinstance(result, pd.DataFrame)
    assert result.equals(df)


def test_find_golden_sample_vectorized_picks_high_volume(monkeypatch):
    rows = []
    for i in range(61):
        rows.append(
            {
                "store_id": "s1",
                "product_id": "p1",
                "dt": f"2024-01-{(i % 28) + 1:02d}",
                "hours_sale": [10] * 24,
                "hours_stock_status": [1] * 20 + [0] * 4,
            }
        )
        rows.append(
            {
                "store_id": "s1",
                "product_id": "p2",
                "dt": f"2024-01-{(i % 28) + 1:02d}",
                "hours_sale": [1] * 24,
                "hours_stock_status": [1] * 20 + [0] * 4,
            }
        )

    df = pd.DataFrame(rows)
    store_id, product_id = data_loader.find_golden_sample_vectorized(df)
    assert store_id == "s1"
    assert product_id == "p1"


def test_explode_and_save_writes_parquet(tmp_path):
    rows = [
        {
            "store_id": "s1",
            "product_id": "p1",
            "dt": "2024-01-01",
            "hours_sale": [1] * 24,
            "hours_stock_status": [1] * 23 + [0],
            "discount": 1.0,
            "avg_temperature": 5.0,
        },
        {
            "store_id": "s1",
            "product_id": "p1",
            "dt": "2024-01-02",
            "hours_sale": [2] * 24,
            "hours_stock_status": [1] * 24,
            "discount": 1.0,
            "avg_temperature": 5.0,
        },
    ]
    df = pd.DataFrame(rows)
    output_path = tmp_path / "golden.parquet"

    data_loader.explode_and_save(df, store_id="s1", product_id="p1", output_path=output_path)

    assert output_path.exists()
    flat = pd.read_parquet(output_path)
    assert len(flat) == 48
    assert set(["hour_index", "sales", "is_stockout", "time_step"]).issubset(flat.columns)
