import numpy as np
import pandas as pd


def mma(df, nb):
    if len(df) >= nb:
        column = f'MMA{nb}'
        df[column] = [None for _ in range(len(df))]
        for index in range(0, len(df) - nb + 1):
            mean = sum(df[index:index + nb]["high"]) / nb
            df.loc[nb + index - 1, column] = mean

    return df
