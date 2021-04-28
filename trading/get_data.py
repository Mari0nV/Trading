from client import authent
from binance.client import Client

import pandas as pd
import numpy as np
import json


@authent
def get_candle_data(currency, client=None):
    klines = client.get_historical_klines(currency, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2021", "15 Apr, 2021", limit=10)
    df = pd.DataFrame(np.array(klines)[:,:6], columns=["time", "open", "high", "low", "close", "volume"])
    df = df.astype(np.float64)
    return df
