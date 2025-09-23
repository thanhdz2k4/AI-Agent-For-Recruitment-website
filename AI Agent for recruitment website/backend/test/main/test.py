import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwG9yqwJHcFy8cO1tBMRhadnYYMNe0vkKnmZsKAHNeW9B7dq0pz-qDoXcdaSzJvHl7e/exec"

rows = [
    {"predict": "Backend Developer", "status": "PASS"},
    {"predict": "Data Analyst", "status": "FAIL"},
    {"predict": "Blockchain Dev", "status": "PASS"}
]

payload = {
    "rows": rows,
    "predictCol": 3,  # tùy ý, có thể bỏ để mặc định
    "statusCol": 4,   # tùy ý, có thể bỏ để mặc định
    "startRow": 2     # tùy ý, có thể bỏ để mặc định
}

response = requests.post(WEB_APP_URL, json=payload)
print(response.text)
