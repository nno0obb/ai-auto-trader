import json
import time
import traceback
from math import ceil

import schedule
from dotenv import load_dotenv

from modules.gpt import get_gpt
from modules.log import get_logger
from modules.task import get_task
from modules.trader import get_trader
from modules.webhook import get_webhook

load_dotenv()

EPOCH = 0


def run():
    global EPOCH
    EPOCH += 1

    try:
        gpt, trader, task, webhook, logger = get_gpt(), get_trader(), get_task(), get_webhook(), get_logger()
        tickers = ["KRW-PENGU", "KRW-DOGE", "KRW-MOODENG"]  # 펭귄, 강아지, 하마

        start_msg = f"### [ORDER] Epoch: {EPOCH} ###"
        logger.info(start_msg)

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

        end_msg = "-" * len(start_msg)
        logger.info(end_msg)

    except Exception:
        traceback.print_exc()


def main():
    # schedule.every(1).minute.do(run)
    schedule.every(1).hour.do(run)

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            exit(0)


if __name__ == "__main__":
    main()
