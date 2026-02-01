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
