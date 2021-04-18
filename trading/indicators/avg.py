import numpy as np
import pandas as pd


def mma(df, nb):
    """ Compute Modified Moving Average of each point from the "high" column of a dataframe
        (except the first ones), then add the associated MMA column into the dataframe. """
    column = f'MMA{nb}'
    df[column] = [None for _ in range(len(df))]
    if len(df) >= nb:
        for index in range(0, len(df) - nb + 1):
            mean = sum(df[index:index + nb]["high"]) / nb
            df.loc[nb + index - 1, column] = mean

    return df


def mme(df, nb, alpha=0.5):
    """ Compute Exponential Moving Average of each point from the "high" column of a dataframe
        (except the first ones), then add the associated MME column into the dataframe.
        alpha is the degree of weighting decrease, comprised between 0 and 1. (A higher alpha discounts
        older observations faster. """
    column = f'MME{nb}-{alpha}'
    df[column] = [None for _ in range(len(df))]
    if len(df) >= nb:
        for index in range(0, len(df) - nb + 1):
            if alpha != 0:
                mean = sum([((1-alpha)**(nb - p - 1)) * df["high"][index + p] for p in range(0, nb)]) / ((1 - (1 - alpha)**nb)/ alpha)
            else:
                mean = sum(df[index:index + nb]["high"]) / nb
            df.loc[nb + index - 1, column] = mean

    return df
