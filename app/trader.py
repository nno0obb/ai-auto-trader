import os
from datetime import datetime

import pandas as pd
import pyupbit
import requests
import ta
from dotenv import load_dotenv

load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")


class Trader:
    def __init__(self):
        self.trader = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

    # 한화로 거래 가능한 모든 암호화폐 목록
    def get_all_tickers(self) -> list[str]:
        return pyupbit.get_tickers(fiat="KRW")  # ["KRW-BTC", "KRW-ETH", "KRW-XRP", ...]

    # 현재 나의 업비트 계좌 잔액
    def get_my_balance(self) -> float:
        return self.trader.get_balance("KRW")

    # 현재 보유한 특정 코인 현황
    def get_balance(self, ticker: str) -> float:
        return self.trader.get_balance(ticker)

    # 현재 보유한 특정 코인 평균 매수 가격
    def get_avg_price(self, ticker: str) -> float:
        return self.trader.get_avg_price(ticker)

    # 현재 나의 주문 목록
    def get_my_orders(self, ticker: str) -> list[dict]:
        """
        {
            "uuid": "...",
            "side": "bid",
            "ord_type": "price",
            "price": "5000",
            "avg_price": "48.32415",
            "state": "cancel",
            "market": "KRW-PENGU",
            "created_at": "YYYY-MM-DDTHH:MM:SS+09:00",
            "reserved_fee": "2.5",
            "remaining_fee": "0.0000000001705",
            "paid_fee": "2.4999999998295",
            "locked": "0.0000003411705",
            "prevented_locked": "0",
            "executed_volume": "103.51966873",
            "trades_count": 1,
            "application_name": "self_issued_open_api",
            "thirdparty": False,
            "is_cancel_and_new_order": False,
        }
        """
        orders = [
            *self.trader.get_order(ticker, state="wait"),
            *self.trader.get_order(ticker, state="watch"),
            *self.trader.get_order(ticker, state="done"),
            *self.trader.get_order(ticker, state="cancel"),
        ]
        orders.sort(key=lambda x: datetime.strptime(x["created_at"], "%Y-%m-%dT%H:%M:%S+09:00"))
        return orders

    # 특정 코인의 현재 가격
    def get_current_price(self, ticker: str) -> float:
        return pyupbit.get_current_price(ticker)

    # 특정 코인의 고가/시가/저가/종가/거래량 데이터
    def get_ohlcv(self, ticker: str, count: int, interval: str) -> pd.DataFrame:
        return pyupbit.get_ohlcv(ticker, count=count, interval=interval)

    # 특정 코인의 시장가 매수
    def buy(self, ticker: str, price: float) -> bool:
        """
        {
            "uuid": "...",
            "side": "bid",
            "ord_type": "price",
            "price": "5000",
            "state": "wait",
            "market": "KRW-PENGU",
            "created_at": "YYYY-MM-DDTHH:MM:SS+09:00",
            "reserved_fee": "2.5",
            "remaining_fee": "2.5",
            "paid_fee": "0",
            "locked": "0",
            "prevented_locked": "0",
            "executed_volume": "0",
        }
        """
        return self.trader.buy_market_order(ticker=ticker, price=price)

    # 특정 코인의 시장가 매도
    def sell(self, ticker: str, volume: float) -> bool:
        """
        {
            "uuid": "...",
            "side": "ask",
            "ord_type": "market",
            "state": "wait",
            "market": "KRW-PENGU",
            "created_at": "YYYY-MM-DDTHH:MM:SS+09:00",
            "volume": "150",
            "remaining_volume": "150",
            "prevented_volume": "0",
            "reserved_fee": "0",
            "remaining_fee": "0",
            "paid_fee": "0",
            "locked": "150",
            "prevented_locked": "0",
            "executed_volume": "0",
            "trades_count": 0,
        }
        """
        return self.trader.sell_market_order(ticker=ticker, volume=volume)

    def hold(self):
        pass

    def get_avg_buy_price(self, ticker: str) -> float:
        return self.trader.get_avg_buy_price(ticker)

    def get_fear_greed_index(self) -> dict:
        base_url = "https://api.alternative.me/fng/"
        api_url = base_url + "?limit=1"
        response = requests.get(api_url)
        response_data = response.json()["data"]
        fear_greed_index = response_data[0]
        return fear_greed_index

    def get_order_by_uuid(self, ticker: str, uuid: str) -> dict:
        orders = self.get_my_orders(ticker)
        for order in orders:
            if order["uuid"] == uuid:
                return order
        return None

    def get_data(self, ticker: str) -> dict:
        # 초단타를 위한 상세한 데이터 수집
        current_price = self.get_current_price(ticker)
        avg_buy_price = self.get_avg_buy_price(ticker)
        balance = self.get_balance(ticker)
        print(f"[Ticker] {ticker}")
        print(f"[Balance] {balance}")
        krw_balance = self.get_my_balance()

        # 1분봉 데이터 (최근 50개 - 기술적 분석을 위해 더 많은 데이터 필요)
        ohlcv_data = self.get_ohlcv(ticker, count=50, interval="minute1")

        # 수익률 계산
        profit_loss_pct = 0
        if balance > 0 and avg_buy_price > 0:
            profit_loss_pct = ((current_price - avg_buy_price) / avg_buy_price) * 100

        # 기술적 분석 지표 계산
        try:
            # 이동평균선
            ohlcv_data["sma_5"] = ta.trend.sma_indicator(ohlcv_data["close"], window=5)
            ohlcv_data["sma_10"] = ta.trend.sma_indicator(ohlcv_data["close"], window=10)
            ohlcv_data["sma_20"] = ta.trend.sma_indicator(ohlcv_data["close"], window=20)

            # RSI (상대강도지수)
            ohlcv_data["rsi"] = ta.momentum.rsi(ohlcv_data["close"], window=14)

            # MACD
            macd_line = ta.trend.macd(ohlcv_data["close"])
            macd_signal = ta.trend.macd_signal(ohlcv_data["close"])
            ohlcv_data["macd"] = macd_line
            ohlcv_data["macd_signal"] = macd_signal
            ohlcv_data["macd_histogram"] = macd_line - macd_signal

            # 볼린저 밴드
            bollinger = ta.volatility.BollingerBands(ohlcv_data["close"])
            ohlcv_data["bb_upper"] = bollinger.bollinger_hband()
            ohlcv_data["bb_middle"] = bollinger.bollinger_mavg()
            ohlcv_data["bb_lower"] = bollinger.bollinger_lband()

            # 스토캐스틱
            stoch = ta.momentum.StochasticOscillator(ohlcv_data["high"], ohlcv_data["low"], ohlcv_data["close"])
            ohlcv_data["stoch_k"] = stoch.stoch()
            ohlcv_data["stoch_d"] = stoch.stoch_signal()

            # 거래량 지표
            ohlcv_data["volume_sma"] = ta.volume.volume_sma(ohlcv_data["close"], ohlcv_data["volume"], window=10)

            # 최근 데이터와 기술적 지표 요약
            latest = ohlcv_data.iloc[-1]
            prev = ohlcv_data.iloc[-2]

            technical_summary = {
                "current_vs_sma5": (
                    round(((current_price - latest["sma_5"]) / latest["sma_5"]) * 100, 2)
                    if pd.notna(latest["sma_5"])
                    else 0
                ),
                "current_vs_sma10": (
                    round(((current_price - latest["sma_10"]) / latest["sma_10"]) * 100, 2)
                    if pd.notna(latest["sma_10"])
                    else 0
                ),
                "rsi": round(latest["rsi"], 2) if pd.notna(latest["rsi"]) else 50,
                "rsi_signal": "oversold" if latest["rsi"] < 30 else "overbought" if latest["rsi"] > 70 else "neutral",
                "macd_signal": "bullish" if latest["macd"] > latest["macd_signal"] else "bearish",
                "macd_momentum": "increasing" if latest["macd_histogram"] > prev["macd_histogram"] else "decreasing",
                "bb_position": (
                    "upper"
                    if current_price > latest["bb_upper"]
                    else "lower" if current_price < latest["bb_lower"] else "middle"
                ),
                "stoch_signal": (
                    "oversold" if latest["stoch_k"] < 20 else "overbought" if latest["stoch_k"] > 80 else "neutral"
                ),
                "volume_vs_avg": (
                    round((latest["volume"] / latest["volume_sma"]) * 100, 0) if pd.notna(latest["volume_sma"]) else 100
                ),
            }

        except Exception as e:
            technical_summary = {"error": f"Technical analysis failed: {str(e)}"}

        return {
            "ticker": ticker,
            "current_price": current_price,
            "avg_buy_price": avg_buy_price,
            "coin_balance": balance,
            "krw_balance": krw_balance,
            "profit_loss_percent": round(profit_loss_pct, 2),
            "position_value_krw": round(balance * current_price, 0),
            "can_buy": krw_balance >= 5000,
            "can_sell": balance > 0 and (balance * current_price) >= 5000,
            "technical_analysis": technical_summary,
            "recent_ohlcv_with_indicators": ohlcv_data.tail(10).round(2).to_string(),  # 최근 10개 캔들과 지표들
            "fear_greed_index": self.get_fear_greed_index(),
        }


def test():
    trader = Trader()
    pengu_balance = trader.get_balance("KRW-PENGU")
    print(pengu_balance)


if __name__ == "__main__":
    test()
