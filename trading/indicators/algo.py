from trading.get_data import get_candle_data
from trading.indicators.indicators import (
    directional_movement,
    parabolic_sar,
    rsi,
    stochastic,
)

from client import authent
import json
from klotan import criteria

# OAXBTC, KMDETH

@authent
def get_coins_list(client=None):
    infos = client.get_all_tickers()
    coins = [ticker["symbol"] for ticker in infos]

    print(f"Retrieved {len(coins)} coins.")
    return coins

def interesting_coin(df):
    if "RSI14" in df and "ADX14" in df and "Parabolic_SAR" in df:
        # if df["RSI14"].iloc[-1] < 40:
        if df["DI+14"].iloc[-1] > df["DI-14"].iloc[-1]:
                # if df["ADX14"].iloc[-1] > 30:
            if df["Parabolic_SAR"].iloc[-1] < df["low"].iloc[-1]:
                #         if df["Stochastic14"].iloc[-1] < 40:
                #             if df["Stochastic14"].iloc[-1] > df["Stochastic14_Signal3"].iloc[-1]:
                return True

    return False


if __name__ == '__main__':
    coins = get_coins_list()
    try:
        with open("empty_coins.json", "r") as fp:
            empty_coins = json.load(fp)["empty"]
    except Exception:
        empty_coins = []
    coins = [coin for coin in coins if coin not in empty_coins]
    for coin in coins:
        df = get_candle_data(coin, begin="2021-01-01 00:00:00", end="now", granularity="1d")
        if df.empty or df is None:
            empty_coins.append(coin)
            with open("empty_coins.json", "w") as fp:
                json.dump({"empty": empty_coins}, fp)
            continue
        df = parabolic_sar(df)
        df = directional_movement(df)
        df = rsi(df)
        df = stochastic(df)

        if interesting_coin(df):
            if 'ETH' not in coin:
                print("Interesting coin: ", coin)
                print(df.tail(), '\n')

        # print(df.tail())


# if __name__ == '__main__':
#     df = get_candle_data("BTCUSDT", begin="2021-01-01 00:00:00", end="now", granularity="1d")
#     df = parabolic_sar(df)
#     df = directional_movement(df)
#     df = rsi(df)
#     df = stochastic(df)
                                                                 
#     print(df.tail())