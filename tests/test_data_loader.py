import pytest
import pandas as pd
from src import data_loader


def test_stream_fresh_retail_yields_dataframe():
    gen = data_loader.stream_fresh_retail("Dingdong-Inc/FreshRetailNet-50K")
    df = next(gen)
    assert isinstance(df, pd.DataFrame)
    # Expect empty frame in placeholder stub
    assert df.shape[0] == 0
