#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar sinais da memória/CSV para o Supabase
Garante que os sinais não sejam perdidos durante redeploys
"""

import os
import sys
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def migrate_signals_to_supabase():
    """Migra todos os sinais existentes para o Supabase"""
    
    print("🔄 Iniciando migração de sinais para Supabase...")
    
    # Configurações do Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Variáveis de ambiente SUPABASE não configuradas")
        return False
    
    headers = {
        'apikey': supabase_anon_key,
        'Authorization': f'Bearer {supabase_anon_key}',
        'Content-Type': 'application/json'
    }
    
    # Verificar se a tabela signals existe
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/signals?limit=1",
            headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Erro ao acessar tabela signals: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
        print("✅ Tabela signals acessível no Supabase")
    except Exception as e:
        print(f"❌ Erro ao verificar tabela signals: {e}")
        return False
    
    # Buscar sinais existentes no CSV
    csv_files = [
        'back/sinais_lista.csv',
        'back/historico_sinais.csv'
    ]
    
    total_migrated = 0
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"\n📂 Processando arquivo: {csv_file}")
            
            try:
                df = pd.read_csv(csv_file)
                print(f"📊 Encontrados {len(df)} sinais no arquivo")
                
                for index, row in df.iterrows():
                    try:
                        # Preparar dados do sinal (apenas campos básicos que existem na tabela)
                        signal_data = {
                            'symbol': str(row.get('symbol', '')),
                            'type': str(row.get('type', '')),
                            'entry_price': float(row.get('entry_price', 0)),
                            'target_price': float(row.get('target_price', 0)),
                            'entry_time': str(row.get('entry_time', datetime.now().isoformat())),
                            'status': str(row.get('status', 'OPEN')),
                            'quality_score': float(row.get('quality_score', 0)),
                            'signal_class': str(row.get('signal_class', '')) if pd.notna(row.get('signal_class')) else None,
                            'timeframe': str(row.get('timeframe', '1h'))
                        }
                        
                        # Remover campos None
                        signal_data = {k: v for k, v in signal_data.items() if v is not None and v != ''}
                        
                        # Verificar se o sinal já existe no Supabase
                        check_response = requests.get(
                            f"{supabase_url}/rest/v1/signals?symbol=eq.{signal_data['symbol']}&type=eq.{signal_data['type']}&entry_price=eq.{signal_data['entry_price']}",
                            headers=headers
                        )
                        
                        if check_response.status_code == 200 and len(check_response.json()) > 0:
                            print(f"⏭️ Sinal já existe: {signal_data['symbol']} - {signal_data['type']}")
                            continue
                        
                        # Salvar no Supabase
                        response = requests.post(
                            f"{supabase_url}/rest/v1/signals",
                            headers=headers,
                            json=signal_data
                        )
                        
                        if response.status_code in [200, 201]:
                            print(f"✅ Migrado: {signal_data['symbol']} - {signal_data['type']}")
                            total_migrated += 1
                        else:
                            print(f"❌ Erro ao migrar {signal_data['symbol']}: {response.status_code} - {response.text}")
                            
                    except Exception as e:
                        print(f"❌ Erro ao processar linha {index}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Erro ao processar arquivo {csv_file}: {e}")
                continue
        else:
            print(f"⚠️ Arquivo não encontrado: {csv_file}")
    
    print(f"\n🎉 Migração concluída! Total de sinais migrados: {total_migrated}")
    return total_migrated > 0

def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    
    print("\n🔍 Verificando migração...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    headers = {
        'apikey': supabase_anon_key,
        'Authorization': f'Bearer {supabase_anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/signals?select=count",
            headers=headers
        )
        
        if response.status_code == 200:
            count = len(response.json())
            print(f"📊 Total de sinais no Supabase: {count}")
            
            # Buscar alguns sinais recentes
            recent_response = requests.get(
                f"{supabase_url}/rest/v1/signals?order=created_at.desc&limit=5",
                headers=headers
            )
            
            if recent_response.status_code == 200:
                recent_signals = recent_response.json()
                print(f"\n📋 Últimos 5 sinais migrados:")
                for signal in recent_signals:
                    print(f"  • {signal.get('symbol')} - {signal.get('type')} - {signal.get('status')}")
            
            return True
        else:
            print(f"❌ Erro ao verificar migração: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Script de Migração de Sinais para Supabase")
    print("=" * 50)
    
    # Executar migração
    success = migrate_signals_to_supabase()
    
    if success:
        # Verificar migração
        verify_migration()
        print("\n✅ Migração concluída com sucesso!")
        print("🎯 Os sinais agora estão persistidos no Supabase e não serão perdidos em redeploys.")
    else:
        print("\n❌ Migração falhou. Verifique as configurações do Supabase.")
        sys.exit(1)