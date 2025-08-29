-- Script SQL para atualizar a tabela signals no Supabase
-- Execute este script no Supabase SQL Editor

-- Adicionar colunas que estão faltando na tabela signals
ALTER TABLE signals 
ADD COLUMN IF NOT EXISTS projection_percentage DECIMAL(8,2),
ADD COLUMN IF NOT EXISTS confirmation_reasons TEXT,
ADD COLUMN IF NOT EXISTS confirmation_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS btc_correlation DECIMAL(5,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS btc_trend VARCHAR(20) DEFAULT 'NEUTRAL',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Atualizar a coluna status para ter um valor padrão
ALTER TABLE signals 
ALTER COLUMN status SET DEFAULT 'CONFIRMED';

-- Adicionar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);
CREATE INDEX IF NOT EXISTS idx_signals_btc_trend ON signals(btc_trend);
CREATE INDEX IF NOT EXISTS idx_signals_quality_score ON signals(quality_score);

-- Verificar a estrutura atualizada
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'signals' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- Inserir um sinal de teste para verificar se está funcionando
INSERT INTO signals (
    symbol, 
    type, 
    entry_price, 
    target_price, 
    projection_percentage,
    quality_score, 
    signal_class, 
    status,
    confirmation_reasons,
    confirmation_attempts,
    btc_correlation,
    btc_trend
) VALUES (
    'BTCUSDT',
    'COMPRA',
    45000.00,
    47000.00,
    4.44,
    95.5,
    'ELITE',
    'CONFIRMED',
    'breakout_confirmed, volume_confirmed, btc_aligned',
    3,
    0.85,
    'BULLISH'
);

-- Verificar se o sinal foi inserido
SELECT * FROM signals WHERE symbol = 'BTCUSDT' ORDER BY created_at DESC LIMIT 1;