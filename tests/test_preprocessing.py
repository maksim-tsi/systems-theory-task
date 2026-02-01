import pandas as pd
from src import preprocessing


def test_explode_hours_sale_simple():
    df = pd.DataFrame({"id": [1, 2], "hours_sale": [[1, 2], [3]]})
    out = preprocessing.explode_hours_sale(df, "hours_sale")
    assert out.shape[0] == 3
    assert "hours_sale" in out.columns


def test_impute_stockouts_basic():
    df = pd.DataFrame({"sales": [10, 0, None, 5]})
    out = preprocessing.impute_stockouts(df, "sales")
    assert out["sales"].isnull().sum() == 0
    assert out["sales"].iloc[1] != 0.0 or out["sales"].iloc[2] != 0.0


def test_filter_daytime_hours():
    df = pd.DataFrame({"hour_index": list(range(24)), "sales": range(24)})
    out = preprocessing.filter_daytime_hours(df, "hour_index", start=8, end=22)
    assert out["hour_index"].min() == 8
    assert out["hour_index"].max() == 22
    assert out.shape[0] == 15


def test_aggregate_daily_sales_sum():
    df = pd.DataFrame(
        {
            "dt": [
                "2024-01-01 01:00:00",
                "2024-01-01 02:00:00",
                "2024-01-02 01:00:00",
            ],
            "sales": [1.0, 2.0, 3.0],
        }
    )
    out = preprocessing.aggregate_daily(df, dt_col="dt", value_col="sales", agg="sum")
    assert out.shape[0] == 2
    assert out["sales"].iloc[0] == 3.0
    assert out["sales"].iloc[1] == 3.0
