import requests
import json

# URL do endpoint de login
LOGIN_URL = "http://localhost:5000/api/auth/login"

# Credenciais de teste
credentials = {
    "username": "jonatasprojetos2013@gmail.com",
    "password": "admin123"
}

# Cabeçalhos da requisição
headers = {
    "Content-Type": "application/json"
}

print(f"Tentando login para o usuário: {credentials['username']}")

try:
    # Faz a requisição POST para o endpoint de login
    response = requests.post(LOGIN_URL, data=json.dumps(credentials), headers=headers)

    # Imprime o status code e a resposta
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Verifica se o login foi bem-sucedido (status 200 OK)
    if response.status_code == 200:
        print("Login bem-sucedido!")
    else:
        print("Login falhou.")

except requests.exceptions.ConnectionError as e:
    print(f"Erro de conexão: {e}. Certifique-se de que o servidor Flask está rodando em {LOGIN_URL}.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")