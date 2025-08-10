import json
import os

# import sqlite3
from typing import Any

import pandas as pd
import pyupbit
import requests
import ta
from dotenv import load_dotenv
from openai import OpenAI

from schema import Answer

# Initialize SQLite database connection
# conn = sqlite3.connect("logs.db")
# cursor = conn.cursor()

# Create a table for logs if it doesn't exist
# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS logs (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#     message TEXT
# )
# """
# )
# conn.commit()


load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")


class GPT:
    def __init__(self):
        self.openai_client = OpenAI()
        self.system_prompt = "\n".join(
            [
                "You are an expert in cryptocurrency scalping (초단타) trading.",
                "Your strategy is to make quick profits from small price movements within minutes.",
                "Analyze the provided 1-minute OHLCV data and make rapid trading decisions.",
                "",
                "SCALPING STRATEGY RULES:",
                "🚀 PRIMARY GOAL: MAKE QUICK PROFITS! BE AGGRESSIVE!",
                "",
                "1. ENTRY SIGNALS (BUY) - LOOK FOR THESE ACTIVELY:",
                "   - Price above SMA5 or SMA10 (upward momentum)",
                "   - RSI oversold (<30) and starting to recover",
                "   - MACD bullish crossover or increasing histogram",
                "   - Price bouncing off Bollinger Band lower band",
                "   - Stochastic oversold (<20) and turning up",
                "   - Volume above average (>100% of volume SMA)",
                "   - Any combination of positive technical signals",
                "   ⭐ BE READY TO BUY ON TECHNICAL MOMENTUM!",
                "",
                "2. EXIT SIGNALS (SELL) - BUT DON'T BE TOO EAGER:",
                "   - Good profit: 2-5% gain (don't be greedy, but don't sell too early)",
                "   - RSI overbought (>70) with declining momentum",
                "   - Price hitting Bollinger Band upper band",
                "   - MACD bearish crossover or decreasing histogram",
                "   - Stochastic overbought (>80) and turning down",
                "   - Volume declining significantly (<80% of average)",
                "   - Stop loss: 2-3% loss (give some room for volatility)",
                "",
                "3. TRADING MINDSET:",
                "   - FAVOR BUY decisions when you have KRW available",
                "   - Only SELL when you have clear profit or strong loss",
                "   - HOLD only when truly uncertain",
                "   - Take calculated risks - this is scalping!",
                "",
                "4. DECISION PRIORITY (IMPORTANT):",
                "   - BUY: If any positive momentum signals (be optimistic!)",
                "   - SELL: Only if you have good profits (>2%) or significant losses (>2%)",
                "   - HOLD: Rarely - only when completely sideways",
                "",
                "Response in JSON format:",
                "",
                "Response Examples (FAVOR BUY WHEN POSSIBLE):",
                '{"decision": "buy", "reason": "3 green candles in a row with increasing volume, momentum building"}',
                '{"decision": "buy", "reason": "Price bounced off recent low, small volume increase, scalp opportunity"}',
                '{"decision": "buy", "reason": "Consolidation pattern breaking upward, good entry point"}',
                '{"decision": "buy", "reason": "Minor dip finished, showing signs of recovery, quick scalp"}',
                '{"decision": "sell", "reason": "Hit 3.2% profit target, volume declining, secure gains"}',
                '{"decision": "sell", "reason": "2.8% loss, clear downtrend, cut losses"}',
                '{"decision": "hold", "reason": "Completely flat movement, no clear direction"}',
            ]
        )

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def ask_with_data(self, data: Any) -> Answer:
        if isinstance(data, pd.DataFrame):
            data = data.to_string()  # JSON 대신 문자열 형태로 변환

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": f"""🚀 SCALPING ANALYSIS REQUEST 🚀

=== CURRENT TRADING DATA ===
{data}

=== SCALPING DECISION NEEDED ===
Analyze this data for QUICK SCALPING opportunities:

📊 TECHNICAL ANALYSIS (USE THESE INDICATORS):
- RSI: Is it oversold (<30), overbought (>70), or neutral?
- MACD: Is it bullish/bearish? Is momentum increasing/decreasing?
- Moving Averages: Is price above/below SMA5, SMA10?
- Bollinger Bands: Is price at upper/middle/lower band?
- Stochastic: Is it oversold/overbought/neutral?
- Volume: Is it above/below average? Any spikes?

💰 PROFIT/LOSS STATUS:
- If you own this coin: Is it profitable? How much % gain/loss?
- Should you take quick profits (1-3% target) or cut losses?

⚡ ENTRY/EXIT TIMING:
- Is this the right moment for a quick BUY scalp?
- Or should you SELL to take profits/cut losses?
- Is momentum building up or dying down?

Remember: This is SCALPING - quick in, quick out! Don't overthink, follow the momentum!""",
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "answer",
                    "schema": Answer.model_json_schema() | {"additionalProperties": False},
                    "strict": True,
                },
            },
        )
        response_text = response.choices[0].message.content
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

    def get_avg_buy_price(self, ticker: str) -> float:
        return self.trader.get_avg_buy_price(ticker)

    def get_fear_greed_index(self) -> dict:
        base_url = "https://api.alternative.me/fng/"
        api_url = base_url + "?limit=1"
        response = requests.get(api_url)
        response_data = response.json()["data"]
        fear_greed_index = response_data[0]
        return fear_greed_index

    def get_data(self, ticker: str) -> dict:
        # 초단타를 위한 상세한 데이터 수집
        current_price = self.get_current_price(ticker)
        avg_buy_price = self.get_avg_buy_price(ticker)
        balance = self.get_balance(ticker)
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
