from pprint import pprint

import pyupbit
from dotenv import load_dotenv

load_dotenv()


def get_ohlcv(ticker: str):
    ohlcv = pyupbit.get_ohlcv(ticker=ticker)
    return ohlcv


def test():
    ohlcv_krw_btc = get_ohlcv(ticker="KRW-BTC")
    pprint(ohlcv_krw_btc)


if __name__ == "__main__":
    test()
