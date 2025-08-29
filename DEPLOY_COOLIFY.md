# Deploy no Coolify - 1Crypten

## Configurações Necessárias

### 1. Variáveis de Ambiente
Configure as seguintes variáveis de ambiente no Coolify:

```bash
# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://fvwdcsqucajnqupsprmo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2d2Rjc3F1Y2FqbnF1cHNwcm1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyMTAzNzUsImV4cCI6MjA2ODc4NjM3NX0.h7cNPa_WtSn7s1DDPAdBhLqUZYQLJbn3wDoAIMEFYyQ
SUPABASE_DATABASE_URL=postgresql://postgres:Fh@xj_wgU-D2Vde@db.fvwdcsqucajnqupsprmo.supabase.co:5432/postgres

# Binance API (Trading)
BINANCE_API_KEY=aUApdM0jyXeyI1HPxHymi9hSD6QZ3TXFORTknlyc1jADrkCJ7SNSayoZ6oiPCYEj
BINANCE_SECRET_KEY=YGt2MXqsIhgjk6EsCwRCUjB3LpZ0L8xGAt9w4JYK6wyX2LveLHBFvRjoyBfIVcZM

# Telegram Bot (Notificações)
TELEGRAM_BOT_TOKEN=7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ
TELEGRAM_CHAT_ID=1249100206

# SendPulse (E-mail Marketing)
SENDPULSE_CLIENT_ID=7b28b045d31c3d6d51591d7f56a26c99
SENDPULSE_CLIENT_SECRET=26393054ce0cd24fc16a73382a3d5eef
SENDPULSE_SENDER_EMAIL=crypten@portaldigital10.com
SENDPULSE_API_URL=https://api.sendpulse.com

# Mercado Pago (Pagamentos - TESTE)
MERCADO_PAGO_ACCESS_TOKEN=TEST-6555567678065222-081500-d19fea4c0e7513745e4aba7f14244ba4-150384131
MERCADO_PAGO_PUBLIC_KEY=TEST-49cb27ee-fe8c-4aa0-b055-092bf4616484

# JWT e Segurança
JWT_SECRET=X9eR3cM7zL10prasempre1kP5f
SECRET_KEY=gZ4vNpWq8sB2kF6a10prasempre

# URLs de Produção
FRONTEND_URL=https://1crypten.space
BACKEND_URL=https://api.1crypten.space
API_BASE_URL=https://api.1crypten.space
CORS_ORIGINS=https://1crypten.space,https://www.1crypten.space

# Flask
FLASK_ENV=production
FLASK_PORT=5000
```

### 2. Configuração do Projeto

- **Tipo**: Docker Compose
- **Arquivo**: `docker-compose.coolify.yml`
- **Porta Principal**: 80 (Nginx)
- **Health Check**: `/api/health`

### 3. Domínio e SSL

- **Domínio**: 1crypten.space
- **Subdomínio**: www.1crypten.space
- **SSL**: Configurado via Coolify

### 4. Serviços

1. **PostgreSQL** (porta 5432)
   - Database: trading_signals
   - User: postgres
   - Health check automático

2. **Redis** (porta 6379)
   - Cache e sessões
   - Health check automático

3. **Backend Flask** (porta 5000)
   - API REST
   - Análise técnica
   - Integração Binance/Telegram

4. **Frontend React** (porta interna 80)
   - Interface do usuário
   - Build otimizado para produção

5. **Nginx** (porta 80)
   - Proxy reverso
   - Servir arquivos estáticos
   - SSL termination

### 5. Verificação de Deploy

Após o deploy, verifique:

1. **Health Check**: `https://1crypten.space/api/health`
2. **API Status**: `https://1crypten.space/api/status`
3. **Frontend**: `https://1crypten.space/`
4. **Login**: `https://1crypten.space/api/auth/login`

### 6. Logs e Monitoramento

- Logs do Coolify mostrarão o status de cada serviço
- Backend registra análises de mercado
- Health checks automáticos a cada 30s

### 7. Troubleshooting

**Erro 503 Service Unavailable:**
- Verificar se todos os serviços estão rodando
- Verificar logs do Nginx
- Verificar conectividade entre serviços

**Erro de Conexão com Database:**
- Verificar variáveis de ambiente do PostgreSQL
- Verificar se o serviço postgres está healthy

**Erro de API:**
- Verificar logs do backend
- Verificar variáveis de ambiente da Binance
- Verificar conectividade com APIs externas

### 8. Comandos Úteis

```bash
# Verificar status dos serviços
curl https://1crypten.space/api/health

# Verificar logs do scheduler
curl https://1crypten.space/api/scheduler-logs

# Forçar limpeza de sinais
curl -X POST https://1crypten.space/api/force-cleanup
```

### 9. Backup e Manutenção

- PostgreSQL: Backup automático via Coolify
- Redis: Dados em cache, não críticos
- Logs: Rotação automática

### 10. Atualizações

Para atualizar a aplicação:
1. Fazer push das alterações para o GitHub
2. Coolify detectará automaticamente
3. Rebuild e redeploy automático
4. Zero downtime com health checks