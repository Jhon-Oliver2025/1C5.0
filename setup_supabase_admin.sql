-- Script para configurar usuário admin no Supabase
-- Execute este script no SQL Editor do Supabase

-- 1. Criar tabela users se não existir
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- 3. Criar função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 4. Criar trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Inserir usuário admin (senha: admin123)
-- Hash bcrypt da senha 'admin123': $2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.
INSERT INTO users (username, email, password, is_admin, status)
VALUES (
    'admin',
    'jonatasprojetos2013@gmail.com',
    '$2b$12$tZZmsFsR8xOWif4Uk6148OmZIzvwbhjyBqV5aWEmCt.G4F639Fl0.',
    TRUE,
    'active'
)
ON CONFLICT (email) DO UPDATE SET
    username = EXCLUDED.username,
    password = EXCLUDED.password,
    is_admin = TRUE,
    status = 'active',
    updated_at = CURRENT_TIMESTAMP;

-- 6. Verificar se o usuário foi criado
SELECT 
    id,
    username,
    email,
    is_admin,
    status,
    created_at
FROM users 
WHERE email = 'jonatasprojetos2013@gmail.com';

-- 7. Criar tabela de tokens de autenticação
CREATE TABLE IF NOT EXISTS auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 8. Criar índices para tokens
CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires_at ON auth_tokens(expires_at);

-- 9. Criar tabela de sinais de trading
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('COMPRA', 'VENDA')),
    entry_price DECIMAL(20, 8) NOT NULL,
    target_price DECIMAL(20, 8),
    projection_percentage DECIMAL(5, 2),
    quality_score DECIMAL(5, 2),
    signal_class VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected', 'expired')),
    rsi DECIMAL(5, 2),
    trend_score DECIMAL(5, 2),
    entry_score DECIMAL(5, 2),
    rsi_score DECIMAL(5, 2),
    pattern_score DECIMAL(5, 2),
    btc_correlation DECIMAL(5, 4),
    btc_trend VARCHAR(20),
    trend_timeframe VARCHAR(10),
    entry_timeframe VARCHAR(10),
    confirmed_at TIMESTAMP,
    confirmation_reasons TEXT,
    confirmation_attempts INTEGER DEFAULT 0,
    generation_reasons JSONB,
    trend_analysis JSONB,
    entry_analysis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Criar índices para sinais
CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_signals_status ON trading_signals(status);
CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_trading_signals_signal_type ON trading_signals(signal_type);

-- 11. Criar trigger para atualizar updated_at em trading_signals
DROP TRIGGER IF EXISTS update_trading_signals_updated_at ON trading_signals;
CREATE TRIGGER update_trading_signals_updated_at
    BEFORE UPDATE ON trading_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 12. Criar tabela de configurações do bot
CREATE TABLE IF NOT EXISTS bot_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Criar índice para configurações
CREATE INDEX IF NOT EXISTS idx_bot_config_key ON bot_config(key);

-- 14. Criar trigger para atualizar updated_at em bot_config
DROP TRIGGER IF EXISTS update_bot_config_updated_at ON bot_config;
CREATE TRIGGER update_bot_config_updated_at
    BEFORE UPDATE ON bot_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 15. Inserir configurações padrão
INSERT INTO bot_config (key, value, description)
VALUES 
    ('system_status', 'active', 'Status geral do sistema'),
    ('scan_interval', '60', 'Intervalo de escaneamento em segundos'),
    ('quality_score_minimum', '65.0', 'Pontuação mínima para sinais'),
    ('max_pairs', '100', 'Número máximo de pares para análise'),
    ('target_percentage_min', '6.0', 'Porcentagem mínima de alvo')
ON CONFLICT (key) DO NOTHING;

-- 16. Verificar estrutura criada
SELECT 
    'users' as table_name,
    COUNT(*) as record_count
FROM users
UNION ALL
SELECT 
    'auth_tokens' as table_name,
    COUNT(*) as record_count
FROM auth_tokens
UNION ALL
SELECT 
    'trading_signals' as table_name,
    COUNT(*) as record_count
FROM trading_signals
UNION ALL
SELECT 
    'bot_config' as table_name,
    COUNT(*) as record_count
FROM bot_config;

-- 17. Mostrar usuário admin criado
SELECT 
    'USUÁRIO ADMIN CRIADO COM SUCESSO!' as status,
    username,
    email,
    'admin123' as password,
    is_admin,
    status as user_status,
    created_at
FROM users 
WHERE email = 'jonatasprojetos2013@gmail.com';

-- Fim do script
-- Execute este script no SQL Editor do Supabase para configurar tudo automaticamente