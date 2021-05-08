from trading.indicators.indicators import (
    bollinger,
    directional_movement,
    macd,
    mma,
    mme,
    parabolic_sar,
    rsi,
    stochastic
)

import json
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
            assert df[f"MMA{nb}"][i] != df[f"MMA{nb}"][i]
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
            assert df[f"MME{nb}-{alpha}"][i] != df[f"MME{nb}-{alpha}"][i]
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


def test_that_stochastic_is_computed():
    values = [
        (127.01, 125.36, None), (127.62, 126.16, None), (126.59, 124.93, None), (127.35, 126.09, None), (128.17, 126.82, None),
        (128.43, 126.48, None), (127.37, 126.03, None), (126.42, 124.83, None), (126.90, 126.39, None), (126.85, 125.72, None),
        (125.65, 124.56, None), (125.72, 124.57, None), (127.16, 125.07, None), (127.72, 126.86, 127.29), (127.69, 126.63, 127.18),
        (128.22, 126.80, 128.01), (128.27, 126.71, 127.11), (128.09, 126.80, 127.73), (128.27, 126.13, 127.06), (127.74, 125.92, 127.33),
        (128.77, 126.99, 128.71), (129.29, 127.81, 127.87), (130.06, 128.47, 128.58), (129.12, 128.06, 128.60), (129.29, 127.61, 127.93),
        (128.47, 127.60, 128.11), (128.09, 127.00, 127.60), (128.65, 126.90, 127.60), (129.14, 127.49, 128.69), (128.64, 127.40, 128.27)
    ]
    sto = [None] * 13 + [
        70.54, 67.70, 89.147, 65.89, 81.91, 64.599, 74.66, 98.57, 69.979, 73.09, 73.45, 61.20, 60.92, 40.58, 40.58, 66.908, 56.76
        ]
    df = pd.DataFrame(values, columns=["high", "low", "close"])
    df = stochastic(df)

    assert set(df.columns) == set([
        'high', 'low', 'close', 'Stochastic14', 'Stochastic14_Signal3',
        ])
    for i in range(len(sto)):
        if not sto[i]:
            assert df['Stochastic14'][i] != df['Stochastic14'][i]  # method to check for NaN values
        else:
            assert math.isclose(sto[i], df['Stochastic14'][i], rel_tol=0.0001)


def test_that_rsi_is_computed():
    close = [
        44.3489, 44.0902, 44.1497, 43.6124, 44.3278, 44.8264, 45.0955, 45.4245, 45.8433, 46.0826, 45.8931, 46.0328, 45.614,
        46.282, 46.282, 46.0028, 46.0328, 46.4116, 46.2222, 45.6439, 46.2122, 46.2521, 45.7137, 46.4515, 45.7835, 45.3548,
        44.0288, 44.1783, 44.2181, 44.5672, 43.4205, 42.6628, 43.1314
    ]
    rsi_result = [None] * 14 + [
        70.384, 66.187, 66.419, 69.281, 66.24, 57.887, 62.846, 63.173, 55.993, 62.315, 54.659, 50.382, 39.964,
        41.434, 41.842, 45.436, 37.286, 33.065, 37.758
    ]
    df = pd.DataFrame(close, columns=["close"])
    df = rsi(df)

    for i in range(len(rsi_result)):
        if not rsi_result[i]:
            assert df['RSI14'][i] != df['RSI14'][i]  # method to check for NaN values
        else:
            assert math.isclose(rsi_result[i], df['RSI14'][i], rel_tol=0.0001)


def test_directional_movement():
    with open("tests/data_adx.json", "r") as fd:
        data = json.load(fd)["data"]
    
    values = [(data["low"][i], data["high"][i], data["close"][i]) for i in range(len(data["high"]))]
    df = pd.DataFrame(values, columns=["low", "high", "close"])
    df = directional_movement(df)

    for i in range(len(data["high"])):
        # Checking DI+ values
        if not data["di_plus"][i]:
            assert df['DI+14'][i] != df['DI+14'][i]  # method to check for NaN values
        else:
            assert math.isclose(data["di_plus"][i], df['DI+14'][i])

        # Checking DI- values
        if not data["di_minus"][i]:
            assert df['DI-14'][i] != df['DI-14'][i]  # method to check for NaN values
        else:
            assert math.isclose(data["di_minus"][i], df['DI-14'][i])
        
        # Checking ADX values
        if not data["adx"][i]:
            assert df['ADX14'][i] != df['ADX14'][i]  # method to check for NaN values
        else:
            assert math.isclose(data["adx"][i], df['ADX14'][i])


@pytest.mark.parametrize("values, sar", [
    ([
        (47.95, 47.32), (48.11, 47.25), (48.30, 47.77), (48.17, 47.91), (48.60, 47.90), (48.33, 47.74),  # rising trend
        (48.40, 48.10), (48.55, 48.06), (48.45, 48.07), (48.70, 47.79), (48.72, 48.14), (48.90, 48.39),
        (48.87, 48.37), (48.82, 48.24), (49.05, 48.64), (49.20, 48.94), (49.35, 48.86)
    ], [
        47.32, 48.11, 47.25, 47.25, 47.27, 47.32, 47.38, 47.42, 47.47, 47.52, 47.59, 47.68, 47.80, 47.91,
        48.01, 48.13, 48.28
    ]),
    ([
        (46.60, 45.60), (46.59, 45.90), (46.55, 45.38), (46.30, 45.25), (45.43, 43.99), (44.55, 44.07),  # falling trend
        (44.84, 44.00), (44.80, 43.96), (44.38, 43.27), (43.97, 42.58), (43.23, 42.83), (43.73, 42.98),
        (43.92, 43.37), (43.61, 42.57), (42.97, 42.07), (43.13, 42.59), (43.46, 42.71)
    ], [
        45.6, 45.6, 46.59, 46.59, 46.55, 46.40, 46.26, 46.12, 45.95, 45.68, 45.31, 44.98, 44.69, 44.44,
        44.18, 43.84, 43.56
    ]

    )
])
def test_parabolic_sar(values, sar):
    df = pd.DataFrame(values, columns=["high", "low"])
    df = parabolic_sar(df)

    for i in range(len(sar)):
        assert math.isclose(sar[i], df["Parabolic_SAR"][i], rel_tol=0.01)
