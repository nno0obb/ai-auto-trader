import traceback
from pprint import pprint

from dotenv import load_dotenv

from app.gpt import GPT
from app.trader import Trader

load_dotenv()


DEBUG = True


def run():
    try:
        gpt, trader = GPT(), Trader()
        tickers = ["KRW-PENGU", "KRW-DOGE", "KRW-MOODENG"]  # 펭귄, 강아지, 하마
        wait_order_uuids = []
        for ticker in tickers:
            data = trader.get_data(ticker)
            gpt_answer = gpt.ask_with_data(data)
            if gpt_answer.decision == "buy":  # bid
                if DEBUG:
                    print(f"[Ticker] {ticker}")
                    print("[Decision] Buy")
                    print(f"[Reason] {gpt_answer.reason}")

                if trader.get_my_balance() < 5_000:
                    if DEBUG:
                        print("[Error] Not enough balance to buy")
                        print()
                    else:
                        print(f"{ticker} | Buy | Volume: 0 KRW | Count: 0 | Error: Insufficient balance")
                    continue

                buy_resp = trader.buy(ticker, 5_000)  # 5000원 만큼씩 매수
                buy_order_uuid = buy_resp.get("uuid")
                wait_order_uuids.append(buy_order_uuid)
                if buy_order_uuid:
                    # 매수한 코인 개수 계산 (5000원 / 현재가격)
                    current_price = trader.get_current_price(ticker)
                    estimated_count = 5_000 / current_price
                    if DEBUG:
                        pprint(buy_resp)
                    else:
                        print(f"{ticker} | Buy | Volume: 5,000 KRW | Count: {estimated_count:.2f} | Success")
                else:
                    if DEBUG:
                        print(f"[Error] Buy order failed: {buy_resp}")
                    else:
                        print(f"{ticker} | Buy | Volume: 0 KRW | Count: 0 | Error: Order failed")
            elif gpt_answer.decision == "sell":  # ask
                if DEBUG:
                    print(f"[Ticker] {ticker}")
                    print("[Decision] Sell")
                    print(f"[Reason] {gpt_answer.reason}")

                balance = trader.get_balance(ticker)
                price = trader.get_current_price(ticker)
                # 최소 주문금액 5,000원을 만족하는 수량으로 계산
                min_volume = 5_000 / price
                volume = min(balance, max(balance, min_volume))  # 보유량과 최소량 중 적절한 값

                if balance > 0:
                    total_value = balance * price
                    if total_value >= 5_000:  # 전체 보유량이 5,000원 이상이면 전체 매도
                        sell_resp = trader.sell(ticker, balance)
                        if sell_resp.get("uuid"):
                            if DEBUG:
                                pprint(sell_resp)
                            else:
                                print(
                                    f"{ticker} | Sell | Volume: {total_value:.0f} KRW | Count: {balance:.2f} | Success"
                                )
                        else:
                            if DEBUG:
                                print(f"[Error] Sell order failed: {sell_resp}")
                            else:
                                print(f"{ticker} | Sell | Volume: 0 KRW | Count: 0 | Error: Order failed")
                    else:
                        # 5,000원 미만이면 매도 불가
                        if DEBUG:
                            print(f"[Info] Small position value: {total_value:.0f} KRW")
                            print(f"[Error] Cannot sell - insufficient volume for minimum order")
                        else:
                            print(
                                f"{ticker} | Sell | Volume: {total_value:.0f} KRW | Count: {balance:.2f} | Error: Insufficient volume"
                            )
                else:
                    if DEBUG:
                        print("[Info] No balance to sell")
                    else:
                        print(f"{ticker} | Sell | Volume: 0 KRW | Count: 0 | Error: No balance")
            elif gpt_answer.decision == "hold":
                if DEBUG:
                    print(f"[Ticker] {ticker}")
                    print("[Decision] Hold")
                    print(f"[Reason] {gpt_answer.reason}")
                else:
                    print(f"{ticker} | Hold | Volume: 0 KRW | Count: 0 | No action")

            if DEBUG:
                print()
    except Exception:
        traceback.print_exc()


def main():
    iteration_count = 1
    for epoch in range(iteration_count):
        print(f"### Epoch {epoch + 1} / {iteration_count} ###")
        print()
        run()
        print("-" * 100)
        print()


if __name__ == "__main__":
    main()
