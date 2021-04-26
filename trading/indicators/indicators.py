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


def bollinger(df, nb=20, c_input="high"):
    """ Compute Bollinger upper and lower bands.
        Bollinger upper band is the value of the MMA20 + 2*standard deviation
        Bollinger lower band is the value of the MMA20 - 2*standard deviation
    """
    column_mma = f"MMA{nb}"
    if column_mma not in df:
        df = mma(df, nb, c_input=c_input)
    
    c_bollinger_lower = f"Bollinger{nb}_lower"
    c_bollinger_upper = f"Bollinger{nb}_upper"

    if len(df) >= nb:
        for index in range(0, len(df) - nb + 1):
            deviation_squared = [(df[c_input][index + i] - df[column_mma][nb + index - 1])**2 for i in range(0, nb)]
            mean_dev = sum(deviation_squared) / nb
            standard_dev = math.sqrt(mean_dev)
            bollinger_down = df[column_mma][nb + index - 1] - 2 * standard_dev
            bollinger_up = df[column_mma][nb + index - 1] + 2 * standard_dev
            df.loc[nb + index - 1, c_bollinger_lower] = bollinger_down
            df.loc[nb + index - 1, c_bollinger_upper] = bollinger_up

    return df


def stochastic(df, nb=14, nb_signal=3):
    """ Compute stochastic oscillator.
    Stochastic measures the level of the close relative to the high-low range over 14 days.
    """
    column_sto = f"Stochastic{nb}"
    column_signal = f"Stochastic{nb}_Signal{nb_signal}"

    if len(df) >= nb:
        # Stochastic
        for index in range(0, len(df) - nb + 1):
            lowest = min(df[index:index + nb]["low"])
            highest = max(df[index:index + nb]["high"])
            sto = (df["close"][index + nb - 1] - lowest)/(highest - lowest) * 100
            df.loc[index + nb - 1, column_sto] = sto
        
        # Stochastic signal
        df = mma(df, 3, c_input=column_sto, c_output=column_signal)
    
    return df


def rsi(df, nb=14):
    """ Compute RSI (Relative Strength Index). RSI measures the speed and change of price movements.
        RSI = 100 - (100 / (1 + RS)) where RS = average gain / average loss over 14 days.
    """
    column_rsi = f"RSI{nb}"
    avg_gain = None
    avg_loss = None
    if len(df) >= nb:
        for index in range(1, len(df) - nb + 1):
            if not avg_gain:
                gain = [
                    df["close"][index + i] - df["close"][index + i - 1] 
                        for i in range(0, nb) if df["close"][index + i] - df["close"][index + i - 1] > 0
                ]
                loss = [
                    -(df["close"][index + i] - df["close"][index + i - 1])
                        for i in range(0, nb) if df["close"][index+i] - df["close"][index + i - 1] < 0
                ]
                avg_gain = sum(gain) / nb
                avg_loss = sum(loss) / nb
            else:
                current_gain = df["close"][index + nb - 1] - df["close"][index + nb - 2] \
                    if df["close"][index + nb - 1] - df["close"][index + nb - 2] > 0 else 0
                current_loss = -(df["close"][index + nb - 1] - df["close"][index + nb - 2]) \
                    if df["close"][index + nb - 1] - df["close"][index + nb - 2] < 0 else 0
                avg_gain = (avg_gain * (nb - 1) + current_gain) / 14
                avg_loss = (avg_loss * (nb - 1) + current_loss) / 14
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            df.loc[index + nb - 1, column_rsi] = rsi

    return df


def directional_movement(df, nb=14):
    """ Compute ADX, +DI and -DI.
    ADX = Average Directional Index (measures the strength of the trend), 
    +DI = Plus directional Indicator, -DI = Minus Directional Indicator
    (measure the trend direction)
    """
    column_adx = f"ADX{nb}"
    column_diplus = f"DI+{nb}"
    column_diminus = f"DI-{nb}"

    if len(df) >= nb:
        true_ranges = [df["high"][0] - df["low"][0]]
        dms_plus = [0]
        dms_minus = [0]
        for current in range(1, len(df)):
            # True range
            true_ranges.append(max(
                df["high"][current] - df["low"][current],
                abs(df["high"][current] - df["close"][current - 1]),
                abs(df["low"][current] - df["close"][current - 1])
            ))

            # DM+ and DM-
            if (df["high"][current] - df["high"][current - 1]) > (df["low"][current - 1] - df["low"][current]):
                dms_plus.append(max(df["high"][current] - df["high"][current - 1], 0))
                dms_minus.append(0)
            else:
                dms_plus.append(0)
                dms_minus.append(max(df["low"][current - 1] - df["low"][current], 0))

        average_true_range = None
        adx = None
        dxs = []
        for index in range(1, len(df) - nb + 1):
            current = index + nb - 1
            if not average_true_range:
                average_true_range = sum(true_ranges[:nb]) / nb
                tr_nb = sum(true_ranges[1:nb+1])
                dm_plus_nb = sum(dms_plus[1:nb+1])
                dm_minus_nb = sum(dms_minus[1:nb+1])
            else:
                average_true_range = (average_true_range * (nb - 1) + true_ranges[current]) / nb
                tr_nb = tr_nb - tr_nb/nb + true_ranges[current]
                dm_plus_nb = dm_plus_nb - dm_plus_nb/nb + dms_plus[current]
                dm_minus_nb = dm_minus_nb - dm_minus_nb/nb + dms_minus[current]
            di_plus = dm_plus_nb / tr_nb * 100
            di_minus = dm_minus_nb / tr_nb * 100
            current_dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100
            dxs.append(current_dx)
            if current >= nb * 2 - 1:
                if not adx:
                    adx = sum(dxs[:nb]) / nb
                else:
                    adx = ((adx * 13) + current_dx) / nb
                df.loc[current, column_adx] = adx
            df.loc[current, column_diplus] = di_plus
            df.loc[current, column_diminus] = di_minus

    return df


def parabolic_sar(df, starting_af=0.02, maximum=0.2):
    """ Compute Parabolic SAR.
    SAR = previous_SAR + previous_af(previous_EP - previous_SAR) for rising trend
    SAR = previous_SAR - previous_af(previous_SAR - previous_EP) for falling trend
    af stands for Acceleration Factor, and EP for Extreme Point.
    """
    column_sar = "Parabolic_SAR"

    if len(df) > 2:
        if df['high'][1] > df["high"][0]:
            sar = df['low'][1]
            rising = True
            previous_ep = df['high'][2]
        else:
            sar = df['high'][1]
            rising = False
            previous_ep = df['low'][2]
        af = starting_af
        for index in range(2, len(df)):
            if sar < df['high'][index]:
                # rising trend
                if not rising:
                # starting rising trend
                    rising = True
                    af = starting_af
                sar = min(sar + af * (previous_ep - sar), min(df['low'][index - 1], df['low'][index - 2]))
                ep = df['high'][index]
                if ep > previous_ep and af < maximum:
                    af = min(af + starting_af, maximum)
                    previous_ep = ep
            else:
                # falling trend
                if rising:
                    # starting falling trend 
                    rising = False
                    af = starting_af
                sar = max(sar - af * (sar - previous_ep), max(df['high'][index - 1], df['high'][index - 2]))
                ep = df['low'][index]
                if ep < previous_ep and af < maximum:
                    af = min(af + starting_af, maximum)
                    previous_ep = ep
            df.loc[index, column_sar] = sar
        
        return df
