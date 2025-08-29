#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o salvamento de sinais no Supabase
Testa se a integração está funcionando corretamente
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Adicionar o diretório back ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

# Carregar variáveis de ambiente
load_dotenv()

try:
    from api_routes.auth_supabase import SupabaseAuth
except ImportError as e:
    print(f"❌ Erro ao importar SupabaseAuth: {e}")
    sys.exit(1)

def test_supabase_connection():
    """
    Testa a conexão com o Supabase
    """
    print("🔍 Testando conexão com Supabase...")
    
    # Criar instância do SupabaseAuth
    supabase_auth = SupabaseAuth()
    
    if not supabase_auth.is_available:
        print("❌ Supabase não está disponível")
        print("💡 Verifique as variáveis de ambiente:")
        print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
        print(f"   SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY')[:20] if os.getenv('SUPABASE_ANON_KEY') else 'Não definida'}...")
        return False
    
    print("✅ Supabase está disponível")
    return supabase_auth

def test_signal_save(supabase_auth):
    """
    Testa o salvamento de um sinal no Supabase
    """
    print("\n🧪 Testando salvamento de sinal...")
    
    # Criar sinal de teste
    test_signal = {
        'symbol': 'BTCUSDT',
        'type': 'COMPRA',
        'entry_price': 45000.0,
        'target_price': 47000.0,
        'projection_percentage': 4.44,
        'quality_score': 95.5,
        'signal_class': 'ELITE',
        'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'confirmed_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'confirmation_reasons': 'breakout_confirmed, volume_confirmed, btc_aligned',
        'confirmation_attempts': 3,
        'btc_correlation': 0.85,
        'btc_trend': 'BULLISH'
    }
    
    print(f"📊 Sinal de teste: {test_signal['symbol']} - {test_signal['type']}")
    print(f"   💰 Preço entrada: ${test_signal['entry_price']}")
    print(f"   🎯 Preço alvo: ${test_signal['target_price']}")
    print(f"   📈 Projeção: {test_signal['projection_percentage']}%")
    print(f"   ⭐ Qualidade: {test_signal['quality_score']}")
    print(f"   🏆 Classe: {test_signal['signal_class']}")
    
    # Tentar salvar no Supabase
    try:
        result = supabase_auth.save_signal_to_supabase(test_signal)
        
        if result:
            print("\n✅ SUCESSO: Sinal salvo no Supabase!")
            print("🎯 A integração está funcionando corretamente")
            return True
        else:
            print("\n❌ FALHA: Não foi possível salvar o sinal")
            print("🔧 Verifique os logs acima para mais detalhes")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO: Exceção ao salvar sinal: {e}")
        return False

def test_table_structure():
    """
    Testa se a tabela signals existe no Supabase
    """
    print("\n🔍 Verificando estrutura da tabela signals...")
    
    try:
        import requests
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Variáveis de ambiente não configuradas")
            return False
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        # Tentar fazer uma consulta simples na tabela
        response = requests.get(
            f"{supabase_url}/rest/v1/signals?limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Tabela 'signals' existe e é acessível")
            data = response.json()
            print(f"📊 Registros encontrados: {len(data)}")
            
            if data:
                print("📋 Estrutura do primeiro registro:")
                for key, value in data[0].items():
                    print(f"   - {key}: {type(value).__name__}")
            
            return True
        else:
            print(f"❌ Erro ao acessar tabela: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        return False

def create_signals_table_sql():
    """
    Gera SQL para criar a tabela signals se ela não existir
    """
    print("\n📋 SQL para criar tabela 'signals' no Supabase:")
    print("=" * 60)
    
    sql = """
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(15,8) NOT NULL,
    target_price DECIMAL(15,8) NOT NULL,
    projection_percentage DECIMAL(8,2),
    quality_score DECIMAL(5,2),
    signal_class VARCHAR(20),
    status VARCHAR(20) DEFAULT 'CONFIRMED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at VARCHAR(50),
    confirmation_reasons TEXT,
    confirmation_attempts INTEGER DEFAULT 0,
    btc_correlation DECIMAL(5,4) DEFAULT 0,
    btc_trend VARCHAR(20) DEFAULT 'NEUTRAL',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);
CREATE INDEX IF NOT EXISTS idx_signals_confirmed_at ON signals(confirmed_at);

-- Habilitar RLS (Row Level Security) se necessário
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública (ajuste conforme necessário)
CREATE POLICY IF NOT EXISTS "Allow public read access" ON signals
    FOR SELECT USING (true);

-- Política para permitir inserção com chave de serviço
CREATE POLICY IF NOT EXISTS "Allow service role insert" ON signals
    FOR INSERT WITH CHECK (true);
"""
    
    print(sql)
    print("=" * 60)
    print("💡 Execute este SQL no Supabase SQL Editor para criar a tabela")

def main():
    """
    Função principal
    """
    print("🚀 Teste de Integração Supabase - Salvamento de Sinais")
    print("=" * 60)
    
    # Testar conexão
    supabase_auth = test_supabase_connection()
    if not supabase_auth:
        print("\n❌ Falha na conexão. Abortando testes.")
        return
    
    # Testar estrutura da tabela
    table_ok = test_table_structure()
    if not table_ok:
        print("\n⚠️ Tabela 'signals' não encontrada ou inacessível")
        create_signals_table_sql()
        print("\n💡 Crie a tabela primeiro e execute o teste novamente")
        return
    
    # Testar salvamento
    save_ok = test_signal_save(supabase_auth)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Conexão Supabase: {'OK' if supabase_auth else 'FALHA'}")
    print(f"✅ Tabela signals: {'OK' if table_ok else 'FALHA'}")
    print(f"✅ Salvamento: {'OK' if save_ok else 'FALHA'}")
    
    if supabase_auth and table_ok and save_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A integração com Supabase está funcionando")
        print("🎯 Sinais confirmados serão salvos automaticamente")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique as configurações e tente novamente")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()