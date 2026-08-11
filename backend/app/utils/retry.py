import time

from google.genai.errors import ServerError


def retry_llm(func, retries=5, delay=3):

    last_exception = None

    for attempt in range(retries):

        try:
            return func()

        except ServerError as e:

            last_exception = e

            print(f"\nRetry {attempt+1}/{retries}")

            print(e)

            time.sleep(delay)

    raise last_exception