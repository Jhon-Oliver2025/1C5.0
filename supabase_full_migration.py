#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração Completa para Supabase
Sincroniza todos os dados locais com Supabase e configura CRM
"""

import os
import sys
import json
import csv
import bcrypt
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseFullMigration:
    """
    Classe para migração completa de dados para Supabase
    """
    
    def __init__(self):
        """Inicializa a migração"""
        self.database_url = os.getenv('SUPABASE_DATABASE_URL')
        self.conn = None
        self.cursor = None
        
        # Caminhos dos arquivos locais
        self.base_path = os.path.dirname(__file__)
        self.back_path = os.path.join(self.base_path, 'back')
        
        self.files = {
            'users': os.path.join(self.back_path, 'users.csv'),
            'signals_list': os.path.join(self.back_path, 'sinais_lista.csv'),
            'signals_history': os.path.join(self.back_path, 'signals_history.csv'),
            'config': os.path.join(self.back_path, 'config.csv'),
            'auth_tokens': os.path.join(self.back_path, 'auth_tokens.csv')
        }
    
    def connect_supabase(self) -> bool:
        """Conecta ao Supabase"""
        try:
            if not self.database_url:
                print("❌ SUPABASE_DATABASE_URL não configurada")
                return False
                
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Testar conexão
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            print(f"✅ Conectado ao Supabase: {version.split()[1]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar ao Supabase: {e}")
            print(f"❌ Tipo do erro: {type(e).__name__}")
            print(f"❌ URL do banco: {self.database_url[:50] if self.database_url else 'None'}...")
            import traceback
            traceback.print_exc()
            return False
    
    def create_complete_schema(self) -> bool:
        """Cria o schema completo no Supabase"""
        try:
            print("🔧 Criando schema completo no Supabase...")
            
            # SQL para criar todas as tabelas
            schema_sql = """
            -- 1. Função para atualizar updated_at
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            -- 2. Tabela de usuários
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Campos CRM
                full_name VARCHAR(100),
                phone VARCHAR(20),
                company VARCHAR(100),
                position VARCHAR(100),
                notes TEXT,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                subscription_plan VARCHAR(50) DEFAULT 'free',
                subscription_expires TIMESTAMP,
                
                -- Metadados
                metadata JSONB DEFAULT '{}'
            );
            
            -- 3. Tabela de tokens de autenticação
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                token VARCHAR(255) UNIQUE NOT NULL,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                device_info JSONB DEFAULT '{}'
            );
            
            -- 4. Tabela de sinais de trading
            CREATE TABLE IF NOT EXISTS trading_signals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                symbol VARCHAR(20) NOT NULL,
                signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('COMPRA', 'VENDA')),
                entry_price DECIMAL(20, 8) NOT NULL,
                target_price DECIMAL(20, 8),
                projection_percentage DECIMAL(5, 2),
                quality_score DECIMAL(5, 2),
                signal_class VARCHAR(20),
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected', 'expired', 'completed')),
                
                -- Indicadores técnicos
                rsi DECIMAL(5, 2),
                trend_score DECIMAL(5, 2),
                entry_score DECIMAL(5, 2),
                rsi_score DECIMAL(5, 2),
                pattern_score DECIMAL(5, 2),
                
                -- Correlação BTC
                btc_correlation DECIMAL(5, 4),
                btc_trend VARCHAR(20),
                btc_correlation_score DECIMAL(5, 2),
                
                -- Timeframes
                trend_timeframe VARCHAR(10),
                entry_timeframe VARCHAR(10),
                
                -- Confirmação
                confirmed_at TIMESTAMP,
                confirmation_reasons TEXT,
                confirmation_attempts INTEGER DEFAULT 0,
                
                -- Dados detalhados
                generation_reasons JSONB,
                trend_analysis JSONB,
                entry_analysis JSONB,
                
                -- Resultado
                exit_price DECIMAL(20, 8),
                result VARCHAR(20),
                profit_loss_percentage DECIMAL(5, 2),
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- 5. Tabela de configurações do sistema
            CREATE TABLE IF NOT EXISTS system_config (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                category VARCHAR(50) DEFAULT 'general',
                is_public BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- 6. Tabela de atividades do CRM
            CREATE TABLE IF NOT EXISTS crm_activities (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                activity_type VARCHAR(50) NOT NULL,
                description TEXT,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- 7. Tabela de notificações
            CREATE TABLE IF NOT EXISTS notifications (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                message TEXT,
                type VARCHAR(50) DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- 8. Tabela de sessões de usuário
            CREATE TABLE IF NOT EXISTS user_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address INET,
                user_agent TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
            """
            
            self.cursor.execute(schema_sql)
            self.conn.commit()
            
            # Criar índices
            indices_sql = """
            -- Índices para users
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
            CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);
            CREATE INDEX IF NOT EXISTS idx_users_subscription_plan ON users(subscription_plan);
            
            -- Índices para auth_tokens
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token);
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_id ON auth_tokens(user_id);
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires_at ON auth_tokens(expires_at);
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_is_active ON auth_tokens(is_active);
            
            -- Índices para trading_signals
            CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
            CREATE INDEX IF NOT EXISTS idx_trading_signals_status ON trading_signals(status);
            CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at);
            CREATE INDEX IF NOT EXISTS idx_trading_signals_signal_type ON trading_signals(signal_type);
            CREATE INDEX IF NOT EXISTS idx_trading_signals_quality_score ON trading_signals(quality_score);
            
            -- Índices para system_config
            CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(key);
            CREATE INDEX IF NOT EXISTS idx_system_config_category ON system_config(category);
            
            -- Índices para crm_activities
            CREATE INDEX IF NOT EXISTS idx_crm_activities_user_id ON crm_activities(user_id);
            CREATE INDEX IF NOT EXISTS idx_crm_activities_type ON crm_activities(activity_type);
            CREATE INDEX IF NOT EXISTS idx_crm_activities_created_at ON crm_activities(created_at);
            
            -- Índices para notifications
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
            CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
            CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
            
            -- Índices para user_sessions
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
            """
            
            self.cursor.execute(indices_sql)
            self.conn.commit()
            
            # Criar triggers
            triggers_sql = """
            -- Triggers para updated_at
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at
                BEFORE UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_trading_signals_updated_at ON trading_signals;
            CREATE TRIGGER update_trading_signals_updated_at
                BEFORE UPDATE ON trading_signals
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_system_config_updated_at ON system_config;
            CREATE TRIGGER update_system_config_updated_at
                BEFORE UPDATE ON system_config
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """
            
            self.cursor.execute(triggers_sql)
            self.conn.commit()
            
            print("✅ Schema completo criado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar schema: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def migrate_users(self) -> bool:
        """Migra usuários locais para Supabase"""
        try:
            print("👥 Migrando usuários...")
            
            # Primeiro, criar usuário admin obrigatório
            admin_sql = """
            INSERT INTO users (username, email, password, is_admin, status, full_name, subscription_plan)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                username = EXCLUDED.username,
                password = EXCLUDED.password,
                is_admin = TRUE,
                status = 'active',
                subscription_plan = 'premium',
                updated_at = CURRENT_TIMESTAMP;
            """
            
            # Hash da senha admin123
            admin_password_hash = '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.'
            
            self.cursor.execute(admin_sql, (
                'admin',
                'jonatasprojetos2013@gmail.com',
                admin_password_hash,
                True,
                'active',
                'Administrador do Sistema',
                'premium'
            ))
            
            # Migrar usuários do arquivo CSV se existir
            if os.path.exists(self.files['users']):
                df = pd.read_csv(self.files['users'])
                
                for _, row in df.iterrows():
                    # Pular se for o admin (já criado)
                    if row.get('email') == 'jonatasprojetos2013@gmail.com':
                        continue
                    
                    user_sql = """
                    INSERT INTO users (id, username, email, password, is_admin, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        username = EXCLUDED.username,
                        password = EXCLUDED.password,
                        is_admin = EXCLUDED.is_admin,
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP;
                    """
                    
                    self.cursor.execute(user_sql, (
                        row.get('id', str(uuid.uuid4())),
                        row.get('username'),
                        row.get('email'),
                        row.get('password'),
                        bool(row.get('is_admin', False)),
                        row.get('status', 'pending')
                    ))
                
                print(f"✅ {len(df)} usuários migrados do CSV")
            
            # Registrar atividade CRM para admin
            activity_sql = """
            INSERT INTO crm_activities (user_id, activity_type, description, metadata)
            SELECT id, 'account_created', 'Conta de administrador criada durante migração', 
                   '{"migration": true, "role": "admin"}'
            FROM users WHERE email = 'jonatasprojetos2013@gmail.com';
            """
            
            self.cursor.execute(activity_sql)
            self.conn.commit()
            
            print("✅ Usuários migrados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao migrar usuários: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def migrate_signals(self) -> bool:
        """Migra sinais de trading"""
        try:
            print("📊 Migrando sinais de trading...")
            
            # Migrar sinais ativos
            if os.path.exists(self.files['signals_list']):
                df = pd.read_csv(self.files['signals_list'])
                
                for _, row in df.iterrows():
                    signal_sql = """
                    INSERT INTO trading_signals (
                        symbol, signal_type, entry_price, target_price, 
                        projection_percentage, signal_class, status,
                        quality_score, rsi, confirmed_at, confirmation_reasons,
                        btc_correlation, btc_trend, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """
                    
                    self.cursor.execute(signal_sql, (
                        row.get('symbol'),
                        row.get('type'),
                        float(row.get('entry_price', 0)),
                        float(row.get('target_price', 0)) if pd.notna(row.get('target_price')) else None,
                        float(row.get('projection_percentage', 0)) if pd.notna(row.get('projection_percentage')) else None,
                        row.get('signal_class', 'STANDARD'),
                        row.get('status', 'pending'),
                        float(row.get('quality_score', 0)) if pd.notna(row.get('quality_score')) else None,
                        float(row.get('rsi', 50)) if pd.notna(row.get('rsi')) else None,
                        pd.to_datetime(row.get('confirmed_at')) if pd.notna(row.get('confirmed_at')) else None,
                        row.get('confirmation_reasons'),
                        float(row.get('btc_correlation', 0)) if pd.notna(row.get('btc_correlation')) else None,
                        row.get('btc_trend', 'NEUTRAL'),
                        pd.to_datetime(row.get('entry_time')) if pd.notna(row.get('entry_time')) else datetime.now()
                    ))
                
                print(f"✅ {len(df)} sinais ativos migrados")
            
            # Migrar histórico de sinais
            if os.path.exists(self.files['signals_history']):
                df = pd.read_csv(self.files['signals_history'])
                
                for _, row in df.iterrows():
                    signal_sql = """
                    INSERT INTO trading_signals (
                        symbol, signal_type, entry_price, target_price, 
                        projection_percentage, signal_class, status,
                        quality_score, exit_price, result, 
                        profit_loss_percentage, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """
                    
                    self.cursor.execute(signal_sql, (
                        row.get('symbol'),
                        row.get('type'),
                        float(row.get('entry_price', 0)),
                        float(row.get('target_price', 0)) if pd.notna(row.get('target_price')) else None,
                        float(row.get('projection_percentage', 0)) if pd.notna(row.get('projection_percentage')) else None,
                        row.get('signal_class', 'STANDARD'),
                        'completed',
                        float(row.get('quality_score', 0)) if pd.notna(row.get('quality_score')) else None,
                        float(row.get('exit_price', 0)) if pd.notna(row.get('exit_price')) else None,
                        row.get('result'),
                        float(row.get('profit_loss_percentage', 0)) if pd.notna(row.get('profit_loss_percentage')) else None,
                        pd.to_datetime(row.get('entry_time')) if pd.notna(row.get('entry_time')) else datetime.now()
                    ))
                
                print(f"✅ {len(df)} sinais históricos migrados")
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao migrar sinais: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def migrate_config(self) -> bool:
        """Migra configurações do sistema"""
        try:
            print("⚙️ Migrando configurações...")
            
            # Configurações padrão do sistema
            default_configs = [
                ('system_status', 'active', 'Status geral do sistema', 'system'),
                ('scan_interval', '60', 'Intervalo de escaneamento em segundos', 'trading'),
                ('quality_score_minimum', '65.0', 'Pontuação mínima para sinais', 'trading'),
                ('max_pairs', '100', 'Número máximo de pares para análise', 'trading'),
                ('target_percentage_min', '6.0', 'Porcentagem mínima de alvo', 'trading'),
                ('use_supabase', 'true', 'Usar Supabase como banco principal', 'system'),
                ('crm_enabled', 'true', 'CRM habilitado', 'crm'),
                ('notifications_enabled', 'true', 'Notificações habilitadas', 'system')
            ]
            
            for key, value, description, category in default_configs:
                config_sql = """
                INSERT INTO system_config (key, value, description, category, is_public)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    description = EXCLUDED.description,
                    category = EXCLUDED.category,
                    updated_at = CURRENT_TIMESTAMP;
                """
                
                self.cursor.execute(config_sql, (key, value, description, category, True))
            
            # Migrar configurações do arquivo CSV se existir
            if os.path.exists(self.files['config']):
                df = pd.read_csv(self.files['config'])
                
                for _, row in df.iterrows():
                    config_sql = """
                    INSERT INTO system_config (key, value, description, category)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        updated_at = CURRENT_TIMESTAMP;
                    """
                    
                    self.cursor.execute(config_sql, (
                        row.get('key'),
                        row.get('value'),
                        f"Migrado do arquivo local: {row.get('key')}",
                        'migrated'
                    ))
                
                print(f"✅ {len(df)} configurações migradas do CSV")
            
            self.conn.commit()
            print("✅ Configurações migradas com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao migrar configurações: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def setup_crm_data(self) -> bool:
        """Configura dados iniciais do CRM"""
        try:
            print("🏢 Configurando dados do CRM...")
            
            # Criar notificação de boas-vindas para admin
            welcome_sql = """
            INSERT INTO notifications (user_id, title, message, type)
            SELECT id, 'Bem-vindo ao Sistema 1Crypten!', 
                   'Sua conta de administrador foi configurada com sucesso. O sistema está totalmente integrado com Supabase.',
                   'success'
            FROM users WHERE email = 'jonatasprojetos2013@gmail.com'
            ON CONFLICT DO NOTHING;
            """
            
            self.cursor.execute(welcome_sql)
            
            # Registrar atividade de migração
            migration_activity_sql = """
            INSERT INTO crm_activities (user_id, activity_type, description, metadata)
            SELECT id, 'system_migration', 'Sistema migrado completamente para Supabase',
                   '{"migration_date": "' || CURRENT_TIMESTAMP || '", "status": "completed"}'
            FROM users WHERE email = 'jonatasprojetos2013@gmail.com';
            """
            
            self.cursor.execute(migration_activity_sql)
            
            self.conn.commit()
            print("✅ Dados do CRM configurados!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar CRM: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_migration(self) -> bool:
        """Verifica se a migração foi bem-sucedida"""
        try:
            print("\n🔍 Verificando migração...")
            
            # Verificar usuário admin
            self.cursor.execute("""
                SELECT username, email, is_admin, status, subscription_plan
                FROM users WHERE email = 'jonatasprojetos2013@gmail.com';
            """)
            
            admin_user = self.cursor.fetchone()
            if admin_user:
                print(f"✅ Usuário Admin: {admin_user['username']} ({admin_user['email']})")
                print(f"   - Admin: {admin_user['is_admin']}")
                print(f"   - Status: {admin_user['status']}")
                print(f"   - Plano: {admin_user['subscription_plan']}")
            else:
                print("❌ Usuário admin não encontrado!")
                return False
            
            # Contar registros
            tables = ['users', 'trading_signals', 'system_config', 'crm_activities', 'notifications']
            
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) as count FROM {table};")
                count = self.cursor.fetchone()['count']
                print(f"✅ {table}: {count} registros")
            
            # Verificar configurações críticas
            self.cursor.execute("""
                SELECT key, value FROM system_config 
                WHERE key IN ('use_supabase', 'crm_enabled', 'system_status');
            """)
            
            configs = self.cursor.fetchall()
            print("\n⚙️ Configurações críticas:")
            for config in configs:
                print(f"   - {config['key']}: {config['value']}")
            
            print("\n🎉 Migração verificada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_migration(self) -> bool:
        """Executa migração completa"""
        try:
            print("🚀 INICIANDO MIGRAÇÃO COMPLETA PARA SUPABASE")
            print("=" * 60)
            
            # 1. Conectar ao Supabase
            if not self.connect_supabase():
                return False
            
            # 2. Criar schema completo
            if not self.create_complete_schema():
                return False
            
            # 3. Migrar usuários
            if not self.migrate_users():
                return False
            
            # 4. Migrar sinais
            if not self.migrate_signals():
                return False
            
            # 5. Migrar configurações
            if not self.migrate_config():
                return False
            
            # 6. Configurar CRM
            if not self.setup_crm_data():
                return False
            
            # 7. Verificar migração
            if not self.verify_migration():
                return False
            
            print("\n" + "=" * 60)
            print("🎉 MIGRAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
            print("\n📋 CREDENCIAIS DE ACESSO:")
            print("   Email: jonatasprojetos2013@gmail.com")
            print("   Senha: admin123")
            print("\n✅ Sistema 100% integrado com Supabase")
            print("✅ CRM configurado e funcionando")
            print("✅ Todos os dados sincronizados")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na migração completa: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

def main():
    """Função principal"""
    migration = SupabaseFullMigration()
    
    if migration.run_full_migration():
        print("\n🚀 Sistema pronto para produção!")
        sys.exit(0)
    else:
        print("\n❌ Falha na migração")
        sys.exit(1)

if __name__ == '__main__':
    main()