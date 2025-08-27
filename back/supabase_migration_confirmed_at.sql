
-- Migração para adicionar coluna confirmed_at à tabela signals
-- Execute este script no SQL Editor do Supabase

-- 1. Adicionar coluna confirmed_at
ALTER TABLE signals 
ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMPTZ;

-- 2. Atualizar registros existentes confirmados
UPDATE signals 
SET confirmed_at = created_at 
WHERE status = 'CONFIRMED' AND confirmed_at IS NULL;

-- 3. Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_signals_confirmed_at 
ON signals(confirmed_at) 
WHERE confirmed_at IS NOT NULL;

-- 4. Adicionar comentário à coluna
COMMENT ON COLUMN signals.confirmed_at IS 'Timestamp quando o sinal foi confirmado';

-- 5. Verificar resultado
SELECT 
    COUNT(*) as total_signals,
    COUNT(confirmed_at) as signals_with_confirmed_at,
    COUNT(*) - COUNT(confirmed_at) as signals_without_confirmed_at
FROM signals;

-- 6. Mostrar alguns registros para verificação
SELECT id, symbol, status, created_at, confirmed_at
FROM signals 
WHERE status = 'CONFIRMED'
ORDER BY confirmed_at DESC NULLS LAST
LIMIT 5;
