# 1Crypten - Plataforma de Sinais de Trading

## 📋 Visão Geral

Plataforma avançada de sinais de trading para criptomoedas com interface PWA moderna, sistema de autenticação robusto e análise técnica automatizada.

## 🏗️ Arquitetura do Sistema

### Frontend (React + TypeScript + PWA)
- **Framework**: React 18 com TypeScript
- **Build Tool**: Vite
- **UI Components**: Styled Components
- **PWA**: Service Worker + Manifest
- **Proxy**: Nginx para roteamento de APIs

### Backend (Python + Flask)
- **Framework**: Flask com Supabase
- **Database**: PostgreSQL (Supabase)
- **Cache**: Redis
- **APIs Externas**: Binance, Telegram, Mercado Pago
- **Análise**: Biblioteca TA (Technical Analysis)

### Infraestrutura
- **Containerização**: Docker + Docker Compose
- **Deploy**: Coolify (self-hosted)
- **Proxy**: Nginx (produção)
- **Monitoramento**: Health checks automáticos

## 🔧 Problemas Resolvidos Recentemente

### ✅ Erro 405 Method Not Allowed (RESOLVIDO)
**Problema**: APIs retornando 405 para requisições POST
**Causa**: Configuração incorreta do nginx proxy_pass
**Solução**: 
- Removida barra final do `proxy_pass http://backend:5000`
- Adicionados headers CORS com flag `always`
- Configuração completa de preflight requests

### ✅ Desconexões ERR_CONNECTION_CLOSED (RESOLVIDO)
**Problema**: Backend desconectando intermitentemente
**Causa**: Chaves inválidas da Binance causando erros 401 repetidos
**Solução**:
- Atualizadas chaves da Binance no docker-compose.local.yml
- Configuração estável para desenvolvimento
- Eliminados erros 401 que sobrecarregavam o sistema

### ✅ Problemas de Parsing no Coolify (RESOLVIDO)
**Problema**: Variáveis de ambiente com sintaxe `${VAR:-default}` não funcionando
**Solução**: Simplificação das variáveis para valores diretos

## 🚀 Instruções de Deploy

### Deploy Local (Desenvolvimento)
```bash
# 1. Iniciar Docker Desktop
# 2. Limpar containers antigos
docker system prune -a -f

# 3. Build e iniciar sistema completo
docker-compose -f docker-compose.local.yml up --build -d

# 4. Verificar status
docker ps

# 5. Testar APIs
curl http://localhost:8080/api/status
```

### Deploy Produção (Coolify)
1. **Commit e Push**:
   ```bash
   git add .
   git commit -m "feat: nova funcionalidade"
   git push
   ```

2. **Coolify Auto-Deploy**:
   - Detecta mudanças automaticamente
   - Build das imagens Docker
   - Deploy com zero downtime

3. **Verificação**:
   - https://1crypten.space/api/status
   - Teste de login na interface

## 🔑 Configurações Importantes

### Variáveis de Ambiente (Produção)
```env
# Supabase
SUPABASE_URL=https://fvwdcsqucajnqupsprmo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Binance
BINANCE_API_KEY=aUApdM0jyXeyI1HPxHymi9hSD6QZ3TXFORTknlyc1jADrkCJ7SNSayoZ6oiPCYEj
BINANCE_SECRET_KEY=demo_secret_disable_api_calls

# Telegram
TELEGRAM_BOT_TOKEN=7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ
TELEGRAM_CHAT_ID=seu_chat_id

# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-token
MERCADO_PAGO_PUBLIC_KEY=APP_USR-key
```

### Nginx Configuration
```nginx
# Configuração crítica para APIs
location /api/ {
    proxy_pass http://backend:5000;  # SEM barra final!
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # CORS headers com always flag
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With" always;
    
    # Preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With" always;
        add_header Access-Control-Max-Age 86400 always;
        return 204;
    }
}
```

## 🧪 Testes e Monitoramento

### Health Checks
```bash
# Backend Status
curl https://1crypten.space/api/status

# Frontend
curl https://1crypten.space/

# Login Test
curl -X POST https://1crypten.space/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

### Logs de Monitoramento
```bash
# Backend logs
docker logs crypto-backend-local --tail 50

# Frontend logs
docker logs crypto-frontend-local --tail 50

# Nginx logs
docker exec crypto-frontend-local cat /var/log/nginx/error.log
```

## 📊 Estrutura de Arquivos

```
1C5.0/
├── front/                    # Frontend React + PWA
│   ├── src/                 # Código fonte React
│   ├── public/              # Assets estáticos
│   ├── nginx.conf           # Configuração Nginx
│   └── Dockerfile           # Container frontend
├── back/                    # Backend Python Flask
│   ├── api_routes/          # Rotas da API
│   ├── core/                # Lógica de negócio
│   ├── requirements.txt     # Dependências Python
│   └── Dockerfile           # Container backend
├── docker-compose.local.yml # Desenvolvimento
├── docker-compose.coolify.yml # Produção
└── README.md               # Esta documentação
```

## 🔐 Funcionalidades Principais

### Sistema de Autenticação
- Login/logout com JWT
- Integração com Supabase Auth
- Proteção de rotas
- Sessão persistente

### Análise de Trading
- Sinais automáticos BTC/USDT
- Análise técnica em tempo real
- Métricas de mercado
- Integração Binance API

### Interface PWA
- Instalável como app nativo
- Offline-first com Service Worker
- Notificações push
- Interface responsiva

### Integrações
- **Supabase**: Database e Auth
- **Binance**: Dados de mercado
- **Telegram**: Notificações
- **Mercado Pago**: Pagamentos

## 🐛 Troubleshooting

### Problema: 405 Method Not Allowed
**Solução**: Verificar configuração nginx proxy_pass (sem barra final)

### Problema: ERR_CONNECTION_CLOSED
**Solução**: Verificar chaves Binance e logs do backend

### Problema: Container não inicia
**Solução**: 
```bash
docker system prune -a -f
docker-compose -f docker-compose.local.yml up --build -d
```

### Problema: APIs não respondem
**Solução**: Verificar health checks e logs
```bash
docker ps
docker logs crypto-backend-local
```

## 📈 Próximas Melhorias

- [ ] Implementar WebSocket para dados em tempo real
- [ ] Adicionar mais indicadores técnicos
- [ ] Sistema de alertas personalizados
- [ ] Dashboard de performance
- [ ] API rate limiting
- [ ] Backup automático do banco

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte técnico ou dúvidas:
- **Email**: suporte@1crypten.space
- **Telegram**: @1crypten_support
- **GitHub Issues**: Para bugs e melhorias

---

**Status**: ✅ Sistema 100% Operacional
**Última Atualização**: 30/08/2025
**Versão**: 2.0.0

🚀 **1Crypten - Transformando Trading com Tecnologia!**