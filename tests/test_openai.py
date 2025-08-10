from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def test():
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        input="Write a one-sentence bedtime story about a unicorn.",
    )

    pprint(response.output_text)


if __name__ == "__main__":
    test()
