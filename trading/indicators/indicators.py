import numpy as np
import pandas as pd
import math


def mma(df, nb, c_input="high", c_output=None):
    """ Compute Modified Moving Average of each point from a column of a dataframe
        (except the first ones), then add the associated MMA column into the dataframe. """
    column_mma = f'MMA{nb}' if not c_output else c_output
    df[column_mma] = [None for _ in range(len(df))]
    if len(df) >= nb:
        for index in range(0, len(df) - nb + 1):
            mean = sum(df[index:index + nb][c_input]) / nb
            df.loc[nb + index - 1, column_mma] = mean

    return df


def mme(df, nb, c_input="high", alpha=None, c_output=None):
    """ Compute Exponential Moving Average of each point from a column of a dataframe
        (except the first ones), then add the associated MME column into the dataframe.
        alpha is the degree of weighting decrease, comprised between 0 and 1. (A higher alpha discounts
        older observations faster. """
    alpha = 2 / (nb+1) if alpha is None else alpha
    column_output = f'MME{nb}-{round(alpha, 2)}' if not c_output else c_output
    df[column_output] = [None for _ in range(len(df))]

    if len(df) >= nb:
        for index in range(0, len(df) - nb + 1):
            if alpha != 0:
                mean = sum([((1-alpha)**(nb - p - 1)) * df[c_input][index + p] for p in range(0, nb)]) / ((1 - (1 - alpha)**nb)/ alpha)
            else:
                mean = sum(df[index:index + nb][c_input]) / nb
            df.loc[nb + index - 1, column_output] = mean

    return df


def macd(df, mme_short=12, mme_long=26, signal=9):
    """ Compute MACD, signal and histogram of each point from a column of a dataframe
        (except the first ones), then add the associated columns into the dataframe.
        MACD is the difference between two MME (by default 12 and 26).
        The signal is the MME9 of the MACD.
        The histogram is the MACD minus the signal.
    """

    # MACD
    column_mme_short = f"MME{mme_short}-{round(2/(mme_short+1), 2)}"
    column_mme_long = f"MME{mme_long}-{round(2/(mme_long+1), 2)}"
    column_macd = f"MACD({mme_short},{mme_long})"

    if column_mme_short not in df:
        df = mme(df, mme_short)
    if column_mme_long not in df:
        df = mme(df, mme_long)
    
    df[column_macd] = df[column_mme_short] - df[column_mme_long]

    # MACD signal
    column_signal = f"MACD_signal({mme_short},{mme_long})"
    df = mme(df, 9, c_input=column_macd, c_output=column_signal)

    # MACD histogram
    column_histo = f"MACD_histo({mme_short},{mme_long})"
    df[column_histo] = df[column_macd] - df[column_signal]

    return df
