-- Script SQL para criar/atualizar a tabela signals no Supabase
-- Execute este script no SQL Editor do Supabase Dashboard

-- Criar a tabela signals se não existir
CREATE TABLE IF NOT EXISTS public.signals (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('COMPRA', 'VENDA')),
    entry_price DECIMAL(20, 8) NOT NULL,
    target_price DECIMAL(20, 8) NOT NULL,
    entry_time TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CONFIRMED', 'CLOSED', 'CANCELLED')),
    quality_score DECIMAL(10, 2) DEFAULT 0,
    signal_class TEXT,
    projection_percentage DECIMAL(10, 2) DEFAULT 0,
    confirmed_at TIMESTAMPTZ,
    confirmation_reasons TEXT DEFAULT '',
    confirmation_attempts INTEGER DEFAULT 0,
    btc_correlation DECIMAL(10, 4) DEFAULT 0,
    btc_trend TEXT DEFAULT 'NEUTRAL',
    trend_score DECIMAL(10, 2) DEFAULT 0,
    rsi_score DECIMAL(10, 2) DEFAULT 0,
    timeframe TEXT DEFAULT '1h',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Adicionar colunas que podem estar faltando (se a tabela já existir)
DO $$ 
BEGIN
    -- Adicionar btc_correlation se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'btc_correlation') THEN
        ALTER TABLE public.signals ADD COLUMN btc_correlation DECIMAL(10, 4) DEFAULT 0;
    END IF;
    
    -- Adicionar btc_trend se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'btc_trend') THEN
        ALTER TABLE public.signals ADD COLUMN btc_trend TEXT DEFAULT 'NEUTRAL';
    END IF;
    
    -- Adicionar projection_percentage se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'projection_percentage') THEN
        ALTER TABLE public.signals ADD COLUMN projection_percentage DECIMAL(10, 2) DEFAULT 0;
    END IF;
    
    -- Adicionar confirmed_at se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'confirmed_at') THEN
        ALTER TABLE public.signals ADD COLUMN confirmed_at TIMESTAMPTZ;
    END IF;
    
    -- Adicionar confirmation_reasons se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'confirmation_reasons') THEN
        ALTER TABLE public.signals ADD COLUMN confirmation_reasons TEXT DEFAULT '';
    END IF;
    
    -- Adicionar confirmation_attempts se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'confirmation_attempts') THEN
        ALTER TABLE public.signals ADD COLUMN confirmation_attempts INTEGER DEFAULT 0;
    END IF;
    
    -- Adicionar trend_score se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'trend_score') THEN
        ALTER TABLE public.signals ADD COLUMN trend_score DECIMAL(10, 2) DEFAULT 0;
    END IF;
    
    -- Adicionar rsi_score se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'rsi_score') THEN
        ALTER TABLE public.signals ADD COLUMN rsi_score DECIMAL(10, 2) DEFAULT 0;
    END IF;
    
    -- Adicionar timeframe se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'timeframe') THEN
        ALTER TABLE public.signals ADD COLUMN timeframe TEXT DEFAULT '1h';
    END IF;
    
    -- Adicionar updated_at se não existir
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'signals' AND column_name = 'updated_at') THEN
        ALTER TABLE public.signals ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON public.signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_type ON public.signals(type);
CREATE INDEX IF NOT EXISTS idx_signals_status ON public.signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON public.signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_confirmed_at ON public.signals(confirmed_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_type ON public.signals(symbol, type);

-- Criar trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_signals_updated_at ON public.signals;
CREATE TRIGGER update_signals_updated_at
    BEFORE UPDATE ON public.signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Habilitar RLS (Row Level Security) se necessário
ALTER TABLE public.signals ENABLE ROW LEVEL SECURITY;

-- Criar política para permitir acesso público (ajuste conforme necessário)
DROP POLICY IF EXISTS "Allow public access" ON public.signals;
CREATE POLICY "Allow public access" ON public.signals
    FOR ALL USING (true);

-- Comentários para documentação
COMMENT ON TABLE public.signals IS 'Tabela para armazenar sinais de trading';
COMMENT ON COLUMN public.signals.symbol IS 'Símbolo do par de trading (ex: BTCUSDT)';
COMMENT ON COLUMN public.signals.type IS 'Tipo do sinal: COMPRA ou VENDA';
COMMENT ON COLUMN public.signals.entry_price IS 'Preço de entrada do sinal';
COMMENT ON COLUMN public.signals.target_price IS 'Preço alvo do sinal';
COMMENT ON COLUMN public.signals.status IS 'Status do sinal: OPEN, CONFIRMED, CLOSED, CANCELLED';
COMMENT ON COLUMN public.signals.quality_score IS 'Pontuação de qualidade do sinal';
COMMENT ON COLUMN public.signals.signal_class IS 'Classificação do sinal (ELITE, PREMIUM, etc.)';
COMMENT ON COLUMN public.signals.projection_percentage IS 'Porcentagem de projeção do sinal';
COMMENT ON COLUMN public.signals.btc_correlation IS 'Correlação com BTC';
COMMENT ON COLUMN public.signals.btc_trend IS 'Tendência do BTC no momento do sinal';

-- Verificar a estrutura final da tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'signals'
ORDER BY ordinal_position;