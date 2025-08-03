import json
import os
from typing import Any

import pandas as pd
import pyupbit
from dotenv import load_dotenv
from openai import OpenAI

from schema import Answer

load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")


class GPT:
    def __init__(self):
        self.openai_client = OpenAI()
        self.system_prompt = "\n".join(
            [
                "You are an expert in Bitcoin investing.",
                "Tell me whether to buy, sell, or hold at the moment based on the chart data provided.",
                "It's okay to invest boldly.",
                "Try aggressive investment.",
                "Response in Json format.",
                "",
                "Response Example:",
                '{"decision": "buy", "reason": "some technical reason"}',
                '{"decision": "sell", "reason": "some technical reason"}',
                '{"decision": "hold", "reason": "some technical reason"}',
            ]
        )

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def ask_with_data(self, data: Any) -> Answer:
        if isinstance(data, pd.DataFrame):
            data = data.to_json()

        response = self.openai_client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self.system_prompt,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": data,
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{\n  "decision": "hold",\n  "reason": "The recent chart data shows high volatility with rapid price increases followed by sharp drops. After a peak, the price appears to be consolidating around the 157-160M level with moderate volume and no clear breakout or breakdown signals. There is no strong bullish reversal or bearish continuation pattern; thus, it\'s prudent to hold and wait for more confirmation before making a new buy or sell decision."\n}',
                        }
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "answer",
                    "schema": Answer.model_json_schema() | {"additionalProperties": False},
                }
            },
        )
        response_text = response.to_dict()["output"][0]["content"][0]["text"]
        response_data = json.loads(response_text)
        return Answer(decision=response_data["decision"], reason=response_data["reason"])


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
            self.trader.get_order(ticker, state="wait"),
            self.trader.get_order(ticker, state="watch"),
            self.trader.get_order(ticker, state="done"),
            self.trader.get_order(ticker, state="cancel"),
        ]
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


def test():
    trader = Trader()

    pengu_price = trader.get_current_price("KRW-PENGU")
    print(pengu_price)

    pengu_ohlcv = trader.get_ohlcv("KRW-PENGU", count=10, interval="day")
    print(pengu_ohlcv)

    # print(trader.buy("KRW-PENGU", 5000))
    print(trader.get_my_orders("KRW-PENGU"))

    print(trader.get_balance("KRW-PENGU"))

    print(trader.sell("KRW-PENGU", 150))


if __name__ == "__main__":
    test()
