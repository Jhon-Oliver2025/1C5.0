#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar e corrigir problemas de 503 Service Unavailable e persistência de token
"""

import requests
import os
from dotenv import load_dotenv
import json
import time

# Carregar variáveis de ambiente
load_dotenv()

def test_backend_routes():
    """
    Testa as rotas do backend que estão retornando 503
    """
    print("\n🔍 === TESTE DAS ROTAS BACKEND ===")
    
    base_url = "https://1crypten.space"
    routes_to_test = [
        "/api/status",
        "/api/btc-signals/confirmed",
        "/api/btc-signals/pending",
        "/api/btc-signals/metrics",
        "/api/auth/login",
        "/api/signals",
        "/api/market-status"
    ]
    
    results = {}
    
    for route in routes_to_test:
        try:
            print(f"\n📡 Testando: {base_url}{route}")
            
            response = requests.get(
                f"{base_url}{route}",
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            results[route] = {
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'response_size': len(response.text),
                'content_type': response.headers.get('content-type', 'unknown')
            }
            
            if response.status_code == 200:
                print(f"   ✅ {route}: {response.status_code} - OK")
            elif response.status_code == 503:
                print(f"   ❌ {route}: {response.status_code} - Service Unavailable")
            else:
                print(f"   ⚠️ {route}: {response.status_code} - {response.reason}")
                
        except requests.exceptions.RequestException as e:
            results[route] = {
                'status_code': 'ERROR',
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ {route}: ERRO - {e}")
    
    return results

def test_login_flow():
    """
    Testa o fluxo completo de login
    """
    print(f"\n🔐 === TESTE DO FLUXO DE LOGIN ===")
    
    base_url = "https://1crypten.space"
    login_data = {
        "email": "jonatasprojetos2013@gmail.com",
        "password": "admin123"
    }
    
    try:
        # Fazer login
        print(f"\n📤 Fazendo login...")
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            timeout=10,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'token' in data or 'access_token' in data:
                token = data.get('token') or data.get('access_token')
                print(f"   ✅ Login sucesso! Token: {token[:20]}...")
                
                # Testar token em rota protegida
                print(f"\n🔒 Testando token em rota protegida...")
                
                auth_response = requests.get(
                    f"{base_url}/api/btc-signals/confirmed",
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10
                )
                
                print(f"   Status com token: {auth_response.status_code}")
                
                if auth_response.status_code == 200:
                    print(f"   ✅ Token válido!")
                    return {'success': True, 'token': token}
                else:
                    print(f"   ❌ Token inválido: {auth_response.text[:100]}")
                    return {'success': False, 'error': 'Token inválido'}
            else:
                print(f"   ❌ Login sem token na resposta")
                return {'success': False, 'error': 'Sem token na resposta'}
        else:
            print(f"   ❌ Login falhou: {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"   ❌ Erro no login: {e}")
        return {'success': False, 'error': str(e)}

def check_backend_health():
    """
    Verifica a saúde geral do backend
    """
    print(f"\n🏥 === VERIFICAÇÃO DE SAÚDE DO BACKEND ===")
    
    base_url = "https://1crypten.space"
    health_endpoints = [
        "/",
        "/status",
        "/api/health"
    ]
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: OK")
            else:
                print(f"   ❌ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: ERRO - {e}")

def generate_frontend_fix():
    """
    Gera código para corrigir persistência de token no frontend
    """
    print(f"\n🔧 === GERANDO CORREÇÃO PARA FRONTEND ===")
    
    fix_code = '''
// Correção para persistência de token no AuthContext
// Adicionar ao arquivo src/context/AuthContext.tsx

// 1. Salvar token no localStorage após login
const login = async (email: string, password: string) => {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      const data = await response.json();
      const token = data.token || data.access_token;
      
      if (token) {
        // Salvar no localStorage
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        
        // Atualizar estado
        setToken(token);
        setUser(data.user);
        setIsAuthenticated(true);
        
        console.log('✅ Login realizado e token salvo');
        return { success: true };
      }
    }
    
    throw new Error('Token não recebido');
  } catch (error) {
    console.error('❌ Erro no login:', error);
    return { success: false, error: error.message };
  }
};

// 2. Carregar token do localStorage na inicialização
useEffect(() => {
  const savedToken = localStorage.getItem('auth_token');
  const savedUser = localStorage.getItem('user_data');
  
  if (savedToken && savedUser) {
    try {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
      console.log('✅ Token restaurado do localStorage');
    } catch (error) {
      console.error('❌ Erro ao restaurar token:', error);
      logout();
    }
  }
  
  setLoading(false);
}, []);

// 3. Limpar localStorage no logout
const logout = () => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_data');
  setToken(null);
  setUser(null);
  setIsAuthenticated(false);
  console.log('🔐 Logout realizado');
};

// 4. Interceptor para adicionar token automaticamente
const apiCall = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('auth_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return fetch(url, {
    ...options,
    headers,
  });
};
'''
    
    print(f"\n📝 Código de correção gerado:")
    print(f"   - Persistência de token no localStorage")
    print(f"   - Restauração automática na inicialização")
    print(f"   - Interceptor para adicionar token nas requisições")
    print(f"   - Limpeza adequada no logout")
    
    return fix_code

def main():
    """
    Função principal
    """
    print("🚀 Iniciando diagnóstico completo...")
    
    # Teste 1: Verificar saúde do backend
    check_backend_health()
    
    # Teste 2: Testar rotas específicas
    route_results = test_backend_routes()
    
    # Teste 3: Testar fluxo de login
    login_result = test_login_flow()
    
    # Teste 4: Gerar correção para frontend
    frontend_fix = generate_frontend_fix()
    
    # Resumo final
    print(f"\n📊 === RESUMO DO DIAGNÓSTICO ===")
    
    # Contar rotas com problema
    failed_routes = [route for route, result in route_results.items() if not result.get('success', False)]
    working_routes = [route for route, result in route_results.items() if result.get('success', False)]
    
    print(f"\n🔍 ROTAS:")
    print(f"   ✅ Funcionando: {len(working_routes)}")
    print(f"   ❌ Com problema: {len(failed_routes)}")
    
    if failed_routes:
        print(f"\n❌ Rotas com problema:")
        for route in failed_routes:
            result = route_results[route]
            print(f"   - {route}: {result.get('status_code', 'ERROR')}")
    
    print(f"\n🔐 LOGIN:")
    if login_result.get('success'):
        print(f"   ✅ Login funcionando")
    else:
        print(f"   ❌ Login com problema: {login_result.get('error')}")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    if failed_routes:
        print(f"   1. Verificar logs do backend no Coolify")
        print(f"   2. Reiniciar containers se necessário")
        print(f"   3. Verificar inicialização do btc_signal_manager")
    
    if not login_result.get('success'):
        print(f"   4. Aplicar correção de persistência de token no frontend")
        print(f"   5. Verificar configuração do Supabase")
    
    print(f"\n🔍 === FIM DO DIAGNÓSTICO ===\n")

if __name__ == "__main__":
    main()