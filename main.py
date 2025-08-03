from pprint import pprint

from dotenv import load_dotenv

from app import GPT, Trader

load_dotenv()


def run():
    try:
        gpt, trader = GPT(), Trader()
        tickers = ["KRW-PENGU", "KRW-DOGE", "KRW-MOODENG"]  # 펭귄, 강아지, 하마
        for ticker in tickers:
            data = trader.get_ohlcv(ticker, count=100, interval="minute1")
            gpt_answer = gpt.ask_with_data(data)
            if gpt_answer.decision == "buy":
                print(f"Ticker: {ticker}")
                print("Decision: Buy")
                print(f"Reason: {gpt_answer.reason}")
                buy_resp = trader.buy(ticker, 5_000)  # 5000원 만큼씩 매수
                pprint(buy_resp)
            elif gpt_answer.decision == "sell":
                print(f"Ticker: {ticker}")
                print("Decision: Sell")
                print(f"Reason: {gpt_answer.reason}")
                pengu_balance = trader.get_balance(ticker)
                pengu_price = trader.get_current_price(ticker)
                pengu_volume = 5_000 // pengu_price + 1
                if pengu_balance >= pengu_volume:
                    sell_resp = trader.sell(ticker, pengu_volume)
                    pprint(sell_resp)
            elif gpt_answer.decision == "hold":
                print(f"Ticker: {ticker}")
                print("Decision: Hold")
                print(f"Reason: {gpt_answer.reason}")
            print()
    except Exception as exc:
        print(exc.with_traceback())


def main():
    iteration_count = 10
    for epoch in range(iteration_count):
        print(f"### Epoch {epoch + 1} / {iteration_count} ###")
        print()
        run()
        print("-" * 100)
        print()


if __name__ == "__main__":
    main()
