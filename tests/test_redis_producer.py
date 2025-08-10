from uuid import uuid4

import redis


def test():
    r = redis.Redis(host="localhost", port=6379, db=0)
    queue = "test_queue"
    message = f"test_message_{uuid4()}"

    resp = r.lpush(queue, message)
    print(resp)


if __name__ == "__main__":
    test()
