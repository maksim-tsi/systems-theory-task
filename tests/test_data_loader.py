import pytest
import pandas as pd
from src import data_loader


class DummyIterable:
    def __init__(self, records):
        self._it = iter(records)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._it)


def test_stream_fresh_retail_chunking_and_filter(monkeypatch):
    records = [
        {"id": 1, "hours_sale": [1, 2], "is_stockout": False, "sales": 10},
        {"id": 2, "hours_sale": [3], "is_stockout": True, "sales": 0},
        {"id": 3, "hours_sale": [4, 5], "is_stockout": False, "sales": 5},
    ]

    def fake_load_dataset(repo, split=None, streaming=False):
        return DummyIterable(records)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)

    gen = data_loader.stream_fresh_retail(
        "Dingdong-Inc/FreshRetailNet-50K",
        batch_size=1,
        filter_fn=lambda r: not r.get("is_stockout", False),
    )
    batches = list(gen)

    assert len(batches) == 2
    assert all(isinstance(b, pd.DataFrame) for b in batches)
    all_ids = [row["id"] for b in batches for row in b.to_dict(orient="records")]
    assert set(all_ids) == {1, 3}


def test_dataset_requires_token_on_auth_error(monkeypatch):
    from requests.exceptions import HTTPError

    def fake_load_dataset(repo, split=None, streaming=False):
        raise HTTPError("401 Client Error: Unauthorized for url")

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)
    assert data_loader.dataset_requires_auth("Dingdong-Inc/FreshRetailNet-50K") is True


def test_dataset_does_not_require_token_on_success(monkeypatch):
    def fake_load_dataset(repo, split=None, streaming=False):
        return iter([{"id": 1}])

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)
    assert data_loader.dataset_requires_auth("Dingdong-Inc/FreshRetailNet-50K") is False


def test_stream_hourly_fresh_retail_explodes_and_types(monkeypatch):
    records = [
        {
            "store_id": "s1",
            "product_id": "p1",
            "hours_sale": [1, 2],
            "hours_stock_status": [1, 0],
        }
    ]

    def fake_load_dataset(repo, split=None, streaming=False):
        return DummyIterable(records)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)

    batches = list(
        data_loader.stream_hourly_fresh_retail(
            "Dingdong-Inc/FreshRetailNet-50K", batch_size=10
        )
    )
    assert len(batches) == 1
    df = batches[0]
    assert len(df) == 2
    assert set(df["hour_index"].tolist()) == {0, 1}
    assert str(df["sales"].dtype) == "float32"
    assert str(df["is_stockout"].dtype) == "int8"


def test_scan_and_select_picks_high_score(monkeypatch):
    records = [
        {
            "store_id": "s1",
            "product_id": "p1",
            "category": "Vegetables",
            "hours_sale": [10, 12, 11, 9],
            "hours_stock_status": [1, 1, 0, 1],
        },
        {
            "store_id": "s1",
            "product_id": "p2",
            "category": "Vegetables",
            "hours_sale": [0, 0, 0, 1],
            "hours_stock_status": [1, 1, 1, 1],
        },
    ]

    def fake_load_dataset(repo, split=None, streaming=False):
        return DummyIterable(records)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)

    selection = data_loader.scan_and_select(
        "Dingdong-Inc/FreshRetailNet-50K",
        max_records=10,
        category_allowlist=["Vegetables"],
        min_avg_sales=5.0,
        min_stockout_rate=0.05,
        max_stockout_rate=0.5,
    )
    assert selection["store_id"] == "s1"
    assert selection["product_id"] == "p1"
    assert selection["score"] > 0


def test_materialize_golden_sample_writes_parquet(monkeypatch, tmp_path):
    records = [
        {
            "store_id": "s1",
            "product_id": "p1",
            "category": "Dairy",
            "hours_sale": [10, 12],
            "hours_stock_status": [1, 0],
        }
    ]

    def fake_load_dataset(repo, split=None, streaming=False):
        return DummyIterable(records)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)
    output_path = tmp_path / "golden.parquet"

    result = data_loader.materialize_golden_sample(
        "Dingdong-Inc/FreshRetailNet-50K",
        output_path=output_path,
        scan_records=10,
        category_allowlist=["Dairy"],
        min_avg_sales=5.0,
        min_stockout_rate=0.05,
        max_stockout_rate=0.9,
    )

    assert output_path.exists()
    assert result["row_count"] == 2
