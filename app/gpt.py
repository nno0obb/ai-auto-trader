import json
import os
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")


class Answer(BaseModel):
    decision: str
    reason: str


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


def test():
    gpt = GPT()
    print(gpt.get_system_prompt())
    print(Answer.model_json_schema())


if __name__ == "__main__":
    test()
