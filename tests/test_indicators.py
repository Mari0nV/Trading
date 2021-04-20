from trading.indicators.indicators import (
    bollinger,
    macd,
    mma,
    mme
)

import pandas as pd
import math
import pytest
import random

@pytest.mark.parametrize("nb, values, mma_column", [
    (1, [0.2], [0.2]),
    (1, [0.2, 0.3, 0.4], [0.2, 0.3, 0.4]),
    (2, [0.2, 0.3, 0.4], [None, 0.25, 0.35]),
    (3, [0.2, 0.3, 0.4], [None, None, 0.3]),
    (4, [0.2, 0.3, 0.4], [None, None, None]),
    (20, [
        90.70, 92.90, 92.98, 91.80, 92.66, 92.68, 92.30, 92.77, 92.54, 92.95, 93.20,
        91.07, 89.83, 89.74, 90.40, 90.74, 88.02, 88.09, 88.84, 90.78, 90.54, 91.39, 90.65
        ], [
            None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, 91.25, 91.24, 91.17, 91.05
        ])
])
def test_that_mma_is_computed(nb, values, mma_column):
    df = pd.DataFrame(values, columns=["high"])
    df = mma(df, nb)
    for i in range(len(mma_column)):
        if not mma_column[i]:
            assert not df[f"MMA{nb}"][i]
        else:
            assert round(df[f"MMA{nb}"][i], 2) == mma_column[i]

@pytest.mark.parametrize("nb, alpha, values, mme_column", [
    (1, 0.5, [0.2], [0.2]),
    (1, 0.5, [0.2, 0.3, 0.4], [0.2, 0.3, 0.4]),
    (2, 0.5, [0.2, 0.3, 0.4], [None, 4/15, 11/30]),
    (3, 0.5, [0.2, 0.3, 0.4], [None, None, 12/35]),
    (3, 0.2, [0.2, 0.3, 0.4], [None, None, 96/305]),
    (3, 0, [0.2, 0.3, 0.4], [None, None, 0.3]),  # alpha = 0 -> same as MMA
    (3, 1, [0.2, 0.3, 0.4], [None, None, 0.4]),  # alpha = 1 -> only current value taken into account
    (4, 0.5, [0.2, 0.3, 0.4], [None, None, None]),
])
def test_that_mme_is_computed(nb, alpha, values, mme_column):
    df = pd.DataFrame(values, columns=["high"])
    df = mme(df, nb, alpha=alpha)
    for i in range(len(mme_column)):
        if not mme_column[i]:
            assert not df[f"MME{nb}-{alpha}"][i]
        else:
            assert math.isclose(mme_column[i], df[f"MME{nb}-{alpha}"][i])


def test_that_macd_is_computed():
    values = [random.uniform(0, 1) for _ in range(100)]
    df = pd.DataFrame(values, columns=["high"])
    df = macd(df)
    
    assert set(df.columns) == set([
        'high', 'MME12-0.15', 'MME26-0.07', 'MACD(12,26)', 'MACD_signal(12,26)',
        'MACD_histo(12,26)'
        ])
    assert df[:26]['MACD(12,26)'].isnull().sum() == 25
    assert df[:34]['MACD_signal(12,26)'].isnull().sum() == 33
    assert df[:34]['MACD_histo(12,26)'].isnull().sum() == 33
    assert df[26:]['MACD(12,26)'].isnull().sum() == 0
    assert df[34:]['MACD_signal(12,26)'].isnull().sum() == 0
    assert df[34:]['MACD_histo(12,26)'].isnull().sum() == 0


def test_that_bollinger_is_computed():
    values = [
        90.70, 92.90, 92.98, 91.80, 92.66, 92.68, 92.30, 92.77, 92.54, 92.95, 93.20,
        91.07, 89.83, 89.74, 90.40, 90.74, 88.02, 88.09, 88.84, 90.78, 90.54, 91.39, 90.65
    ]
    mma = [
        88.71, 89.05, 89.24, 89.39, 89.51, 89.69, 89.75, 89.91, 90.08, 90.38, 90.66, 90.86, 90.88,
        90.91, 90.99, 91.15, 91.19, 91.12, 91.17, 91.25, 91.24, 91.17, 91.05
    ]
    upper_band = [None] * 19 + [94.53, 94.53, 94.37, 94.15]
    lower_band = [None] * 19 + [87.97, 87.95, 87.96, 87.95]
    df = pd.DataFrame(values, columns=["high"])
    df["MMA20"] = mma
    df = bollinger(df)

    for i in range(len(upper_band)):
        if not upper_band[i]:
            assert df["Bollinger20_lower"][i] != df["Bollinger20_lower"][i]  # method to check for NaN values
            assert df["Bollinger20_upper"][i] != df["Bollinger20_upper"][i]  # method to check for NaN values
        else:
            assert math.isclose(upper_band[i], df["Bollinger20_upper"][i], rel_tol=0.0001)
            assert math.isclose(lower_band[i], df["Bollinger20_lower"][i], rel_tol=0.0001)
