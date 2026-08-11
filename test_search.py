import os
import requests
from dotenv import load_dotenv

load_dotenv()

headers = {
    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

params = {
    "query": "Software Engineer Intern",
    "page": "1",
    "num_pages": "1",
}

response = requests.get(
    "https://jsearch.p.rapidapi.com/search",
    headers=headers,
    params=params,
)

print(response.status_code)
print(response.text)