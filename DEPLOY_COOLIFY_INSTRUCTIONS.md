# 🚀 Deploy no Coolify - 1Crypten Trading Bot

## 📋 Pré-requisitos

Antes de fazer o deploy no Coolify, você precisa ter:

### 1. Credenciais do Supabase
- URL do projeto Supabase
- Chave anônima (anon key)
- Chave de serviço (service role key)
- URL de conexão com o banco de dados

### 2. Credenciais da API Binance
- API Key da Binance
- Secret Key da Binance
- ⚠️ **IMPORTANTE**: Configure as permissões corretas na Binance (apenas leitura para dados de mercado)

### 3. Bot do Telegram (Opcional)
- Token do bot do Telegram
- Chat ID para receber notificações

## 🔧 Configuração no Coolify

### Passo 1: Criar o Projeto
1. Acesse seu painel do Coolify
2. Clique em "New Project"
3. Conecte seu repositório GitHub
4. Selecione o branch principal

### Passo 2: Configurar Variáveis de Ambiente

No painel do Coolify, adicione as seguintes variáveis de ambiente:

#### 🔐 Configurações Básicas
```env
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_PORT=5000
SECRET_KEY=SUA_CHAVE_SECRETA_FORTE_AQUI
JWT_SECRET=SUA_JWT_SECRET_FORTE_AQUI
```

#### 🗄️ Supabase (OBRIGATÓRIO)
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima_supabase
SUPABASE_SERVICE_ROLE_KEY=sua_chave_servico_supabase
SUPABASE_DATABASE_URL=postgresql://postgres:senha@db.projeto.supabase.co:5432/postgres
USE_SUPABASE=true
```

#### 📈 Binance API (OBRIGATÓRIO)
```env
BINANCE_API_KEY=sua_api_key_binance
BINANCE_SECRET_KEY=sua_secret_key_binance
USE_BINANCE_API=true
```

#### 🤖 Telegram (OPCIONAL)
```env
TELEGRAM_BOT_TOKEN=seu_token_telegram
TELEGRAM_CHAT_ID=seu_chat_id
```

#### 🌐 URLs e CORS
```env
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
API_BASE_URL=https://api.seu-dominio.com
FRONTEND_URL=https://seu-dominio.com
```

#### ⚡ Redis
```env
REDIS_URL=redis://redis:6379/0
```

### Passo 3: Configurar Serviços

#### 🔴 Redis
1. No Coolify, adicione um serviço Redis
2. Use a imagem: `redis:7-alpine`
3. Configure o nome do serviço como `redis`

#### 🐳 Backend
1. Configure o Dockerfile: `./back/Dockerfile`
2. Porta interna: `5000`
3. Comando de inicialização: `python app_supabase.py`

#### ⚛️ Frontend
1. Configure o Dockerfile: `./front/Dockerfile`
2. Porta interna: `80`
3. Variáveis de ambiente:
   ```env
   VITE_API_URL=https://api.seu-dominio.com
   VITE_DOMAIN=https://seu-dominio.com
   NODE_ENV=production
   ```

### Passo 4: Configurar Domínios

1. **Frontend**: `seu-dominio.com`
2. **Backend API**: `api.seu-dominio.com`

### Passo 5: Configurar SSL

1. Ative SSL automático no Coolify
2. Configure redirecionamento HTTPS

## 🔍 Verificação do Deploy

### Endpoints para Testar

1. **Status da API**:
   ```bash
   curl https://api.seu-dominio.com/api/status
   ```

2. **Sinais BTC**:
   ```bash
   curl https://api.seu-dominio.com/api/btc-signals/pending
   ```

3. **Status do Mercado**:
   ```bash
   curl https://api.seu-dominio.com/api/market-status
   ```

### Logs para Monitorar

1. Acesse os logs do backend no Coolify
2. Verifique se não há erros de conexão
3. Confirme que o Redis está conectado
4. Verifique se a API Binance está funcionando

## 🚨 Troubleshooting

### Problema: Backend não inicia
**Solução**: Verifique as variáveis de ambiente, especialmente Supabase e Binance

### Problema: Erro de conexão com Redis
**Solução**: Certifique-se de que o serviço Redis está rodando e o nome está correto

### Problema: API Binance retorna erro 401
**Solução**: Verifique se as chaves da Binance estão corretas e têm as permissões adequadas

### Problema: Frontend não carrega
**Solução**: Verifique se a variável VITE_API_URL está apontando para o backend correto

### Problema: CORS Error
**Solução**: Adicione o domínio do frontend na variável CORS_ORIGINS

## 📊 Monitoramento

### Métricas Importantes

1. **CPU e Memória**: Monitore o uso de recursos
2. **Logs de Erro**: Verifique erros recorrentes
3. **Tempo de Resposta**: APIs devem responder em < 2s
4. **Uptime**: Sistema deve ter 99%+ de disponibilidade

### Alertas Recomendados

1. **Alto uso de CPU** (> 80%)
2. **Alto uso de memória** (> 90%)
3. **Muitos erros 5xx** (> 10 por minuto)
4. **Tempo de resposta alto** (> 5s)

## 🔄 Atualizações

### Deploy Automático

1. Configure webhook no GitHub
2. Ative auto-deploy no Coolify
3. Pushes na branch principal farão deploy automático

### Deploy Manual

1. Acesse o painel do Coolify
2. Clique em "Deploy"
3. Aguarde a conclusão
4. Verifique os logs

## 🛡️ Segurança

### Checklist de Segurança

- [ ] SSL/HTTPS ativado
- [ ] Variáveis de ambiente seguras
- [ ] Chaves da API com permissões mínimas
- [ ] CORS configurado corretamente
- [ ] Rate limiting ativado
- [ ] Logs não expõem informações sensíveis

### Backup

1. **Banco de Dados**: Supabase faz backup automático
2. **Código**: Mantido no GitHub
3. **Configurações**: Documente todas as variáveis de ambiente

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs no Coolify
2. Teste os endpoints individualmente
3. Confirme todas as variáveis de ambiente
4. Verifique a conectividade entre serviços

## 🎯 Próximos Passos

Após o deploy bem-sucedido:

1. Configure monitoramento avançado
2. Implemente alertas personalizados
3. Configure backup automático
4. Otimize performance conforme necessário
5. Documente procedimentos operacionais

---

**✅ Sistema pronto para produção!**

O 1Crypten Trading Bot está configurado para funcionar 24/7 no Coolify, gerando sinais de trading em tempo real com integração completa ao Supabase e APIs externas.

**Recursos Ativos:**
- ⚡ Redis para cache de alta performance
- 🗄️ Supabase como banco de dados principal
- 📈 API Binance para dados de mercado em tempo real
- 🤖 Notificações via Telegram
- 🔄 Sistema de sinais automatizado
- 📊 Monitoramento de mercado 24/7
- 🛡️ Segurança e SSL configurados
- 🚀 Deploy automático via GitHub

**Performance Esperada:**
- Tempo de resposta: < 2 segundos
- Uptime: 99.9%
- Processamento: 1000+ requisições/minuto
- Latência de dados: < 1 segundo

**Próximas Funcionalidades:**
- Dashboard de analytics avançado
- Alertas personalizáveis
- API para integração com terceiros
- Mobile app (PWA)
- Sistema de backtesting

🎉 **Parabéns! Seu sistema de trading está no ar!**