#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção do Usuário Admin no Supabase
Atualiza o usuário admin existente com os dados corretos
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class FixAdminUser:
    """
    Corrige o usuário admin no Supabase
    """
    
    def __init__(self):
        """Inicializa a correção"""
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
    
    def get_current_admin(self) -> dict:
        """Busca o usuário admin atual"""
        try:
            print("🔍 Buscando usuário admin atual...")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users?email=eq.jonatasprojetos2013@gmail.com",
                headers=self.headers
            )
            
            if response.status_code == 200:
                users = response.json()
                
                if users:
                    admin = users[0]
                    print("✅ Usuário admin encontrado:")
                    print(f"   - ID: {admin.get('id')}")
                    print(f"   - Email: {admin.get('email')}")
                    print(f"   - Username: {admin.get('username')}")
                    print(f"   - Is Admin: {admin.get('is_admin')}")
                    print(f"   - Password: {'Definida' if admin.get('password') else 'Não definida'}")
                    return admin
                else:
                    print("❌ Usuário admin não encontrado")
                    return None
            else:
                print(f"❌ Erro ao buscar admin: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar admin: {e}")
            return None
    
    def update_admin_user(self, admin_id: str) -> bool:
        """Atualiza o usuário admin com os dados corretos"""
        try:
            print("\n🔧 Atualizando usuário admin...")
            
            # Dados corretos do admin
            update_data = {
                'username': 'admin',
                'password': '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.',
                'is_admin': True
            }
            
            # Atualizar usando o ID
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/users?id=eq.{admin_id}",
                headers=self.headers,
                json=update_data
            )
            
            print(f"Status da atualização: {response.status_code}")
            
            if response.status_code in [200, 204]:
                print("✅ Usuário admin atualizado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao atualizar admin: {response.status_code}")
                print(f"❌ Resposta: {response.text}")
                
                # Tentar atualização campo por campo
                print("\n🔄 Tentando atualização campo por campo...")
                
                # Atualizar username
                username_response = requests.patch(
                    f"{self.supabase_url}/rest/v1/users?id=eq.{admin_id}",
                    headers=self.headers,
                    json={'username': 'admin'}
                )
                
                if username_response.status_code in [200, 204]:
                    print("✅ Username atualizado")
                else:
                    print(f"❌ Erro ao atualizar username: {username_response.status_code}")
                
                # Atualizar is_admin
                admin_response = requests.patch(
                    f"{self.supabase_url}/rest/v1/users?id=eq.{admin_id}",
                    headers=self.headers,
                    json={'is_admin': True}
                )
                
                if admin_response.status_code in [200, 204]:
                    print("✅ is_admin atualizado")
                else:
                    print(f"❌ Erro ao atualizar is_admin: {admin_response.status_code}")
                
                # Atualizar password
                password_response = requests.patch(
                    f"{self.supabase_url}/rest/v1/users?id=eq.{admin_id}",
                    headers=self.headers,
                    json={'password': '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.'}
                )
                
                if password_response.status_code in [200, 204]:
                    print("✅ Password atualizado")
                    return True
                else:
                    print(f"❌ Erro ao atualizar password: {password_response.status_code}")
                    return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar admin: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_admin_fixed(self) -> bool:
        """Verifica se o admin foi corrigido"""
        try:
            print("\n🔍 Verificando correção...")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users?email=eq.jonatasprojetos2013@gmail.com",
                headers=self.headers
            )
            
            if response.status_code == 200:
                users = response.json()
                
                if users:
                    admin = users[0]
                    print("✅ Usuário admin após correção:")
                    print(f"   - Email: {admin.get('email')}")
                    print(f"   - Username: {admin.get('username')}")
                    print(f"   - Is Admin: {admin.get('is_admin')}")
                    print(f"   - Password Hash: {admin.get('password', '')[:20]}...")
                    
                    # Verificar se todos os campos estão corretos
                    checks = {
                        'username': admin.get('username') == 'admin',
                        'is_admin': admin.get('is_admin') == True,
                        'password': admin.get('password') == '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.'
                    }
                    
                    print("\n📋 Verificação dos campos:")
                    for field, is_correct in checks.items():
                        status = "✅" if is_correct else "❌"
                        print(f"   {status} {field}: {'Correto' if is_correct else 'Incorreto'}")
                    
                    all_correct = all(checks.values())
                    
                    if all_correct:
                        print("\n🎉 Usuário admin totalmente corrigido!")
                        return True
                    else:
                        print("\n⚠️ Alguns campos ainda precisam de correção")
                        return False
                else:
                    print("❌ Usuário admin não encontrado")
                    return False
            else:
                print(f"❌ Erro ao verificar admin: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return False
    
    def run_fix(self) -> bool:
        """Executa a correção completa"""
        try:
            print("🔧 CORREÇÃO DO USUÁRIO ADMIN")
            print("=" * 40)
            
            # 1. Buscar admin atual
            admin = self.get_current_admin()
            if not admin:
                print("❌ Não foi possível encontrar o usuário admin")
                return False
            
            admin_id = admin.get('id')
            if not admin_id:
                print("❌ ID do usuário admin não encontrado")
                return False
            
            # 2. Atualizar admin
            if not self.update_admin_user(admin_id):
                print("❌ Falha ao atualizar usuário admin")
                return False
            
            # 3. Verificar correção
            if not self.verify_admin_fixed():
                print("❌ Verificação falhou")
                return False
            
            print("\n" + "=" * 40)
            print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n📋 CREDENCIAIS DE LOGIN:")
            print("   Email: jonatasprojetos2013@gmail.com")
            print("   Senha: admin123")
            print("\n✅ Usuário admin configurado corretamente")
            print("✅ Sistema pronto para login em produção")
            print("\n🔗 Acesse: https://1crypten.space/login")
            print("=" * 40)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na correção: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Função principal"""
    fixer = FixAdminUser()
    
    if fixer.run_fix():
        print("\n🚀 Sistema pronto para uso!")
        print("\n📝 Próximos passos:")
        print("1. Acesse https://1crypten.space/login")
        print("2. Faça login com jonatasprojetos2013@gmail.com / admin123")
        print("3. Verifique se o CRM está funcionando")
        sys.exit(0)
    else:
        print("\n❌ Falha na correção")
        sys.exit(1)

if __name__ == '__main__':
    main()