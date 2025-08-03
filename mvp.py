import json
import os

import pyupbit
from dotenv import load_dotenv
from openai import OpenAI

from utils import get_my_balance, get_balance

load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
upbit_client = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)


df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")

prompt_system = """
You are an expert in Bitcoin investing. Tell me whether to buy, sell, or hold at the moment based on the chart data provided. Response in Json format.

Response Example:
{"decision": "buy", "reason": "some technical reason"}
{"decision": "sell", "reason": "some technical reason"}
{"decision": "hold", "reason": "some technical reason"}
"""

prompt_user = df.to_json()


client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt_system,
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt_user,
                }
            ],
        },
        {
            "id": "msg_688f51323de0819d9e040283283a1f460cf0aaf2950d14e2",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": '{\n  "decision": "hold",\n  "reason": "The recent chart data shows high volatility with rapid price increases followed by sharp drops. After a peak, the price appears to be consolidating around the 157-160M level with moderate volume and no clear breakout or breakdown signals. There is no strong bullish reversal or bearish continuation pattern; thus, it\'s prudent to hold and wait for more confirmation before making a new buy or sell decision."\n}',
                }
            ],
        },
    ],
    text={"format": {"type": "text"}},
)

response_text = response.to_dict()["output"][0]["content"][0]["text"]
response_data = json.loads(response_text)
decision = response_data["decision"]
reason = response_data["reason"]
balance = get_my_balance()
rate = 0.9995


print(f"Decision: {decision}")
print(f"Reason: {reason}")
print(f"Balance: {balance}")

if decision == "buy":
    if balance * rate < 5_000:
        print("Not enough balance")
        exit()
    print("Buy")
    print(upbit_client.buy_market_order("KRW-BTC", 5_000))
elif decision == "sell":
    print("Sell")
    print(upbit_client.sell_market_order("KRW-BTC", 5_000))
else:
    print("Hold")
