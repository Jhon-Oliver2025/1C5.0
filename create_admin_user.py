#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário admin no Supabase
"""

import os
import sys
import bcrypt
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Carregar variáveis de ambiente
load_dotenv()

def create_admin_user():
    """
    Cria o usuário admin no Supabase se não existir
    """
    print("🔧 Criando usuário admin no Supabase...")
    
    try:
        # Conectar ao Supabase
        database_url = os.getenv('SUPABASE_DATABASE_URL')
        if not database_url:
            print("❌ SUPABASE_DATABASE_URL não configurada")
            return False
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se a tabela users existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("📋 Criando tabela users...")
            cursor.execute("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Criar índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            
            conn.commit()
            print("✅ Tabela users criada com sucesso!")
        
        # Verificar se o usuário admin já existe
        cursor.execute("""
            SELECT * FROM users 
            WHERE email = %s OR username = %s;
        """, ('jonatasprojetos2013@gmail.com', 'admin'))
        
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"✅ Usuário admin já existe: {existing_user['username']} ({existing_user['email']})")
            
            # Verificar se precisa atualizar a senha
            password = 'admin123'
            stored_password = existing_user['password']
            
            # Verificar se a senha atual está correta
            if stored_password.startswith('$2b$'):
                password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
                if password_valid:
                    print("✅ Senha do admin está correta")
                else:
                    print("⚠️ Senha do admin precisa ser atualizada")
                    # Atualizar senha
                    new_password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute("""
                        UPDATE users 
                        SET password = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                    """, (new_password_hash, existing_user['id']))
                    conn.commit()
                    print("✅ Senha do admin atualizada")
            else:
                print("⚠️ Senha não está em formato hash, atualizando...")
                new_password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users 
                    SET password = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                """, (new_password_hash, existing_user['id']))
                conn.commit()
                print("✅ Senha do admin atualizada para formato hash")
                
            # Garantir que é admin e está ativo
            cursor.execute("""
                UPDATE users 
                SET is_admin = TRUE, status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (existing_user['id'],))
            conn.commit()
            print("✅ Status de admin confirmado")
            
        else:
            print("👤 Criando usuário admin...")
            
            # Gerar hash da senha
            password = 'admin123'
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Inserir usuário admin
            cursor.execute("""
                INSERT INTO users (username, email, password, is_admin, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, username, email;
            """, ('admin', 'jonatasprojetos2013@gmail.com', password_hash, True, 'active'))
            
            new_user = cursor.fetchone()
            conn.commit()
            
            print(f"✅ Usuário admin criado com sucesso!")
            print(f"   ID: {new_user['id']}")
            print(f"   Username: {new_user['username']}")
            print(f"   Email: {new_user['email']}")
            print(f"   Senha: admin123")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Configuração do usuário admin concluída!")
        print("\n📝 Credenciais para login:")
        print("   Email: jonatasprojetos2013@gmail.com")
        print("   Senha: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        print(f"❌ Tipo do erro: {type(e).__name__}")
        print(f"❌ URL do banco: {database_url[:50]}...")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Função principal
    """
    print("🔧 Script de Criação do Usuário Admin")
    print("=" * 50)
    
    # Verificar se as variáveis de ambiente estão configuradas
    database_url = os.getenv('SUPABASE_DATABASE_URL')
    if not database_url:
        print("❌ SUPABASE_DATABASE_URL não configurada")
        print("💡 Configure as variáveis de ambiente do Supabase primeiro")
        sys.exit(1)
    
    # Criar usuário admin
    if create_admin_user():
        print("\n✅ Script executado com sucesso!")
        print("🚀 Agora você pode fazer login em produção com as credenciais do admin")
    else:
        print("\n❌ Falha na execução do script")
        sys.exit(1)

if __name__ == '__main__':
    main()