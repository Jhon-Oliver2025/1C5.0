import requests
import json

url = "https://1crypten.space/api/auth/login"
headers = {"Content-Type": "application/json"}
data = {"username": "test@example.com", "password": "password123"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")