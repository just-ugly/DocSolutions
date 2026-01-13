import requests


def dify_request(question: str):
    DIFY_API_KEY = "app-1IwfITLttFa7sNpXP26AN3YN"
    DIFY_URL = "https://api.dify.ai/v1/workflows/run"

    HEADERS = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "question": question
        },
        "response_mode": "blocking",
        "user": "human-user"
    }

    response = requests.post(DIFY_URL, json=payload, headers=HEADERS)
    result = response.json()

    answer = result["data"]["outputs"].get("answer")
    return answer