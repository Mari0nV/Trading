from client import authent
from binance.client import Client

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import dateparser
import pytz
import os

import trading.config as cfg
from trading.utils import date_to_milliseconds


g_mapping = {  # periods in ms
    "1d": 864e5,
    "4h": 144e5, 
    "15m": 9e5,
    "1m": 6e4
}


@authent
def get_data_from_binance(currency, granularity, start_date, end_date, client=None):
    start_date = date_to_milliseconds(start_date)
    end_date = date_to_milliseconds(end_date)

    klines = client.get_historical_klines(
                currency,
                granularity,
                str(start_date),
                str(end_date)
            )
    
    clean_klines = [
        kline[:6] for kline in klines
    ]
    return clean_klines


def get_candle_data(currency, begin="2020-01-01 00:00:00", end="now", granularity="1d", folder=cfg.COINS_FOLDER):
    filename = f"{folder}/{currency}_{granularity}_data.json"
    begin_ms = date_to_milliseconds(begin)
    end_ms = date_to_milliseconds(end)
    nb_periods_float = (end_ms - begin_ms) / g_mapping[granularity]
    if not nb_periods_float.is_integer():
        nb_periods = int(nb_periods_float) + 1
    else:
        nb_periods = int(nb_periods_float)
    try:
        # Get existing data from file
        with open(filename, "r") as fp:
            data = json.load(fp)["data"]
            klines = data["klines"]
            first_date_ms = int(klines[0][0])
            last_date_ms = int(klines[-1][0])

        begin_first = False
        end_last = False
        # Retrieve missing data from beginning
        if begin_ms < data["begin"]:
            starting_klines = get_data_from_binance(
                currency,
                granularity,
                begin_ms,
                first_date_ms
            )
            with open(filename, "w") as fp:
                klines = starting_klines[:-1] + klines
                json.dump({"data": {
                    "klines": klines,
                    "begin": begin_ms,
                    "end": last_date_ms
                    }}, fp)
            begin_first = True
            first_date_ms = begin_ms
        # Retrieve recent missing data
        if end_ms > data["end"]:
            ending_klines = get_data_from_binance(
                currency,
                granularity,
                last_date_ms,
                end_ms
            )
            with open(filename, "w") as fp:
                klines = klines + ending_klines[1:]
                json.dump({"data": {
                    "klines": klines,
                    "begin": first_date_ms,
                    "end": end_ms
                    }}, fp)
            end_last = True
        nb_periods_file = len(klines)
        if nb_periods == nb_periods_file or begin_first:  # begin is the time of the first kline of the file
            index_begin, index_end = 0, nb_periods
        elif end_last:  # end is the time of the last kline of the file
            index_begin, index_end = nb_periods_file - nb_periods, nb_periods_file
        else:  # begin and end are in the middle of the file
            index_set = False
            for i, kline in enumerate(klines[::-1]):
                if end_ms <= int(kline[0]):
                    index_end = len(klines) - (i + 1)
                    index_begin = index_end - nb_periods
                    index_set = True
            if not index_set:
                index_begin, index_end = 0, nb_periods_file
    except (FileNotFoundError, json.JSONDecodeError):
        # Create file with all data
        with open(filename, "w") as fp:
            klines = get_data_from_binance(
                currency,
                granularity,
                begin,
                end
            )
            if klines:
                json.dump({
                    "data": {
                        "klines": klines,
                        "begin": begin_ms,
                        "end": end_ms
                        }
                    }, fp)
        index_begin, index_end = 0, nb_periods
    
    if not klines:
        os.remove(filename)
        return pd.DataFrame()
    # import pdb; pdb.set_trace()
    try:
        df = pd.DataFrame(np.array(klines[index_begin:index_end])[:,:6], columns=["time", "open", "high", "low", "close", "volume"])
        df = df.astype(np.float64)
        return df
    except Exception as e:
        print(currency, e)
        return pd.DataFrame()


if __name__ == '__main__':
    data = get_data_from_binance("ETHUSDT", start_date="2021-05-04 22:00:00", end_date= "2021-05-04 23:35:00", granularity="15m")
    
    for elt in data:
        print(elt[0], datetime.fromtimestamp(int(elt[0])/1000))
