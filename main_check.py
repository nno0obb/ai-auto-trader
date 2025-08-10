import json
import time
import traceback

from modules.log import get_logger
from modules.task import get_task
from modules.trader import get_trader
from modules.webhook import get_webhook


def run():
    try:
        task, trader, webhook, logger = get_task(), get_trader(), get_webhook(), get_logger()
        order_uuid = task.pop()
        order_data = trader.get_order_data(order_uuid)

        if order_data:
            if order_data["state"] == "wait":
                task.push(order_uuid)
            elif order_data["state"] == "cancel":
                logger.info("\n%s\n", json.dumps(order_data, indent=4))
                webhook.send_message(trader.get_webhook_message_about_buy_close(order_data))
            elif order_data["state"] == "done":
                logger.info("\n%s\n", json.dumps(order_data, indent=4))
                webhook.send_message(trader.get_webhook_message_about_sell_close(order_data))
        else:
            task.push(order_uuid)

    except Exception:
        traceback.print_exc()
    except KeyboardInterrupt:
        exit(0)


def main():
    epoch = 0
    while True:
        epoch += 1
        start_msg = f"### [CHECK] Epoch: {epoch} ###"
        end_msg = "-" * len(start_msg)
        print(start_msg)
        print()

        run()
        time.sleep(1)

        print(end_msg)
        print()


if __name__ == "__main__":
    main()
