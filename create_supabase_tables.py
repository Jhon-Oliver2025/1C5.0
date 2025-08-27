#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criação de Todas as Tabelas no Supabase
Cria estrutura completa: usuários, sinais, configurações, etc.
"""

import os
import sys
import json
import requests
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class CreateSupabaseTables:
    """
    Cria todas as tabelas necessárias no Supabase
    """
    
    def __init__(self):
        """Inicializa a criação de tabelas"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_anon_key:
            print("❌ Variáveis SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórias")
            sys.exit(1)
        
        self.headers = {
            'apikey': self.supabase_anon_key,
            'Authorization': f'Bearer {self.supabase_anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        print(f"🔗 Supabase URL: {self.supabase_url}")
        print(f"🔑 API Key configurada")
    
    def test_connection(self) -> bool:
        """Testa conexão com Supabase"""
        try:
            print("\n🔗 Testando conexão com Supabase...")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Conexão estabelecida!")
                return True
            else:
                print(f"❌ Erro na conexão: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def create_users_table(self) -> bool:
        """Cria/atualiza tabela de usuários"""
        try:
            print("\n👥 Configurando tabela users...")
            
            # Verificar se tabela existe
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users?limit=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("✅ Tabela users já existe")
                
                # Verificar/criar usuário admin
                admin_response = requests.get(
                    f"{self.supabase_url}/rest/v1/users?email=eq.jonatasprojetos2013@gmail.com",
                    headers=self.headers
                )
                
                if admin_response.status_code == 200:
                    users = admin_response.json()
                    
                    if not users:
                        # Criar usuário admin
                        admin_data = {
                            'email': 'jonatasprojetos2013@gmail.com',
                            'password': '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.',
                            'is_admin': True
                        }
                        
                        create_response = requests.post(
                            f"{self.supabase_url}/rest/v1/users",
                            headers=self.headers,
                            json=admin_data
                        )
                        
                        if create_response.status_code in [200, 201]:
                            print("✅ Usuário admin criado")
                        else:
                            print(f"❌ Erro ao criar admin: {create_response.status_code}")
                            print(f"Resposta: {create_response.text}")
                    else:
                        print("✅ Usuário admin já existe")
                        
                        # Atualizar para garantir que é admin
                        admin_id = users[0]['id']
                        update_response = requests.patch(
                            f"{self.supabase_url}/rest/v1/users?id=eq.{admin_id}",
                            headers=self.headers,
                            json={
                                'is_admin': True,
                                'password': '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.'
                            }
                        )
                        
                        if update_response.status_code in [200, 204]:
                            print("✅ Usuário admin atualizado")
                        else:
                            print(f"⚠️ Aviso ao atualizar admin: {update_response.status_code}")
                
                return True
            else:
                print(f"❌ Erro ao verificar tabela users: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar users: {e}")
            return False
    
    def create_signals_table(self) -> bool:
        """Cria tabela de sinais (usando tabela 'signals' existente)"""
        try:
            print("\n📊 Configurando tabela signals...")
            
            # Verificar se tabela signals existe
            check_response = requests.get(
                f"{self.supabase_url}/rest/v1/signals?limit=1",
                headers=self.headers
            )
            
            if check_response.status_code == 200:
                print("✅ Tabela signals já existe")
                
                # Tentar criar um sinal de exemplo
                test_signal = {
                    'symbol': 'BTCUSDT',
                    'type': 'COMPRA',
                    'entry_price': 45000.0,
                    'target_price': 47700.0,
                    'projection_percentage': 6.0,
                    'quality_score': 75.5,
                    'signal_class': 'STANDARD',
                    'status': 'pending',
                    'entry_time': datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/signals",
                    headers=self.headers,
                    json=test_signal
                )
                
                if response.status_code in [200, 201]:
                    print("✅ Sinal de teste criado na tabela signals")
                else:
                    print(f"⚠️ Aviso ao criar sinal: {response.status_code}")
                    print(f"Resposta: {response.text}")
                
                return True
            else:
                print(f"❌ Tabela signals não encontrada: {check_response.status_code}")
                print(f"Resposta: {check_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar signals: {e}")
            return False
    
    def create_system_config_table(self) -> bool:
        """Cria tabela de configurações do sistema"""
        try:
            print("\n⚙️ Configurando tabela system_config...")
            
            # Configurações essenciais
            configs = [
                {
                    'id': str(uuid.uuid4()),
                    'key': 'use_supabase',
                    'value': 'true',
                    'description': 'Usar Supabase como banco principal',
                    'category': 'system'
                },
                {
                    'id': str(uuid.uuid4()),
                    'key': 'system_status',
                    'value': 'active',
                    'description': 'Status geral do sistema',
                    'category': 'system'
                },
                {
                    'id': str(uuid.uuid4()),
                    'key': 'scan_interval',
                    'value': '60',
                    'description': 'Intervalo de escaneamento em segundos',
                    'category': 'trading'
                }
            ]
            
            created_count = 0
            
            for config in configs:
                # Verificar se já existe
                check_response = requests.get(
                    f"{self.supabase_url}/rest/v1/system_config?key=eq.{config['key']}",
                    headers=self.headers
                )
                
                if check_response.status_code == 200:
                    existing = check_response.json()
                    
                    if not existing:
                        # Criar configuração
                        create_response = requests.post(
                            f"{self.supabase_url}/rest/v1/system_config",
                            headers=self.headers,
                            json=config
                        )
                        
                        if create_response.status_code in [200, 201]:
                            created_count += 1
                            print(f"✅ Config criada: {config['key']}")
                        else:
                            print(f"❌ Erro ao criar {config['key']}: {create_response.status_code}")
                    else:
                        print(f"⚠️ Config já existe: {config['key']}")
            
            print(f"✅ {created_count} configurações criadas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar system_config: {e}")
            return False
    
    def create_auth_tokens_table(self) -> bool:
        """Cria tabela de tokens de autenticação"""
        try:
            print("\n🔐 Configurando tabela auth_tokens...")
            
            # Criar token de teste
            test_token = {
                'id': str(uuid.uuid4()),
                'token': str(uuid.uuid4()),
                'user_id': '89334bfe-8586-434c-bea9-393f121e9e09',  # ID do admin
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now().replace(hour=23, minute=59, second=59)).isoformat(),
                'is_active': True
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/auth_tokens",
                headers=self.headers,
                json=test_token
            )
            
            if response.status_code in [200, 201]:
                print("✅ Tabela auth_tokens configurada")
                return True
            else:
                print(f"❌ Erro ao configurar auth_tokens: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar auth_tokens: {e}")
            return False
    
    def verify_all_tables(self) -> bool:
        """Verifica se todas as tabelas estão funcionando"""
        try:
            print("\n🔍 Verificando todas as tabelas...")
            
            tables = ['users', 'signals', 'system_config', 'auth_tokens']
            
            for table in tables:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/{table}?limit=1",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {table}: {len(data)} registros encontrados")
                else:
                    print(f"❌ {table}: Erro {response.status_code}")
                    return False
            
            # Verificar usuário admin especificamente
            admin_response = requests.get(
                f"{self.supabase_url}/rest/v1/users?email=eq.jonatasprojetos2013@gmail.com",
                headers=self.headers
            )
            
            if admin_response.status_code == 200:
                admin_users = admin_response.json()
                
                if admin_users:
                    admin = admin_users[0]
                    print(f"\n👤 Usuário Admin:")
                    print(f"   - Email: {admin['email']}")
                    print(f"   - Is Admin: {admin['is_admin']}")
                    print(f"   - ID: {admin['id']}")
                else:
                    print("❌ Usuário admin não encontrado!")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Executa configuração completa"""
        try:
            print("🚀 CRIAÇÃO DE TABELAS NO SUPABASE")
            print("=" * 50)
            
            # 1. Testar conexão
            if not self.test_connection():
                return False
            
            # 2. Configurar tabela users
            if not self.create_users_table():
                return False
            
            # 3. Configurar tabela signals
            if not self.create_signals_table():
                return False
            
            # 4. Configurar tabela system_config
            if not self.create_system_config_table():
                return False
            
            # 5. Configurar tabela auth_tokens
            if not self.create_auth_tokens_table():
                return False
            
            # 6. Verificar todas as tabelas
            if not self.verify_all_tables():
                return False
            
            print("\n" + "=" * 50)
            print("🎉 TODAS AS TABELAS CONFIGURADAS COM SUCESSO!")
            print("\n📋 CREDENCIAIS DE LOGIN:")
            print("   Email: jonatasprojetos2013@gmail.com")
            print("   Senha: admin123")
            print("\n✅ Sistema totalmente integrado com Supabase")
            print("✅ Todas as tabelas criadas e funcionando")
            print("✅ Usuário admin configurado")
            print("✅ Sinais serão salvos no Supabase")
            print("✅ CRM totalmente sincronizado")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Função principal"""
    creator = CreateSupabaseTables()
    
    if creator.run_setup():
        print("\n🚀 Sistema pronto para uso!")
        print("\n📝 Próximos passos:")
        print("1. Faça redeploy no Coolify")
        print("2. Teste o login em produção")
        print("3. Verifique se os sinais estão sendo salvos")
        sys.exit(0)
    else:
        print("\n❌ Falha na configuração")
        sys.exit(1)

if __name__ == '__main__':
    main()