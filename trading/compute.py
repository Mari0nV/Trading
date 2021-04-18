from client import authent
from trading.utils import (
    mma
)
from binance.client import Client

import pandas as pd
import numpy as np
import json


@authent
def compute(client=None):
    klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2021", "15 Apr, 2021", limit=10)
    with open('test_data.json', "w") as f:
        json.dump({"data": klines}, f)
    # df = pd.DataFrame(np.array(klines)[:,:6], columns=["timestamp", "open", "high", "low", "close", "volume"])
    # print(df)




if __name__ == '__main__':
    #compute()
    with open('test_data.json', "r") as f:
        data = json.load(f)["data"]
    df = pd.DataFrame(np.array(data)[:,:6], columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["high"] = pd.to_numeric(df["high"], downcast="float")
    print(df[:5])
    df = mma(df, 10)
    print(df)