# 🔧 Configuração do Usuário Admin no Supabase

## 📋 Visão Geral

Este guia explica como configurar o usuário administrador no Supabase para o sistema 1Crypten. O sistema foi projetado para usar Supabase como banco de dados principal.

## 🚀 Passos para Configuração

### 1. Acesse o Painel do Supabase

1. Vá para [https://supabase.com](https://supabase.com)
2. Faça login na sua conta
3. Selecione o projeto: `fvwdcsqucajnqupsprmo`

### 2. Execute o Script SQL

1. No painel do Supabase, vá para **SQL Editor**
2. Clique em **New Query**
3. Copie todo o conteúdo do arquivo `setup_supabase_admin.sql`
4. Cole no editor SQL
5. Clique em **Run** para executar

### 3. Verificar Criação

Após executar o script, você verá:

```sql
-- Resultado esperado:
USUÁRIO ADMIN CRIADO COM SUCESSO!
username: admin
email: jonatasprojetos2013@gmail.com
password: admin123
is_admin: true
user_status: active
```

## 🔑 Credenciais do Admin

**Para fazer login no sistema:**
- **Email**: `jonatasprojetos2013@gmail.com`
- **Senha**: `admin123`

## 📊 Estrutura Criada

O script cria automaticamente:

### Tabelas:
- ✅ `users` - Usuários do sistema
- ✅ `auth_tokens` - Tokens de autenticação
- ✅ `trading_signals` - Sinais de trading
- ✅ `bot_config` - Configurações do sistema

### Índices:
- ✅ Índices de performance para todas as tabelas
- ✅ Índices para consultas rápidas

### Triggers:
- ✅ Auto-atualização de `updated_at`
- ✅ Controle de timestamps

## 🔧 Configurações do Sistema

O arquivo `.env` foi configurado para:
```env
USE_SUPABASE=true
SUPABASE_URL=https://fvwdcsqucajnqupsprmo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DATABASE_URL=postgresql://postgres:Fh@xj_wgU-D2Vde@db.fvwdcsqucajnqupsprmo.supabase.co:5432/postgres
```

## 🚀 Deploy em Produção

### Variáveis de Ambiente no Coolify:

Configure estas variáveis no Coolify:

```env
# Supabase
SUPABASE_URL=https://fvwdcsqucajnqupsprmo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2d2Rjc3F1Y2FqbnF1cHNwcm1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyMTAzNzUsImV4cCI6MjA2ODc4NjM3NX0.h7cNPa_WtSn7s1DDPAdBhLqUZYQLJbn3wDoAIMEFYyQ
SUPABASE_DATABASE_URL=postgresql://postgres:Fh@xj_wgU-D2Vde@db.fvwdcsqucajnqupsprmo.supabase.co:5432/postgres

# Sistema
USE_SUPABASE=true
FLASK_ENV=production
```

## ✅ Verificação

Para verificar se tudo está funcionando:

1. **Acesse o sistema**: `https://1crypten.space/login`
2. **Faça login com**:
   - Email: `jonatasprojetos2013@gmail.com`
   - Senha: `admin123`
3. **Deve funcionar perfeitamente!**

## 🔍 Troubleshooting

### Erro de Conexão
Se houver erro de conexão:
1. Verifique se as variáveis de ambiente estão corretas
2. Confirme se o projeto Supabase está ativo
3. Teste a conexão no SQL Editor do Supabase

### Usuário Não Encontrado
Se o login falhar:
1. Execute novamente o script SQL
2. Verifique se o usuário foi criado:
   ```sql
   SELECT * FROM users WHERE email = 'jonatasprojetos2013@gmail.com';
   ```

### Erro 401 Unauthorized
Se continuar dando 401:
1. Limpe o cache do navegador
2. Verifique se `USE_SUPABASE=true` no ambiente
3. Confirme se as chaves do Supabase estão corretas

## 🎉 Conclusão

Após seguir estes passos:
- ✅ Usuário admin estará criado no Supabase
- ✅ Sistema configurado para usar Supabase
- ✅ Login funcionando em produção
- ✅ Todas as tabelas e estruturas criadas

**O sistema 1Crypten estará 100% funcional com Supabase!**