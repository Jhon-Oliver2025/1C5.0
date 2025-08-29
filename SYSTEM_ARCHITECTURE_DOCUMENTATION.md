# 🏗️ Documentação da Arquitetura do Sistema - 1Crypten

## 📅 Data de Atualização: 29/08/2025

---

## 🎯 **Visão Geral da Arquitetura**

Sistema de trading de criptomoedas com análise técnica em tempo real, checkout em duas etapas com CRM integrado e PWA completo.

### ✅ **Arquitetura Atual (Corrigida):**

```mermaid
graph TB
    subgraph "🌐 Coolify (Produção)"
        COOLIFY["🔒 Coolify Platform"]
        HTTPS["🔐 HTTPS/SSL Automático"]
        LB["⚖️ Load Balancer"]
    end
    
    subgraph "🐳 Docker Containers"
        NGINX["🌐 Nginx (Proxy Local)"]
        FRONTEND["📱 Frontend (React/Vite)"]
        BACKEND["🐍 Backend (Python/Flask)"]
        REDIS["🔄 Redis (Cache)"]
        POSTGRES["💾 PostgreSQL (Local)"]
    end
    
    subgraph "☁️ Supabase Cloud"
        SUPABASE_DB["🗄️ PostgreSQL (Principal)"]
        SUPABASE_AUTH["🔐 Auth & Users"]
        SUPABASE_API["🔌 REST API"]
        SUPABASE_REALTIME["⚡ Realtime"]
    end
    
    subgraph "🔌 APIs Externas"
        BINANCE["📊 Binance API"]
        MERCADOPAGO["💳 Mercado Pago"]
        SENDPULSE["📧 SendPulse"]
        TELEGRAM["📱 Telegram Bot"]
    end
    
    COOLIFY --> NGINX
    NGINX --> FRONTEND
    NGINX --> BACKEND
    BACKEND --> REDIS
    BACKEND --> POSTGRES
    BACKEND --> SUPABASE_DB
    BACKEND --> SUPABASE_AUTH
    BACKEND --> BINANCE
    BACKEND --> MERCADOPAGO
    BACKEND --> SENDPULSE
    BACKEND --> TELEGRAM
    FRONTEND --> SUPABASE_API
    FRONTEND --> SUPABASE_REALTIME
```

---

## 🗄️ **Banco de Dados: Arquitetura Híbrida**

### ✅ **Supabase (Principal - Cloud)**

**🎯 Uso Principal:**
- 👥 **Autenticação e Usuários**
- 💳 **Sistema de Checkout e CRM**
- 📊 **Dados de Clientes e Pagamentos**
- 📈 **Métricas e Analytics**
- 🔄 **Sincronização em Tempo Real**

**📋 Configuração:**
```env
# Variáveis de Ambiente Supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

**🏗️ Estrutura de Tabelas:**
- `users` - Usuários autenticados
- `customers` - Dados do CRM (leads/customers)
- `customer_events` - Eventos de rastreamento
- `payments` - Histórico de pagamentos
- `course_access` - Controle de acesso aos cursos
- `user_sessions` - Sessões ativas

### ✅ **PostgreSQL Local (Secundário - Docker)**

**🎯 Uso Secundário:**
- 📊 **Sinais de Trading (cache local)**
- 🔄 **Dados temporários de análise**
- 📈 **Cache de dados da Binance**
- ⚡ **Performance crítica**

**📋 Configuração:**
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=crypto_signals
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

**🏗️ Estrutura de Tabelas:**
- `btc_signals` - Sinais de Bitcoin
- `market_data` - Dados de mercado
- `technical_analysis` - Análises técnicas
- `cache_data` - Cache temporário

---

## 🌐 **Proxy e HTTPS: Configuração Atual**

### ⚠️ **Redundância Identificada: Nginx + Coolify**

**🔍 Situação Atual:**
- 🟡 **Coolify**: Fornece HTTPS/SSL automático
- 🟡 **Nginx Local**: Proxy adicional nos containers
- ⚠️ **Redundância**: Dupla camada de proxy

**✅ Configuração Recomendada:**

#### **Opção 1: Manter Nginx (Atual)**
```yaml
# docker-compose.prod.yml
nginx:
  image: nginx:alpine
  container_name: crypto-nginx
  ports:
    - "80:80"
    - "443:443"  # ⚠️ Redundante com Coolify
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
```

**✅ Vantagens:**
- 🔧 Controle total sobre configurações
- 📊 Logs detalhados
- ⚡ Cache local
- 🔄 Load balancing customizado

**❌ Desvantagens:**
- 🔄 Redundância com Coolify
- 🐳 Container adicional
- 🔧 Manutenção extra

#### **Opção 2: Remover Nginx (Recomendado)**
```yaml
# docker-compose.prod.yml (Simplificado)
frontend:
  build: ./front
  ports:
    - "3000:80"  # Expor diretamente
    
backend:
  build: ./back
  ports:
    - "5000:5000"  # Expor diretamente
```

**✅ Vantagens:**
- 🎯 Arquitetura mais simples
- 🚀 Menos overhead
- 🔧 Menos manutenção
- ⚡ Coolify gerencia tudo

**❌ Desvantagens:**
- 🔧 Menos controle sobre proxy
- 📊 Dependência do Coolify

### 🎯 **Recomendação Final:**

**Para Produção com Coolify:**
- ✅ **Remover Nginx** dos containers
- ✅ **Deixar Coolify** gerenciar HTTPS/SSL
- ✅ **Expor serviços** diretamente
- ✅ **Simplificar** arquitetura

---

## 🐳 **Containers Docker: Configuração Atual**

### ✅ **1. Frontend (React/Vite + PWA)**

```dockerfile
# front/Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
```

**🎯 Funcionalidades:**
- ⚛️ **React 18** com TypeScript
- ⚡ **Vite** para build otimizado
- 📱 **PWA** com Service Worker
- 💳 **Checkout em 2 etapas**
- 🎨 **Styled Components**
- 📊 **Real-time** com Supabase

**📊 Métricas:**
- 📦 **Build Size**: ~600KB (gzipped)
- ⚡ **Build Time**: ~2m 30s
- 📱 **PWA Score**: 95%
- 🎯 **Performance**: 92%

### ✅ **2. Backend (Python/Flask + Supabase)**

```dockerfile
# back/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app_supabase:app"]
```

**🎯 Funcionalidades:**
- 🐍 **Flask** com Gunicorn
- 🗄️ **Supabase** como DB principal
- 📊 **Binance API** para dados
- 💳 **Mercado Pago** para pagamentos
- 📧 **SendPulse** para e-mail
- 🤖 **Telegram Bot** para notificações
- 🔄 **Redis** para cache

**📊 Configuração de Performance:**
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

### ✅ **3. PostgreSQL Local (Cache)**

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=crypto_signals
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./back/init.sql:/docker-entrypoint-initdb.d/init.sql
```

**🎯 Uso:**
- 📊 Cache de sinais de trading
- ⚡ Dados temporários de alta performance
- 🔄 Backup local de dados críticos

### ✅ **4. Redis (Cache & Sessions)**

```yaml
redis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data
```

**🎯 Uso:**
- 🔄 Cache de APIs externas
- 👥 Sessões de usuários
- ⚡ Cache de consultas frequentes
- 📊 Rate limiting

### ✅ **5. Nginx (Proxy Local) - ⚠️ Redundante**

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"  # ⚠️ Redundante com Coolify
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
```

**⚠️ Status:** Redundante com Coolify HTTPS

---

## 🔌 **Integrações Externas**

### ✅ **1. Supabase (Principal)**

**🎯 Serviços Utilizados:**
- 🗄️ **Database**: PostgreSQL gerenciado
- 🔐 **Auth**: Sistema de autenticação
- 🔌 **API**: REST API automática
- ⚡ **Realtime**: WebSocket para updates
- 📊 **Dashboard**: Interface administrativa

**📋 Configuração:**
```python
# supabase_config.py
class SupabaseConfig:
    def __init__(self):
        self.SUPABASE_URL = os.getenv('SUPABASE_URL')
        self.SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
```

### ✅ **2. Binance API**

**🎯 Funcionalidades:**
- 📊 Dados de mercado em tempo real
- 📈 Histórico de preços
- 🔄 WebSocket para updates
- 📊 Análise técnica

### ✅ **3. Mercado Pago**

**🎯 Funcionalidades:**
- 💳 Processamento de pagamentos
- 🔄 Webhooks de confirmação
- 💰 Checkout transparente
- 📊 Relatórios de vendas

### ✅ **4. SendPulse**

**🎯 Funcionalidades:**
- 📧 E-mail marketing
- 🤖 Automações de CRM
- 📊 Métricas de engajamento
- 🎯 Segmentação de leads

### ✅ **5. Telegram Bot**

**🎯 Funcionalidades:**
- 🚨 Alertas de sinais
- 📊 Notificações de sistema
- 🔔 Alertas de pagamentos
- 📈 Relatórios automáticos

---

## 🔄 **Fluxo de Dados**

### ✅ **1. Autenticação (Supabase)**

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant S as Supabase
    participant B as Backend
    
    U->>F: Login
    F->>S: Auth Request
    S->>F: JWT Token
    F->>B: API Request + Token
    B->>S: Validate Token
    S->>B: User Data
    B->>F: Response
```

### ✅ **2. Checkout em 2 Etapas**

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant B as Backend
    participant S as Supabase
    participant MP as Mercado Pago
    
    U->>F: Dados Pessoais (Etapa 1)
    F->>B: Save Customer
    B->>S: Insert Customer (status: lead)
    S->>B: Customer ID
    B->>F: Success
    
    U->>F: Pagamento (Etapa 2)
    F->>B: Create Payment
    B->>MP: Create Preference
    MP->>B: Payment URL
    B->>F: Redirect URL
    
    MP->>B: Webhook (Payment Confirmed)
    B->>S: Update Customer (status: customer)
    B->>S: Grant Course Access
```

### ✅ **3. Sinais de Trading**

```mermaid
sequenceDiagram
    participant B as Backend
    participant BA as Binance API
    participant PG as PostgreSQL Local
    participant R as Redis
    participant T as Telegram
    participant F as Frontend
    
    B->>BA: Get Market Data
    BA->>B: Price Data
    B->>B: Technical Analysis
    B->>PG: Save Signal
    B->>R: Cache Signal
    B->>T: Send Alert
    B->>F: Real-time Update
```

---

## 📊 **Monitoramento e Logs**

### ✅ **Health Checks**

```yaml
# Configuração de Health Checks
backend:
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s

postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 10s
    timeout: 5s
    retries: 5

redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 3s
    retries: 3
```

### ✅ **Logs Estruturados**

```python
# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🚀 **Deploy e Produção**

### ✅ **Coolify (Recomendado)**

**🎯 Configuração Simplificada:**
```yaml
# docker-compose.coolify.yml (Sem Nginx)
version: '3.8'

services:
  backend:
    build: ./back
    ports:
      - "5000:5000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      # ... outras variáveis
    depends_on:
      - redis
      - postgres

  frontend:
    build: ./front
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=https://api.1crypten.space

  redis:
    image: redis:7-alpine
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=crypto_signals
```

**✅ Vantagens do Coolify:**
- 🔒 **HTTPS/SSL**: Automático com Let's Encrypt
- 🌐 **Domínios**: Gerenciamento automático
- 📊 **Monitoramento**: Dashboard integrado
- 🔄 **Deploy**: Git-based automático
- 📈 **Scaling**: Horizontal automático
- 💾 **Backups**: Automáticos

### ✅ **Variáveis de Ambiente**

```env
# Produção - Coolify
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_DATABASE_URL=postgresql://postgres:pass@db.project.supabase.co:5432/postgres

BINANCE_API_KEY=your-binance-key
BINANCE_SECRET_KEY=your-binance-secret

MERCADO_PAGO_ACCESS_TOKEN=your-mp-token
MERCADO_PAGO_PUBLIC_KEY=your-mp-public-key

SENDPULSE_CLIENT_ID=your-sendpulse-id
SENDPULSE_CLIENT_SECRET=your-sendpulse-secret

TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id

REDIS_URL=redis://redis:6379/0
POSTGRES_PASSWORD=your-postgres-password
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

---

## 🔧 **Comandos Úteis**

### ✅ **Desenvolvimento Local**

```bash
# Iniciar sistema completo
docker-compose -f docker-compose.prod.yml up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild específico
docker-compose build backend
docker-compose up -d backend

# Limpeza completa
./rebuild_docker_system.ps1  # Windows
./rebuild_docker_system.sh   # Linux/macOS
```

### ✅ **Produção (Coolify)**

```bash
# Deploy automático via Git
git add .
git commit -m "Deploy: Nova funcionalidade"
git push origin main

# Monitoramento
# Via dashboard do Coolify
# https://coolify.1crypten.space
```

### ✅ **Supabase**

```bash
# Conectar ao banco
psql "postgresql://postgres:pass@db.project.supabase.co:5432/postgres"

# Backup
pg_dump "postgresql://postgres:pass@db.project.supabase.co:5432/postgres" > backup.sql

# Restore
psql "postgresql://postgres:pass@db.project.supabase.co:5432/postgres" < backup.sql
```

---

## 📋 **Checklist de Deploy**

### ✅ **Pré-Deploy**
- [ ] Supabase configurado e testado
- [ ] Variáveis de ambiente definidas
- [ ] Build do frontend funcionando
- [ ] APIs externas configuradas
- [ ] Health checks passando
- [ ] Testes automatizados passando

### ✅ **Deploy**
- [ ] Código commitado e enviado
- [ ] Coolify detectou mudanças
- [ ] Build automático executado
- [ ] Containers iniciados
- [ ] Health checks passando
- [ ] HTTPS funcionando

### ✅ **Pós-Deploy**
- [ ] Frontend acessível
- [ ] APIs respondendo
- [ ] Autenticação funcionando
- [ ] Checkout funcionando
- [ ] PWA instalável
- [ ] Logs sem erros críticos

---

## 🎯 **Próximos Passos**

### 🔥 **Imediato**
1. **Decidir sobre Nginx**: Manter ou remover redundância
2. **Testar Coolify**: Verificar HTTPS automático
3. **Otimizar containers**: Reduzir overhead
4. **Monitorar performance**: Métricas em produção

### ⚡ **Curto Prazo**
1. **Implementar CI/CD**: Testes automáticos
2. **Configurar alertas**: Monitoramento proativo
3. **Otimizar Supabase**: Queries e índices
4. **Implementar cache**: Redis mais eficiente

### 🚀 **Médio Prazo**
1. **Microserviços**: Separar responsabilidades
2. **Kubernetes**: Orquestração avançada
3. **CDN**: Distribuição global
4. **Auto-scaling**: Escalabilidade automática

---

**📅 Última Atualização:** 29/08/2025  
**🔄 Status:** Arquitetura Documentada e Corrigida  
**🎯 Foco:** Supabase como DB Principal + Coolify HTTPS  
**⚠️ Ação:** Decidir sobre redundância do Nginx  

---

> 💡 **Nota:** Esta documentação reflete a arquitetura real do sistema, incluindo o Supabase como banco de dados principal e a identificação da redundância entre Nginx local e HTTPS do Coolify.

**🎉 Sistema 1Crypten - Arquitetura Híbrida Cloud + Local! ☁️**