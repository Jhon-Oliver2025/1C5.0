#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar conexão com o servidor Flask
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Suprimir warnings de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_health_endpoint():
    """Testa o endpoint de health check"""
    print("🔍 Testando endpoint de health check...")
    
    try:
        response = requests.get(
            "http://localhost:5000/api/health",
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"⏰ Timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_login_endpoint():
    """Testa o endpoint de login"""
    print("\n🔐 Testando endpoint de login...")
    
    try:
        data = {
            "email": "jonatasprojetos2013@gmail.com",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"⏰ Timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes de conexão...")
    
    # Testar health check primeiro
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Se health check funcionar, testar login
        test_login_endpoint()
    else:
        print("❌ Servidor não está respondendo ao health check")
    
    print("\n✅ Testes concluídos.")