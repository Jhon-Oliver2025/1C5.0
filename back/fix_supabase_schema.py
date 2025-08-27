#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir estrutura da tabela signals no Supabase
"""

import os
import requests
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_credentials():
    """
    Obtém as credenciais do Supabase
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not all([supabase_url, supabase_anon_key]):
        print("❌ Credenciais do Supabase não encontradas!")
        return None, None, None
    
    return supabase_url, supabase_anon_key, supabase_service_role_key

def check_table_structure():
    """
    Verifica a estrutura atual da tabela signals
    """
    print("\n🔍 === VERIFICANDO ESTRUTURA DA TABELA SIGNALS ===")
    
    supabase_url, supabase_anon_key, service_role_key = get_supabase_credentials()
    if not supabase_url:
        return False
    
    # Usar service role key se disponível, senão anon key
    api_key = service_role_key if service_role_key else supabase_anon_key
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Tentar buscar um registro para ver a estrutura
        response = requests.get(
            f"{supabase_url}/rest/v1/signals?limit=1",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status da consulta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                columns = list(data[0].keys())
                print(f"   ✅ Colunas encontradas: {columns}")
                
                # Verificar se confirmed_at existe
                if 'confirmed_at' in columns:
                    print(f"   ✅ Coluna 'confirmed_at' existe")
                    return True
                else:
                    print(f"   ❌ Coluna 'confirmed_at' NÃO existe")
                    return False
            else:
                print(f"   ⚠️ Tabela vazia, não é possível verificar estrutura")
                return None
        else:
            print(f"   ❌ Erro ao consultar tabela: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na verificação: {e}")
        return False

def add_confirmed_at_column():
    """
    Adiciona a coluna confirmed_at à tabela signals
    """
    print(f"\n🔧 === ADICIONANDO COLUNA CONFIRMED_AT ===")
    
    supabase_url, supabase_anon_key, service_role_key = get_supabase_credentials()
    if not supabase_url:
        return False
    
    # Usar service role key para operações DDL
    api_key = service_role_key if service_role_key else supabase_anon_key
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # SQL para adicionar a coluna
    sql_query = """
    ALTER TABLE signals 
    ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMPTZ;
    """
    
    try:
        # Executar SQL via RPC (se disponível) ou via REST
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": sql_query},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Coluna 'confirmed_at' adicionada com sucesso")
            return True
        else:
            print(f"   ❌ Erro ao adicionar coluna: {response.text}")
            
            # Tentar método alternativo via SQL direto
            print(f"   🔄 Tentando método alternativo...")
            return add_column_alternative_method()
            
    except Exception as e:
        print(f"   ❌ Erro na execução: {e}")
        print(f"   🔄 Tentando método alternativo...")
        return add_column_alternative_method()

def add_column_alternative_method():
    """
    Método alternativo para adicionar coluna usando SQL direto
    """
    print(f"\n🔄 === MÉTODO ALTERNATIVO - SQL DIRETO ===")
    
    sql_commands = [
        "ALTER TABLE signals ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMPTZ;",
        "UPDATE signals SET confirmed_at = created_at WHERE status = 'CONFIRMED' AND confirmed_at IS NULL;",
        "CREATE INDEX IF NOT EXISTS idx_signals_confirmed_at ON signals(confirmed_at) WHERE confirmed_at IS NOT NULL;"
    ]
    
    print(f"\n📝 Comandos SQL para executar manualmente:")
    for i, cmd in enumerate(sql_commands, 1):
        print(f"   {i}. {cmd}")
    
    print(f"\n🎯 INSTRUÇÕES:")
    print(f"   1. Acesse: https://supabase.com/dashboard/project/fvwdcsqucajnqupsprmo")
    print(f"   2. Vá em 'SQL Editor'")
    print(f"   3. Execute os comandos acima um por um")
    print(f"   4. Verifique se a coluna foi criada")
    
    return False  # Retorna False pois precisa ser feito manualmente

def update_existing_records():
    """
    Atualiza registros existentes para ter confirmed_at
    """
    print(f"\n🔄 === ATUALIZANDO REGISTROS EXISTENTES ===")
    
    supabase_url, supabase_anon_key, service_role_key = get_supabase_credentials()
    if not supabase_url:
        return False
    
    api_key = service_role_key if service_role_key else supabase_anon_key
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Buscar registros confirmados sem confirmed_at
        response = requests.get(
            f"{supabase_url}/rest/v1/signals?status=eq.CONFIRMED&confirmed_at=is.null",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            records = response.json()
            print(f"   📊 Encontrados {len(records)} registros para atualizar")
            
            if records:
                # Atualizar cada registro
                for record in records:
                    update_response = requests.patch(
                        f"{supabase_url}/rest/v1/signals?id=eq.{record['id']}",
                        headers=headers,
                        json={"confirmed_at": record['created_at']},
                        timeout=10
                    )
                    
                    if update_response.status_code in [200, 204]:
                        print(f"   ✅ Registro {record['id']} atualizado")
                    else:
                        print(f"   ❌ Erro ao atualizar {record['id']}: {update_response.text}")
                
                return True
            else:
                print(f"   ✅ Nenhum registro precisa ser atualizado")
                return True
        else:
            print(f"   ❌ Erro ao buscar registros: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na atualização: {e}")
        return False

def test_fixed_query():
    """
    Testa a consulta que estava falhando
    """
    print(f"\n🧪 === TESTANDO CONSULTA CORRIGIDA ===")
    
    supabase_url, supabase_anon_key, service_role_key = get_supabase_credentials()
    if not supabase_url:
        return False
    
    api_key = supabase_anon_key  # Usar anon key para teste
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Testar a consulta que estava falhando
        response = requests.get(
            f"{supabase_url}/rest/v1/signals?select=*&status=eq.CONFIRMED&order=confirmed_at.desc",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Consulta funcionando! Retornados {len(data)} registros")
            
            if data:
                print(f"   📊 Primeiro registro: {data[0].get('symbol', 'N/A')} - {data[0].get('confirmed_at', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Consulta ainda falhando: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

def create_migration_script():
    """
    Cria script de migração SQL
    """
    print(f"\n📝 === CRIANDO SCRIPT DE MIGRAÇÃO ===")
    
    migration_sql = '''
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
'''
    
    migration_file = "supabase_migration_confirmed_at.sql"
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_sql)
    
    print(f"   ✅ Script criado: {migration_file}")
    print(f"   📋 Execute este script no Supabase SQL Editor")
    
    return migration_file

def main():
    """
    Função principal
    """
    print("🚀 Iniciando correção da estrutura do Supabase...")
    
    # Passo 1: Verificar estrutura atual
    has_column = check_table_structure()
    
    if has_column is True:
        print(f"\n✅ Coluna 'confirmed_at' já existe! Testando consulta...")
        if test_fixed_query():
            print(f"\n🎉 Tudo funcionando corretamente!")
            return
    
    # Passo 2: Criar script de migração
    migration_file = create_migration_script()
    
    # Passo 3: Tentar adicionar coluna automaticamente
    if has_column is False:
        print(f"\n🔧 Tentando adicionar coluna automaticamente...")
        success = add_confirmed_at_column()
        
        if success:
            # Passo 4: Atualizar registros existentes
            update_existing_records()
            
            # Passo 5: Testar consulta
            test_fixed_query()
    
    # Resumo final
    print(f"\n📊 === RESUMO ===")
    print(f"   📝 Script de migração: {migration_file}")
    print(f"   🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Execute o script SQL no Supabase Dashboard")
    print(f"   2. Verifique se a coluna foi criada")
    print(f"   3. Teste a aplicação novamente")
    print(f"   4. Verifique se o erro 'column does not exist' foi resolvido")
    
    print(f"\n🔗 LINKS ÚTEIS:")
    print(f"   - Dashboard: https://supabase.com/dashboard/project/fvwdcsqucajnqupsprmo")
    print(f"   - SQL Editor: https://supabase.com/dashboard/project/fvwdcsqucajnqupsprmo/sql")
    
    print(f"\n🔍 === FIM ===\n")

if __name__ == "__main__":
    main()