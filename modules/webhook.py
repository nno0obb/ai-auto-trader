import os
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()


@lru_cache
def get_webhook():
    return Webhook()


class Webhook:
    def __init__(self):
        self.webhook_url = os.getenv("WEBHOOK_URL")

    def send_message(self, message: str) -> bool:
        response = requests.post(self.webhook_url, json={"content": message})
        return response.status_code == requests.codes.no_content


def test():
    webhook = Webhook()
    print(webhook.send_message("test"))


if __name__ == "__main__":
    test()
