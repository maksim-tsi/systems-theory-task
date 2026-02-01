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
    assert len(df) == 24
    assert set(df["hour_index"].tolist()) == set(range(24))


def test_scan_and_select_picks_high_score(monkeypatch):
    records = []
    for _ in range(12):
        records.append(
            {
                "store_id": "s1",
                "product_id": "p1",
                "hours_sale": [10, 12, 11, 9],
            }
        )
    for _ in range(12):
        records.append(
            {
                "store_id": "s1",
                "product_id": "p2",
                "hours_sale": [0, 0, 0, 1],
            }
        )

    def fake_load_dataset(repo, split=None, streaming=False):
        return DummyIterable(records)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)

    selection = data_loader.scan_and_select(
        "Dingdong-Inc/FreshRetailNet-50K",
        scan_records=30,
        min_avg_daily_sales=2.0,
    )
    assert selection["store_id"] == "s1"
    assert selection["product_id"] == "p1"


def test_materialize_golden_sample_writes_parquet(monkeypatch, tmp_path):
    records = [
        {
            "store_id": "s1",
            "product_id": "p1",
            "hours_sale": [10, 12],
            "hours_stock_status": [1, 0],
            "dt": "2024-01-01",
        }
    ]

    def fake_load_dataset(repo, split=None, streaming=False):
        return DummyIterable(records)

    monkeypatch.setattr("src.data_loader.datasets.load_dataset", fake_load_dataset)
    output_path = tmp_path / "golden.parquet"

    result = data_loader.materialize_golden_sample(
        output_path=output_path,
        repo="Dingdong-Inc/FreshRetailNet-50K",
        scan_depth=10,
    )

    assert output_path.exists()
    assert len(result) == 24
