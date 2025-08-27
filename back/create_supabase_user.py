#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário no Supabase
"""

import os
import requests
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

def create_supabase_user():
    """
    Cria um usuário no Supabase via API
    """
    print("\n🔐 === CRIANDO USUÁRIO NO SUPABASE ===")
    
    # Verificar variáveis de ambiente
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"\n📋 CONFIGURAÇÃO:")
    print(f"   SUPABASE_URL: {supabase_url}")
    print(f"   SUPABASE_ANON_KEY: {supabase_anon_key[:20] if supabase_anon_key else 'NÃO DEFINIDA'}...")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Variáveis de ambiente não configuradas!")
        return False
    
    # Headers para Supabase
    headers = {
        'apikey': supabase_anon_key,
        'Authorization': f'Bearer {supabase_anon_key}',
        'Content-Type': 'application/json'
    }
    
    # Dados do usuário
    email = "jonatasprojetos2013@gmail.com"
    password = "admin123"
    
    print(f"\n👤 CRIANDO USUÁRIO:")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)}")
    
    # Tentar criar usuário
    try:
        signup_url = f"{supabase_url}/auth/v1/signup"
        print(f"\n📡 URL de registro: {signup_url}")
        
        payload = {
            "email": email,
            "password": password,
            "data": {
                "name": "Admin User",
                "role": "admin"
            }
        }
        
        print(f"\n📤 Enviando requisição de registro...")
        response = requests.post(
            signup_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"\n📥 RESPOSTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ USUÁRIO CRIADO COM SUCESSO!")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"   User Email: {data.get('user', {}).get('email', 'N/A')}")
            print(f"   Email Confirmed: {data.get('user', {}).get('email_confirmed_at', 'N/A')}")
            
            # Tentar fazer login imediatamente
            print(f"\n🔐 Testando login com o usuário criado...")
            return test_login(supabase_url, headers, email, password)
            
        elif response.status_code == 422:
            print(f"   ⚠️ USUÁRIO JÁ EXISTE!")
            print(f"   Resposta: {response.text}")
            
            # Se usuário já existe, tentar fazer login
            print(f"\n🔐 Testando login com usuário existente...")
            return test_login(supabase_url, headers, email, password)
            
        else:
            print(f"   ❌ ERRO AO CRIAR USUÁRIO!")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERRO DE CONEXÃO: {e}")
        return False
    except Exception as e:
        print(f"   ❌ ERRO INESPERADO: {e}")
        return False

def test_login(supabase_url, headers, email, password):
    """
    Testa o login após criar/verificar usuário
    """
    try:
        login_url = f"{supabase_url}/auth/v1/token?grant_type=password"
        
        payload = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            login_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"\n📥 RESULTADO DO LOGIN:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LOGIN FUNCIONANDO!")
            print(f"   Access Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"   ❌ LOGIN AINDA FALHA!")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERRO NO TESTE DE LOGIN: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando criação de usuário Supabase...")
    
    success = create_supabase_user()
    
    print(f"\n📊 === RESULTADO FINAL ===")
    if success:
        print(f"   ✅ USUÁRIO CRIADO E LOGIN FUNCIONANDO!")
        print(f"   🎯 Agora você pode testar o login no frontend")
        print(f"   📧 Email: jonatasprojetos2013@gmail.com")
        print(f"   🔑 Senha: admin123")
    else:
        print(f"   ❌ FALHA NA CRIAÇÃO/LOGIN DO USUÁRIO")
        print(f"   🔧 Verifique as configurações do Supabase")
    
    print(f"\n🔍 === FIM ===\n")