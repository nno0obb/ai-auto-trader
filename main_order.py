import json
import time
import traceback
from math import ceil

from dotenv import load_dotenv

from modules.gpt import get_gpt
from modules.log import get_logger
from modules.task import get_task
from modules.trader import get_trader
from modules.webhook import get_webhook

load_dotenv()


DEBUG = True


def run():
    try:
        gpt, trader, task, webhook, logger = get_gpt(), get_trader(), get_task(), get_webhook(), get_logger()
        tickers = ["KRW-PENGU", "KRW-DOGE", "KRW-MOODENG"]  # 펭귄, 강아지, 하마
        for ticker in tickers:
            data = trader.get_data(ticker)
            gpt_answer = gpt.ask_with_data(data)
            if gpt_answer.decision == "buy":  # bid
                if trader.get_my_balance() > (5_000 * 1.0005):
                    buy_resp = trader.buy(ticker, 5_000)
                    buy_order_uuid = buy_resp.get("uuid")
                    task.push(buy_order_uuid)
                    logger.info("\n%s\n", json.dumps(buy_resp, indent=4))
                    webhook.send_message(trader.get_webhook_message_about_buy_open(buy_resp))

            elif gpt_answer.decision == "sell":  # ask
                balance = trader.get_balance(ticker)
                price = trader.get_current_price(ticker)
                volume = ceil(5_000 / price)
                if balance > volume:
                    sell_resp = trader.sell(ticker, volume)
                    sell_order_uuid = sell_resp.get("uuid")
                    task.push(sell_order_uuid)
                    logger.info("\n%s\n", json.dumps(sell_resp, indent=4))
                    webhook.send_message(trader.get_webhook_message_about_sell_open(sell_resp))

    except Exception:
        traceback.print_exc()
    except KeyboardInterrupt:
        exit(0)


def main():
    epoch = 0
    while True:
        epoch += 1
        start_msg = f"### [ORDER] Epoch: {epoch} ###"
        end_msg = "-" * len(start_msg)
        print(start_msg)
        print()

        run()
        time.sleep(1)

        print(end_msg)
        print()


if __name__ == "__main__":
    main()
