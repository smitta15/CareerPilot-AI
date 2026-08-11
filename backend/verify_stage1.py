import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000"


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def test_health():
    print_header("1. Testing Health Endpoint")

    try:
        r = requests.get(f"{BASE_URL}/")
        print("Status:", r.status_code)

        try:
            pprint(r.json())
        except Exception:
            print(r.text)

    except Exception as e:
        print("FAILED:", e)


def test_chat():
    print_header("2. Testing Search Workflow")

    payload = {
        "user_query": "Find backend internships"
    }

    try:
        r = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=120
        )

        print("Status:", r.status_code)

        if r.status_code == 200:
            data = r.json()
            print("\nThread ID:", data["thread_id"])

            print("\nResult:")
            pprint(data["result"])

            if "thread_id" in data:
                print("\nThread ID:", data["thread_id"])

            if "jobs" in data:
                print("\nJobs Found:", len(data["jobs"]))

                if len(data["jobs"]) > 0:
                    print("\nFirst Job:")
                    pprint(data["jobs"][0])

        else:
            print(r.text)

    except Exception as e:
        print("FAILED:", e)


def test_applications():
    print_header("3. Testing Application History")

    try:
        r = requests.get(f"{BASE_URL}/applications")

        print("Status:", r.status_code)

        try:
            pprint(r.json())
        except Exception:
            print(r.text)

    except Exception as e:
        print("FAILED:", e)


if __name__ == "__main__":

    print("\nStarting Stage-1 Verification...\n")

    test_health()
    test_chat()
    test_applications()

    print("\nVerification Finished.")