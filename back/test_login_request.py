import requests
import json
import requests

print("Iniciando teste de login...")

url = "http://localhost:5000/api/auth/login"
headers = {"Content-Type": "application/json"}
data = {"email": "jonatasprojetos2013@gmail.com", "password": "admin123"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError as e:
    print(f"Erro de conexão: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")