from client import authent
from binance.client import Client

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

folder = "coins_data"

@authent
def get_candle_data(currency, client=None, begin="2020-01-01 02:00:00", end="now", granularity="1d"):
    filename = f"{folder}/{currency}_{granularity}_data.json"
    try:
        # Get existing data from file
        with open(filename, "r") as fp:
            data = json.load(fp)["data"]
            klines = data["klines"]
            first_date = datetime.fromtimestamp(int(klines[0][0])/1000)
            last_date = datetime.fromtimestamp(int(klines[-1][0])/1000)
            begin = datetime.strptime(begin, "%Y-%m-%d %H:%M:%S")
            if end != "now":
                end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            else:
                end = datetime.now()
                end = end - timedelta(
                    hours=end.hour,
                    minutes=end.minute,
                    seconds=end.second,
                    microseconds=end.microsecond)
        
        begin_first = False
        end_last = False
        # Retrieve missing data from beginning
        if begin.timestamp() * 1000 < data["begin"]:
            starting_klines = client.get_historical_klines(
                currency,
                granularity,
                str(begin.timestamp() * 1000),
                str(first_date.timestamp() * 1000),
                limit=10
            )
            with open(filename, "w") as fp:
                klines = starting_klines[:-1] + klines
                json.dump({"data": {
                    "klines": klines,
                    "begin": begin.timestamp() * 1000,
                    "end": end.timestamp() * 1000
                    }}, fp)
            begin_first = True
        # Retrieve recent missing data
        if end.timestamp() * 1000 > data["end"]:
            ending_klines = client.get_historical_klines(
                currency,
                granularity,
                str(last_date.timestamp() * 1000),
                str(end.timestamp() * 1000),
                limit=10
            )
            with open(filename, "w") as fp:
                klines = klines + ending_klines
                json.dump({"data": {
                    "klines": klines,
                    "begin": begin.timestamp() * 1000,
                    "end": end.timestamp() * 1000
                    }}, fp)
            end_last = True
        nb_days = (end - begin).days
        nb_days_file = len(klines)
        if nb_days == nb_days_file or begin_first:  # begin is the time of the first kline of the file
            index_begin, index_end = 0, nb_days
        elif end_last:  # end is the time of the last kline of the file
            index_begin, index_end = nb_days_file - nb_days, nb_days_file
        else:  # begin and end are in the middle of the file
            index_set = False
            for i, kline in enumerate(klines[::-1]):
                if end <= datetime.fromtimestamp(int(kline[0])/1000):
                    index_end = len(klines) - i
                    index_begin = index_end - nb_days
                    index_set = True
            if not index_set:
                index_begin, index_end = 0, nb_days_file
    except (FileNotFoundError, json.JSONDecodeError):
        # Create file with all data
        with open(filename, "w") as fp:
            klines = client.get_historical_klines(
                currency,
                granularity,
                begin,
                end,
                limit=10
            )
            begin = datetime.strptime(begin, "%Y-%m-%d %H:%M:%S")
            if end != "now":
                end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            else:
                end = datetime.now()
            if klines:
                json.dump({
                    "data": {
                        "klines": klines,
                        "begin": begin.timestamp() * 1000,
                        "end": end.timestamp() * 1000
                        }
                    }, fp)
        nb_days = (end - begin).days
        index_begin, index_end = 0, nb_days
    
    if not klines:
        # print(f"No available data for {currency}.")
        os.remove(filename)
        return pd.DataFrame()
    
    df = pd.DataFrame(np.array(klines[index_begin:index_end])[:,:6], columns=["time", "open", "high", "low", "close", "volume"])
    df = df.astype(np.float64)
    return df


if __name__ == '__main__':
    data = get_candle_data("BTCUSDT", begin="2020-02-01 00:00:00", end='now')
    print(data)
