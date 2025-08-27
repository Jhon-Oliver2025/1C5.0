#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar correções de autenticação no frontend
"""

import os
import shutil
from pathlib import Path

def backup_original_file():
    """
    Faz backup do arquivo original AuthContext.tsx
    """
    print("\n📋 === FAZENDO BACKUP DO ARQUIVO ORIGINAL ===")
    
    original_path = Path("front/src/context/AuthContext.tsx")
    backup_path = Path("front/src/context/AuthContext.tsx.backup")
    
    if original_path.exists():
        shutil.copy2(original_path, backup_path)
        print(f"   ✅ Backup criado: {backup_path}")
        return True
    else:
        print(f"   ⚠️ Arquivo original não encontrado: {original_path}")
        return False

def apply_auth_fix():
    """
    Aplica a correção do AuthContext
    """
    print("\n🔧 === APLICANDO CORREÇÃO DE AUTENTICAÇÃO ===")
    
    fix_path = Path("front/src/context/AuthContextFix.tsx")
    target_path = Path("front/src/context/AuthContext.tsx")
    
    if fix_path.exists():
        # Copiar arquivo de correção para o local correto
        shutil.copy2(fix_path, target_path)
        print(f"   ✅ Correção aplicada: {target_path}")
        
        # Remover arquivo temporário
        fix_path.unlink()
        print(f"   🗑️ Arquivo temporário removido: {fix_path}")
        
        return True
    else:
        print(f"   ❌ Arquivo de correção não encontrado: {fix_path}")
        return False

def create_api_hook():
    """
    Cria hook personalizado para chamadas à API
    """
    print("\n🪝 === CRIANDO HOOK DE API ===")
    
    hook_content = '''
// Hook personalizado para chamadas à API com autenticação automática
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

interface ApiResponse<T = any> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

export const useApi = () => {
  const { apiCall } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = async <T = any>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiCall(url, options);
      
      if (response.ok) {
        const data = await response.json();
        setLoading(false);
        return { data, error: null, loading: false };
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Erro desconhecido' }));
        const errorMessage = errorData.error || `Erro ${response.status}`;
        setError(errorMessage);
        setLoading(false);
        return { data: null, error: errorMessage, loading: false };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro de conexão';
      setError(errorMessage);
      setLoading(false);
      return { data: null, error: errorMessage, loading: false };
    }
  };

  return {
    request,
    loading,
    error,
  };
};

export default useApi;
'''
    
    hook_path = Path("front/src/hooks/useApi.ts")
    
    # Criar diretório se não existir
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Escrever arquivo
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)
    
    print(f"   ✅ Hook criado: {hook_path}")
    return True

def update_login_page():
    """
    Atualiza a página de login para usar o novo AuthContext
    """
    print("\n🔐 === ATUALIZANDO PÁGINA DE LOGIN ===")
    
    login_fix = '''
// Exemplo de como usar o novo AuthContext na página de login
// Adicionar ao componente de Login

import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

const LoginPage = () => {
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLogging, setIsLogging] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLogging(true);

    try {
      const result = await login(email, password);
      
      if (result.success) {
        console.log('✅ Login realizado com sucesso!');
        // Redirecionar para dashboard ou página principal
        // navigate('/dashboard');
      } else {
        setError(result.error || 'Erro no login');
        console.error('❌ Erro no login:', result.error);
      }
    } catch (err) {
      setError('Erro de conexão');
      console.error('❌ Erro de conexão:', err);
    } finally {
      setIsLogging(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
        disabled={isLogging}
      />
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Senha"
        required
        disabled={isLogging}
      />
      
      <button type="submit" disabled={isLogging || loading}>
        {isLogging ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
};

export default LoginPage;
'''
    
    example_path = Path("front/src/examples/LoginExample.tsx")
    
    # Criar diretório se não existir
    example_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Escrever arquivo
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(login_fix)
    
    print(f"   ✅ Exemplo de login criado: {example_path}")
    return True

def create_readme():
    """
    Cria README com instruções de uso
    """
    print("\n📖 === CRIANDO DOCUMENTAÇÃO ===")
    
    readme_content = '''
# Correção de Autenticação - Frontend

## Problema Resolvido

O sistema estava fazendo logout automático porque o token não estava sendo persistido no localStorage. Esta correção resolve:

- ✅ Persistência de token no localStorage
- ✅ Restauração automática na inicialização
- ✅ Interceptor para adicionar token nas requisições
- ✅ Limpeza adequada no logout
- ✅ Verificação de expiração de token
- ✅ Logout automático quando token expira

## Arquivos Modificados

1. **`src/context/AuthContext.tsx`** - Context de autenticação corrigido
2. **`src/hooks/useApi.ts`** - Hook para chamadas à API
3. **`src/examples/LoginExample.tsx`** - Exemplo de uso

## Como Usar

### 1. No componente de Login:

```tsx
import { useAuth } from '../context/AuthContext';

const LoginComponent = () => {
  const { login } = useAuth();
  
  const handleLogin = async (email: string, password: string) => {
    const result = await login(email, password);
    
    if (result.success) {
      // Login realizado com sucesso
      // Token foi automaticamente salvo no localStorage
    } else {
      // Mostrar erro
      console.error(result.error);
    }
  };
};
```

### 2. Para chamadas à API:

```tsx
import { useAuth } from '../context/AuthContext';

const DataComponent = () => {
  const { apiCall } = useAuth();
  
  const fetchData = async () => {
    // Token é automaticamente adicionado
    const response = await apiCall('/api/data');
    const data = await response.json();
  };
};
```

### 3. Usando o hook useApi:

```tsx
import useApi from '../hooks/useApi';

const DataComponent = () => {
  const { request, loading, error } = useApi();
  
  const fetchData = async () => {
    const result = await request('/api/data');
    
    if (result.data) {
      // Usar dados
    } else {
      // Tratar erro
      console.error(result.error);
    }
  };
};
```

## Funcionalidades

- **Persistência**: Token salvo no localStorage
- **Restauração**: Dados carregados automaticamente na inicialização
- **Expiração**: Token expira em 24 horas
- **Verificação**: Verifica validade a cada minuto
- **Interceptor**: Adiciona token automaticamente nas requisições
- **Logout**: Limpa todos os dados salvos

## Logs de Debug

O sistema agora inclui logs detalhados:

- `✅ Auth: Dados salvos no localStorage`
- `✅ Auth: Dados restaurados do localStorage`
- `🔐 Auth: Logout realizado`
- `⚠️ Auth: Token expirado, fazendo logout automático`

## Teste

Para testar se a correção funcionou:

1. Faça login
2. Recarregue a página
3. Verifique se continua logado
4. Verifique os logs no console do navegador

## Backup

O arquivo original foi salvo como `AuthContext.tsx.backup`
'''
    
    readme_path = Path("front/AUTH_FIX_README.md")
    
    # Escrever arquivo
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"   ✅ Documentação criada: {readme_path}")
    return True

def main():
    """
    Função principal
    """
    print("🚀 Aplicando correções de autenticação...")
    
    # Mudar para o diretório do projeto
    os.chdir(Path(__file__).parent)
    
    success_count = 0
    total_steps = 5
    
    # Passo 1: Backup
    if backup_original_file():
        success_count += 1
    
    # Passo 2: Aplicar correção
    if apply_auth_fix():
        success_count += 1
    
    # Passo 3: Criar hook
    if create_api_hook():
        success_count += 1
    
    # Passo 4: Exemplo de login
    if update_login_page():
        success_count += 1
    
    # Passo 5: Documentação
    if create_readme():
        success_count += 1
    
    # Resumo
    print(f"\n📊 === RESUMO ===")
    print(f"   ✅ Passos concluídos: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print(f"   🎉 Todas as correções aplicadas com sucesso!")
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1. Fazer commit das mudanças")
        print(f"   2. Fazer deploy no Coolify")
        print(f"   3. Testar login no frontend")
        print(f"   4. Verificar se o token persiste após reload")
    else:
        print(f"   ⚠️ Algumas correções falharam")
    
    print(f"\n🔍 === FIM ===\n")

if __name__ == "__main__":
    main()