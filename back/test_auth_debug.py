#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para testar autenticação Supabase localmente
"""

import os
import requests
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

def test_supabase_auth():
    """
    Testa a autenticação com Supabase diretamente
    """
    print("\n🔍 === TESTE DE AUTENTICAÇÃO SUPABASE ===")
    
    # Verificar variáveis de ambiente
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"\n📋 VARIÁVEIS DE AMBIENTE:")
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
    
    # Credenciais de teste
    email = "jonatasprojetos2013@gmail.com"
    password = "admin123"
    
    print(f"\n🔐 TESTANDO LOGIN:")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)}")
    
    # Tentar login
    try:
        login_url = f"{supabase_url}/auth/v1/token?grant_type=password"
        print(f"\n📡 URL de login: {login_url}")
        
        payload = {
            "email": email,
            "password": password
        }
        
        print(f"\n📤 Enviando requisição...")
        response = requests.post(
            login_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"\n📥 RESPOSTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LOGIN SUCESSO!")
            print(f"   Access Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"   User Email: {data.get('user', {}).get('email', 'N/A')}")
            return True
        else:
            print(f"   ❌ LOGIN FALHOU!")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERRO DE CONEXÃO: {e}")
        return False
    except Exception as e:
        print(f"   ❌ ERRO INESPERADO: {e}")
        return False

def test_backend_endpoint():
    """
    Testa o endpoint do backend local
    """
    print(f"\n🌐 === TESTE DO BACKEND LOCAL ===")
    
    try:
        # Testar se o backend está rodando
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        print(f"   ✅ Backend rodando: {response.status_code}")
        
        # Testar login no backend
        login_data = {
            "email": "jonatasprojetos2013@gmail.com",
            "password": "admin123"
        }
        
        print(f"\n🔐 Testando login no backend...")
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ LOGIN NO BACKEND SUCESSO!")
            return True
        else:
            print(f"   ❌ LOGIN NO BACKEND FALHOU!")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Backend não está rodando em localhost:5000")
        return False
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes de debug...")
    
    # Teste 1: Supabase direto
    supabase_ok = test_supabase_auth()
    
    # Teste 2: Backend local
    backend_ok = test_backend_endpoint()
    
    print(f"\n📊 === RESUMO DOS TESTES ===")
    print(f"   Supabase Direto: {'✅ OK' if supabase_ok else '❌ FALHOU'}")
    print(f"   Backend Local: {'✅ OK' if backend_ok else '❌ FALHOU'}")
    
    if supabase_ok and not backend_ok:
        print(f"\n🎯 DIAGNÓSTICO: Supabase funciona, mas backend tem problema!")
    elif not supabase_ok and not backend_ok:
        print(f"\n🎯 DIAGNÓSTICO: Problema nas credenciais ou configuração Supabase!")
    elif supabase_ok and backend_ok:
        print(f"\n🎯 DIAGNÓSTICO: Tudo funcionando! Problema pode ser no frontend.")
    else:
        print(f"\n🎯 DIAGNÓSTICO: Situação inesperada - investigar mais.")
    
    print(f"\n🔍 === FIM DOS TESTES ===\n")