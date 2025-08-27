#!/usr/bin/env python3
# Script para corrigir todas as referências de localStorage.getItem('token') para 'auth_token'

import os
import re

def fix_token_references():
    """Corrige todas as referências de token no frontend"""
    
    # Diretório do frontend
    frontend_dir = os.path.join(os.path.dirname(__file__), 'front', 'src')
    
    # Padrões a serem substituídos
    patterns = [
        (r"localStorage\.getItem\('token'\)", "localStorage.getItem('auth_token')"),
        (r"localStorage\.setItem\('token',", "localStorage.setItem('auth_token',"),
        (r"localStorage\.removeItem\('token'\)", "localStorage.removeItem('auth_token')")
    ]
    
    files_modified = []
    
    # Percorrer todos os arquivos .ts e .tsx
    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx')):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Aplicar todas as substituições
                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)
                    
                    # Se houve mudanças, salvar o arquivo
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        relative_path = os.path.relpath(file_path, frontend_dir)
                        files_modified.append(relative_path)
                        print(f"✅ Corrigido: {relative_path}")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar {file_path}: {e}")
    
    print(f"\n🎯 Resumo:")
    print(f"📁 Arquivos modificados: {len(files_modified)}")
    
    if files_modified:
        print("\n📋 Lista de arquivos corrigidos:")
        for file in files_modified:
            print(f"  - {file}")
    
    return files_modified

if __name__ == '__main__':
    print("🔧 Iniciando correção de referências de token...")
    modified_files = fix_token_references()
    
    if modified_files:
        print("\n✅ Correção concluída com sucesso!")
        print("\n🎯 Próximos passos:")
        print("1. Teste o login novamente")
        print("2. Verifique se o dashboard não volta mais para login")
        print("3. Confirme que os tokens estão sendo encontrados")
    else:
        print("\n✅ Nenhuma correção necessária - todos os arquivos já estão corretos!")