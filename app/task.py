import redis


class Task:
    def __init__(self):
        self.queue_name = "order_uuids"
        self.broker = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        self.consumer = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    def push(self, message: str):
        self.broker.lpush(self.queue_name, message)

    def pop(self) -> str:
        return self.consumer.brpop(self.queue_name, timeout=0)

    def size(self) -> int:
        return self.broker.llen(self.queue_name)
