#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica estrutura existente no Supabase
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class CheckSupabaseStructure:
    """
    Verifica estrutura existente no Supabase
    """
    
    def __init__(self):
        """Inicializa a verificação"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_anon_key:
            print("❌ Variáveis SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórias")
            sys.exit(1)
        
        self.headers = {
            'apikey': self.supabase_anon_key,
            'Authorization': f'Bearer {self.supabase_anon_key}',
            'Content-Type': 'application/json'
        }
    
    def check_table(self, table_name: str) -> dict:
        """Verifica se uma tabela existe e sua estrutura"""
        try:
            print(f"\n🔍 Verificando tabela '{table_name}'...")
            
            # Tentar buscar dados da tabela
            response = requests.get(
                f"{self.supabase_url}/rest/v1/{table_name}?limit=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tabela '{table_name}' existe com {len(data)} registros")
                
                if data:
                    print(f"📋 Estrutura da primeira linha:")
                    for key, value in data[0].items():
                        print(f"   - {key}: {type(value).__name__}")
                
                return {
                    'exists': True,
                    'status_code': response.status_code,
                    'data_count': len(data),
                    'sample_data': data[0] if data else None
                }
            else:
                print(f"❌ Tabela '{table_name}' não encontrada: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
                return {
                    'exists': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            print(f"❌ Erro ao verificar '{table_name}': {e}")
            return {
                'exists': False,
                'error': str(e)
            }
    
    def check_all_tables(self) -> dict:
        """Verifica todas as tabelas possíveis"""
        try:
            print("🔍 VERIFICANDO ESTRUTURA DO SUPABASE")
            print("=" * 50)
            
            # Lista de tabelas para verificar
            tables_to_check = [
                'users',
                'signals',
                'trading_signals',
                'system_config',
                'auth_tokens',
                'bot_config',
                'notifications',
                'crm_activities',
                'user_sessions'
            ]
            
            results = {}
            
            for table in tables_to_check:
                results[table] = self.check_table(table)
            
            # Resumo
            print("\n" + "=" * 50)
            print("📊 RESUMO DAS TABELAS")
            print("=" * 50)
            
            existing_tables = []
            missing_tables = []
            
            for table, result in results.items():
                if result['exists']:
                    existing_tables.append(table)
                    print(f"✅ {table}")
                else:
                    missing_tables.append(table)
                    print(f"❌ {table}")
            
            print(f"\n📈 Estatísticas:")
            print(f"   - Tabelas existentes: {len(existing_tables)}")
            print(f"   - Tabelas ausentes: {len(missing_tables)}")
            
            if existing_tables:
                print(f"\n✅ Tabelas disponíveis: {', '.join(existing_tables)}")
            
            if missing_tables:
                print(f"\n❌ Tabelas ausentes: {', '.join(missing_tables)}")
            
            return results
            
        except Exception as e:
            print(f"❌ Erro na verificação geral: {e}")
            return {}
    
    def check_admin_user(self) -> bool:
        """Verifica especificamente o usuário admin"""
        try:
            print("\n👤 VERIFICANDO USUÁRIO ADMIN")
            print("-" * 30)
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users?email=eq.jonatasprojetos2013@gmail.com",
                headers=self.headers
            )
            
            if response.status_code == 200:
                users = response.json()
                
                if users:
                    admin = users[0]
                    print(f"✅ Usuário admin encontrado:")
                    print(f"   - ID: {admin.get('id')}")
                    print(f"   - Email: {admin.get('email')}")
                    print(f"   - Is Admin: {admin.get('is_admin')}")
                    print(f"   - Password: {'Definida' if admin.get('password') else 'Não definida'}")
                    
                    # Verificar se pode fazer login
                    expected_hash = '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.'
                    if admin.get('password') == expected_hash:
                        print(f"   ✅ Senha correta (admin123)")
                    else:
                        print(f"   ⚠️ Senha diferente do esperado")
                    
                    return True
                else:
                    print("❌ Usuário admin não encontrado")
                    return False
            else:
                print(f"❌ Erro ao buscar admin: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar admin: {e}")
            return False
    
    def run_check(self) -> dict:
        """Executa verificação completa"""
        try:
            # 1. Verificar todas as tabelas
            results = self.check_all_tables()
            
            # 2. Verificar usuário admin
            admin_ok = self.check_admin_user()
            
            print("\n" + "=" * 50)
            print("🎯 CONCLUSÃO")
            print("=" * 50)
            
            if results.get('users', {}).get('exists') and admin_ok:
                print("✅ Sistema de usuários: FUNCIONANDO")
            else:
                print("❌ Sistema de usuários: PROBLEMA")
            
            if results.get('signals', {}).get('exists'):
                print("✅ Sistema de sinais: DISPONÍVEL")
            else:
                print("❌ Sistema de sinais: INDISPONÍVEL")
            
            print("\n📝 Recomendações:")
            print("1. Use as tabelas existentes")
            print("2. Adapte o backend para a estrutura atual")
            print("3. Crie apenas as tabelas ausentes necessárias")
            
            return results
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return {}

def main():
    """Função principal"""
    checker = CheckSupabaseStructure()
    results = checker.run_check()
    
    if results:
        print("\n🚀 Verificação concluída!")
    else:
        print("\n❌ Falha na verificação")

if __name__ == '__main__':
    main()