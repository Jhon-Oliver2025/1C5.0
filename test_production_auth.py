#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar autenticação em produção
Testa tanto o sistema local quanto o Supabase
"""

import requests
import json
from datetime import datetime

def test_production_auth():
    """
    Testa autenticação em produção
    """
    print("🔍 TESTE DE AUTENTICAÇÃO EM PRODUÇÃO")
    print("=" * 50)
    
    # URLs para teste
    base_url = "https://1crypten.space"
    auth_url = f"{base_url}/api/auth/login"
    
    # Credenciais do admin
    credentials = {
        "username": "jonatasprojetos2013@gmail.com",
        "password": "admin123"
    }
    
    print(f"🌐 URL de teste: {auth_url}")
    print(f"👤 Usuário: {credentials['username']}")
    print(f"🔑 Senha: {'*' * len(credentials['password'])}")
    print()
    
    try:
        # 1. Testar se o endpoint existe
        print("1️⃣ Testando conectividade...")
        response = requests.get(f"{base_url}/api/", timeout=10)
        print(f"   Status da API base: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API está online")
        else:
            print(f"   ⚠️ API retornou: {response.status_code}")
        
        print()
        
        # 2. Testar login
        print("2️⃣ Testando login...")
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TestScript/1.0'
        }
        
        response = requests.post(
            auth_url,
            json=credentials,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers de resposta: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Resposta JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Resposta texto: {response.text[:500]}")
        
        if response.status_code == 200:
            print("   ✅ Login bem-sucedido!")
            return True
        elif response.status_code == 401:
            print("   ❌ Erro 401: Credenciais inválidas ou sistema não configurado")
        elif response.status_code == 503:
            print("   ⚠️ Erro 503: Supabase não disponível")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text}")
        
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Timeout: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False

def test_backend_health():
    """
    Testa saúde geral do backend
    """
    print("\n🏥 TESTE DE SAÚDE DO BACKEND")
    print("=" * 50)
    
    base_url = "https://1crypten.space"
    
    endpoints = [
        "/",
        "/api/",
        "/api/signals",
        "/api/auth/verify"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"🔍 Testando: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ OK")
            elif response.status_code == 401:
                print("   🔐 Requer autenticação (normal)")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()

def main():
    """
    Função principal
    """
    print(f"🚀 DIAGNÓSTICO DE PRODUÇÃO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    # Teste de saúde
    test_backend_health()
    
    # Teste de autenticação
    auth_success = test_production_auth()
    
    print("\n📊 RESUMO")
    print("=" * 50)
    
    if auth_success:
        print("✅ Sistema funcionando corretamente")
        print("🎯 Login em produção: SUCESSO")
    else:
        print("❌ Problemas identificados")
        print("🔧 Ações necessárias:")
        print("   1. Verificar configuração do Supabase")
        print("   2. Confirmar variáveis de ambiente")
        print("   3. Verificar Site URL no Supabase")
        print("   4. Redeploy se necessário")
    
    print(f"\n⏰ Teste concluído: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()