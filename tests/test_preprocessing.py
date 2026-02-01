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
