#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da API de admin em produção
"""

import requests
import json

def test_production_admin():
    """Testa a rota check-admin em produção"""
    
    print("🔍 Testando API de admin em produção...")
    print("📍 URL: https://1crypten.space")
    
    # Testar rota básica
    try:
        print("\n1. Testando rota básica...")
        response = requests.get("https://1crypten.space/api/")
        print(f"Status: {response.status_code}")
        if response.ok:
            print(f"Resposta: {response.json()}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na rota básica: {e}")
    
    # Testar check-admin sem token
    try:
        print("\n2. Testando check-admin sem token...")
        response = requests.get("https://1crypten.space/api/auth/check-admin")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro no check-admin sem token: {e}")
    
    # Testar check-admin com token fake
    try:
        print("\n3. Testando check-admin com token fake...")
        headers = {
            'Authorization': 'Bearer fake-token-123',
            'Content-Type': 'application/json'
        }
        response = requests.get("https://1crypten.space/api/auth/check-admin", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro no check-admin com token fake: {e}")
    
    # Testar login
    try:
        print("\n4. Testando login...")
        login_data = {
            'email': 'jonatasprojetos2013@gmail.com',
            'password': 'admin123'
        }
        response = requests.post("https://1crypten.space/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Login bem-sucedido! Token: {data.get('token', 'N/A')[:20]}...")
            
            # Testar check-admin com token real
            if 'token' in data:
                print("\n5. Testando check-admin com token real...")
                headers = {
                    'Authorization': f'Bearer {data["token"]}',
                    'Content-Type': 'application/json'
                }
                response = requests.get("https://1crypten.space/api/auth/check-admin", headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Resposta: {response.text}")
        else:
            print(f"Erro no login: {response.text}")
    except Exception as e:
        print(f"Erro no login: {e}")
    
    print("\n✅ Teste concluído!")

if __name__ == '__main__':
    test_production_admin()