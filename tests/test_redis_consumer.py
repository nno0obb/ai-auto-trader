import redis


def test():
    r = redis.Redis(host="localhost", port=6379, db=0)
    queue = "test_queue"

    while True:
        message = r.brpop(queue, timeout=0)
        print(message)


if __name__ == "__main__":
    test()
