import numpy as np
import pandas as pd


def mma(df, nb):
    column = f'MMA{nb}'
    df[column] = [0 for _ in range(len(df))]
    index = 0
    for index in range(0, len(df)-nb):
        mean = sum(df[index:index+nb]["high"]) / nb
        df.loc[nb+index, column] = mean

    return df
