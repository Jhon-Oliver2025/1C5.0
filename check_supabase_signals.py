#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar sinais confirmados no Supabase
Consulta a tabela de sinais e exibe os dados organizados
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Adicionar o diretório back ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

try:
    from supabase import create_client, Client
    from supabase_config import SupabaseConfig
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("💡 Execute: pip install supabase")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()

def conectar_supabase():
    """
    Estabelece conexão com o Supabase
    """
    try:
        config = SupabaseConfig()
        
        if not config.is_configured:
            print("❌ Configuração do Supabase inválida")
            return None
            
        # Criar cliente Supabase
        supabase: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_SERVICE_ROLE_KEY  # Usar service role para acesso completo
        )
        
        print("✅ Conexão com Supabase estabelecida")
        return supabase
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return None

def listar_tabelas(supabase):
    """
    Lista todas as tabelas disponíveis no banco
    """
    try:
        # Consultar tabelas do sistema
        response = supabase.rpc('get_table_names').execute()
        
        if response.data:
            print("\n📋 Tabelas disponíveis:")
            for table in response.data:
                print(f"   - {table}")
        else:
            print("\n⚠️ Nenhuma tabela encontrada ou erro na consulta")
            
    except Exception as e:
        print(f"\n⚠️ Não foi possível listar tabelas: {e}")
        print("💡 Tentando tabelas conhecidas...")

def consultar_sinais_confirmados(supabase):
    """
    Consulta sinais confirmados na tabela de sinais
    """
    tabelas_possiveis = [
        'signals',
        'sinais', 
        'btc_signals',
        'trading_signals',
        'confirmed_signals'
    ]
    
    print("\n🔍 Procurando sinais confirmados...")
    
    for tabela in tabelas_possiveis:
        try:
            print(f"\n📊 Verificando tabela: {tabela}")
            
            # Tentar consultar a tabela
            response = supabase.table(tabela).select('*').execute()
            
            if response.data:
                print(f"✅ Tabela {tabela} encontrada com {len(response.data)} registros")
                
                # Filtrar apenas sinais confirmados
                sinais_confirmados = []
                for sinal in response.data:
                    # Verificar diferentes campos que podem indicar confirmação
                    if (sinal.get('confirmed') == True or 
                        sinal.get('status') == 'confirmed' or
                        sinal.get('is_confirmed') == True or
                        sinal.get('confirmado') == True):
                        sinais_confirmados.append(sinal)
                
                if sinais_confirmados:
                    print(f"\n✅ {len(sinais_confirmados)} sinais confirmados encontrados:")
                    exibir_sinais(sinais_confirmados)
                else:
                    print(f"\n⚠️ Nenhum sinal confirmado encontrado na tabela {tabela}")
                    print("📋 Primeiros 3 registros para análise:")
                    for i, sinal in enumerate(response.data[:3]):
                        print(f"   {i+1}. {sinal}")
                
                return True
                
        except Exception as e:
            print(f"   ❌ Erro ao consultar {tabela}: {e}")
            continue
    
    print("\n❌ Nenhuma tabela de sinais encontrada")
    return False

def exibir_sinais(sinais):
    """
    Exibe os sinais de forma organizada
    """
    print("\n" + "="*80)
    print("📈 SINAIS CONFIRMADOS NO SUPABASE")
    print("="*80)
    
    for i, sinal in enumerate(sinais, 1):
        print(f"\n🎯 SINAL #{i}")
        print("-" * 40)
        
        # Campos comuns de sinais
        campos_importantes = [
            'symbol', 'simbolo', 'pair', 'moeda',
            'direction', 'direcao', 'tipo', 'action',
            'entry_price', 'preco_entrada', 'price', 'valor',
            'target', 'alvo', 'take_profit', 'tp',
            'stop_loss', 'sl', 'stop',
            'confidence', 'confianca', 'score',
            'created_at', 'criado_em', 'timestamp', 'data',
            'confirmed', 'confirmado', 'status'
        ]
        
        for campo in campos_importantes:
            if campo in sinal and sinal[campo] is not None:
                valor = sinal[campo]
                if isinstance(valor, str) and len(valor) > 50:
                    valor = valor[:50] + "..."
                print(f"   {campo}: {valor}")
        
        # Mostrar outros campos não listados
        outros_campos = {k: v for k, v in sinal.items() 
                        if k not in campos_importantes and v is not None}
        
        if outros_campos:
            print("   Outros campos:")
            for k, v in outros_campos.items():
                if isinstance(v, str) and len(v) > 30:
                    v = v[:30] + "..."
                print(f"     {k}: {v}")

def consultar_estatisticas(supabase):
    """
    Consulta estatísticas gerais dos sinais
    """
    print("\n📊 ESTATÍSTICAS DOS SINAIS")
    print("="*50)
    
    tabelas_possiveis = ['signals', 'sinais', 'btc_signals', 'trading_signals']
    
    for tabela in tabelas_possiveis:
        try:
            # Total de registros
            response = supabase.table(tabela).select('*', count='exact').execute()
            total = response.count if hasattr(response, 'count') else len(response.data or [])
            
            if total > 0:
                print(f"\n📋 Tabela: {tabela}")
                print(f"   📊 Total de registros: {total}")
                
                # Tentar contar confirmados
                try:
                    confirmed_response = supabase.table(tabela).select('*').eq('confirmed', True).execute()
                    confirmados = len(confirmed_response.data or [])
                    print(f"   ✅ Sinais confirmados: {confirmados}")
                    print(f"   📈 Taxa de confirmação: {(confirmados/total)*100:.1f}%")
                except:
                    print(f"   ⚠️ Não foi possível contar sinais confirmados")
                
                # Últimos registros
                try:
                    recent_response = supabase.table(tabela).select('*').order('created_at', desc=True).limit(5).execute()
                    if recent_response.data:
                        print(f"   🕒 Últimos 5 registros:")
                        for record in recent_response.data:
                            created_at = record.get('created_at', 'N/A')
                            symbol = record.get('symbol', record.get('simbolo', 'N/A'))
                            status = record.get('confirmed', record.get('status', 'N/A'))
                            print(f"     - {created_at} | {symbol} | {status}")
                except:
                    print(f"   ⚠️ Não foi possível obter registros recentes")
                    
        except Exception as e:
            continue

def main():
    """
    Função principal
    """
    print("🚀 Verificador de Sinais Supabase - 1Crypten")
    print("=" * 50)
    
    # Conectar ao Supabase
    supabase = conectar_supabase()
    if not supabase:
        print("❌ Falha na conexão. Verifique as configurações.")
        return
    
    # Listar tabelas disponíveis
    listar_tabelas(supabase)
    
    # Consultar sinais confirmados
    encontrou_sinais = consultar_sinais_confirmados(supabase)
    
    # Mostrar estatísticas
    consultar_estatisticas(supabase)
    
    if not encontrou_sinais:
        print("\n💡 DICAS PARA RESOLVER:")
        print("1. Verifique se as tabelas de sinais existem no Supabase")
        print("2. Confirme se as variáveis de ambiente estão corretas")
        print("3. Verifique as permissões da service role key")
        print("4. Consulte a documentação do banco de dados")
    
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    main()