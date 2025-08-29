#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar sinais confirmados usando conexão direta PostgreSQL
Consulta diretamente o banco de dados do Supabase
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from urllib.parse import urlparse

# Carregar variáveis de ambiente
load_dotenv()

def conectar_postgres():
    """
    Conecta diretamente ao PostgreSQL do Supabase
    """
    try:
        database_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not database_url:
            print("❌ SUPABASE_DATABASE_URL não encontrada no .env")
            return None
            
        print(f"🔗 Conectando ao banco: {database_url.split('@')[1] if '@' in database_url else 'URL mascarada'}")
        
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(database_url)
        print("✅ Conexão PostgreSQL estabelecida")
        
        return conn
        
    except Exception as e:
        print(f"❌ Erro ao conectar com PostgreSQL: {e}")
        return None

def listar_tabelas(conn):
    """
    Lista todas as tabelas do banco
    """
    try:
        cursor = conn.cursor()
        
        # Consultar tabelas do schema public
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        
        print("\n📋 Tabelas disponíveis no banco:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
            
        cursor.close()
        return [t[0] for t in tabelas]
        
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return []

def analisar_estrutura_tabela(conn, nome_tabela):
    """
    Analisa a estrutura de uma tabela
    """
    try:
        cursor = conn.cursor()
        
        # Obter estrutura da tabela
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """, (nome_tabela,))
        
        colunas = cursor.fetchall()
        
        if colunas:
            print(f"\n📊 Estrutura da tabela '{nome_tabela}':")
            for coluna in colunas:
                nome, tipo, nullable, default = coluna
                print(f"   - {nome} ({tipo}) {'NULL' if nullable == 'YES' else 'NOT NULL'}")
                
        cursor.close()
        return [c[0] for c in colunas]
        
    except Exception as e:
        print(f"❌ Erro ao analisar tabela {nome_tabela}: {e}")
        return []

def contar_registros(conn, nome_tabela):
    """
    Conta registros em uma tabela
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela};")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception as e:
        print(f"❌ Erro ao contar registros em {nome_tabela}: {e}")
        return 0

def consultar_sinais_tabela(conn, nome_tabela, colunas):
    """
    Consulta sinais em uma tabela específica
    """
    try:
        cursor = conn.cursor()
        
        # Verificar se existe coluna de confirmação
        colunas_confirmacao = ['confirmed', 'confirmado', 'is_confirmed', 'status']
        coluna_confirmacao = None
        
        for col in colunas_confirmacao:
            if col in colunas:
                coluna_confirmacao = col
                break
        
        # Consultar todos os registros primeiro
        cursor.execute(f"SELECT * FROM {nome_tabela} ORDER BY created_at DESC LIMIT 10;")
        registros = cursor.fetchall()
        
        if registros:
            print(f"\n📊 Últimos 10 registros da tabela '{nome_tabela}':")
            
            # Obter nomes das colunas
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (nome_tabela,))
            
            nomes_colunas = [row[0] for row in cursor.fetchall()]
            
            for i, registro in enumerate(registros, 1):
                print(f"\n🎯 REGISTRO #{i}")
                print("-" * 40)
                
                for j, valor in enumerate(registro):
                    if j < len(nomes_colunas):
                        nome_col = nomes_colunas[j]
                        if valor is not None:
                            # Truncar valores muito longos
                            if isinstance(valor, str) and len(valor) > 50:
                                valor = valor[:50] + "..."
                            print(f"   {nome_col}: {valor}")
            
            # Tentar filtrar confirmados se houver coluna
            if coluna_confirmacao:
                if coluna_confirmacao == 'status':
                    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {coluna_confirmacao} = 'confirmed' ORDER BY created_at DESC;")
                else:
                    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {coluna_confirmacao} = true ORDER BY created_at DESC;")
                
                confirmados = cursor.fetchall()
                
                if confirmados:
                    print(f"\n✅ {len(confirmados)} sinais confirmados encontrados!")
                    
                    for i, sinal in enumerate(confirmados[:5], 1):
                        print(f"\n🎯 SINAL CONFIRMADO #{i}")
                        print("-" * 40)
                        
                        for j, valor in enumerate(sinal):
                            if j < len(nomes_colunas):
                                nome_col = nomes_colunas[j]
                                if valor is not None:
                                    if isinstance(valor, str) and len(valor) > 50:
                                        valor = valor[:50] + "..."
                                    print(f"   {nome_col}: {valor}")
                else:
                    print(f"\n⚠️ Nenhum sinal confirmado encontrado na coluna '{coluna_confirmacao}'")
            else:
                print(f"\n⚠️ Nenhuma coluna de confirmação encontrada em '{nome_tabela}'")
                print(f"💡 Colunas disponíveis: {', '.join(colunas)}")
        
        cursor.close()
        return len(registros) > 0
        
    except Exception as e:
        print(f"❌ Erro ao consultar sinais em {nome_tabela}: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 Verificador Direto de Sinais PostgreSQL - 1Crypten")
    print("=" * 60)
    
    # Conectar ao PostgreSQL
    conn = conectar_postgres()
    if not conn:
        print("❌ Falha na conexão. Verifique SUPABASE_DATABASE_URL no .env")
        return
    
    try:
        # Listar todas as tabelas
        tabelas = listar_tabelas(conn)
        
        if not tabelas:
            print("❌ Nenhuma tabela encontrada")
            return
        
        # Procurar tabelas relacionadas a sinais
        tabelas_sinais = []
        palavras_chave = ['signal', 'sinal', 'btc', 'trading', 'crypto', 'trade']
        
        for tabela in tabelas:
            for palavra in palavras_chave:
                if palavra.lower() in tabela.lower():
                    tabelas_sinais.append(tabela)
                    break
        
        if tabelas_sinais:
            print(f"\n🎯 Tabelas relacionadas a sinais encontradas: {tabelas_sinais}")
            
            for tabela in tabelas_sinais:
                print(f"\n" + "="*60)
                print(f"📊 ANALISANDO TABELA: {tabela}")
                print("="*60)
                
                # Contar registros
                total = contar_registros(conn, tabela)
                print(f"📈 Total de registros: {total}")
                
                if total > 0:
                    # Analisar estrutura
                    colunas = analisar_estrutura_tabela(conn, tabela)
                    
                    # Consultar sinais
                    consultar_sinais_tabela(conn, tabela, colunas)
        else:
            print("\n⚠️ Nenhuma tabela relacionada a sinais encontrada")
            print("💡 Analisando todas as tabelas...")
            
            for tabela in tabelas[:5]:  # Limitar a 5 tabelas
                print(f"\n📊 Verificando tabela: {tabela}")
                total = contar_registros(conn, tabela)
                print(f"   📈 Total de registros: {total}")
                
                if total > 0:
                    colunas = analisar_estrutura_tabela(conn, tabela)
                    
                    # Se tem muitas colunas, pode ser uma tabela de sinais
                    if len(colunas) > 5:
                        print(f"   🔍 Tabela com {len(colunas)} colunas - investigando...")
                        consultar_sinais_tabela(conn, tabela, colunas)
        
    finally:
        conn.close()
        print("\n✅ Conexão fechada")
    
    print("\n🎯 Verificação concluída!")

if __name__ == "__main__":
    main()